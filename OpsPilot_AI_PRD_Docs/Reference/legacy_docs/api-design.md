# 赛领OpsPilot管理平台 - API 设计文档

| 版本 | 日期 | 作者 | 变更说明 |
|-----|------|-----|---------|
| v1.2 | 2024-03-25 | CRT | 重构：根据PRD v1.3更新，新增SOP模板引擎API、审核矩阵API、角色权限API、审计日志API |
| v1.1 | 2024-03-24 | CRT | 重构：根据PRD v1.2更新，新增台账管理模块API，更新计划分类枚举值 |
| v1.0 | 2024-03-22 | CRT | 重构：按照五大业务阶段重新组织API |
| v0.1 | 2024-03-20 | CRT | 初稿，核心API定义 |

---

## 1. 接口概览

### 1.1 计划分类枚举值

| 枚举值 | 说明 | 范围选择方式 | 自动生成工作项 |
|-------|------|-------------|---------------|
| new_system | 新系统上线 | 创建新台账 | 补充应用系统台账 |
| new_feature | 新功能发布 | 查询+编辑 | 补充新增的功能模块 |
| business_change | 业务功能变更 | 查询+勾选 | 更新应用系统台账 |
| db_change | 数据库变更 | 查询+勾选 | 更新数据库相关台账 |

### 1.2 角色编码

| 角色编码 | 角色名称 | 说明 |
|---------|---------|------|
| ops_manager | 甲方运维经理 | 计划管理、工作项审核（关键项）、外包质量管理 |
| ops_expert | 甲方运维专家 | SOP模板管理、验收标准维护、关键交付物审核 |
| vendor_team | 乙方外部服务团队 | 任务执行、交付物上传、进度更新 |

### 1.3 审核等级

| 审核等级 | 说明 | 审核方式 |
|---------|------|---------|
| normal | 普通项 | 乙方自审/脚本自动核验/甲方抽检 |
| critical | 关键项 | 强制甲方专家人工审核 |

---

## 2. 计划管理API

### 2.1 计划CRUD接口

#### GET /api/plans
获取计划列表

**Query参数**:
| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| category | string | 否 | 计划分类筛选 |
| status | string | 否 | 状态筛选 |
| priority | string | 否 | 优先级筛选 |
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页大小，默认20 |

**响应成功**:
```json
{
  "code": 200,
  "data": {
    "total": 100,
    "page": 1,
    "size": 20,
    "items": [
      {
        "id": "plan-001",
        "plan_id": "PLAN-20240325-001",
        "name": "XX系统上线计划",
        "category": "new_system",
        "priority": "P0",
        "status": "IN_PROGRESS",
        "planned_start_time": "2024-03-30T09:00:00Z",
        "progress": 45,
        "created_by": "user-001",
        "created_at": "2024-03-25T10:00:00Z"
      }
    ]
  }
}
```

#### POST /api/plans
创建计划

**请求体**:
```json
{
  "name": "XX系统上线计划",
  "category": "new_system",
  "priority": "P0",
  "planned_start_time": "2024-03-30T09:00:00Z",
  "planned_end_time": "2024-04-05T18:00:00Z",
  "tag": "核心业务系统",
  "sop_template_id": "sop-001"
}
```

**响应成功**:
```json
{
  "code": 200,
  "data": {
    "id": "plan-001",
    "plan_id": "PLAN-20240325-001",
    "name": "XX系统上线计划",
    "category": "new_system",
    "priority": "P0",
    "status": "DRAFT",
    "sop_template_id": "sop-001",
    "created_at": "2024-03-25T10:00:00Z"
  }
}
```

#### GET /api/plans/{id}
获取计划详情

**响应成功**:
```json
{
  "code": 200,
  "data": {
    "id": "plan-001",
    "plan_id": "PLAN-20240325-001",
    "name": "XX系统上线计划",
    "category": "new_system",
    "priority": "P0",
    "status": "IN_PROGRESS",
    "scope_type": "new_app",
    "scope_description": "新建XX业务系统",
    "related_inventory_ids": ["app-001"],
    "sop_template_id": "sop-001",
    "audit_matrix_config_id": "audit-001",
    "planned_start_time": "2024-03-30T09:00:00Z",
    "planned_end_time": "2024-04-05T18:00:00Z",
    "actual_start_time": "2024-03-30T09:00:00Z",
    "progress": 45,
    "work_items": [
      {
        "id": "wi-001",
        "name": "补充应用系统台账",
        "category": "inventory",
        "audit_level": "critical",
        "status": "completed",
        "sequence": 1
      }
    ]
  }
}
```

