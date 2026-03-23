# 仿真运维经理 - API 设计文档

| 版本 | 日期 | 作者 | 变更说明 |
|-----|------|-----|---------|
| v1.0 | 2024-03-22 | CRT | 重构：按照五大业务阶段重新组织API，使接口更清晰、更有条理 |
| v0.7 | 2024-03-22 | CRT | 新增：计划管理API，支持计划创建、仪表盘和标签管理 |
| v0.1 | 2024-03-20 | CRT | 初稿，核心API定义 |

---

## 1. 接口概览

### 1.1 业务阶段与API对应关系

根据业务流程的五大阶段，API按以下方式组织：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API 业务阶段对应关系                               │
└─────────────────────────────────────────────────────────────────────────────┘

第一阶段：计划制定
├── POST   /api/plans                    # 创建计划
├── GET    /api/plans                    # 获取计划列表
├── GET    /api/plans/{id}               # 获取计划详情
├── PUT    /api/plans/{id}               # 更新计划
├── DELETE /api/plans/{id}               # 删除计划
├── POST   /api/plans/{id}/materials     # 上传审批材料
└── GET    /api/plans/dashboard          # 计划仪表盘

第二阶段：工作项拆解
├── POST   /api/plans/{id}/work-items              # 添加工作项
├── GET    /api/plans/{id}/work-items              # 获取工作项列表
├── POST   /api/work-items/{id}/sub-items          # 添加子工作项
├── GET    /api/work-items/{parent_id}/sub-items   # 获取子工作项列表
└── PUT    /api/plans/{id}/workflow                # 保存工作流编排

第三阶段：验收标准制定
├── POST   /api/sub-work-items/{id}/criteria       # 制定验收标准
├── GET    /api/criteria/templates                 # 获取预置模板
├── POST   /api/criteria/import                    # 导入文档作为验收标准
├── GET    /api/knowledge/items                    # 从知识库选择
└── PUT    /api/sub-work-items/{id}/criteria       # 更新验收标准

第四阶段：交付物管理
├── POST   /api/sub-work-items/{id}/deliverables   # 上传交付物
├── GET    /api/sub-work-items/{id}/deliverables   # 获取交付物列表
├── DELETE /api/deliverables/{id}                  # 删除交付物
└── GET    /api/deliverables/{id}/download         # 下载交付物

第五阶段：核验执行
├── POST   /api/deliverables/{id}/verify           # 触发核验
├── GET    /api/verification-methods               # 获取核验方式配置
├── POST   /api/verification/manual                # 人工核验提交
├── POST   /api/verification/script                # 脚本核验执行
├── POST   /api/verification/ai                    # AI分析执行
└── GET    /api/sub-work-items/{id}/result         # 获取核验结果
```

### 1.2 接口规范

**基础URL**: `/api`

**认证方式**: JWT Token (Header: `Authorization: Bearer {token}`)

**请求格式**: JSON

**响应格式**:
```json
{
  "code": 0,        // 0表示成功，非0表示错误
  "message": "",    // 错误信息（code不为0时）
  "data": {}        // 响应数据
}
```

**HTTP状态码**:
- 200: 请求成功
- 400: 请求参数错误
- 401: 未认证
- 403: 无权限
- 404: 资源不存在
- 500: 服务器内部错误

---

## 2. 第一阶段：计划管理API

### 2.1 计划基础操作

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
  "involved_systems": ["订单系统", "支付系统"]
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
    "category": "STANDARD",
    "priority": "P1",
    "status": "DRAFT",
    "tag": "PLAN-20240322-001-STD-1711072800",
    "planned_start_time": "2024-03-25T10:00:00Z",
    "planned_end_time": "2024-03-25T18:00:00Z",
    "description": "本次上线包含订单模块优化、支付接口升级",
    "involved_systems": ["订单系统", "支付系统"],
    "progress": 0,
    "created_at": "2024-03-22T10:00:00Z",
    "message": "计划创建成功，已生成数据标签"
  }
}
```

---

#### GET /api/plans
获取计划列表

