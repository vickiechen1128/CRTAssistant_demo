# 赛领OpsPilot管理平台 - 数据模型设计

| 版本 | 日期 | 作者 | 变更说明 |
|-----|------|-----|---------|
| v1.1 | 2024-03-25 | CRT | 重构：根据PRD v1.3更新，新增SOP模板、工作项审核等级、审核矩阵、角色权限等数据模型 |
| v1.0 | 2024-03-24 | CRT | 重构：根据PRD v1.2更新，完善台账管理模块 |
| v0.8 | 2024-03-22 | CRT | 新增：计划管理模块数据模型 |
| v0.1 | 2024-03-20 | CRT | 初稿，核心实体定义 |

---

## 1. 计划管理模块

### 1.1 计划表 (plans)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| plan_id | VARCHAR(50) | NOT NULL, UNIQUE | 计划唯一标识，格式：PLAN-YYYYMMDD-XXX |
| name | VARCHAR(200) | NOT NULL | 计划名称 |
| category | ENUM | NOT NULL | 计划分类：new_system/new_feature/business_change/db_change |
| priority | ENUM | NOT NULL | P0/P1/P2/P3 |
| status | ENUM | NOT NULL | DRAFT/PENDING/IN_PROGRESS/COMPLETED/CANCELLED |
| scope_type | ENUM | | new_app/edit_app/select_app/select_app_cloud |
| related_inventory_ids | JSON | | 关联的台账ID列表 |
| tag | VARCHAR(100) | | 数据标签 |
| sop_template_id | VARCHAR(36) | FK | 关联的SOP模板ID |
| audit_matrix_config_id | VARCHAR(36) | FK | 关联的审核矩阵配置ID |
| created_by | VARCHAR(36) | NOT NULL | 创建人ID（甲方运维经理） |
| planned_start_time | DATETIME | NOT NULL | 计划执行时间 |
| planned_end_time | DATETIME | | 计划结束时间（预估） |
| actual_start_time | DATETIME | | 实际开始时间 |
| actual_end_time | DATETIME | | 实际结束时间 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

---

## 2. 台账管理模块

### 2.1 应用系统台账表 (inventory_applications)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| app_name | VARCHAR(100) | NOT NULL | 应用名称 |
| app_description | TEXT | | 应用情况说明 |
| function_modules | JSON | | 功能模块列表（含module_name, launch_time）|
| hostname | VARCHAR(100) | | 主机名 |
| app_url | VARCHAR(500) | | 应用地址URL |
| business_owner | VARCHAR(50) | NOT NULL | 业务负责人 |
| project_owner | VARCHAR(50) | NOT NULL | 项目负责人 |
| launch_time | DATETIME | | 系统上线时间 |
| status | ENUM | NOT NULL | active/inactive/archived |
| related_plan_ids | JSON | | 关联的计划ID列表 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 2.2 云服务资源台账表 (inventory_cloud_resources)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| app_id | VARCHAR(36) | FK | 关联应用系统ID |
| resource_type | ENUM | NOT NULL | compute/network/storage/backup/middleware/database/cache/message_queue |
| resource_name | VARCHAR(100) | NOT NULL | 资源名称 |
| configuration | JSON | | 配置详情 |
| related_plan_ids | JSON | | 关联的计划ID列表 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 2.3 系统及软件账号台账表 (inventory_accounts)

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
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

---

## 3. SOP模板引擎模块

