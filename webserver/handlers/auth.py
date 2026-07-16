#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
认证相关 Handler
"""

import logging
import secrets
import string
from datetime import datetime, timedelta

from webserver.handlers.base import BaseHandler, auth_required, admin_required
from webserver.models import User, Card

logger = logging.getLogger(__name__)


def generate_card_code() -> str:
    """生成卡密：ABCD-1234-EFGH-5678 格式"""
    chars = string.ascii_uppercase + string.digits
    parts = [''.join(secrets.choice(chars) for _ in range(4)) for _ in range(4)]
    return '-'.join(parts)


class RegisterHandler(BaseHandler):
    """注册 Handler"""

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

    def post(self):
        """用户注册"""
        try:
            data = self._get_post_data()
            username = data.get('username', '').strip()
            password = data.get('password', '')
            card_code = data.get('card_code', '').strip()

            # 验证参数
            if not username or not password:
                return self.write_error("invalid_params", "用户名和密码不能为空")

            if len(username) < 3 or len(username) > 50:
                return self.write_error("invalid_username", "用户名长度必须在3-50个字符之间")

            if len(password) < 6 or len(password) > 20:
                return self.write_error("invalid_password", "密码长度必须在6-20个字符之间")

            # 检查用户名是否已存在
            if User.get_by_username(username):
                return self.write_error("username_exists", "用户名已存在")

            # 验证卡密
            if not card_code:
                return self.write_error("invalid_card", "请输入卡密")

            card = Card.get_by_code(card_code)
            if not card:
                return self.write_error("invalid_card", "卡密无效")

            if card.used:
                return self.write_error("card_used", "卡密已被使用")

            if card.expires_at and card.expires_at < datetime.now():
                return self.write_error("card_expired", "卡密已过期")

            # 创建用户
            user = User.create(username, password, username)

            # 激活用户
            expiry_date = datetime.now() + timedelta(days=card.duration_days)
            user.activate(expiry_date)

            # 标记卡密已使用
            card.redeem(user.id)

            # 设置登录状态
            self.set_current_user(user.id)

            logger.info(f"用户 {username} 注册成功")
            return self.write_success({
                "user_id": user.id,
                "username": user.username,
                "expiry_date": user.expiry_date.isoformat() if user.expiry_date else None
            })

        except Exception as e:
            logger.error(f"注册失败: {e}")
            return self.write_error("register_failed", "注册失败，请稍后重试")


class LoginHandler(BaseHandler):
    """登录 Handler"""

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

    def post(self):
        """用户登录"""
        try:
            data = self._get_post_data()
            username = data.get('username', '').strip().lower()
            password = data.get('password', '')

            if not username or not password:
                return self.write_error("invalid_params", "用户名和密码不能为空")

            # 查找用户
            user = User.get_by_username(username)
            if not user:
                return self.write_error("invalid_credentials", "用户名或密码错误")

            # 验证密码
            if not user.verify_password(password):
                return self.write_error("invalid_credentials", "用户名或密码错误")

            # 检查账号是否激活
            if not user.active:
                return self.write_error("account_inactive", "账号未激活")

            # 检查账号是否过期
            if user.expiry_date and user.expiry_date < datetime.now():
                return self.write_error("account_expired", "账号已过期，请续费")

            # 更新最后登录时间
            user.update_last_login()

            # 设置登录状态
            self.set_current_user(user.id)

            logger.info(f"用户 {username} 登录成功")
            return self.write_success({
                "user_id": user.id,
                "username": user.username,
                "name": user.name,
                "admin": user.admin,
                "expiry_date": user.expiry_date.isoformat() if user.expiry_date else None
            })

        except Exception as e:
            logger.error(f"登录失败: {e}")
            return self.write_error("login_failed", "登录失败，请稍后重试")


class LogoutHandler(BaseHandler):
    """登出 Handler"""

    @auth_required
    def post(self):
        """用户登出"""
        self.clear_current_user()
        return self.write_success()


class MeHandler(BaseHandler):
    """当前用户信息 Handler"""

    @auth_required
    def get(self):
        """获取当前用户信息"""
        user = self.get_current_user()
        return self.write_success(user.to_dict())


class RedeemHandler(BaseHandler):
    """卡密兑换 Handler"""

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
        """兑换卡密"""
        try:
            data = self._get_post_data()
            card_code = data.get('card_code', '').strip()

            if not card_code:
                return self.write_error("invalid_card", "请输入卡密")

            # 查找卡密
            card = Card.get_by_code(card_code)
            if not card:
                return self.write_error("invalid_card", "卡密无效")

            if card.used:
                return self.write_error("card_used", "卡密已被使用")

            if card.expires_at and card.expires_at < datetime.now():
                return self.write_error("card_expired", "卡密已过期")

            # 获取当前用户
            user = self.get_current_user()

            # 延长有效期
            user.extend_expiry(card.duration_days)

            # 标记卡密已使用
            card.redeem(user.id)

            logger.info(f"用户 {user.username} 兑换卡密成功，延长 {card.duration_days} 天")
            return self.write_success({
                "duration_days": card.duration_days,
                "new_expiry_date": user.expiry_date.isoformat() if user.expiry_date else None
            })

        except Exception as e:
            logger.error(f"卡密兑换失败: {e}")
            return self.write_error("redeem_failed", "卡密兑换失败，请稍后重试")


class GenerateCardsHandler(BaseHandler):
    """生成卡密 Handler（管理员）"""

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

    @admin_required
    def post(self):
        """批量生成卡密"""
        try:
            data = self._get_post_data()
            count = int(data.get('count', 10))
            card_type = data.get('type', 'register')
            duration_days = int(data.get('duration_days', 30))

            if count < 1 or count > 100:
                return self.write_error("invalid_count", "生成数量必须在1-100之间")

            if card_type not in ['register', 'renew']:
                return self.write_error("invalid_type", "卡密类型必须是 register 或 renew")

            if duration_days < 1 or duration_days > 3650:
                return self.write_error("invalid_duration", "有效期天数必须在1-3650之间")

            codes = []
            for _ in range(count):
                code = generate_card_code()
                Card.create(code, card_type, duration_days)
                codes.append(code)

            logger.info(f"管理员生成 {count} 个卡密")
            return self.write_success({
                "codes": codes,
                "count": len(codes),
                "type": card_type,
                "duration_days": duration_days
            })

        except Exception as e:
            logger.error(f"生成卡密失败: {e}")
            return self.write_error("generate_failed", "生成卡密失败，请稍后重试")
