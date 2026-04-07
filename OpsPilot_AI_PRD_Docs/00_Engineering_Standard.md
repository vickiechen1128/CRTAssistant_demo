# 赛领OpsPilot管理平台 - 工程实现标准

> **AI编程助手必读**：本文档包含编码前必须了解的目录结构、路由规范、关键实现片段和避坑指南。

---

## 1. 项目目录结构

### 1.1 后端 (backend/)
```
app/
├── main.py              # FastAPI入口
├── config.py            # 配置管理
├── database.py          # 数据库连接
├── models/              # SQLAlchemy模型
│   ├── user.py
│   ├── admission_task.py
│   ├── checklist.py
│   ├── inventory.py
│   ├── deliverable.py
│   ├── verification.py
│   ├── workflow.py
│   ├── work_item.py
│   └── workflow_instance.py
├── schemas/             # Pydantic模型
├── routers/             # API路由
│   ├── auth.py
│   ├── users.py
│   ├── admission_tasks.py
│   ├── checklist_items.py
│   ├── inventories.py
│   ├── deliverables.py
│   ├── verification_scripts.py
│   ├── verification_execute.py
│   ├── workflows.py
│   ├── work_items.py
│   ├── workflow_instances.py
│   ├── dashboard.py
│   └── templates.py
├── services/            # 业务逻辑
├── core/                # 安全/权限/异常
└── utils/               # 工具函数
```

### 1.2 前端 (frontend/src/)
```
├── api/                 # API客户端
│   ├── index.js         # axios实例
│   ├── auth.js
│   ├── tasks.js
│   ├── checklist.js
│   ├── inventory.js
│   ├── deliverable.js
│   ├── verification.js
│   ├── workflow.js
│   └── dashboard.js
├── stores/              # Zustand状态管理
├── components/
│   ├── Layout/
│   │   └── MainLayout.jsx    # 主布局(含侧边栏)
│   ├── Common/          # 通用组件
│   └── Business/        # 业务组件
│       ├── Workflow/
│       │   ├── WorkflowDesigner.jsx
│       │   ├── WorkflowProgress.jsx
│       │   ├── WorkItemCard.jsx
│       │   ├── WorkItemList.jsx
│       │   ├── AcceptanceCriteriaForm.jsx
│       │   └── WorkItemVerification.jsx
│       └── Progress/
├── pages/               # 页面组件
│   ├── Login/
│   ├── Dashboard/
│   ├── AdmissionTasks/
│   ├── Inventories/
│   ├── Verification/
│   └── Settings/
├── hooks/               # 自定义Hooks
└── utils/               # 工具函数
```

---

## 2. 前端路由表

| 路由 | 组件 | 权限 |
|-----|------|------|
| `/login` | Login | 公开 |
| `/` | Dashboard | 需登录 |
| `/admission-tasks` | TaskList | 需登录 |
| `/admission-tasks/new` | CreateTask | 需登录 |
| `/admission-tasks/:id` | TaskDetail | 需登录 |
| `/inventories/task/:taskId` | Inventories | 需登录 |
| `/inventories/server` | ServerInventoryList | 需登录 |
| `/inventories/cloud` | CloudInventoryList | 需登录 |
| `/inventories/account` | AccountInventoryList | 需登录 |
| `/workflows` | WorkflowList | 需登录 |
| `/workflows/new` | WorkflowCreate | 需登录 |
| `/workflows/:id` | WorkflowDetail | 需登录 |
| `/workflows/:id/edit` | WorkflowEdit | 需登录 |
| `/workflow-instances/:id` | WorkflowInstanceDetail | 需登录 |

### 侧边栏菜单
```javascript
const menuItems = [
  { key: '/', label: '仪表盘' },
  { key: '/admission-tasks', label: '准入任务' },
  {
    key: 'workflows',
    label: '工作流管理',
    children: [
      { key: '/workflows', label: '工作流模板' },
      { key: '/workflow-instances', label: '工作流实例' },
    ]
  },
  {
    key: 'inventories',
    label: '台账管理',
    children: [
      { key: '/inventories/server', label: '应用系统台账' },
      { key: '/inventories/cloud', label: '云服务台账' },
      { key: '/inventories/account', label: '系统账户台账' },
    ]
  },
  {
    key: 'verification',
    label: '验证管理',
    children: [
      { key: '/verification/scripts', label: '验证脚本' },
      { key: '/verification/records', label: '验证记录' },
    ]
  },
  { key: '/settings', label: '系统设置' },
];
```

---

## 3. 关键实现片段

### 3.1 密码安全 (bcrypt)
```python
import bcrypt

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
```

### 3.2 数据库索引策略
```python
# admission_tasks
Index('idx_task_status', 'status')
Index('idx_task_release_date', 'release_date')

# checklist_items
Index('idx_item_task', 'task_id')
Index('idx_item_status', 'status')
Index('idx_item_assignee', 'assignee_id')

# inventory_accounts
Index('idx_account_inventory', 'inventory_id')
Index('idx_account_valid', 'valid_until')
```

### 3.3 JWT Token结构
```json
{
  "sub": "1",
  "username": "zhangsan",
  "role": "ops_manager",
  "iat": 1700000000,
  "exp": 1700003600
}
```
- Access Token: 2小时有效期
- Refresh Token: 7天有效期

