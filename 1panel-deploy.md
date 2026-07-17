# 1Panel 部署方案

## 方式一：Docker Compose 部署（推荐）

### 1. 准备代码

```bash
# 克隆代码
git clone https://github.com/isexbt-ai/ebooksite.git /opt/ebooksite
cd /opt/ebooksite

# 构建前端
cd app
npm install
npm run build
cd ..
```

### 2. 修改配置

编辑 `docker-compose.yml`：

```yaml
version: "3.8"

services:
  ebooksite:
    build: .
    restart: always
    ports:
      - "8080:8080"    # 映射到宿主机 8080 端口
    volumes:
      - ./data:/app/data    # 数据持久化
      - ./app/.output:/app/app/.output  # 前端构建产物
    environment:
      - TZ=Asia/Shanghai
      - SECRET_KEY=your-secret-key-here-change-this
      - ADMIN_USERNAME=admin
      - ADMIN_PASSWORD=your-strong-password
      - PORT=8080
```

编辑 `Dockerfile`，修改端口：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "server.py"]
```

### 3. 1Panel 部署步骤

1. **进入 1Panel → 容器 → 编排**
2. **创建编排**
   - 名称：`ebooksite`
   - 路径：`/opt/ebooksite`
   - 选择 `docker-compose.yml`
3. **点击创建并启动**

### 4. 配置反向代理

1. **进入 1Panel → 网站 → 创建网站**
2. **选择反向代理**
   - 域名：`your-domain.com`
   - 代理地址：`http://127.0.0.1:8080`
3. **开启 HTTPS**（申请证书）

---

## 方式二：1Panel 应用商店部署（自定义）

### 创建应用目录

```bash
mkdir -p /opt/1panel/apps/local/ebooksite
```

### 创建 data.yml

```yaml
additionalProperties:
  formFields:
    - default: 8080
      edit: true
      envKey: PANEL_APP_PORT_HTTP
      labelEn: HTTP Port
      labelZh: HTTP 端口
      required: true
      rule: paramPort
      type: number
    - default: admin
      edit: true
      envKey: ADMIN_USERNAME
      labelEn: Admin Username
      labelZh: 管理员账号
      required: true
      type: text
    - default: admin123
      edit: true
      envKey: ADMIN_PASSWORD
      labelEn: Admin Password
      labelZh: 管理员密码
      required: true
      type: password
    - default: your-secret-key
      edit: true
      envKey: SECRET_KEY
      labelEn: Secret Key
      labelZh: 安全密钥
      required: true
      type: password
```

### 创建 docker-compose.yml

```yaml
services:
  ebooksite:
    image: isexbt/ebooksite:latest
    container_name: ${CONTAINER_NAME}
    restart: always
    ports:
      - ${PANEL_APP_PORT_HTTP}:8080
    volumes:
      - ./data:/app/data
    environment:
      - TZ=Asia/Shanghai
      - SECRET_KEY=${SECRET_KEY}
      - ADMIN_USERNAME=${ADMIN_USERNAME}
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
      - PORT=8080
    networks:
      - 1panel-network

networks:
  1panel-network:
    external: true
```

### 导入到 1Panel

1. **进入 1Panel → 应用商店 → 本地应用**
2. **导入应用**，选择上述目录
3. **安装应用**

---

## 方式三：直接容器运行（最简单）

### 1. 构建镜像

```bash
cd /opt/ebooksite

# 构建前端
cd app && npm install && npm run build && cd ..

# 构建 Docker 镜像
docker build -t ebooksite:latest .
```

### 2. 1Panel 中创建容器

1. **进入 1Panel → 容器 → 容器**
2. **创建容器**
   - 镜像：`ebooksite:latest`
   - 端口映射：`8080 → 8080`
   - 挂载卷：`/opt/ebooksite/data → /app/data`
   - 环境变量：
     - `SECRET_KEY=your-secret-key`
     - `ADMIN_USERNAME=admin`
     - `ADMIN_PASSWORD=your-password`
     - `PORT=8080`
3. **启动容器**

### 3. 配置网站

1. **创建网站 → 反向代理**
2. **域名**：`your-domain.com`
3. **代理地址**：`http://127.0.0.1:8080`
4. **启用 HTTPS**

---

## 数据备份

### 自动备份脚本

```bash
#!/bin/bash
# /opt/backup-ebooksite.sh

BACKUP_DIR="/opt/backups/ebooksite"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p ${BACKUP_DIR}

# 备份数据库和书籍文件
tar czf ${BACKUP_DIR}/ebooksite_${DATE}.tar.gz -C /opt/ebooksite data/

# 保留最近 7 天备份
find ${BACKUP_DIR} -name "ebooksite_*.tar.gz" -mtime +7 -delete

echo "备份完成: ${BACKUP_DIR}/ebooksite_${DATE}.tar.gz"
```

### 添加到 1Panel 计划任务

1. **进入 1Panel → 计划任务**
2. **创建任务**
   - 类型：Shell 脚本
   - 名称：ebooksite 备份
   - 脚本内容：上面的备份脚本
   - 执行周期：每天 3:00

---

## 更新部署

```bash
# 拉取最新代码
cd /opt/ebooksite
git pull origin main

# 重新构建前端
cd app && npm install && npm run build && cd ..

# 重启容器
docker-compose down
docker-compose up -d
```

---

## 目录结构

```
/opt/ebooksite/
├── app/                    # Nuxt 前端
│   ├── .output/           # 构建产物
│   ├── pages/
│   └── ...
├── webserver/             # Tornado 后端
│   ├── handlers/
│   ├── models.py
│   └── ...
├── data/                  # 数据目录（需持久化）
│   ├── books.db          # SQLite 数据库
│   ├── books/            # 书籍文件
│   └── covers/           # 封面图片
├── server.py             # 启动入口
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `PORT` | 服务端口 | `8080` |
| `SECRET_KEY` | Cookie 加密密钥 | 随机生成 |
| `ADMIN_USERNAME` | 管理员账号 | `admin` |
| `ADMIN_PASSWORD` | 管理员密码 | `admin123` |
| `TZ` | 时区 | `Asia/Shanghai` |
| `DEBUG` | 调试模式 | `false` |

---

## 常见问题

### 1. 前端 404
确保 `app/.output` 目录存在且已构建：
```bash
cd app && npm run build
```

### 2. 数据库权限
确保容器有写入权限：
```bash
chmod 777 /opt/ebooksite/data
```

### 3. 端口冲突
修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "9090:8080"  # 宿主机 9090 映射到容器 8080
```
