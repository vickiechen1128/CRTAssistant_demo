/**
 * 仪表盘页面
 * 展示系统概览、快捷入口
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Row, Col, Statistic, Button, List, Tag, Space } from 'antd';
import {
  FileTextOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  PlusOutlined,
  ScheduleOutlined,
  BookOutlined,
  DatabaseOutlined,
  CloudOutlined,
  UserOutlined,
  ArrowRightOutlined,
} from '@ant-design/icons';

function Dashboard() {
  const navigate = useNavigate();

  // 快捷入口数据
  const quickActions = [
    {
      title: '创建计划',
      desc: '新建准入计划',
      icon: <ScheduleOutlined style={{ fontSize: 24, color: '#667eea' }} />,
      path: '/plans/new',
      color: '#667eea',
    },
    {
      title: '台账管理',
      desc: '管理应用/云资源/账号',
      icon: <BookOutlined style={{ fontSize: 24, color: '#764ba2' }} />,
      path: '/inventories',
      color: '#764ba2',
    },
    {
      title: '应用台账',
      desc: '创建应用系统台账',
      icon: <DatabaseOutlined style={{ fontSize: 24, color: '#11998e' }} />,
      path: '/inventories/app/create',
      color: '#11998e',
    },
    {
      title: '云服务台账',
      desc: '创建云服务资源台账',
      icon: <CloudOutlined style={{ fontSize: 24, color: '#38ef7d' }} />,
      path: '/inventories/cloud/create',
      color: '#38ef7d',
    },
  ];

  // 最近计划数据
  const recentPlans = [
    { id: 'PLAN-2024-001', name: '订单管理系统V2.0上线', status: 'processing', date: '2024-03-20' },
    { id: 'PLAN-2024-002', name: '支付接口优化升级', status: 'pending', date: '2024-03-19' },
    { id: 'PLAN-2024-003', name: '数据库迁移项目', status: 'completed', date: '2024-03-18' },
  ];

  const statusMap = {
    processing: { color: 'gold', text: '进行中' },
    pending: { color: 'blue', text: '待启动' },
    completed: { color: 'green', text: '已完成' },
  };

  return (
    <div>
      {/* 页面标题 */}
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ margin: 0, fontSize: 24, fontWeight: 600 }}>仪表盘</h2>
        <p style={{ margin: '8px 0 0 0', color: '#666' }}>欢迎使用仿真运维经理系统</p>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card hoverable>
            <Statistic
              title="计划总数"
              value={156}
              prefix={<ScheduleOutlined />}
              valueStyle={{ color: '#667eea' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card hoverable>
            <Statistic
              title="进行中"
              value={45}
              valueStyle={{ color: '#1890ff' }}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card hoverable>
            <Statistic
              title="待启动"
              value={23}
              valueStyle={{ color: '#faad14' }}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card hoverable>
            <Statistic
              title="已完成"
              value={88}
              valueStyle={{ color: '#52c41a' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 快捷入口 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        {quickActions.map((action, index) => (
          <Col span={6} key={index}>
            <Card
              hoverable
              onClick={() => navigate(action.path)}
              bodyStyle={{ padding: 20 }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <div
                  style={{
                    width: 56,
                    height: 56,
                    background: `${action.color}15`,
                    borderRadius: 12,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  {action.icon}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 4 }}>{action.title}</div>
                  <div style={{ fontSize: 13, color: '#999' }}>{action.desc}</div>
                </div>
                <ArrowRightOutlined style={{ color: '#999' }} />
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* 最近计划和台账统计 */}
      <Row gutter={16}>
        <Col span={12}>
          <Card
            title="最近计划"
            extra={<Button type="link" onClick={() => navigate('/plans')}>查看全部</Button>}
          >
            <List
              dataSource={recentPlans}
              renderItem={(item) => (
                <List.Item
                  actions={[
                    <Button type="link" onClick={() => navigate(`/plans`)}>查看</Button>
                  ]}
                >
                  <List.Item.Meta
                    title={item.name}
                    description={
                      <Space>
                        <span style={{ fontFamily: 'monospace', color: '#999' }}>{item.id}</span>
                        <Tag color={statusMap[item.status]?.color}>{statusMap[item.status]?.text}</Tag>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="台账统计">
            <Row gutter={16}>
              <Col span={8}>
                <Card style={{ textAlign: 'center', background: '#f8f9fa', border: 'none' }}>
                  <DatabaseOutlined style={{ fontSize: 32, color: '#667eea', marginBottom: 8 }} />
                  <div style={{ fontSize: 24, fontWeight: 700 }}>18</div>
                  <div style={{ fontSize: 13, color: '#666' }}>应用系统</div>
                </Card>
              </Col>
              <Col span={8}>
                <Card style={{ textAlign: 'center', background: '#f8f9fa', border: 'none' }}>
                  <CloudOutlined style={{ fontSize: 32, color: '#11998e', marginBottom: 8 }} />
                  <div style={{ fontSize: 24, fontWeight: 700 }}>56</div>
                  <div style={{ fontSize: 13, color: '#666' }}>云资源</div>
                </Card>
              </Col>
              <Col span={8}>
                <Card style={{ textAlign: 'center', background: '#f8f9fa', border: 'none' }}>
                  <UserOutlined style={{ fontSize: 32, color: '#fc4a1a', marginBottom: 8 }} />
                  <div style={{ fontSize: 24, fontWeight: 700 }}>42</div>
                  <div style={{ fontSize: 13, color: '#666' }}>系统账号</div>
                </Card>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default Dashboard;
