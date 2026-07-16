# BookSite - 精简版图书管理系统

基于 Talebook 的精简版图书管理系统，支持卡密注册、网络书库搜索下载。

## 功能特性

- 账号密码注册/登录
- 卡密系统（注册卡/续费卡）
- 网络书库搜索下载
- 本地书籍管理
- 管理后台（卡密管理、用户管理、书源管理）
- 主题切换（浅色/深色）
- 多语言支持（中文/英文）

## 技术栈

- 前端：Nuxt 4 + Vue 3 + Vuetify 3 + Pinia
- 后端：Python 3.11 + Tornado 6.5 + SQLite
- 部署：Docker + docker-compose

## 快速开始

### 使用 Docker 部署

```bash
# 克隆项目
git clone <repository-url>
cd booksite

# 启动服务
docker-compose up -d

# 访问 http://localhost:8080
```

### 手动部署

```bash
# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖
cd app
npm install
npm run build
cd ..

# 启动服务
python server.py
```

## 默认账号

- 用户名：admin
- 密码：admin123

## 项目结构

```
booksite/
├── app/                    # 前端 (Nuxt 4)
│   ├── components/         # 公共组件
│   ├── pages/             # 页面路由
│   ├── plugins/            # 插件
│   ├── stores/             # Pinia 状态管理
│   └── i18n/               # 国际化
├── webserver/              # 后端 (Tornado)
│   ├── handlers/           # API 路由处理器
│   ├── models.py           # 数据库模型
│   └── settings.py         # 系统配置
├── tests/                  # 测试
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 开发计划

1. 基础框架搭建 ✅
2. 认证系统（登录/注册/卡密）
3. 网络书库搜索下载
4. 书籍管理
5. 管理后台
6. 优化与部署

## License

MIT
