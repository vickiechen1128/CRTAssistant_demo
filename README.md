# OpsPilot - 运维准入验收与审计管理平台

面向甲方运维经理的准入验收与审计管理系统，基于 DDD（领域驱动设计）架构构建。

## 核心定位

**OpsPilot** 帮助甲方运维经理：
1. **准入验收**：制定标准化验收标准，系统性核验乙方交付物
2. **审计留痕**：完整记录验收过程（标准制定→交付物提交→审核结论）

> **核心原则**：子工作项 = 验收项 = 甲方制定的检查标准，乙方按标准执行任务并提交证明，甲方按标准核验并留痕

## 技术栈

### 后端 (Backend)
- **FastAPI** - 高性能异步 Web 框架
- **SQLAlchemy** - ORM 框架
- **SQLite** - 开发环境数据库（可迁移至 PostgreSQL/MySQL）
- **Pydantic** - 数据验证与序列化
- **Uvicorn** - ASGI 服务器

### 前端 (Frontend)
- **React 18** - UI 框架
- **Vite** - 构建工具
- **Ant Design** - UI 组件库
- **Zustand** - 状态管理
- **Tailwind CSS** - 样式工具

## 项目结构

采用 **DDD（领域驱动设计）** 分层架构：

```
CRTAssistant_demo/
├── backend/                          # FastAPI 后端
│   ├── app/
│   │   ├── core/                     # 核心基础设施
│   │   │   ├── config.py             # 配置管理
│   │   │   ├── database.py           # 数据库连接
│   │   │   ├── security.py           # 安全/认证
│   │   │   └── exceptions.py         # 异常定义
│   │   ├── modules/                  # 业务模块（DDD 分层）
│   │   │   ├── plan/                 # 计划管理模块 (Module_01)
│   │   │   │   ├── domain/           # 领域层
│   │   │   │   │   ├── entities/     # 领域实体
│   │   │   │   │   ├── value_objects/# 值对象
│   │   │   │   │   ├── repositories/ # 仓储接口
│   │   │   │   │   ├── services/     # 领域服务
│   │   │   │   │   └── events/       # 领域事件
│   │   │   │   ├── application/      # 应用层
│   │   │   │   │   ├── dtos/         # 数据传输对象
│   │   │   │   │   └── plan_service.py
│   │   │   │   ├── infrastructure/   # 基础设施层
│   │   │   │   │   └── persistence/  # 持久化实现
│   │   │   │   └── interfaces/       # 接口层
│   │   │   │       └── api/          # API 接口
│   │   │   ├── inventory/            # 台账管理模块 (Module_02)
│   │   │   │   └── ...               # 同上结构
│   │   │   └── sop_template/         # SOP模板引擎 (Module_03)
│   │   │       └── ...               # 同上结构
│   │   ├── main.py                   # FastAPI 入口
│   │   └── schemas/                  # 共享 Schema
│   ├── requirements.txt              # Python 依赖
│   └── run.py                        # 启动脚本
├── frontend/                         # React 前端
│   ├── src/
│   │   ├── components/               # React 组件
│   │   │   ├── Layout/               # 布局组件
│   │   │   ├── Common/               # 通用组件
│   │   │   └── Business/             # 业务组件
│   │   ├── pages/                    # 页面组件
│   │   ├── stores/                   # Zustand 状态管理
│   │   ├── api/                      # API 客户端
│   │   └── utils/                    # 工具函数
│   ├── package.json
│   └── vite.config.js
├── OpsPilot_AI_PRD_Docs/             # 产品需求文档
│   ├── 00_Global_Architecture.md     # 全局架构
│   ├── 00_Engineering_Standard.md    # 工程规范
│   └── Modules/                      # 模块详细设计
└── data/                             # SQLite 数据库目录
```

## 业务模块

