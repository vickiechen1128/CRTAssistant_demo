# 仿真运维经理 - API 设计文档

| 版本 | 日期 | 作者 | 变更说明 |
|-----|------|-----|---------|
| v0.1 | 2024-03-20 | CRT | 初稿，核心API定义 |

## 1. 接口概览

### 1.1 模块划分

| 模块 | 基础路径 | 描述 |
|-----|---------|------|
| 认证 | /api/auth | 登录、登出、Token刷新 |
| 用户 | /api/users | 用户管理 |
| 准入任务 | /api/admission-tasks | 准入检查任务CRUD |
| 检查清单 | /api/checklist-items | 检查项管理 |
| 台账 | /api/inventories | 台账管理（含三类明细） |
| 交付物 | /api/deliverables | 文件上传下载 |
| 验证脚本 | /api/verification-scripts | 脚本管理 |
| 验证执行 | /api/verification-execute | 脚本执行和结果查询 |
| 仪表盘 | /api/dashboard | 统计数据 |
| 模板 | /api/templates | 检查清单模板 |

### 1.2 接口列表

| 方法 | 路径 | 描述 | 状态 |
|-----|------|------|-----|
| POST | /api/auth/login | 用户登录 | 待实现 |
| POST | /api/auth/logout | 用户登出 | 待实现 |
| GET | /api/auth/me | 获取当前用户信息 | 待实现 |
| GET | /api/users | 用户列表 | 待实现 |
| GET | /api/admission-tasks | 准入任务列表 | 待实现 |
| POST | /api/admission-tasks | 创建准入任务 | 待实现 |
| GET | /api/admission-tasks/{id} | 获取任务详情 | 待实现 |
| PUT | /api/admission-tasks/{id} | 更新任务 | 待实现 |
| POST | /api/admission-tasks/{id}/start | 启动任务 | 待实现 |
| POST | /api/admission-tasks/{id}/submit | 提交审核 | 待实现 |
| GET | /api/checklist-items | 检查项列表 | 待实现 |
| PUT | /api/checklist-items/{id} | 更新检查项 | 待实现 |
| POST | /api/checklist-items/{id}/verify | 确认检查项 | 待实现 |
| GET | /api/inventories | 台账列表 | 待实现 |
| POST | /api/inventories | 创建台账 | 待实现 |
| GET | /api/inventories/{id} | 获取台账详情 | 待实现 |
| PUT | /api/inventories/{id} | 更新台账 | 待实现 |
| POST | /api/inventories/{id}/submit | 提交台账审核 | 待实现 |
| POST | /api/inventories/{id}/confirm | 确认台账 | 待实现 |
| POST | /api/deliverables | 上传交付物 | 待实现 |
| GET | /api/deliverables/{id} | 下载交付物 | 待实现 |
| DELETE | /api/deliverables/{id} | 删除交付物 | 待实现 |
| GET | /api/verification-scripts | 脚本列表 | 待实现 |
| POST | /api/verification-scripts | 创建脚本 | 待实现 |
| GET | /api/verification-scripts/{id} | 获取脚本详情 | 待实现 |
| POST | /api/verification-execute | 执行验证脚本 | 待实现 |
| GET | /api/verification-execute/{id} | 获取执行结果 | 待实现 |
| GET | /api/dashboard/overview | 仪表盘概览 | 待实现 |
| GET | /api/dashboard/tasks | 任务统计 | 待实现 |
| GET | /api/templates | 模板列表 | 待实现 |
| GET | /api/templates/{id} | 获取模板详情 | 待实现 |

## 2. 详细定义

### 2.1 认证模块

#### POST /api/auth/login
用户登录

**请求**:
```json
{
  "username": "string, required",
  "password": "string, required"
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "username": "zhangsan",
      "real_name": "张三",
      "role": "ops_manager"
    }
  }
}
```

#### GET /api/auth/me
获取当前登录用户信息

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "username": "zhangsan",
    "email": "zhangsan@company.com",
    "real_name": "张三",
    "role": "ops_manager",
    "department": "运维部"
  }
}
```

---

### 2.2 准入任务模块

#### GET /api/admission-tasks
获取准入任务列表

**请求参数**:
| 参数名 | 位置 | 类型 | 必填 | 说明 | 示例 |
|-------|-----|------|-----|------|------|
| page | query | integer | 否 | 页码 | 1 |
| per_page | query | integer | 否 | 每页条数 | 20 |
| status | query | string | 否 | 状态筛选 | in_progress |
| system_name | query | string | 否 | 系统名称搜索 | 订单 |

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": 1,
        "task_no": "ADM202403200001",
        "system_name": "订单管理系统",
        "system_code": "ORDER_SYS",
        "version": "v2.1.0",
        "release_date": "2024-04-01",
        "status": "in_progress",
        "progress": 75,
        "creator": {
          "id": 1,
          "real_name": "张三"
        },
        "manager": {
          "id": 2,
          "real_name": "李四"
        },
        "created_at": "2024-03-20T10:00:00Z",
        "updated_at": "2024-03-20T15:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 50,
      "total_pages": 3
    }
  }
}
```

