#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""API 路由注册"""

from webserver.handlers.auth import (
    RegisterHandler,
    LoginHandler,
    LogoutHandler,
    MeHandler,
    RedeemHandler,
    GenerateCardsHandler,
)
from webserver.handlers.books import (
    SearchHandler,
    BookListHandler,
    BookDetailHandler,
    BookDownloadHandler,
)
from webserver.handlers.admin import (
    AdminLoginHandler,
    AdminStatsHandler,
    AdminUsersHandler,
    AdminDeleteUserHandler,
    AdminCardsHandler,
    AdminBooksHandler,
    AdminScanBooksHandler,
    AdminDeleteBookHandler,
)
from webserver.handlers.user import (
    UserSettingsHandler,
    UserPasswordHandler,
)
from webserver.handlers.settings import (
    BuyLinkHandler,
    FeedbackHandler,
    AdminFeedbackListHandler,
    AdminFeedbackDeleteHandler,
    AdminSettingsHandler,
)

# 路由列表
routes = [
    # 认证相关
    (r"/api/auth/register", RegisterHandler),
    (r"/api/auth/login", LoginHandler),
    (r"/api/auth/logout", LogoutHandler),
    (r"/api/auth/me", MeHandler),
    (r"/api/auth/redeem", RedeemHandler),

    # 书籍搜索（公开）
    (r"/api/books/search", SearchHandler),
    (r"/api/books/download/([0-9]+)", BookDownloadHandler),
    (r"/api/books", BookListHandler),
    (r"/api/books/([0-9]+)", BookDetailHandler),

    # 用户设置
    (r"/api/user/settings", UserSettingsHandler),
    (r"/api/user/password", UserPasswordHandler),

    # 系统设置（公开）
    (r"/api/settings/buy_link", BuyLinkHandler),

    # 用户反馈
    (r"/api/feedback", FeedbackHandler),

    # 后台独立登录
    (r"/api/admin/auth/login", AdminLoginHandler),

    # 管理员相关
    (r"/api/admin/cards/generate", GenerateCardsHandler),
    (r"/api/admin/stats", AdminStatsHandler),
    (r"/api/admin/users", AdminUsersHandler),
    (r"/api/admin/users/([0-9]+)/delete", AdminDeleteUserHandler),
    (r"/api/admin/cards", AdminCardsHandler),
    (r"/api/admin/books", AdminBooksHandler),
    (r"/api/admin/books/scan", AdminScanBooksHandler),
    (r"/api/admin/books/([0-9]+)/delete", AdminDeleteBookHandler),

    # 管理员 - 系统设置
    (r"/api/admin/settings", AdminSettingsHandler),

    # 管理员 - 反馈管理
    (r"/api/admin/feedbacks", AdminFeedbackListHandler),
    (r"/api/admin/feedbacks/([0-9]+)/delete", AdminFeedbackDeleteHandler),
]
