/**
 * Inventory 模块入口
 * 统一导出模块对外暴露的所有内容
 */

// 导出路由
export { inventoryRoutes } from './router';

// 导出视图组件
export { default as InventoryListView } from './views/InventoryListView';

// 导出状态管理
export { useInventoryStore } from './store';

// 导出 API
export * from './api';
