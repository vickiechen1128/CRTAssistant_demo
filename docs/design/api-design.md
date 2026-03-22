# 仿真运维经理 - API 设计文档

| 版本 | 日期 | 作者 | 变更说明 |
|-----|------|-----|---------|
| v0.7 | 2024-03-22 | CRT | 新增：计划管理API，支持计划创建、仪表盘和标签管理 |
| v0.6 | 2024-03-22 | CRT | 新增：知识库管理API，支持验收标准与知识库关联 |
| v0.5 | 2024-03-22 | CRT | 新增：脚本验证相关API，完善验收标准详细配置接口 |
| v0.4 | 2024-03-22 | CRT | 重构：完善工作流、报告分析、五大核心检查项API，简化验收标准设计 |
| v0.3 | 2024-03-22 | CRT | 新增工作流管理API |
| v0.2 | 2024-03-22 | CRT | 更新：与后端实际路由对齐 |
| v0.1 | 2024-03-20 | CRT | 初稿，核心API定义 |

---

## 1. 接口概览

### 1.1 模块划分

| 模块 | 基础路径 | 描述 | 状态 |
|-----|---------|------|------|
| 认证 | /api/auth | 登录、登出、Token刷新 | ✅ 已实现 |
| 用户 | /api/users | 用户管理 | ✅ 已实现 |
| **计划** | **/api/plans** | **计划管理和仪表盘** | **🚧 新增** |
| **工作流** | **/api/workflows** | **工作流模板管理** | **🚧 待完善** |
| **工作流实例** | **/api/workflow-instances** | **工作流执行实例和进度** | **🚧 待完善** |
| **知识库** | **/api/knowledge** | **知识库管理和智能匹配** | **🚧 新增** |
| **脚本验证** | **/api/scripts** | **验证脚本管理和执行** | **🚧 新增** |
| **报告分析** | **/api/analysis** | **交付物分析和报告生成** | **🚧 新增** |
| 准入任务 | /api/admission-tasks | 准入检查任务CRUD | ✅ 已实现 |
| 台账 | /api/inventories | 台账管理 | ✅ 已实现 |
| 交付物 | /api/deliverables | 文件上传下载 | ✅ 已实现 |
| 仪表盘 | /api/dashboard | 统计数据 | ✅ 已实现 |
| 标准模板 | /api/standard-templates | 验收标准模板库 | 🚧 新增 |

---

## 2. 计划管理模块（新增）

### 2.1 计划基础操作

#### GET /api/plans
获取计划列表

**请求参数**:
```json
{
  "page": 1,
  "per_page": 20,
  "category": "STANDARD",
  "status": "IN_PROGRESS",
  "priority": "P1",
  "keyword": "订单系统",
  "start_date": "2024-03-01",
  "end_date": "2024-03-31"
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "plan-001",
        "plan_id": "PLAN-20240322-001",
        "name": "订单系统V2.0上线",
        "category": "STANDARD",
        "category_name": "标准上线",
        "priority": "P1",
        "priority_label": "高",
        "status": "IN_PROGRESS",
        "status_label": "执行中",
        "planned_start_time": "2024-03-25T10:00:00Z",
        "planned_end_time": "2024-03-25T18:00:00Z",
        "progress": 75,
        "involved_systems": ["订单系统", "支付系统"],
        "workflow_instance_id": "wfi-001",
        "tag": "PLAN-20240322-001-STD-1711072800",
        "created_by": "user-001",
        "created_at": "2024-03-22T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 15
    }
  }
}
```

---

#### POST /api/plans
创建计划

**请求体**:
```json
{
  "name": "订单系统V2.0上线",
  "category": "STANDARD",
  "priority": "P1",
  "planned_start_time": "2024-03-25T10:00:00Z",
  "planned_end_time": "2024-03-25T18:00:00Z",
  "description": "本次上线包含订单模块优化、支付接口升级",
  "involved_systems": ["订单系统", "支付系统"],
  "workflow_id": "wf-001",
  "auto_start": false
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "plan-001",
    "plan_id": "PLAN-20240322-001",
    "name": "订单系统V2.0上线",
    "tag": "PLAN-20240322-001-STD-1711072800",
    "status": "DRAFT",
    "workflow_instance_id": "wfi-001",
    "message": "计划创建成功，已生成数据标签"
  }
}
```

---

