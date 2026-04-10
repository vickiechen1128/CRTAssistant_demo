# OpsPilot Serv00 部署指南（同域部署）

## 系统要求

- **平台**: Serv00.com FreeBSD 虚拟机
- **内存**: 512 MB
- **磁盘**: 3 GB
- **Python**: 3.9+
- **网络**: 可公网访问

---

## 版本号规范

### 格式说明

OpsPilot 使用以下版本号格式：

```
v主版本.次版本.修订-YYYYMMDD-构建序号
```

**示例**: `v1.2.0-20250407-001`

### 字段含义

| 字段 | 位置 | 说明 | 变更时机 |
|------|------|------|----------|
| v | 前缀 | 版本标识 | 固定 |
| 主版本 | 第1位 | 重大功能更新 | 不兼容的API更改时递增 |
| 次版本 | 第2位 | 新增功能 | 向后兼容的功能添加时递增 |
| 修订号 | 第3位 | Bug修复 | 向后兼容的问题修复时递增 |
| 日期 | YYYYMMDD | 构建日期 | 自动 |
| 构建序号 | 001-999 | 当日第几次构建 | 自动递增 |

### 版本文件说明

构建后会生成以下文件：

```
production-deploy/
├── versions/                          # 版本历史目录
│   ├── frontend-v1.0.0-20250407-001.zip   # 带版本号的前端包
│   ├── backend-v1.0.0-20250407-001.zip    # 带版本号的后端包
│   ├── opspilot-serv00-deploy-v1.0.0-20250407-001.zip  # 完整部署包
│   └── version-history.md             # 版本历史记录
├── frontend-dist.zip                  # 最新前端包（快捷方式）
└── backend-dist.zip                   # 最新后端包（快捷方式）
```

---

## 部署包说明

```
opspilot-serv00-deploy-v{版本号}.zip
├── frontend-dist.zip      # 前端静态文件
├── backend-dist.zip       # 后端 Python 应用
└── docs/                  # 文档
```

---

## 部署步骤（同域部署）

同域部署是指前端和后端共享同一个域名，例如：
- 前端页面：`https://opspilot.chenruiting2024.serv00.net/`
- API 接口：`https://opspilot.chenruiting2024.serv00.net/api/v1/`

### 第一步：上传文件

```bash
# 在本地执行，上传到 Serv00
scp opspilot-serv00-deploy-v1.0.0-20250407-001.zip your_username@srvXX.serv00.com:~
```

### 第二步：登录并解压

```bash
# SSH 登录
ssh your_username@srvXX.serv00.com

# 解压
cd ~
unzip opspilot-serv00-deploy-v{版本号}.zip
```

### 第三步：部署后端

```bash
# 创建应用目录
mkdir -p ~/opspilot-backend
cd ~/opspilot-backend

# 解压后端包
unzip ~/backend-dist.zip

# 查看版本号
cat VERSION

# 配置环境变量
cp .env.production .env
nano .env
# 修改以下配置：
# - SECRET_KEY: 随机密钥
# - DATABASE_URL: 数据库路径（保持默认即可）
# 注意：同域部署不需要配置 CORS_ORIGINS

# 安装依赖
pip install -r requirements.txt --user

# 创建数据目录
mkdir -p ~/opspilot_data
mkdir -p ~/opspilot_uploads
```

### 第四步：部署前端

```bash
# 解压前端包
unzip frontend-dist.zip

# 查看前端版本
cat dist/config.js | grep VERSION

# 移动 dist 到网站目录
mv dist ~/domains/your-domain.serv00.com/public_html/
```

### 第五步：配置 Serv00 面板

#### 后端配置（Python 应用）

1. 登录 https://panel.serv00.com
2. 进入 **WWW Websites**
3. 添加网站：
   - **Type**: Python
   - **Domain**: your-domain.serv00.com
   - **Root directory**: `~/opspilot-backend`
   - **Command**: `python serv00_start.py`

> **注意**: Python 应用会自动处理 `/api/*` 路径的请求

#### 前端配置（静态文件）

**方案一：Serv00 面板添加静态网站（推荐）**

1. 进入 **WWW Websites**
2. 添加网站：
   - **Type**: Static
   - **Domain**: your-domain.serv00.com
   - **Root directory**: `~/domains/your-domain.serv00.com/public_html/dist`

**方案二：Python 应用托管静态文件**

如果不想在面板配置两个网站，可以让 Python 应用同时托管前端静态文件（需要修改后端代码添加静态文件路由）。

### 第六步：启动后端