#### PUT /api/plans/{id}
更新计划

#### DELETE /api/plans/{id}
删除计划

### 2.2 范围选择接口

#### POST /api/plans/{id}/scope
选择涉及范围，系统自动生成第一个工作项

**请求体根据计划分类不同而变化**：

**新系统上线 (new_system)**:
```json
{
  "scope_type": "new_app",
  "application": {
    "app_name": "XX业务系统",
    "app_description": "核心业务系统",
    "business_owner": "张三",
    "project_owner": "李四"
  }
}
```

**新功能发布 (new_feature)**:
```json
{
  "scope_type": "edit_app",
  "application_id": "app-001",
  "function_modules": [
    {
      "module_name": "订单管理模块",
      "launch_time": "2024-03-30T00:00:00Z"
    }
  ]
}
```

**业务功能变更 (business_change)**:
```json
{
  "scope_type": "select_app",
  "application_ids": ["app-001", "app-002"]
}
```

**数据库变更 (db_change)**:
```json
{
  "scope_type": "select_app_cloud",
  "application_ids": ["app-001"],
  "cloud_resource_ids": ["cloud-001", "cloud-002"]
}
```

**响应成功**:
```json
{
  "code": 200,
  "data": {
    "scope_type": "new_app",
    "related_inventory_ids": ["app-001"],
    "auto_generated_work_item": {
      "id": "wi-001",
      "name": "补充应用系统台账",
      "category": "inventory",
      "audit_level": "critical",
      "status": "pending",
      "sequence": 1
    }
  }
}
```

### 2.3 计划状态流转接口

#### POST /api/plans/{id}/start
启动计划（草稿→执行中）

#### POST /api/plans/{id}/complete
完成计划

---

## 3. 工作项管理API

### 3.1 工作项CRUD接口

#### GET /api/plans/{plan_id}/work-items
获取计划下的工作项列表

**Query参数**:
| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| status | string | 否 | 状态筛选 |
| audit_level | string | 否 | 审核等级筛选 |
| assigned_to | string | 否 | 分配给指定团队 |

#### POST /api/plans/{plan_id}/work-items
创建工作项

**请求体**:
```json
{
  "name": "部署方案文档",
  "category": "base_resource",
  "audit_level": "critical",
  "parent_work_item_id": "wi-parent-001",
  "sequence": 2,
  "description": "编写系统部署方案文档",
  "assigned_to": "vendor-team-001",
  "template_id": "wit-001"
}
```

#### GET /api/work-items/{id}
获取工作项详情

**响应成功**:
```json
{
  "code": 200,
  "data": {
    "id": "wi-001",
    "work_item_id": "WI-20240325-001",
    "plan_id": "plan-001",
    "parent_work_item_id": null,
    "name": "部署方案文档",
    "category": "base_resource",
    "audit_level": "critical",
    "status": "in_progress",
    "sequence": 2,
    "assigned_to": "vendor-team-001",
    "description": "编写系统部署方案文档",
    "deliverables": [
      {
        "id": "del-001",
        "name": "部署方案文档",
        "status": "uploaded",
        "version": 1
      }
    ],
    "acceptance_criteria": [
      {
        "id": "ac-001",
        "description": "包含回滚方案",
        "verification_method": "manual"
      }
    ],
    "execution_steps": [
      {
        "id": "step-001",
        "name": "需求分析",
        "status": "completed",
        "actual_hours": 4
      }
    ],
    "started_at": "2024-03-25T10:00:00Z",
    "created_at": "2024-03-25T09:00:00Z"
  }
}
```

#### PUT /api/work-items/{id}
更新工作项

#### DELETE /api/work-items/{id}
删除工作项

### 3.2 工作项分配接口

#### POST /api/work-items/{id}/assign
分配工作项给乙方团队

**请求体**:
```json
{
  "assigned_to": "vendor-team-001",
  "assigned_by": "user-001",
  "comments": "请在3个工作日内完成"
}
```

### 3.3 工作项状态流转接口

#### POST /api/work-items/{id}/start
开始执行工作项

#### POST /api/work-items/{id}/complete
完成工作项

#### POST /api/work-items/{id}/reject
驳回工作项

**请求体**:
```json
{
  "reason": "交付物不符合要求，缺少回滚方案",
  "rejected_by": "user-001"
}
```

---

## 4. 交付物管理API