#### GET /api/plans/{id}
获取计划详情

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "plan-001",
    "plan_id": "PLAN-20240322-001",
    "name": "订单系统V2.0上线",
    "category": "STANDARD",
    "category_name": "标准上线",
    "priority": "P1",
    "priority_label": "高",
    "status": "IN_PROGRESS",
    "status_label": "执行中",
    "description": "本次上线包含订单模块优化、支付接口升级",
    "planned_start_time": "2024-03-25T10:00:00Z",
    "planned_end_time": "2024-03-25T18:00:00Z",
    "actual_start_time": "2024-03-25T10:05:00Z",
    "actual_end_time": null,
    "involved_systems": ["订单系统", "支付系统"],
    "progress": 75,
    "tag": "PLAN-20240322-001-STD-1711072800",
    "workflow": {
      "instance_id": "wfi-001",
      "workflow_name": "标准上线检查流程",
      "workflow_status": "IN_PROGRESS",
      "overall_progress": 75,
      "work_items": [
        {
          "id": "wi-001",
          "name": "基础资源标准化交付",
          "status": "COMPLETED",
          "progress": 100
        },
        {
          "id": "wi-002",
          "name": "安全基线核验",
          "status": "IN_PROGRESS",
          "progress": 60
        }
      ]
    },
    "materials": [
      {
        "id": "pm-001",
        "material_type": "meeting_minutes",
        "material_type_label": "会议纪要",
        "file_name": "会议纪要_订单系统上线.pdf",
        "file_size": 2048000,
        "description": "3月20日上线评审会议纪要",
        "uploaded_at": "2024-03-22T10:00:00Z"
      }
    ],
    "verification_progress": [
      {
        "verification_type": "inventory",
        "verification_type_label": "服务对象台账",
        "total_items": 5,
        "completed_items": 5,
        "passed_items": 5,
        "failed_items": 0,
        "progress": 100,
        "status": "COMPLETED"
      },
      {
        "verification_type": "resource_delivery",
        "verification_type_label": "基础资源交付",
        "total_items": 10,
        "completed_items": 7,
        "passed_items": 6,
        "failed_items": 1,
        "progress": 70,
        "status": "IN_PROGRESS"
      }
    ],
    "created_by": "user-001",
    "created_by_name": "张三",
    "created_at": "2024-03-22T10:00:00Z",
    "updated_at": "2024-03-22T14:30:00Z"
  }
}
```

---

#### PUT /api/plans/{id}
更新计划

**请求体**:
```json
{
  "name": "订单系统V2.0上线（更新）",
  "priority": "P0",
  "planned_start_time": "2024-03-26T10:00:00Z",
  "description": "更新计划说明"
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "plan-001",
    "message": "计划更新成功"
  }
}
```

---

#### DELETE /api/plans/{id}
删除计划

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "message": "计划删除成功"
  }
}
```

---

#### POST /api/plans/{id}/start
启动计划

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "plan-001",
    "status": "IN_PROGRESS",
    "actual_start_time": "2024-03-25T10:05:00Z",
    "message": "计划已启动，工作流实例开始执行"
  }
}
```

---

#### POST /api/plans/{id}/complete
完成计划

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "plan-001",
    "status": "COMPLETED",
    "actual_end_time": "2024-03-25T17:30:00Z",
    "message": "计划已完成"
  }
}
```

---

### 2.2 计划仪表盘

#### GET /api/plans/dashboard
获取计划仪表盘数据

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "statistics": {
      "total": 25,
      "in_progress": 8,
      "pending": 5,
      "completed": 10,
      "overdue": 2
    },
    "charts": {
      "trend": {
        "labels": ["03-01", "03-05", "03-10", "03-15", "03-20", "03-25"],
        "datasets": [
          {
            "label": "创建数",
            "data": [2, 3, 1, 4, 5, 2]
          },
          {
            "label": "完成数",
            "data": [1, 2, 2, 3, 4, 3]
          }
        ]
      },
      "category_distribution": [
        { "category": "STANDARD", "name": "标准上线", "count": 18, "percentage": 72 },
        { "category": "BUSINESS", "name": "业务需求", "count": 7, "percentage": 28 }
      ],
      "priority_distribution": [
        { "priority": "P0", "name": "紧急", "count": 2, "percentage": 8 },
        { "priority": "P1", "name": "高", "count": 10, "percentage": 40 },
        { "priority": "P2", "name": "中", "count": 10, "percentage": 40 },
        { "priority": "P3", "name": "低", "count": 3, "percentage": 12 }
      ]
    },
    "recent_plans": [
      {
        "id": "plan-001",
        "plan_id": "PLAN-20240322-001",
        "name": "订单系统V2.0上线",
        "priority": "P1",
        "status": "IN_PROGRESS",
        "progress": 75,
        "planned_start_time": "2024-03-25T10:00:00Z"
      }
    ],
    "overdue_plans": [
      {
        "id": "plan-002",
        "plan_id": "PLAN-20240320-002",
        "name": "支付系统优化",
        "priority": "P0",
        "planned_start_time": "2024-03-20T10:00:00Z",
        "days_overdue": 5
      }
    ]
  }
}
```

---

### 2.3 计划审批材料

#### POST /api/plans/{id}/materials
上传审批材料

**请求体** (multipart/form-data):
```
material_type: meeting_minutes
file: [二进制文件内容]
description: 3月20日上线评审会议纪要
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "pm-001",
    "material_type": "meeting_minutes",
    "file_name": "会议纪要_订单系统上线.pdf",
    "file_size": 2048000,
    "message": "材料上传成功"
  }
}
```

---

#### DELETE /api/plans/{id}/materials/{material_id}
删除审批材料

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "message": "材料删除成功"
  }
}
```

---

### 2.4 计划标签管理

