/**
 * 主布局组件
 * 包含顶部导航和内容区
 */

import React from 'react';
import { Outlet, useNavigate, useLocation, Navigate } from 'react-router-dom';
import { Layout, Menu, Dropdown, Avatar, Space, Badge } from 'antd';
import {
  DashboardOutlined,
  FileTextOutlined,
  UserOutlined,
  LogoutOutlined,
  DatabaseOutlined,
  CloudOutlined,
  SafetyOutlined,
  ToolOutlined,
  FileSearchOutlined,
  NodeIndexOutlined,
  BranchesOutlined,
  ScheduleOutlined,
  BookOutlined,
  CheckCircleOutlined,
  GiftOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '../../stores';

const { Header, Content } = Layout;

function MainLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, isAuthenticated } = useAuthStore();

  // TODO: 登录功能开发完成后启用
  // 未登录时重定向到登录页
  // if (!isAuthenticated) {
  //   return <Navigate to="/login" replace />;
  // }

  // 顶部导航菜单项
  const navItems = [
    {
      key: '/plans',
      icon: <ScheduleOutlined />,
      label: '计划管理',
    },
    {
      key: '/inventories',
      icon: <BookOutlined />,
      label: '台账管理',
    },
    {
      key: '/sop-templates',
      icon: <NodeIndexOutlined />,
      label: '工作流编排',
    },
    {
      key: '/deliverables',
      icon: <GiftOutlined />,
      label: '交付物管理',
    },
    {
      key: '/verification',
      icon: <CheckCircleOutlined />,
      label: '核验执行',
    },
    {
      key: '/knowledge',
      icon: <FileSearchOutlined />,
      label: '知识库',
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
    <Layout style={{ minHeight: '100vh', background: '#f5f7fa' }}>
      {/* 顶部Banner */}
      <Header style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: 0,
        height: 'auto',
        lineHeight: 'normal',
      }}>
        {/* 顶部栏 */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '16px 32px',
          borderBottom: '1px solid rgba(255,255,255,0.1)',
        }}>
          {/* Logo */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            fontSize: '22px',
            fontWeight: 600,
            color: 'white',
          }}>
            <div style={{
              width: '40px',
              height: '40px',
              background: 'rgba(255,255,255,0.2)',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px',
            }}>
              🤖
            </div>
            <span>OpsPilot</span>
          </div>

          {/* 用户信息 */}
          <Space>
            <span style={{ color: 'rgba(255,255,255,0.9)', fontSize: '14px' }}>
              {user?.real_name || user?.username}
            </span>
            <Dropdown
              menu={{ items: userMenuItems, onClick: handleMenuClick }}
              placement="bottomRight"
            >
              <Avatar 
                icon={<UserOutlined />} 
                style={{ 
                  cursor: 'pointer',
                  background: 'rgba(255,255,255,0.2)',
                }} 
              />
            </Dropdown>
          </Space>
        </div>

        {/* 导航Tab */}
        <div style={{
          display: 'flex',
          padding: '0 32px',
          gap: '8px',
        }}>
          {navItems.map(item => (
            <div
              key={item.key}
              onClick={() => navigate(item.key)}
              style={{
                padding: '14px 24px',
                fontSize: '15px',
                cursor: 'pointer',
                transition: 'all 0.3s',
                borderBottom: `3px solid ${location.pathname.startsWith(item.key) ? 'white' : 'transparent'}`,
                opacity: location.pathname.startsWith(item.key) ? 1 : 0.7,
                background: location.pathname.startsWith(item.key) ? 'rgba(255,255,255,0.15)' : 'transparent',
                fontWeight: location.pathname.startsWith(item.key) ? 500 : 'normal',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                color: 'white',
              }}
              onMouseEnter={(e) => {
                if (!location.pathname.startsWith(item.key)) {
                  e.currentTarget.style.opacity = '1';
                  e.currentTarget.style.background = 'rgba(255,255,255,0.1)';
                }
              }}
              onMouseLeave={(e) => {
                if (!location.pathname.startsWith(item.key)) {
                  e.currentTarget.style.opacity = '0.7';
                  e.currentTarget.style.background = 'transparent';
                }
              }}
            >
              {item.icon}
              <span>{item.label}</span>
            </div>
          ))}
        </div>
      </Header>

      {/* 内容区 */}
      <Content style={{ 
        padding: '24px 32px',
        minHeight: 280,
      }}>
        <Outlet />
      </Content>
    </Layout>
  );
}

export default MainLayout;