```bash
# 手动启动测试
cd ~/opspilot-backend
python serv00_start.py

# 或使用脚本
./start.sh
```

---

## 版本回退（重要）

当新版本出现问题时，可以快速回退到之前的稳定版本。

### 查看已部署版本

**前端版本查看：**
```bash
# 方法1: 查看配置文件
cat ~/domains/your-domain.serv00.com/public_html/dist/config.js | grep VERSION

# 方法2: 浏览器控制台
# 打开前端页面，按 F12 -> Console，输入：window.APP_CONFIG.VERSION
```

**后端版本查看：**
```bash
cat ~/opspilot-backend/VERSION
```

### 回退前端

```bash
# 1. 确定要回退的版本（假设要回退到 v1.0.0-20250406-003）
VERSION="v1.0.0-20250406-003"

# 2. 备份当前版本（可选但推荐）
mv ~/domains/your-domain.serv00.com/public_html/dist \
   ~/domains/your-domain.serv00.com/public_html/dist.backup.$(date +%Y%m%d%H%M%S)

# 3. 解压指定版本的前端包
cd ~
unzip opspilot-serv00-deploy-${VERSION}.zip
unzip frontend-${VERSION}.zip

# 4. 部署指定版本
mv dist ~/domains/your-domain.serv00.com/public_html/

# 5. 验证版本
cat ~/domains/your-domain.serv00.com/public_html/dist/config.js | grep VERSION
```

### 回退后端

```bash
# 1. 确定要回退的版本
VERSION="v1.0.0-20250406-003"

# 2. 备份当前版本和数据（重要！）
cd ~
cp -r ~/opspilot-backend ~/opspilot-backend.backup.$(date +%Y%m%d%H%M%S)
cp ~/opspilot_data/app.db ~/opspilot_data/app.db.backup.$(date +%Y%m%d%H%M%S)

# 3. 停止当前服务（在 Serv00 面板中停止 Python 应用）

# 4. 清理并重新部署
cd ~/opspilot-backend
rm -rf app/ requirements.txt start.sh serv00_start.py .env.production VERSION

# 5. 解压指定版本的后端包
cd ~
unzip opspilot-serv00-deploy-${VERSION}.zip
unzip backend-${VERSION}.zip -d ~/opspilot-backend/

# 6. 保留原有环境配置
cd ~/opspilot-backend
cp .env.production .env
# 根据需要修改 .env

# 7. 在 Serv00 面板中重新启动 Python 应用

# 8. 验证版本
cat ~/opspilot-backend/VERSION
```

### 版本回退最佳实践

1. **数据库兼容性**: 回退后端版本时，注意数据库结构是否兼容。如果不兼容，需要先恢复数据库备份。
2. **先回后端，再回前端**: 避免前后端版本不一致导致API调用失败。
3. **保留至少3个历史版本**: 定期清理，但保留最近的3个版本以备紧急回退。
4. **记录回退原因**: 在版本历史文档中记录为什么回退，便于问题追踪。

---

## 目录结构

```
~
├── domains/
│   └── your-domain.serv00.com/          # 同域部署，单一域名
│       └── public_html/
│           └── dist/                    # 前端文件
│               ├── index.html
│               ├── config.js            # API 配置（含版本号）
│               └── assets/
├── opspilot-backend/                    # 后端应用
│   ├── app/                             # 业务代码
│   ├── requirements.txt                 # 依赖
│   ├── serv00_start.py                 # 启动脚本
│   ├── start.sh                        # 启动脚本
│   ├── .env                            # 环境配置
│   └── VERSION                         # 版本号文件
├── opspilot_data/                       # 数据库
│   └── app.db
└── opspilot_uploads/                    # 上传文件
```

---

## 配置说明

### 前端配置 (config.js)

同域部署时，前端 API 地址使用相对路径或同域绝对路径：

```javascript
window.APP_CONFIG = {
    // 同域部署：使用相对路径或同域完整 URL
    API_BASE_URL: '/api/v1',
    // 或使用完整 URL
    // API_BASE_URL: 'https://opspilot.chenruiting2024.serv00.net/api/v1',
    UPLOAD_BASE_URL: '/uploads',
    APP_NAME: 'OpsPilot',
    VERSION: 'v1.0.0-20250407-001'  // 自动写入的版本号
};
```

### 后端配置 (.env)

```bash
# 运行环境
ENV=production
DEBUG=false

# 数据库
DATABASE_URL=sqlite:///home/your_username/opspilot_data/app.db

# 安全密钥（必须修改）
SECRET_KEY=your-random-secret-key-min-32-characters

# CORS（同域部署，可注释掉或设为同一域）
# CORS_ORIGINS 在同域部署时不需要特别配置
# 如果需要明确设置，可以设为：
# CORS_ORIGINS=https://your-domain.serv00.com

# 服务端口
HOST=0.0.0.0
PORT=8000
```