#### GET /api/plans/{id}/tags
获取计划关联的标签资源

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "tag": "PLAN-20240322-001-STD-1711072800",
    "resources": {
      "servers": [
        {
          "resource_id": "srv-001",
          "resource_name": "order-server-01",
          "resource_type": "server",
          "tagged_at": "2024-03-22T10:00:00Z"
        },
        {
          "resource_id": "srv-002",
          "resource_name": "order-server-02",
          "resource_type": "server",
          "tagged_at": "2024-03-22T10:00:00Z"
        }
      ],
      "applications": [
        {
          "resource_id": "app-001",
          "resource_name": "订单系统",
          "resource_type": "application",
          "tagged_at": "2024-03-22T10:00:00Z"
        }
      ],
      "accounts": [
        {
          "resource_id": "acc-001",
          "resource_name": "order_admin",
          "resource_type": "account",
          "tagged_at": "2024-03-22T10:00:00Z"
        }
      ]
    },
    "total_count": 10
  }
}
```

---

#### POST /api/plans/{id}/tags
为资源打标签

**请求体**:
```json
{
  "resources": [
    {
      "resource_type": "server",
      "resource_id": "srv-003",
      "resource_name": "order-server-03"
    }
  ]
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "tagged_count": 1,
    "message": "成功为1个资源打标签"
  }
}
```

---

#### DELETE /api/plans/{id}/tags
移除资源标签

**请求体**:
```json
{
  "resource_type": "server",
  "resource_id": "srv-003"
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "message": "标签移除成功"
  }
}
```

---

### 2.5 核验任务进度

#### GET /api/plans/{id}/verification-progress
获取计划核验任务进度

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "plan_id": "plan-001",
    "overall_progress": 75,
    "verifications": [
      {
        "verification_type": "inventory",
        "verification_type_label": "服务对象台账",
        "total_items": 5,
        "completed_items": 5,
        "passed_items": 5,
        "failed_items": 0,
        "pending_items": 0,
        "progress": 100,
        "status": "COMPLETED",
        "last_updated": "2024-03-25T12:00:00Z"
      },
      {
        "verification_type": "resource_delivery",
        "verification_type_label": "基础资源交付",
        "total_items": 10,
        "completed_items": 7,
        "passed_items": 6,
        "failed_items": 1,
        "pending_items": 3,
        "progress": 70,
        "status": "IN_PROGRESS",
        "last_updated": "2024-03-25T14:30:00Z"
      },
      {
        "verification_type": "permission",
        "verification_type_label": "权限移交",
        "total_items": 3,
        "completed_items": 0,
        "passed_items": 0,
        "failed_items": 0,
        "pending_items": 3,
        "progress": 0,
        "status": "PENDING",
        "last_updated": null
      },
      {
        "verification_type": "security",
        "verification_type_label": "安全基线",
        "total_items": 8,
        "completed_items": 0,
        "passed_items": 0,
        "failed_items": 0,
        "pending_items": 8,
        "progress": 0,
        "status": "PENDING",
        "last_updated": null
      },
      {
        "verification_type": "monitoring",
        "verification_type_label": "监控告警",
        "total_items": 4,
        "completed_items": 0,
        "passed_items": 0,
        "failed_items": 0,
        "pending_items": 4,
        "progress": 0,
        "status": "PENDING",
        "last_updated": null
      }
    ]
  }
}
```

---

## 3. 工作流管理模块

### 2.1 工作流模板

#### GET /api/workflows
获取工作流模板列表

**请求参数**:
```json
{
  "page": 1,
  "per_page": 20,
  "is_preset": true,
  "keyword": "标准上线"
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "wf-001",
        "name": "标准上线检查流程",
        "description": "适用于一般业务系统上线前检查",
        "version": "v1.0",
        "is_preset": true,
        "status": "active",
        "work_item_count": 5,
        "created_by": "user-001",
        "created_at": "2024-03-22T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 10
    }
  }
}
```

---

#### POST /api/workflows
创建工作流模板

**请求体**:
```json
{
  "name": "标准上线检查流程",
  "description": "适用于一般业务系统上线前检查",
  "work_items": [
    {
      "name": "基础资源标准化交付",
      "description": "服务器、网络、存储等基础资源的配置标准化检查",
      "work_item_type": "resource_delivery",
      "display_order": 1,
      "estimated_duration": 120,
      "is_required": true,
      "acceptance_criteria": [
        {
          "content": "资源配置符合标准化要求",
          "criteria_type": "manual",
          "is_required": true
        }
      ]
    },
    {
      "name": "服务对象台账",
      "description": "应用系统、云服务、账户等台账信息的完整性和准确性",
      "work_item_type": "inventory",
      "display_order": 2,
      "estimated_duration": 60,
      "is_required": true,
      "acceptance_criteria": [
        {
          "content": "所有台账信息已完整填写",
          "criteria_type": "manual",
          "is_required": true
        }
      ]
    },
    {
      "name": "生产环境权限移交",
      "description": "生产环境访问权限的分配、审核和移交",
      "work_item_type": "permission_handover",
      "display_order": 3,
      "estimated_duration": 90,
      "is_required": true,
      "acceptance_criteria": [
        {
          "content": "权限移交流程已完成",
          "criteria_type": "manual",
          "is_required": true
        }
      ]
    },
    {
      "name": "安全基线核验",
      "description": "安全基线配置检查，包括账户安全、漏洞扫描等",
      "work_item_type": "security_baseline",
      "display_order": 4,
      "estimated_duration": 60,
      "is_required": true,
      "acceptance_criteria": [
        {
          "content": "安全加固报告显示通过",
          "criteria_type": "auto",
          "is_required": true,
          "auto_check_script": "extract_security_report_conclusion"
        }
      ]
    },
    {
      "name": "监控告警配置确认",
      "description": "监控项、告警规则、值班配置等确认",
      "work_item_type": "monitoring",
      "display_order": 5,
      "estimated_duration": 30,
      "is_required": true,
      "acceptance_criteria": [
        {
          "content": "云监控Agent已安装",
          "criteria_type": "manual",
          "is_required": true
        },
        {
          "content": "监控指标已接入统一监控平台",
          "criteria_type": "manual",
          "is_required": true
        },
        {
          "content": "告警阈值和接收人已配置",
          "criteria_type": "manual",
          "is_required": true
        }
      ]
    }
  ]
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "wf-001",
    "name": "标准上线检查流程",
    "message": "工作流模板创建成功"
  }
}
```

