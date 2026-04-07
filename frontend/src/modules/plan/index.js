/**
 * Plan 模块入口
 * 统一导出模块对外暴露的所有内容
 */

// 导出路由
export { planRoutes } from './router';

// 导出业务组件（供其他模块使用）
export { default as PlanCard } from './components/PlanCard';
export { default as PlanStatusBadge } from './components/PlanStatusBadge';
export { default as PlanForm } from './components/PlanForm';
export { default as PlanStepsForm } from './components/PlanStepsForm';

// 导出步骤组件（供其他模块使用）
export { default as BasicInfoStep } from './components/PlanStepsForm/BasicInfoStep';
export { default as ApprovalFilesStep } from './components/PlanStepsForm/ApprovalFilesStep';
export { default as InventoryScopeStep } from './components/PlanStepsForm/InventoryScopeStep';
export { default as PreviewStep } from './components/PlanStepsForm/PreviewStep';

// 导出 Store
export { usePlanStore } from './store';

// 导出 API
export * from './api';

// 导出类型
export * from './api/types';