**请求参数**:
```json
{
  "page": 1,
  "per_page": 20,
  "category": "STANDARD",        // 可选：STANDARD/BUSINESS
  "status": "IN_PROGRESS",       // 可选：DRAFT/PENDING/IN_PROGRESS/COMPLETED
  "priority": "P1",              // 可选：P0/P1/P2/P3
  "keyword": "订单系统",          // 可选：搜索关键词
  "start_date": "2024-03-01",    // 可选：计划开始时间范围
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
        "tag": "PLAN-20240322-001-STD-1711072800",
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
    "priority": "P1",
    "status": "IN_PROGRESS",
    "planned_start_time": "2024-03-25T10:00:00Z",
    "planned_end_time": "2024-03-25T18:00:00Z",
    "actual_start_time": "2024-03-25T10:05:00Z",
    "actual_end_time": null,
    "description": "本次上线包含订单模块优化、支付接口升级",
    "involved_systems": ["订单系统", "支付系统"],
    "progress": 75,
    "tag": "PLAN-20240322-001-STD-1711072800",
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
    "workflow": {
      "id": "wf-001",
      "name": "标准上线检查流程",
      "status": "IN_PROGRESS",
      "progress": 75,
      "work_items": [
        {
          "id": "wi-001",
          "name": "服务对象台账收集",
          "status": "COMPLETED",
          "progress": 100,
          "sub_items": [
            {
              "id": "wi-001-01",
              "name": "应用系统台账表",
              "status": "COMPLETED",
              "verification_method": "manual",
              "has_criteria": true,
              "has_deliverable": true
            }
          ]
        }
      ]
    },
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

#### POST /api/plans/{id}/materials
上传审批材料

**请求体** (multipart/form-data):
```
file: [二进制文件]
material_type: "meeting_minutes"  // meeting_minutes/approval_email/screenshot/other
description: "3月20日上线评审会议纪要"
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
    "file_path": "/uploads/plans/plan-001/meeting.pdf",
    "description": "3月20日上线评审会议纪要",
    "uploaded_at": "2024-03-22T10:00:00Z",
    "message": "材料上传成功"
  }
}
```

---

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
      "delayed": 2
    },
    "charts": {
      "trend": {
        "dates": ["2024-03-01", "2024-03-02", ...],
        "created": [2, 3, ...],
        "completed": [1, 2, ...]
      },
      "category_distribution": [
        {"name": "标准上线", "value": 15},
        {"name": "业务变更", "value": 10}
      ],
      "priority_distribution": [
        {"name": "P0紧急", "value": 2},
        {"name": "P1高", "value": 8},
        {"name": "P2中", "value": 10},
        {"name": "P3低", "value": 5}
      ]
    },
    "recent_plans": [
      {
        "id": "plan-001",
        "plan_id": "PLAN-20240322-001",
        "name": "订单系统V2.0上线",
        "status": "IN_PROGRESS",
        "progress": 75,
        "planned_start_time": "2024-03-25T10:00:00Z"
      }
    ]
  }
}
```

---

## 3. 第二阶段：工作项拆解API

### 3.1 父工作项管理

#### POST /api/plans/{plan_id}/work-items
添加父工作项到计划

**请求体**:
```json
{
  "name": "服务对象台账收集",
  "work_item_type": "inventory",
  "description": "收集应用系统、云服务、账户等台账信息",
  "display_order": 1,
  "is_required": true
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "wi-001",
    "plan_id": "plan-001",
    "name": "服务对象台账收集",
    "work_item_type": "inventory",
    "work_item_level": "parent",
    "display_order": 1,
    "is_required": true,
    "status": "active",
    "created_at": "2024-03-22T10:00:00Z",
    "message": "父工作项添加成功"
  }
}
```

---

