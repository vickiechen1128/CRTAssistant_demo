#!/bin/bash
#
# 后端生产环境启动脚本
# Serv00 专用
#

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# 加载环境变量
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# 创建数据目录
mkdir -p ~/opspilot_data
mkdir -p ~/opspilot_uploads

# 显示版本信息
if [ -f "VERSION" ]; then
    echo "版本: $(cat VERSION)"
fi

# 显示启动信息
echo "========================================"
echo "  OpsPilot 后端启动中..."
echo "========================================"
echo "环境: ${ENV:-production}"
echo "端口: ${PORT:-8000}"
echo "数据库: ${DATABASE_URL:-sqlite}"
if [ -f "VERSION" ]; then
    echo "版本: $(cat VERSION)"
fi
echo "========================================"

# 启动服务
exec python serv00_start.py
