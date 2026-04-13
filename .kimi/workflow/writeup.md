# Week4 自动化工作流实践报告

## 项目背景

本项目为 **OpsPilot** - 面向甲方运维经理的准入验收与审计管理系统。采用 DDD（领域驱动设计）架构，包含以下核心模块：

- **Plan** (计划管理): 管理运维计划的完整生命周期
- **Inventory** (台账管理): 管理应用系统/云服务/账号三类台账
- **SOP Template** (SOP模板): 管理验收标准和工作项模板
- **Verification** (验证执行): 执行验收逻辑（待开发）
- **Workflow** (工作流): 执行工作流（待开发）

## 我的开发工作流程

```
1. PRD 编写 → OpsPilot_AI_PRD_Docs/Modules/Module_XX_*.md
2. DDD 后端开发 → backend/app/modules/{module}/
3. 接口联调测试 → 验证跨模块调用
4. 前端开发 → frontend/src/modules/{module}/
```

**核心痛点**: 第3步（多模块接口联调测试）耗时且容易遗漏场景。

## 自动化工作流设计

### 工作流 1: api-integration-test（API 联调测试）

#### 设计灵感

参考 Kimi Skills 文档中的 "测试运行器" 示例，针对 DDD 架构下多模块调用的特点，设计了专门的联调测试 Skill。

#### 目标

自动化验证跨模块接口调用的正确性，包括：
- 接口调用链完整性
- 数据转换正确性（DTO ↔ Entity ↔ Model）
- 事务一致性
- 错误传播机制

#### 输入/输出

**输入**:
- `--module`: 主模块名称
- `--scenario`: 测试场景名称
- `--verbose`: 详细输出标志

**输出**:
- 测试执行摘要（通过率、响应时间）
- 失败的测试详情
- HTML 测试报告

#### 使用示例

```bash
# 测试计划-台账同步场景
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

#### 如何运行

1. 确保后端服务已启动: `cd backend && python run.py`
2. 调用 Skill: `/skill:api-integration-test --module=<模块名> --scenario=<场景>`
3. 查看控制台输出和生成的 HTML 报告

#### 回滚/安全说明

- 测试在独立的数据库事务中执行，测试数据不会污染开发数据库
- 测试失败不会修改任何数据
- 可在 `backend/tests/integration/api/` 中查看和修改生成的测试代码

---

### 工作流 2: generate-ddd-scaffold（DDD 代码骨架生成）

#### 设计灵感

参考 Kimi Skills 文档中的 "重构工具" 和 "代码生成" 示例，针对 DDD 架构的重复性代码结构，设计了自动生成代码骨架的 Skill。

#### 目标

根据 PRD 自动生成 DDD 分层架构的完整代码骨架，减少重复性编码工作。

#### 输入/输出

**输入**:
- `--prd`: PRD 文件名
- `--module-name`: 模块名称（可选，自动解析）
- `--with-tests`: 同时生成测试代码

**输出**:
- 完整的 DDD 目录结构
- Domain/Application/Infrastructure/Interfaces 各层代码模板
- 可选的测试代码骨架

#### 使用示例

```bash
# 根据验证执行模块 PRD 生成代码骨架
/skill:generate-ddd-scaffold --prd=Module_04_Verification_Execution.md --with-tests
```

**预期输出**:
```
📖 解析 PRD: Module_04_Verification_Execution.md
   • 模块名称: verification
   • 识别实体: VerificationTask, VerificationRecord, VerificationScript
   • 识别值对象: VerificationStatus, VerificationMethod
   • 识别接口: 12 个 REST API

🏗️  生成 DDD 代码骨架:
   ✓ domain/entities/verification_task.py
   ✓ domain/entities/verification_record.py
   ✓ domain/entities/verification_script.py
   ✓ domain/value_objects/verification_status.py
   ✓ domain/repositories/verification_task_repository.py
   ✓ application/verification_service.py
   ✓ infrastructure/persistence/models/verification_task_model.py
   ✓ interfaces/api/routes/verification_routes.py
   ✓ ... (共 18 个文件)

🧪 生成测试骨架:
   ✓ tests/unit/test_verification_domain.py
   ✓ tests/integration/api/test_verification_api.py

📋 下一步:
   1. 检查生成的代码，根据业务逻辑完善实体方法
   2. 在 main.py 中注册路由
   3. 运行数据库迁移
   4. 使用 /skill:api-integration-test 进行联调测试