### 4.1 交付物CRUD接口

#### GET /api/work-items/{work_item_id}/deliverables
获取工作项的交付物列表

#### POST /api/work-items/{work_item_id}/deliverables
创建交付物要求（甲方配置）

**请求体**:
```json
{
  "name": "部署方案文档",
  "description": "包含系统架构、部署步骤、回滚方案",
  "required_formats": ["PDF", "Word"]
}
```

#### POST /api/deliverables/{id}/upload
上传交付物文件

**请求体**: multipart/form-data
```
file: [二进制文件]
version: 1
comments: "第一版部署方案"
```

**响应成功**:
```json
{
  "code": 200,
  "data": {
    "id": "del-001",
    "name": "部署方案文档",
    "file_path": "/uploads/2024/03/deploy-plan-v1.pdf",
    "file_size": 2048000,
    "version": 1,
    "status": "uploaded",
    "uploaded_by": "user-vendor-001",
    "uploaded_at": "2024-03-25T14:00:00Z"
  }
}
```

### 4.2 交付物版本管理

#### GET /api/deliverables/{id}/versions
获取交付物版本历史

---

## 5. 核验审核API

### 5.1 验收标准管理

#### GET /api/work-items/{work_item_id}/acceptance-criteria
获取验收标准列表

#### POST /api/work-items/{work_item_id}/acceptance-criteria
创建验收标准

**请求体**:
```json
{
  "description": "包含回滚方案",
  "verification_method": "manual",
  "pass_criteria": "文档中包含完整的回滚步骤"
}
```

### 5.2 核验执行

#### POST /api/deliverables/{id}/verify
执行核验

**请求体**:
```json
{
  "criterion_id": "ac-001",
  "conclusion": "passed",
  "verification_method": "manual",
  "comments": "文档完整，包含回滚方案",
  "verified_by": "user-001"
}
```

**响应成功**:
```json
{
  "code": 200,
  "data": {
    "result_id": "vr-001",
    "deliverable_id": "del-001",
    "criterion_id": "ac-001",
    "conclusion": "passed",
    "verification_method": "manual",
    "verified_by": "user-001",
    "comments": "文档完整，包含回滚方案",
    "created_at": "2024-03-25T15:00:00Z"
  }
}
```

#### POST /api/deliverables/{id}/verify/script
脚本自动核验

**请求体**:
```json
{
  "script_id": "script-001",
  "parameters": {
    "target_host": "192.168.1.100"
  }
}
```

#### POST /api/deliverables/{id}/verify/ai
AI智能分析核验

**请求体**:
```json
{
  "analysis_type": "document_review",
  "extract_fields": ["architecture", "deployment_steps", "rollback_plan"]
}
```

### 5.3 审核任务管理

#### GET /api/audit-tasks/pending
获取待审核任务列表

**Query参数**:
| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| audit_level | string | 否 | 审核等级筛选：normal/critical |
| role | string | 否 | 角色筛选：ops_manager/ops_expert |

**响应成功**:
```json
{
  "code": 200,
  "data": {
    "total": 10,
    "items": [
      {
        "work_item_id": "wi-001",
        "work_item_name": "部署方案文档",
        "audit_level": "critical",
        "plan_id": "plan-001",
        "plan_name": "XX系统上线计划",
        "deliverable_id": "del-001",
        "deliverable_name": "部署方案文档-v1.pdf",
        "uploaded_by": "vendor-team-001",
        "uploaded_at": "2024-03-25T14:00:00Z",
        "waiting_hours": 24
      }
    ]
  }
}
```

---

## 6. SOP模板引擎API

### 6.1 SOP模板管理

#### GET /api/sop-templates
获取SOP模板列表

**Query参数**:
| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| category | string | 否 | 模板分类筛选 |
| status | string | 否 | 状态筛选 |

**响应成功**:
```json
{
  "code": 200,
  "data": {
    "total": 5,
    "items": [
      {
        "id": "sop-001",
        "template_id": "SOP-NEW-SYSTEM-v1",
        "template_name": "新系统上线模板",
        "category": "new_system",
        "version": "1.0",
        "status": "active",
        "created_by": "user-expert-001",
        "created_at": "2024-03-20T10:00:00Z"
      }
    ]
  }
}
```

#### POST /api/sop-templates
创建SOP模板（甲方运维专家）

**请求体**:
```json
{
  "template_name": "新系统上线模板",
  "category": "new_system",
  "description": "适用于全新业务系统首次上线的标准流程",
  "version": "1.0"
}
```

