/**
 * 主应用组件
 */

import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './stores';

// 页面组件
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

// 计划管理页面
import PlanManagement from './pages/Plans/Management';
import PlanCreation from './pages/Plans/Creation';

// 台账管理页面
import InventoryManagement from './pages/Inventories/Management';
import AppInventoryCreate from './pages/Inventories/AppCreate';
import CloudInventoryCreate from './pages/Inventories/CloudCreate';
import AccountInventoryCreate from './pages/Inventories/AccountCreate';

// 布局组件
import MainLayout from './components/Layout/MainLayout';

function App() {
  const { isAuthenticated, user, fetchUser } = useAuthStore();
  const [isInitializing, setIsInitializing] = React.useState(true);

  // 初始化时获取用户信息
  useEffect(() => {
    console.log('App初始化, isAuthenticated:', isAuthenticated, 'user:', user);
    const token = localStorage.getItem('access_token');
    console.log('本地token:', token ? '存在' : '不存在');
    
    // 如果有token，需要验证token有效性
    if (token) {
      console.log('调用fetchUser验证token');
      fetchUser().finally(() => {
        setIsInitializing(false);
      });
    } else {
      setIsInitializing(false);
    }
  }, []); // 空依赖，只执行一次

  // 初始化期间显示加载状态
  if (isInitializing) {
    return (
      <div style={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#f0f2f5'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 24, marginBottom: 16 }}>加载中...</div>
          <div style={{ color: '#999' }}>正在验证登录状态</div>
        </div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        {/* 登录页 */}
        <Route 
          path="/login" 
          element={isAuthenticated ? <Navigate to="/" /> : <Login />} 
        />
        
        {/* 需要登录的路由 */}
        <Route element={<MainLayout />}>
          <Route path="/" element={<Dashboard />} />
          
          {/* 计划管理路由 */}
          <Route path="/plans" element={<PlanManagement />} />
          <Route path="/plans/new" element={<PlanCreation />} />
          
          {/* 台账管理路由 */}
          <Route path="/inventories" element={<InventoryManagement />} />
          <Route path="/inventories/app/create" element={<AppInventoryCreate />} />
          <Route path="/inventories/cloud/create" element={<CloudInventoryCreate />} />
          <Route path="/inventories/account/create" element={<AccountInventoryCreate />} />
        </Route>

        {/* 默认重定向 */}
        <Route 
          path="*" 
          element={<Navigate to={isAuthenticated ? "/" : "/login"} />} 
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
