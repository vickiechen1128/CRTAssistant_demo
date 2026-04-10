/**
 * 全局路由配置
 * 显式注册各模块路由
 * 
 * TODO: 登录功能待开发
 * - 当前版本暂不启用登录验证
 * - 所有页面均可直接访问
 * - 未来需要登录时，取消注释 ProtectedRoute 相关代码
 */
import React, { Suspense } from 'react';
import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom';
import { Spin } from 'antd';

// 导入 Plan 模块路由
import { planRoutes } from '../../modules/plan';
// 导入 Inventory 模块路由
import { inventoryRoutes } from '../../modules/inventory';
// 导入 SOP 模板模块路由
import { sopTemplateRoutes } from '../../modules/sop_template';

// 懒加载页面组件
const MainLayout = React.lazy(() => import('../components/Layout/MainLayout'));

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

// TODO: 登录功能开发完成后启用
// 路由守卫组件 - 暂时禁用，所有页面均可访问
// const ProtectedRoute = ({ children }) => {
//   const token = localStorage.getItem('token');
//   if (!token) {
//     return <Navigate to="/login" replace />;
//   }
//   return children;
// };

// TODO: 登录页面开发完成后启用
// 临时登录页面 - 仅作为占位
const LoginPage = () => (
  <div style={{ 
    display: 'flex', 
    justifyContent: 'center', 
    alignItems: 'center', 
    height: '100vh',
    flexDirection: 'column'
  }}>
    <h1>登录页面</h1>
    <p>此功能正在开发中...</p>
    <a href="/plans">直接进入应用</a>
  </div>
);

// 创建路由配置
export const router = createBrowserRouter([
  {
    path: '/login',
    element: (
      <Suspense fallback={<PageLoading />}>
        <LoginPage />
      </Suspense>
    ),
  },
  {
    path: '/',
    element: (
      // TODO: 登录功能完成后启用 ProtectedRoute
      // <ProtectedRoute>
      <Suspense fallback={<PageLoading />}>
        <MainLayout>
          <Outlet />
        </MainLayout>
      </Suspense>
      // </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <Navigate to="/plans" replace />,
      },
      {
        path: 'dashboard',
        element: (
          <Suspense fallback={<PageLoading />}>
            <div>仪表盘（待实现）</div>
          </Suspense>
        ),
      },
      // 🎯 显式挂载 Plan 模块路由
      ...planRoutes,
      // 🎯 显式挂载 Inventory 模块路由
      ...inventoryRoutes,
      // 🎯 显式挂载 SOP 模板模块路由
      ...sopTemplateRoutes,
    ],
  },
]);

export default router;
