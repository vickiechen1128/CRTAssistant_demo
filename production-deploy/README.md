# OpsPilot 生产环境部署包

专为 Serv00.com (FreeBSD, 512M RAM, 3G 空间) 优化的部署方案。

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
├── versions/                          # 版本历史目录
│   ├── frontend-v1.0.0-20250407-001.zip   # 带版本号的前端包
│   ├── backend-v1.0.0-20250407-001.zip    # 带版本号的后端包
│   ├── opspilot-serv00-deploy-v1.0.0-20250407-001.zip  # 完整部署包
│   └── version-history.md             # 版本历史记录
├── frontend-dist.zip                  # 最新前端包（快捷方式）
└── backend-dist.zip                   # 最新后端包（快捷方式）
```

### 版本回退

如需回退到历史版本，从 `versions/` 目录找到对应版本包，解压部署即可。

详细回退步骤请参考 `docs/DEPLOY.md` 的**版本回退**章节。

---

## 目录结构

```
production-deploy/
├── frontend/
│   ├── .env.production          # 前端生产环境配置模板
│   └── dist/                    # 构建后的前端文件（运行时生成）
├── backend/
│   ├── .env.production          # 后端生产环境配置模板
│   ├── start.sh                 # 启动脚本
│   ├── check-version.sh         # 版本查看脚本
│   ├── serv00_start.py          # Serv00 优化启动脚本
│   └── VERSION                  # 版本号文件（运行时生成）
├── scripts/
│   ├── build-frontend.sh        # 前端构建脚本
│   └── package-all.sh           # 完整打包脚本
├── docs/
│   └── DEPLOY.md                # 详细部署指南
└── README.md                    # 本文件
```

---

## 快速开始

### 1. 完整打包（推荐）

```bash
cd production-deploy/scripts
chmod +x package-all.sh
./package-all.sh
```

这将生成：
- `versions/frontend-v{版本}.zip` - 带版本号的前端包
- `versions/backend-v{版本}.zip` - 带版本号的后端包
- `versions/opspilot-serv00-deploy-v{版本}.zip` - 完整部署包
- `frontend-dist.zip` / `backend-dist.zip` - 无版本号的快捷包

### 2. 指定版本号打包

```bash
./package-all.sh
# 脚本会自动生成版本号: v1.0.0-YYYYMMDD-001
```

如需手动指定版本：
```bash
# 修改 package-all.sh 中的版本变量
MAJOR_VERSION="1"
MINOR_VERSION="1"  # 改为新版本
PATCH_VERSION="0"
```

### 3. 仅打包前端

```bash
cd production-deploy/scripts
chmod +x build-frontend.sh
./build-frontend.sh
```

或指定版本号：
```bash
./build-frontend.sh v1.0.1-20250408-001
```

### 4. 手动构建

#### 前端
```bash
cd ../frontend
npm install
npm run build
# 构建结果在 dist/ 目录
```

#### 后端
```bash
cd ../backend
pip install -r requirements.txt
python serv00_start.py
```

---

## 部署到 Serv00

### 上传文件

```bash
# 上传带版本号的完整包
scp opspilot-serv00-deploy-v1.0.0-20250407-001.zip your_username@srvXX.serv00.com:~

# 或上传快捷包（始终是最新版本）
scp opspilot-serv00-deploy.zip your_username@srvXX.serv00.com:~
```

### 解压并部署

```bash
ssh your_username@srvXX.serv00.com
cd ~
unzip opspilot-serv00-deploy-v{版本}.zip
```

详细步骤请参考 `docs/DEPLOY.md`

---

## 配置说明

### 前端配置

编辑 `frontend/dist/config.js`：

```javascript
window.APP_CONFIG = {
    // 同域部署：使用相对路径
    API_BASE_URL: '/api/v1',
    UPLOAD_BASE_URL: '/uploads',
    // 跨域部署：使用完整 URL
    // API_BASE_URL: 'https://your-domain.serv00.net/api/v1',
    // UPLOAD_BASE_URL: 'https://your-domain.serv00.net/uploads',
    APP_NAME: 'OpsPilot',
    VERSION: 'v1.0.0-20250407-001'  // 自动写入的版本号
};
```

**查看前端版本**：浏览器控制台输入 `window.APP_CONFIG.VERSION`

### 后端配置

复制并编辑 `backend/.env`：

```bash
cp backend/.env.production backend/.env
nano backend/.env
```

关键配置项：
- `SECRET_KEY`: 随机密钥（必须修改）
- `CORS_ORIGINS`: 同域部署时可注释掉，跨域部署时填写前端域名
- `DATABASE_URL`: 数据库路径

**查看后端版本**：
```bash
cd ~/opspilot-backend
./check-version.sh
# 或
cat VERSION
```

---

## 系统要求

- **平台**: FreeBSD (Serv00.com)
- **内存**: 512 MB（已优化适配）
- **磁盘**: 3 GB
- **Python**: 3.9+
- **Node.js**: 18+（仅构建时需要）

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
   - 静态文件分离

3. **性能优化**:
   - 静态文件直接由 Web 服务器处理
   - 减少连接保持时间
   - 代码分割和懒加载

4. **版本管理**:
   - 自动版本号生成
   - 版本历史记录
   - 快速回退支持

---

## 文件清单

### 前端包 (frontend-v{版本}.zip)
- `dist/` - 静态文件目录
  - `index.html` - 入口页面
  - `config.js` - 运行时配置（含版本号）
  - `assets/` - JS/CSS 资源

### 后端包 (backend-v{版本}.zip)
- `app/` - Python 业务代码
- `requirements.txt` - 依赖列表
- `serv00_start.py` - 启动脚本
- `start.sh` - 便捷启动脚本
- `check-version.sh` - 版本查看脚本
- `.env.production` - 配置模板
- `VERSION` - 版本号文件

---

## 故障排查

查看 `docs/DEPLOY.md` 中的故障排查章节。

---

## 更新日志

### v1.0.0 (2025-04-07)
- 初始版本
- 支持 Serv00 FreeBSD 部署
- 512M 内存优化
- 语义化版本管理
- 版本回退支持

---

## 许可证

MIT License
