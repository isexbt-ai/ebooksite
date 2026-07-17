# 1Panel Docker Compose 部署方案

## 快速部署步骤

### 1. 准备代码

在服务器上执行：

```bash
# 克隆代码
git clone https://github.com/isexbt-ai/ebooksite.git /opt/ebooksite
cd /opt/ebooksite

# 构建并启动
docker-compose up -d
```

### 2. 1Panel 中配置

**进入 1Panel → 容器 → 编排 → 创建编排**

- **名称**：`ebooksite`
- **路径**：`/opt/ebooksite`
- **Compose 文件**：`docker-compose.yml`

点击**创建并启动**。

### 3. 配置反向代理

**进入 1Panel → 网站 → 创建网站 → 反向代理**

- **域名**：`your-domain.com`
- **代理地址**：`http://127.0.0.1:8080`

点击**保存**，然后**申请 HTTPS 证书**。

### 4. 完成

访问 `https://your-domain.com` 即可。

---

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SECRET_KEY` | Cookie 加密密钥 | `your-secret-key-here-change-this` |
| `ADMIN_USERNAME` | 管理员账号 | `admin` |
| `ADMIN_PASSWORD` | 管理员密码 | `admin123` |
| `PORT` | 服务端口 | `8080` |

---

## 数据持久化

`data/` 目录挂载到容器内 `/app/data`，包含：
- `books.db` - SQLite 数据库
- `books/` - 书籍文件
- `covers/` - 封面图片

---

## 更新部署

```bash
cd /opt/ebooksite
git pull origin main
docker-compose down
docker-compose up -d --build
```
