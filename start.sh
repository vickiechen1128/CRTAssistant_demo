#!/usr/bin/env bash
#
# CRTAssistant_demo 一键启动脚本
# 同时启动后端 (FastAPI) 和前端 (Vite/React) 服务
#

set -euo pipefail
IFS=$'\n\t'

# 脚本元数据
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# 颜色定义
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# 配置
BACKEND_PORT=8000
FRONTEND_PORT=5173
BACKEND_DIR="${SCRIPT_DIR}/backend"
FRONTEND_DIR="${SCRIPT_DIR}/frontend"

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $*"
}

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :"${port}" -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 清理函数 - 杀死后台进程
cleanup() {
    local exit_code=$?
    echo ""
    log_step "正在停止服务..."

    # 停止后端进程
    if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "${BACKEND_PID}" 2>/dev/null; then
        log_info "停止后端服务 (PID: ${BACKEND_PID})..."
        kill "${BACKEND_PID}" 2>/dev/null || true
        wait "${BACKEND_PID}" 2>/dev/null || true
    fi

    # 停止前端进程
    if [[ -n "${FRONTEND_PID:-}" ]] && kill -0 "${FRONTEND_PID}" 2>/dev/null; then
        log_info "停止前端服务 (PID: ${FRONTEND_PID})..."
        kill "${FRONTEND_PID}" 2>/dev/null || true
        wait "${FRONTEND_PID}" 2>/dev/null || true
    fi

    log_info "服务已停止"
    exit "${exit_code}"
}

# 设置清理陷阱
trap cleanup EXIT INT TERM

# 显示使用说明
usage() {
    cat <<EOF
用法: ./${SCRIPT_NAME} [选项]

选项:
    -h, --help      显示此帮助信息
    -b, --backend   仅启动后端服务
    -f, --frontend  仅启动前端服务
    --no-check      跳过环境检查

示例:
    ./${SCRIPT_NAME}              # 启动前后端服务
    ./${SCRIPT_NAME} -b           # 仅启动后端
    ./${SCRIPT_NAME} -f           # 仅启动前端
EOF
}

# 检查 Python 环境
check_python() {
    log_step "检查 Python 环境..."

    if ! command -v python3 &>/dev/null; then
        log_error "未找到 python3，请先安装 Python 3"
        exit 1
    fi

    local python_version
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    log_info "Python 版本: ${python_version}"

    # 检查虚拟环境
    if [[ -d "${BACKEND_DIR}/venv" ]]; then
        log_info "检测到虚拟环境"
    elif [[ -d "${BACKEND_DIR}/.venv" ]]; then
        log_info "检测到虚拟环境"
    else
        log_warn "未检测到虚拟环境，将使用系统 Python"
    fi
}

# 检查 Node.js 环境
check_node() {
    log_step "检查 Node.js 环境..."

    if ! command -v node &>/dev/null; then
        log_error "未找到 node，请先安装 Node.js"
        exit 1
    fi

    local node_version
    node_version=$(node --version)
    log_info "Node.js 版本: ${node_version}"

    if ! command -v npm &>/dev/null; then
        log_error "未找到 npm，请先安装 npm"
        exit 1
    fi
}

# 检查依赖
check_dependencies() {
    log_step "检查项目依赖..."

    # 检查后端依赖
    if [[ ! -d "${BACKEND_DIR}/venv" && ! -d "${BACKEND_DIR}/.venv" ]]; then
        log_warn "后端虚拟环境不存在，建议先运行: cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    fi

    # 检查前端依赖
    if [[ ! -d "${FRONTEND_DIR}/node_modules" ]]; then
        log_warn "前端依赖未安装，正在自动安装..."
        (cd "${FRONTEND_DIR}" && npm install)
    else
        log_info "前端依赖已安装"
    fi
}

