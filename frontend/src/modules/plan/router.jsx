/**
 * Plan 模块路由配置
 * 显式定义模块内部路由
 */
import React, { Suspense } from 'react';
import { Spin } from 'antd';

// 懒加载页面组件
const PlanListView = React.lazy(() => import('./views/PlanListView'));
const PlanCreateView = React.lazy(() => import('./views/PlanCreateView'));
const PlanDetailView = React.lazy(() => import('./views/PlanDetailView'));
const PlanEditView = React.lazy(() => import('./views/PlanEditView'));

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

/**
 * Plan 模块路由配置
 */
export const planRoutes = [
  {
    path: '/plans',
    element: (
      <Suspense fallback={<PageLoading />}>
        <PlanListView />
      </Suspense>
    ),
  },
  {
    path: '/plans/create',
    element: (
      <Suspense fallback={<PageLoading />}>
        <PlanCreateView />
      </Suspense>
    ),
  },
  {
    path: '/plans/:id',
    element: (
      <Suspense fallback={<PageLoading />}>
        <PlanDetailView />
      </Suspense>
    ),
  },
  {
    path: '/plans/:id/edit',
    element: (
      <Suspense fallback={<PageLoading />}>
        <PlanEditView />
      </Suspense>
    ),
  },
];

export default planRoutes;
