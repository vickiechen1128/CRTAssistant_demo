# Skill: prd-to-code-checklist

## 基本信息

- **名称**: prd-to-code-checklist
- **描述**: 将 PRD 转换为前后端开发任务清单
- **调用方式**: `/skill:prd-to-code-checklist --prd=<PRD文件名>`

## 使用场景

开始编码前，需要：
1. 明确后端开发任务（实体→仓储→服务→接口）
2. 明确前端开发任务（API→Store→组件→页面）
3. 识别跨模块调用点
4. 评估开发工作量和依赖关系

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `--prd` | string | 是 | PRD 文件名（如 `Module_04_Verification_Execution.md`） |
| `--output` | string | 否 | 输出文件路径（默认输出到控制台） |
| `--format` | string | 否 | 输出格式：markdown/json（默认 markdown） |

## 执行步骤

### 1. 解析 PRD

读取 `OpsPilot_AI_PRD_Docs/Modules/{prd}`，提取：
- 模块名称和职责
- 用户故事列表
- 领域实体定义
- REST API 接口定义
- 跨模块依赖关系
- 前端页面和组件需求

### 2. 生成后端开发清单

**领域层任务**:
```markdown
### 领域层 (Domain Layer)

#### 实体 (Entities)
- [ ] {EntityName}
  - [ ] 定义属性: id, name, status, ...
  - [ ] 实现 create() 工厂方法
  - [ ] 实现业务方法: update(), delete(), ...
  - [ ] 实现状态流转方法: submit(), approve(), reject(), ...
  - [ ] 编写单元测试

#### 值对象 (Value Objects)
- [ ] {StatusVO}
  - [ ] 定义枚举值: DRAFT, PENDING, APPROVED, ...
- [ ] {TypeVO}
  - [ ] 定义枚举值: TYPE_A, TYPE_B, ...

#### 仓储接口 (Repository Interfaces)
- [ ] I{Entity}Repository
  - [ ] get_by_id()
  - [ ] get_all()
  - [ ] create()
  - [ ] update()
  - [ ] delete()
  - [ ] 自定义查询方法: get_by_status(), ...

#### 领域事件 (Domain Events)
- [ ] {EventName}
  - [ ] 定义事件属性
  - [ ] 实现事件处理器
```

**应用层任务**:
```markdown
### 应用层 (Application Layer)

#### DTOs
- [ ] Create{Entity}DTO
- [ ] Update{Entity}DTO
- [ ] {Entity}ResponseDTO
- [ ] {Entity}ListDTO

#### 应用服务 (Application Service)
- [ ] {Module}Service
  - [ ] create_{entity}() - 创建实体
  - [ ] get_{entity}() - 获取详情
  - [ ] list_{entity}s() - 获取列表
  - [ ] update_{entity}() - 更新实体
  - [ ] delete_{entity}() - 删除实体
  - [ ] 跨模块调用方法: sync_with_inventory(), ...
```

**基础设施层任务**:
```markdown
### 基础设施层 (Infrastructure Layer)

#### 数据库模型
- [ ] {Entity}Model (SQLAlchemy)
  - [ ] 定义表结构
  - [ ] 定义字段和索引
  - [ ] 实现 to_entity() 方法
  - [ ] 实现 from_entity() 方法

#### 仓储实现
- [ ] {Entity}RepositoryImpl
  - [ ] 实现所有接口方法
  - [ ] 处理数据库异常

#### 外部服务实现（如有）
- [ ] {ExternalService}Impl
```

**接口层任务**:
```markdown
### 接口层 (Interfaces Layer)

#### API Schema
- [ ] Create{Entity}Request
- [ ] Update{Entity}Request
- [ ] {Entity}Response

#### API 路由
- [ ] POST /api/v1/{module}s - 创建
- [ ] GET /api/v1/{module}s - 列表
- [ ] GET /api/v1/{module}s/{id} - 详情
- [ ] PUT /api/v1/{module}s/{id} - 更新
- [ ] DELETE /api/v1/{module}s/{id} - 删除
- [ ] POST /api/v1/{module}s/{id}/submit - 提交
- [ ] POST /api/v1/{module}s/{id}/approve - 审批
```

