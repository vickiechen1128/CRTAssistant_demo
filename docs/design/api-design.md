# 仿真运维经理 - API 设计文档

| 版本 | 日期 | 作者 | 变更说明 |
|-----|------|-----|---------|
| v1.1 | 2024-03-24 | CRT | 重构：根据PRD v1.2更新，新增台账管理模块API，更新计划分类枚举值 |
| v1.0 | 2024-03-22 | CRT | 重构：按照五大业务阶段重新组织API |
| v0.1 | 2024-03-20 | CRT | 初稿，核心API定义 |

---

## 1. 接口概览

### 1.1 计划分类枚举值（更新）

| 枚举值 | 说明 | 范围选择方式 | 自动生成工作项 |
|-------|------|-------------|---------------|
| new_system | 新系统上线 | 创建新台账 | 补充应用系统台账 |
| new_feature | 新功能发布 | 查询+编辑 | 补充新增的功能模块 |
| business_change | 业务功能变更 | 查询+勾选 | 更新应用系统台账 |
| db_change | 数据库变更 | 查询+勾选 | 更新数据库相关台账 |

### 1.2 业务阶段与API对应关系



---

## 2. 计划管理API更新

### 2.1 计划分类与范围选择

计划创建时根据分类自动确定范围选择方式：

| 计划分类 | 范围选择API | 操作类型 | 说明 |
|---------|------------|---------|------|
| new_system | POST /api/plans/{id}/scope | 创建新台账 | 填写完整应用系统信息 |
| new_feature | POST /api/plans/{id}/scope | 查询+编辑 | 选择台账后编辑功能模块 |
| business_change | POST /api/plans/{id}/scope | 查询+勾选 | 多选已有台账 |
| db_change | POST /api/plans/{id}/scope | 查询+勾选 | 多选已有台账 |

### 2.2 范围选择接口（新增）

#### POST /api/plans/{id}/scope
选择涉及范围，系统自动生成第一个工作项

**请求体根据计划分类不同而变化**

**响应成功**:


---

## 3. 台账管理API（新增章节）

### 3.1 应用系统台账接口

#### GET /api/inventories/applications
获取应用系统台账列表

#### POST /api/inventories/applications
创建应用系统台账

#### GET /api/inventories/applications/{id}
获取应用系统台账详情

#### PUT /api/inventories/applications/{id}
更新应用系统台账

### 3.2 云服务资源台账接口

#### GET /api/inventories/cloud-resources
获取云服务资源台账列表（支持IAAS/PAAS筛选）

#### POST /api/inventories/cloud-resources
创建云服务资源台账

### 3.3 系统及软件账号台账接口

#### GET /api/inventories/accounts
获取账号台账列表

#### POST /api/inventories/accounts
创建账号台账

### 3.4 批量导入接口

#### POST /api/inventories/import
批量导入台账数据（Excel格式）

**请求体**: multipart/form-data


**响应成功**:


---

**注意**: 本文档已根据PRD v1.2更新，主要变更包括：
1. 更新计划分类枚举值（4种分类）
2. 新增台账管理模块API
3. 新增范围选择接口
4. 明确计划分类与范围选择的对应关系
