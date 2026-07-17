#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""用户相关 Handler（设置、密码）"""

import logging

from webserver.handlers.base import BaseHandler, auth_required
from webserver.models import User, Database

logger = logging.getLogger(__name__)


class UserSettingsHandler(BaseHandler):
    """用户设置 Handler"""

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
