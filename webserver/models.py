#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""数据库模型定义"""

import os
import json
import sqlite3
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from webserver.settings import CONF


class Database:
    """数据库连接管理"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.conn = sqlite3.connect(CONF['database'], check_same_thread=False)
            cls._instance.conn.row_factory = sqlite3.Row
        return cls._instance

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """执行 SQL"""
        cursor = self.conn.execute(sql, params)
        self.conn.commit()
        return cursor

    def fetchone(self, sql: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """查询单条记录"""
        cursor = self.conn.execute(sql, params)
        return cursor.fetchone()

    def fetchall(self, sql: str, params: tuple = ()) -> List[sqlite3.Row]:
        """查询多条记录"""
        cursor = self.conn.execute(sql, params)
        return cursor.fetchall()

    def close(self):
        """关闭连接"""
        self.conn.close()


def init_database():
    """初始化数据库表"""
    db = Database()

    # 用户表
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            salt VARCHAR(32) DEFAULT '',
            name VARCHAR(100),
            email VARCHAR(200),
            avatar VARCHAR(200),
            admin BOOLEAN DEFAULT FALSE,
            active BOOLEAN DEFAULT FALSE,
            expiry_date DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login_at DATETIME
        )
    """)

    # 卡密表
    db.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code VARCHAR(32) UNIQUE NOT NULL,
            type VARCHAR(20) NOT NULL,
            duration_days INTEGER NOT NULL,
            used BOOLEAN DEFAULT FALSE,
            used_by INTEGER,
            used_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME,
            FOREIGN KEY (used_by) REFERENCES users(id)
        )
    """)

    # 书籍元数据表
    db.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(500) NOT NULL,
            author VARCHAR(200),
            file_path TEXT NOT NULL,
            file_size INTEGER,
            file_format VARCHAR(10),
            cover_path TEXT,
            description TEXT,
            tags TEXT,
            category VARCHAR(100),
            indexed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 为书名和作者添加索引，加速模糊查询
    db.execute("CREATE INDEX IF NOT EXISTS idx_books_title ON books(title)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_books_author ON books(author)")

    # 系统设置表
    db.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key VARCHAR(100) UNIQUE NOT NULL,
            value TEXT DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 用户反馈表
    db.execute("""
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            content TEXT NOT NULL,
            contact VARCHAR(200) DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # 用户下载记录表
    db.execute("""
        CREATE TABLE IF NOT EXISTS user_downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    """)

    # 创建默认管理员账号
    create_default_admin()


def create_default_admin():
    """创建默认管理员账号"""
    db = Database()

    # 检查是否已有管理员
    row = db.fetchone("SELECT id FROM users WHERE admin = TRUE LIMIT 1")
    if row:
        return

    # 创建默认管理员
    username = CONF['admin_username']
    password = CONF['admin_password']
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    db.execute(
        """INSERT INTO users (username, password_hash, name, admin, active, expiry_date)
           VALUES (?, ?, ?, TRUE, TRUE, ?)""",
        (username, password_hash, '管理员', datetime.now() + timedelta(days=36500))
    )


