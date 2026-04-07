# 台账列表选择报错修复总结

## 问题描述

在计划创建第三步"选择涉及范围"时，控制台报错：
```
TypeError: inventoryList.map is not a function
    at InventoryScopeStep
```

## 问题原因

1. **后端响应格式不一致**：后端返回的分页数据格式为 `{ data: [...] }`，而前端期望的是 `{ items: [...] }`
2. **前端缺乏空值检查**：`inventoryList` 可能为 `undefined` 或非数组类型

## 修复内容

### 1. 后端修复

#### 新建文件：`app/core/response.py`
统一 API 响应格式工具：
```python
{
  "success": true,
  "message": "Success",
  "data": { ... },
  "error": null
}
```

#### 更新文件：`app/modules/inventory/interfaces/api/routes/inventory_routes.py`
- 导入响应工具：`from app.core.response import success_response, error_response`
- 修改 `list_applications` 接口，使用统一响应格式
- 返回数据字段改为 `items` 而非 `data`（与前端约定一致）

**修改前：**
```python
return {
    "page": result.page,
    "size": result.size,
    "total": result.total,
    "total_pages": result.total_pages,
    "data": result.data
}
```

**修改后：**
```python
return success_response({
    "page": result.page,
    "size": result.size,
    "total": result.total,
    "total_pages": result.total_pages,
    "items": result.data
})
```

### 2. 前端修复

#### 更新文件：`src/modules/plan/components/PlanStepsForm/InventoryScopeStep.jsx`
- 添加数组类型检查：`Array.isArray(inventoryList) && inventoryList.map(...)`

#### 更新文件：`src/modules/plan/store/planStore.js`
- 简化数据处理逻辑：`const list = result?.items || [];`

## 响应格式变更

### 后端响应格式（修复后）
```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "items": [...],
    "page": 1,
    "size": 20,
    "total": 100,
    "total_pages": 5
  },
  "error": null
}
```

### 前端接收数据（axios 拦截器处理后）
```javascript
// axios 拦截器返回 data.data
{
  "items": [...],
  "page": 1,
  "size": 20,
  "total": 100,
  "total_pages": 5
}
```

## 验证

### 后端测试
```bash
cd CRTAssistant_demo/backend
python3 -c "
from app.core.response import success_response
response = success_response({'items': []}, '获取成功')
print(response)
"
```

输出：
```python
{
  'success': True,
  'message': '获取成功',
  'data': {'items': []},
  'error': None
}
```

### 前端测试
```javascript
// Store 中的处理
const result = await getInventoryList(params);
const list = result?.items || [];  // 正确获取数组
```

## 相关文件变更

```
backend/
├── app/
│   ├── core/
│   │   └── response.py              # 新建：统一响应格式
│   └── modules/inventory/interfaces/api/routes/
│       └── inventory_routes.py      # 更新：使用统一响应

frontend/
└── src/modules/plan/
    ├── components/PlanStepsForm/
    │   └── InventoryScopeStep.jsx   # 更新：数组类型检查
    └── store/
        └── planStore.js             # 更新：简化数据处理
```

## 后续建议

1. **统一所有接口响应格式**：将其他接口也迁移到统一响应格式
2. **添加类型定义**：为 API 响应添加 TypeScript 类型定义
3. **前端数据校验**：使用 zod 等库验证 API 响应数据结构

---

**修复日期**: 2026-03-30
**修复状态**: ✅ 已完成
