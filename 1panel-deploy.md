# 搜书机器人 - 1Panel 部署指南

## 部署方式：1Panel 面板直接上传代码

### 1. 打包代码

在本地执行：

```bash
cd /home/isecbt/work/搜书机器人
zip -r booksite.zip backend/ frontend/ data/ 1panel-deploy.md
```

### 2. 上传到服务器

**1Panel → 文件 → 上传**

- 上传到 `/opt/booksite/`
- 解压：`unzip booksite.zip`

### 3. 创建 PHP 网站

**1Panel → 网站 → 创建网站 → 运行环境**

| 配置项 | 值 |
|--------|-----|
| 域名 | `your-domain.com` |
| 根目录 | `/opt/booksite/backend/public` |
| PHP 版本 | `8.1+` |
| 运行方式 | `PHP-FPM` |

### 4. 配置伪静态

**1Panel → 网站 → 设置 → 伪静态**

```nginx
location / {
    try_files $uri $uri/ /index.php?$query_string;
}

location ~ \\.php$ {
    fastcgi_pass unix:/tmp/php-cgi-81.sock;
    fastcgi_index index.php;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    include fastcgi_params;
}
```

### 5. 配置 HTTPS

**1Panel → 网站 → 设置 → HTTPS → 申请证书**

---

## 目录结构

```
/opt/booksite/
├── backend/           # Laravel 后端（已包含依赖和构建产物）
│   ├── app/
│   ├── bootstrap/
│   ├── config/
│   ├── database/
│   ├── public/          # ← Web 根目录指向这里
│   │   ├── index.php
│   │   ├── index.html     # ← 前端构建产物
│   │   └── assets/        # ← 前端资源
│   ├── routes/
│   ├── storage/
│   ├── vendor/          # ← PHP 依赖（已安装）
│   └── ...
├── frontend/          # Vue 3 前端源码（可选，已构建到 backend/public）
├── data/              # SQLite 数据库和上传文件
│   ├── books.db         # ← 数据库（已创建）
│   └── books/
└── 1panel-deploy.md   # 本文件
```

---

## 环境变量

编辑 `/opt/booksite/backend/.env`：

```env
APP_NAME=搜书机器人
APP_ENV=production
APP_KEY=base64:xxx
APP_DEBUG=false
APP_URL=https://your-domain.com

DB_CONNECTION=sqlite
DB_DATABASE=/opt/booksite/data/books.db

SANCTUM_STATEFUL_DOMAINS=your-domain.com
```

---

## 数据备份

创建 `/opt/booksite/backup.sh`：

```bash
#!/bin/bash

BACKUP_DIR="/opt/backups/booksite"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
cp /opt/booksite/data/books.db $BACKUP_DIR/books_${DATE}.db

# 备份书籍文件
tar -czf $BACKUP_DIR/books_${DATE}.tar.gz -C /opt/booksite data/books/

# 保留最近 7 天
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "备份完成: $DATE"
```

---

## 常见问题

### 1. SQLite 写入权限

```bash
chmod 777 /opt/booksite/data
```

### 2. 前端路由 404

确保伪静态配置正确，所有路由指向 `index.php`。

### 3. 跨域问题

确保 `SANCTUM_STATEFUL_DOMAINS` 配置正确。

### 4. 文件上传大小

在 PHP 配置中调整：
```ini
upload_max_filesize = 100M
post_max_size = 100M
```