---

#### GET /api/workflows/{id}
获取工作流模板详情

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "wf-001",
    "name": "标准上线检查流程",
    "description": "适用于一般业务系统上线前检查",
    "version": "v1.0",
    "is_preset": true,
    "status": "active",
    "work_items": [
      {
        "id": "wi-001",
        "name": "基础资源标准化交付",
        "work_item_type": "resource_delivery",
        "display_order": 1,
        "acceptance_criteria": [
          {
            "id": "ac-001",
            "content": "资源配置符合标准化要求",
            "criteria_type": "manual",
            "is_required": true
          }
        ]
      }
    ],
    "created_by": "user-001",
    "created_at": "2024-03-22T10:00:00Z"
  }
}
```

---

### 2.2 标准模板库

#### GET /api/standard-templates
获取标准验收标准模板

**请求参数**:
```json
{
  "template_type": "criteria",
  "work_item_type": "security_baseline"
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "st-001",
        "name": "安全基线核验标准",
        "description": "安全团队提供的加固报告核验",
        "template_type": "criteria",
        "work_item_type": "security_baseline",
        "content": [
          {
            "content": "安全加固报告显示通过",
            "criteria_type": "auto",
            "is_required": true,
            "auto_check_script": "extract_security_report_conclusion"
          }
        ]
      },
      {
        "id": "st-002",
        "name": "监控告警配置标准",
        "description": "监控告警配置确认清单",
        "template_type": "criteria",
        "work_item_type": "monitoring",
        "content": [
          {
            "content": "云监控Agent已安装",
            "criteria_type": "manual",
            "is_required": true
          },
          {
            "content": "监控指标已接入统一监控平台",
            "criteria_type": "manual",
            "is_required": true
          },
          {
            "content": "告警阈值和接收人已配置",
            "criteria_type": "manual",
            "is_required": true
          }
        ]
      }
    ]
  }
}
```

---

### 2.4 验证脚本管理

#### GET /api/scripts
获取验证脚本列表

**请求参数**:
```json
{
  "page": 1,
  "per_page": 20,
  "script_type": "system_baseline",
  "is_preset": true
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "vs-001",
        "name": "系统基线检查脚本",
        "description": "验证系统账户安全、磁盘分区、网络配置等7项基线",
        "script_type": "system_baseline",
        "script_language": "bash",
        "execution_target": "remote",
        "timeout_seconds": 300,
        "output_format": "json",
        "is_preset": true,
        "version": "v1.0",
        "created_at": "2024-03-22T10:00:00Z"
      },
      {
        "id": "vs-002",
        "name": "软件部署检查脚本",
        "description": "验证安装路径、脚本规范、一键部署、日志记录",
        "script_type": "software_deploy",
        "script_language": "bash",
        "is_preset": true,
        "version": "v1.0"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 5
    }
  }
}
```

---

#### GET /api/scripts/{id}
获取验证脚本详情

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "vs-001",
    "name": "系统基线检查脚本",
    "description": "验证系统账户安全、磁盘分区、网络配置等7项基线",
    "script_type": "system_baseline",
    "script_content": "#!/bin/bash\n# 系统基线检查脚本\n...",
    "script_language": "bash",
    "execution_target": "remote",
    "timeout_seconds": 300,
    "output_format": "json",
    "is_preset": true,
    "version": "v1.0",
    "checklist_items": [
      {"id": "1", "content": "系统账户安全 - 设定符合《账户创建以及权限》基线要求"},
      {"id": "2", "content": "磁盘分区合规 - 系统盘与应用/数据盘物理或逻辑隔离"},
      {"id": "3", "content": "网络安全 - 防火墙策略最小化，仅开放必要端口"},
      {"id": "4", "content": "系统基础环境配置 - 时区同步(NTP)、字符集(UTF-8)"},
      {"id": "5", "content": "自动更新控制 - 禁止机器自动重启、禁止自动更新"},
      {"id": "6", "content": "证书管理 - 证书导入(如有)"},
      {"id": "7", "content": "其他安全基线 - 符合组织安全基线要求"}
    ],
    "created_by": "user-001",
    "created_at": "2024-03-22T10:00:00Z"
  }
}
```

---

#### POST /api/scripts
创建自定义验证脚本

**请求体**:
```json
{
  "name": "自定义应用检查脚本",
  "description": "检查应用服务状态",
  "script_type": "custom",
  "script_content": "#!/bin/bash\necho '{\"status\": \"running\"}'",
  "script_language": "bash",
  "execution_target": "remote",
  "timeout_seconds": 60,
  "output_format": "json"
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "vs-006",
    "name": "自定义应用检查脚本",
    "message": "验证脚本创建成功"
  }
}
```

---

#### POST /api/scripts/{id}/execute
执行验证脚本

**请求体**:
```json
{
  "work_item_instance_id": "wii-001",
  "target_host": "192.168.1.100",
  "target_port": 22,
  "username": "admin",
  "auth_type": "key",
  "private_key": "-----BEGIN RSA PRIVATE KEY-----...",
  "parameters": {
    "check_level": "strict"
  }
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "execution_id": "se-001",
    "script_id": "vs-001",
    "execution_status": "running",
    "message": "脚本已开始执行",
    "started_at": "2024-03-22T10:00:00Z"
  }
}
```

---

