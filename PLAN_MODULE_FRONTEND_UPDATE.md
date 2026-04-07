# 计划管理模块前端开发总结

## 概述

根据后端优化后的接口，完成了计划管理模块前端页面的全面更新，支持多步骤计划创建流程和完整的计划详情展示。

## 主要更新内容

### 1. API 层更新

#### 新增接口 (`src/modules/plan/api/plan.js`)
- `getPlan(id)` - 获取计划基本信息
- `getPlanDetail(id)` - 获取计划详情（包含完整关联信息）
- `previewPlanChanges(data)` - 预览计划变更
- `getInventoryList(params)` - 获取台账列表
- `getAppModules(appId)` - 获取应用系统的功能模块

#### 类型定义更新 (`src/modules/plan/api/types.js`)
- 新增 `ModuleAction` - 功能模块操作类型（create/update/delete）
- 新增 `moduleActionOptions` - 操作类型选项配置
- 新增 `PlanCreationSteps` - 计划创建步骤配置
- 新增辅助函数：`getInventoryActionType`, `requiresInventorySelection`, `allowMultipleInventory`

### 2. Store 层更新 (`src/modules/plan/store/planStore.js`)

#### 新增状态
- `creationStep` - 当前创建步骤
- `creationData` - 创建表单数据
  - `basicInfo` - 基本信息
  - `approvalFiles` - 审批材料
  - `affectedModules` - 受影响功能模块
  - `relatedInventoryIds` - 关联台账ID
- `previewData` - 预览数据
- `inventoryList` - 台账列表
- `appModules` - 应用模块列表

#### 新增 Actions
- `setCreationStep` - 设置创建步骤
- `resetCreationStep` - 重置创建状态
- `setCreationData` - 更新创建数据
- `addApprovalFile` / `removeApprovalFile` - 审批文件管理
- `addAffectedModule` / `updateAffectedModule` / `removeAffectedModule` - 模块管理
- `setRelatedInventoryIds` - 设置关联台账
- `fetchGeneratedPlanId` - 获取预生成的PlanID
- `fetchPreviewChanges` - 获取变更预览
- `fetchInventoryList` - 获取台账列表
- `fetchAppModules` - 获取应用模块

### 3. 组件层更新

#### 新建多步骤表单组件 (`src/modules/plan/components/PlanStepsForm/`)

**BasicInfoStep.jsx** - 基本信息步骤
- 计划名称输入
- 计划分类选择
- 优先级选择（P0-P3）
- 计划开始/结束时间
- 计划说明

**ApprovalFilesStep.jsx** - 审批材料步骤
- 拖拽上传组件
- 文件大小限制（20MB）
- 文件类型限制（PDF、图片）
- 已上传文件列表展示
- 文件删除功能

**InventoryScopeStep.jsx** - 涉及范围步骤（核心）
- 根据计划分类动态展示不同界面
- 应用系统选择（单选/多选）
- 功能模块管理（新增/编辑/删除）
- 版本变更记录

**PreviewStep.jsx** - 预览确认步骤
- 计划信息摘要
- 台账变更摘要
- 生命周期日志预览
- 工作流检查项预览
- 审批材料确认

**index.jsx** - 步骤表单容器
- 步骤导航
- 数据校验
- 步骤切换逻辑
- 最终提交

### 4. 视图层更新

#### PlanListView.jsx - 计划列表页
**新增展示字段：**
- PlanID 显示
- 数据标签显示
- 关联信息统计（应用系统数、功能模块数）
- 图标化展示关联数量

#### PlanDetailView.jsx - 计划详情页
**新增 Tabs：**
1. **概览 Tab**
   - 基本信息展示
   - 统计信息卡片（关联应用、功能模块、审批材料数量）

2. **台账范围 Tab**
   - 关联应用系统列表
   - 影响功能模块表格

3. **生命周期 Tab**（新增）
   - 时间线展示
   - 日志类型标签
   - 操作人信息

4. **审批材料 Tab**
   - 文件列表展示
   - 文件大小和上传时间

5. **工作流 Tab**（预留）
   - 模板类型
   - 进度展示
   - 检查项列表

#### PlanCreateView.jsx - 计划创建页
- 使用新的多步骤表单
- 页面加载时重置创建状态

### 5. 路由配置

