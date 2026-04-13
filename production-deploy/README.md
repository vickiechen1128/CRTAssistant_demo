# OpsPilot 生产环境部署包

专为 Serv00.com (FreeBSD, 512M RAM, 3G 空间) 优化的部署方案。

> **部署模式**: Proxy 模式，前后端同域部署
> **代码位置**: `~/opspilot/`

---

## 版本号规范

OpsPilot 使用语义化版本规范，格式如下：

```
v主版本.次版本.修订-YYYYMMDD-构建序号
```

**示例**: `v1.2.0-20250407-001`

### 字段说明

| 字段 | 位置 | 说明 | 变更时机 |
|------|------|------|----------|
| v | 前缀 | 版本标识 | 固定 |
| 主版本 | 第1位 | 重大功能更新 | 不兼容的API更改时递增 |
| 次版本 | 第2位 | 新增功能 | 向后兼容的功能添加时递增 |
| 修订号 | 第3位 | Bug修复 | 向后兼容的问题修复时递增 |
| 日期 | YYYYMMDD | 构建日期 | 自动 |
| 构建序号 | 001-999 | 当日第几次构建 | 自动递增 |

### 版本文件

构建后会生成以下文件：

```
production-deploy/
├── versions/
│   └── opspilot-serv00-proxy-v1.0.0-20250407-001.zip  # 完整部署包
└── opspilot-serv00-proxy-latest.zip                   # 最新部署包（快捷方式）
```

### 版本回退

如需回退到历史版本，从 `versions/` 目录找到对应版本包，解压部署即可。

详细回退步骤请参考 `docs/DEPLOY.md` 的**版本回退**章节。

---

## 目录结构

```
production-deploy/
├── backend-dist/                # 后端代码（构建产物）
├── scripts/
│   └── build-serv00-proxy.sh    # ⭐ Proxy 模式打包脚本
├── docs/
│   └── DEPLOY.md                # 详细部署指南
├── versions/                    # 版本历史目录
├── .gitignore                   # Git 忽略规则
├── README.md                    # 本文件
└── STRUCTURE.md                 # 目录结构说明
```

生产环境部署后的目录结构：

```
~
├── opspilot/                    # 应用主目录 ⭐
│   ├── app/                     # 后端业务代码
│   ├── frontend/                # 前端文件
│   │   └── dist/               # 构建后的前端
│   ├── serv00_start.py         # 启动脚本
│   ├── requirements.txt        # Python 依赖
│   ├── .env                    # 环境配置
│   └── VERSION                 # 版本号文件
├── opspilot_data/               # 数据库目录
└── opspilot_uploads/            # 上传文件目录
```

---

## 快速开始

### 1. 构建部署包（Proxy 模式）

```bash
cd production-deploy/scripts
chmod +x build-serv00-proxy.sh
./build-serv00-proxy.sh
```

这将生成：
- `versions/opspilot-serv00-proxy-v{版本}.zip` - 带版本号的部署包
- `opspilot-serv00-proxy-latest.zip` - 无版本号的快捷包

### 2. 指定版本号打包

```bash
./build-serv00-proxy.sh
# 脚本会自动生成版本号: v1.0.0-YYYYMMDD-001
```

如需手动指定版本，修改脚本中的版本变量：
```bash
MAJOR_VERSION="1"
MINOR_VERSION="1"  # 改为新版本
PATCH_VERSION="0"
```

---

## 部署到 Serv00

### 上传文件

```bash
# 上传带版本号的完整包
scp opspilot-serv00-proxy-v1.0.0-20250407-001.zip your_username@srvXX.serv00.com:~

# 或上传快捷包（始终是最新版本）
scp opspilot-serv00-proxy-latest.zip your_username@srvXX.serv00.com:~
```

### 解压并部署

```bash
ssh your_username@srvXX.serv00.com
cd ~

# 停止现有服务
pkill -f serv00_start.py

# 备份数据
cp ~/opspilot_data/app.db ~/opspilot_data/app.db.bak.$(date +%Y%m%d-%H%M%S)

# 清理旧代码
rm -rf ~/opspilot

# 解压部署包
unzip opspilot-serv00-proxy-latest.zip

# 部署到 ~/opspilot/
mkdir -p ~/opspilot
cd ~/opspilot
unzip -o ~/backend-dist.zip
mv backend-dist/* .
rm -rf backend-dist
mkdir -p frontend
unzip -o ~/frontend-dist.zip -d frontend/dist

# 配置环境变量
cp .env.production .env
nano .env  # 修改 SECRET_KEY

# 启动服务
nohup python serv00_start.py > app.log 2>&1 &

# 查看日志
tail -f app.log
```

### 配置 Serv00 面板

1. 登录 https://panel.serv00.com
2. 进入 **WWW Websites**
3. 添加或编辑网站：
   - **Domain**: your-domain.serv00.com
   - **Type**: Proxy
   - **Proxy Target**: `http://localhost:60361`

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

**查看前端版本**：浏览器控制台输入 `window.APP_CONFIG.VERSION`

### 后端配置 (.env)

复制并编辑 `~/opspilot/.env`：

```bash
cp ~/opspilot/.env.production ~/opspilot/.env
nano ~/opspilot/.env
```

关键配置项：
- `SECRET_KEY`: 随机密钥（必须修改）
- `PORT`: 服务端口（默认 60361，与 Proxy 配置一致）
- `DATABASE_URL`: 数据库路径

**查看后端版本**：
```bash
cat ~/opspilot/VERSION
```

---

## 系统要求

- **平台**: FreeBSD (Serv00.com)
- **内存**: 512 MB（已优化适配）
- **磁盘**: 3 GB
- **Python**: 3.9+
- **Node.js**: 18+（仅构建时需要）

---

## Proxy 模式特点

1. **单一入口**: 所有请求通过 Proxy 转发到后端
2. **后端托管前端**: FastAPI 同时提供 API 和静态文件
3. **简化配置**: 不需要在面板配置静态网站
4. **同域部署**: 天然避免 CORS 问题

---

## 优化说明

针对 Serv00 资源限制，做了以下优化：

1. **内存优化**:
   - 单 Worker 模式
   - 限制请求数自动重启
   - SQLite 零额外内存

2. **空间优化**:
   - 前端仅保留构建产物
   - 后端排除缓存和测试文件

3. **性能优化**:
   - 减少连接保持时间
   - 代码分割和懒加载

4. **版本管理**:
   - 自动版本号生成
   - 版本历史记录
   - 快速回退支持

---

## 故障排查

### 502 Bad Gateway

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

1. **检查前端目录**:
   ```bash
   ls -la ~/opspilot/frontend/dist/
   ```

2. **检查日志中的前端路径**:
   ```bash
   grep "前端路径" ~/opspilot/app.log
   ```

查看 `docs/DEPLOY.md` 中的详细故障排查章节。

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

## 更新日志

### v1.0.0 (2025-04-10)
- 初始版本
- 支持 Serv00 FreeBSD 部署
- 512M 内存优化
- Proxy 模式部署
- 语义化版本管理
- 版本回退支持

---

## 许可证

MIT License
