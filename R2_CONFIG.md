# Cloudflare R2 存储配置指南

## 配置步骤

### 1. 登录 Cloudflare 控制台

访问: https://dash.cloudflare.com

### 2. 创建 R2 存储桶

1. 左侧菜单 → R2 对象存储
2. 点击 创建存储桶
3. 填写信息：

| 配置项 | 值 |
|--------|-----|
| 存储桶名称 | booksite-novels |
| 位置 | 自动（Automatic） |

### 3. 获取 API 令牌

1. 进入 R2 对象存储 → 管理 R2 API 令牌
2. 点击 创建 API 令牌
3. 权限选择：对象读和写
4. 记录以下信息：

```
Account ID:          ________________________________
Access Key ID:       ________________________________
Secret Access Key:   ________________________________
R2 Endpoint:         https://<account-id>.r2.cloudflarestorage.com
```

### 4. 配置自定义域名（可选但推荐）

1. 进入存储桶 → 设置 → 公共访问
2. 启用 允许公共访问
3. 绑定自定义域名，例如：r2.yourdomain.com

---

## 填写配置

编辑 backend/.env 文件，填写以下信息：

```env
# ============================================
# Cloudflare R2 存储配置
# ============================================

# 从 Cloudflare 控制台获取
R2_ACCESS_KEY_ID=your-access-key-id-here
R2_SECRET_ACCESS_KEY=your-secret-access-key-here
R2_ACCOUNT_ID=your-account-id-here

# R2 端点（将 <account-id> 替换为你的 Account ID）
R2_ENDPOINT=https://<account-id>.r2.cloudflarestorage.com

# 存储桶名称
R2_BUCKET=booksite-novels

# 区域（保持 auto 即可）
R2_REGION=auto

# 公开访问 URL（使用自定义域名或 Public URL）
# 如果使用自定义域名: https://r2.yourdomain.com
# 如果使用默认 URL:   https://<account-id>.r2.cloudflarestorage.com/booksite-novels
R2_PUBLIC_URL=https://r2.yourdomain.com

# 预签名 URL 有效期（秒，默认 1 小时）
R2_PRESIGNED_URL_EXPIRES=3600
```

---

## 配置检查清单

- [ ] 已创建 R2 存储桶
- [ ] 已获取 Access Key ID
- [ ] 已获取 Secret Access Key
- [ ] 已获取 Account ID
- [ ] 已配置自定义域名（可选）
- [ ] 已在 .env 中填写所有配置
- [ ] 已运行 php artisan config:clear 清除配置缓存

---

## 快速验证

配置完成后，运行以下命令验证：

```bash
cd /opt/1panel/apps/openresty/openresty/www/sites/book/index/backend
php artisan r2:test
```

如果看到 R2 连接成功！，说明配置正确。
