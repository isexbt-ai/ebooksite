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
from webserver.handlers.batch_download import (
    SourceCategoriesHandler,
    BatchDownloadHandler,
    BatchDownloadStatusHandler,
    BatchDownloadListHandler,
    BatchDownloadStopHandler,
)
from webserver.handlers.admin import (
    AdminStatsHandler,
    AdminUsersHandler,
    AdminDeleteUserHandler,
    AdminCardsHandler,
    AdminSourcesHandler,
    AdminDeleteSourceHandler,
    AdminToggleSourceHandler,
    AdminBooksHandler,
    AdminDeleteBookHandler,
)
from webserver.handlers.user import (
    UserSettingsHandler,
    UserPasswordHandler,
    BooksHandler,
    DeleteBookHandler,
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

    # 搜索下载
    (r"/api/search", SearchHandler),
    (r"/api/download", DownloadHandler),
    (r"/api/download/([0-9]+)/status", DownloadStatusHandler),
    (r"/api/download/history", DownloadHistoryHandler),

    # 本地书籍库
    (r"/api/books", BooksHandler),
    (r"/api/books/([0-9]+)/delete", DeleteBookHandler),

    # 用户设置
    (r"/api/user/settings", UserSettingsHandler),
    (r"/api/user/password", UserPasswordHandler),

    # 系统设置（公开）
    (r"/api/settings/buy_link", BuyLinkHandler),

    # 用户反馈
    (r"/api/feedback", FeedbackHandler),

    # 管理员相关
    (r"/api/admin/cards/generate", GenerateCardsHandler),
    (r"/api/admin/stats", AdminStatsHandler),
    (r"/api/admin/users", AdminUsersHandler),
    (r"/api/admin/users/([0-9]+)/delete", AdminDeleteUserHandler),
    (r"/api/admin/cards", AdminCardsHandler),
    (r"/api/admin/sources", AdminSourcesHandler),
    (r"/api/admin/sources/([0-9]+)/delete", AdminDeleteSourceHandler),
    (r"/api/admin/sources/([0-9]+)/toggle", AdminToggleSourceHandler),
    (r"/api/admin/books", AdminBooksHandler),
    (r"/api/admin/books/([0-9]+)/delete", AdminDeleteBookHandler),

    # 管理员 - 系统设置
    (r"/api/admin/settings", AdminSettingsHandler),

    # 批量下载
    (r"/api/admin/sources/([0-9]+)/categories", SourceCategoriesHandler),
    (r"/api/admin/batch-download", BatchDownloadHandler),
    (r"/api/admin/batch-download/([0-9]+)/status", BatchDownloadStatusHandler),
    (r"/api/admin/batch-download/tasks", BatchDownloadListHandler),
    (r"/api/admin/batch-download/([0-9]+)/stop", BatchDownloadStopHandler),
    (r"/api/admin/feedbacks", AdminFeedbackListHandler),
    (r"/api/admin/feedbacks/([0-9]+)/delete", AdminFeedbackDeleteHandler),
]
