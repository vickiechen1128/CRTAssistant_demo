# OpsPilot Serv00 部署指南（Proxy 模式）

> **部署模式**: 前后端同域部署，Serv00 面板配置 Proxy
> **代码位置**: `~/opspilot/`
> **前端位置**: `~/opspilot/frontend/dist/`

---

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
│   ├── opspilot-serv00-proxy-v1.0.0-20250407-001.zip  # 完整部署包
│   └── version-history.md             # 版本历史记录
└── opspilot-serv00-proxy-latest.zip   # 最新部署包（快捷方式）
```

---

## 部署包说明

```
opspilot-serv00-proxy-v{版本号}.zip
├── backend-dist.zip       # 后端 Python 应用
├── frontend-dist.zip      # 前端静态文件
└── docs/                  # 文档
```

---

## 部署步骤（Proxy 模式）

Proxy 模式是指：
- Serv00 面板配置 **Proxy** 类型网站
- 所有请求（包括前端页面和 API）都通过 Proxy 转发到后端
- 后端同时提供 API 服务和前端静态文件

### 第一步：上传文件

```bash
# 在本地执行，上传到 Serv00
scp opspilot-serv00-proxy-latest.zip your_username@srvXX.serv00.com:~
```

### 第二步：登录并解压

```bash
# SSH 登录
ssh your_username@srvXX.serv00.com

# 进入主目录
cd ~

# 解压部署包
unzip opspilot-serv00-proxy-latest.zip
```

### 第三步：部署到 ~/opspilot/

```bash
# 停止现有服务（如果有）
pkill -f serv00_start.py

# 备份现有数据（重要！）
mkdir -p ~/opspilot_data
cp ~/opspilot_data/app.db ~/opspilot_data/app.db.bak.$(date +%Y%m%d-%H%M%S) 2>/dev/null || true

# 清理旧代码（保留数据目录）
rm -rf ~/opspilot

# 创建 opspilot 目录
mkdir -p ~/opspilot