```

#### 如何运行

1. 确保 PRD 文件已保存到 `OpsPilot_AI_PRD_Docs/Modules/`
2. 调用 Skill: `/skill:generate-ddd-scaffold --prd=<PRD文件名>`
3. 检查生成的代码并根据业务逻辑完善

#### 回滚/安全说明

- 生成的代码是基础骨架，不会覆盖已有文件
- 需要在生成的代码基础上根据业务逻辑完善
- 建议在生成后先进行代码审查再提交

---

### 工作流 3: prd-to-code-checklist（PRD 转开发清单）

#### 设计灵感

参考 Kimi Skills 文档中的 "文档同步" 示例，针对 PRD 到代码的转换过程，设计了自动生成开发任务清单的 Skill。

#### 目标

将 PRD 转换为结构化的前后端开发任务清单，帮助开发者：
- 明确开发任务和顺序
- 识别跨模块依赖
- 评估开发工作量

#### 输入/输出

**输入**:
- `--prd`: PRD 文件名
- `--output`: 输出文件路径（可选）
- `--format`: 输出格式（markdown/json）

**输出**:
- 后端开发任务清单（Domain/Application/Infrastructure/Interfaces）
- 前端开发任务清单（API/Store/Components/Views）
- 跨模块调用分析
- 开发顺序建议

#### 使用示例

```bash
# 生成验证执行模块的开发清单
/skill:prd-to-code-checklist --prd=Module_04_Verification_Execution.md
```

**预期输出**:
```markdown
# Module_04_Verification_Execution 开发任务清单

## 模块信息
- **模块名称**: verification
- **模块职责**: 执行验收逻辑（人工/脚本/AI）
- **预计开发周期**: 10-15 天

## 后端开发任务

### 领域层
- [ ] VerificationTask 实体
  - [ ] 属性: id, plan_id, work_item_id, status, method, result, ...
  - [ ] 方法: create(), start(), complete(), fail(), retry()
- [ ] 值对象: VerificationStatus, VerificationMethod
- [ ] 仓储接口: IVerificationTaskRepository

### 应用层
- [ ] VerificationService
  - [ ] create_task() - 创建验证任务
  - [ ] execute_task() - 执行任务
  - [ ] retry_task() - 重试失败任务

## 前端开发任务

### API 层
- [ ] verificationApi.createTask(data)
- [ ] verificationApi.executeTask(id)

### Store 层
- [ ] verificationStore
  - [ ] state: tasks, currentTask, executionResult
  - [ ] actions: fetchTasks, executeTask

## 开发顺序
1. 领域层 (2天)
2. 应用层 (1天)
3. 基础设施层 (1天)
4. 接口层 (1天)
5. 联调测试 (2天)
6. 前端开发 (3天)
```

#### 如何运行

1. 确保 PRD 文件已保存到 `OpsPilot_AI_PRD_Docs/Modules/`
2. 调用 Skill: `/skill:prd-to-code-checklist --prd=<PRD文件名>`
3. 将生成的清单保存到项目文档中跟踪进度

#### 回滚/安全说明

- 仅生成文档，不会修改任何代码
- 清单仅供参考，实际开发时可能需要调整

---

### 工作流 4: sync-module-prd（模块 PRD 同步校验）

#### 设计灵感

参考 Kimi Skills 文档中的 "文档同步" 示例，针对多模块项目中 PRD 与全局架构容易不一致的问题，设计了自动同步校验 Skill。

#### 目标

在更新模块 PRD 时，自动校验和同步全局架构：
- 校验模块定义与全局架构的一致性
- 检测实体定义差异
- 验证接口依赖关系
- 生成同步建议

#### 输入/输出

**输入**:
- `--module`: 模块名称
- `--check-only`: 仅检查标志
- `--update-global`: 自动更新全局架构

**输出**:
- 一致性检查报告
- 不一致项详细列表
- 全局架构更新建议
- 模块 PRD 调整建议

#### 使用示例

```bash
# 校验验证执行模块 PRD 与全局架构的一致性
/skill:sync-module-prd --module=verification
```

**预期输出**:
```
📖 读取文档:
   ✓ 00_Global_Architecture.md
   ✓ Module_04_Verification_Execution.md

🔍 执行一致性校验:
   ✓ 模块定义: 通过
   ✓ 实体定义: 通过
   ⚠ 接口依赖: 发现 1 个警告
   ✓ 用户故事: 通过

⚠️  发现 1 个警告:
   workflow 模块依赖未在全局架构中声明
   建议: 在 00_Global_Architecture.md 第 2.2.4 节添加接口调用关系

