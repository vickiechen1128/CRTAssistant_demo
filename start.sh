#!/bin/bash
# CRTAssistant 一键启动脚本
# 同时启动后端和前端服务

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  CRTAssistant 应用启动脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查端口占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 杀死占用端口的进程
kill_port() {
    local port=$1
    if check_port $port; then
        echo -e "${YELLOW}端口 $port 被占用，正在释放...${NC}"
        lsof -Pi :$port -sTCP:LISTEN -t | xargs kill -9 2>/dev/null
        sleep 1
    fi
}

# 释放端口
echo -e "${BLUE}[1/3] 检查端口占用...${NC}"
kill_port 8000
kill_port 5173
echo -e "${GREEN}✓ 端口已释放${NC}"
echo ""

# 启动后端
echo -e "${BLUE}[2/3] 启动后端服务 (FastAPI)...${NC}"
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
python run.py &
BACKEND_PID=$!
echo -e "${GREEN}✓ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
echo -e "  ${BLUE}→ http://127.0.0.1:8000${NC}"
echo -e "  ${BLUE}→ API文档: http://127.0.0.1:8000/docs${NC}"
echo ""

# 等待后端启动
sleep 3

# 启动前端
echo -e "${BLUE}[3/3] 启动前端服务 (Vite)...${NC}"
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✓ 前端服务已启动 (PID: $FRONTEND_PID)${NC}"
echo -e "  ${BLUE}→ http://localhost:5173/${NC}"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  所有服务已启动成功！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}使用说明:${NC}"
echo -e "  • 前端页面: ${BLUE}http://localhost:5173/${NC}"
echo -e "  • 后端API:  ${BLUE}http://127.0.0.1:8000${NC}"
echo -e "  • API文档:  ${BLUE}http://127.0.0.1:8000/docs${NC}"
echo ""
echo -e "${YELLOW}停止服务:${NC}"
echo -e "  • 按 ${BLUE}Ctrl+C${NC} 停止所有服务"
echo ""

# 捕获 Ctrl+C 信号，优雅退出
trap 'echo ""; echo -e "${YELLOW}正在停止服务...${NC}"; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo -e "${GREEN}✓ 服务已停止${NC}"; exit 0' INT

# 等待进程
wait
