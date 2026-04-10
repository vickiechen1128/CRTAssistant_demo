#!/bin/bash
#
# Serv00 部署脚本
# 一键打包后端代码并生成部署指南
#

set -e

echo "========================================"
echo "  OpsPilot 后端部署打包工具"
echo "========================================"

# 颜色定义
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $*"
}

# 项目目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/backend"
DEPLOY_DIR="${SCRIPT_DIR}/serv00_deploy"

cd "${SCRIPT_DIR}"

# 清理旧的部署文件
log_step "清理旧的部署文件..."
rm -rf "${DEPLOY_DIR}"
mkdir -p "${DEPLOY_DIR}"

# 复制后端代码
log_step "复制后端代码..."
cp -r "${BACKEND_DIR}/app" "${DEPLOY_DIR}/"
cp "${BACKEND_DIR}/requirements.txt" "${DEPLOY_DIR}/"
cp "${BACKEND_DIR}/serv00_deploy.py" "${DEPLOY_DIR}/"
cp "${BACKEND_DIR}/.env.example" "${DEPLOY_DIR}/"

# 创建启动脚本
log_step "创建启动脚本..."
cat > "${DEPLOY_DIR}/start.sh" << 'EOF'
#!/bin/bash
# Serv00 启动脚本

cd "$(dirname "$0")"

# 加载环境变量
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# 创建数据目录
mkdir -p ~/opspilot_data

# 安装依赖
pip install -r requirements.txt --user

# 启动服务
python serv00_deploy.py
EOF

chmod +x "${DEPLOY_DIR}/start.sh"

# 创建 supervisor 配置文件（用于后台运行）
log_step "创建 Supervisor 配置..."
cat > "${DEPLOY_DIR}/opspilot.ini" << 'EOF'
[program:opspilot]
command=python %(ENV_HOME)s/serv00_deploy/serv00_deploy.py
directory=%(ENV_HOME)s/serv00_deploy
autostart=true
autorestart=true
stderr_logfile=%(ENV_HOME)s/logs/opspilot.err.log
stdout_logfile=%(ENV_HOME)s/logs/opspilot.out.log
environment=HOME="%(ENV_HOME)s",USER="%(ENV_USER)s"
EOF

# 打包
log_step "打包文件..."
cd "${SCRIPT_DIR}"
zip -r "serv00_backend.zip" "serv00_deploy/"

# 显示结果
log_info "打包完成！"
echo ""
echo "========================================"
echo "  部署文件信息"
echo "========================================"
echo "文件: serv00_backend.zip"
echo "大小: $(du -h serv00_backend.zip | cut -f1)"
echo ""
echo "========================================"
echo "  部署步骤"
echo "========================================"
echo ""
echo "1. 上传 serv00_backend.zip 到 Serv00:"
echo "   scp serv00_backend.zip your_username@srvXX.serv00.com:~"
echo ""
echo "2. SSH 登录并解压:"
echo "   ssh your_username@srvXX.serv00.com"
echo "   unzip serv00_backend.zip"
echo ""
echo "3. 配置环境变量:"
echo "   cd ~/serv00_deploy"
echo "   cp .env.example .env"
echo "   # 编辑 .env 文件，修改域名和密钥"
echo ""
echo "4. 安装依赖:"
echo "   pip install -r requirements.txt --user"
echo ""
echo "5. 启动服务:"
echo "   python serv00_deploy.py"
echo ""
echo "6. 配置 Serv00 面板:"
echo "   - 进入 WWW Websites"
echo "   - 添加 Python 类型网站"
echo "   - 指向 ~/serv00_deploy"
echo "   - 启动命令: python serv00_deploy.py"
echo ""
echo "========================================"
