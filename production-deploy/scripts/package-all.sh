#!/bin/bash
#
# 完整打包脚本 - 前端 + 后端
# 生成可用于 Serv00 部署的压缩包
#
# 版本号规范: v主版本.次版本.修订-YYYYMMDD-构建序号
# 示例: v1.2.0-20250407-001
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
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"
FRONTEND_SOURCE="${PROJECT_ROOT}/frontend"
BACKEND_SOURCE="${PROJECT_ROOT}/backend"
VERSIONS_DIR="${DEPLOY_DIR}/versions"

cd "${PROJECT_ROOT}"

# ============================================
# 版本号生成逻辑
# ============================================

# 默认版本配置（可根据需要修改）
MAJOR_VERSION="1"
MINOR_VERSION="0"
PATCH_VERSION="0"

# 读取已存在版本记录，自动递增构建序号
get_next_build_number() {
    local date_str=$1
    local max_num=0
    
    if [ -d "${VERSIONS_DIR}" ]; then
        # 查找同一天已有的构建包
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

# 生成版本号
DATE_STR=$(date +%Y%m%d)
BUILD_NUM=$(get_next_build_number "${DATE_STR}")
VERSION="v${MAJOR_VERSION}.${MINOR_VERSION}.${PATCH_VERSION}-${DATE_STR}-${BUILD_NUM}"
VERSION_FILE="${VERSIONS_DIR}/.current_version"

echo "========================================"
echo "  OpsPilot 生产环境打包工具"
echo "  目标: Serv00 (FreeBSD, 512M RAM, 3G)"
echo "========================================"
echo ""
log_version "当前构建版本: ${VERSION}"
echo ""

# ===== 步骤 0: 创建版本目录 =====
log_step "[0/5] 初始化版本目录..."
mkdir -p "${VERSIONS_DIR}"
echo "${VERSION}" > "${VERSION_FILE}"
log_info "版本记录保存至: ${VERSION_FILE}"

# ===== 步骤 1: 构建前端 =====
log_step "[1/5] 构建前端..."

if [ ! -d "${FRONTEND_SOURCE}" ]; then
    log_error "前端源码目录不存在"
    exit 1
fi

cd "${FRONTEND_SOURCE}"

# 安装依赖
if [ ! -d "node_modules" ]; then
    log_warn "安装前端依赖..."
    npm install
fi

# 复制生产环境配置
cp "${DEPLOY_DIR}/frontend/.env.production" .env.production

# 构建
log_info "执行构建..."
npm run build

if [ ! -d "dist" ]; then
    log_error "前端构建失败"
    exit 1
fi

# 添加运行时配置（包含版本号）
log_info "写入版本号到前端配置..."
cat > dist/config.js << EOF
// 运行时配置 - 可在不重新构建的情况下修改 API 地址
// 版本: ${VERSION}
// 构建时间: $(date '+%Y-%m-%d %H:%M:%S')
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

# 复制到部署目录
rm -rf "${DEPLOY_DIR}/frontend/dist"
cp -r dist "${DEPLOY_DIR}/frontend/"

cd "${PROJECT_ROOT}"

# ===== 步骤 2: 准备后端 =====
log_step "[2/5] 准备后端..."

# 写入版本号文件到后端
BUILD_TIME=$(date '+%Y-%m-%d %H:%M:%S')
echo "${VERSION}" > "${DEPLOY_DIR}/backend/VERSION"
echo "BUILD_TIME=${BUILD_TIME}" >> "${DEPLOY_DIR}/backend/VERSION"

# 更新后端 .env.production 中的版本号
log_info "更新后端版本号配置..."
sed -i.bak "s/^APP_VERSION=.*/APP_VERSION=${VERSION}/" "${DEPLOY_DIR}/backend/.env.production"
sed -i.bak "s/^BUILD_TIME=.*/BUILD_TIME=${BUILD_TIME}/" "${DEPLOY_DIR}/backend/.env.production"
rm -f "${DEPLOY_DIR}/backend/.env.production.bak"

if [ ! -d "${BACKEND_SOURCE}" ]; then
    log_error "后端源码目录不存在"
    exit 1
fi

# 清理并复制后端文件
rm -rf "${DEPLOY_DIR}/backend/app"
rm -rf "${DEPLOY_DIR}/backend/requirements.txt"

cp -r "${BACKEND_SOURCE}/app" "${DEPLOY_DIR}/backend/"
cp "${BACKEND_SOURCE}/requirements.txt" "${DEPLOY_DIR}/backend/"

# ===== 步骤 3: 创建部署包 =====
log_step "[3/5] 创建部署包..."

# 定义带版本号的文件名
FRONTEND_ZIP="frontend-${VERSION}.zip"
BACKEND_ZIP="backend-${VERSION}.zip"
FULL_PACKAGE_ZIP="opspilot-serv00-deploy-${VERSION}.zip"

# 前端包（带版本号）
cd "${DEPLOY_DIR}/frontend"
zip -r "${VERSIONS_DIR}/${FRONTEND_ZIP}" dist/ -x "*.map" 2>/dev/null || zip -r "${VERSIONS_DIR}/${FRONTEND_ZIP}" dist/
FRONTEND_SIZE=$(du -h "${VERSIONS_DIR}/${FRONTEND_ZIP}" | cut -f1)

# 后端包（带版本号）
cd "${DEPLOY_DIR}/backend"
zip -r "${VERSIONS_DIR}/${BACKEND_ZIP}" app/ requirements.txt start.sh serv00_start.py .env.production VERSION -x "*/__pycache__/*" -x "*.pyc" 2>/dev/null || \
zip -r "${VERSIONS_DIR}/${BACKEND_ZIP}" app/ requirements.txt start.sh serv00_start.py .env.production VERSION
BACKEND_SIZE=$(du -h "${VERSIONS_DIR}/${BACKEND_ZIP}" | cut -f1)

# 创建兼容旧流程的软链接/副本（不带版本号，始终指向最新版本）
cp "${VERSIONS_DIR}/${FRONTEND_ZIP}" "${DEPLOY_DIR}/frontend-dist.zip"
cp "${VERSIONS_DIR}/${BACKEND_ZIP}" "${DEPLOY_DIR}/backend-dist.zip"

# 完整包（包含文档和脚本）
cd "${DEPLOY_DIR}"
zip -r "${VERSIONS_DIR}/${FULL_PACKAGE_ZIP}" \
    frontend-dist.zip \
    backend-dist.zip \
    docs/ \
    -x "*/__pycache__/*" -x "*.pyc" 2>/dev/null || \
zip -r "${VERSIONS_DIR}/${FULL_PACKAGE_ZIP}" \
    frontend-dist.zip \
    backend-dist.zip \
    docs/

# 复制完整包到项目根目录
cp "${VERSIONS_DIR}/${FULL_PACKAGE_ZIP}" "${PROJECT_ROOT}/opspilot-serv00-deploy-${VERSION}.zip"
cp "${VERSIONS_DIR}/${FULL_PACKAGE_ZIP}" "${PROJECT_ROOT}/opspilot-serv00-deploy.zip"

TOTAL_SIZE=$(du -h "${VERSIONS_DIR}/${FULL_PACKAGE_ZIP}" | cut -f1)

# ===== 步骤 4: 生成版本清单 =====
log_step "[4/5] 生成版本清单..."

cat > "${VERSIONS_DIR}/version-history.md" << EOF
# OpsPilot 版本发布历史

## 版本号规范

格式: \`v主版本.次版本.修订-YYYYMMDD-构建序号\`

示例: \`v1.2.0-20250407-001\`

### 版本号说明

| 字段 | 说明 | 示例 |
|------|------|------|
| v | 版本前缀 | v |
| 主版本 | 重大功能更新，可能不兼容 | 1 |
| 次版本 | 新增功能，向后兼容 | 2 |
| 修订号 | Bug修复 | 0 |
| 日期 | 构建日期 | 20250407 |
| 构建序号 | 当日第几次构建 | 001 |

### 当前版本

- **版本号**: ${VERSION}
- **构建时间**: $(date '+%Y-%m-%d %H:%M:%S')
- **构建人**: $(whoami)@$(hostname)

### 历史版本

| 版本号 | 构建时间 | 文件名 |
|--------|----------|--------|
EOF

# 追加历史版本记录
ls -t "${VERSIONS_DIR}"/*.zip 2>/dev/null | head -20 | while read f; do
    basename=$(basename "$f")
    filetime=$(stat -c %y "$f" 2>/dev/null || stat -f %Sm "$f" 2>/dev/null)
    version=$(echo "$basename" | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+-[0-9]+-[0-9]+' || echo "unknown")
    echo "| ${version} | ${filetime} | ${basename} |" >> "${VERSIONS_DIR}/version-history.md"
done

# ===== 步骤 5: 显示结果 =====
log_step "[5/5] 打包完成！"

echo ""
echo "========================================"
echo "  打包结果"
echo "========================================"
echo ""
log_version "版本号: ${VERSION}"
echo ""
echo "📦 前端包 (带版本): production-deploy/versions/${FRONTEND_ZIP}"
echo "   大小: ${FRONTEND_SIZE}"
echo ""
echo "📦 后端包 (带版本): production-deploy/versions/${BACKEND_ZIP}"
echo "   大小: ${BACKEND_SIZE}"
echo ""
echo "📦 完整部署包 (带版本): opspilot-serv00-deploy-${VERSION}.zip"
echo "   大小: ${TOTAL_SIZE}"
echo ""
echo "📋 快捷文件 (无版本号，始终最新):"
echo "   - production-deploy/frontend-dist.zip"
echo "   - production-deploy/backend-dist.zip"
echo "   - opspilot-serv00-deploy.zip"
echo ""
echo "📄 版本历史: production-deploy/versions/version-history.md"
echo ""
echo "========================================"
echo ""

# 显示部署指南
cat "${DEPLOY_DIR}/docs/DEPLOY.md" 2>/dev/null || echo "请查看 production-deploy/docs/DEPLOY.md 获取部署指南"

echo ""
echo "✅ 打包完成！请将 opspilot-serv00-deploy-${VERSION}.zip 上传到 Serv00"
echo ""
echo "💡 版本回退提示:"
echo "   如需回退，从 production-deploy/versions/ 目录找到对应版本包"
echo "   解压部署即可快速回退到指定版本"