### 3.1 SOP模板表 (sop_templates)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| template_id | VARCHAR(50) | NOT NULL, UNIQUE | 模板唯一标识 |
| template_name | VARCHAR(100) | NOT NULL | 模板名称 |
| category | ENUM | NOT NULL | 模板分类：new_system/new_feature/business_change/db_change |
| description | TEXT | | 模板描述 |
| version | VARCHAR(20) | NOT NULL | 模板版本 |
| status | ENUM | NOT NULL | active/inactive/deprecated |
| created_by | VARCHAR(36) | NOT NULL | 创建人ID（甲方运维专家） |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 3.2 工作项模板表 (work_item_templates)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| template_id | VARCHAR(50) | NOT NULL, UNIQUE | 工作项模板唯一标识 |
| sop_template_id | VARCHAR(36) | FK | 关联SOP模板ID |
| parent_template_id | VARCHAR(36) | FK | 父工作项模板ID（为空表示父工作项） |
| template_name | VARCHAR(100) | NOT NULL | 工作项模板名称 |
| category | ENUM | NOT NULL | 工作项分类：inventory/base_resource/security/permission/monitoring |
| sequence | INT | NOT NULL | 执行顺序 |
| audit_level | ENUM | NOT NULL | 审核等级：normal/critical |
| description | TEXT | | 工作项描述 |
| deliverables_config | JSON | NOT NULL | 交付物要求配置 [{name, format[], required, description}] |
| acceptance_criteria_config | JSON | | 验收标准配置 [{criterion_id, description, verification_method}] |
| execution_steps_config | JSON | | 执行步骤配置 [{step_id, sequence, name, description, responsible_role, estimated_hours}] |
| status | ENUM | NOT NULL | active/inactive |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 3.3 流程节点配置表 (workflow_nodes)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| sop_template_id | VARCHAR(36) | FK | 关联SOP模板ID |
| node_id | VARCHAR(50) | NOT NULL | 节点标识 |
| node_name | VARCHAR(100) | NOT NULL | 节点名称 |
| sequence | INT | NOT NULL | 节点顺序 |
| entry_conditions | JSON | | 准入条件 [{condition_type, condition_value}] |
| exit_conditions | JSON | | 准出条件 [{condition_type, condition_value}] |
| work_item_template_ids | JSON | NOT NULL | 关联的工作项模板ID列表 |
| audit_level | ENUM | | 节点审核等级：normal/critical |
| mandatory_rules | JSON | | 强制规则配置 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

---

## 4. 工作项管理模块

### 4.1 工作项表 (work_items)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| work_item_id | VARCHAR(50) | NOT NULL, UNIQUE | 工作项唯一标识 |
| plan_id | VARCHAR(36) | FK | 关联计划ID |
| parent_work_item_id | VARCHAR(36) | FK | 父工作项ID（为空表示父工作项） |
| template_id | VARCHAR(36) | FK | 关联的工作项模板ID |
| name | VARCHAR(100) | NOT NULL | 工作项名称 |
| category | ENUM | NOT NULL | 工作项分类：inventory/base_resource/security/permission/monitoring |
| sequence | INT | NOT NULL | 执行顺序 |
| audit_level | ENUM | NOT NULL | 审核等级：normal/critical |
| status | ENUM | NOT NULL | pending/in_progress/completed/rejected |
| assigned_to | VARCHAR(36) | | 分配给乙方团队ID |
| description | TEXT | | 工作项描述 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |
| started_at | DATETIME | | 实际开始时间 |
| completed_at | DATETIME | | 实际完成时间 |

### 4.2 交付物表 (deliverables)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| deliverable_id | VARCHAR(50) | NOT NULL, UNIQUE | 交付物唯一标识 |
| work_item_id | VARCHAR(36) | FK | 关联工作项ID |
| name | VARCHAR(100) | NOT NULL | 交付物名称 |
| description | TEXT | | 交付物描述 |
| required_formats | JSON | NOT NULL | 要求的格式 [PDF, Word, Excel, etc.] |
| uploaded_by | VARCHAR(36) | | 上传人ID |
| file_path | VARCHAR(500) | | 文件存储路径 |
| file_size | BIGINT | | 文件大小(字节) |
| version | INT | NOT NULL, DEFAULT 1 | 版本号 |
| status | ENUM | NOT NULL | pending/uploaded/under_review/passed/rejected |
| uploaded_at | DATETIME | | 上传时间 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 4.3 验收标准表 (acceptance_criteria)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| criterion_id | VARCHAR(50) | NOT NULL, UNIQUE | 验收标准唯一标识 |
| work_item_id | VARCHAR(36) | FK | 关联工作项ID |
| description | TEXT | NOT NULL | 验收标准描述 |
| verification_method | ENUM | NOT NULL | manual/script/ai |
| script_id | VARCHAR(36) | FK | 关联的脚本ID（verification_method为script时） |
| ai_config | JSON | | AI分析配置（verification_method为ai时） |
| pass_criteria | TEXT | | 通过标准描述 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 4.4 核验结论表 (verification_results)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| result_id | VARCHAR(50) | NOT NULL, UNIQUE | 核验结论唯一标识 |
| deliverable_id | VARCHAR(36) | FK | 关联交付物ID |
| criterion_id | VARCHAR(36) | FK | 关联验收标准ID |
| conclusion | ENUM | NOT NULL | passed/failed/pending_improvement |
| verification_method | ENUM | NOT NULL | manual/script/ai |
| verified_by | VARCHAR(36) | | 核验人ID |
| verification_data | JSON | | 核验数据（脚本输出/AI分析结果） |
| comments | TEXT | | 核验意见 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 4.5 执行步骤表 (execution_steps)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| step_id | VARCHAR(50) | NOT NULL | 步骤标识 |
| work_item_id | VARCHAR(36) | FK | 关联工作项ID |
| sequence | INT | NOT NULL | 步骤顺序 |
| name | VARCHAR(100) | NOT NULL | 步骤名称 |
| description | TEXT | | 步骤描述 |
| responsible_role | VARCHAR(50) | | 负责角色 |
| assigned_to | VARCHAR(36) | | 分配给的用户ID |
| estimated_hours | INT | | 预计工时 |
| actual_hours | INT | | 实际工时 |
| status | ENUM | NOT NULL | pending/in_progress/completed |
| started_at | DATETIME | | 开始时间 |
| completed_at | DATETIME | | 完成时间 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

