/**
 * 全局路由配置
 * 显式注册各模块路由
 */
import React, { Suspense, useEffect } from 'react';
import { createBrowserRouter, Navigate, Outlet, useNavigate } from 'react-router-dom';
import { Spin } from 'antd';

// 导入 Plan 模块路由
import { planRoutes } from '../../modules/plan';
// 导入 Inventory 模块路由
import { inventoryRoutes } from '../../modules/inventory';

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

// 路由守卫组件
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

// 登录页面组件 - 自动设置 token 并跳转（临时方案）
const LoginPage = () => {
  const navigate = useNavigate();
  
  useEffect(() => {
    // 临时方案：自动设置 token 并跳转到计划列表
    localStorage.setItem('token', 'demo-token');
    navigate('/plans', { replace: true });
  }, [navigate]);
  
  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      flexDirection: 'column'
    }}>
      <Spin size="large" />
      <p style={{ marginTop: 16 }}>正在登录...</p>
    </div>
  );
};

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
      <ProtectedRoute>
        <Suspense fallback={<PageLoading />}>
          <MainLayout>
            <Outlet />
          </MainLayout>
        </Suspense>
      </ProtectedRoute>
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
    ],
  },
]);

export default router;
