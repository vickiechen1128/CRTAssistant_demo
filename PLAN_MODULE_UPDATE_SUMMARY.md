# 计划管理模块 (Module_01) 更新总结

## 更新概述

根据 `Module_01_Plan_Management_Optimized.md` 优化版文档，对计划管理模块进行了全面增强，强化了与台账管理模块的双向关联，支持功能模块独立实体的CRUD操作。

## 主要变更

### 1. 领域层 (Domain Layer)

#### 新增值对象
- **`AffectedModule`** (`domain/value_objects/affected_module.py`)
  - 记录受影响功能模块及变更内容
  - 属性：module_id, module_name, action, before_version, after_version, change_description
  - 支持操作类型：create/update/delete

#### 更新实体
- **`Plan`** (`domain/entities/plan.py`)
  - 新增 `affected_modules: List[AffectedModule]` - 受影响功能模块列表
  - 新增 `approval_files_detail: List[Dict]` - 审批材料详细信息
  - 新增 `template_type: str` - 工作流模板类型
  - 新增 `actual_start_time` 和 `actual_end_time` 字段
  - 新增方法：`add_affected_module()`, `update_affected_modules()`, `add_approval_file()`
  - 更新 `complete()` 方法：触发 PlanCompletedEvent

#### 更新值对象
- **`Category`** (`domain/value_objects/category.py`)
  - 新增 `label` 属性 - 分类显示标签
  - 新增 `default_template_type` 属性 - 默认模板类型

- **`Priority`** (`domain/value_objects/priority.py`)
  - 新增 `label` 属性 - 优先级显示标签

- **`PlanStatus`** (`domain/value_objects/plan_status.py`)
  - 新增 `label` 属性 - 状态显示标签

#### 更新领域事件
- **`PlanCreatedEvent`** - 添加 `template_type` 字段
- **`PlanCompletedEvent`** - 扩展字段：plan_name, category, affected_modules, inventory_ids
  - 用于触发台账更新和生命周期日志生成

### 2. 基础设施层 (Infrastructure Layer)

#### 更新数据库模型
- **`PlanModel`** (`infrastructure/persistence/models/plan_model.py`)
  - 新增 `affected_modules` (JSON) - 受影响功能模块列表
  - 新增 `approval_files_detail` (JSON) - 审批材料详细信息
  - 新增 `template_type` (String) - 模板类型
  - 新增 `related_inventory_ids` (JSON) - 关联台账ID列表
  - 新增索引优化查询性能

#### 更新仓储实现
- **`PlanRepositoryImpl`** (`infrastructure/persistence/plan_repository_impl.py`)
  - 更新 `_to_model()` - 处理新字段序列化
  - 更新 `_update_model()` - 处理新字段更新
  - 更新 `_to_entity()` - 处理新字段反序列化
  - `get_next_sequence()` - 支持 PlanID 生成（PLAN-YYYYMMDD-XXX格式）

### 3. 应用层 (Application Layer)

#### 更新 DTOs
- **新增 DTOs** (`application/dtos/plan_dtos.py`)
  - `ApprovalFileDetail` - 审批材料详细信息
  - `AffectedModuleItem` - 受影响功能模块项
  - `PlanPreviewRequest/Response` - 变更预览请求/响应
  - `GeneratePlanIdResponse` - 预生成PlanID响应
  - `PlanRelatedInventoryInfo` - 关联台账信息
  - `PlanLifecycleLogInfo` - 生命周期日志信息
  - `PlanDetailResponse` - 计划详情响应（完整关联信息）

- **更新现有 DTOs**
  - `CreatePlanRequest` - 添加 affected_modules, approval_files, related_inventory_ids
  - `UpdatePlanRequest` - 添加 affected_modules
  - `PlanResponse` - 添加 category_label, priority_label, status_label, template_type, affected_modules, approval_files

#### 更新应用服务
- **`PlanService`** (`application/plan_service.py`)
  - 更新 `create_plan()` - 支持 affected_modules 和 approval_files
  - 更新 `update_plan()` - 支持 affected_modules 更新
  - 新增 `get_plan_detail()` - 获取完整关联信息
  - 更新 `complete_plan()` - 触发台账更新事件
  - 新增 `preview_changes()` - 预览计划变更（Step 4）
  - 新增 `generate_plan_id()` - 预生成PlanID

### 4. 接口层 (Interface Layer)

#### 更新 Schemas
- **新增 Schemas** (`interfaces/api/schemas/plan_schemas.py`)
  - `ApprovalFileDetailSchema`
  - `AffectedModuleItemSchema`
  - `PlanPreviewRequestSchema/ResponseSchema`
  - `GeneratePlanIdResponseSchema`
  - `PlanDetailResponseSchema`