---

## 5. 审核矩阵模块

### 5.1 审核矩阵配置表 (audit_matrix_configs)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| config_id | VARCHAR(50) | NOT NULL, UNIQUE | 配置唯一标识 |
| config_name | VARCHAR(100) | NOT NULL | 配置名称 |
| description | TEXT | | 配置描述 |
| created_by | VARCHAR(36) | NOT NULL | 创建人ID（甲方运维专家） |
| status | ENUM | NOT NULL | active/inactive |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 5.2 审核规则表 (audit_rules)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| config_id | VARCHAR(36) | FK | 关联审核矩阵配置ID |
| audit_level | ENUM | NOT NULL | 审核等级：normal/critical |
| primary_audit_method | ENUM | NOT NULL | 主要审核方式：self_review/script_auto/expert_manual |
| secondary_audit_method | ENUM | | 辅助审核方式：self_review/script_auto/ai_assist/expert_manual |
| sampling_ratio | DECIMAL(3,2) | | 抽检比例（0-1之间，普通项适用） |
| auto_pass_threshold | DECIMAL(5,2) | | 自动通过阈值（脚本置信度，如95.00） |
| mandatory_reviewer_role | VARCHAR(50) | | 强制审核人角色（关键项适用） |
| escalation_rule | TEXT | | 升级规则描述 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

---

## 6. 用户权限模块

### 6.1 用户表 (users)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| user_id | VARCHAR(50) | NOT NULL, UNIQUE | 用户唯一标识 |
| username | VARCHAR(50) | NOT NULL, UNIQUE | 用户名 |
| email | VARCHAR(100) | NOT NULL | 邮箱 |
| phone | VARCHAR(20) | | 手机号 |
| real_name | VARCHAR(50) | NOT NULL | 真实姓名 |
| organization | VARCHAR(100) | | 所属组织/公司 |
| status | ENUM | NOT NULL | active/inactive/locked |
| last_login_at | DATETIME | | 最后登录时间 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 6.2 角色表 (roles)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| role_code | VARCHAR(50) | NOT NULL, UNIQUE | 角色编码：ops_manager/ops_expert/vendor_team |
| role_name | VARCHAR(50) | NOT NULL | 角色名称 |
| description | TEXT | | 角色描述 |
| data_scope | ENUM | NOT NULL | 数据范围：all/assigned/own |
| status | ENUM | NOT NULL | active/inactive |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 6.3 用户角色关联表 (user_roles)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| user_id | VARCHAR(36) | FK | 用户ID |
| role_id | VARCHAR(36) | FK | 角色ID |
| assigned_by | VARCHAR(36) | | 分配人ID |
| assigned_at | DATETIME | | 分配时间 |
| created_at | DATETIME | NOT NULL | 创建时间 |

### 6.4 权限表 (permissions)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| permission_code | VARCHAR(100) | NOT NULL, UNIQUE | 权限编码 |
| permission_name | VARCHAR(100) | NOT NULL | 权限名称 |
| resource_type | VARCHAR(50) | NOT NULL | 资源类型：plan/work_item/sop_template/inventory/etc. |
| operation | VARCHAR(50) | NOT NULL | 操作类型：create/read/update/delete/audit/etc. |
| description | TEXT | | 权限描述 |
| created_at | DATETIME | NOT NULL | 创建时间 |

