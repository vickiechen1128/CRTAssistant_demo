/**
 * Inventory 模块路由配置
 * 台账管理路由
 */
import React, { Suspense } from 'react';
import { Spin } from 'antd';

// 加载中组件
const PageLoading = () => (
  <div style={{ 
    display: 'flex', 
    justifyContent: 'center', 
    alignItems: 'center', 
    height: '100vh' 
  }}>
    <Spin size="large" tip="加载中..." />
  </div>
);

// 懒加载页面组件
const InventoryListView = React.lazy(() => import('./views/InventoryListView'));
const ApplicationCreateView = React.lazy(() => import('./views/ApplicationCreateView'));
const ApplicationDetailView = React.lazy(() => import('./views/ApplicationDetailViewEnhanced'));
const ApplicationEditView = React.lazy(() => import('./views/ApplicationEditView'));
const CloudResourceCreateView = React.lazy(() => import('./views/CloudResourceCreateView'));
const AccountCreateView = React.lazy(() => import('./views/AccountCreateView'));

/**
 * Inventory 模块路由配置
 */
export const inventoryRoutes = [
  {
    path: '/inventories',
    element: (
      <Suspense fallback={<PageLoading />}>
        <InventoryListView />
      </Suspense>
    ),
  },
  {
    path: '/inventories/applications/create',
    element: (
      <Suspense fallback={<PageLoading />}>
        <ApplicationCreateView />
      </Suspense>
    ),
  },
  {
    path: '/inventories/applications/:id',
    element: (
      <Suspense fallback={<PageLoading />}>
        <ApplicationDetailView />
      </Suspense>
    ),
  },
  {
    path: '/inventories/applications/:id/edit',
    element: (
      <Suspense fallback={<PageLoading />}>
        <ApplicationEditView />
      </Suspense>
    ),
  },
  {
    path: '/inventories/cloud-resources/create',
    element: (
      <Suspense fallback={<PageLoading />}>
        <CloudResourceCreateView />
      </Suspense>
    ),
  },
  {
    path: '/inventories/accounts/create',
    element: (
      <Suspense fallback={<PageLoading />}>
        <AccountCreateView />
      </Suspense>
    ),
  },
];

export default inventoryRoutes;
