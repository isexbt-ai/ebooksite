FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# 复制 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 构建前端（如果 .output 不存在）
RUN if [ ! -d "app/.output" ]; then \
    cd app && npm install && npm run build && cd ..; \
    fi

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "server.py"]