### 后端 CORS 配置说明

同域部署时，浏览器不会触发跨域请求，因此：

1. **无需特殊 CORS 配置**：如果前后端完全同域（协议+域名+端口都相同）
2. **如需保留 CORS 配置**：可以设置为同一域名，不影响功能

修改 `app/core/config.py` 中的 CORS 设置（如需要）：

```python
# 同域部署时，CORS 可以设为允许所有或仅允许本域
CORS_ORIGINS = ["https://your-domain.serv00.com"]  # 明确指定本域
# 或
CORS_ORIGINS = ["*"]  # 允许所有（同域部署时安全）
```

---

## 内存优化

针对 Serv00 512M 内存限制，已做以下优化：

1. **单 Worker 模式**: 只启动 1 个 Uvicorn worker
2. **限制请求数**: 每个 worker 处理 1000 请求后自动重启
3. **减少连接保持时间**: 5 秒 keep-alive
4. **SQLite 数据库**: 无需额外内存开销
5. **静态文件分离**: 前端不占用 Python 进程内存

---

## 故障排查

### 端口被占用
```bash
# 查看占用端口的进程
lsof -i :8000

# 终止进程
kill -9 <PID>
```

### 权限问题
```bash
# 确保脚本可执行
chmod +x ~/opspilot-backend/start.sh
```

### 数据库问题
```bash
# 检查数据库目录权限
ls -la ~/opspilot_data/

# 重新初始化数据库
rm ~/opspilot_data/app.db
cd ~/opspilot-backend
python -c "from app.core.database import init_db; init_db()"
```

### 内存不足
```bash
# 查看内存使用
free -m

# 查看进程内存
ps aux | grep python
```

### 同域部署 404 问题

如果前端页面能打开但 API 调用 404：

1. **检查 Python 应用是否运行**：在 Serv00 面板查看状态
2. **检查路径配置**：确保前端 `config.js` 中的 `API_BASE_URL` 配置正确
3. **检查后端路由**：确认后端应用已正确配置 `/api/*` 路由

---

## 更新部署

### 正常更新（推荐）

使用新版本包直接部署：

```bash
# 1. 上传新版本包
scp opspilot-serv00-deploy-v1.0.1-20250408-001.zip your_username@srvXX.serv00.com:~

# 2. SSH 登录并解压
ssh your_username@srvXX.serv00.com
cd ~
unzip opspilot-serv00-deploy-v1.0.1-20250408-001.zip

# 3. 备份数据（重要）
cp ~/opspilot_data/app.db ~/opspilot_data/app.db.bak

# 4. 更新后端（注意保留 .env 文件）
cd ~/opspilot-backend
# 备份当前版本（便于回退）
cp -r . ~/opspilot-backend-v$(cat VERSION).bak
# 解压新版本
unzip -o ~/backend-dist.zip
# 保留原有配置
# 重启服务

# 5. 更新前端
cd ~/domains/your-domain.serv00.com/public_html/
rm -rf dist
unzip ~/frontend-dist.zip

# 6. 验证新版本
cat ~/opspilot-backend/VERSION
cat ~/domains/your-domain.serv00.com/public_html/dist/config.js | grep VERSION
```

### 快速回退

如果更新后有问题，立即回退：

```bash
# 使用之前备份的版本目录
cd ~/opspilot-backend
cp -r ~/opspilot-backend-v1.0.0-20250407-001.bak/* .
# 重启服务
```

---

## 安全建议

1. **修改默认密钥**: 务必修改 SECRET_KEY
2. **启用 HTTPS**: Serv00 自动提供 SSL
3. **同域部署优势**: 无需担心 CORS 安全问题，API 请求天然受同源策略保护
4. **定期备份**: 备份数据库文件
5. **文件权限**: 上传目录设置适当权限

---

## 监控和维护

```bash
# 查看日志
tail -f ~/opspilot-backend/logs/app.log

# 检查服务状态
ps aux | grep serv00_start

# 查看磁盘使用
df -h

# 查看内存使用
free -m

# 查看当前部署版本
echo "=== 前端版本 ==="
grep VERSION ~/domains/*/public_html/dist/config.js
echo "=== 后端版本 ==="
cat ~/opspilot-backend/VERSION
```

---

## 联系支持

- Serv00 文档: https://docs.serv00.com
- 项目文档: 查看项目 README.md