#### GET /api/sop-templates/{id}
获取SOP模板详情

**响应成功**:
```json
{
  "code": 200,
  "data": {
    "id": "sop-001",
    "template_id": "SOP-NEW-SYSTEM-v1",
    "template_name": "新系统上线模板",
    "category": "new_system",
    "description": "适用于全新业务系统首次上线的标准流程",
    "version": "1.0",
    "status": "active",
    "work_item_templates": [
      {
        "id": "wit-001",
        "template_name": "补充应用系统台账",
        "category": "inventory",
        "audit_level": "critical",
        "sequence": 1
      },
      {
        "id": "wit-002",
        "template_name": "基础资源标准化交付",
        "category": "base_resource",
        "audit_level": "normal",
        "sequence": 2
      }
    ],
    "workflow_nodes": [
      {
        "id": "node-001",
        "node_name": "准备阶段",
        "sequence": 1,
        "audit_level": "critical"
      }
    ]
  }
}
```

#### PUT /api/sop-templates/{id}
更新SOP模板

#### DELETE /api/sop-templates/{id}
删除SOP模板

### 6.2 工作项模板管理

#### GET /api/sop-templates/{sop_id}/work-item-templates
获取工作项模板列表

#### POST /api/sop-templates/{sop_id}/work-item-templates
创建工作项模板

**请求体**:
```json
{
  "template_name": "部署方案文档",
  "category": "base_resource",
  "audit_level": "critical",
  "sequence": 2,
  "parent_template_id": "wit-parent-001",
  "description": "编写系统部署方案文档",
  "deliverables_config": [
    {
      "name": "部署方案文档",
      "format": ["PDF", "Word"],
      "required": true,
      "description": "包含系统架构、部署步骤、回滚方案"
    }
  ],
  "acceptance_criteria_config": [
    {
      "criterion_id": "ac-001",
      "description": "包含回滚方案",
      "verification_method": "manual"
    }
  ],
  "execution_steps_config": [
    {
      "step_id": "step-001",
      "sequence": 1,
      "name": "需求分析",
      "description": "理解系统架构和部署需求",
      "responsible_role": "乙方技术负责人",
      "estimated_hours": 4
    }
  ]
}
```

### 6.3 流程节点管理

#### GET /api/sop-templates/{sop_id}/workflow-nodes
获取流程节点列表

#### POST /api/sop-templates/{sop_id}/workflow-nodes
创建流程节点

**请求体**:
```json
{
  "node_name": "准备阶段",
  "sequence": 1,
  "entry_conditions": [],
  "exit_conditions": [
    {
      "condition_type": "deliverable_uploaded",
      "condition_value": "true"
    }
  ],
  "work_item_template_ids": ["wit-001"],
  "audit_level": "critical",
  "mandatory_rules": {
    "require_deliverable": true,
    "require_audit": true
  }
}
```

---

## 7. 审核矩阵API

### 7.1 审核矩阵配置管理

#### GET /api/audit-matrix-configs
获取审核矩阵配置列表

#### POST /api/audit-matrix-configs
创建审核矩阵配置（甲方运维专家）

**请求体**:
```json
{
  "config_name": "标准审核矩阵",
  "description": "适用于一般项目的审核规则配置"
}
```

#### GET /api/audit-matrix-configs/{id}
获取审核矩阵配置详情

**响应成功**:
```json
{
  "code": 200,
  "data": {
    "id": "audit-001",
    "config_id": "AUDIT-MATRIX-001",
    "config_name": "标准审核矩阵",
    "description": "适用于一般项目的审核规则配置",
    "created_by": "user-expert-001",
    "status": "active",
    "rules": [
      {
        "id": "rule-001",
        "audit_level": "normal",
        "primary_audit_method": "self_review",
        "secondary_audit_method": "script_auto",
        "sampling_ratio": 0.3,
        "auto_pass_threshold": 95.00
      },
      {
        "id": "rule-002",
        "audit_level": "critical",
        "primary_audit_method": "expert_manual",
        "secondary_audit_method": "ai_assist",
        "mandatory_reviewer_role": "ops_expert",
        "escalation_rule": "审核不通过时，自动通知乙方负责人重新提交"
      }
    ]
  }
}
```

### 7.2 审核规则管理

#### POST /api/audit-matrix-configs/{config_id}/rules
创建审核规则

**请求体**:
```json
{
  "audit_level": "normal",
  "primary_audit_method": "self_review",
  "secondary_audit_method": "script_auto",
  "sampling_ratio": 0.3,
  "auto_pass_threshold": 95.00
}
```