#### POST /api/admission-tasks
创建准入任务

**请求体**:
```json
{
  "system_name": "订单管理系统",
  "system_code": "ORDER_SYS",
  "version": "v2.1.0",
  "release_date": "2024-04-01",
  "manager_id": 2,
  "template_id": 1,
  "remark": "紧急上线任务"
}
```

**响应成功** (201):
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "task_no": "ADM202403200001",
    "system_name": "订单管理系统",
    "status": "draft",
    "progress": 0,
    "created_at": "2024-03-20T10:00:00Z"
  }
}
```

#### GET /api/admission-tasks/{id}
获取任务详情（含检查项、台账、进度）

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "task_no": "ADM202403200001",
    "system_name": "订单管理系统",
    "status": "in_progress",
    "progress": 75,
    "checklist_summary": {
      "total": 20,
      "pending": 2,
      "in_progress": 3,
      "passed": 15,
      "rejected": 0
    },
    "control_dimension_progress": {
      "inventory": {"total": 3, "completed": 3},
      "baseline": {"total": 5, "completed": 4},
      "deployment": {"total": 4, "completed": 2},
      "security": {"total": 4, "completed": 0},
      "monitoring": {"total": 4, "completed": 0}
    },
    "checklist_items": [...],
    "inventories": [...],
    "created_at": "2024-03-20T10:00:00Z"
  }
}
```

---

### 2.3 检查清单模块

#### GET /api/checklist-items
获取检查项列表

**请求参数**:
| 参数名 | 位置 | 类型 | 必填 | 说明 | 示例 |
|-------|-----|------|-----|------|------|
| task_id | query | integer | 是 | 任务ID | 1 |
| control_dimension | query | string | 否 | 管控维度 | baseline |
| status | query | string | 否 | 状态 | pending |

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": 1,
        "control_dimension": "baseline",
        "category": "系统账户安全",
        "item_name": "系统账户安全基线检查",
        "description": "检查系统账户是否符合基线要求",
        "acceptance_criteria": "1.禁用root远程登录 2.密码复杂度要求...",
        "status": "pending_review",
        "assignee": {
          "id": 3,
          "real_name": "王五"
        },
        "verifier": null,
        "due_date": "2024-03-25",
        "deliverables_count": 2,
        "verification_method": "script",
        "sort_order": 1
      }
    ]
  }
}
```

#### PUT /api/checklist-items/{id}
更新检查项（分配责任人、修改截止日期等）

**请求体**:
```json
{
  "assignee_id": 3,
  "due_date": "2024-03-25",
  "remark": "请优先处理"
}
```

#### POST /api/checklist-items/{id}/verify
确认检查项完成

**请求体**:
```json
{
  "status": "passed",
  "remark": "验证通过，符合基线要求"
}
```

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "status": "passed",
    "verifier": {
      "id": 2,
      "real_name": "李四"
    },
    "verified_at": "2024-03-20T16:00:00Z"
  }
}
```

---

### 2.4 台账模块

#### POST /api/inventories
创建台账（含明细数据）

**请求体**:
```json
{
  "task_id": 1,
  "inventory_type": "server",
  "servers": [
    {
      "ip_address": "192.168.1.100",
      "hostname": "order-app-01",
      "os_type": "CentOS 7.9",
      "cpu_cores": 8,
      "memory_gb": 32,
      "purpose": "订单服务应用服务器",
      "responsible_person": "李四",
      "online_date": "2024-04-01"
    }
  ]
}
```

#### GET /api/inventories/{id}
获取台账详情

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "task_id": 1,
    "inventory_type": "server",
    "status": "confirmed",
    "servers": [
      {
        "id": 1,
        "ip_address": "192.168.1.100",
        "hostname": "order-app-01",
        "os_type": "CentOS 7.9",
        "cpu_cores": 8,
        "memory_gb": 32,
        "disk_gb": 500,
        "purpose": "订单服务应用服务器",
        "system_belong": "订单管理系统",
        "environment": "production",
        "responsible_person": "李四",
        "online_date": "2024-04-01",
        "status": "active"
      }
    ],
    "submitted_by": {
      "id": 3,
      "real_name": "王五"
    },
    "submitted_at": "2024-03-20T14:00:00Z",
    "confirmed_by": {
      "id": 2,
      "real_name": "李四"
    },
    "confirmed_at": "2024-03-20T15:00:00Z"
  }
}
```

#### POST /api/inventories/{id}/submit
提交台账审核

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "status": "submitted",
    "submitted_at": "2024-03-20T14:00:00Z"
  }
}
```

---

### 2.5 交付物模块

#### POST /api/deliverables
上传交付物

