/**
 * 仪表盘页面
 * 展示任务统计、待办事项
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Row, Col, Statistic, Button, List, Tag, Spin } from 'antd';
import {
  FileTextOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  PlusOutlined,
} from '@ant-design/icons';
import { dashboardApi } from '../../api/dashboard';

function Dashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await dashboardApi.getOverview();
      setData(response.data);
    } catch (error) {
      console.error('获取仪表盘数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" />
      </div>
    );
  }

  const { task_stats, my_tasks } = data || {};

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between' }}>
        <h2 style={{ margin: 0 }}>仪表盘</h2>
        <Button 
          type="primary" 
          icon={<PlusOutlined />}
          onClick={() => navigate('/admission-tasks/new')}
        >
          创建准入任务
        </Button>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总任务数"
              value={task_stats?.total || 0}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="进行中"
              value={task_stats?.in_progress || 0}
              valueStyle={{ color: '#1890ff' }}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待审核"
              value={task_stats?.pending_review || 0}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已通过"
              value={task_stats?.passed || 0}
              valueStyle={{ color: '#52c41a' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 我的任务 */}
      <Row gutter={16}>
        <Col span={12}>
          <Card title="我的任务" bordered={false}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic title="分配给我" value={my_tasks?.assigned || 0} />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="待处理" 
                  value={my_tasks?.pending || 0}
                  valueStyle={{ color: '#ff4d4f' }}
                />
              </Col>
            </Row>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="快速入口" bordered={false}>
            <Button 
              type="primary" 
              block 
              style={{ marginBottom: 8 }}
              onClick={() => navigate('/admission-tasks')}
            >
              查看所有任务
            </Button>
            <Button block onClick={() => navigate('/admission-tasks/new')}>
              创建新任务
            </Button>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default Dashboard;