- **更新现有 Schemas**
  - `CreatePlanSchema` - 添加 affected_modules, approval_files, related_inventory_ids
  - `PlanResponseSchema` - 添加各类 label 和扩展字段

#### 更新路由
- **`plan_routes.py`** (`interfaces/api/routes/plan_routes.py`)
  - `GET /plans/generate-id` - 预生成PlanID
  - `POST /plans/preview` - 预览计划变更
  - `GET /plans/{plan_id}/detail` - 获取计划详情（完整关联信息）
  - 保留原有CRUD和状态管理端点

## 业务规则实现

### PlanID 生成规则
- 格式：`PLAN-{YYYYMMDD}-{当日三位流水号}`
- 示例：`PLAN-20240322-001`
- 实现：`PlanId.generate()` + `PlanRepositoryImpl.get_next_sequence()`

### 数据标签生成规则
- 格式：`{分类简码}-{Unix时间戳}`（前缀为PlanID）
- 分类简码映射：
  - new_system → NEW
  - new_feature → FTR
  - func_change → FUN
  - arch_change → ARC
  - security_check → SEC

### 计划分类与台账操作对照

| 计划分类 | 模板类型 | 台账操作 | 生命周期日志 |
|---------|---------|---------|-------------|
| new_system | new_system | 创建应用系统+模块+资源+账号 | system_launch |
| new_feature | new_feature | 创建功能模块 | module_launch |
| func_change | func_change | 更新功能模块 | module_update |
| arch_change | arch_change | 更新应用系统+资源 | system_upgrade |
| security_check | security | 打标签或不操作 | - |

### 状态流转
```
DRAFT → IN_PROGRESS → COMPLETED
  ↓         ↓
CANCELLED ← PENDING
```

## API 端点列表

### 基础 CRUD
- `POST /api/plans` - 创建计划
- `GET /api/plans` - 查询计划列表
- `GET /api/plans/{plan_id}` - 获取计划基本信息
- `PUT /api/plans/{plan_id}` - 更新计划
- `DELETE /api/plans/{plan_id}` - 删除计划

### 增强功能
- `GET /api/plans/generate-id` - 预生成PlanID
- `POST /api/plans/preview` - 预览计划变更
- `GET /api/plans/{plan_id}/detail` - 获取计划详情（含关联信息）

### 状态管理
- `POST /api/plans/{plan_id}/start` - 启动计划
- `POST /api/plans/{plan_id}/complete` - 完成计划
- `POST /api/plans/{plan_id}/cancel` - 取消计划

### 台账关联
- `POST /api/plans/{plan_id}/inventory` - 关联台账

## 与台账模块的双向追溯

### 计划 → 台账追溯
计划详情页可展示：
1. 关联应用系统列表
2. 影响功能模块列表（含操作类型和版本变更）
3. 本次计划产生的生命周期日志

### 台账 → 计划追溯
在台账详情页可查看：
1. 关联计划列表（通过 lifecycle_logs.related_plan_id）
2. 完整的变更历史

## 待实现功能（预留扩展点）

1. **台账操作执行** - `complete_plan()` 中需要根据计划分类调用台账服务
2. **生命周期日志生成** - 需要与台账模块的生命周期日志服务集成
3. **工作流触发** - 计划创建/完成后需要触发 Module_03 的检查项生成
4. **P0计划二次确认** - 需要额外的审批流程实现
5. **时间冲突检测** - 同一应用系统同时段多计划检测

## 测试验证

```python
# 基础导入测试
from app.modules.plan.domain.entities import Plan
from app.modules.plan.domain.value_objects import Category, Priority, PlanStatus, AffectedModule
from app.modules.plan.application import PlanService

# 值对象测试
category = Category('new_feature')
print(category.label)  # 输出: 新功能上线

priority = Priority.from_string('P1')
print(priority.label)  # 输出: P1 - 高优先级

module = AffectedModule(
    module_id='mod-001',
    module_name='支付网关',
    action='create',
    after_version='v1.0.0'
)
```

## 数据库迁移说明

新增字段已添加到 `PlanModel`，需要执行数据库迁移：

```sql
-- SQLite 示例
ALTER TABLE plans ADD COLUMN affected_modules JSON DEFAULT '[]';
ALTER TABLE plans ADD COLUMN approval_files_detail JSON DEFAULT '[]';
ALTER TABLE plans ADD COLUMN template_type VARCHAR(50) DEFAULT 'new_feature';
ALTER TABLE plans ADD COLUMN related_inventory_ids JSON DEFAULT '[]';
```

---

**更新日期**: 2026-03-30
**模块版本**: v3.0 (优化版)