| 模块 | 名称 | 核心职责 | 状态 |
|------|------|----------|------|
| Module_01 | Plan Management | 管理运维计划的完整生命周期 | ✅ 已完成 |
| Module_02 | Inventory Management | 管理应用系统/云服务/账号三类台账 | ✅ 已完成 |
| Module_03 | SOP Template Engine | 管理SOP模板、审核矩阵、驱动工作项生成 | ✅ 已完成 |
| Module_04 | Workflow Execution | 执行工作流，管理任务状态流转 | 🚧 待开发 |
| Module_05 | Knowledge Base | 管理企业运维知识资产 | 🚧 待开发 |
| Module_06 | Verification Engine | 执行核验逻辑（人工/脚本/AI） | 🚧 待开发 |
| Module_07 | File & Deliverable | 管理交付物文件 | 🚧 待开发 |
| Module_08 | Notification Center | 跨模块消息推送 | 🚧 待开发 |

## 快速开始

### 环境要求

- **Python**: 3.10+
- **Node.js**: 18+
- **npm**: 9+ 或 **pnpm**: 8+

### 1. 安装后端依赖

```bash
cd backend

# 创建虚拟环境（推荐）
# 方式一：使用 venv 目录
python3 -m venv venv

# 方式二：使用 .venv 目录（与 start.sh 脚本兼容）
python3 -m venv .venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# 或
source .venv/bin/activate
# Windows:
# venv\Scripts\activate
# 或
# .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 安装前端依赖

```bash
cd frontend

# 使用 npm 安装依赖
npm install

# 或使用 pnpm（更快）
pnpm install
```

### 3. 启动开发服务器

#### 方式一：一键启动（推荐）

```bash
# 在项目根目录执行
./start.sh
```

此脚本会自动：
- 检查 Python 和 Node.js 环境
- 检查并安装前端依赖
- 启动后端服务 (http://127.0.0.1:8000)
- 启动前端服务 (http://127.0.0.1:5173)

#### 方式二：分别启动（开发调试）

**终端 1 - 启动后端:**
```bash
cd backend

# 激活虚拟环境
source venv/bin/activate
# 或
source .venv/bin/activate

# 启动服务
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
- **API 基础地址**: http://127.0.0.1:8000/api/v1

## API 接口概览

### 计划管理 (Plan)
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/plans` | 创建计划 |
| GET | `/api/v1/plans` | 查询计划列表 |
| GET | `/api/v1/plans/{id}` | 获取计划详情 |
| PUT | `/api/v1/plans/{id}` | 更新计划 |
| DELETE | `/api/v1/plans/{id}` | 删除计划 |
| POST | `/api/v1/plans/{id}/start` | 启动计划 |
| POST | `/api/v1/plans/{id}/complete` | 完成计划 |
| POST | `/api/v1/plans/{id}/cancel` | 取消计划 |
| POST | `/api/v1/plans/{id}/inventory` | 关联台账 |

### 台账管理 (Inventory)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/inventories` | 查询台账列表 |
| POST | `/api/v1/inventories` | 创建台账 |
| GET | `/api/v1/inventories/{id}` | 获取台账详情 |
| PUT | `/api/v1/inventories/{id}` | 更新台账 |
| DELETE | `/api/v1/inventories/{id}` | 删除台账 |

### SOP 模板 (SOP Template)
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/sop-templates` | 创建模板 |
| GET | `/api/v1/sop-templates` | 查询模板列表 |
| GET | `/api/v1/sop-templates/{id}` | 获取模板详情 |
| PUT | `/api/v1/sop-templates/{id}` | 更新模板 |
| DELETE | `/api/v1/sop-templates/{id}` | 删除模板 |
| POST | `/api/v1/sop-templates/{id}/publish` | 发布模板 |
| POST | `/api/v1/sop-templates/{id}/deprecate` | 弃用模板 |
| POST | `/api/v1/sop-templates/{id}/clone` | 克隆模板 |
| POST | `/api/v1/sop-templates/{id}/instantiate` | 实例化模板 |

### 审核矩阵 (Audit Matrix)
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/audit-matrix-configs` | 创建审核矩阵 |
| GET | `/api/v1/audit-matrix-configs` | 查询列表 |
| GET | `/api/v1/audit-matrix-configs/{id}` | 获取详情 |
| PUT | `/api/v1/audit-matrix-configs/{id}` | 更新配置 |
| DELETE | `/api/v1/audit-matrix-configs/{id}` | 删除配置 |
| POST | `/api/v1/audit-matrix-configs/{id}/rules` | 添加规则 |
| PUT | `/api/v1/audit-matrix-configs/{id}/rules/{rule_id}` | 更新规则 |
| DELETE | `/api/v1/audit-matrix-configs/{id}/rules/{rule_id}` | 删除规则 |

