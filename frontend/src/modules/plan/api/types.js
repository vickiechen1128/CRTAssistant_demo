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
