#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
管理员相关 Handler
"""

import logging
import os
import json
import zipfile
import tarfile
import shutil
from datetime import datetime

from webserver.handlers.base import BaseHandler, admin_required
from webserver.models import User, Card, BookSource, DownloadLog, Database
from webserver.settings import CONF

logger = logging.getLogger(__name__)


def extract_archive(file_path: str, dest_dir: str) -> list[str]:
    """解压压缩包，返回解压出的文件列表"""
    extracted_files = []

    if not os.path.exists(file_path):
        return extracted_files

    # 获取文件扩展名
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

    @admin_required
    def post(self):
        """上传本地书籍（支持压缩包解压）"""
        try:
            # 获取上传的文件
            if 'file' not in self.request.files:
                return self.write_error("invalid_params", "请上传文件")

            file_info = self.request.files['file'][0]
            filename = file_info['filename']
            content_type = file_info['content_type']
            body = file_info['body']

            # 获取元数据
            title = self.get_argument('title', '').strip()
            author = self.get_argument('author', '').strip()
            publisher = self.get_argument('publisher', '').strip()

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
                # 解压到临时目录
                extract_dir = os.path.join(CONF['uploads_dir'], f"extract_{datetime.now().strftime('%Y%m%d%H%M%S')}")
                os.makedirs(extract_dir, exist_ok=True)

                extracted = extract_archive(temp_path, extract_dir)

                # 移动解压出的书籍文件到 books 目录
                for extracted_file in extracted:
                    if os.path.isfile(extracted_file):
                        dest_path = os.path.join(books_dir, os.path.basename(extracted_file))
                        # 避免文件名冲突
                        counter = 1
                        while os.path.exists(dest_path):
                            name, ext = os.path.splitext(os.path.basename(extracted_file))
                            dest_path = os.path.join(books_dir, f"{name}_{counter}{ext}")
                            counter += 1

                        shutil.move(extracted_file, dest_path)
                        uploaded_files.append(dest_path)

                # 清理解压目录
                shutil.rmtree(extract_dir, ignore_errors=True)
                # 删除原始压缩包
                os.remove(temp_path)
            else:
                # 普通文件，直接移动到 books 目录
                dest_path = os.path.join(books_dir, filename)
                counter = 1
                while os.path.exists(dest_path):
                    name, ext = os.path.splitext(filename)
                    dest_path = os.path.join(books_dir, f"{name}_{counter}{ext}")
                    counter += 1

                shutil.move(temp_path, dest_path)
                uploaded_files.append(dest_path)

            # 记录到数据库
            user = self.get_current_user()
            for file_path in uploaded_files:
                DownloadLog.create(
                    user_id=user.id,
                    book_title=title,
                    book_author=author,
                    source_url=publisher,
                )
                # 更新状态为已完成
                db = Database()
                db.execute(
                    "UPDATE download_logs SET status = 'completed', file_path = ?, file_size = ? WHERE id = (SELECT MAX(id) FROM download_logs)",
                    (file_path, os.path.getsize(file_path))
                )

            logger.info(f"管理员上传书籍: {title}, 文件数: {len(uploaded_files)}")
            return self.write_success({
                "uploaded_count": len(uploaded_files),
                "files": uploaded_files,
            })

        except Exception as e:
            logger.error(f"上传书籍失败: {e}")
            return self.write_error("upload_failed", f"上传失败: {str(e)}")


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
