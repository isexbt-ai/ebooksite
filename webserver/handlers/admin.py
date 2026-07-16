#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
管理员相关 Handler
"""

import logging
import os
import json
import aiohttp
from datetime import datetime

from webserver.handlers.base import BaseHandler, admin_required
from webserver.models import User, Card, BookSource, DownloadLog, Database
from webserver.legado_parser import LegadoParser, RuleExecutor, parse_legado_sources

logger = logging.getLogger(__name__)


class AdminStatsHandler(BaseHandler):
    """管理员统计信息 Handler"""

    @admin_required
    def get(self):
        """获取统计数据"""
        try:
            db = Database()

            total_users = db.fetchone("SELECT COUNT(*) as count FROM users")['count']
            total_books = db.fetchone("SELECT COUNT(*) as count FROM download_logs")['count']
            total_cards = db.fetchone("SELECT COUNT(*) as count FROM cards")['count']
            total_downloads = db.fetchone(
                "SELECT COUNT(*) as count FROM download_logs WHERE status = 'completed'"
            )['count']

            return self.write_success({
                "total_users": total_users,
                "total_books": total_books,
                "total_cards": total_cards,
                "total_downloads": total_downloads,
            })

        except Exception as e:
            logger.error(f"获取统计数据失败: {e}")
            return self.write_error("stats_failed", "获取统计数据失败")


class AdminUsersHandler(BaseHandler):
    """管理员用户列表 Handler"""

    @admin_required
    def get(self):
        """获取用户列表"""
        try:
            page = int(self.get_argument('page', '1'))
            size = int(self.get_argument('size', '20'))
            offset = (page - 1) * size

            db = Database()

            # 获取用户列表
            rows = db.fetchall(
                "SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (size, offset)
            )
            users = [User(row).to_dict() for row in rows]

            # 获取总数
            total = db.fetchone("SELECT COUNT(*) as count FROM users")['count']

            return self.write_success({
                "total": total,
                "items": users,
                "page": page,
                "size": size,
            })

        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            return self.write_error("users_failed", "获取用户列表失败")


class AdminDeleteUserHandler(BaseHandler):
    """管理员删除用户 Handler"""

    @admin_required
    def post(self, user_id):
        """删除用户"""
        try:
            user_id = int(user_id)

            # 不能删除自己
            current_user = self.get_current_user()
            if current_user.id == user_id:
                return self.write_error("cannot_delete_self", "不能删除自己")

            user = User.get_by_id(user_id)
            if not user:
                return self.write_error("not_found", "用户不存在")

            db = Database()
            db.execute("DELETE FROM users WHERE id = ?", (user_id,))

            logger.info(f"管理员删除用户 {user.username} (ID: {user_id})")
            return self.write_success()

        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            return self.write_error("delete_failed", "删除用户失败")


class AdminCardsHandler(BaseHandler):
    """管理员卡密列表 Handler"""

    @admin_required
    def get(self):
        """获取卡密列表"""
        try:
            page = int(self.get_argument('page', '1'))
            size = int(self.get_argument('size', '20'))
            offset = (page - 1) * size

            db = Database()

            # 获取卡密列表
            rows = db.fetchall(
                "SELECT * FROM cards ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (size, offset)
            )
            cards = [Card(row).to_dict() for row in rows]

            # 获取总数
            total = db.fetchone("SELECT COUNT(*) as count FROM cards")['count']

            return self.write_success({
                "total": total,
                "items": cards,
                "page": page,
                "size": size,
            })

        except Exception as e:
            logger.error(f"获取卡密列表失败: {e}")
            return self.write_error("cards_failed", "获取卡密列表失败")


class AdminSourcesHandler(BaseHandler):
    """管理员书源列表 Handler"""

    @admin_required
    def get(self):
        """获取所有书源"""
        try:
            sources = BookSource.get_all(enabled_only=False)
            return self.write_success({
                "items": [source.to_dict() for source in sources],
            })

        except Exception as e:
            logger.error(f"获取书源列表失败: {e}")
            return self.write_error("sources_failed", "获取书源列表失败")

    @admin_required
    def post(self):
        """添加新书源"""
        try:
            data = self._get_post_data()
            name = data.get('name', '').strip()
            url = data.get('url', '').strip()
            source_type = data.get('type', 'opds').strip()

            if not name:
                return self.write_error("invalid_name", "书源名称不能为空")
            if not url:
                return self.write_error("invalid_url", "书源地址不能为空")

            source = BookSource.create(name, url, source_type)

            logger.info(f"管理员添加书源: {name}")
            return self.write_success(source.to_dict())

        except Exception as e:
            logger.error(f"添加书源失败: {e}")
            return self.write_error("add_source_failed", "添加书源失败")


class AdminDeleteSourceHandler(BaseHandler):
    """管理员删除书源 Handler"""

    @admin_required
    def post(self, source_id):
        """删除书源"""
        try:
            source_id = int(source_id)
            source = BookSource.get_by_id(source_id)
            if not source:
                return self.write_error("not_found", "书源不存在")

            source.delete()

            logger.info(f"管理员删除书源: {source.name} (ID: {source_id})")
            return self.write_success()

        except Exception as e:
            logger.error(f"删除书源失败: {e}")
            return self.write_error("delete_failed", "删除书源失败")


class AdminToggleSourceHandler(BaseHandler):
    """管理员切换书源状态 Handler"""

    @admin_required
    def post(self, source_id):
        """切换书源启用状态"""
        try:
            source_id = int(source_id)
            source = BookSource.get_by_id(source_id)
            if not source:
                return self.write_error("not_found", "书源不存在")

            new_enabled = not source.enabled
            source.update(enabled=new_enabled)
            source.enabled = new_enabled

            logger.info(f"管理员切换书源状态: {source.name} -> {'启用' if new_enabled else '禁用'}")
            return self.write_success({
                "id": source.id,
                "enabled": new_enabled,
            })

        except Exception as e:
            logger.error(f"切换书源状态失败: {e}")
            return self.write_error("toggle_failed", "切换书源状态失败")


class AdminBooksHandler(BaseHandler):
    """管理员书籍列表 Handler"""

    @admin_required
    def get(self):
        """获取书籍列表（从下载记录）"""
        try:
            page = int(self.get_argument('page', '1'))
            size = int(self.get_argument('size', '20'))
            offset = (page - 1) * size

            db = Database()

            # 获取下载记录列表
            rows = db.fetchall(
                "SELECT * FROM download_logs ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (size, offset)
            )
            books = [DownloadLog(row).to_dict() for row in rows]

            # 获取总数
            total = db.fetchone("SELECT COUNT(*) as count FROM download_logs")['count']

            return self.write_success({
                "total": total,
                "items": books,
                "page": page,
                "size": size,
            })

        except Exception as e:
            logger.error(f"获取书籍列表失败: {e}")
            return self.write_error("books_failed", "获取书籍列表失败")


class AdminDeleteBookHandler(BaseHandler):
    """管理员删除书籍 Handler"""

    @admin_required
    def post(self, book_id):
        """删除书籍（删除文件和记录）"""
        try:
            book_id = int(book_id)
            log = DownloadLog.get_by_id(book_id)
            if not log:
                return self.write_error("not_found", "书籍记录不存在")

            # 删除文件
            if log.file_path and os.path.exists(log.file_path):
                try:
                    os.remove(log.file_path)
                except OSError as e:
                    logger.warning(f"删除文件失败: {e}")

            # 删除数据库记录
            db = Database()
            db.execute("DELETE FROM download_logs WHERE id = ?", (book_id,))

            logger.info(f"管理员删除书籍: {log.book_title} (ID: {book_id})")
            return self.write_success()

        except Exception as e:
            logger.error(f"删除书籍失败: {e}")
            return self.write_error("delete_failed", "删除书籍失败")


class AdminImportLegadoHandler(BaseHandler):
    """导入 Legado 书源 Handler"""

    @admin_required
    def post(self):
        """导入 Legado 书源 JSON"""
        try:
            # 获取请求体中的 JSON 数据
            body = self.request.body
            if not body:
                return self.write_error("invalid_params", "请提供书源 JSON 数据")

            json_text = body.decode('utf-8')
            sources = parse_legado_sources(json_text)

            if not sources:
                return self.write_error("invalid_source", "无法解析有效的 Legado 书源")

            imported = []
            skipped = []

            for source in sources:
                try:
                    # 检查是否已存在相同 URL 的书源
                    existing = self._find_source_by_url(source.book_source_url)
                    if existing:
                        skipped.append({
                            "name": source.book_source_name,
                            "url": source.book_source_url,
                            "reason": "书源已存在"
                        })
                        continue

                    # 存储 Legado 书源到数据库
                    config = {
                        "legado": True,
                        "bookSourceUrl": source.book_source_url,
                        "bookSourceGroup": source.book_source_group,
                        "bookSourceType": source.book_source_type,
                        "searchUrl": source.search_url,
                        "ruleSearch": source.rule_search,
                        "ruleBookInfo": source.rule_book_info,
                        "ruleToc": source.rule_toc,
                        "ruleContent": source.rule_content,
                        "exploreUrl": source.explore_url,
                        "header": source.header,
                    }

                    new_source = BookSource.create(
                        name=source.book_source_name,
                        url=source.book_source_url,
                        type='legado',
                        config=config
                    )

                    imported.append({
                        "id": new_source.id,
                        "name": new_source.name,
                        "url": new_source.url,
                    })

                except Exception as e:
                    logger.warning(f"导入书源 {source.book_source_name} 失败: {e}")
                    skipped.append({
                        "name": source.book_source_name,
                        "url": source.book_source_url,
                        "reason": str(e)
                    })

            logger.info(f"成功导入 {len(imported)} 个 Legado 书源，跳过 {len(skipped)} 个")
            return self.write_success({
                "imported": imported,
                "skipped": skipped,
                "total": len(sources),
            })

        except Exception as e:
            logger.error(f"导入 Legado 书源失败: {e}")
            return self.write_error("import_failed", f"导入失败: {str(e)}")

    def _find_source_by_url(self, url: str) -> bool:
        """检查是否已存在相同 URL 的书源"""
        try:
            db = Database()
            row = db.fetchone("SELECT id FROM book_sources WHERE url = ? LIMIT 1", (url,))
            return row is not None
        except:
            return False


class AdminTestLegadoHandler(BaseHandler):
    """测试 Legado 书源 Handler"""

    @admin_required
    async def post(self):
        """测试 Legado 书源搜索功能"""
        try:
            data = self.request.body_arguments
            source_id = data.get('source_id', [b''])[0].decode('utf-8')
            keyword = data.get('keyword', [b'test'])[0].decode('utf-8')

            if not source_id:
                return self.write_error("invalid_params", "请提供书源ID")

            source = BookSource.get_by_id(int(source_id))
            if not source:
                return self.write_error("not_found", "书源不存在")

            if source.type != 'legado':
                return self.write_error("invalid_type", "只能测试 Legado 类型书源")

            # 获取 Legado 配置
            config = source.config or {}
            search_url_template = config.get('searchUrl', '')

            if not search_url_template:
                return self.write_error("no_search_url", "该书源没有配置搜索URL")

            # 构建搜索 URL
            from webserver.legado_parser import LegadoSource
            legado_source = LegadoSource({
                'bookSourceUrl': source.url,
                'bookSourceName': source.name,
                'searchUrl': search_url_template,
                'ruleSearch': config.get('ruleSearch', {}),
            })

            search_url = LegadoParser.build_search_url(legado_source, keyword)

            # 发送请求
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    search_url,
                    timeout=aiohttp.ClientTimeout(total=10),
                    headers={'User-Agent': 'Mozilla/5.0'}
                ) as response:
                    if response.status != 200:
                        return self.write_error(
                            "request_failed",
                            f"请求失败，状态码: {response.status}"
                        )

                    content = await response.text()

            return self.write_success({
                "search_url": search_url,
                "status_code": response.status,
                "content_length": len(content),
                "preview": content[:500] if content else "",
            })

        except Exception as e:
            logger.error(f"测试 Legado 书源失败: {e}")
            return self.write_error("test_failed", f"测试失败: {str(e)}")