#### GET /api/scripts/executions/{executionId}
获取脚本执行结果

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "se-001",
    "script_id": "vs-001",
    "script_name": "系统基线检查脚本",
    "work_item_instance_id": "wii-001",
    "target_host": "192.168.1.100",
    "execution_status": "success",
    "exit_code": 0,
    "stdout": {
      "overall_result": "passed",
      "check_items": [
        {"id": "1", "name": "系统账户安全", "result": "passed", "detail": "账户策略已配置"},
        {"id": "2", "name": "磁盘分区合规", "result": "passed", "detail": "系统盘与数据盘已分离"},
        {"id": "3", "name": "网络安全", "result": "passed", "detail": "防火墙规则符合要求"},
        {"id": "4", "name": "系统基础环境配置", "result": "passed", "detail": "NTP和字符集已配置"},
        {"id": "5", "name": "自动更新控制", "result": "passed", "detail": "自动更新已禁用"},
        {"id": "6", "name": "证书管理", "result": "na", "detail": "无需证书"},
        {"id": "7", "name": "其他安全基线", "result": "passed", "detail": "符合组织安全基线"}
      ]
    },
    "stderr": "",
    "execution_duration_ms": 5230,
    "started_at": "2024-03-22T10:00:00Z",
    "completed_at": "2024-03-22T10:00:05Z"
  }
}
```

---

## 3. 知识库管理模块

### 3.1 知识分类管理

#### GET /api/knowledge/categories
获取知识分类列表

**请求参数**:
```json
{
  "page": 1,
  "per_page": 20,
  "is_preset": true,
  "work_item_type": "resource_delivery"
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "kc-001",
        "code": "RSD",
        "name": "基础资源标准化交付",
        "description": "系统基线、软件部署相关规范",
        "parent_id": null,
        "work_item_types": ["resource_delivery"],
        "display_order": 1,
        "is_preset": true,
        "status": "active",
        "item_count": 5,
        "created_at": "2024-03-22T10:00:00Z"
      },
      {
        "id": "kc-002",
        "code": "INV",
        "name": "服务对象台账收集",
        "description": "应用系统、云服务、账户台账相关规范",
        "work_item_types": ["inventory"],
        "is_preset": true,
        "item_count": 3
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 5
    }
  }
}
```

---

#### POST /api/knowledge/categories
创建知识分类

**请求体**:
```json
{
  "code": "CUSTOM",
  "name": "自定义分类",
  "description": "用户自定义的验收要求分类",
  "parent_id": null,
  "work_item_types": ["custom"],
  "display_order": 10
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "kc-006",
    "code": "CUSTOM",
    "name": "自定义分类",
    "message": "知识分类创建成功"
  }
}
```

---

### 3.2 知识条目管理

#### GET /api/knowledge/items
获取知识条目列表

**请求参数**:
```json
{
  "page": 1,
  "per_page": 20,
  "category_id": "kc-001",
  "content_type": "baseline",
  "keyword": "系统基线",
  "work_item_type": "resource_delivery"
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "ki-001",
        "category_id": "kc-001",
        "category_name": "基础资源标准化交付",
        "title": "生产环境系统基线配置要求",
        "content_type": "baseline",
        "source_format": "md",
        "version": "v1.0",
        "tags": ["系统基线", "安全配置", "账户管理"],
        "work_item_types": ["resource_delivery"],
        "usage_count": 15,
        "is_preset": true,
        "status": "published",
        "created_by": "user-001",
        "created_at": "2024-03-22T10:00:00Z",
        "updated_at": "2024-03-22T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 10
    }
  }
}
```

---

#### GET /api/knowledge/items/{id}
获取知识条目详情

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "ki-001",
    "category_id": "kc-001",
    "category_name": "基础资源标准化交付",
    "title": "生产环境系统基线配置要求",
    "content_type": "baseline",
    "source_format": "md",
    "content": "# 生产环境系统基线配置要求\n\n## 1. 系统账户安全\n设定符合《账户创建以及权限》基线要求...\n\n## 2. 磁盘分区合规\n系统盘与应用/数据盘物理或逻辑隔离...",
    "content_structure": {
      "items": [
        {
          "id": "1",
          "title": "系统账户安全",
          "content": "设定符合《账户创建以及权限》基线要求",
          "level": 2
        },
        {
          "id": "2",
          "title": "磁盘分区合规",
          "content": "系统盘与应用/数据盘物理或逻辑隔离",
          "level": 2
        }
      ]
    },
    "source_file": {
      "name": "system_baseline.md",
      "url": "/uploads/knowledge/system_baseline.md",
      "size": 2048
    },
    "version": "v1.0",
    "tags": ["系统基线", "安全配置"],
    "work_item_types": ["resource_delivery"],
    "usage_count": 15,
    "is_preset": true,
    "status": "published",
    "created_by": "user-001",
    "created_at": "2024-03-22T10:00:00Z",
    "updated_at": "2024-03-22T10:00:00Z"
  }
}
```

---

#### POST /api/knowledge/items
创建知识条目

**请求体**:
```json
{
  "category_id": "kc-001",
  "title": "自定义基线要求",
  "content_type": "requirement",
  "content": "# 自定义基线要求\n\n## 检查项1\n详细要求说明...",
  "tags": ["自定义", "基线"],
  "work_item_types": ["resource_delivery"]
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "ki-010",
    "title": "自定义基线要求",
    "message": "知识条目创建成功"
  }
}
```

---

#### POST /api/knowledge/items/{id}/import
从文件导入知识条目