class User:
    """用户模型"""

    def __init__(self, row: Optional[sqlite3.Row] = None):
        if row:
            self.id = row['id']
            self.username = row['username']
            self.password_hash = row['password_hash']
            self.salt = row['salt']
            self.name = row['name']
            self.email = row['email']
            self.avatar = row['avatar']
            self.admin = bool(row['admin'])
            self.active = bool(row['active'])
            # 处理 SQLite 返回的字符串日期
            expiry = row['expiry_date']
            if expiry and isinstance(expiry, str):
                try:
                    self.expiry_date = datetime.fromisoformat(expiry)
                except ValueError:
                    self.expiry_date = None
            else:
                self.expiry_date = expiry

            created = row['created_at']
            if created and isinstance(created, str):
                try:
                    self.created_at = datetime.fromisoformat(created)
                except ValueError:
                    self.created_at = None
            else:
                self.created_at = created

            updated = row['updated_at']
            if updated and isinstance(updated, str):
                try:
                    self.updated_at = datetime.fromisoformat(updated)
                except ValueError:
                    self.updated_at = None
            else:
                self.updated_at = updated

            last_login = row['last_login_at']
            if last_login and isinstance(last_login, str):
                try:
                    self.last_login_at = datetime.fromisoformat(last_login)
                except ValueError:
                    self.last_login_at = None
            else:
                self.last_login_at = last_login
        else:
            self.id = None
            self.username = ''
            self.password_hash = ''
            self.salt = ''
            self.name = ''
            self.email = ''
            self.avatar = ''
            self.admin = False
            self.active = False
            self.expiry_date = None
            self.created_at = None
            self.updated_at = None
            self.last_login_at = None

    @classmethod
    def get_by_id(cls, user_id: int) -> Optional['User']:
        """根据 ID 获取用户"""
        db = Database()
        row = db.fetchone("SELECT * FROM users WHERE id = ?", (user_id,))
        return cls(row) if row else None

    @classmethod
    def get_by_username(cls, username: str) -> Optional['User']:
        """根据用户名获取用户"""
        db = Database()
        row = db.fetchone("SELECT * FROM users WHERE username = ?", (username.lower(),))
        return cls(row) if row else None

    @classmethod
    def create(cls, username: str, password: str, name: str = '', email: str = '') -> 'User':
        """创建用户"""
        db = Database()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cursor = db.execute(
            """INSERT INTO users (username, password_hash, name, email, active)
               VALUES (?, ?, ?, ?, FALSE)""",
            (username.lower(), password_hash, name, email)
        )

        return cls.get_by_id(cursor.lastrowid)

    def verify_password(self, password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def update_password(self, password: str):
        """更新密码"""
        db = Database()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db.execute(
            "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (password_hash, self.id)
        )

    def activate(self, expiry_date: datetime):
        """激活用户"""
        db = Database()
        db.execute(
            "UPDATE users SET active = TRUE, expiry_date = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (expiry_date, self.id)
        )
        self.active = True
        self.expiry_date = expiry_date

    def extend_expiry(self, days: int):
        """延长有效期"""
        now = datetime.now()
        if self.expiry_date and self.expiry_date > now:
            new_expiry = self.expiry_date + timedelta(days=days)
        else:
            new_expiry = now + timedelta(days=days)

        db = Database()
        db.execute(
            "UPDATE users SET expiry_date = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_expiry, self.id)
        )
        self.expiry_date = new_expiry

    def update_last_login(self):
        """更新最后登录时间"""
        db = Database()
        db.execute(
            "UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = ?",
            (self.id,)
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'avatar': self.avatar,
            'admin': self.admin,
            'active': self.active,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Card:
    """卡密模型"""

    def __init__(self, row: Optional[sqlite3.Row] = None):
        if row:
            self.id = row['id']
            self.code = row['code']
            self.type = row['type']
            self.duration_days = row['duration_days']
            self.used = bool(row['used'])
            self.used_by = row['used_by']

            # 处理 SQLite 返回的字符串日期
            used_at = row['used_at']
            if used_at and isinstance(used_at, str):
                try:
                    self.used_at = datetime.fromisoformat(used_at)
                except ValueError:
                    self.used_at = None
            else:
                self.used_at = used_at

            created = row['created_at']
            if created and isinstance(created, str):
                try:
                    self.created_at = datetime.fromisoformat(created)
                except ValueError:
                    self.created_at = None
            else:
                self.created_at = created

            expires = row['expires_at']
            if expires and isinstance(expires, str):
                try:
                    self.expires_at = datetime.fromisoformat(expires)
                except ValueError:
                    self.expires_at = None
            else:
                self.expires_at = expires
        else:
            self.id = None
            self.code = ''
            self.type = 'register'
            self.duration_days = 30
            self.used = False
            self.used_by = None
            self.used_at = None
            self.created_at = None
            self.expires_at = None

    @classmethod
    def get_by_code(cls, code: str) -> Optional['Card']:
        """根据卡密获取"""
        db = Database()
        row = db.fetchone("SELECT * FROM cards WHERE code = ?", (code,))
        return cls(row) if row else None

    @classmethod
    def create(cls, code: str, type: str, duration_days: int) -> 'Card':
        """创建卡密"""
        db = Database()
        cursor = db.execute(
            "INSERT INTO cards (code, type, duration_days) VALUES (?, ?, ?)",
            (code, type, duration_days)
        )
        return cls.get_by_id(cursor.lastrowid)

    @classmethod
    def get_by_id(cls, card_id: int) -> Optional['Card']:
        """根据 ID 获取卡密"""
        db = Database()
        row = db.fetchone("SELECT * FROM cards WHERE id = ?", (card_id,))
        return cls(row) if row else None

    def redeem(self, user_id: int) -> bool:
        """兑换卡密"""
        if self.used:
            return False

        if self.expires_at and self.expires_at < datetime.now():
            return False

        db = Database()
        db.execute(
            """UPDATE cards SET used = TRUE, used_by = ?, used_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (user_id, self.id)
        )
        self.used = True
        self.used_by = user_id
        self.used_at = datetime.now()
        return True

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'code': self.code,
            'type': self.type,
            'duration_days': self.duration_days,
            'used': self.used,
            'used_by': self.used_by,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
        }


class Book:
    """书籍模型"""

    def __init__(self, row: Optional[sqlite3.Row] = None):
        if row:
            self.id = row['id']
            self.title = row['title']
            self.author = row['author']
            self.file_path = row['file_path']
            self.file_size = row['file_size']
            self.file_format = row['file_format']
            self.cover_path = row['cover_path']
            self.description = row['description']
            self.tags = row['tags']
            self.category = row['category']

            # 处理 SQLite 返回的字符串日期
            indexed = row['indexed_at']
            if indexed and isinstance(indexed, str):
                try:
                    self.indexed_at = datetime.fromisoformat(indexed)
                except ValueError:
                    self.indexed_at = None
            else:
                self.indexed_at = indexed

            created = row['created_at']
            if created and isinstance(created, str):
                try:
                    self.created_at = datetime.fromisoformat(created)
                except ValueError:
                    self.created_at = None
            else:
                self.created_at = created
        else:
            self.id = None
            self.title = ''
            self.author = ''
            self.file_path = ''
            self.file_size = 0
            self.file_format = ''
            self.cover_path = ''
            self.description = ''
            self.tags = ''
            self.category = ''
            self.indexed_at = None
            self.created_at = None

    @classmethod
    def get_by_id(cls, book_id: int) -> Optional['Book']:
        """根据 ID 获取书籍"""
        db = Database()
        row = db.fetchone("SELECT * FROM books WHERE id = ?", (book_id,))
        return cls(row) if row else None

    @classmethod
    def create(cls, title: str, author: str, file_path: str, file_size: int = 0,
               file_format: str = '', description: str = '', category: str = '') -> 'Book':
        """创建书籍记录"""
        db = Database()
        cursor = db.execute(
            """INSERT INTO books (title, author, file_path, file_size, file_format, description, category)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (title, author, file_path, file_size, file_format, description, category)
        )
        return cls.get_by_id(cursor.lastrowid)

    @classmethod
    def get_all(cls, page: int = 1, size: int = 20) -> List['Book']:
        """获取所有书籍（分页）"""
        db = Database()
        offset = (page - 1) * size
        rows = db.fetchall(
            "SELECT * FROM books ORDER BY title ASC LIMIT ? OFFSET ?",
            (size, offset)
        )
        return [cls(row) for row in rows]

    @classmethod
    def search(cls, query: str, page: int = 1, size: int = 20) -> dict:
        """模糊搜索书籍"""
        db = Database()
        offset = (page - 1) * size

        # 构建模糊查询条件
        keywords = query.split()
        conditions = []
        params = []

        for kw in keywords:
            conditions.append("(title LIKE ? OR author LIKE ?)")
            params.extend([f"%{kw}%", f"%{kw}%"])

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # 查询总数
        count_sql = f"SELECT COUNT(*) as count FROM books WHERE {where_clause}"
        total_row = db.fetchone(count_sql, tuple(params))

        # 查询分页数据
        sql = f"""
            SELECT * FROM books
            WHERE {where_clause}
            ORDER BY title ASC
            LIMIT ? OFFSET ?
        """
        params.extend([size, offset])
        rows = db.fetchall(sql, tuple(params))

        books = [cls(row) for row in rows]

        return {
            "total": total_row['count'],
            "items": [book.to_dict() for book in books],
            "page": page,
            "size": size,
        }

    @classmethod
    def get_total_count(cls) -> int:
        """获取书籍总数"""
        db = Database()
        row = db.fetchone("SELECT COUNT(*) as count FROM books")
        return row['count']

    @classmethod
    def delete_by_id(cls, book_id: int):
        """根据 ID 删除书籍"""
        db = Database()
        db.execute("DELETE FROM books WHERE id = ?", (book_id,))

    @classmethod
    def clear_all(cls):
        """清空所有书籍"""
        db = Database()
        db.execute("DELETE FROM books")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_format': self.file_format,
            'cover_path': self.cover_path,
            'description': self.description,
            'tags': self.tags,
            'category': self.category,
            'indexed_at': self.indexed_at.isoformat() if self.indexed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class UserDownload:
    """用户下载记录模型"""

    @classmethod
    def record_download(cls, user_id: int, book_id: int):
        """记录用户下载"""
        db = Database()
        db.execute(
            "INSERT INTO user_downloads (user_id, book_id) VALUES (?, ?)",
            (user_id, book_id)
        )

    @classmethod
    def get_download_count(cls, user_id: int) -> int:
        """获取用户今日下载次数"""
        db = Database()
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        row = db.fetchone(
            """SELECT COUNT(*) as count FROM user_downloads
               WHERE user_id = ? AND date(downloaded_at) = date('now')""",
            (user_id,)
        )
        return row['count'] if row else 0

    @classmethod
    def get_total_download_count(cls, user_id: int) -> int:
        """获取用户总下载次数"""
        db = Database()
        row = db.fetchone(
            "SELECT COUNT(*) as count FROM user_downloads WHERE user_id = ?",
            (user_id,)
        )
        return row['count'] if row else 0
