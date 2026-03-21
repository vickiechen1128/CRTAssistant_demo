# CRTAssistant Demo

基于 FastAPI + React 的轻量级应用脚手架，参考 week2/app 实验技术栈构建。

## 技术栈

### 后端 (Backend)
- **FastAPI** - 高性能 Web 框架
- **SQLite** - 轻量级数据库
- **Uvicorn** - ASGI 服务器
- **Pydantic** - 数据验证

### 前端 (Frontend)
- **React 18** - UI 框架
- **Vite** - 构建工具
- **原生 CSS** - 样式

## 项目结构

```
CRTAssistant_demo/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── main.py       # FastAPI 入口
│   │   ├── db.py         # SQLite 数据库操作
│   │   ├── routers/      # API 路由
│   │   └── services/     # 业务逻辑服务
│   ├── requirements.txt  # Python 依赖
│   └── run.py            # 启动脚本
├── frontend/             # React 前端
│   ├── src/
│   │   ├── components/   # React 组件
│   │   ├── hooks/        # 自定义 Hooks
│   │   ├── services/     # API 服务
│   │   ├── App.jsx       # 主组件
│   │   └── main.jsx      # 入口
│   ├── package.json      # Node 依赖
│   └── vite.config.js    # Vite 配置
└── data/                 # SQLite 数据库目录
```

## 快速开始

### 1. 安装后端依赖

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 安装前端依赖

```bash
cd frontend

# 使用 npm 或 pnpm
npm install
# 或
pnpm install
```

### 3. 启动开发服务器

**终端 1 - 启动后端:**
```bash
cd backend
python run.py
```
后端运行在 http://127.0.0.1:8000

**终端 2 - 启动前端:**
```bash
cd frontend
npm run dev
```
前端运行在 http://127.0.0.1:5173

### 4. 访问应用

- **前端页面**: http://localhost:5173
- **API 文档**: http://127.0.0.1:8000/docs
- **API 基础地址**: http://127.0.0.1:8000

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/items` | 获取所有 items |
| POST | `/items` | 创建 item |
| GET | `/items/{id}` | 获取单个 item |
| PUT | `/items/{id}` | 更新 item |
| DELETE | `/items/{id}` | 删除 item |

## 开发指南

### 添加新 API 路由

1. 在 `backend/app/routers/` 创建新文件，如 `users.py`:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("")
def list_users():
    return [{"id": 1, "name": "Alice"}]
```

2. 在 `backend/app/main.py` 注册路由:

```python
from .routers import items, users

app.include_router(items.router)
app.include_router(users.router)  # 新增
```

3. 前端添加对应 API 调用:

```javascript
// frontend/src/services/api.js
export const usersApi = {
  list: () => request('/users'),
};
```

### 前端组件开发

- 组件放在 `frontend/src/components/`
- Hooks 放在 `frontend/src/hooks/`
- API 服务放在 `frontend/src/services/`

## 生产部署

### 构建前端

```bash
cd frontend
npm run build
```

构建产物在 `frontend/dist/` 目录。

### 启动生产服务

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

FastAPI 会自动挂载 `frontend/dist` 目录作为静态文件。

## 扩展建议

- **后端**: 可以添加 LLM 调用服务（参考原 week2/app 的 `extract_llm.py`）
- **前端**: 可以添加路由（react-router）、状态管理（Zustand/Redux）
- **数据库**: 可替换为 PostgreSQL/MySQL
- **部署**: 可使用 Docker 容器化部署

## 参考

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [React 文档](https://react.dev/)
- [Vite 文档](https://vitejs.dev/)
