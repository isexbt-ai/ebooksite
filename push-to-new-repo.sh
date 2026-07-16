#!/bin/bash
# 推送到新仓库的脚本

echo "=== 图书管理系统 - 推送脚本 ==="
echo ""

# 获取用户输入
read -p "请输入您的 GitHub 用户名: " USERNAME
read -p "请输入新仓库名称 (例如: booksite-private): " REPO_NAME

# 移除旧的远程仓库
echo "正在移除旧的远程仓库..."
git remote remove origin 2>/dev/null

# 添加新的远程仓库
REMOTE_URL="https://github.com/${USERNAME}/${REPO_NAME}.git"
echo "正在添加新的远程仓库: ${REMOTE_URL}"
git remote add origin ${REMOTE_URL}

# 推送代码
echo "正在推送代码..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 推送成功！"
    echo "仓库地址: ${REMOTE_URL}"
else
    echo ""
    echo "❌ 推送失败，请检查："
    echo "1. 仓库是否已创建"
    echo "2. 用户名和仓库名是否正确"
    echo "3. 是否有权限推送"
fi
