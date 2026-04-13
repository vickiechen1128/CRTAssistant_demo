# Skill: api-integration-test

## 基本信息

- **名称**: api-integration-test
- **描述**: 自动化 API 联调测试，验证跨模块接口调用的正确性
- **调用方式**: `/skill:api-integration-test --module=<模块名> --scenario=<场景名>`

## 使用场景

当完成涉及多个模块的后端开发后，需要验证：
1. 跨模块接口调用链是否完整
2. 数据转换是否正确（DTO ↔ Entity ↔ Model）
3. 事务一致性（数据库操作是否回滚）
4. 错误传播（异常是否正确传递和处理）

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `--module` | string | 是 | 主模块名称（如 plan, inventory, verification） |
| `--scenario` | string | 否 | 测试场景名称（如 inventory-sync, workflow-execution） |
| `--verbose` | flag | 否 | 显示详细输出 |

## 执行步骤

### 1. 分析 PRD 中的接口调用关系

读取 `OpsPilot_AI_PRD_Docs/Modules/Module_XX_*.md`，提取：
- 接口定义（路径、方法、请求/响应格式）
- 跨模块调用关系
- 数据流转规则

### 2. 生成联调测试用例

根据 PRD 生成测试用例：

```python
# 示例：计划创建时同步创建台账
def test_create_plan_with_inventory_sync():
    """测试创建计划时同步创建应用系统台账"""
    # Step 1: 调用计划创建接口
    plan_response = client.post("/api/v1/plans", json={
        "name": "测试计划",
        "category": "new_system_launch",
        "basic_info": {...}
    })
    assert plan_response.status_code == 201
    plan_id = plan_response.json()["id"]

    # Step 2: 验证台账是否同步创建
    inventory_response = client.get(f"/api/v1/inventory/applications?plan_id={plan_id}")
    assert inventory_response.status_code == 200
    assert len(inventory_response.json()["items"]) > 0

    # Step 3: 验证生命周期日志
    log_response = client.get(f"/api/v1/inventory/lifecycle-logs?plan_id={plan_id}")
    assert log_response.status_code == 200
    assert any(log["type"] == "system_launch" for log in log_response.json())
```

### 3. 执行测试并收集结果

```bash
cd backend
python -m pytest tests/integration/api/test_{module}_api.py::{scenario} -v
```

### 4. 输出测试报告

生成包含以下内容的报告：
- 测试通过率
- 失败的测试及原因
- 接口调用链路图
- 性能指标（响应时间）

## 示例

### 示例 1：测试计划-台账同步

```
/skill:api-integration-test --module=plan --scenario=inventory-sync
```

**预期输出**:
```
🔄 开始执行联调测试: plan → inventory

📋 测试场景: 创建计划时同步创建台账
   ├── 测试 1: 新系统上线时创建应用系统台账 [PASS]
   ├── 测试 2: 新功能上线时添加功能模块 [PASS]
   ├── 测试 3: 计划状态变更同步更新台账状态 [PASS]
   └── 测试 4: 生命周期日志记录 [PASS]

📊 测试结果摘要:
   • 总测试数: 4
   • 通过: 4
   • 失败: 0
   • 平均响应时间: 120ms

✅ 所有测试通过！可以进行前端开发。
```

### 示例 2：测试工作流执行

```
/skill:api-integration-test --module=verification --scenario=workflow-execution
```

**预期输出**:
```
🔄 开始执行联调测试: verification → workflow → inventory

📋 测试场景: 执行验收工作流
   ├── 测试 1: 创建工作流实例 [PASS]
   ├── 测试 2: 执行工作项并更新进度 [PASS]
   ├── 测试 3: 提交交付物并触发审核 [PASS]
   ├── 测试 4: 审核通过后更新台账状态 [FAIL]
   │   └── 错误: 期望状态 'online'，实际状态 'testing'
   └── 测试 5: 记录审计日志 [PASS]

📊 测试结果摘要:
   • 总测试数: 5
   • 通过: 4
   • 失败: 1
   • 失败详情见: backend/test_reports/integration_test_20240413.html

⚠️ 发现 1 个问题，请修复后再进行前端开发。
```

## 实现指南

当用户调用此 Skill 时，按以下步骤执行：

1. **读取 PRD 文件**
   - 定位到 `OpsPilot_AI_PRD_Docs/Modules/Module_XX_{module}_*.md`
   - 提取接口定义和跨模块调用关系

2. **分析现有代码**
   - 检查 `backend/app/modules/{module}/` 下的实现
   - 识别依赖的其他模块

3. **生成测试代码**
   - 在 `backend/tests/integration/api/` 下生成测试文件
   - 测试文件名: `test_{module}_{scenario}.py`

4. **执行测试**
   - 使用 pytest 执行生成的测试
   - 收集测试结果和覆盖率

5. **生成报告**
   - 输出测试摘要到控制台
   - 生成 HTML 报告到 `backend/test_reports/`

## 注意事项

1. 测试前确保数据库已初始化且有测试数据
2. 测试会修改数据库，建议在隔离环境执行
3. 跨模块调用测试需要所有相关模块已实现
4. 失败的测试会阻止前端开发建议