**请求体** (multipart/form-data):
```
category_id: kc-001
title: 从Excel导入的检查清单
content_type: checklist
file: [二进制文件内容]
tags: ["导入", "检查清单"]
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "ki-011",
    "title": "从Excel导入的检查清单",
    "parsed_items": 10,
    "message": "文件导入成功，已解析10个检查项"
  }
}
```

---

### 3.3 智能匹配与生成

#### POST /api/knowledge/match
智能匹配知识条目

**请求体**:
```json
{
  "work_item_type": "resource_delivery",
  "work_item_name": "基础资源标准化交付",
  "keywords": ["系统基线", "磁盘分区", "网络安全"],
  "limit": 10
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "matches": [
      {
        "knowledge_id": "ki-001",
        "title": "生产环境系统基线配置要求",
        "category_name": "基础资源标准化交付",
        "content_type": "baseline",
        "match_score": 0.95,
        "match_reason": "工作项类型完全匹配，关键词高度相关",
        "suggested_criteria": [
          {
            "content": "系统账户安全 - 设定符合《账户创建以及权限》基线要求",
            "criteria_type": "script",
            "verification_method": "script",
            "deliverable_desc": "脚本执行报告"
          },
          {
            "content": "磁盘分区合规 - 系统盘与应用/数据盘物理或逻辑隔离",
            "criteria_type": "script",
            "verification_method": "script",
            "deliverable_desc": "脚本执行报告"
          }
        ]
      },
      {
        "knowledge_id": "ki-002",
        "title": "软件部署规范",
        "match_score": 0.75,
        "match_reason": "工作项类型匹配"
      }
    ]
  }
}
```

---

#### POST /api/knowledge/generate-criteria
基于知识条目生成验收标准

**请求体**:
```json
{
  "knowledge_id": "ki-001",
  "work_item_id": "wi-001",
  "selected_items": ["1", "2", "3"]
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "generated_criteria": [
      {
        "content": "系统账户安全 - 设定符合《账户创建以及权限》基线要求",
        "criteria_type": "script",
        "verification_method": "script",
        "is_required": true,
        "deliverable_types": ["json", "txt"],
        "deliverable_desc": "脚本执行报告（JSON格式）",
        "source_knowledge_id": "ki-001",
        "source_knowledge_version": "v1.0",
        "generation_confidence": 0.95
      },
      {
        "content": "磁盘分区合规 - 系统盘与应用/数据盘物理或逻辑隔离",
        "criteria_type": "script",
        "verification_method": "script",
        "is_required": true,
        "deliverable_types": ["json", "txt"],
        "deliverable_desc": "脚本执行报告（JSON格式）",
        "source_knowledge_id": "ki-001",
        "source_knowledge_version": "v1.0",
        "generation_confidence": 0.95
      }
    ],
    "message": "成功生成2条验收标准"
  }
}
```

---

### 3.4 版本管理

