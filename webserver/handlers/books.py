#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""书籍搜索和列表 Handler"""

import logging
import os
import time
import urllib.parse

from webserver.handlers.base import BaseHandler, auth_required
from webserver.models import Book, UserDownload, Database
from webserver.settings import CONF

logger = logging.getLogger(__name__)

# 默认下载限速（KB/s），0 表示不限速
DEFAULT_DOWNLOAD_SPEED_LIMIT = 500


def get_download_limit() -> int:
    """获取每日下载上限（从数据库配置读取）"""
    try:
        db = Database()
        row = db.fetchone("SELECT value FROM system_settings WHERE key = 'download_limit'")
        if row and row['value']:
            return int(row['value'])
    except (ValueError, TypeError):
        pass
    return 10  # 默认10次


def get_download_speed_limit() -> int:
    """获取下载限速（KB/s），0 表示不限速"""
    try:
        db = Database()
        row = db.fetchone("SELECT value FROM system_settings WHERE key = 'download_speed_limit'")
        if row and row['value']:
            return int(row['value'])
    except (ValueError, TypeError):
        pass
    return DEFAULT_DOWNLOAD_SPEED_LIMIT  # 默认 500KB/s


class SearchHandler(BaseHandler):
    """书籍搜索 Handler（支持模糊查询）"""

    def get(self):
        """搜索书籍"""
        query = self.get_argument('q', '').strip()
        page = int(self.get_argument('page', '1'))
        size = int(self.get_argument('size', '20'))

        if not query:
            return self.write_error("invalid_params", "请输入搜索关键词")

        try:
            result = Book.search(query, page, size)
            return self.write_success(result)

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return self.write_error("search_failed", "搜索失败，请稍后重试")


class BookListHandler(BaseHandler):
    """书籍列表 Handler"""

    def get(self):
        """获取书籍列表"""
        try:
            page = int(self.get_argument('page', '1'))
            size = int(self.get_argument('size', '20'))

            books = Book.get_all(page, size)
            total = Book.get_total_count()

            return self.write_success({
                "total": total,
                "items": [book.to_dict() for book in books],
                "page": page,
                "size": size,
            })

        except Exception as e:
            logger.error(f"获取书籍列表失败: {e}")
            return self.write_error("list_failed", "获取书籍列表失败")


class BookDetailHandler(BaseHandler):
    """书籍详情 Handler"""

    def get(self, book_id):
        """获取书籍详情"""
        try:
            book_id = int(book_id)
            book = Book.get_by_id(book_id)

            if not book:
                return self.write_error("not_found", "书籍不存在")

            return self.write_success(book.to_dict())

        except Exception as e:
            logger.error(f"获取书籍详情失败: {e}")
            return self.write_error("detail_failed", "获取书籍详情失败")


class BookDownloadHandler(BaseHandler):
    """书籍下载 Handler"""

    def get(self, book_id):
        """下载书籍文件（需要登录，有每日下载上限）"""
        try:
            # 1. 验证登录
            user = self.get_current_user()
            if not user:
                self.set_status(401)
                self.write_json({"err": "unauthorized", "msg": "请先登录"})
                return

            # 2. 检查下载上限
            download_count = UserDownload.get_download_count(user.id)
            daily_limit = get_download_limit()
            if download_count >= daily_limit:
                self.set_status(403)
                self.write_json({
                    "err": "download_limit_reached",
                    "msg": f"今日下载次数已达上限（{daily_limit}次），请明天再试"
                })
                return

            # 3. 获取书籍
            book_id = int(book_id)
            book = Book.get_by_id(book_id)

            if not book:
                self.write_error("not_found", "书籍不存在")
                return

            if not book.file_path or not os.path.exists(book.file_path):
                self.write_error("not_found", "书籍文件不存在")
                return

            # 4. 记录下载
            UserDownload.record_download(user.id, book.id)

            # 5. 返回文件（支持限速）
            filename = os.path.basename(book.file_path)
            encoded_filename = urllib.parse.quote(filename)

            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', f"attachment; filename*=UTF-8''{encoded_filename}")
            self.set_header('Content-Length', str(book.file_size or os.path.getsize(book.file_path)))

            # 获取限速配置
            speed_limit = get_download_speed_limit()
            chunk_size = 8192  # 8KB

            with open(book.file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    self.write(chunk)
                    self.flush()

                    # 限速处理
                    if speed_limit > 0:
                        # 计算发送时间，控制速率
                        # speed_limit 单位 KB/s，chunk_size 单位 bytes
                        expected_time = len(chunk) / (speed_limit * 1024)
                        time.sleep(expected_time)

            self.finish()

            logger.info(f"用户 {user.username} 下载书籍: {book.title} (ID: {book_id}), 今日第 {download_count + 1} 次, 限速: {speed_limit}KB/s")

        except Exception as e:
            logger.error(f"下载书籍失败: {e}")
            self.write_error("download_failed", "下载失败")