**请求**: `multipart/form-data`
| 字段名 | 类型 | 必填 | 说明 |
|-------|-----|-----|------|
| checklist_item_id | integer | 是 | 关联检查项ID |
| file | File | 是 | 文件 |
| description | string | 否 | 文件描述 |

**响应成功** (201):
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "file_name": "系统基线配置手册.pdf",
    "file_type": "pdf",
    "file_size": 1024000,
    "file_path": "/uploads/2024/03/xxx.pdf",
    "description": "系统基线配置操作手册",
    "uploaded_at": "2024-03-20T14:30:00Z",
    "uploader": {
      "id": 3,
      "real_name": "王五"
    }
  }
}
```

#### GET /api/deliverables/{id}
下载交付物

**响应**: 文件流，Content-Type 根据文件类型

---

### 2.6 验证执行模块

#### POST /api/verification-execute
执行验证脚本

**请求体**:
```json
{
  "checklist_item_id": 5,
  "script_id": 1,
  "target_server": "192.168.1.100",
  "parameters": {
    "timeout": 300
  }
}
```

**响应成功** (202 - 异步执行):
```json
{
  "code": 0,
  "data": {
    "execution_id": "exec_20240320160000",
    "status": "running",
    "message": "脚本正在执行中，请稍后查询结果"
  }
}
```

#### GET /api/verification-execute/{execution_id}
获取执行结果

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "id": "exec_20240320160000",
    "task_id": 1,
    "checklist_item_id": 5,
    "script_id": 1,
    "target_server": "192.168.1.100",
    "executor": {
      "id": 2,
      "real_name": "李四"
    },
    "status": "success",
    "started_at": "2024-03-20T16:00:00Z",
    "completed_at": "2024-03-20T16:00:45Z",
    "duration_seconds": 45,
    "result_summary": {
      "total": 11,
      "passed": 8,
      "failed": 2,
      "warning": 1
    },
    "result_detail": [
      {
        "check_item": "root远程登录",
        "expected": "已禁用",
        "actual": "已禁用",
        "status": "passed"
      },
      {
        "check_item": "密码复杂度",
        "expected": "8位以上，包含大小写和数字",
        "actual": "6位数字",
        "status": "failed",
        "suggestion": "修改/etc/security/pwquality.conf配置"
      }
    ],
    "output_log": "脚本执行输出的原始日志内容..."
  }
}
```

---

### 2.7 仪表盘模块

#### GET /api/dashboard/overview
获取仪表盘概览数据

**响应成功** (200):
```json
{
  "code": 0,
  "data": {
    "task_stats": {
      "total": 50,
      "in_progress": 10,
      "pending_review": 5,
      "passed": 30,
      "rejected": 5
    },
    "my_tasks": {
      "assigned": 5,
      "overdue": 2,
      "pending_verify": 3
    },
    "recent_activities": [
      {
        "type": "task_created",
        "content": "张三创建了订单管理系统准入任务",
        "time": "2024-03-20T10:00:00Z"
      }
    ],
    "control_dimension_stats": {
      "inventory": {"total": 15, "completed": 12},
      "baseline": {"total": 25, "completed": 18},
      "deployment": {"total": 20, "completed": 10}
    }
  }
}
```

---

## 3. 通用响应格式

### 成功响应

```json
{
  "code": 0,
  "data": {},
  "message": "success"
}
```

### 错误响应

```json
{
  "code": 4001,
  "message": "参数错误：缺少必填字段",
  "details": {
    "field": "system_name",
    "error": "required"
  }
}
```

**错误码定义**:

| 错误码 | 说明 | 场景 |
|-------|------|-----|
| 0 | 成功 | - |
| 4000 | 请求参数错误 | 参数格式不正确 |
| 4001 | 缺少必填参数 | 必填字段未提供 |
| 4002 | 参数值非法 | 参数值超出范围 |
| 4010 | 未授权 | 未登录或Token过期 |
| 4030 | 权限不足 | 无操作权限 |
| 4040 | 资源不存在 | 查询的ID不存在 |
| 4090 | 资源冲突 | 重复创建或状态冲突 |
| 5000 | 服务器内部错误 | 系统异常 |
| 5001 | 脚本执行失败 | 验证脚本执行出错 |

## 4. 认证与授权

### 认证方式
- **类型**: JWT (JSON Web Token)
- **Header**: `Authorization: Bearer <token>`
- **Token有效期**: 2小时
- **刷新机制**: 支持refresh_token刷新

### 权限控制

| 角色 | 权限说明 |
|-----|---------|
| ops_manager | 运维经理，全部权限 |
| admin | 系统管理员，用户和模板管理 |
| developer | 开发人员，填写台账、上传交付物 |
| security | 安全人员，审核安全相关检查项 |
| viewer | 只读用户，查看任务和进度 |

### 数据权限
- 运维经理：可见全部任务
- 开发人员：仅可见被分配的任务和检查项
- 安全人员：可见所有任务的安检检查项
