#!/bin/bash
#
# Serv00 Proxy 模式部署包构建脚本
# 适用于：前后端同域部署，Serv00 面板配置 Proxy
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
BACKEND_SOURCE="${PROJECT_ROOT}/backend"
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

# 获取版本号
get_version() {
    local date_str=$(date +%Y%m%d)
    local build_num=$(get_next_build_number $date_str)
    echo "v${MAJOR_VERSION}.${MINOR_VERSION}.${PATCH_VERSION}-${date_str}-${build_num}"
}

# 主版本号
VERSION=$(get_version)
BUILD_TIME=$(date '+%Y-%m-%d %H:%M:%S')

log_version "构建版本: ${VERSION}"
log_version "构建时间: ${BUILD_TIME}"

# 创建版本目录
mkdir -p "${VERSIONS_DIR}"

# ============================================
# 构建前端
# ============================================
log_step "构建前端..."
cd "${FRONTEND_SOURCE}"

# 安装依赖
npm install

# 生产构建
npm run build

# 创建 config.js 为同域部署配置
cat > dist/config.js << EOF
window.APP_CONFIG = {
    API_BASE_URL: '/api/v1',
    UPLOAD_BASE_URL: '/uploads',
    APP_NAME: 'OpsPilot',
    VERSION: '${VERSION}'
};
EOF

# 写入版本信息到 config.js
echo "// Build Time: ${BUILD_TIME}" >> dist/config.js

log_info "前端构建完成"

# ============================================
# 准备后端
# ============================================
log_step "准备后端..."
cd "${BACKEND_SOURCE}"

# 更新版本号文件
echo "${VERSION}" > "${DEPLOY_DIR}/backend-dist/VERSION"
echo "Build Time: ${BUILD_TIME}" >> "${DEPLOY_DIR}/backend-dist/VERSION"

# 复制后端代码到部署目录
rm -rf "${DEPLOY_DIR}/backend-dist/app"
cp -r app "${DEPLOY_DIR}/backend-dist/"

# 复制其他必要文件
cp requirements.txt "${DEPLOY_DIR}/backend-dist/"
cp -f "${DEPLOY_DIR}/backend/.env.production" "${DEPLOY_DIR}/backend-dist/.env.production"

# 更新 .env.production 中的版本号
sed -i '' "s/APP_VERSION=.*/APP_VERSION=${VERSION}/" "${DEPLOY_DIR}/backend-dist/.env.production"
sed -i '' "s/BUILD_TIME=.*/BUILD_TIME=${BUILD_TIME}/" "${DEPLOY_DIR}/backend-dist/.env.production"

log_info "后端准备完成"

# ============================================
# 创建 Serv00 启动脚本
# ============================================
log_step "创建 Serv00 启动脚本..."

cat > "${DEPLOY_DIR}/backend-dist/serv00_start.py" << 'EOF'
#!/usr/bin/env python3
"""
Serv00 生产环境启动脚本
针对 Proxy 模式部署优化
"""
import uvicorn
import os
import sys

# 添加应用目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def read_version():
    """读取版本号文件"""
    version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION")
    version_info = {}
    
    if os.path.exists(version_file):
        try:
            with open(version_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    version_info['version'] = lines[0].strip()
                if len(lines) > 1:
                    version_info['build_time'] = lines[1].strip()
        except Exception as e:
            print(f"读取版本文件失败: {e}")
    
    return version_info

if __name__ == "__main__":
    # 读取版本信息
    version_info = read_version()
    version = version_info.get('version', 'unknown')
    build_time = version_info.get('build_time', 'unknown')
    
    print(f"=" * 50)
    print(f"OpsPilot Serv00 生产环境")
    print(f"版本: {version}")
    print(f"构建时间: {build_time}")
    print(f"=" * 50)
    
    # 从环境变量读取配置，或使用默认值
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "60361"))
    
    print(f"启动服务: http://{host}:{port}")
    print(f"前端路径: ~/opspilot/frontend/dist")
    print(f"=" * 50)
    
    # 启动服务
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,
        workers=1,
        limit_max_requests=1000,
        timeout_keep_alive=5,
    )
EOF

chmod +x "${DEPLOY_DIR}/backend-dist/serv00_start.py"

log_info "启动脚本创建完成"

# ============================================
# 打包
# ============================================
log_step "打包部署文件..."

cd "${DEPLOY_DIR}"

# 打包后端
rm -f backend-dist.zip
zip -r backend-dist.zip backend-dist/

# 打包前端
rm -f frontend-dist.zip
cd "${FRONTEND_SOURCE}/dist"
zip -r "${DEPLOY_DIR}/frontend-dist.zip" .

# 创建完整部署包
cd "${DEPLOY_DIR}"
DEPLOY_PACKAGE="opspilot-serv00-proxy-${VERSION}.zip"

zip "${DEPLOY_PACKAGE}" \
    backend-dist.zip \
    frontend-dist.zip \
    -x "versions/*" \
    -x "backend/*" \
    -x "backend-dist/*"

# 移动到版本目录
mv "${DEPLOY_PACKAGE}" "${VERSIONS_DIR}/"

# 同时创建快捷方式
cp "${VERSIONS_DIR}/${DEPLOY_PACKAGE}" "${DEPLOY_DIR}/opspilot-serv00-proxy-latest.zip"

log_info "打包完成"

# ============================================
# 输出结果
# ============================================
echo ""
echo "========================================"
echo "  构建结果"
echo "========================================"
log_version "版本号: ${VERSION}"
echo ""
echo "📦 部署包: ${VERSIONS_DIR}/${DEPLOY_PACKAGE}"
echo "📦 快捷方式: ${DEPLOY_DIR}/opspilot-serv00-proxy-latest.zip"
echo ""
echo "部署说明:"
echo "1. 上传 ${DEPLOY_PACKAGE} 到 Serv00 的 ~/ 目录"
echo "2. 解压: unzip ${DEPLOY_PACKAGE}"
echo "3. 部署后端:"
echo "   mkdir -p ~/opspilot"
echo "   unzip backend-dist.zip -d ~/opspilot/"
echo "   mv ~/opspilot/backend-dist/* ~/opspilot/"
echo "   rm -rf ~/opspilot/backend-dist"
echo "4. 部署前端:"
echo "   mkdir -p ~/opspilot/frontend"
echo "   unzip frontend-dist.zip -d ~/opspilot/frontend/dist"
echo "5. 配置 .env 文件"
echo "6. 在 Serv00 面板配置 Proxy 到 http://localhost:60361"
echo "========================================"
