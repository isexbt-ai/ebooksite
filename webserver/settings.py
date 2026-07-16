#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
系统配置
"""

import os
import secrets

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# 数据库路径
DATABASE_PATH = os.path.join(DATA_DIR, 'books.db')

# 文件存储路径
BOOKS_DIR = os.path.join(DATA_DIR, 'books')
COVERS_DIR = os.path.join(DATA_DIR, 'covers')
UPLOADS_DIR = os.path.join(DATA_DIR, 'uploads')

# 确保子目录存在
for d in [BOOKS_DIR, COVERS_DIR, UPLOADS_DIR]:
    os.makedirs(d, exist_ok=True)

# 配置字典
CONF = {
    # 基础配置
    'port': int(os.environ.get('PORT', 8080)),
    'debug': os.environ.get('DEBUG', 'false').lower() == 'true',
    'cookie_secret': os.environ.get('SECRET_KEY', secrets.token_hex(32)),
    'cookie_expire': 7 * 24 * 3600,  # 7天

    # 数据库
    'database': DATABASE_PATH,

    # 文件路径
    'books_dir': BOOKS_DIR,
    'covers_dir': COVERS_DIR,
    'uploads_dir': UPLOADS_DIR,

    # 上传配置
    'max_upload_size': 100 * 1024 * 1024,  # 100MB
    'upload_chunk_size': 4 * 1024 * 1024,  # 4MB

    # 管理员配置
    'admin_username': os.environ.get('ADMIN_USERNAME', 'admin'),
    'admin_password': os.environ.get('ADMIN_PASSWORD', 'admin123'),

    # 注册配置
    'allow_register': True,
    'require_card_for_register': True,  # 注册是否需要卡密

    # 主题配置
    'theme_path': os.path.join(BASE_DIR, 'app', '.output', 'public'),

    # 国际化
    'default_language': 'zh',
    'supported_languages': ['zh', 'en'],
}