**关键项规则示例**:
```json
{
  "audit_level": "critical",
  "primary_audit_method": "expert_manual",
  "secondary_audit_method": "ai_assist",
  "mandatory_reviewer_role": "ops_expert",
  "escalation_rule": "审核不通过时，自动通知乙方负责人重新提交"
}
```

---

## 8. 台账管理API

### 8.1 应用系统台账接口

#### GET /api/inventories/applications
获取应用系统台账列表

**Query参数**:
| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| app_name | string | 否 | 应用名称搜索 |
| business_owner | string | 否 | 业务负责人筛选 |
| status | string | 否 | 状态筛选 |
| related_plan_id | string | 否 | 关联计划ID筛选 |

#### POST /api/inventories/applications
创建应用系统台账

**请求体**:
```json
{
  "app_name": "XX业务系统",
  "app_description": "核心业务系统",
  "function_modules": [
    {
      "module_name": "订单管理",
      "launch_time": "2024-03-30T00:00:00Z"
    }
  ],
  "hostname": "app-server-01",
  "app_url": "https://app.example.com",
  "business_owner": "张三",
  "project_owner": "李四",
  "launch_time": "2024-03-30T00:00:00Z"
}
```

#### GET /api/inventories/applications/{id}
获取应用系统台账详情

#### PUT /api/inventories/applications/{id}
更新应用系统台账

#### DELETE /api/inventories/applications/{id}
删除应用系统台账

### 8.2 云服务资源台账接口

#### GET /api/inventories/cloud-resources
获取云服务资源台账列表

**Query参数**:
| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| resource_type | string | 否 | 资源类型筛选：compute/network/storage/backup/middleware/database/cache/message_queue |
| app_id | string | 否 | 关联应用系统ID |

#### POST /api/inventories/cloud-resources
创建云服务资源台账

### 8.3 系统及软件账号台账接口

#### GET /api/inventories/accounts
获取账号台账列表

**Query参数**:
| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| account_type | string | 否 | 账号类型：system/software |
| app_id | string | 否 | 关联应用系统ID |
| status | string | 否 | 状态筛选 |

#### POST /api/inventories/accounts
创建账号台账

### 8.4 批量导入接口

#### POST /api/inventories/import
批量导入台账数据（Excel格式）

**请求体**: multipart/form-data
```
file: [Excel文件]
type: application  # 导入类型：application/cloud_resource/account
```

**响应成功**:
```json
{
  "code": 200,
  "data": {
    "total": 100,
    "success": 98,
    "failed": 2,
    "errors": [
      {
        "row": 5,
        "message": "应用名称不能为空"
      }
    ]
  }
}
```

---

## 9. 用户权限API

### 9.1 用户管理

#### GET /api/users
获取用户列表

#### POST /api/users
创建用户

**请求体**:
```json
{
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "phone": "13800138000",
  "real_name": "张三",
  "organization": "XX科技公司",
  "role_ids": ["role-001"]
}
```

#### GET /api/users/{id}
获取用户详情

#### PUT /api/users/{id}
更新用户信息

#### DELETE /api/users/{id}
删除用户

### 9.2 角色管理

#### GET /api/roles
获取角色列表

**响应成功**:
```json
{
  "code": 200,
  "data": [
    {
      "id": "role-001",
      "role_code": "ops_manager",
      "role_name": "甲方运维经理",
      "description": "计划管理、工作项审核（关键项）、外包质量管理",
      "data_scope": "all"
    },
    {
      "id": "role-002",
      "role_code": "ops_expert",
      "role_name": "甲方运维专家",
      "description": "SOP模板管理、验收标准维护、关键交付物审核",
      "data_scope": "all"
    },
    {
      "id": "role-003",
      "role_code": "vendor_team",
      "role_name": "乙方外部服务团队",
      "description": "任务执行、交付物上传、进度更新",
      "data_scope": "assigned"
    }
  ]
}
```

#### POST /api/roles
创建角色

#### POST /api/users/{user_id}/roles
分配角色给用户

**请求体**:
```json
{
  "role_id": "role-001",
  "assigned_by": "user-admin-001"
}
```

### 9.3 权限管理

#### GET /api/permissions
获取权限列表

#### POST /api/roles/{role_id}/permissions
分配权限给角色

**请求体**:
```json
{
  "permission_ids": ["perm-001", "perm-002"]
}
```