#### GET /api/plans/{plan_id}/work-items
获取计划的父工作项列表

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "wi-001",
        "name": "服务对象台账收集",
        "work_item_type": "inventory",
        "work_item_type_label": "台账收集",
        "description": "收集应用系统、云服务、账户等台账信息",
        "display_order": 1,
        "is_required": true,
        "sub_item_count": 3,
        "status": "active"
      },
      {
        "id": "wi-002",
        "name": "基础资源标准化交付",
        "work_item_type": "resource_delivery",
        "work_item_type_label": "资源交付",
        "description": "验证系统基线配置和软件标准化部署",
        "display_order": 2,
        "is_required": true,
        "sub_item_count": 2,
        "status": "active"
      }
    ]
  }
}
```

---

### 3.2 子工作项管理

#### POST /api/work-items/{parent_id}/sub-items
在父工作项下添加子工作项

**请求体**:
```json
{
  "name": "应用系统台账表",
  "description": "收集应用系统基本信息：IP、主机名、配置、用途等",
  "display_order": 1,
  "is_required": true,
  "estimated_duration": 60,
  "verification_method": "manual",
  "deliverable_types": ["excel"],
  "deliverable_desc": "应用系统台账表（Excel格式）"
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "wi-001-01",
    "parent_id": "wi-001",
    "name": "应用系统台账表",
    "work_item_level": "child",
    "display_order": 1,
    "is_required": true,
    "estimated_duration": 60,
    "verification_method": "manual",
    "deliverable_types": ["excel"],
    "deliverable_desc": "应用系统台账表（Excel格式）",
    "has_criteria": false,
    "created_at": "2024-03-22T10:00:00Z",
    "message": "子工作项添加成功"
  }
}
```

---

#### GET /api/work-items/{parent_id}/sub-items
获取父工作项下的子工作项列表

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "parent_work_item": {
      "id": "wi-001",
      "name": "服务对象台账收集",
      "work_item_type": "inventory"
    },
    "items": [
      {
        "id": "wi-001-01",
        "name": "应用系统台账表",
        "description": "收集应用系统基本信息",
        "display_order": 1,
        "is_required": true,
        "verification_method": "manual",
        "verification_method_label": "人工核验",
        "deliverable_types": ["excel"],
        "deliverable_desc": "应用系统台账表（Excel格式）",
        "has_criteria": true,
        "criteria_summary": "IP、主机名、配置等必填",
        "status": "active"
      },
      {
        "id": "wi-001-02",
        "name": "云服务开通台账表",
        "description": "收集云服务开通信息",
        "display_order": 2,
        "is_required": true,
        "verification_method": "manual",
        "verification_method_label": "人工核验",
        "deliverable_types": ["excel"],
        "deliverable_desc": "云服务开通台账表（Excel格式）",
        "has_criteria": false,
        "status": "active"
      }
    ]
  }
}
```

---

#### PUT /api/sub-work-items/{id}
更新子工作项

**请求体**:
```json
{
  "name": "应用系统台账表（更新）",
  "description": "更新后的描述",
  "verification_method": "script",
  "deliverable_types": ["excel", "pdf"]
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "wi-001-01",
    "message": "子工作项更新成功"
  }
}
```

---

#### DELETE /api/sub-work-items/{id}
删除子工作项

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "message": "子工作项删除成功"
  }
}
```

---

### 3.3 工作流编排

#### PUT /api/plans/{plan_id}/workflow
保存计划的工作流编排

**请求体**:
```json
{
  "work_items": [
    {
      "id": "wi-001",
      "display_order": 1
    },
    {
      "id": "wi-002",
      "display_order": 2
    }
  ],
  "dependencies": [
    {
      "work_item_id": "wi-002",
      "depends_on_id": "wi-001"
    }
  ]
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "plan_id": "plan-001",
    "workflow_id": "wf-001",
    "message": "工作流编排保存成功"
  }
}
```

---

## 4. 第三阶段：验收标准制定API

### 4.1 验收标准管理

#### POST /api/sub-work-items/{sub_work_item_id}/criteria
为子工作项制定验收标准

**请求体**:
```json
{
  "content": "应用系统台账表验收标准",
  "source": "preset_template",  // preset_template/knowledge/import/manual
  "source_id": "template-001",
  "verification_method": "manual",  // manual/script/ai
  "checklist_items": [
    {
      "id": "1",
      "content": "IP地址已填写",
      "required": true
    },
    {
      "id": "2",
      "content": "主机名已填写",
      "required": true
    },
    {
      "id": "3",
      "content": "配置信息已填写",
      "required": true
    }
  ],
  "deliverable_types": ["excel"],
  "deliverable_desc": "应用系统台账表（Excel格式），包含IP、主机名、配置、用途、所属系统、责任人、上线时间",
  "script_id": null,
  "ai_config": null
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "criteria-001",
    "sub_work_item_id": "wi-001-01",
    "content": "应用系统台账表验收标准",
    "verification_method": "manual",
    "checklist_items_count": 3,
    "created_at": "2024-03-22T10:00:00Z",
    "message": "验收标准制定成功"
  }
}
```

---

#### GET /api/sub-work-items/{sub_work_item_id}/criteria
获取子工作项的验收标准

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "criteria-001",
    "sub_work_item_id": "wi-001-01",
    "sub_work_item_name": "应用系统台账表",
    "parent_work_item_name": "服务对象台账收集",
    "content": "应用系统台账表验收标准",
    "source": "preset_template",
    "source_id": "template-001",
    "verification_method": "manual",
    "verification_method_label": "人工核验",
    "checklist_items": [
      {
        "id": "1",
        "content": "IP地址已填写",
        "required": true
      },
      {
        "id": "2",
        "content": "主机名已填写",
        "required": true
      }
    ],
    "deliverable_types": ["excel"],
    "deliverable_desc": "应用系统台账表（Excel格式）",
    "created_at": "2024-03-22T10:00:00Z",
    "updated_at": "2024-03-22T10:00:00Z"
  }
}
```

