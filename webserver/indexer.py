#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""书籍扫描与索引器

支持自动扫描目录，提取书籍元数据并建立数据库索引。
"""

import os
import re
import logging
from pathlib import Path
from typing import Optional, List, Tuple

from webserver.models import Database, Book
from webserver.settings import CONF

logger = logging.getLogger(__name__)

# 支持的书籍格式
SUPPORTED_FORMATS = ('.epub', '.pdf', '.txt', '.mobi', '.azw3')


def extract_metadata_from_filename(filename: str) -> Tuple[str, Optional[str]]:
    """从文件名提取书名和作者

    支持格式：
    - 书名_作者.epub
    - 书名 - 作者.epub
    - 书名.epub

    Args:
        filename: 文件名（含扩展名）

    Returns:
        (书名, 作者) 元组，作者可能为 None
    """
    name = Path(filename).stem

    # 尝试匹配 "书名_作者" 格式
    if '_' in name:
        parts = name.split('_', 1)
        return parts[0].strip(), parts[1].strip() if len(parts) > 1 else None

    # 尝试匹配 "书名 - 作者" 格式
    if ' - ' in name:
        parts = name.split(' - ', 1)
        return parts[0].strip(), parts[1].strip() if len(parts) > 1 else None

    return name.strip(), None


def get_file_format(filename: str) -> str:
    """获取文件格式（小写扩展名）"""
    return os.path.splitext(filename)[1].lower()


def scan_books_directory(books_dir: str) -> List[dict]:
    """扫描书籍目录，返回书籍元数据列表

    Args:
        books_dir: 书籍目录路径

    Returns:
        书籍元数据字典列表
    """
    books = []

    if not os.path.exists(books_dir):
        logger.warning(f"书籍目录不存在: {books_dir}")
        return books

    for root, dirs, files in os.walk(books_dir):
        for file in files:
            if file.lower().endswith(SUPPORTED_FORMATS):
                file_path = os.path.join(root, file)
                title, author = extract_metadata_from_filename(file)
                file_size = os.path.getsize(file_path)
                file_format = get_file_format(file)

                books.append({
                    'title': title or file,
                    'author': author or '',
                    'file_path': file_path,
                    'file_size': file_size,
                    'file_format': file_format,
                })

    return books


def index_book(db: Database, file_path: str) -> Optional[int]:
    """索引单本书，返回书籍 ID

    Args:
        db: 数据库连接
        file_path: 文件路径

    Returns:
        书籍 ID，如果失败则返回 None
    """
    try:
        filename = os.path.basename(file_path)
        title, author = extract_metadata_from_filename(filename)
        file_size = os.path.getsize(file_path)
        file_format = get_file_format(filename)

        # 检查是否已存在
        existing = db.fetchone(
            "SELECT id FROM books WHERE file_path = ?",
            (file_path,)
        )
        if existing:
            return existing['id']

        # 插入数据库
        cursor = db.execute(
            """INSERT INTO books (title, author, file_path, file_size, file_format)
               VALUES (?, ?, ?, ?, ?)""",
            (title or filename, author or '', file_path, file_size, file_format)
        )

        return cursor.lastrowid
    except Exception as e:
        logger.error(f"索引书籍失败 {file_path}: {e}")
        return None


def scan_and_index(books_dir: str, full_rebuild: bool = False) -> dict:
    """扫描目录并建立索引

    Args:
        books_dir: 书籍目录路径
        full_rebuild: 是否完全重建索引（清空后重新扫描）

    Returns:
        {"scanned": 新增数量, "total": 总数量, "message": 状态消息}
    """
    db = Database()

    if full_rebuild:
        db.execute("DELETE FROM books")
        logger.info("清空书籍索引，开始完全重建")

    # 获取已索引的文件路径集合
    existing_paths = set()
    if not full_rebuild:
        rows = db.fetchall("SELECT file_path FROM books")
        existing_paths = {row['file_path'] for row in rows}

    # 扫描目录
    scanned_count = 0
    for root, dirs, files in os.walk(books_dir):
        for file in files:
            if file.lower().endswith(SUPPORTED_FORMATS):
                file_path = os.path.join(root, file)

                # 跳过已索引的文件
                if file_path in existing_paths:
                    continue

                # 提取元数据并插入数据库
                book_id = index_book(db, file_path)
                if book_id:
                    scanned_count += 1

    # 获取总数
    total = Book.get_total_count()

    message = f"扫描完成，新增 {scanned_count} 本书籍"
    if full_rebuild:
        message = f"完全重建索引，共 {total} 本书籍"

    logger.info(message)
    return {
        "scanned": scanned_count,
        "total": total,
        "message": message,
    }


def get_books_dir() -> str:
    """获取书籍目录路径"""
    return CONF.get('books_dir', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'books'))