# 解压后端
cd ~/opspilot
unzip -o ~/backend-dist.zip
mv backend-dist/* .
rm -rf backend-dist

# 解压前端
mkdir -p ~/opspilot/frontend
unzip -o ~/frontend-dist.zip -d ~/opspilot/frontend/dist

# 检查目录结构
ls -la ~/opspilot/
ls -la ~/opspilot/frontend/dist/
```

### 第四步：配置环境变量

```bash
cd ~/opspilot

# 复制配置模板
cp .env.production .env

# 编辑配置
nano .env
```

修改以下配置项：

```bash
# 安全密钥（必须修改！生成随机字符串）
SECRET_KEY=your-random-secret-key-min-32-characters

# 数据库路径（保持默认即可）
DATABASE_URL=sqlite:///home/your_username/opspilot_data/app.db

# 服务端口（保持默认）
PORT=60361

# CORS（同域部署，可保持默认）
CORS_ORIGINS=["https://your-domain.serv00.com"]
```

### 第五步：配置 Serv00 面板

1. 登录 https://panel.serv00.com
2. 进入 **WWW Websites**
3. 添加或编辑网站：
   - **Domain**: your-domain.serv00.com
   - **Type**: Proxy
   - **Proxy Target**: `http://localhost:60361`

> **注意**: Proxy 模式下不需要配置 Root directory，所有请求都会转发到后端

### 第六步：启动服务

```bash
cd ~/opspilot

# 启动服务
nohup python serv00_start.py > app.log 2>&1 &

# 查看日志
tail -f app.log
```

等待看到以下输出表示启动成功：
```
==================================================
OpsPilot Serv00 生产环境
版本: v1.0.0-20250410-001
构建时间: 2026-04-10 16:25:32
==================================================
启动服务: http://0.0.0.0:60361
前端路径: ~/opspilot/frontend/dist
==================================================
```

---

## 目录结构

```
~
├── opspilot/                    # 应用主目录
│   ├── app/                     # 后端业务代码
│   ├── frontend/                # 前端文件
│   │   └── dist/                # 构建后的前端
│   │       ├── index.html
│   │       ├── config.js
│   │       └── assets/
│   ├── serv00_start.py          # 启动脚本
│   ├── requirements.txt         # Python 依赖
│   ├── .env                     # 环境配置
│   ├── .env.production          # 配置模板
│   └── VERSION                  # 版本号文件
│
├── opspilot_data/               # 数据库目录
│   └── app.db                   # SQLite 数据库
│
└── opspilot_uploads/            # 上传文件目录
```

---

## 版本回退

### 查看已部署版本

```bash
# 后端版本
cat ~/opspilot/VERSION

# 前端版本
grep VERSION ~/opspilot/frontend/dist/config.js
```

### 回退到历史版本

```bash
# 1. 确定要回退的版本
VERSION="v1.0.0-20250406-003"

# 2. 备份数据
cp ~/opspilot_data/app.db ~/opspilot_data/app.db.bak.$(date +%Y%m%d%H%M%S)

# 3. 停止服务
pkill -f serv00_start.py

# 4. 清理并重新部署
rm -rf ~/opspilot
mkdir -p ~/opspilot

# 5. 解压指定版本（假设历史版本包在 ~/versions/ 目录）
cd ~/opspilot
unzip ~/versions/opspilot-serv00-proxy-${VERSION}.zip
unzip -o backend-dist.zip
mv backend-dist/* .
rm -rf backend-dist
mkdir -p frontend
unzip -o frontend-dist.zip -d frontend/dist

# 6. 恢复配置
cp .env.production .env
# 根据需要修改 .env

# 7. 启动服务
nohup python serv00_start.py > app.log 2>&1 &
```

---

## 配置说明

### 前端配置 (config.js)

Proxy 模式下，前端 API 地址使用相对路径：

```javascript
window.APP_CONFIG = {
    API_BASE_URL: '/api/v1',
    UPLOAD_BASE_URL: '/uploads',
    APP_NAME: 'OpsPilot',
    VERSION: 'v1.0.0-20250407-001'
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

# 服务端口（与 Serv00 Proxy 配置一致）
HOST=0.0.0.0
PORT=60361

# CORS（同域部署）
CORS_ORIGINS=["https://your-domain.serv00.com"]
```

---

## 内存优化

针对 Serv00 512M 内存限制，已做以下优化：

1. **单 Worker 模式**: 只启动 1 个 Uvicorn worker
2. **限制请求数**: 每个 worker 处理 1000 请求后自动重启
3. **减少连接保持时间**: 5 秒 keep-alive
4. **SQLite 数据库**: 无需额外内存开销

---

## 故障排查

### 502 Bad Gateway

如果看到 502 错误：

1. **检查后端是否运行**:
   ```bash
   ps aux | grep serv00_start
   ```

2. **检查端口是否监听**:
   ```bash
   lsof -i :60361
   ```

3. **查看错误日志**:
   ```bash
   tail -50 ~/opspilot/app.log
   ```

4. **检查 Proxy 配置**:
   - 确认 Serv00 面板中 Proxy Target 是 `http://localhost:60361`
   - 确认不是 `https://localhost:60361`

### 前端页面 404

如果 API 正常但前端页面 404：

1. **检查前端目录**:
   ```bash
   ls -la ~/opspilot/frontend/dist/
   ls -la ~/opspilot/frontend/dist/index.html
   ```

2. **检查日志中的前端路径**:
   ```bash
   grep "前端路径" ~/opspilot/app.log
   ```

### 数据库错误

```bash
# 检查数据库目录权限
ls -la ~/opspilot_data/

# 重新初始化数据库（会清空数据！）
rm ~/opspilot_data/app.db
cd ~/opspilot
python -c "from app.core.database import init_db; init_db()"
```

### 内存不足

```bash
# 查看内存使用
free -m

# 查看进程内存
ps aux | grep python
```

---

## 更新部署

### 正常更新

```bash
# 1. 上传新版本包
scp opspilot-serv00-proxy-latest.zip your_username@srvXX.serv00.com:~

# 2. SSH 登录
ssh your_username@srvXX.serv00.com

# 3. 备份数据
cp ~/opspilot_data/app.db ~/opspilot_data/app.db.bak

# 4. 停止服务
pkill -f serv00_start.py

# 5. 重新部署（按照第三步的步骤）
# ...

# 6. 启动服务
cd ~/opspilot
nohup python serv00_start.py > app.log 2>&1 &

# 7. 验证版本
cat ~/opspilot/VERSION
```

---

## 监控和维护

```bash
# 查看日志
tail -f ~/opspilot/app.log

# 检查服务状态
ps aux | grep serv00_start

# 查看磁盘使用
df -h

# 查看内存使用
free -m

# 查看当前部署版本
echo "=== 后端版本 ==="
cat ~/opspilot/VERSION
echo "=== 前端版本 ==="
grep VERSION ~/opspilot/frontend/dist/config.js
```

---

## 联系支持

- Serv00 文档: https://docs.serv00.com
- 项目文档: 查看项目 README.md
