#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""基础 Handler 和工具函数"""

import json
import logging
import time
import tornado.web
from typing import Optional

from webserver.models import User

logger = logging.getLogger(__name__)

# 登录失败限制：5 分钟内最多 5 次
LOGIN_ATTEMPT_LIMIT = 5
LOGIN_ATTEMPT_WINDOW = 300  # 5 分钟

# 内存中的登录失败记录（IP -> {count, last_time}）
_login_attempts: dict = {}


def check_login_rate_limit(ip: str) -> bool:
    """检查登录频率限制

    Args:
        ip: 客户端 IP

    Returns:
        True: 允许登录
        False: 超过限制
    """
    now = time.time()
    if ip in _login_attempts:
        record = _login_attempts[ip]
        if now - record['last_time'] > LOGIN_ATTEMPT_WINDOW:
            # 超过时间窗口，重置
            _login_attempts[ip] = {'count': 1, 'last_time': now}
            return True
        if record['count'] >= LOGIN_ATTEMPT_LIMIT:
            return False
        record['count'] += 1
        record['last_time'] = now
    else:
        _login_attempts[ip] = {'count': 1, 'last_time': now}
    return True


class BaseHandler(tornado.web.RequestHandler):
    """基础 Handler"""

    def set_default_headers(self):
        """设置默认安全响应头"""
        self.set_header("X-Frame-Options", "DENY")
        self.set_header("X-Content-Type-Options", "nosniff")
        # 移除 X-XSS-Protection（现代浏览器已弃用，CSP 替代）
        self.set_header("Referrer-Policy", "strict-origin-when-cross-origin")
        # 更严格的 CSP
        self.set_header("Content-Security-Policy",
                         "default-src 'self'; "
                         "script-src 'self'; "
                         "style-src 'self' 'unsafe-inline'; "
                         "img-src 'self' data: https:; "
                         "font-src 'self'; "
                         "connect-src 'self'; "
                         "frame-ancestors 'none'; "
                         "base-uri 'self';")
        self.set_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        # 添加额外的安全头
        self.set_header("Permissions-Policy", "geolocation=(), microphone=(), camera=()")

    def prepare(self):
        """请求预处理"""
        pass

    def _get_post_data(self) -> dict:
        """获取 POST 请求数据，自动兼容 form-data 和 JSON"""
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
            # application/x-www-form-urlencoded 或 multipart/form-data
            result = {}
            for key, values in self.request.body_arguments.items():
                if values:
                    result[key] = values[0].decode('utf-8')
            return result

    def get_current_user(self) -> Optional[User]:
        """获取当前登录用户 - 支持 cookie 和 Authorization header"""
        # 1. 先尝试从 secure_cookie 获取
        user_id = self.get_secure_cookie("user_id")
        if user_id:
            try:
                user = User.get_by_id(int(user_id))
                if user and user.active:
                    return user
            except (ValueError, TypeError):
                pass

        # 2. 尝试从 Authorization header 获取 (Bearer token)
        auth_header = self.request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
            try:
                user = User.get_by_id(int(token))
                if user and user.active:
                    return user
            except (ValueError, TypeError):
                pass

        return None

    def get_current_admin(self) -> Optional[User]:
        """获取当前后台登录的管理员"""
        # 1. 先尝试从 admin_user_id secure_cookie 获取
        admin_user_id = self.get_secure_cookie("admin_user_id")
        if admin_user_id:
            try:
                user = User.get_by_id(int(admin_user_id))
                if user and user.admin:
                    return user
            except (ValueError, TypeError):
                pass

        # 2. 尝试从 Authorization header 获取 (Bearer token)
        auth_header = self.request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
            try:
                user = User.get_by_id(int(token))
                if user and user.admin:
                    return user
            except (ValueError, TypeError):
                pass

        return None

    def set_current_user(self, user_id: int, remember: bool = False):
        """设置当前用户

        Args:
            user_id: 用户ID
            remember: 是否保持登录状态（True=30天，False=7天）
        """
        expires_days = 30 if remember else 7
        self.set_secure_cookie("user_id", str(user_id), expires_days=expires_days)

    def set_current_admin(self, user_id: int, remember: bool = False):
        """设置当前后台管理员

        Args:
            user_id: 用户ID
            remember: 是否保持登录状态（True=30天，False=7天）
        """
        expires_days = 30 if remember else 7
        self.set_secure_cookie("admin_user_id", str(user_id), expires_days=expires_days)

    def clear_current_user(self):
        """清除当前用户"""
        self.clear_cookie("user_id")

    def clear_current_admin(self):
        """清除当前后台管理员"""
        self.clear_cookie("admin_user_id")

    def write_json(self, data: dict):
        """返回 JSON 响应"""
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.write(json.dumps(data, ensure_ascii=False, default=str))

    def write_success(self, data: dict = None):
        """返回成功响应"""
        response = {"err": "ok"}
        if data:
            response["data"] = data
        self.write_json(response)

    def write_error(self, code: str, message: str = "", status_code: int = 400):
        """返回错误响应"""
        self.set_status(status_code)
        self.write_json({"err": code, "msg": message})


def auth_required(func):
    """登录验证装饰器"""
    def wrapper(self, *args, **kwargs):
        user = self.get_current_user()
        if not user:
            self.write_error("unauthorized", "请先登录", 401)
            return
        return func(self, *args, **kwargs)
    return wrapper


def admin_required(func):
    """管理员验证装饰器（支持前台和后台登录）"""
    def wrapper(self, *args, **kwargs):
        # 先尝试前台登录
        user = self.get_current_user()
        # 再尝试后台登录
        if not user or not user.admin:
            user = self.get_current_admin()
        if not user:
            self.write_error("unauthorized", "请先登录", 401)
            return
        if not user.admin:
            self.write_error("forbidden", "需要管理员权限", 403)
            return
        return func(self, *args, **kwargs)
    return wrapper
