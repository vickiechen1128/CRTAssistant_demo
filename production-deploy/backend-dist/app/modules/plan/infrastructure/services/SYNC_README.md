# 计划管理与台账管理数据同步机制

## 概述

本模块实现了计划管理（Plan）和台账管理（Inventory）之间的双向数据同步机制，确保两个模块的数据一致性。

## 同步策略

采用**混合同步模式**：

1. **事件驱动实时同步** - 当计划或台账状态变更时，立即触发同步
2. **定时补偿同步** - 每小时检查一次数据一致性，修复不一致数据

## 核心组件

### 1. DataSyncService (数据同步服务)

位置：`data_sync_service.py`

功能：
- 计划 → 台账同步：计划启动、完成、取消时同步到台账
- 台账 → 计划同步：台账状态变更时同步到计划
- 一致性检查：检查计划与台账的数据一致性
- 数据修复：修复不一致的数据
- 同步日志：记录所有同步操作

主要方法：
- `sync_plan_started()` - 计划启动时的台账同步
- `sync_plan_completed()` - 计划完成时的台账同步
- `sync_plan_cancelled()` - 计划取消时的台账同步
- `sync_inventory_status_changed()` - 台账状态变更时的计划同步
- `check_consistency()` - 检查数据一致性
- `repair_inconsistency()` - 修复数据不一致

### 2. SyncScheduler (同步调度器)

位置：`sync_scheduler.py`

功能：
- 管理定时同步任务
- 每小时执行一致性检查
- 每天清理过期日志

使用方式：
```python
from app.modules.plan.infrastructure.services.sync_scheduler import get_scheduler

# 在应用启动时
scheduler = get_scheduler(db_session)
await scheduler.start()

# 在应用关闭时
await scheduler.stop()
```

### 3. 事件处理器

位置：`event_handlers/sync_event_handlers.py`

功能：
- 监听领域事件并触发同步
- PlanSyncEventHandler - 处理计划相关事件
- InventorySyncEventHandler - 处理台账相关事件

### 4. API 接口

位置：`interfaces/api/routes/sync_routes.py`

提供的接口：
- `GET /sync/logs` - 获取同步日志
- `GET /sync/statistics` - 获取同步统计
- `GET /sync/consistency-check` - 执行一致性检查
- `POST /sync/repair/{plan_id}` - 修复指定计划的数据不一致

## 同步场景

### 场景1：计划启动

**触发条件**：计划状态从 DRAFT/PENDING → IN_PROGRESS

**同步操作**：
- 标记关联台账为"计划中"
- 在台账中记录计划关联信息

### 场景2：计划完成

**触发条件**：计划状态从 IN_PROGRESS → COMPLETED

**同步操作**（根据计划分类）：

| 计划分类 | 台账操作 |
|---------|---------|
| new_system | 创建应用系统 + 功能模块 |
| new_feature | 创建功能模块 |
| func_change | 更新功能模块版本/状态 |
| arch_change | 更新应用系统架构信息 |
| security_check | 仅记录检查日志 |

### 场景3：计划取消

**触发条件**：计划状态从 IN_PROGRESS → CANCELLED

**同步操作**：
- 在台账中记录计划取消
- 移除"计划中"标记

### 场景4：台账状态变更

**触发条件**：台账状态发生变更

**同步操作**：
- 检查关联的计划
- 如果计划正在进行中，发送提醒

## 数据一致性检查

检查项：
1. 计划已完成但台账未创建
2. 计划已完成但台账状态不匹配
3. 计划进行中但台账已停用
4. 计划已取消但台账仍标记为"计划中"

## 同步日志

每条同步记录包含：
- 同步类型（plan_to_inventory / inventory_to_plan / repair）
- 源ID和目标ID
- 操作类型
- 状态（pending / success / failed / partial）
- 详细信息
- 错误信息（如果有）
- 创建时间

## 使用示例

### 在计划完成服务中集成同步

```python
from app.modules.plan.infrastructure.services.data_sync_service import DataSyncService

class PlanCompletionService:
    def __init__(self, inventory_service, lifecycle_service, data_sync_service=None):
        self._inventory_service = inventory_service
        self._lifecycle_service = lifecycle_service
        self._data_sync_service = data_sync_service

    def complete_plan(self, plan, completed_by):
        # 执行台账操作
        result = self._inventory_service.create_application(...)

        # 执行数据同步
        if self._data_sync_service:
            sync_result = self._data_sync_service.sync_plan_completed(
                plan_id=plan.id,
                plan_name=plan.name,
                category=plan.category.value,
                inventory_ids=[result.inventory_id],
                affected_modules=[...],
                completed_by=completed_by
            )

        return CompletionResult(..., sync_log_id=sync_result.id)
```

### 手动触发一致性检查

```python
from app.modules.plan.infrastructure.services.data_sync_service import DataSyncService

sync_service = DataSyncService(db_session)

# 检查所有计划
result = sync_service.check_consistency()
print(f"发现 {result['inconsistent_count']} 处不一致")

# 检查指定计划
result = sync_service.check_consistency(plan_id="PLAN-001")

# 修复不一致
if result['inconsistent_count'] > 0:
    repair_result = sync_service.repair_inconsistency("PLAN-001")
```

## 注意事项

1. 同步操作是异步执行的，不会阻塞主流程
2. 同步失败会记录日志，不会导致计划操作失败
3. 定时任务需要在应用启动时手动启动
4. 生产环境建议将同步日志持久化到数据库
