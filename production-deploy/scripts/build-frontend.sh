#!/bin/bash
#
# 前端生产环境构建脚本
# 用法: ./build-frontend.sh [版本号]
#
# 版本号规范: v主版本.次版本.修订-YYYYMMDD-构建序号
# 示例: v1.0.0-20250407-001
#

set -e

# 颜色定义
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly RED='\033[0;31m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }
log_version() { echo -e "${CYAN}[VERSION]${NC} $*"; }

# 项目路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
FRONTEND_SOURCE="${PROJECT_ROOT}/frontend"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"
VERSIONS_DIR="${DEPLOY_DIR}/versions"

# 默认版本配置
MAJOR_VERSION="1"
MINOR_VERSION="0"
PATCH_VERSION="0"

# 获取下一个构建序号
get_next_build_number() {
    local date_str=$1
    local max_num=0
    
    if [ -d "${VERSIONS_DIR}" ]; then
        for f in "${VERSIONS_DIR}"/*${date_str}*.zip; do
            [ -f "$f" ] || continue
            local num=$(echo "$f" | grep -oE "${date_str}-[0-9]+" | cut -d'-' -f4)
            if [ -n "$num" ] && [ "$num" -gt "$max_num" ]; then
                max_num=$num
            fi
        done 2>/dev/null
    fi
    
    printf "%03d" $((max_num + 1))
}

# 版本号生成或解析
if [ -n "$1" ]; then
    # 使用传入的版本号
    VERSION="$1"
    log_info "使用指定版本号: ${VERSION}"
else
    # 自动生成版本号
    DATE_STR=$(date +%Y%m%d)
    BUILD_NUM=$(get_next_build_number "${DATE_STR}")
    VERSION="v${MAJOR_VERSION}.${MINOR_VERSION}.${PATCH_VERSION}-${DATE_STR}-${BUILD_NUM}"
    log_version "自动生成版本号: ${VERSION}"
fi

# 创建版本目录
mkdir -p "${VERSIONS_DIR}"

cd "${PROJECT_ROOT}"

log_step "开始构建前端生产环境包 [${VERSION}]..."

# 检查源文件
if [ ! -d "${FRONTEND_SOURCE}" ]; then
    log_error "前端源码目录不存在: ${FRONTEND_SOURCE}"
    exit 1
fi

# 复制生产环境配置
log_step "复制生产环境配置..."
cp "${DEPLOY_DIR}/frontend/.env.production" "${FRONTEND_SOURCE}/.env.production"

# 进入前端目录
cd "${FRONTEND_SOURCE}"

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    log_warn "未找到 node_modules，正在安装依赖..."
    npm install
fi

# 构建生产环境
log_step "构建生产环境..."
npm run build

# 检查构建结果
if [ ! -d "dist" ]; then
    log_error "构建失败，未找到 dist 目录"
    exit 1
fi

# 复制到部署目录
log_step "复制构建结果到部署目录..."
rm -rf "${DEPLOY_DIR}/frontend/dist"
cp -r dist "${DEPLOY_DIR}/frontend/"

# 创建运行时配置脚本（包含版本号）
BUILD_TIME=$(date '+%Y-%m-%d %H:%M:%S')
cat > "${DEPLOY_DIR}/frontend/dist/config.js" << EOF
// 运行时配置 - 可在不重新构建的情况下修改 API 地址
// 版本: ${VERSION}
// 构建时间: ${BUILD_TIME}
window.APP_CONFIG = {
    // 后端 API 地址
    API_BASE_URL: 'https://opspilot.chenruiting2024.serv00.net/api/v1',
    
    // 上传文件基础地址
    UPLOAD_BASE_URL: 'https://opspilot.chenruiting2024.serv00.net/uploads',
    
    // 应用信息
    APP_NAME: 'OpsPilot',
    VERSION: '${VERSION}'
};
EOF

# 修改 index.html 引入配置
cd "${DEPLOY_DIR}/frontend/dist"
if [ -f "index.html" ]; then
    # 在 </head> 前插入 config.js
    sed -i '' 's|</head>|<script src="./config.js"></script>\n</head>|' index.html 2>/dev/null || \
    sed -i 's|</head>|<script src="./config.js"></script>\n</head>|' index.html
fi

# 打包（带版本号和不带版本号两种）
log_step "打包前端文件..."
cd "${DEPLOY_DIR}/frontend"

# 带版本号的包
FRONTEND_VERSIONED="frontend-${VERSION}.zip"
zip -r "${VERSIONS_DIR}/${FRONTEND_VERSIONED}" dist/

# 无版本号的快捷包（始终指向最新）
zip -r "${DEPLOY_DIR}/frontend-dist.zip" dist/

# 显示结果
FILE_SIZE=$(du -h "${VERSIONS_DIR}/${FRONTEND_VERSIONED}" | cut -f1)
LINK_SIZE=$(du -h "${DEPLOY_DIR}/frontend-dist.zip" | cut -f1)

log_info "前端构建完成！"
echo ""
echo "========================================"
echo "  构建结果"
echo "========================================"
log_version "版本号: ${VERSION}"
echo ""
echo "📦 带版本号文件: production-deploy/versions/${FRONTEND_VERSIONED}"
echo "   大小: ${FILE_SIZE}"
echo ""
echo "📦 快捷文件: production-deploy/frontend-dist.zip"
echo "   大小: ${LINK_SIZE}"
echo ""
echo "部署说明:"
echo "1. 将 frontend-dist.zip 或 versions/${FRONTEND_VERSIONED} 上传到 Serv00"
echo "2. 解压到网站目录"
echo "3. 修改 dist/config.js 中的 API_BASE_URL"
echo ""
echo "💡 提示: 如需回退版本，从 versions/ 目录选择历史版本包"
echo "========================================"