### 9.4 当前用户接口

#### GET /api/users/me
获取当前登录用户信息

**响应成功**:
```json
{
  "code": 200,
  "data": {
    "id": "user-001",
    "username": "zhangsan",
    "real_name": "张三",
    "email": "zhangsan@example.com",
    "roles": [
      {
        "role_code": "ops_manager",
        "role_name": "甲方运维经理"
      }
    ],
    "permissions": [
      "plan:create",
      "plan:read",
      "plan:update",
      "work_item:audit"
    ]
  }
}
```

#### GET /api/users/me/menus
获取当前用户的菜单权限

**响应成功**:
```json
{
  "code": 200,
  "data": {
    "menus": [
      {
        "name": "计划管理",
        "icon": "📋",
        "children": [
          {
            "name": "创建计划",
            "path": "/plans/create",
            "permission": "plan:create"
          },
          {
            "name": "计划列表",
            "path": "/plans",
            "permission": "plan:read"
          }
        ]
      }
    ]
  }
}
```

---

## 10. 审计日志API

### 10.1 操作日志查询

#### GET /api/audit-logs
获取操作审计日志

**Query参数**:
| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| operation_type | string | 否 | 操作类型筛选 |
| operator_id | string | 否 | 操作人ID筛选 |
| target_id | string | 否 | 目标ID筛选 |
| start_time | datetime | 否 | 开始时间 |
| end_time | datetime | 否 | 结束时间 |
| page | int | 否 | 页码 |
| size | int | 否 | 每页大小 |

**响应成功**:
```json
{
  "code": 200,
  "data": {
    "total": 1000,
    "page": 1,
    "size": 20,
    "items": [
      {
        "log_id": "LOG-20240325-001",
        "operation_type": "plan",
        "operation_action": "create",
        "operator_id": "user-001",
        "operator_role": "ops_manager",
        "target_id": "plan-001",
        "target_type": "plan",
        "new_value": {
          "name": "XX系统上线计划",
          "category": "new_system"
        },
        "operation_result": "success",
        "ip_address": "192.168.1.100",
        "created_at": "2024-03-25T10:00:00Z"
      }
    ]
  }
}
```

---

## 11. 统计报表API

### 11.1 外包质量统计

#### GET /api/statistics/vendor-quality
获取外包团队交付质量统计

**Query参数**:
| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| vendor_id | string | 否 | 乙方团队ID |
| start_time | datetime | 否 | 开始时间 |
| end_time | datetime | 否 | 结束时间 |

**响应成功**:
```json
{
  "code": 200,
  "data": {
    "vendor_id": "vendor-001",
    "vendor_name": "XX外包团队",
    "statistics": {
      "total_work_items": 100,
      "completed_work_items": 85,
      "pass_rate": 0.92,
      "average_audit_rounds": 1.5,
      "average_completion_hours": 48,
      "delay_rate": 0.08
    },
    "trend": [
      {
        "month": "2024-01",
        "pass_rate": 0.90,
        "delay_rate": 0.10
      },
      {
        "month": "2024-02",
        "pass_rate": 0.93,
        "delay_rate": 0.07
      }
    ]
  }
}
```

### 11.2 计划进度统计

#### GET /api/statistics/plan-progress
获取计划进度统计

**响应成功**:
```json
{
  "code": 200,
  "data": {
    "total_plans": 50,
    "status_distribution": {
      "DRAFT": 5,
      "PENDING": 10,
      "IN_PROGRESS": 25,
      "COMPLETED": 10
    },
    "category_distribution": {
      "new_system": 15,
      "new_feature": 20,
      "business_change": 10,
      "db_change": 5
    },
    "average_completion_days": 7.5
  }
}
```

---

**本文档根据PRD v1.3更新**

主要变更包括：
1. 新增SOP模板引擎API：/api/sop-templates, /api/sop-templates/{id}/work-item-templates, /api/sop-templates/{id}/workflow-nodes
2. 新增审核矩阵API：/api/audit-matrix-configs, /api/audit-matrix-configs/{id}/rules
3. 新增用户权限API：/api/users, /api/roles, /api/permissions, /api/users/me
4. 新增审计日志API：/api/audit-logs
5. 新增审核任务API：/api/audit-tasks/pending
6. 新增统计报表API：/api/statistics/vendor-quality, /api/statistics/plan-progress
7. 更新工作项API：增加审核等级字段、分配接口、状态流转接口
8. 更新核验API：增加脚本自动核验、AI智能分析核验接口
