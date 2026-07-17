#!/bin/bash
# =============================================================================
# 搜书机器人 - 远程仓库更新脚本
# 功能：拉取远程仓库最新代码，自动构建前端，重启服务
# =============================================================================

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_DIR="/opt/ebooksite"
PROJECT_NAME="ebooksite"
GIT_BRANCH="main"
ENV_FILE=".env"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 生成随机密钥
generate_secret_key() {
    if command -v openssl &> /dev/null; then
        openssl rand -hex 32
    else
        python3 -c "import secrets; print(secrets.token_hex(32))"
    fi
}

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 未安装"
        exit 1
    fi
}

# 生成 .env 文件
generate_env_file() {
    if [ -f "$ENV_FILE" ]; then
        log_info ".env 文件已存在，跳过生成"
        return
    fi

    log_info "首次运行，生成 .env 配置文件..."

    SECRET_KEY=$(generate_secret_key)

    cat > "$ENV_FILE" << EOF
# 搜书机器人环境配置
# 首次运行自动生成，请勿删除

# 安全密钥（自动生成）
SECRET_KEY=${SECRET_KEY}

# 管理员账号（建议修改）
ADMIN_USERNAME=admin

# 管理员密码（强烈建议修改）
ADMIN_PASSWORD=admin123
EOF

    log_success ".env 文件已生成"
    log_warn "请编辑 .env 文件修改管理员密码！"
}

# 构建前端
build_frontend() {
    log_info "正在构建前端..."
    cd app

    # 检查 node_modules 是否存在
    if [ ! -d "node_modules" ]; then
        log_info "安装前端依赖..."
        npm install
    fi

    # 构建前端 - 限制内存使用，适配低内存服务器
    log_info "构建前端产物..."
    export NODE_OPTIONS="--max-old-space-size=768"
    if ! npm run build; then
        log_error "前端构建失败！"
        unset NODE_OPTIONS
        cd ..
        exit 1
    fi
    unset NODE_OPTIONS

    # 验证构建产物
    if [ ! -d ".output/public" ]; then
        log_error "构建产物目录不存在: app/.output/public"
        cd ..
        exit 1
    fi

    if [ ! -f ".output/public/index.html" ]; then
        log_error "构建产物不完整，缺少 index.html"
        cd ..
        exit 1
    fi

    cd ..
    log_success "前端构建完成"
}

# 主函数
main() {
    log_info "========================================"
    log_info "搜书机器人 - 远程仓库更新脚本"
    log_info "========================================"
    echo ""

    # 检查依赖
    check_command git
    check_command docker
    check_command docker-compose

    # 检查项目目录
    if [ ! -d "$PROJECT_DIR" ]; then
        log_error "项目目录不存在: $PROJECT_DIR"
        log_info "请先克隆仓库: git clone https://github.com/isexbt-ai/ebooksite.git $PROJECT_DIR"
        exit 1
    fi

    cd "$PROJECT_DIR"

    # 检查是否为 git 仓库
    if [ ! -d ".git" ]; then
        log_error "目录 $PROJECT_DIR 不是有效的 git 仓库"
        exit 1
    fi

    # 生成 .env 文件（首次运行）
    generate_env_file

    # 获取当前版本
    CURRENT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    log_info "当前版本: $CURRENT_COMMIT"

    # 拉取最新代码
    log_info "正在拉取远程仓库最新代码..."
    git fetch origin

    # 检查是否有更新
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/$GIT_BRANCH)

    if [ "$LOCAL" = "$REMOTE" ]; then
        log_success "已经是最新版本，无需更新"

        # 即使没有更新，也检查容器是否在运行
        if ! docker ps | grep -q "$PROJECT_NAME"; then
            log_info "容器未运行，启动服务..."
            docker-compose up -d
            log_success "服务已启动"
        fi

        exit 0
    fi

    log_info "发现新版本，开始更新..."

    # 直接覆盖本地代码
    log_info "拉取最新代码（覆盖本地修改）..."
    git reset --hard "origin/$GIT_BRANCH"

    NEW_COMMIT=$(git rev-parse --short HEAD)
    log_success "代码已更新到: $NEW_COMMIT"

    # 显示更新日志
    echo ""
    log_info "更新日志:"
    git log --oneline "$CURRENT_COMMIT..$NEW_COMMIT" | head -20
    echo ""

    # 构建前端（在宿主机上）
    if [ -d "app" ]; then
        build_frontend
    fi

    # 重启 Docker 服务
    if [ -f "docker-compose.yml" ]; then
        log_info "正在重启 Docker 服务..."
        docker-compose down
        docker-compose up -d --build
        log_success "服务已重启"
    else
        log_warn "未找到 docker-compose.yml，跳过 Docker 重启"
    fi

    # 清理旧镜像
    log_info "清理未使用的 Docker 镜像..."
    docker image prune -f &> /dev/null || true

    # 显示状态
    echo ""
    log_success "========================================"
    log_success "更新完成!"
    log_success "========================================"
    log_info "项目目录: $PROJECT_DIR"
    log_info "当前版本: $(git rev-parse --short HEAD)"
    log_info "访问地址: http://$(hostname -I | awk '{print $1}'):8080"
    echo ""
}

# 执行主函数
main "$@"
