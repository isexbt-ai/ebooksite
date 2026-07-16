#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
网络书库搜索 Handler
支持 OPDS、API 和 Legado 书源
"""

import logging
import aiohttp
import xml.etree.ElementTree as ET
import json
import re
from urllib.parse import urljoin

from tornado.web import RequestHandler
from webserver.handlers.base import BaseHandler, auth_required
from webserver.models import BookSource
from webserver.legado_parser import LegadoParser, RuleExecutor, parse_legado_sources

logger = logging.getLogger(__name__)


class SearchHandler(BaseHandler):
    """搜索 Handler"""

    async def get(self):
        """搜索书籍"""
        query = self.get_argument('query', '')
        source_id = self.get_argument('source', '')
        page = int(self.get_argument('page', '1'))

        if not query:
            return self.write_error("invalid_params", "请输入搜索关键词")

        try:
            # 获取书源
            if source_id:
                sources = [BookSource.get_by_id(int(source_id))]
            else:
                sources = BookSource.get_all(enabled_only=True)

            # 并行搜索
            results = []
            for source in sources:
                if not source:
                    continue
                try:
                    if source.type == 'opds':
                        items = await self.search_opds(source, query, page)
                    elif source.type == 'api':
                        items = await self.search_api(source, query, page)
                    elif source.type == 'legado':
                        items = await self.search_legado(source, query, page)
                    else:
                        continue

                    results.extend(items)
                except Exception as e:
                    logger.error(f"搜索书源 {source.name} 失败: {e}")

            return self.write_success({
                "total": len(results),
                "items": results,
                "page": page,
            })

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return self.write_error("search_failed", "搜索失败，请稍后重试")

    async def search_opds(self, source: BookSource, query: str, page: int) -> list:
        """搜索 OPDS 书源"""
        url = urljoin(source.url, f"search/{query}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    return []

                xml_data = await response.text()
                return self.parse_opds(xml_data, source)

    async def search_api(self, source: BookSource, query: str, page: int) -> list:
        """搜索 API 书源"""
        url = urljoin(source.url, "search")

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                params={'q': query, 'page': page},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    return []

                data = await response.json()
                return data.get('items', [])

    async def search_legado(self, source: BookSource, query: str, page: int) -> list:
        """搜索 Legado 书源"""
        try:
            config = source.config or {}
            search_url_template = config.get('searchUrl', '')

            if not search_url_template:
                logger.warning(f"Legado 书源 {source.name} 没有配置搜索URL")
                return []

            # 构建 Legado 源对象
            from webserver.legado_parser import LegadoSource
            legado_source = LegadoSource({
                'bookSourceUrl': source.url,
                'bookSourceName': source.name,
                'searchUrl': search_url_template,
                'ruleSearch': config.get('ruleSearch', {}),
                'ruleBookInfo': config.get('ruleBookInfo', {}),
            })

            # 构建搜索 URL
            search_url = LegadoParser.build_search_url(legado_source, query, page)
            logger.info(f"Legado 搜索 URL: {search_url}")

            # 分离 URL 和选项
            url_options = {}
            url_to_fetch = search_url
            if ',{' in search_url:
                parts = search_url.rsplit(',{', 1)
                url_to_fetch = parts[0]
                try:
                    url_options = json.loads('{' + parts[1])
                except:
                    pass

            # 发送请求
            headers = {'User-Agent': 'Mozilla/5.0'}
            if source.config and 'header' in source.config:
                try:
                    custom_headers = json.loads(source.config['header'])
                    headers.update(custom_headers)
                except:
                    pass

            async with aiohttp.ClientSession() as session:
                # 处理 POST 请求
                method = url_options.get('method', 'GET')
                charset = url_options.get('charset', 'utf-8')

                if method.upper() == 'POST':
                    body = url_options.get('body', '')
                    body = body.replace('{{key}}', query)
                    body = body.replace('{{page}}', str(page))

                    async with session.post(
                        url_to_fetch,
                        data=body.encode(charset),
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=15)
                    ) as response:
                        if response.status != 200:
                            return []
                        content = await response.text()
                else:
                    async with session.get(
                        url_to_fetch,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=15)
                    ) as response:
                        if response.status != 200:
                            return []
                        content = await response.text()

            # 解析搜索结果
            return await self.parse_legado_search(content, source, config)

        except Exception as e:
            logger.error(f"Legado 搜索失败: {e}")
            return []

    async def parse_legado_search(self, content: str, source: BookSource, config: dict) -> list:
        """解析 Legado 搜索结果"""
        try:
            rule_search = config.get('ruleSearch', {})
            if not rule_search:
                return []

            # 检测内容类型（JSON 或 HTML）
            is_json = False
            json_data = None
            try:
                json_data = json.loads(content)
                is_json = True
            except:
                pass

            # 获取书籍列表规则
            book_list_rule = rule_search.get('bookList', '')
            if not book_list_rule:
                return []

            # 根据规则类型解析
            rule_type = LegadoParser.detect_rule_type(book_list_rule)

            if is_json and rule_type == 'jsonpath':
                # JSON 数据 + JSONPath 规则
                results = RuleExecutor.apply_rule(json_data, book_list_rule, 'jsonpath')
                return self._extract_books_from_json(results, rule_search, source)
            elif is_json:
                # JSON 数据但没有 JSONPath 规则
                if isinstance(json_data, list):
                    return self._extract_books_from_json(json_data, rule_search, source)
                elif isinstance(json_data, dict) and 'data' in json_data:
                    return self._extract_books_from_json(json_data.get('data', []), rule_search, source)
            else:
                # HTML 数据
                return self._extract_books_from_html(content, rule_search, source)

            return []

        except Exception as e:
            logger.error(f"解析 Legado 搜索结果失败: {e}")
            return []

    def _extract_books_from_html(self, html: str, rule_search: dict, source: BookSource) -> list:
        """从 HTML 中提取书籍信息"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            # 获取书籍列表规则
            book_list_rule = rule_search.get('bookList', '')

            # 解析 bookList 规则
            if book_list_rule.startswith('@css:'):
                book_list_rule = book_list_rule[5:]
            elif book_list_rule.startswith('@'):
                book_list_rule = book_list_rule[1:]

            # 获取书籍列表元素
            if '@' in book_list_rule:
                selector = book_list_rule.split('@')[0]
            else:
                selector = book_list_rule

            book_elements = soup.select(selector) if selector else [soup]
            results = []

            for elem in book_elements:
                try:
                    book = self._extract_book_info(elem, rule_search, source, 'html')
                    if book and book.get('title'):
                        results.append(book)
                except Exception as e:
                    logger.debug(f"提取单本书籍信息失败: {e}")
                    continue

            return results

        except Exception as e:
            logger.error(f"从 HTML 提取书籍失败: {e}")
            return []

    def _extract_books_from_json(self, data_list: list, rule_search: dict, source: BookSource) -> list:
        """从 JSON 数据中提取书籍信息"""
        results = []

        if not isinstance(data_list, list):
            if isinstance(data_list, dict):
                data_list = [data_list]
            else:
                return results

        for item in data_list:
            try:
                book = self._extract_book_info(item, rule_search, source, 'json')
                if book and book.get('title'):
                    results.append(book)
            except Exception as e:
                logger.debug(f"提取 JSON 书籍信息失败: {e}")
                continue

        return results

    def _extract_book_info(self, element, rule_search: dict, source: BookSource, data_type: str) -> dict:
        """提取单本书籍信息"""
        book = {
            'id': '',
            'title': '',
            'author': '',
            'summary': '',
            'cover_url': '',
            'source': source.name,
            'source_id': source.id,
            'download_url': '',
        }

        if data_type == 'html':
            from bs4 import BeautifulSoup
            if not isinstance(element, BeautifulSoup) and hasattr(element, 'select'):
                soup = element
            else:
                # element 是 Tag
                soup = element

            # 书名
            name_rule = rule_search.get('name', '')
            if name_rule:
                book['title'] = self._extract_text_from_element(soup, name_rule)

            # 作者
            author_rule = rule_search.get('author', '')
            if author_rule:
                book['author'] = self._extract_text_from_element(soup, author_rule)

            # 封面
            cover_rule = rule_search.get('coverUrl', '')
            if cover_rule:
                book['cover_url'] = self._extract_attr_from_element(soup, cover_rule, 'src')

            # 简介
            intro_rule = rule_search.get('intro', '')
            if intro_rule:
                book['summary'] = self._extract_text_from_element(soup, intro_rule)

            # 书籍 URL
            book_url_rule = rule_search.get('bookUrl', '')
            if book_url_rule:
                book['download_url'] = self._extract_attr_from_element(soup, book_url_rule, 'href')

        elif data_type == 'json':
            # JSON 数据直接取字段
            if isinstance(element, dict):
                book['title'] = self._get_json_value(element, rule_search.get('name', ''), 'name')
                book['author'] = self._get_json_value(element, rule_search.get('author', ''), 'author')
                book['cover_url'] = self._get_json_value(element, rule_search.get('coverUrl', ''), 'cover')
                book['summary'] = self._get_json_value(element, rule_search.get('intro', ''), 'intro')
                book['download_url'] = self._get_json_value(element, rule_search.get('bookUrl', ''), 'url')

        return book

    def _extract_text_from_element(self, element, rule: str) -> str:
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

    def _extract_attr_from_element(self, element, rule: str, default_attr: str = 'href') -> str:
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

    def _get_json_value(self, data: dict, rule: str, fallback_key: str = '') -> str:
        """从 JSON 数据中获取值"""
        if not rule:
            return data.get(fallback_key, '')

        # 直接是字段名
        if rule in data:
            val = data[rule]
            return str(val) if val is not None else ''

        # 尝试 JSONPath 风格
        if rule.startswith('$.'):
            key = rule[2:]
            if key in data:
                val = data[key]
                return str(val) if val is not None else ''

        return ''

    def parse_opds(self, xml_data: str, source: BookSource) -> list:
        """解析 OPDS XML"""
        try:
            root = ET.fromstring(xml_data)
            items = []

            # 解析 entry 元素
            for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                item = {
                    'id': entry.findtext('{http://www.w3.org/2005/Atom}id', ''),
                    'title': entry.findtext('{http://www.w3.org/2005/Atom}title', ''),
                    'author': entry.findtext('{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name', ''),
                    'summary': entry.findtext('{http://www.w3.org/2005/Atom}summary', ''),
                    'source': source.name,
                    'source_id': source.id,
                }

                # 获取封面链接
                for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
                    rel = link.get('rel', '')
                    href = link.get('href', '')
                    if 'image' in rel or 'cover' in rel:
                        item['cover_url'] = href
                    elif 'acquisition' in rel:
                        item['download_url'] = href

                items.append(item)

            return items
        except ET.ParseError as e:
            logger.error(f"解析 OPDS XML 失败: {e}")
            return []