### 6.5 角色权限关联表 (role_permissions)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| role_id | VARCHAR(36) | FK | 角色ID |
| permission_id | VARCHAR(36) | FK | 权限ID |
| created_at | DATETIME | NOT NULL | 创建时间 |

---

## 7. 审计日志模块

### 7.1 操作审计日志表 (audit_logs)

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|-----|------|
| id | VARCHAR(36) | PK | 主键 |
| log_id | VARCHAR(50) | NOT NULL, UNIQUE | 日志唯一标识 |
| operation_type | ENUM | NOT NULL | 操作类型：plan/work_item/deliverable/sop_template/permission/etc. |
| operation_action | VARCHAR(50) | NOT NULL | 操作动作：create/update/delete/audit/upload/etc. |
| operator_id | VARCHAR(36) | NOT NULL | 操作人ID |
| operator_role | VARCHAR(50) | NOT NULL | 操作人角色 |
| target_id | VARCHAR(36) | | 操作目标ID |
| target_type | VARCHAR(50) | | 操作目标类型 |
| old_value | JSON | | 变更前数据 |
| new_value | JSON | | 变更后数据 |
| operation_result | ENUM | NOT NULL | success/failure |
| error_message | TEXT | | 错误信息 |
| ip_address | VARCHAR(50) | | 操作IP地址 |
| user_agent | VARCHAR(500) | | 用户代理信息 |
| created_at | DATETIME | NOT NULL | 创建时间 |

---

## 8. 实体关系图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         赛领OpsPilot管理平台 - 数据模型ER图                      │
└─────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
    │    users     │◄───────►│  user_roles  │◄───────►│    roles     │
    └──────────────┘         └──────────────┘         └──────┬───────┘
                                                              │
                                                              ▼
                                                    ┌──────────────┐
                                                    │role_permissions│
                                                    └──────┬───────┘
                                                           ▼
                                                   ┌──────────────┐
                                                   │  permissions │
                                                   └──────────────┘

    ┌──────────────┐         ┌──────────────┐         ┌──────────────────┐
    │    plans     │◄───────►│  work_items  │◄───────►│  deliverables    │
    └──────┬───────┘         └──────┬───────┘         └──────────────────┘
           │                        │
           │                        ▼
           │               ┌──────────────────┐
           │               │acceptance_criteria│
           │               └────────┬─────────┘
           │                        │
           │                        ▼
           │               ┌──────────────────┐
           │               │verification_results│
           │               └──────────────────┘
           │
           ▼
    ┌──────────────────┐
    │sop_templates     │◄──────┐
    └──────┬───────────┘       │
           │                   │
           ▼                   │
    ┌──────────────────┐       │
    │work_item_templates│       │
    └──────────────────┘       │
                               │
           ┌───────────────────┘
           ▼
    ┌──────────────────┐
    │  workflow_nodes  │
    └──────────────────┘

    ┌──────────────────────┐
    │audit_matrix_configs  │◄──────┐
    └──────────┬───────────┘       │
               │                   │
               ▼                   │
        ┌──────────────┐           │
        │  audit_rules │◄──────────┘
        └──────────────┘

    ┌─────────────────────────────┐
    │      inventory_applications │
    └─────────────────────────────┘

    ┌─────────────────────────────┐
    │   inventory_cloud_resources │
    └─────────────────────────────┘

    ┌─────────────────────────────┐
    │     inventory_accounts      │
    └─────────────────────────────┘

    ┌─────────────────────────────┐
    │        audit_logs           │
    └─────────────────────────────┘
```

---

**本文档根据PRD v1.3更新**

主要变更包括：
1. 新增SOP模板引擎相关表：sop_templates, work_item_templates, workflow_nodes
2. 新增工作项审核等级字段：work_items.audit_level
3. 新增审核矩阵相关表：audit_matrix_configs, audit_rules
4. 新增用户权限相关表：users, roles, user_roles, permissions, role_permissions
5. 新增审计日志表：audit_logs
6. 新增执行步骤表：execution_steps
7. 更新计划表字段：增加sop_template_id, audit_matrix_config_id等字段