#### GET /api/knowledge/items/{id}/versions
获取知识条目版本历史

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "knowledge_id": "ki-001",
    "current_version": "v1.2",
    "versions": [
      {
        "version": "v1.2",
        "change_log": "新增证书管理要求",
        "created_by": "user-001",
        "created_at": "2024-03-22T12:00:00Z"
      },
      {
        "version": "v1.1",
        "change_log": "完善网络安全要求",
        "created_by": "user-001",
        "created_at": "2024-03-20T10:00:00Z"
      },
      {
        "version": "v1.0",
        "change_log": "初始版本",
        "created_by": "user-001",
        "created_at": "2024-03-15T10:00:00Z"
      }
    ]
  }
}
```

---

#### POST /api/knowledge/items/{id}/versions
创建新版本

**请求体**:
```json
{
  "content": "# 更新后的内容...",
  "change_log": "新增证书管理要求",
  "version_type": "minor"
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "new_version": "v1.2",
    "message": "新版本创建成功"
  }
}
```

---

### 3.4 文档导入与解析

#### POST /api/knowledge/parse-document
解析上传的文档并提取检查项

**请求体** (multipart/form-data):
```
file: [二进制文件内容]
file_type: word  // word/excel/markdown
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "file_name": "系统基线验收标准.docx",
    "file_size": 2355200,
    "parsed_content": {
      "title": "系统基线验收标准",
      "items": [
        {
          "id": "1",
          "title": "系统账户安全",
          "content": "设定符合《账户创建以及权限》基线要求",
          "level": 1,
          "type": "heading"
        },
        {
          "id": "2",
          "title": "磁盘分区合规",
          "content": "系统盘与应用/数据盘物理或逻辑隔离",
          "level": 1,
          "type": "heading"
        }
      ],
      "tables": [
        {
          "headers": ["检查项", "要求", "验证方式"],
          "rows": [
            ["账户安全", "符合基线要求", "脚本验证"],
            ["磁盘分区", "物理隔离", "脚本验证"]
          ]
        }
      ]
    },
    "suggested_criteria": [
      {
        "content": "系统账户安全 - 设定符合《账户创建以及权限》基线要求",
        "criteria_type": "script",
        "confidence": 0.92
      },
      {
        "content": "磁盘分区合规 - 系统盘与应用/数据盘物理或逻辑隔离",
        "criteria_type": "script",
        "confidence": 0.90
      }
    ]
  }
}
```

---

### 3.5 工作流集成接口

#### POST /api/knowledge/workflow-link
将知识条目关联到工作项验收标准

**请求体**:
```json
{
  "workflow_id": "wf-001",
  "work_item_id": "wi-001",
  "knowledge_ids": ["ki-001", "ki-002"],
  "auto_generate": true,
  "selected_criteria": ["1", "2", "3", "4"]
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "linked_count": 2,
    "generated_criteria": [
      {
        "id": "ac-001",
        "content": "系统账户安全 - 设定符合《账户创建以及权限》基线要求",
        "criteria_type": "script",
        "source_knowledge_id": "ki-001",
        "source_knowledge_version": "v1.0"
      },
      {
        "id": "ac-002",
        "content": "磁盘分区合规 - 系统盘与应用/数据盘物理或逻辑隔离",
        "criteria_type": "script",
        "source_knowledge_id": "ki-001",
        "source_knowledge_version": "v1.0"
      }
    ],
    "message": "成功关联2个知识条目，生成4条验收标准"
  }
}
```

---

#### GET /api/knowledge/workflow-candidates/{workflow_id}
获取工作流候选知识条目（智能推荐）

**请求参数**:
```json
{
  "work_item_type": "resource_delivery",
  "limit": 10
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "recommendations": [
      {
        "knowledge_id": "ki-001",
        "title": "生产环境系统基线配置要求",
        "category_name": "基础资源标准化交付",
        "match_score": 0.98,
        "match_reason": "工作项类型完全匹配，历史使用频率高",
        "already_linked": false,
        "usage_count": 15
      },
      {
        "knowledge_id": "ki-002",
        "title": "软件标准化部署规范",
        "category_name": "基础资源标准化交付",
        "match_score": 0.92,
        "match_reason": "工作项类型匹配",
        "already_linked": false,
        "usage_count": 8
      }
    ],
    "linked_knowledge": [
      {
        "knowledge_id": "ki-003",
        "title": "系统基线检查脚本使用手册",
        "linked_at": "2024-03-22T10:00:00Z"
      }
    ]
  }
}
```

---

#### POST /api/knowledge/batch-generate
批量生成验收标准

**请求体**:
```json
{
  "workflow_id": "wf-001",
  "work_item_id": "wi-001",
  "knowledge_items": [
    {
      "knowledge_id": "ki-001",
      "selected_items": ["1", "2", "3", "4", "5", "6", "7"]
    },
    {
      "knowledge_id": "ki-002",
      "selected_items": ["1", "2", "3", "4"]
    }
  ],
  "default_verification_method": "script"
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "total_generated": 11,
    "criteria": [
      {
        "id": "ac-001",
        "content": "系统账户安全 - 设定符合《账户创建以及权限》基线要求",
        "criteria_type": "script",
        "verification_method": "script",
        "source_knowledge_id": "ki-001",
        "generation_confidence": 0.95
      }
    ],
    "message": "成功生成11条验收标准"
  }
}
```

---

## 4. 工作流实例模块

### 3.1 工作流实例管理

#### POST /api/workflow-instances
创建工作流实例（绑定准入任务）

**请求体**:
```json
{
  "workflow_id": "wf-001",
  "task_id": "task-001",
  "remark": "订单管理系统V2.0上线检查"
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "wfi-001",
    "workflow_id": "wf-001",
    "task_id": "task-001",
    "status": "pending",
    "overall_progress": 0,
    "work_item_instances": [
      {
        "id": "wii-001",
        "work_item_id": "wi-001",
        "name": "基础资源标准化交付",
        "status": "pending",
        "progress": 0,
        "result": "not_started"
      }
    ]
  }
}
```

---

#### GET /api/workflow-instances/{id}
获取工作流实例详情

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "wfi-001",
    "workflow_id": "wf-001",
    "task_id": "task-001",
    "status": "in_progress",
    "overall_progress": 60,
    "started_at": "2024-03-22T10:00:00Z",
    "work_item_instances": [
      {
        "id": "wii-001",
        "work_item_id": "wi-001",
        "name": "基础资源标准化交付",
        "work_item_type": "resource_delivery",
        "status": "completed",
        "progress": 100,
        "result": "passed",
        "result_source": "manual",
        "completed_at": "2024-03-22T11:00:00Z"
      },
      {
        "id": "wii-004",
        "work_item_id": "wi-004",
        "name": "安全基线核验",
        "work_item_type": "security_baseline",
        "status": "pending_review",
        "progress": 80,
        "result": "not_started",
        "deliverables": [
          {
            "id": "del-001",
            "file_name": "security_scan_report.pdf",
            "uploaded_at": "2024-03-22T12:00:00Z"
          }
        ]
      }
    ]
  }
}
```

---

#### POST /api/workflow-instances/{id}/start
启动工作流实例

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "message": "工作流实例已启动",
    "started_at": "2024-03-22T10:00:00Z"
  }
}
```

---

### 3.2 工作项实例执行

#### POST /api/workflow-instances/{id}/work-items/{workItemId}/complete
完成工作项

**请求体**:
```json
{
  "result": "passed",
  "result_source": "manual",
  "remark": "所有资源配置符合标准"
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "message": "工作项已完成",
    "next_work_items": ["wii-002"]
  }
}
```

---

## 4. 报告生成与分析助手模块

### 4.1 交付物分析

#### POST /api/analysis/deliverables/{deliverableId}/analyze
分析交付物（调用AI服务）

**请求体**:
```json
{
  "work_item_instance_id": "wii-004",
  "analysis_type": "security_report"
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "analysis_id": "ar-001",
    "analysis_status": "processing",
    "estimated_time": 30
  }
}
```

---

#### GET /api/analysis/results/{analysisId}
获取分析结果

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "ar-001",
    "deliverable_id": "del-001",
    "analysis_status": "completed",
    "auto_result": "passed",
    "auto_analysis_report": {
      "summary": {
        "overall_result": "passed",
        "confidence": 0.95,
        "key_findings": ["安全加固报告显示通过"]
      },
      "criteria_checks": [
        {
          "criteria_id": "ac-004",
          "criteria_content": "安全加固报告显示通过",
          "result": "passed",
          "evidence": "报告第3页结论部分明确标注：'本次安全加固检查通过'",
          "severity": "normal"
        }
      ],
      "recommendations": []
    },
    "final_result": null,
    "final_result_source": null,
    "analyzed_at": "2024-03-22T12:05:00Z"
  }
}
```

