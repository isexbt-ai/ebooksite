#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
API 路由注册
"""

from webserver.handlers.auth import (
    RegisterHandler,
    LoginHandler,
    LogoutHandler,
    MeHandler,
    RedeemHandler,
    GenerateCardsHandler,
)
from webserver.handlers.search import SearchHandler
from webserver.handlers.download import DownloadHandler, DownloadStatusHandler, DownloadHistoryHandler

# 路由列表
routes = [
    # 认证相关
    (r"/api/auth/register", RegisterHandler),
    (r"/api/auth/login", LoginHandler),
    (r"/api/auth/logout", LogoutHandler),
    (r"/api/auth/me", MeHandler),
    (r"/api/auth/redeem", RedeemHandler),

    # 搜索下载
    (r"/api/search", SearchHandler),
    (r"/api/download", DownloadHandler),
    (r"/api/download/([0-9]+)/status", DownloadStatusHandler),
    (r"/api/download/history", DownloadHistoryHandler),

    # 管理员相关
    (r"/api/admin/cards/generate", GenerateCardsHandler),
]
