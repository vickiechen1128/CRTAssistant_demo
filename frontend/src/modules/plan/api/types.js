/**
 * Plan 模块 API 类型定义
 */

// 计划分类
export const PlanCategory = {
  NEW_SYSTEM: 'new_system',
  NEW_FEATURE: 'new_feature',
  FUNC_CHANGE: 'func_change',
  ARCH_CHANGE: 'arch_change',
  SECURITY_CHECK: 'security_check',
};

// 计划优先级
export const PlanPriority = {
  P0: 'P0',
  P1: 'P1',
  P2: 'P2',
  P3: 'P3',
};

// 计划状态
export const PlanStatus = {
  DRAFT: 'DRAFT',
  PENDING: 'PENDING',
  IN_PROGRESS: 'IN_PROGRESS',
  COMPLETED: 'COMPLETED',
  CANCELLED: 'CANCELLED',
};

// 功能模块操作类型
export const ModuleAction = {
  CREATE: 'create',
  UPDATE: 'update',
  DELETE: 'delete',
};

// 分类选项（用于下拉选择）
export const categoryOptions = [
  { value: PlanCategory.NEW_SYSTEM, label: '新系统上线', code: 'NEW' },
  { value: PlanCategory.NEW_FEATURE, label: '新功能上线', code: 'FTR' },
  { value: PlanCategory.FUNC_CHANGE, label: '功能变更', code: 'FUN' },
  { value: PlanCategory.ARCH_CHANGE, label: '架构变更', code: 'ARC' },
  { value: PlanCategory.SECURITY_CHECK, label: '安全检查', code: 'SEC' },
];

// 优先级选项
export const priorityOptions = [
  { value: PlanPriority.P0, label: 'P0 - 最高优先级', color: 'red' },
  { value: PlanPriority.P1, label: 'P1 - 高优先级', color: 'orange' },
  { value: PlanPriority.P2, label: 'P2 - 中优先级', color: 'blue' },
  { value: PlanPriority.P3, label: 'P3 - 低优先级', color: 'green' },
];

// 状态选项
export const statusOptions = [
  { value: PlanStatus.DRAFT, label: '草稿', color: 'default' },
  { value: PlanStatus.PENDING, label: '待确认', color: 'warning' },
  { value: PlanStatus.IN_PROGRESS, label: '执行中', color: 'processing' },
  { value: PlanStatus.COMPLETED, label: '已完成', color: 'success' },
  { value: PlanStatus.CANCELLED, label: '已取消', color: 'error' },
];

// 模块操作选项
export const moduleActionOptions = [
  { value: ModuleAction.CREATE, label: '新增', color: 'green', icon: 'plus' },
  { value: ModuleAction.UPDATE, label: '更新', color: 'blue', icon: 'edit' },
  { value: ModuleAction.DELETE, label: '删除', color: 'red', icon: 'delete' },
];

// 模板类型映射
export const templateTypeMap = {
  [PlanCategory.NEW_SYSTEM]: 'new_system',
  [PlanCategory.NEW_FEATURE]: 'new_feature',
  [PlanCategory.FUNC_CHANGE]: 'func_change',
  [PlanCategory.ARCH_CHANGE]: 'arch_change',
  [PlanCategory.SECURITY_CHECK]: 'security',
};

// 获取分类配置
export const getCategoryConfig = (category) => {
  return categoryOptions.find(opt => opt.value === category);
};

// 获取优先级配置
export const getPriorityConfig = (priority) => {
  return priorityOptions.find(opt => opt.value === priority);
};

// 获取状态配置
export const getStatusConfig = (status) => {
  return statusOptions.find(opt => opt.value === status);
};

// 获取模块操作配置
export const getModuleActionConfig = (action) => {
  return moduleActionOptions.find(opt => opt.value === action);
};

/**
 * 计划创建步骤
 */
export const PlanCreationSteps = [
  { title: '基本信息', description: '填写计划名称、分类等' },
  { title: '审批材料', description: '上传审批文件' },
  { title: '涉及范围', description: '选择台账和功能模块' },
  { title: '预览确认', description: '确认变更内容' },
];

/**
 * 获取计划分类对应的台账操作方式
 * @param {string} category - 计划分类
 * @returns {string} - 操作方式描述
 */
export const getInventoryActionType = (category) => {
  const actionMap = {
    [PlanCategory.NEW_SYSTEM]: 'create_new',
    [PlanCategory.NEW_FEATURE]: 'select_and_edit',
    [PlanCategory.FUNC_CHANGE]: 'select_existing',
    [PlanCategory.ARCH_CHANGE]: 'select_existing',
    [PlanCategory.SECURITY_CHECK]: 'security_scan',
  };
  return actionMap[category] || 'select_existing';
};

/**
 * 是否需要选择台账
 * @param {string} category - 计划分类
 * @returns {boolean}
 */
export const requiresInventorySelection = (category) => {
  return category !== PlanCategory.SECURITY_CHECK;
};

/**
 * 是否可以多选台账
 * @param {string} category - 计划分类
 * @returns {boolean}
 */
export const allowMultipleInventory = (category) => {
  return [PlanCategory.FUNC_CHANGE, PlanCategory.ARCH_CHANGE].includes(category);
};