---

#### POST /api/analysis/results/{analysisId}/confirm
确认/修正分析结果

**请求体**:
```json
{
  "final_result": "passed",
  "manual_remark": "经人工复核，报告结论明确，予以通过"
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "message": "分析结果已确认",
    "final_result": "passed",
    "confirmed_at": "2024-03-22T12:10:00Z"
  }
}
```

---

### 4.2 批量分析报告

#### POST /api/analysis/workflow-instances/{instanceId}/report
生成工作流实例综合分析报告

**请求体**:
```json
{
  "report_type": "comprehensive",
  "include_recommendations": true
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "report_id": "rpt-001",
    "report_url": "/api/analysis/reports/rpt-001/download",
    "summary": {
      "total_work_items": 5,
      "completed": 3,
      "passed": 3,
      "failed": 0,
      "pending_improvement": 0,
      "overall_progress": 60
    },
    "work_item_results": [
      {
        "work_item_name": "基础资源标准化交付",
        "result": "passed",
        "result_source": "manual"
      },
      {
        "work_item_name": "安全基线核验",
        "result": "passed",
        "result_source": "auto",
        "analysis_confidence": 0.95
      }
    ],
    "recommendations": [
      "建议加快监控告警配置确认进度"
    ]
  }
}
```

---

## 5. 五大核心检查项模块

### 5.1 安全基线核验

#### POST /api/security-baselines
创建安全基线核验记录

**请求体**:
```json
{
  "work_item_instance_id": "wii-004",
  "check_category": "system",
  "check_item": "主机安全加固检查",
  "check_standard": "安全团队提供的加固标准",
  "scan_report_id": "del-001"
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "sb-001",
    "work_item_instance_id": "wii-004",
    "check_result": "pending",
    "message": "已关联扫描报告，等待分析"
  }
}
```

---

#### POST /api/security-baselines/{id}/analyze
分析安全扫描报告

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "analysis_id": "ar-002",
    "analysis_status": "processing",
    "message": "正在使用AI分析安全报告..."
  }
}
```

---

### 5.2 监控告警配置确认

#### POST /api/monitoring-configs
创建监控配置确认记录

**请求体**:
```json
{
  "work_item_instance_id": "wii-005",
  "config_items": [
    {
      "config_type": "agent",
      "config_name": "云监控Agent安装",
      "is_configured": true,
      "evidence": "Agent版本v2.1.0，运行正常"
    },
    {
      "config_type": "metric",
      "config_name": "监控指标接入",
      "is_configured": true,
      "evidence": "CPU、内存、磁盘、网络指标已接入"
    },
    {
      "config_type": "alert",
      "config_name": "告警规则配置",
      "is_configured": true,
      "is_tested": true,
      "test_result": "告警通知正常，延迟<30s"
    }
  ]
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "mc-001",
    "work_item_instance_id": "wii-005",
    "config_count": 3,
    "configured_count": 3,
    "message": "监控配置确认记录已创建"
  }
}
```

---

## 6. AI分析服务集成

### 6.1 分析服务配置

系统支持配置不同的AI服务提供商：

```json
{
  "ai_provider": "kimi",
  "api_key": "sk-xxx",
  "api_endpoint": "https://api.moonshot.cn/v1",
  "model": "moonshot-v1-128k",
  "analysis_types": {
    "security_report": {
      "prompt_template": "请分析以下安全扫描报告，提取结论：通过/不通过",
      "max_tokens": 2000
    },
    "deliverable_review": {
      "prompt_template": "请审查以下交付物内容是否符合要求",
      "max_tokens": 4000
    }
  }
}
```

### 6.2 支持的AI服务

| 服务 | 标识 | 特点 | 成本 |
|-----|------|------|------|
| Kimi Code | kimi | 长文本处理能力强，适合报告分析 | 已有订阅 |
| 阿里云百炼 | bailian | 国内服务，稳定可靠 | 按量付费 |
| 火山引擎 | volcengine | 字节跳动，性价比高 | 按量付费 |
| DeepSeek | deepseek | 开源，成本低 | 开源免费 |

---

## 7. 错误码定义

| 错误码 | 说明 | 场景 |
|-------|------|------|
| 0 | 成功 | 请求处理成功 |
| 4001 | 参数错误 | 请求参数缺失或格式不正确 |
| 4002 | 工作流不存在 | 指定的工作流ID不存在 |
| 4003 | 工作流已发布 | 已发布的工作流不能直接修改 |
| 4004 | 工作项依赖冲突 | 工作项依赖关系存在循环 |
| 4005 | 分析服务不可用 | AI分析服务调用失败 |
| 4006 | 文件格式不支持 | 上传的交付物格式不支持分析 |
| 5001 | 服务器内部错误 | 系统内部错误 |

---

## 8. 相关文档

- [PRD文档](./PRD.md)
- [数据模型设计](./data-model.md)
- [原型设计](../prototype/wireframes.md)
- [业务规则](./business-rules.md)
