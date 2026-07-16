#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
批量下载 Handler - Legado 书源分类批量下载
"""

import logging
import os
import json
import asyncio
import aiohttp
import re
from datetime import datetime
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin, urlparse

from webserver.handlers.base import BaseHandler, admin_required
from webserver.models import BookSource, DownloadTask, DownloadTaskItem, Database
from webserver.settings import CONF

logger = logging.getLogger(__name__)

# 全局任务状态（内存中，用于停止任务）
_running_tasks: Dict[int, bool] = {}


def sanitize_filename(name: str) -> str:
    """清理文件名，移除非法字符"""
    if not name:
        return 'unknown'
    # 移除非法字符
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    # 限制长度
    return name[:100].strip()


def is_duplicate(title: str, author: str) -> bool:
    """检查书籍是否已下载（去重）"""
    if not title:
        return False

    # 1. 检查数据库中已完成的下载
    db = Database()
    row = db.fetchone(
        """SELECT id FROM download_task_items
           WHERE book_title = ? AND book_author = ? AND status = 'completed'""",
        (title, author or '')
    )
    if row:
        return True

    # 2. 检查文件系统
    filename = f"{sanitize_filename(title)}_{sanitize_filename(author)}.txt"
    expected_path = os.path.join(CONF['books_dir'], filename)
    return os.path.exists(expected_path)


class SourceCategoriesHandler(BaseHandler):
    """获取 Legado 书源分类列表"""

    @admin_required
    def get(self, source_id):
        """获取书源分类列表"""
        try:
            source_id = int(source_id)
            source = BookSource.get_by_id(source_id)

            if not source:
                return self.write_error("not_found", "书源不存在")

            if source.type != 'legado':
                return self.write_error("invalid_type", "仅支持 Legado 书源")

            # 解析 exploreUrl 获取分类
            config = source.config or {}
            explore_url = config.get('exploreUrl', '')

            if not explore_url:
                # 尝试从 explore_url 字段获取
                explore_url = config.get('explore_url', '')

            categories = []
            if explore_url:
                for line in explore_url.strip().split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    if '::' in line:
                        parts = line.split('::', 1)
                        categories.append({
                            'name': parts[0].strip(),
                            'url': parts[1].strip(),
                        })
                    elif line.startswith('http'):
                        # 没有名称的URL，使用URL作为名称
                        categories.append({
                            'name': f'分类{len(categories) + 1}',
                            'url': line.strip(),
                        })

            return self.write_success({
                'source_id': source_id,
                'source_name': source.name,
                'categories': categories,
            })

        except Exception as e:
            logger.error(f"获取分类列表失败: {e}")
            return self.write_error("fetch_failed", f"获取分类列表失败: {str(e)}")


class BatchDownloadHandler(BaseHandler):
    """批量下载 Handler"""

    @admin_required
    async def post(self):
        """创建批量下载任务"""
        try:
            data = self._get_post_data()
            source_id = int(data.get('source_id', 0))
            categories = data.get('categories', [])  # 要下载的分类列表

            if not source_id:
                return self.write_error("invalid_params", "请提供书源ID")

            source = BookSource.get_by_id(source_id)
            if not source:
                return self.write_error("not_found", "书源不存在")

            # 创建任务
            task = DownloadTask.create(source_id, source.name)
            _running_tasks[task.id] = True

            # 启动异步下载
            asyncio.create_task(
                run_batch_download(task.id, source, categories)
            )

            logger.info(f"创建批量下载任务: 书源={source.name}, ID={task.id}")
            return self.write_success(task.to_dict())

        except Exception as e:
            logger.error(f"创建批量下载任务失败: {e}")
            return self.write_error("create_failed", f"创建任务失败: {str(e)}")


class BatchDownloadStatusHandler(BaseHandler):
    """批量下载状态 Handler"""

    @admin_required
    def get(self, task_id):
        """获取任务状态和进度"""
        try:
            task_id = int(task_id)
            task = DownloadTask.get_by_id(task_id)

            if not task:
                return self.write_error("not_found", "任务不存在")

            return self.write_success(task.to_dict())

        except Exception as e:
            logger.error(f"获取任务状态失败: {e}")
            return self.write_error("status_failed", "获取任务状态失败")


class BatchDownloadListHandler(BaseHandler):
    """批量下载任务列表 Handler"""

    @admin_required
    def get(self):
        """获取批量下载任务列表"""
        try:
            tasks = DownloadTask.get_all(limit=50)
            return self.write_success({
                'items': [task.to_dict() for task in tasks],
            })

        except Exception as e:
            logger.error(f"获取任务列表失败: {e}")
            return self.write_error("list_failed", "获取任务列表失败")


class BatchDownloadStopHandler(BaseHandler):
    """停止批量下载任务 Handler"""

    @admin_required
    def post(self, task_id):
        """停止任务"""
        try:
            task_id = int(task_id)
            task = DownloadTask.get_by_id(task_id)

            if not task:
                return self.write_error("not_found", "任务不存在")

            # 标记任务为停止
            _running_tasks[task_id] = False
            task.update_status('stopped')

            logger.info(f"停止批量下载任务: ID={task_id}")
            return self.write_success()

        except Exception as e:
            logger.error(f"停止任务失败: {e}")
            return self.write_error("stop_failed", "停止任务失败")


# ==================== 下载核心逻辑 ====================

async def run_batch_download(task_id: int, source: BookSource, categories: List[Dict]):
    """执行批量下载任务"""
    task = DownloadTask.get_by_id(task_id)
    if not task:
        return

    task.update_status('running')

    try:
        # 获取分类列表
        if not categories:
            categories = await fetch_explore_categories(source)

        if not categories:
            task.update_status('failed')
            return

        total_books = 0

        # 遍历每个分类
        for category in categories:
            if task_id not in _running_tasks or not _running_tasks[task_id]:
                break

            task.update_progress(current_category=category.get('name', ''))

            page = 1
            while True:
                if task_id not in _running_tasks or not _running_tasks[task_id]:
                    break

                task.update_progress(current_page=page)

                # 获取该分类一页的书籍
                books = await fetch_books_from_category(source, category, page)
                if not books:
                    break

                # 下载每本书
                for book in books:
                    if task_id not in _running_tasks or not _running_tasks[task_id]:
                        break

                    # 去重检查
                    if is_duplicate(book.get('title'), book.get('author')):
                        task.update_progress(skip_count=task.skip_count + 1)
                        continue

                    # 创建任务项
                    item = DownloadTaskItem.create(
                        task_id=task_id,
                        category=category.get('name', ''),
                        book_title=book.get('title', ''),
                        book_author=book.get('author', ''),
                        source_url=book.get('book_url', ''),
                    )

                    # 下载书籍
                    success = await download_book(source, book, item)

                    if success:
                        task.update_progress(done_count=task.done_count + 1)
                    else:
                        task.update_progress(failed_count=task.failed_count + 1)

                    total_books += 1

                    # 限速：每本书间隔 2 秒
                    await asyncio.sleep(2)

                page += 1

                # 限速：每页间隔 1 秒
                await asyncio.sleep(1)

                # 限制单次任务数量
                if total_books >= 1000:
                    logger.info(f"任务 {task_id} 达到上限 1000 本，停止")
                    break

            if total_books >= 1000:
                break

        # 更新任务状态
        if task_id in _running_tasks and _running_tasks[task_id]:
            task.update_status('completed')

    except Exception as e:
        logger.error(f"批量下载任务 {task_id} 失败: {e}")
        task.update_status('failed')
    finally:
        if task_id in _running_tasks:
            del _running_tasks[task_id]


async def fetch_explore_categories(source: BookSource) -> List[Dict]:
    """获取 Legado 书源的分类列表"""
    config = source.config or {}
    explore_url = config.get('exploreUrl', '')

    if not explore_url:
        explore_url = config.get('explore_url', '')

    categories = []
    if explore_url:
        for line in explore_url.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            if '::' in line:
                parts = line.split('::', 1)
                categories.append({
                    'name': parts[0].strip(),
                    'url': parts[1].strip(),
                })
            elif line.startswith('http'):
                categories.append({
                    'name': f'分类{len(categories) + 1}',
                    'url': line.strip(),
                })

    return categories


async def fetch_books_from_category(source: BookSource, category: Dict, page: int = 1) -> List[Dict]:
    """获取某个分类下的书籍列表"""
    url = category.get('url', '').replace('{{page}}', str(page))

    if not url:
        return []

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10), headers={'User-Agent': 'Mozilla/5.0'}) as resp:
                if resp.status != 200:
                    logger.warning(f"获取分类书籍失败: HTTP {resp.status}, URL={url}")
                    return []
                content = await resp.text()

        # 解析书籍列表
        config = source.config or {}
        rule_explore = config.get('ruleExplore', {})
        rule_search = config.get('ruleSearch', {})

        if rule_explore:
            return parse_explore_content(content, rule_explore, source)
        elif rule_search:
            return parse_search_content(content, rule_search, source)
        else:
            # 如果没有规则，尝试通用解析
            return parse_generic_content(content, source)

    except Exception as e:
        logger.error(f"获取分类书籍失败: {e}, URL={url}")
        return []


def parse_explore_content(content: str, rule_explore: Dict, source: BookSource) -> List[Dict]:
    """解析分类页面内容，提取书籍列表"""
    books = []

    try:
        # 尝试 JSON 解析
        try:
            json_data = json.loads(content)
            if isinstance(json_data, list):
                for item in json_data:
                    book = extract_book_from_dict(item, rule_explore, source)
                    if book and book.get('title'):
                        books.append(book)
                return books
            elif isinstance(json_data, dict):
                # 尝试从常见字段提取
                for key in ['data', 'items', 'list', 'books']:
                    if key in json_data and isinstance(json_data[key], list):
                        for item in json_data[key]:
                            book = extract_book_from_dict(item, rule_explore, source)
                            if book and book.get('title'):
                                books.append(book)
                        return books
        except json.JSONDecodeError:
            pass

        # HTML 解析（使用 BeautifulSoup）
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # 获取书籍列表规则
        book_list_rule = rule_explore.get('bookList', '')
        if not book_list_rule:
            return books

        # 解析 bookList 规则
        selector = book_list_rule
        if selector.startswith('@css:'):
            selector = selector[5:]
        elif selector.startswith('@'):
            selector = selector[1:]

        if '@' in selector:
            selector = selector.split('@')[0]

        book_elements = soup.select(selector) if selector else []

        for elem in book_elements:
            try:
                book = extract_book_from_html(elem, rule_explore, source)
                if book and book.get('title'):
                    books.append(book)
            except Exception as e:
                logger.debug(f"提取单本书籍信息失败: {e}")
                continue

    except Exception as e:
        logger.error(f"解析分类内容失败: {e}")

    return books


def parse_search_content(content: str, rule_search: Dict, source: BookSource) -> List[Dict]:
    """使用搜索规则解析内容"""
    return parse_explore_content(content, rule_search, source)


def parse_generic_content(content: str, source: BookSource) -> List[Dict]:
    """通用解析 - 尝试从HTML中提取书籍列表"""
    books = []
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # 尝试查找常见的书籍列表结构
        # 1. 查找包含链接的 dt/dd 结构
        for item in soup.find_all('div', class_='item'):
            try:
                title_elem = item.find('dt')
                if title_elem:
                    link = title_elem.find('a')
                    if link:
                        title = link.get_text(strip=True)
                        book_url = link.get('href', '')
                        if title and book_url:
                            books.append({
                                'title': title,
                                'author': '',
                                'book_url': book_url,
                                'cover_url': '',
                                'source': source.name,
                                'source_id': source.id,
                            })
            except Exception:
                continue

        # 2. 如果没有找到，尝试查找所有包含链接的 dt
        if not books:
            for dt in soup.find_all('dt'):
                try:
                    link = dt.find('a')
                    if link:
                        title = link.get_text(strip=True)
                        book_url = link.get('href', '')
                        if title and book_url:
                            books.append({
                                'title': title,
                                'author': '',
                                'book_url': book_url,
                                'cover_url': '',
                                'source': source.name,
                                'source_id': source.id,
                            })
                except Exception:
                    continue

        # 3. 尝试查找常见的书籍列表项
        if not books:
            for item in soup.find_all(['div', 'li'], class_=re.compile(r'item|book|novel', re.I)):
                try:
                    link = item.find('a')
                    if link:
                        title = link.get_text(strip=True)
                        book_url = link.get('href', '')
                        if title and book_url:
                            books.append({
                                'title': title,
                                'author': '',
                                'book_url': book_url,
                                'cover_url': '',
                                'source': source.name,
                                'source_id': source.id,
                            })
                except Exception:
                    continue

    except Exception as e:
        logger.error(f"通用解析失败: {e}")

    return books


def extract_book_from_dict(data: Dict, rules: Dict, source: BookSource) -> Dict:
    """从字典中提取书籍信息"""
    if not isinstance(data, dict):
        return {}

    title = data.get('name', '') or data.get('title', '') or data.get('bookName', '')
    author = data.get('author', '')
    book_url = data.get('bookUrl', '') or data.get('url', '') or data.get('detail', '')
    cover = data.get('coverUrl', '') or data.get('cover', '')

    return {
        'title': title,
        'author': author,
        'book_url': book_url,
        'cover_url': cover,
        'source': source.name,
        'source_id': source.id,
    }


def extract_book_from_html(elem, rules: Dict, source: BookSource) -> Dict:
    """从 HTML 元素中提取书籍信息"""
    from bs4 import BeautifulSoup

    title = ''
    author = ''
    book_url = ''
    cover = ''

    # 书名
    name_rule = rules.get('name', '')
    if name_rule:
        title = extract_text_from_element(elem, name_rule)

    # 作者
    author_rule = rules.get('author', '')
    if author_rule:
        author = extract_text_from_element(elem, author_rule)

    # 书籍链接
    book_url_rule = rules.get('bookUrl', '')
    if book_url_rule:
        book_url = extract_attr_from_element(elem, book_url_rule, 'href')

    # 封面
    cover_rule = rules.get('coverUrl', '')
    if cover_rule:
        cover = extract_attr_from_element(elem, cover_rule, 'src')

    return {
        'title': title,
        'author': author,
        'book_url': book_url,
        'cover_url': cover,
        'source': source.name,
        'source_id': source.id,
    }


def extract_text_from_element(element, rule: str) -> str:
    """从元素中提取文本"""
    try:
        from bs4 import BeautifulSoup
        if '@' in rule:
            parts = rule.rsplit('@', 1)
            selector = parts[0]
            attr = parts[1]
        else:
            selector = rule
            attr = 'text'

        if selector:
            found = element.select_one(selector)
            if found:
                if attr == 'text':
                    return found.get_text(strip=True)
                else:
                    return found.get(attr, '')
        else:
            if attr == 'text':
                return element.get_text(strip=True)
    except:
        pass
    return ''


def extract_attr_from_element(element, rule: str, default_attr: str = 'href') -> str:
    """从元素中提取属性"""
    try:
        if '@' in rule:
            parts = rule.rsplit('@', 1)
            selector = parts[0]
            attr = parts[1]
        else:
            selector = rule
            attr = default_attr

        if selector:
            found = element.select_one(selector)
            if found:
                return found.get(attr, '')
        else:
            return element.get(attr, '')
    except:
        pass
    return ''


async def download_book(source: BookSource, book: Dict, item: DownloadTaskItem) -> bool:
    """下载单本书籍"""
    try:
        book_url = book.get('book_url', '')
        if not book_url:
            item.update_status('failed', error='没有书籍链接')
            return False

        # 补全 URL
        if book_url.startswith('/'):
            book_url = urljoin(source.url, book_url)
        elif not book_url.startswith('http'):
            book_url = urljoin(source.url, book_url)

        # 获取书籍详情页（带重试）
        content = None
        for attempt in range(3):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(book_url, timeout=aiohttp.ClientTimeout(total=15), headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36'}) as resp:
                        if resp.status != 200:
                            item.update_status('failed', error=f'HTTP {resp.status}')
                            return False
                        content = await resp.text()
                        break
            except Exception as e:
                logger.warning(f"获取书籍详情页失败 (尝试 {attempt+1}/3): {e}")
                if attempt < 2:
                    await asyncio.sleep(2)
                else:
                    raise

        if not content:
            item.update_status('failed', error='无法获取书籍内容')
            return False

        # 解析章节列表
        config = source.config or {}
        rule_toc = config.get('ruleToc', {})
        chapters = parse_chapters(content, rule_toc, source)

        if not chapters:
            # 如果没有章节，直接保存详情页内容
            full_text = f"书名：{book.get('title', '')}\n作者：{book.get('author', '')}\n来源：{source.name}\n{'='*50}\n\n"
            full_text += content
        else:
            # 下载所有章节（限制最多200章，避免超时）
            full_text = f"书名：{book.get('title', '')}\n作者：{book.get('author', '')}\n来源：{source.name}\n{'='*50}\n\n"

            max_chapters = 200
            for idx, chapter in enumerate(chapters[:max_chapters]):
                try:
                    # 添加超时控制，每章最多10秒
                    chapter_content = await asyncio.wait_for(
                        download_chapter(chapter, source),
                        timeout=10.0
                    )
                    full_text += f"\n{'='*50}\n{chapter.get('title', '章节')}\n{'='*50}\n\n"
                    full_text += chapter_content + "\n"

                    # 限速：每章间隔 0.5 秒
                    await asyncio.sleep(0.5)
                except asyncio.TimeoutError:
                    logger.warning(f"下载章节超时: {chapter.get('title', '')}")
                    continue
                except Exception as e:
                    logger.warning(f"下载章节失败: {e}")
                    continue

        # 保存文件
        title = book.get('title', 'unknown')
        author = book.get('author', 'unknown')
        filename = f"{sanitize_filename(title)}_{sanitize_filename(author)}.txt"
        file_path = os.path.join(CONF['books_dir'], filename)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_text)

        item.update_status('completed', file_path=file_path)
        return True

    except Exception as e:
        logger.error(f"下载书籍失败: {e}")
        item.update_status('failed', error=str(e)[:500])
        return False


def parse_chapters(content: str, rule_toc: Dict, source: BookSource) -> List[Dict]:
    """解析章节列表"""
    chapters = []

    try:
        # 尝试 JSON 解析
        try:
            json_data = json.loads(content)
            if isinstance(json_data, list):
                for item in json_data:
                    if isinstance(item, dict):
                        chapters.append({
                            'title': item.get('title', '') or item.get('name', ''),
                            'url': item.get('url', '') or item.get('link', ''),
                        })
                return chapters
        except json.JSONDecodeError:
            pass

        # HTML 解析
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        chapter_list_rule = rule_toc.get('chapterList', '')
        if not chapter_list_rule:
            return chapters

        selector = chapter_list_rule
        if selector.startswith('@css:'):
            selector = selector[5:]
        elif selector.startswith('@'):
            selector = selector[1:]

        if '@' in selector:
            selector = selector.split('@')[0]

        chapter_elements = soup.select(selector) if selector else []

        for elem in chapter_elements:
            try:
                title_rule = rule_toc.get('chapterName', '')
                url_rule = rule_toc.get('chapterUrl', '')

                title = extract_text_from_element(elem, title_rule) if title_rule else elem.get_text(strip=True)
                url = extract_attr_from_element(elem, url_rule, 'href') if url_rule else elem.get('href', '')

                if title:
                    chapters.append({
                        'title': title,
                        'url': url,
                    })
            except Exception as e:
                continue

    except Exception as e:
        logger.error(f"解析章节列表失败: {e}")

    return chapters


async def download_chapter(chapter: Dict, source: BookSource) -> str:
    """下载单个章节"""
    url = chapter.get('url', '')
    if not url:
        return ''

    # 补全 URL
    if url.startswith('/'):
        url = urljoin(source.url, url)
    elif not url.startswith('http'):
        url = urljoin(source.url, url)

    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10), headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36'}) as resp:
            if resp.status != 200:
                return ''
            content = await resp.text()

    # 解析正文内容
    config = source.config or {}
    rule_content = config.get('ruleContent', {})

    return parse_content(content, rule_content)


def parse_content(content: str, rule_content: Dict) -> str:
    """解析正文内容"""
    if not rule_content:
        return content

    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        content_rule = rule_content.get('content', '')
        if not content_rule:
            return soup.get_text(separator='\n', strip=True)

        selector = content_rule
        if selector.startswith('@css:'):
            selector = selector[5:]
        elif selector.startswith('@'):
            selector = selector[1:]

        if '@' in selector:
            selector = selector.split('@')[0]

        elem = soup.select_one(selector)
        if elem:
            return elem.get_text(separator='\n', strip=True)
        else:
            return soup.get_text(separator='\n', strip=True)

    except Exception as e:
        logger.error(f"解析正文失败: {e}")
        return content
