# 搜书机器人 - 精简版图书管理系统

支持卡密注册、网络书库搜索下载、本地书籍管理。

## 技术栈

- **后端**: Laravel 10 + PHP 8.1+
- **前端**: Vue 3 + Vite + Vuetify 3 + Pinia
- **数据库**: SQLite（单文件，无需额外配置）

## 1Panel 面板部署（推荐）

### 1. 创建 PHP 网站

**1Panel → 网站 → 创建网站 → 运行环境**

- **域名**: `your-domain.com`
- **根目录**: `/opt/booksite/backend/public`
- **PHP 版本**: `8.1+`
- **运行方式**: `PHP-FPM`

### 2. 上传代码

```bash
cd /opt
# 上传代码到 /opt/booksite
```

### 3. 安装依赖

```bash
cd /opt/booksite/backend
composer install --no-dev --optimize-autoloader
```

### 4. 配置环境变量

```bash
cp .env.example .env
php artisan key:generate
```

编辑 `.env`：

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

### 5. 创建数据目录

```bash
mkdir -p /opt/booksite/data
chmod 777 /opt/booksite/data
```

### 6. 运行迁移

```bash
php artisan migrate --force
```

### 7. 构建前端

```bash
cd /opt/booksite/frontend
npm install
npm run build
cp -r dist/* /opt/booksite/backend/public/
```

### 8. 配置伪静态

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

### 9. 配置 HTTPS

**1Panel → 网站 → 设置 → HTTPS → 申请证书**

---

## 目录结构

```
/opt/booksite/
├── backend/           # Laravel 后端
│   ├── app/
│   ├── bootstrap/
│   ├── config/
│   ├── database/
│   ├── public/          # ← Web 根目录指向这里
│   │   ├── index.php
│   │   └── ...
│   ├── routes/
│   ├── storage/
│   ├── vendor/
│   └── ...
├── frontend/          # Vue 3 前端（构建后复制到 public）
├── data/              # SQLite 数据库和上传文件
│   ├── books.db
│   └── books/
└── ...
```

---

## 一键部署脚本

创建 `/opt/booksite/deploy.sh`：

```bash
#!/bin/bash
set -e

echo "🚀 开始部署搜书机器人..."

# 安装后端依赖
echo "📦 安装后端依赖..."
cd /opt/booksite/backend
composer install --no-dev --optimize-autoloader

# 生成密钥
php artisan key:generate

# 运行迁移
php artisan migrate --force

# 构建前端
echo "🔨 构建前端..."
cd /opt/booksite/frontend
npm install
npm run build
cp -r dist/* /opt/booksite/backend/public/

# 设置权限
chmod -R 777 /opt/booksite/data

echo "✅ 部署完成！"
```

执行：
```bash
bash /opt/booksite/deploy.sh
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

---

## License

MIT
