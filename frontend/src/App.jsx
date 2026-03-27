/**
 * 主应用组件
 * 使用新的 Feature-Sliced Design 架构
 */
import React from 'react';
import { RouterProvider } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';

// 导入路由配置
import { router } from './core/router';

// 导入全局样式
import './index.css';

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <RouterProvider router={router} />
    </ConfigProvider>
  );
}

export default App;