📋 下一步:
   1. 根据警告建议更新全局架构
   2. 或使用 --update-global 自动更新
```

#### 如何运行

1. 更新模块 PRD 文件
2. 调用 Skill: `/skill:sync-module-prd --module=<模块名>`
3. 查看校验报告
4. 根据建议更新文档

#### 回滚/安全说明

- `--check-only` 模式不会修改任何文件
- `--update-global` 会自动更新全局架构，建议先检查再更新
- 更新前会自动备份原文件

---

## 前后对比

### 手动工作流（之前）

| 步骤 | 操作 | 耗时 | 痛点 |
|------|------|------|------|
| 1 | 阅读 PRD，理解需求 | 30min | 需要反复查阅 |
| 2 | 手动比对全局架构 | 20min | 容易遗漏不一致 |
| 3 | 手动创建 DDD 目录结构 | 20min | 重复性工作 |
| 4 | 编写实体/仓储/服务代码 | 2-3h | 样板代码多 |
| 5 | 编写测试用例 | 1-2h | 容易遗漏场景 |
| 6 | 手动测试跨模块调用 | 1-2h | 需要准备测试数据 |
| 7 | 整理前端开发任务 | 30min | 容易遗漏 |

**总计**: 5-8.5 小时

### 自动化工作流（之后）

| 步骤 | 操作 | 耗时 | 效果 |
|------|------|------|------|
| 1 | 阅读 PRD，理解需求 | 30min | 不变 |
| 2 | `/skill:sync-module-prd` | 1min | 自动校验一致性 |
| 3 | `/skill:prd-to-code-checklist` | 1min | 自动生成任务清单 |
| 4 | `/skill:generate-ddd-scaffold` | 1min | 自动生成代码骨架 |
| 5 | 完善业务逻辑 | 1-2h | 专注核心业务 |
| 6 | `/skill:api-integration-test` | 2min | 自动执行联调测试 |
| 7 | 修复问题（如有） | 30min | 问题定位更快 |

**总计**: 2-4 小时

**效率提升**: 约 **50-60%**

---

## 如何使用自动化工作流增强项目

### 场景 1: 开发新模块（如 Verification）

```bash
# 1. 编写 PRD 后，校验与全局架构的一致性
/skill:sync-module-prd --module=verification

# 2. 根据校验结果更新全局架构（如有需要）
# 3. 生成开发清单
/skill:prd-to-code-checklist --prd=Module_04_Verification_Execution.md

# 4. 根据清单，生成代码骨架
/skill:generate-ddd-scaffold --prd=Module_04_Verification_Execution.md --with-tests

# 5. 完善业务逻辑代码...

# 6. 完成后进行联调测试
/skill:api-integration-test --module=verification --scenario=workflow-integration

# 7. 测试通过后，开始前端开发
```

### 场景 2: 修改现有模块接口

```bash
# 1. 修改代码后，运行联调测试确保不影响其他模块
/skill:api-integration-test --module=plan --scenario=inventory-sync

# 2. 根据测试结果修复问题
```

### 场景 3: Code Review 前自检

```bash
# 提交 PR 前，自动运行联调测试
/skill:api-integration-test --module=<修改的模块> --verbose
```

---

## 文件清单

### 创建的自动化工作流文件

```
.kimi/
├── skills/
│   ├── api-integration-test/
│   │   └── SKILL.md              # API 联调测试 Skill
│   ├── generate-ddd-scaffold/
│   │   └── SKILL.md              # DDD 代码生成 Skill
│   ├── prd-to-code-checklist/
│   │   └── SKILL.md              # PRD 转开发清单 Skill
│   └── sync-module-prd/
│       └── SKILL.md              # 模块 PRD 同步校验 Skill

AGENTS.md                          # 项目指导文档
writeup.md                         # 本报告
```

---

## 总结

通过这 4 个自动化工作流，我解决了 DDD 架构开发中的核心痛点：

1. **sync-module-prd**: 模块 PRD 与全局架构同步校验，确保文档一致性
2. **prd-to-code-checklist**: PRD 转开发任务清单，明确开发路径
3. **generate-ddd-scaffold**: 根据 PRD 自动生成代码骨架，减少重复编码
4. **api-integration-test**: 自动化多模块联调测试，确保接口调用正确性

这些工作流形成了完整的开发闭环：
```
PRD 编写 → 同步校验 → 生成清单 → 代码生成 → 联调测试 → 前端开发
```

预计可提升 **50-60%** 的开发效率，同时显著降低因文档不一致和接口调用错误导致的 bug。
