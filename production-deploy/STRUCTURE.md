# production-deploy 目录结构说明

本文档说明 `production-deploy` 目录的完整结构和各文件用途。

## 目录结构

```
production-deploy/
├── frontend/                      # 前端部署文件
│   ├── .env.production           # 前端生产环境配置模板
│   └── dist/                     # 构建后的前端文件（运行时生成）
│       └── .gitkeep              # 保持目录在版本控制中
│
├── backend/                       # 后端部署文件
│   ├── .env.production           # 后端生产环境配置模板
│   ├── start.sh                  # 便捷启动脚本
│   ├── check-version.sh          # 版本查看脚本
│   ├── serv00_start.py          # Serv00 优化启动脚本
│   └── VERSION                   # 版本号文件（构建时生成/更新）
│
├── scripts/                       # 构建脚本
│   ├── build-frontend.sh         # 前端构建脚本
│   └── package-all.sh            # 完整打包脚本（前端+后端）
│
├── docs/                          # 文档
│   └── DEPLOY.md                 # 详细部署指南
│
├── versions/                      # 版本历史目录
│   ├── .gitkeep                  # 保持目录在版本控制中
│   └── version-history.md        # 版本历史记录
│
├── .gitignore                     # Git 忽略规则
├── STRUCTURE.md                   # 本文件
└── README.md                      # 项目说明文档
```

## 文件详细说明

### frontend/

| 文件 | 说明 |
|------|------|
| `.env.production` | 前端生产环境配置模板，构建时会被复制到源码目录 |
| `dist/` | 前端构建输出目录（运行时生成），包含静态文件 |

### backend/

| 文件 | 说明 |
|------|------|
| `.env.production` | 后端生产环境配置模板，部署时复制为 `.env` 使用 |
| `start.sh` | 便捷启动脚本，用于手动启动后端服务 |
| `check-version.sh` | 版本查看脚本，显示当前版本和运行状态 |
| `serv00_start.py` | Serv00 平台专用的启动脚本 |
| `VERSION` | 版本号文件，构建时自动生成/更新 |

**注意**: `app/` 和 `requirements.txt` 在构建时从项目根目录的 `backend/` 复制过来。

### scripts/

| 文件 | 说明 |
|------|------|
| `build-frontend.sh` | 仅构建前端，生成 `frontend-dist.zip` |
| `package-all.sh` | 构建前端+后端，生成完整部署包 |

### docs/

| 文件 | 说明 |
|------|------|
| `DEPLOY.md` | 详细的部署指南，包含版本号规范、回退操作等 |

### versions/

| 文件 | 说明 |
|------|------|
| `version-history.md` | 版本历史记录，构建时自动更新 |
| `*.zip` | 历史版本包（构建时生成） |

## 构建流程

运行 `scripts/package-all.sh` 后：

1. 构建前端 → `frontend/dist/`
2. 复制后端文件 → `backend/app/` 和 `backend/requirements.txt`
3. 生成版本号 → 写入 `backend/VERSION`
4. 打包 → `versions/` 目录
5. 创建快捷链接 → `frontend-dist.zip` 和 `backend-dist.zip`

## 部署流程

1. 上传 `opspilot-serv00-deploy-v{版本}.zip` 到服务器
2. 解压部署包
3. 部署前端到 Web 服务器目录
4. 部署后端到应用目录
5. 配置环境变量
6. 启动服务

详细步骤请参考 `docs/DEPLOY.md`。