---

#### PUT /api/criteria/{id}
更新验收标准

**请求体**:
```json
{
  "content": "更新后的验收标准",
  "checklist_items": [
    {
      "id": "1",
      "content": "IP地址已填写",
      "required": true
    }
  ]
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "criteria-001",
    "message": "验收标准更新成功"
  }
}
```

---

### 4.2 验收标准来源

#### GET /api/criteria/templates
获取预置验收标准模板列表

**请求参数**:
```json
{
  "work_item_type": "inventory",  // 可选：按工作项类型筛选
  "keyword": "台账"               // 可选：搜索关键词
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "template-001",
        "name": "应用系统台账验收标准",
        "work_item_type": "inventory",
        "description": "应用系统台账表的标准验收要求",
        "checklist_items_count": 5,
        "applicable_sub_work_items": ["应用系统台账表"]
      },
      {
        "id": "template-002",
        "name": "云服务台账验收标准",
        "work_item_type": "inventory",
        "description": "云服务开通台账表的标准验收要求",
        "checklist_items_count": 4,
        "applicable_sub_work_items": ["云服务开通台账表"]
      }
    ]
  }
}
```

---

#### GET /api/criteria/templates/{id}
获取预置模板详情

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "template-001",
    "name": "应用系统台账验收标准",
    "work_item_type": "inventory",
    "description": "应用系统台账表的标准验收要求",
    "content": "应用系统台账表验收标准详细内容",
    "checklist_items": [
      {
        "id": "1",
        "content": "IP地址已填写",
        "required": true
      },
      {
        "id": "2",
        "content": "主机名已填写",
        "required": true
      }
    ],
    "verification_method": "manual",
    "deliverable_types": ["excel"],
    "deliverable_desc": "应用系统台账表（Excel格式）"
  }
}
```

---

#### POST /api/criteria/import
导入文档作为验收标准

**请求体** (multipart/form-data):
```
file: [二进制文件]
file_type: "markdown"  // markdown/word/excel
sub_work_item_id: "wi-001-01"
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "criteria_id": "criteria-002",
    "sub_work_item_id": "wi-001-01",
    "content": "从文档解析的验收标准内容",
    "parsed_checklist_items": [
      {
        "id": "1",
        "content": "解析的检查项1",
        "required": true
      }
    ],
    "message": "文档导入成功，已生成验收标准"
  }
}
```

---

#### GET /api/knowledge/items
从知识库选择验收标准

**请求参数**:
```json
{
  "category": "baseline",  // 可选：按分类筛选
  "keyword": "安全基线"     // 可选：搜索关键词
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": "knowledge-001",
        "title": "安全基线要求文档",
        "category": "baseline",
        "summary": "系统安全基线配置要求",
        "applicable_work_item_types": ["security_baseline"],
        "version": "v1.0",
        "updated_at": "2024-03-20T10:00:00Z"
      }
    ]
  }
}
```

---

## 5. 第四阶段：交付物管理API

### 5.1 交付物操作

#### POST /api/sub-work-items/{sub_work_item_id}/deliverables
上传交付物

**请求体** (multipart/form-data):
```
file: [二进制文件]
description: "应用系统台账表V1.0"
version: "1.0"
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "del-001",
    "sub_work_item_id": "wi-001-01",
    "sub_work_item_name": "应用系统台账表",
    "file_name": "应用系统台账表_订单系统.xlsx",
    "file_size": 102400,
    "file_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "file_path": "/uploads/deliverables/plan-001/wi-001-01/应用系统台账表.xlsx",
    "description": "应用系统台账表V1.0",
    "version": "1.0",
    "status": "uploaded",
    "uploaded_by": "user-002",
    "uploaded_at": "2024-03-22T10:00:00Z",
    "message": "交付物上传成功"
  }
}
```

---

#### GET /api/sub-work-items/{sub_work_item_id}/deliverables
获取子工作项的交付物列表

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "sub_work_item": {
      "id": "wi-001-01",
      "name": "应用系统台账表",
      "parent_work_item_name": "服务对象台账收集"
    },
    "items": [
      {
        "id": "del-001",
        "file_name": "应用系统台账表_订单系统.xlsx",
        "file_size": 102400,
        "file_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "description": "应用系统台账表V1.0",
        "version": "1.0",
        "status": "verified",
        "verification_result": "passed",
        "uploaded_by": "user-002",
        "uploaded_at": "2024-03-22T10:00:00Z"
      }
    ]
  }
}
```