### 3. 生成前端开发清单

**API 层任务**:
```markdown
### API 层

- [ ] 创建 `frontend/src/modules/{module}/api/index.js`
- [ ] 实现 API 函数:
  - [ ] create{Entity}(data)
  - [ ] get{Entity}List(params)
  - [ ] get{Entity}ById(id)
  - [ ] update{Entity}(id, data)
  - [ ] delete{Entity}(id)
  - [ ] submit{Entity}(id)
  - [ ] approve{Entity}(id)
```

**Store 层任务**:
```markdown
### Store 层 (Zustand)

- [ ] 创建 `frontend/src/modules/{module}/store/{module}Store.js`
- [ ] 定义状态:
  - [ ] {entity}List: []
  - [ ] current{Entity}: null
  - [ ] loading: false
  - [ ] error: null
- [ ] 实现 Actions:
  - [ ] fetch{Entity}List()
  - [ ] fetch{Entity}ById(id)
  - [ ] create{Entity}(data)
  - [ ] update{Entity}(id, data)
  - [ ] delete{Entity}(id)
```

**组件层任务**:
```markdown
### 组件层

#### 业务组件
- [ ] {Entity}Card - 卡片展示
- [ ] {Entity}Form - 表单组件
- [ ] {Entity}Detail - 详情展示
- [ ] {Entity}StatusBadge - 状态标签

#### 列表组件
- [ ] {Entity}List - 列表容器
- [ ] {Entity}Filters - 筛选器
- [ ] {Entity}Table - 表格
```

**页面层任务**:
```markdown
### 页面层

- [ ] {Entity}ListView - 列表页
  - [ ] 路由: /{module}s
- [ ] {Entity}CreateView - 创建页
  - [ ] 路由: /{module}s/new
- [ ] {Entity}DetailView - 详情页
  - [ ] 路由: /{module}s/:id
- [ ] {Entity}EditView - 编辑页
  - [ ] 路由: /{module}s/:id/edit
```

**路由配置任务**:
```markdown
### 路由配置

- [ ] 创建 `frontend/src/modules/{module}/router.jsx`
- [ ] 在 `frontend/src/router.jsx` 中注册模块路由
- [ ] 在侧边栏菜单中添加导航项
```

### 4. 识别跨模块调用点

```markdown
## 跨模块调用分析

### 依赖的模块
- [ ] inventory - 台账管理
  - [ ] 调用点: 创建计划时同步创建台账
  - [ ] 接口: POST /api/v1/inventory/applications
- [ ] plan - 计划管理
  - [ ] 调用点: 验证任务关联计划
  - [ ] 接口: GET /api/v1/plans/{id}

### 被依赖的模块
- [ ] workflow - 工作流执行
  - [ ] 调用方: 验证任务触发工作流
  - [ ] 接口: POST /api/v1/workflow/instances
```

### 5. 生成开发顺序建议

```markdown
## 推荐开发顺序

### 阶段 1: 领域层 (预计 2-3 天)
1. 定义值对象
2. 实现领域实体
3. 定义仓储接口
4. 编写单元测试

### 阶段 2: 应用层 (预计 1-2 天)
1. 定义 DTOs
2. 实现应用服务
3. 处理跨模块调用

### 阶段 3: 基础设施层 (预计 1-2 天)
1. 实现数据库模型
2. 实现仓储
3. 配置数据库迁移

### 阶段 4: 接口层 (预计 1 天)
1. 实现 API 路由
2. 注册路由到 main.py

### 阶段 5: 联调测试 (预计 1-2 天)
1. 使用 /skill:api-integration-test 测试
2. 修复问题

### 阶段 6: 前端开发 (预计 3-5 天)
1. API 层
2. Store 层
3. 组件层
4. 页面层
```