# 启动后端服务
start_backend() {
    log_step "启动后端服务..."

    # 检查端口占用
    if check_port "${BACKEND_PORT}"; then
        log_error "端口 ${BACKEND_PORT} 已被占用"
        exit 1
    fi

    cd "${BACKEND_DIR}"

    # 激活虚拟环境（如果存在）
    if [[ -f "venv/bin/activate" ]]; then
        # shellcheck source=/dev/null
        source venv/bin/activate
    elif [[ -f ".venv/bin/activate" ]]; then
        # shellcheck source=/dev/null
        source .venv/bin/activate
    fi

    log_info "启动 FastAPI 服务 (http://127.0.0.1:${BACKEND_PORT})..."

    # 后台启动后端服务
    python3 run.py &
    BACKEND_PID=$!

    # 等待后端启动
    local retries=0
    local max_retries=30
    while ! check_port "${BACKEND_PORT}"; do
        if [[ ${retries} -ge ${max_retries} ]]; then
            log_error "后端服务启动超时"
            exit 1
        fi
        sleep 1
        ((retries++))
    done

    log_info "后端服务已启动 (PID: ${BACKEND_PID})"
}

# 启动前端服务
start_frontend() {
    log_step "启动前端服务..."

    # 检查端口占用
    if check_port "${FRONTEND_PORT}"; then
        log_error "端口 ${FRONTEND_PORT} 已被占用"
        exit 1
    fi

    cd "${FRONTEND_DIR}"

    log_info "启动 Vite 开发服务器 (http://localhost:${FRONTEND_PORT})..."

    # 后台启动前端服务
    npm run dev &
    FRONTEND_PID=$!

    # 等待前端启动
    local retries=0
    local max_retries=30
    while ! check_port "${FRONTEND_PORT}"; do
        if [[ ${retries} -ge ${max_retries} ]]; then
            log_error "前端服务启动超时"
            exit 1
        fi
        sleep 1
        ((retries++))
    done

    log_info "前端服务已启动 (PID: ${FRONTEND_PID})"
}

# 主函数
main() {
    local run_backend=false
    local run_frontend=false
    local skip_check=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                exit 0
                ;;
            -b|--backend)
                run_backend=true
                shift
                ;;
            -f|--frontend)
                run_frontend=true
                shift
                ;;
            --no-check)
                skip_check=true
                shift
                ;;
            *)
                log_error "未知选项: $1"
                usage
                exit 1
                ;;
        esac
    done

    # 如果没有指定，默认启动全部
    if [[ "${run_backend}" == false && "${run_frontend}" == false ]]; then
        run_backend=true
        run_frontend=true
    fi

    echo "========================================"
    echo "  CRTAssistant_demo 一键启动脚本"
    echo "========================================"
    echo ""

    # 环境检查
    if [[ "${skip_check}" == false ]]; then
        if [[ "${run_backend}" == true ]]; then
            check_python
        fi
        if [[ "${run_frontend}" == true ]]; then
            check_node
        fi
        check_dependencies
        echo ""
    fi

    # 启动服务
    if [[ "${run_backend}" == true ]]; then
        start_backend
    fi

    if [[ "${run_frontend}" == true ]]; then
        start_frontend
    fi

    echo ""
    echo "========================================"
    log_info "所有服务已启动成功！"
    echo "========================================"
    echo ""

    if [[ "${run_backend}" == true ]]; then
        echo -e "  后端 API: ${GREEN}http://127.0.0.1:${BACKEND_PORT}${NC}"
        echo -e "  API 文档: ${GREEN}http://127.0.0.1:${BACKEND_PORT}/docs${NC}"
    fi

    if [[ "${run_frontend}" == true ]]; then
        echo -e "  前端页面: ${GREEN}http://localhost:${FRONTEND_PORT}${NC}"
    fi

    echo ""
    echo "按 Ctrl+C 停止所有服务"
    echo ""

    # 等待所有后台进程
    wait
}

# 运行主函数
main "$@"
