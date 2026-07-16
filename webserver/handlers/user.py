#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
用户相关 Handler（设置、密码、书籍库）
"""

import logging
import os

from webserver.handlers.base import BaseHandler, auth_required
from webserver.models import User, DownloadLog, Database

logger = logging.getLogger(__name__)


class UserSettingsHandler(BaseHandler):
    """用户设置 Handler"""

    def _get_post_data(self):
        """获取 POST 请求数据，支持 form-data 和 JSON"""
        content_type = self.request.headers.get('Content-Type', '')
        if content_type.startswith('application/json'):
            try:
                body = self.request.body
                if body:
                    return json.loads(body.decode('utf-8'))
                return {}
            except (json.JSONDecodeError, UnicodeDecodeError):
                return {}
        else:
            # form-data 格式
            result = {}
            for key, values in self.request.body_arguments.items():
                if values:
                    result[key] = values[0].decode('utf-8')
            return result

    @auth_required
    def post(self):
        """更新用户资料"""
        try:
            data = self._get_post_data()
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()

            user = self.get_current_user()

            db = Database()
            db.execute(
                "UPDATE users SET name = ?, email = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (name, email, user.id)
            )

            logger.info(f"用户 {user.username} 更新资料")
            return self.write_success()

        except Exception as e:
            logger.error(f"更新用户资料失败: {e}")
            return self.write_error("update_failed", "更新用户资料失败")


class UserPasswordHandler(BaseHandler):
    """用户密码 Handler"""

    def _get_post_data(self):
        """获取 POST 请求数据，支持 form-data 和 JSON"""
        content_type = self.request.headers.get('Content-Type', '')
        if content_type.startswith('application/json'):
            try:
                body = self.request.body
                if body:
                    return json.loads(body.decode('utf-8'))
                return {}
            except (json.JSONDecodeError, UnicodeDecodeError):
                return {}
        else:
            # form-data 格式
            result = {}
            for key, values in self.request.body_arguments.items():
                if values:
                    result[key] = values[0].decode('utf-8')
            return result

    @auth_required
    def post(self):
        """修改密码"""
        try:
            data = self._get_post_data()
            old_password = data.get('old_password', '')
            new_password = data.get('new_password', '')

            if not old_password or not new_password:
                return self.write_error("invalid_params", "旧密码和新密码不能为空")

            if len(new_password) < 6 or len(new_password) > 20:
                return self.write_error("invalid_password", "新密码长度必须在6-20个字符之间")

            user = self.get_current_user()

            # 验证旧密码
            if not user.verify_password(old_password):
                return self.write_error("invalid_password", "旧密码错误")

            # 更新密码
            user.update_password(new_password)

            logger.info(f"用户 {user.username} 修改密码")
            return self.write_success()

        except Exception as e:
            logger.error(f"修改密码失败: {e}")
            return self.write_error("password_failed", "修改密码失败")


class BooksHandler(BaseHandler):
    """本地书籍库 Handler"""

    @auth_required
    def get(self):
        """获取本地书籍列表"""
        try:
            page = int(self.get_argument('page', '1'))
            size = int(self.get_argument('size', '20'))
            offset = (page - 1) * size

            db = Database()

            # 获取已完成的下载记录（即本地书籍）
            rows = db.fetchall(
                """SELECT * FROM download_logs
                   WHERE status = 'completed' AND file_path IS NOT NULL
                   ORDER BY completed_at DESC LIMIT ? OFFSET ?""",
                (size, offset)
            )
            books = [DownloadLog(row).to_dict() for row in rows]

            # 获取总数
            total = db.fetchone(
                """SELECT COUNT(*) as count FROM download_logs
                   WHERE status = 'completed' AND file_path IS NOT NULL"""
            )['count']

            return self.write_success({
                "total": total,
                "items": books,
                "page": page,
                "size": size,
            })

        except Exception as e:
            logger.error(f"获取本地书籍列表失败: {e}")
            return self.write_error("books_failed", "获取本地书籍列表失败")


class DeleteBookHandler(BaseHandler):
    """删除本地书籍 Handler"""

    @auth_required
    def post(self, book_id):
        """删除本地书籍"""
        try:
            book_id = int(book_id)
            user = self.get_current_user()

            log = DownloadLog.get_by_id(book_id)
            if not log:
                return self.write_error("not_found", "书籍记录不存在")

            # 只能删除自己的书籍（管理员可以删除所有）
            if log.user_id != user.id and not user.admin:
                return self.write_error("forbidden", "无权删除此书籍")

            # 删除文件
            if log.file_path and os.path.exists(log.file_path):
                try:
                    os.remove(log.file_path)
                except OSError as e:
                    logger.warning(f"删除文件失败: {e}")

            # 删除数据库记录
            db = Database()
            db.execute("DELETE FROM download_logs WHERE id = ?", (book_id,))

            logger.info(f"用户 {user.username} 删除书籍: {log.book_title} (ID: {book_id})")
            return self.write_success()

        except Exception as e:
            logger.error(f"删除书籍失败: {e}")
            return self.write_error("delete_failed", "删除书籍失败")
