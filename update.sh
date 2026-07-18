#!/bin/bash
# 搜书机器人 - 服务器更新脚本
# 用法: bash update.sh
# 部署路径: /opt/booksite/

set -e

DEPLOY_DIR="/opt/booksite"
cd "$DEPLOY_DIR"

echo "=== 搜书机器人更新 ==="

# 1. 拉取最新代码
echo "📦 拉取代码..."
git pull origin main

# 2. 安装后端依赖
echo "📦 安装后端依赖..."
cd backend
composer install --no-dev --optimize-autoloader 2>/dev/null || echo "⚠️  composer install 跳过（如未安装 composer 请忽略）"

# 3. 运行数据库迁移
echo "🗄️  运行迁移..."
php artisan migrate --force 2>/dev/null || echo "⚠️  迁移跳过"

# 4. 构建前端
echo "🔨 构建前端..."
cd ../frontend
npm install --silent
npm run build

# 5. 部署前端到 public
echo "🚀 部署前端..."
rm -rf ../backend/public/index.html ../backend/public/assets/
cp -r dist/* ../backend/public/

# 6. 清理缓存
echo "🧹 清理缓存..."
cd ../backend
php artisan config:clear 2>/dev/null
php artisan route:clear 2>/dev/null
php artisan view:clear 2>/dev/null

# 7. 设置权限
chmod -R 777 "$DEPLOY_DIR/data" 2>/dev/null
chmod -R 755 storage bootstrap/cache 2>/dev/null

echo "✅ 更新完成！"