---

#### GET /api/deliverables/{id}/download
下载交付物

**响应**: 文件流 (Content-Type: application/octet-stream)

---

#### DELETE /api/deliverables/{id}
删除交付物

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "message": "交付物删除成功"
  }
}
```

---

## 6. 第五阶段：核验执行API

### 6.1 核验触发与配置

#### POST /api/deliverables/{deliverable_id}/verify
触发核验

**请求体**:
```json
{
  "verification_method": "manual"  // manual/script/ai
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "verification_id": "ver-001",
    "deliverable_id": "del-001",
    "status": "pending",
    "message": "核验已触发，请等待结果"
  }
}
```

---

#### GET /api/verification-methods
获取可用的核验方式配置

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "methods": [
      {
        "type": "manual",
        "name": "人工核验",
        "description": "由运维管理者人工检查交付物",
        "applicable_scenarios": ["台账收集", "文档审核"]
      },
      {
        "type": "script",
        "name": "脚本核验",
        "description": "自动执行验证脚本进行检查",
        "applicable_scenarios": ["系统基线", "配置检查"],
        "requires_server_access": true
      },
      {
        "type": "ai",
        "name": "AI分析",
        "description": "使用AI自动分析交付物内容",
        "applicable_scenarios": ["报告分析", "文档解析"]
      }
    ]
  }
}
```

---

### 6.2 人工核验

#### POST /api/verification/manual
提交人工核验结果

**请求体**:
```json
{
  "deliverable_id": "del-001",
  "result": "passed",  // passed/failed/improvement
  "checklist_results": [
    {
      "checklist_item_id": "1",
      "result": "passed",
      "remark": "IP地址已正确填写"
    },
    {
      "checklist_item_id": "2",
      "result": "passed",
      "remark": "主机名已正确填写"
    }
  ],
  "evidence": "经检查，所有必填项已填写完整",
  "remark": "符合验收标准"
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "verification_id": "ver-001",
    "deliverable_id": "del-001",
    "result": "passed",
    "verified_by": "user-001",
    "verified_at": "2024-03-22T10:00:00Z",
    "message": "人工核验结果已提交"
  }
}
```

---

### 6.3 脚本核验

#### POST /api/verification/script
执行脚本核验

**请求体**:
```json
{
  "deliverable_id": "del-001",
  "script_id": "script-001",
  "target_host": "192.168.1.100",
  "target_port": 22,
  "username": "admin",
  "auth_type": "key",  // key/password
  "auth_credential": "ssh-private-key-content",
  "timeout": 300
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "verification_id": "ver-002",
    "deliverable_id": "del-001",
    "script_id": "script-001",
    "script_name": "系统基线检查脚本",
    "status": "running",
    "target_host": "192.168.1.100",
    "started_at": "2024-03-22T10:00:00Z",
    "message": "脚本核验已开始执行"
  }
}
```

---

#### GET /api/verification/{id}/status
查询脚本核验状态

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "verification_id": "ver-002",
    "status": "completed",
    "result": "passed",
    "execution_result": {
      "exit_code": 0,
      "stdout": "{\"result\": \"passed\", \"details\": [...]}",
      "stderr": "",
      "execution_duration_ms": 5230
    },
    "started_at": "2024-03-22T10:00:00Z",
    "completed_at": "2024-03-22T10:00:05Z"
  }
}
```

---

### 6.4 AI分析

#### POST /api/verification/ai
执行AI分析

**请求体**:
```json
{
  "deliverable_id": "del-001",
  "analysis_config": {
    "extract_fields": ["conclusion", "risk_level", "vulnerabilities"],
    "judgment_rules": {
      "conclusion_mapping": {
        "通过": "passed",
        "不通过": "failed"
      }
    }
  }
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "verification_id": "ver-003",
    "deliverable_id": "del-001",
    "status": "running",
    "analysis_type": "document_parsing",
    "started_at": "2024-03-22T10:00:00Z",
    "message": "AI分析已开始执行"
  }
}
```

---

#### GET /api/verification/{id}/ai-result
获取AI分析结果

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "verification_id": "ver-003",
    "status": "completed",
    "result": "passed",
    "ai_analysis_result": {
      "extracted_data": {
        "conclusion": "通过",
        "risk_level": "低",
        "vulnerabilities": 0,
        "suggestions": ["建议定期更新补丁"]
      },
      "confidence": 0.95,
      "analysis_summary": "安全扫描报告显示系统符合安全基线要求",
      "key_findings": ["未发现高危漏洞", "配置符合规范"],
      "risk_assessment": "低风险"
    },
    "started_at": "2024-03-22T10:00:00Z",
    "completed_at": "2024-03-22T10:00:30Z"
  }
}
```

