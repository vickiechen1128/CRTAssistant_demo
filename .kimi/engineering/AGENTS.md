# OpsPilot AI 编程助手指导文档

> 本文档为 Kimi Code CLI 提供项目特定的开发指导和上下文信息。

## 项目概览

**OpsPilot** 是面向甲方运维经理的准入验收与审计管理系统，基于 DDD（领域驱动设计）架构构建。

- **后端**: FastAPI + SQLAlchemy + SQLite
- **前端**: React 18 + Vite + Ant Design + Zustand
- **架构**: 严格遵循 DDD 分层（Domain/Application/Infrastructure/Interfaces）

## 开发工作流程

### 标准开发流程

```
1. PRD 编写 → OpsPilot_AI_PRD_Docs/Modules/Module_XX_*.md
2. DDD 后端开发 → backend/app/modules/{module_name}/
3. 接口联调测试 → 验证跨模块调用
4. 前端开发 → frontend/src/modules/{module_name}/
```

### 模块目录结构（DDD 标准）

```
backend/app/modules/{module_name}/
├── domain/                    # 领域层 - 核心业务逻辑
│   ├── entities/              # 领域实体
│   ├── value_objects/         # 值对象
│   ├── repositories/          # 仓储接口（仅接口，无实现）
│   ├── services/              # 领域服务
│   └── events/                # 领域事件
├── application/               # 应用层 - 用例编排
│   ├── dtos/                  # 数据传输对象
│   └── {module}_service.py    # 应用服务
├── infrastructure/            # 基础设施层 - 技术实现
│   ├── persistence/
│   │   ├── models/            # SQLAlchemy 模型
│   │   └── repositories/      # 仓储实现
│   └── services/              # 外部服务实现
└── interfaces/                # 接口层 - 对外暴露
    └── api/
        ├── routes/            # FastAPI 路由
        └── schemas/           # Pydantic 模型
```

## 关键规范

### 1. 跨模块调用规范

**只允许在 Application 层和 Infrastructure 层进行跨模块调用**

```python
# ✅ 正确 - Application 层调用其他模块
class PlanService:
    def __init__(self, inventory_service: IInventoryService):
        self._inventory_service = inventory_service

# ✅ 正确 - Infrastructure 层实现跨模块调用
class InventoryServiceImpl(IInventoryService):
    def create_application(self, data: dict) -> Application:
        # 直接调用 inventory 模块的 repository
        pass

# ❌ 错误 - Domain 层直接依赖其他模块
class PlanDomainService:
    def process(self):
        # 不要在这里直接导入其他模块
        from app.modules.inventory import ...  # 禁止
```

### 2. 接口依赖注入

所有跨模块依赖通过接口注入，在模块的 `__init__.py` 中组装：

```python
# backend/app/modules/plan/__init__.py
from app.modules.plan.infrastructure.services.inventory_service_impl import InventoryServiceImpl
from app.modules.plan.application.plan_service import PlanService

# 组装依赖
inventory_service = InventoryServiceImpl()
plan_service = PlanService(inventory_service=inventory_service)
```

### 3. 数据流转规范

跨模块数据流转必须通过 DTO：

```python
# ✅ 正确 - 使用 DTO 传递数据
class PlanCreateDTO(BaseModel):
    name: str
    inventory_ids: List[int]  # 只传递 ID，不传递完整对象

# ❌ 错误 - 直接传递领域实体
class PlanCreateDTO(BaseModel):
    inventories: List[Inventory]  # 不要这样
```

## 常用命令

### 后端开发

```bash
# 启动开发服务器
cd backend
python run.py

# 运行测试
python run_tests.py                    # 全部测试
python run_tests.py plan               # 计划模块测试
python run_tests.py inventory          # 台账模块测试
python run_tests.py --verbose          # 详细输出

# 数据库操作
# 数据库文件位于: backend/data/opspilot.db
```

### 代码质量

```bash
# 格式化代码
black backend/app

# 代码检查
ruff check backend/app
```

## 测试策略

### 1. 单元测试

测试领域逻辑，不依赖外部服务：

```python
# tests/unit/test_plan_domain.py
def test_plan_status_transition():
    plan = Plan.create(...)
    plan.submit()
    assert plan.status == PlanStatus.PENDING
```

### 2. 集成测试

测试 API 接口和跨模块调用：

```python
# tests/integration/api/test_plan_api.py
def test_create_plan_with_inventory_sync(client):
    """测试创建计划时同步创建台账"""
    response = client.post("/api/v1/plans", json={
        "name": "测试计划",
        "category": "new_system_launch",
        "inventory_scope": {...}
    })
    assert response.status_code == 201
    # 验证台账是否同步创建
    inventory = get_inventory_by_plan(...)
    assert inventory is not None
```

### 3. 联调测试要点

当开发涉及多模块调用的功能时，重点验证：

- [ ] 接口调用链是否完整
- [ ] 数据转换是否正确（DTO ↔ Entity ↔ Model）
- [ ] 事务一致性（数据库操作是否回滚）
- [ ] 错误传播（异常是否正确传递和处理）
- [ ] 事件发布（领域事件是否正确触发）

## 参考文档

| 文档 | 路径 | 用途 |
|------|------|------|
| 工程标准 | `OpsPilot_AI_PRD_Docs/00_Engineering_Standard.md` | 编码规范、避坑指南 |
| 全局架构 | `OpsPilot_AI_PRD_Docs/00_Global_Architecture.md` | 业务模型、模块关系 |
| 模块 PRD | `OpsPilot_AI_PRD_Docs/Modules/Module_XX_*.md` | 需求规格、接口定义 |

## 可用 Skills

### `/skill:api-integration-test`

自动化 API 联调测试，验证跨模块接口调用。

**使用场景**: 完成涉及多模块的后端开发后，进行联调测试
**参数**:
- `--module`: 主模块名（如 plan）
- `--scenario`: 测试场景（如 inventory-sync）

### `/skill:generate-ddd-scaffold`

根据 PRD 自动生成 DDD 代码骨架。

**使用场景**: 编写完 PRD 后，快速生成后端代码模板
**参数**:
- `--prd`: PRD 文件路径（如 `Module_04_Verification_Execution.md`）

### `/skill:prd-to-code-checklist`

将 PRD 转换为开发任务清单。

**使用场景**: 开始编码前，生成前后端开发任务清单
**参数**:
- `--prd`: PRD 文件路径

### `/skill:sync-module-prd`

模块 PRD 与全局架构同步校验。

**使用场景**: 更新模块 PRD 后，校验与全局架构的一致性
**参数**:
- `--module`: 模块名称（如 verification）
- `--check-only`: 仅检查，不生成更新建议
- `--update-global`: 自动更新全局架构文档

**工作流程**:
```
1. 更新 Module_XX_{module}_*.md
2. /skill:sync-module-prd --module={module}
3. 根据校验结果更新全局架构（如有需要）
4. 继续后续开发流程
```

## 注意事项

1. **不要修改已完成的模块核心逻辑**（plan/inventory/sop_template），除非修复 bug
2. **新增模块必须遵循 DDD 目录结构**，保持与现有模块一致
3. **跨模块调用必须通过接口**，禁止直接依赖具体实现
4. **所有数据库操作必须通过仓储**，禁止在 Service 中直接使用 Session
5. **前端 Store 必须与后端 API 分层对应**，一个模块一个 Store
