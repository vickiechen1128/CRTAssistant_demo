#!/bin/bash
#
# 版本信息查看脚本
# 用法: ./check-version.sh
#

set -e

# 颜色定义
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  OpsPilot 版本信息${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# 检查 VERSION 文件
if [ -f "VERSION" ]; then
    echo -e "${GREEN}后端版本信息:${NC}"
    cat VERSION
else
    echo -e "${YELLOW}警告: 未找到 VERSION 文件${NC}"
    echo "当前目录: $(pwd)"
fi

echo ""

# 检查环境变量
if [ -f ".env" ]; then
    echo -e "${GREEN}环境配置:${NC}"
    echo "运行环境: $(grep ENV .env | cut -d'=' -f2 || echo '未设置')"
    echo "调试模式: $(grep DEBUG .env | cut -d'=' -f2 || echo '未设置')"
    echo "服务端口: $(grep PORT .env | cut -d'=' -f2 || echo '8000')"
else
    echo -e "${YELLOW}警告: 未找到 .env 文件${NC}"
fi

echo ""

# 检查运行状态
echo -e "${GREEN}运行状态:${NC}"
if pgrep -f "serv00_start.py" > /dev/null; then
    PID=$(pgrep -f "serv00_start.py")
    echo -e "服务状态: ${GREEN}运行中${NC} (PID: $PID)"
    
    # 内存使用
    MEM=$(ps -o rss= -p $PID 2>/dev/null || echo "N/A")
    if [ "$MEM" != "N/A" ]; then
        echo "内存使用: $(echo "$MEM / 1024" | bc 2>/dev/null || echo "N/A") MB"
    fi
else
    echo -e "服务状态: ${YELLOW}未运行${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"

# 提示前端版本查看方法
echo ""
echo -e "${CYAN}提示: 前端版本可通过以下方式查看:${NC}"
echo "  1. 浏览器控制台输入: window.APP_CONFIG.VERSION"
echo "  2. 查看配置文件: cat ~/domains/*/public_html/dist/config.js | grep VERSION"
