/**
 * 主布局组件
 * 包含侧边栏、顶部导航和内容区
 */

import React, { useEffect } from 'react';
import { Outlet, useNavigate, useLocation, Navigate } from 'react-router-dom';
import { Layout, Menu, Button, Dropdown, Avatar, Space } from 'antd';
import {
  DashboardOutlined,
  FileTextOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  DatabaseOutlined,
  CloudOutlined,
  SafetyOutlined,
  ToolOutlined,
  FileSearchOutlined,
  NodeIndexOutlined,
  BranchesOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '../../stores';

const { Header, Sider, Content } = Layout;

function MainLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, isAuthenticated } = useAuthStore();

  // 未登录时重定向到登录页
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // 侧边栏菜单项
  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/admission-tasks',
      icon: <FileTextOutlined />,
      label: '准入任务',
    },
    {
      key: 'workflows',
      icon: <NodeIndexOutlined />,
      label: '工作流管理',
      children: [
        {
          key: '/workflows',
          icon: <BranchesOutlined />,
          label: '工作流模板',
        },
        {
          key: '/workflow-instances',
          icon: <FileTextOutlined />,
          label: '工作流实例',
        },
      ],
    },
    {
      key: 'inventories',
      icon: <DatabaseOutlined />,
      label: '台账管理',
      children: [
        {
          key: '/inventories/server',
          icon: <DatabaseOutlined />,
          label: '应用系统台账',
        },
        {
          key: '/inventories/cloud',
          icon: <CloudOutlined />,
          label: '云服务台账',
        },
        {
          key: '/inventories/account',
          icon: <UserOutlined />,
          label: '系统账户台账',
        },
      ],
    },
    {
      key: 'verification',
      icon: <FileSearchOutlined />,
      label: '验证管理',
      children: [
        {
          key: '/verification/scripts',
          icon: <ToolOutlined />,
          label: '验证脚本',
        },
        {
          key: '/verification/records',
          icon: <FileTextOutlined />,
          label: '验证记录',
        },
      ],
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '系统设置',
    },
  ];

  // 用户下拉菜单
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人中心',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
  ];

  const handleMenuClick = ({ key }) => {
    if (key === 'logout') {
      logout();
      navigate('/login');
    } else if (key === 'profile') {
      navigate('/profile');
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 侧边栏 */}
      <Sider theme="light" width={200}>
        <div style={{ 
          height: 64, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          fontSize: 18,
          fontWeight: 'bold',
          borderBottom: '1px solid #f0f0f0'
        }}>
          运维经理
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ borderRight: 0 }}
        />
      </Sider>

      <Layout>
        {/* 顶部导航 */}
        <Header style={{ 
          background: '#fff', 
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: '0 1px 4px rgba(0,0,0,0.1)'
        }}>
          <div style={{ fontSize: 16 }}>
            仿真运维经理 - 准入管理系统
          </div>
          
          <Space>
            <span style={{ color: '#666' }}>
              {user?.real_name} ({user?.role})
            </span>
            <Dropdown
              menu={{ items: userMenuItems, onClick: handleMenuClick }}
              placement="bottomRight"
            >
              <Avatar icon={<UserOutlined />} style={{ cursor: 'pointer' }} />
            </Dropdown>
          </Space>
        </Header>

        {/* 内容区 */}
        <Content style={{ 
          margin: 24, 
          padding: 24, 
          background: '#fff',
          borderRadius: 8,
          minHeight: 280,
          overflow: 'auto'
        }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}

export default MainLayout;
