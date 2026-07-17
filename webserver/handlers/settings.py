#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
系统设置和用户反馈 Handler
"""

import logging
import json
from datetime import datetime

from webserver.handlers.base import BaseHandler, auth_required, admin_required
from webserver.models import Database

logger = logging.getLogger(__name__)


class BuyLinkHandler(BaseHandler):
    """卡密购买链接 Handler"""

    def get(self):
        """获取购买链接和书籍数量显示（公开）"""
        try:
            db = Database()
            row = db.fetchone("SELECT value FROM system_settings WHERE key = 'buy_link'")
            url = row['value'] if row else ''
            # 获取书籍数量显示文案
            count_row = db.fetchone("SELECT value FROM system_settings WHERE key = 'book_count_display'")
            book_count_display = count_row['value'] if count_row else ''
            return self.write_success({"url": url, "book_count_display": book_count_display})
        except Exception as e:
            logger.error(f"获取购买链接失败: {e}")
            return self.write_success({"url": "", "book_count_display": ""})

    @admin_required
    def post(self):
        """设置购买链接和书籍数量显示"""
        try:
            data = self._get_post_data()
            url = data.get('url', '').strip()
            book_count_display = data.get('book_count_display', '').strip()

            db = Database()
            # 保存购买链接
            existing = db.fetchone("SELECT id FROM system_settings WHERE key = 'buy_link'")
            if existing:
                db.execute("UPDATE system_settings SET value = ? WHERE key = 'buy_link'", (url,))
            else:
                db.execute("INSERT INTO system_settings (key, value) VALUES ('buy_link', ?)", (url,))

            # 保存书籍数量显示文案
            existing2 = db.fetchone("SELECT id FROM system_settings WHERE key = 'book_count_display'")
            if existing2:
                db.execute("UPDATE system_settings SET value = ? WHERE key = 'book_count_display'", (book_count_display,))
            else:
                db.execute("INSERT INTO system_settings (key, value) VALUES ('book_count_display', ?)", (book_count_display,))

            logger.info(f"管理员设置购买链接和书籍数量显示")
            return self.write_success({"url": url, "book_count_display": book_count_display})
        except Exception as e:
            logger.error(f"设置购买链接失败: {e}")
            return self.write_error("save_failed", "保存失败")


class FeedbackHandler(BaseHandler):
    """用户反馈 Handler"""

    def post(self):
        """提交反馈"""
        try:
            data = self._get_post_data()
            content = data.get('content', '').strip()
            contact = data.get('contact', '').strip()

            if not content:
                return self.write_error("invalid_params", "请输入反馈内容")

            user_id = None
            user = self.get_current_user()
            if user:
                user_id = user.id

            db = Database()
            db.execute(
                "INSERT INTO feedbacks (user_id, content, contact) VALUES (?, ?, ?)",
                (user_id, content, contact)
            )

            logger.info(f"新反馈提交: {content[:50]}...")
            return self.write_success()

        except Exception as e:
            logger.error(f"提交反馈失败: {e}")
            return self.write_error("submit_failed", "提交失败")


class AdminFeedbackListHandler(BaseHandler):
    """管理员反馈列表 Handler"""

    @admin_required
    def get(self):
        """获取反馈列表"""
        try:
            page = int(self.get_argument('page', '1'))
            size = int(self.get_argument('size', '20'))
            offset = (page - 1) * size

            db = Database()
            rows = db.fetchall(
                "SELECT * FROM feedbacks ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (size, offset)
            )
            total = db.fetchone("SELECT COUNT(*) as count FROM feedbacks")['count']

            items = []
            for row in rows:
                items.append({
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'content': row['content'],
                    'contact': row['contact'],
                    'created_at': row['created_at'],
                })

            return self.write_success({
                "total": total,
                "items": items,
                "page": page,
                "size": size,
            })
        except Exception as e:
            logger.error(f"获取反馈列表失败: {e}")
            return self.write_error("list_failed", "获取反馈列表失败")


class AdminFeedbackDeleteHandler(BaseHandler):
    """管理员删除反馈 Handler"""

    @admin_required
    def post(self, feedback_id):
        """删除反馈"""
        try:
            db = Database()
            db.execute("DELETE FROM feedbacks WHERE id = ?", (int(feedback_id),))
            return self.write_success()
        except Exception as e:
            logger.error(f"删除反馈失败: {e}")
            return self.write_error("delete_failed", "删除失败")


class AdminSettingsHandler(BaseHandler):
    """管理员系统设置 Handler"""

    @admin_required
    def get(self):
        """获取所有设置"""
        try:
            db = Database()
            rows = db.fetchall("SELECT * FROM system_settings")
            settings = {row['key']: row['value'] for row in rows}
            return self.write_success(settings)
        except Exception as e:
            logger.error(f"获取系统设置失败: {e}")
            return self.write_error("get_failed", "获取设置失败")

    @admin_required
    def post(self):
        """保存设置"""
        try:
            data = self._get_post_data()
            db = Database()
            for key, value in data.items():
                existing = db.fetchone("SELECT id FROM system_settings WHERE key = ?", (key,))
                if existing:
                    db.execute("UPDATE system_settings SET value = ? WHERE key = ?", (str(value), key))
                else:
                    db.execute("INSERT INTO system_settings (key, value) VALUES (?, ?)", (key, str(value)))
            return self.write_success()
        except Exception as e:
            logger.error(f"保存系统设置失败: {e}")
            return self.write_error("save_failed", "保存失败")
