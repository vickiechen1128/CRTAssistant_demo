# 仿真运维经理 - 数据模型设计

| 版本 | 日期 | 作者 | 变更说明 |
|-----|------|-----|---------|
| v1.0 | 2024-03-24 | CRT | 重构：根据PRD v1.2更新，完善台账管理模块 |
| v0.8 | 2024-03-22 | CRT | 新增：计划管理模块数据模型 |
| v0.1 | 2024-03-20 | CRT | 初稿，核心实体定义 |

## 1. 计划管理模块

### 1.1 计划表 (plans)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| plan_id | VARCHAR(50) | NOT NULL | 计划唯一标识 |
| name | VARCHAR(200) | NOT NULL | 计划名称 |
| category | ENUM | NOT NULL | new_system/new_feature/business_change/db_change |
| priority | ENUM | NOT NULL | P0/P1/P2/P3 |
| status | ENUM | NOT NULL | DRAFT/PENDING/IN_PROGRESS/COMPLETED |
| scope_type | ENUM | | new_app/edit_app/select_app |
| related_inventory_ids | JSON | | 关联的台账ID列表 |
| tag | VARCHAR(100) | NOT NULL | 数据标签 |
| created_at | DATETIME | | 创建时间 |
| updated_at | DATETIME | | 更新时间 |

## 2. 台账管理模块

### 2.1 应用系统台账表

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| app_name | VARCHAR(100) | NOT NULL | 应用名称 |
| app_description | TEXT | | 应用情况说明 |
| function_modules | JSON | | 功能模块列表（含上线时间）|
| hostname | VARCHAR(100) | | 主机名 |
| app_url | VARCHAR(500) | | 应用地址URL |
| business_owner | VARCHAR(50) | NOT NULL | 业务负责人 |
| project_owner | VARCHAR(50) | NOT NULL | 项目负责人 |
| launch_time | DATETIME | | 系统上线时间 |
| status | ENUM | NOT NULL | active/inactive/archived |
| related_plan_ids | JSON | | 关联的计划ID列表 |
| created_at | DATETIME | | 创建时间 |
| updated_at | DATETIME | | 更新时间 |

### 2.2 云服务资源台账表

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| app_id | VARCHAR(36) | FK | 关联应用系统ID |
| resource_type | ENUM | NOT NULL | compute/network/storage/backup/middleware/database/cache/message_queue |
| resource_name | VARCHAR(100) | NOT NULL | 资源名称 |
| configuration | JSON | | 配置详情 |
| related_plan_ids | JSON | | 关联的计划ID列表 |
| created_at | DATETIME | | 创建时间 |
| updated_at | DATETIME | | 更新时间 |

### 2.3 系统及软件账号台账表

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| app_id | VARCHAR(36) | FK | 关联应用系统ID |
| account_type | ENUM | NOT NULL | system/software |
| account_name | VARCHAR(100) | NOT NULL | 账户名 |
| permission_level | ENUM | NOT NULL | admin/read/write/execute |
| holder_name | VARCHAR(50) | NOT NULL | 持有人姓名 |
| valid_from | DATETIME | NOT NULL | 有效期开始 |
| valid_until | DATETIME | NOT NULL | 有效期结束 |
| password_change_cycle | INT | | 密码修改周期(天) |
| status | ENUM | NOT NULL | active/expired/locked |
| related_plan_ids | JSON | | 关联的计划ID列表 |
| created_at | DATETIME | | 创建时间 |
| updated_at | DATETIME | | 更新时间 |

## 3. 台账与计划关联关系

所有台账表均包含 related_plan_ids JSON字段，用于维护与计划的多对多关系。

PlanID格式：PLAN-YYYYMMDD-XXX

---

**本文档根据PRD v1.2更新**
