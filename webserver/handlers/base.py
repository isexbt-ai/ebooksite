#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
基础 Handler 和工具函数
"""

import json
import logging
import tornado.web
from typing import Optional

from webserver.models import User

logger = logging.getLogger(__name__)


class BaseHandler(tornado.web.RequestHandler):
    """基础 Handler"""

    def prepare(self):
        """请求预处理"""
        pass

    def get_current_user(self) -> Optional[User]:
        """获取当前登录用户"""
        user_id = self.get_secure_cookie("user_id")
        if user_id:
            try:
                user = User.get_by_id(int(user_id))
                if user and user.active:
                    return user
            except (ValueError, TypeError):
                pass
        return None

    def set_current_user(self, user_id: int):
        """设置当前用户"""
        self.set_secure_cookie("user_id", str(user_id))

    def clear_current_user(self):
        """清除当前用户"""
        self.clear_cookie("user_id")

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
    """管理员验证装饰器"""
    def wrapper(self, *args, **kwargs):
        user = self.get_current_user()
        if not user:
            self.write_error("unauthorized", "请先登录", 401)
            return
        if not user.admin:
            self.write_error("forbidden", "需要管理员权限", 403)
            return
        return func(self, *args, **kwargs)
    return wrapper
