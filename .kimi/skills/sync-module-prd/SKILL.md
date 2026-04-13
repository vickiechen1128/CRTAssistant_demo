# Skill: sync-module-prd

## 基本信息

- **名称**: sync-module-prd
- **描述**: 模块 PRD 与全局架构同步校验，确保模块需求与全局架构保持一致
- **调用方式**: `/skill:sync-module-prd --module=<模块名> [--check-only]`

## 使用场景

在更新模块 PRD 时，需要：
1. 校验模块 PRD 中的功能定义是否与全局架构一致
2. 检测模块间的依赖关系是否在全局架构中正确体现
3. 识别全局架构需要更新的内容
4. 生成同步建议报告

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `--module` | string | 是 | 模块名称（如 plan, inventory, verification, workflow） |
| `--check-only` | flag | 否 | 仅检查，不生成更新建议 |
| `--update-global` | flag | 否 | 自动更新全局架构文档（需谨慎） |

## 执行步骤

### 1. 读取相关文档

**读取的文件**:
- `OpsPilot_AI_PRD_Docs/00_Global_Architecture.md` - 全局架构文档
- `OpsPilot_AI_PRD_Docs/Modules/Module_XX_{module}_*.md` - 模块 PRD

### 2. 提取关键信息

**从全局架构提取**:
- 模块定义和职责
- 模块间依赖关系
- 接口调用关系
- 数据流转规则
- 实体定义

**从模块 PRD 提取**:
- 用户故事列表
- 功能需求
- 接口定义
- 实体定义
- 依赖的其他模块

### 3. 执行一致性校验

#### 3.1 模块定义校验

```
检查项:
✓ 模块名称是否一致
✓ 模块职责描述是否一致
✓ 模块状态（已完成/开发中/待开发）是否一致
```

#### 3.2 实体定义校验

```
检查项:
✓ 实体名称是否一致
✓ 实体属性是否一致
✓ 实体关系是否一致
✓ 状态枚举值是否一致
```

#### 3.3 接口依赖校验

```
检查项:
✓ 模块调用的其他模块接口是否在全局架构中定义
✓ 接口路径和参数是否一致
✓ 数据流转方向是否一致
```

#### 3.4 用户故事映射校验

```
检查项:
✓ PRD 中的用户故事是否在全局架构中有对应
✓ 用户故事与模块的映射是否正确
```

### 4. 生成校验报告

**报告内容**:
- 一致性检查结果（通过/警告/错误）
- 不一致项详细列表
- 全局架构需要更新的建议
- 模块 PRD 需要调整的建议

### 5. 生成同步建议（可选）

如果指定 `--update-global`，生成全局架构的更新补丁。

## 示例

### 示例 1：校验验证执行模块

```
/skill:sync-module-prd --module=verification
```

**预期输出**:
```
📖 读取文档:
   ✓ 00_Global_Architecture.md
   ✓ Module_04_Verification_Execution.md

🔍 执行一致性校验:

   ┌─ 模块定义校验 ──────────────────────────────┐
   │ ✓ 模块名称: verification                   │
   │ ✓ 模块职责: 执行验收逻辑（人工/脚本/AI）    │
   │ ✓ 模块状态: 待开发 → 开发中                │
   └─────────────────────────────────────────────┘

   ┌─ 实体定义校验 ──────────────────────────────┐
   │ ✓ VerificationTask                          │
   │ ✓ VerificationRecord                        │
   │ ✓ VerificationScript                        │
   │ ⚠ VerificationResult 在全局架构中未定义      │
   └─────────────────────────────────────────────┘

   ┌─ 接口依赖校验 ──────────────────────────────┐
   │ ✓ 依赖 plan 模块: GET /api/v1/plans/{id}   │
   │ ✓ 依赖 inventory 模块: GET /api/v1/inventory│
   │ ⚠ 依赖 workflow 模块未在全局架构中声明      │
   └─────────────────────────────────────────────┘

   ┌─ 用户故事映射校验 ──────────────────────────┐
   │ ✓ MGR-08: 执行核验任务                     │
   │ ✓ MGR-09: 审核交付物                       │
   │ ✓ VEN-03: 提交交付物待验证                 │
   └─────────────────────────────────────────────┘

📊 校验结果摘要:
   • 通过: 12 项
   • 警告: 2 项
   • 错误: 0 项

⚠️  发现 2 个警告:

   1. VerificationResult 实体在全局架构中未定义
      建议: 在 00_Global_Architecture.md 第 2.1 节添加该实体定义

   2. workflow 模块依赖未在全局架构中声明
      建议: 在 00_Global_Architecture.md 第 2.2.4 节添加接口调用关系

📋 下一步:
   1. 根据警告建议更新全局架构
   2. 或使用 --update-global 自动更新
```

### 示例 2：自动更新全局架构

```
/skill:sync-module-prd --module=verification --update-global
```