路由保持不变，支持以下路径：
- `/plans` - 计划列表
- `/plans/create` - 创建计划
- `/plans/:id` - 计划详情
- `/plans/:id/edit` - 编辑计划

## 业务流程

### 创建计划流程（4步骤）

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Step 1     │ -> │  Step 2     │ -> │  Step 3     │ -> │  Step 4     │
│  基本信息   │    │  审批材料   │    │  涉及范围   │    │  预览确认   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
     │                   │                   │                   │
     ▼                   ▼                   ▼                   ▼
• 计划名称           • 文件上传          • 应用系统选择      • 信息摘要
• 计划分类           • 文件列表          • 功能模块管理      • 变更预览
• 优先级             • 文件删除          • 版本变更记录      • 日志预览
• 执行时间                                                  • 提交创建
• 计划说明
```

### Step 3 根据分类的差异化展示

| 分类 | 应用系统选择 | 功能模块管理 |
|-----|-------------|-------------|
| new_system | ❌ 不需要 | ✅ 添加新模块 |
| new_feature | ✅ 单选 | ✅ 添加新模块 |
| func_change | ✅ 多选 | ✅ 选择/编辑现有模块 |
| arch_change | ✅ 多选 | ❌ 不管理模块 |
| security_check | ❌ 不需要 | ❌ 不需要 |

## 与后端接口对应

### API 端点映射

| 前端 API 函数 | 后端端点 | 说明 |
|-------------|---------|------|
| `createPlan` | `POST /api/plans` | 创建计划 |
| `getPlanList` | `GET /api/plans` | 计划列表 |
| `getPlan` | `GET /api/plans/:id` | 计划基本信息 |
| `getPlanDetail` | `GET /api/plans/:id/detail` | 计划详情（完整） |
| `updatePlan` | `PUT /api/plans/:id` | 更新计划 |
| `deletePlan` | `DELETE /api/plans/:id` | 删除计划 |
| `startPlan` | `POST /api/plans/:id/start` | 启动计划 |
| `completePlan` | `POST /api/plans/:id/complete` | 完成计划 |
| `cancelPlan` | `POST /api/plans/:id/cancel` | 取消计划 |
| `linkInventory` | `POST /api/plans/:id/inventory` | 关联台账 |
| `generatePlanId` | `GET /api/plans/generate-id` | 预生成PlanID |
| `previewPlanChanges` | `POST /api/plans/preview` | 预览变更 |

## 文件结构

```
src/modules/plan/
├── api/
│   ├── index.js          # API 入口
│   ├── plan.js           # 计划相关接口
│   └── types.js          # 类型定义
├── components/
│   ├── PlanCard/         # 计划卡片组件
│   ├── PlanForm/         # 计划表单组件
│   ├── PlanStatusBadge/  # 状态徽章组件
│   └── PlanStepsForm/    # 多步骤表单（新增）
│       ├── index.jsx     # 表单容器
│       ├── BasicInfoStep.jsx
│       ├── ApprovalFilesStep.jsx
│       ├── InventoryScopeStep.jsx
│       └── PreviewStep.jsx
├── store/
│   └── planStore.js      # 状态管理
├── views/
│   ├── PlanListView/     # 列表页
│   ├── PlanCreateView/   # 创建页
│   ├── PlanEditView/     # 编辑页
│   └── PlanDetailView/   # 详情页
├── router.jsx            # 路由配置
└── index.js              # 模块入口
```

## 依赖说明

- **React 18** - 核心框架
- **React Router 6** - 路由管理
- **Ant Design 5** - UI组件库
- **Zustand** - 状态管理
- **Axios** - HTTP客户端

## 运行验证

```bash
# 构建项目
cd /CRTAssistant_demo/frontend
npm run build

# 开发模式
npm run dev
```

构建成功输出：
```
vite v5.4.21 building for production...
✓ 3165 modules transformed.
✓ built in 3.65s
```

## 后续扩展建议

1. **P0计划二次确认** - 添加审批流程弹窗
2. **时间冲突检测** - 在同一应用系统同时段多计划时给出警告
3. **台账搜索优化** - 支持模糊搜索和分页加载
4. **模块树形选择** - 支持层级结构的模块选择
5. **文件预览** - 支持PDF和图片的在线预览
6. **批量操作** - 计划列表支持批量启动/取消

---

**更新日期**: 2026-03-30
**前端版本**: v2.0 (优化版)
