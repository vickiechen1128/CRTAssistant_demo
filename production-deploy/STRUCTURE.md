# production-deploy 目录结构说明

本文档说明 `production-deploy` 目录的完整结构和各文件用途。

> **部署模式**: Serv00 Proxy 模式，前后端同域部署
> **代码位置**: `~/opspilot/`

---

## 目录结构

```
production-deploy/
├── backend-dist/                  # 后端代码（构建产物）
│   ├── app/                      # 后端业务代码
│   ├── .env.production           # 环境配置模板
│   └── VERSION                   # 版本号文件
│
├── scripts/                       # 构建脚本
│   └── build-serv00-proxy.sh     # Serv00 Proxy 模式打包脚本 ⭐
│
├── docs/                          # 文档
│   └── DEPLOY.md                 # 详细部署指南（Proxy 模式）
│
├── versions/                      # 版本历史目录
│   ├── .gitkeep                  # 保持目录在版本控制中
│   └── version-history.md        # 版本历史记录
│
├── .gitignore                     # Git 忽略规则
├── STRUCTURE.md                   # 本文件
└── README.md                      # 项目说明文档
```

---

## 生产环境目录结构

部署到 Serv00 后的目录结构：

```
~
├── opspilot/                      # 应用主目录 ⭐
│   ├── app/                       # 后端业务代码
│   │   ├── main.py               # FastAPI 入口
│   │   ├── core/                 # 核心模块
│   │   ├── modules/              # 业务模块
│   │   └── ...
│   │
│   ├── frontend/                  # 前端文件 ⭐
│   │   └── dist/                 # 构建后的前端
│   │       ├── index.html
│   │       ├── config.js         # 运行时配置
│   │       └── assets/           # JS/CSS 资源
│   │
│   ├── serv00_start.py           # Serv00 启动脚本 ⭐
│   ├── requirements.txt          # Python 依赖
│   ├── .env                      # 环境配置（部署后创建）
│   ├── .env.production           # 配置模板
│   └── VERSION                   # 版本号文件
│
├── opspilot_data/                 # 数据库目录
│   └── app.db                    # SQLite 数据库
│
└── opspilot_uploads/              # 上传文件目录
```

---

## 文件详细说明

### scripts/

| 文件 | 说明 |
|------|------|
| `build-serv00-proxy.sh` ⭐ | **Proxy 模式专用打包脚本**，生成 `opspilot-serv00-proxy-v{版本}.zip` |

### backend-dist/

| 文件/目录 | 说明 |
|-----------|------|
| `app/` | 后端业务代码（FastAPI 应用） |
| `.env.production` | 生产环境配置模板 |
| `VERSION` | 版本号文件 |

### docs/

| 文件 | 说明 |
|------|------|
| `DEPLOY.md` | 详细的 Proxy 模式部署指南 |

### versions/

| 文件 | 说明 |
|------|------|
| `version-history.md` | 版本历史记录，构建时自动更新 |
| `opspilot-serv00-proxy-v{版本}.zip` | 历史版本包（构建时生成） |

---

## 构建流程

运行 `scripts/build-serv00-proxy.sh` 后：

1. **构建前端** → `frontend/dist/`
2. **准备后端** → `backend-dist/`
   - 复制 `app/` 目录
   - 复制 `requirements.txt`
   - 生成 `serv00_start.py`
   - 生成 `VERSION` 文件
3. **打包** → `versions/opspilot-serv00-proxy-v{版本}.zip`
   - 包含 `backend-dist.zip`
   - 包含 `frontend-dist.zip`
4. **创建快捷链接** → `opspilot-serv00-proxy-latest.zip`

---

## 部署流程

### 1. 构建部署包

```bash
cd production-deploy/scripts
./build-serv00-proxy.sh
```

### 2. 上传到 Serv00

```bash
scp opspilot-serv00-proxy-latest.zip your_username@srvXX.serv00.com:~
```

### 3. 在 Serv00 上部署

```bash
ssh your_username@srvXX.serv00.com

# 停止服务
pkill -f serv00_start.py

# 备份数据
cp ~/opspilot_data/app.db ~/opspilot_data/app.db.bak

# 清理旧代码
rm -rf ~/opspilot

# 解压部署
cd ~
unzip opspilot-serv00-proxy-latest.zip
mkdir -p ~/opspilot
cd ~/opspilot
unzip -o ~/backend-dist.zip
mv backend-dist/* .
rm -rf backend-dist
mkdir -p frontend
unzip -o ~/frontend-dist.zip -d frontend/dist

# 配置环境
cp .env.production .env
nano .env  # 修改 SECRET_KEY

# 启动服务
nohup python serv00_start.py > app.log 2>&1 &
```

### 4. 配置 Serv00 面板

- **Type**: Proxy
- **Proxy Target**: `http://localhost:60361`

---

## Proxy 模式特点

1. **单一入口**: 所有请求通过 Proxy 转发到后端
2. **后端托管前端**: FastAPI 同时提供 API 和静态文件
3. **简化配置**: 不需要在面板配置静态网站
4. **同域部署**: 天然避免 CORS 问题

---

## 关键路径说明

| 路径 | 说明 |
|------|------|
| `~/opspilot/` | 应用主目录 |
| `~/opspilot/app/` | 后端代码 |
| `~/opspilot/frontend/dist/` | 前端静态文件 |
| `~/opspilot_data/` | 数据库目录 |
| `~/opspilot_uploads/` | 上传文件目录 |

---

## 版本管理

### 版本号文件

- **后端**: `~/opspilot/VERSION`
- **前端**: `~/opspilot/frontend/dist/config.js` 中的 `VERSION`

### 查看版本

```bash
# 后端版本
cat ~/opspilot/VERSION

# 前端版本
grep VERSION ~/opspilot/frontend/dist/config.js
```

---

## 故障排查

### 502 Bad Gateway

- 检查后端是否运行: `ps aux | grep serv00_start`
- 检查端口监听: `lsof -i :60361`
- 检查 Proxy 配置是否为 `http://localhost:60361`

### 前端 404

- 检查前端目录: `ls -la ~/opspilot/frontend/dist/`
- 检查日志: `grep "前端路径" ~/opspilot/app.log`

---

## 联系支持

- Serv00 文档: https://docs.serv00.com
- 项目文档: 查看 `docs/DEPLOY.md`
