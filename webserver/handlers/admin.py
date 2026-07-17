#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""管理员相关 Handler（精简版）"""

import logging
import os
import zipfile
import tarfile
import shutil
from datetime import datetime

from webserver.handlers.base import BaseHandler, admin_required
from webserver.models import User, Card, Book, Database
from webserver.indexer import scan_and_index, get_books_dir
from webserver.settings import CONF

logger = logging.getLogger(__name__)


def extract_archive(file_path: str, dest_dir: str) -> list[str]:
    """解压压缩包，返回解压出的文件列表"""
    extracted_files = []

    if not os.path.exists(file_path):
        return extracted_files

    filename = os.path.basename(file_path)

    try:
        if filename.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(dest_dir)
                extracted_files = [os.path.join(dest_dir, name) for name in zip_ref.namelist()]
        elif filename.endswith('.tar.gz') or filename.endswith('.tgz'):
            with tarfile.open(file_path, 'r:gz') as tar_ref:
                tar_ref.extractall(dest_dir)
                extracted_files = [os.path.join(dest_dir, name) for name in tar_ref.getnames()]
        elif filename.endswith('.tar'):
            with tarfile.open(file_path, 'r') as tar_ref:
                tar_ref.extractall(dest_dir)
                extracted_files = [os.path.join(dest_dir, name) for name in tar_ref.getnames()]
    except Exception as e:
        logger.error(f"解压文件失败: {e}")
        raise

    return extracted_files


class AdminLoginHandler(BaseHandler):
    """后台独立登录 Handler"""

    def post(self):
        """后台登录（仅管理员）"""
        try:
            data = self._get_post_data()
            username = data.get('username', '').strip().lower()
            password = data.get('password', '')

            if not username or not password:
                return self.write_error("invalid_params", "用户名和密码不能为空")

            user = User.get_by_username(username)
            if not user or not user.verify_password(password):
                return self.write_error("invalid_credentials", "用户名或密码错误")

            if not user.admin:
                return self.write_error("forbidden", "需要管理员权限")

            # 设置后台专用 cookie
            self.set_current_admin(user.id)

            logger.info(f"管理员 {username} 登录后台")
            return self.write_success({
                "user_id": user.id,
                "username": user.username,
                "name": user.name,
                "token": str(user.id),
            })

        except Exception as e:
            logger.error(f"后台登录失败: {e}")
            return self.write_error("login_failed", "登录失败，请稍后重试")


class AdminStatsHandler(BaseHandler):
    """管理员统计信息 Handler"""

    @admin_required
    def get(self):
        """获取统计数据"""
        try:
            db = Database()

            total_users = db.fetchone("SELECT COUNT(*) as count FROM users")['count']
            total_books = Book.get_total_count()
            total_cards = db.fetchone("SELECT COUNT(*) as count FROM cards")['count']

            return self.write_success({
                "total_users": total_users,
                "total_books": total_books,
                "total_cards": total_cards,
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

            rows = db.fetchall(
                "SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (size, offset)
            )
            users = [User(row).to_dict() for row in rows]

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

            rows = db.fetchall(
                "SELECT * FROM cards ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (size, offset)
            )
            cards = [Card(row).to_dict() for row in rows]

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


class AdminBooksHandler(BaseHandler):
    """管理员书籍管理 Handler"""

    @admin_required
    def get(self):
        """获取书籍列表"""
        try:
            page = int(self.get_argument('page', '1'))
            size = int(self.get_argument('size', '20'))
            search = self.get_argument('search', '').strip()

            if search:
                result = Book.search(search, page, size)
                return self.write_success(result)

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
            return self.write_error("books_failed", "获取书籍列表失败")

    @admin_required
    def post(self):
        """上传本地书籍（支持压缩包解压）"""
        try:
            if 'file' not in self.request.files:
                return self.write_error("invalid_params", "请上传文件")

            file_info = self.request.files['file'][0]
            filename = file_info['filename']
            body = file_info['body']

            title = self.get_argument('title', '').strip()
            author = self.get_argument('author', '').strip()

            if not title:
                title = os.path.splitext(filename)[0]

            # 保存上传文件到临时目录
            temp_path = os.path.join(CONF['uploads_dir'], filename)
            with open(temp_path, 'wb') as f:
                f.write(body)

            uploaded_files = []
            books_dir = CONF['books_dir']

            # 检查是否为压缩包
            if filename.endswith(('.zip', '.tar.gz', '.tgz', '.tar')):
                extract_dir = os.path.join(CONF['uploads_dir'], f"extract_{datetime.now().strftime('%Y%m%d%H%M%S')}")
                os.makedirs(extract_dir, exist_ok=True)

                extracted = extract_archive(temp_path, extract_dir)

                for extracted_file in extracted:
                    if os.path.isfile(extracted_file):
                        dest_path = os.path.join(books_dir, os.path.basename(extracted_file))
                        counter = 1
                        while os.path.exists(dest_path):
                            name, ext = os.path.splitext(os.path.basename(extracted_file))
                            dest_path = os.path.join(books_dir, f"{name}_{counter}{ext}")
                            counter += 1

                        shutil.move(extracted_file, dest_path)
                        uploaded_files.append(dest_path)

                shutil.rmtree(extract_dir, ignore_errors=True)
                os.remove(temp_path)
            else:
                dest_path = os.path.join(books_dir, filename)
                counter = 1
                while os.path.exists(dest_path):
                    name, ext = os.path.splitext(filename)
                    dest_path = os.path.join(books_dir, f"{name}_{counter}{ext}")
                    counter += 1

                shutil.move(temp_path, dest_path)
                uploaded_files.append(dest_path)

            # 自动索引上传的书籍
            for file_path in uploaded_files:
                from webserver.indexer import index_book
                db = Database()
                index_book(db, file_path)

            logger.info(f"管理员上传书籍: {title}, 文件数: {len(uploaded_files)}")
            return self.write_success({
                "uploaded_count": len(uploaded_files),
                "files": uploaded_files,
            })

        except Exception as e:
            logger.error(f"上传书籍失败: {e}")
            return self.write_error("upload_failed", f"上传失败: {str(e)}")


class AdminScanBooksHandler(BaseHandler):
    """管理员扫描书籍 Handler"""

    @admin_required
    def post(self):
        """扫描书籍目录并建立索引"""
        try:
            data = self._get_post_data() or {}
            full_rebuild = data.get('full_rebuild', False)

            books_dir = CONF['books_dir']
            result = scan_and_index(books_dir, full_rebuild=full_rebuild)

            logger.info(f"管理员扫描书籍目录: {result['message']}")
            return self.write_success(result)

        except Exception as e:
            logger.error(f"扫描书籍失败: {e}")
            return self.write_error("scan_failed", f"扫描失败: {str(e)}")


class AdminDeleteBookHandler(BaseHandler):
    """管理员删除书籍 Handler"""

    @admin_required
    def post(self, book_id):
        """删除书籍"""
        try:
            book_id = int(book_id)
            book = Book.get_by_id(book_id)
            if not book:
                return self.write_error("not_found", "书籍不存在")

            # 删除文件
            if book.file_path and os.path.exists(book.file_path):
                try:
                    os.remove(book.file_path)
                except OSError as e:
                    logger.warning(f"删除文件失败: {e}")

            # 删除数据库记录
            Book.delete_by_id(book_id)

            logger.info(f"管理员删除书籍: {book.title} (ID: {book_id})")
            return self.write_success()

        except Exception as e:
            logger.error(f"删除书籍失败: {e}")
            return self.write_error("delete_failed", "删除书籍失败")
