/**
 * 主应用组件
 */

import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './stores';

// 页面组件
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import TaskList from './pages/AdmissionTasks/List';
import TaskDetail from './pages/AdmissionTasks/Detail';
import CreateTask from './pages/AdmissionTasks/Create';
import Inventories from './pages/Inventories';
import ServerInventory from './pages/Inventories/ServerInventory';
import CloudInventory from './pages/Inventories/CloudInventory';
import AccountInventory from './pages/Inventories/AccountInventory';
import ServerInventoryList from './pages/Inventories/ServerInventoryList';
import CloudInventoryList from './pages/Inventories/CloudInventoryList';
import AccountInventoryList from './pages/Inventories/AccountInventoryList';
import VerificationScripts from './pages/Verification/Scripts';
import VerificationRecords from './pages/Verification/Records';

// 工作流管理页面
import WorkflowList from './pages/Workflows/List';
import WorkflowCreate from './pages/Workflows/Create';

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
          <Route path="/admission-tasks" element={<TaskList />} />
          <Route path="/admission-tasks/new" element={<CreateTask />} />
          <Route path="/admission-tasks/:id" element={<TaskDetail />} />
          {/* 台账管理路由 */}
          <Route path="/inventories/task/:taskId" element={<Inventories />} />
          <Route path="/inventories/server" element={<ServerInventoryList />} />
          <Route path="/inventories/cloud" element={<CloudInventoryList />} />
          <Route path="/inventories/account" element={<AccountInventoryList />} />
          <Route path="/inventories/:id" element={<ServerInventory />} />
          <Route path="/inventories/:taskId/server/create" element={<ServerInventory />} />
          <Route path="/inventories/:taskId/cloud_resource/create" element={<CloudInventory />} />
          <Route path="/inventories/:taskId/account/create" element={<AccountInventory />} />
          {/* 验证管理路由 */}
          <Route path="/verification/scripts" element={<VerificationScripts />} />
          <Route path="/verification/records" element={<VerificationRecords />} />
          {/* 工作流管理路由 */}
          <Route path="/workflows" element={<WorkflowList />} />
          <Route path="/workflows/new" element={<WorkflowCreate />} />
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