## 开发指南

### DDD 分层架构规范

```
┌─────────────────────────────────────────────────────────┐
│                    Interfaces 层                         │
│         (Routes, Schemas, Controllers)                  │
├─────────────────────────────────────────────────────────┤
│                   Application 层                         │
│      (Services, DTOs, Use Cases)                        │
├─────────────────────────────────────────────────────────┤
│                     Domain 层                            │
│   (Entities, Value Objects, Repositories, Services)     │
├─────────────────────────────────────────────────────────┤
│                 Infrastructure 层                        │
│       (Persistence, External Services)                  │
└─────────────────────────────────────────────────────────┘
```

**分层职责：**
- **Domain 层**：核心业务逻辑，不依赖其他层
- **Application 层**：协调领域对象完成用例
- **Infrastructure 层**：技术实现细节
- **Interfaces 层**：用户接口和外部交互

### 添加新模块步骤

1. **创建模块目录结构：**
```bash
mkdir -p backend/app/modules/{module_name}/{domain,application,infrastructure,interfaces}
```

2. **按 DDD 分层实现：**
   - `domain/entities/` - 定义领域实体
   - `domain/value_objects/` - 定义值对象
   - `domain/repositories/` - 定义仓储接口
   - `application/` - 实现应用服务
   - `infrastructure/persistence/` - 实现仓储
   - `interfaces/api/routes/` - 定义 API 路由

3. **注册路由**（`backend/app/main.py`）：
```python
from app.modules.{module_name}.interfaces.api.routes import router as new_router
app.include_router(new_router, prefix="/api/v1")
```

### 领域事件处理

领域事件定义在 `domain/events/` 目录，用于跨聚合通信：

```python
# domain/events/plan_events.py
@dataclass
class PlanCreatedEvent:
    plan_id: str
    name: str
    occurred_at: datetime = datetime.utcnow()
```

## 核心概念

### 计划类型与模板映射

| 计划分类 | 模板类型 | 台账操作 | 检查项 |
|----------|----------|----------|--------|
| 新系统上线 | new_system | 新增台账 | 4项：基础资源/台账/安全/监控 |
| 新功能上线 | new_feature | 编辑台账 | 2项：台账/监控 |
| 功能变更 | func_change | 勾选台账 | 2项：台账/监控 |
| 架构变更 | arch_change | 勾选台账 | 4项：基础资源/台账/安全/监控 |
| 安全检查 | security | 不关联 | 4项：漏洞/基线/渗透/文件安全 |

### 工作项层级结构

```
SOP Template
└── Workflow Node (流程节点)
    └── Parent Work Item (父工作项 - 5大类)
        └── Child Work Item (子工作项 - 验收项)
            └── Grandchild Work Item (孙工作项)
```

### 状态流转

**计划状态：**
```
[DRAFT] → [PENDING] → [IN_PROGRESS] → [COMPLETED]
    ↓
[CANCELLED]
```

**模板状态：**
```
[DRAFT] → [ACTIVE] → [ARCHIVED]
```

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

### Docker 部署（推荐）

```bash
# 构建镜像
docker build -t opspilot .

# 运行容器
docker run -d -p 8000:8000 opspilot
```

## 文档

- [全局架构文档](OpsPilot_AI_PRD_Docs/00_Global_Architecture.md)
- [工程规范](OpsPilot_AI_PRD_Docs/00_Engineering_Standard.md)
- [SOP 模板引擎设计](OpsPilot_AI_PRD_Docs/Modules/Module_03_SOP_Template_Engine.md)

## 参考

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [DDD 领域驱动设计](https://domainlanguage.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [React 文档](https://react.dev/)