## 示例

### 示例：验证执行模块

```
/skill:prd-to-code-checklist --prd=Module_04_Verification_Execution.md
```

**预期输出**:
```markdown
# Module_04_Verification_Execution 开发任务清单

## 模块信息
- **模块名称**: verification
- **模块职责**: 执行验收逻辑（人工/脚本/AI）
- **预计开发周期**: 10-15 天

## 后端开发任务

### 领域层
- [ ] VerificationTask 实体
  - [ ] 属性: id, plan_id, work_item_id, status, method, result, ...
  - [ ] 方法: create(), start(), complete(), fail(), retry()
- [ ] VerificationRecord 实体
  - [ ] 属性: id, task_id, check_item, result, evidence, ...
- [ ] VerificationScript 实体
  - [ ] 属性: id, name, script_type, content, parameters, ...
- [ ] 值对象: VerificationStatus, VerificationMethod, ScriptType
- [ ] 仓储接口: IVerificationTaskRepository, IVerificationRecordRepository, IVerificationScriptRepository

### 应用层
- [ ] DTOs: CreateVerificationTaskDTO, UpdateVerificationTaskDTO, ...
- [ ] VerificationService
  - [ ] create_task() - 创建验证任务
  - [ ] execute_task() - 执行任务（人工/脚本/AI）
  - [ ] get_task_result() - 获取结果
  - [ ] retry_task() - 重试失败任务

### 基础设施层
- [ ] 数据库模型: VerificationTaskModel, VerificationRecordModel, VerificationScriptModel
- [ ] 仓储实现: VerificationTaskRepositoryImpl, ...
- [ ] 脚本执行服务: ScriptExecutionService

### 接口层
- [ ] API 路由:
  - POST /api/v1/verification/tasks
  - GET /api/v1/verification/tasks
  - GET /api/v1/verification/tasks/{id}
  - POST /api/v1/verification/tasks/{id}/execute
  - POST /api/v1/verification/tasks/{id}/retry

## 前端开发任务

### API 层
- [ ] verificationApi.createTask(data)
- [ ] verificationApi.executeTask(id)
- [ ] verificationApi.getTaskResult(id)

### Store 层
- [ ] verificationStore
  - [ ] state: tasks, currentTask, executionResult
  - [ ] actions: fetchTasks, executeTask, retryTask

### 组件层
- [ ] VerificationTaskCard
- [ ] VerificationTaskForm
- [ ] VerificationResultViewer
- [ ] ScriptExecutionPanel

### 页面层
- [ ] VerificationTaskListView (/verification/tasks)
- [ ] VerificationTaskDetailView (/verification/tasks/:id)
- [ ] ScriptManagementView (/verification/scripts)

## 跨模块调用

### 依赖模块
- [ ] plan - 获取计划信息
- [ ] inventory - 获取台账信息用于验证
- [ ] workflow - 工作项状态更新

## 开发顺序

1. 领域层 (2天)
2. 应用层 (1天)
3. 基础设施层 (1天)
4. 接口层 (1天)
5. 联调测试 (2天)
6. 前端开发 (3天)

总计: 10 天
```

## 输出格式

### Markdown 格式（默认）
适合直接保存为开发文档，在项目中跟踪进度。

### JSON 格式
适合与其他工具集成，如项目管理工具、CI/CD 流水线等。

```json
{
  "module": "verification",
  "backend": {
    "domain": [...],
    "application": [...],
    "infrastructure": [...],
    "interfaces": [...]
  },
  "frontend": {
    "api": [...],
    "store": [...],
    "components": [...],
    "views": [...]
  },
  "cross_module_calls": [...],
  "estimated_days": 10
}
```

## 注意事项

1. 任务清单基于 PRD 生成，实际开发时可能需要调整
2. 跨模块调用需要与相关模块开发者协调
3. 时间估算是参考值，根据实际复杂度调整
4. 建议将清单保存到项目文档中，跟踪开发进度