### 3.4 Zustand状态管理模板
```javascript
// stores/workflowStore.js
const useWorkflowStore = create((set, get) => ({
  workflows: [],
  currentWorkflow: null,
  instances: [],
  currentInstance: null,
  progress: null,
  
  fetchWorkflows: async (params) => {...},
  createWorkflow: async (data) => {...},
  updateWorkflow: async (id, data) => {...},
  deleteWorkflow: async (id) => {...},
  fetchInstances: async (workflowId) => {...},
  createInstance: async (workflowId, taskId) => {...},
  executeWorkItem: async (instanceId, workItemId) => {...},
  verifyWorkItem: async (instanceId, workItemId, data) => {...},
  fetchProgress: async (instanceId) => {...},
}));
```

---

## 4. 避坑指南

### 4.1 路由管理规范

#### 4.1.1 路由路径格式
**强制规则**: 所有路由路径必须以 `/` 开头（绝对路径）
```jsx
// ❌ 错误 - 相对路径
{ path: 'sop-templates', element: <SOPTemplateList /> }

// ✅ 正确 - 绝对路径
{ path: '/sop-templates', element: <SOPTemplateList /> }
```

#### 4.1.2 路由配置检查清单
新增页面时必须完成以下检查：
- [ ] 页面组件已创建
- [ ] 路由配置已添加（router.jsx）
- [ ] 导航代码中的路径与路由配置一致
- [ ] 路径以 `/` 开头
- [ ] 动态参数使用 `:id` 格式

#### 4.1.3 路由冲突
**问题**: `/:id` 与 `/new` 冲突，访问 `/new` 被解析为 `id="new"`

**解决**: 静态路由放动态路由之前
```jsx
<Route path="/admission-tasks/new" element={<CreateTask />} />
<Route path="/admission-tasks/:id" element={<TaskDetail />} />
```

### 4.2 前后端数据契约规范

#### 4.2.1 API 数据格式对齐
**强制规则**: 前端提交数据必须与后端 Schema 完全一致

**后端 Schema 定义**（以 Plan 为例）：
```python
class CreatePlanSchema(BaseModel):
    name: str
    category: str
    priority: str
    description: Optional[str]
    planned_start_time: Optional[datetime]
    planned_end_time: Optional[datetime]
```

**前端数据组装**（必须对齐）：
```javascript
// ✅ 正确 - 扁平化结构，字段名一致
const submitData = {
  name: values.name,
  category: values.category,
  priority: values.priority,
  description: values.description,
  planned_start_time: values.planned_start_time?.toISOString(),
  planned_end_time: values.planned_end_time?.toISOString(),
};

// ❌ 错误 - 嵌套结构，字段名不一致
const submitData = {
  basic_info: { name, category, ... },  // 后端不识别
  approval_files: [...],                // 后端不识别
};
```

#### 4.2.2 新增 API 接口检查清单
- [ ] 后端已定义 Pydantic Schema
- [ ] 前端已确认 Schema 字段和类型
- [ ] 前端提交数据结构与 Schema 一致
- [ ] 日期时间字段使用 ISO 8601 格式
- [ ] 枚举值与后端定义完全一致

### 4.3 文件上传安全
- 白名单: .xlsx, .xls, .doc, .docx, .pdf, .txt, .sh, .py
- 大小限制: 50MB
- 存储路径: `uploads/2024/03/20/xxx.pdf` (按日期分目录，Hash命名)

### 4.4 脚本执行
- 异步执行（Celery）
- 默认超时: 300秒
- SSH失败自动重试3次
- 使用只读用户执行检查脚本

### 4.5 常见 HTTP 状态码处理规范

| 状态码 | 含义 | 前端处理 |
|-------|------|---------|
| 400 | 请求参数错误 | 显示具体字段错误提示 |
| 422 | 验证失败 | 根据后端返回的 detail 显示错误 |
| 404 | 资源不存在 | 检查路由配置或资源ID |
| 500 | 服务器错误 | 提示用户稍后重试，记录日志 |

---

## 5. 技术选型

| 层级 | 技术 |
|-----|------|
| 后端框架 | FastAPI |
| 数据库 | SQLite (MVP阶段) |
| 前端框架 | React + Vite |
| UI组件 | Ant Design |
| 状态管理 | Zustand |
| 样式 | Tailwind CSS |
| 任务队列 | Celery |
| 缓存 | Redis |

---

## 6. 工作流模块组件清单

| 组件 | 路径 |
|-----|------|
| WorkflowDesigner | `components/Business/Workflow/WorkflowDesigner.jsx` |
| WorkflowProgress | `components/Business/Workflow/WorkflowProgress.jsx` |
| WorkItemCard | `components/Business/Workflow/WorkItemCard.jsx` |
| WorkItemList | `components/Business/Workflow/WorkItemList.jsx` |
| AcceptanceCriteriaForm | `components/Business/Workflow/AcceptanceCriteriaForm.jsx` |
| WorkItemVerification | `components/Business/Workflow/WorkItemVerification.jsx` |
| ProgressRing | `components/Progress/ProgressRing.jsx` |
| ProgressTimeline | `components/Progress/ProgressTimeline.jsx` |