**预期输出**:
```
📖 读取并分析文档...

🔍 执行一致性校验...

⚠️  发现 2 个需要更新的地方:

📝 更新 00_Global_Architecture.md:

   1. 在第 2.1 节 "核心对象关系" 中添加 VerificationResult 实体:
      ```
      ├─ 验证执行层 (Verification)
      │  ├─ 验证任务: VerificationTask
      │  ├─ 验证记录: VerificationRecord
      │  ├─ 验证脚本: VerificationScript
      │  └─ 验证结果: VerificationResult  [新增]
      ```

   2. 在第 2.2.4 节 "计划-台账集成架构" 中添加 workflow 依赖:
      ```
      依赖模块:
      ├─ plan - 获取计划信息
      ├─ inventory - 获取台账信息
      └─ workflow - 更新工作项状态  [新增]
      ```

✅ 已自动更新 00_Global_Architecture.md

📋 请检查更新内容，确认无误后提交变更。
```

## 校验规则详解

### 规则 1: 模块名称一致性

**检查逻辑**:
```python
def check_module_name(global_arch, module_prd):
    global_name = extract_module_name(global_arch, module_prd.module_id)
    prd_name = module_prd.module_name
    
    if global_name != prd_name:
        return Warning(f"模块名称不一致: 全局架构'{global_name}' vs PRD'{prd_name}'")
    return Pass()
```

### 规则 2: 实体定义一致性

**检查逻辑**:
```python
def check_entities(global_arch, module_prd):
    global_entities = extract_entities(global_arch, module_prd.module_id)
    prd_entities = module_prd.entities
    
    issues = []
    
    # 检查 PRD 中的实体是否在全局架构中定义
    for entity in prd_entities:
        if entity.name not in global_entities:
            issues.append(Warning(f"实体 '{entity.name}' 在全局架构中未定义"))
    
    # 检查属性一致性
    for entity in prd_entities:
        if entity.name in global_entities:
            global_entity = global_entities[entity.name]
            for attr in entity.attributes:
                if attr not in global_entity.attributes:
                    issues.append(Warning(f"实体 '{entity.name}.{attr}' 在全局架构中未定义"))
    
    return issues
```

### 规则 3: 接口依赖一致性

**检查逻辑**:
```python
def check_dependencies(global_arch, module_prd):
    global_deps = extract_dependencies(global_arch, module_prd.module_id)
    prd_deps = module_prd.dependencies
    
    issues = []
    
    # 检查 PRD 中声明的依赖是否在全局架构中
    for dep in prd_deps:
        if dep.module_name not in global_deps:
            issues.append(Warning(f"依赖模块 '{dep.module_name}' 在全局架构中未声明"))
        else:
            # 检查接口定义
            for api in dep.apis:
                if api not in global_deps[dep.module_name]:
                    issues.append(Warning(f"接口 '{api}' 在全局架构中未定义"))
    
    return issues
```

### 规则 4: 用户故事映射一致性

**检查逻辑**:
```python
def check_user_stories(global_arch, module_prd):
    global_stories = extract_user_stories(global_arch, module_prd.module_id)
    prd_stories = module_prd.user_stories
    
    issues = []
    
    # 检查 PRD 中的用户故事是否在全局架构中有对应
    for story in prd_stories:
        if story.id not in global_stories:
            issues.append(Warning(f"用户故事 '{story.id}' 在全局架构中未映射"))
        elif global_stories[story.id].module != module_prd.module_id:
            issues.append(Error(f"用户故事 '{story.id}' 映射到错误模块"))
    
    return issues
```

## 实现指南

当用户调用此 Skill 时，按以下步骤执行：

1. **读取文档**
   ```python
   global_arch = read_file("OpsPilot_AI_PRD_Docs/00_Global_Architecture.md")
   module_prd = read_file(f"OpsPilot_AI_PRD_Docs/Modules/Module_XX_{module}_*.md")
   ```

2. **解析文档结构**
   - 使用 Markdown 解析器提取章节结构
   - 识别模块定义、实体定义、接口定义等关键内容
   - 提取表格中的映射关系

3. **执行校验规则**
   - 依次执行 4 类校验规则
   - 收集所有不一致项

4. **生成报告**
   - 按严重程度分类（错误/警告/通过）
   - 提供具体的修改建议
   - 指出需要更新的文档位置

5. **可选：自动更新**
   - 如果指定 `--update-global`
   - 生成文档补丁
   - 应用更新（需用户确认）

## 注意事项

1. **自动更新需谨慎**: `--update-global` 会直接修改全局架构文档，建议先使用 `--check-only` 查看差异
2. **版本控制**: 建议在运行此 Skill 前提交当前变更，方便回滚
3. **人工审查**: 自动更新后务必人工审查，确保语义正确
4. **模块编号**: 模块 PRD 文件名格式为 `Module_XX_{module}_*.md`，XX 为模块编号

## 与其他 Skill 的配合

```
开发流程:

1. 更新模块 PRD
   ↓
2. /skill:sync-module-prd --module=<模块名>  [本 Skill]
   ↓
3. 根据校验结果更新全局架构（如有需要）
   ↓
4. /skill:prd-to-code-checklist --prd=<PRD文件>  [生成开发清单]
   ↓
5. /skill:generate-ddd-scaffold --prd=<PRD文件>  [生成代码骨架]
   ↓
6. 开发实现
   ↓
7. /skill:api-integration-test --module=<模块名>  [联调测试]
```