---

### 6.5 核验结果查询

#### GET /api/sub-work-items/{sub_work_item_id}/result
获取子工作项的核验结果

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "sub_work_item": {
      "id": "wi-001-01",
      "name": "应用系统台账表",
      "parent_work_item_name": "服务对象台账收集"
    },
    "criteria": {
      "id": "criteria-001",
      "content": "应用系统台账表验收标准"
    },
    "deliverable": {
      "id": "del-001",
      "file_name": "应用系统台账表_订单系统.xlsx",
      "uploaded_at": "2024-03-22T10:00:00Z"
    },
    "verification": {
      "id": "ver-001",
      "method": "manual",
      "method_label": "人工核验",
      "result": "passed",
      "result_label": "通过",
      "checklist_results": [
        {
          "checklist_item_id": "1",
          "content": "IP地址已填写",
          "result": "passed",
          "remark": "IP地址已正确填写"
        },
        {
          "checklist_item_id": "2",
          "content": "主机名已填写",
          "result": "passed",
          "remark": "主机名已正确填写"
        }
      ],
      "evidence": "经检查，所有必填项已填写完整",
      "remark": "符合验收标准",
      "verified_by": "user-001",
      "verified_at": "2024-03-22T10:30:00Z"
    }
  }
}
```

---

## 7. 通用API

### 7.1 文件上传

#### POST /api/upload
通用文件上传接口

**请求体** (multipart/form-data):
```
file: [二进制文件]
file_type: "deliverable"  // deliverable/material/criteria
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "file_id": "file-001",
    "file_name": "example.xlsx",
    "file_size": 102400,
    "file_path": "/uploads/2024/03/example.xlsx",
    "file_url": "/api/files/file-001/download"
  }
}
```

---

### 7.2 数据字典

#### GET /api/dictionaries
获取系统数据字典

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "plan_categories": [
      {"value": "STANDARD", "label": "标准上线"},
      {"value": "BUSINESS", "label": "业务变更"}
    ],
    "plan_status": [
      {"value": "DRAFT", "label": "草稿"},
      {"value": "PENDING", "label": "待执行"},
      {"value": "IN_PROGRESS", "label": "执行中"},
      {"value": "COMPLETED", "label": "已完成"},
      {"value": "CANCELLED", "label": "已取消"}
    ],
    "priorities": [
      {"value": "P0", "label": "紧急", "color": "#ff4d4f"},
      {"value": "P1", "label": "高", "color": "#faad14"},
      {"value": "P2", "label": "中", "color": "#1890ff"},
      {"value": "P3", "label": "低", "color": "#52c41a"}
    ],
    "work_item_types": [
      {"value": "inventory", "label": "台账收集", "icon": "📊"},
      {"value": "resource_delivery", "label": "资源交付", "icon": "🏗️"},
      {"value": "security_baseline", "label": "安全基线", "icon": "🛡️"},
      {"value": "permission_handover", "label": "权限移交", "icon": "🔐"},
      {"value": "monitoring", "label": "监控告警", "icon": "📈"},
      {"value": "custom", "label": "自定义", "icon": "⚙️"}
    ],
    "verification_methods": [
      {"value": "manual", "label": "人工核验"},
      {"value": "script", "label": "脚本核验"},
      {"value": "ai", "label": "AI分析"}
    ],
    "verification_results": [
      {"value": "passed", "label": "通过", "color": "#52c41a"},
      {"value": "failed", "label": "不通过", "color": "#ff4d4f"},
      {"value": "improvement", "label": "待改进", "color": "#faad14"}
    ],
    "material_types": [
      {"value": "meeting_minutes", "label": "会议纪要"},
      {"value": "approval_email", "label": "审批邮件"},
      {"value": "screenshot", "label": "截图"},
      {"value": "other", "label": "其他"}
    ]
  }
}
```

---

## 8. 相关文档

- [PRD文档](./PRD.md)
- [数据模型设计](./data-model.md)
- [流程图文档](./flowcharts.md)
- [业务规则文档](./business-rules.md)
- [技术方案文档](./tech-spec.md)
