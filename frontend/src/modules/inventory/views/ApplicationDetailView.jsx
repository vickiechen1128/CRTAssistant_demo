/**
 * ApplicationDetailView 组件
 * 应用系统详情页面
 */
import React, { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Card,
  Button,
  Descriptions,
  Tag,
  Space,
  Typography,
  Spin,
  message,
} from 'antd';
import { ArrowLeftOutlined, EditOutlined } from '@ant-design/icons';
import { useInventoryStore } from '../store';

const { Title } = Typography;

// 状态映射
const statusMap = {
  active: { label: '活跃', color: 'success' },
  inactive: { label: '停用', color: 'default' },
  archived: { label: '已归档', color: 'warning' },
  expired: { label: '已过期', color: 'error' },
};

/**
 * ApplicationDetailView 组件
 */
const ApplicationDetailView = () => {
  const navigate = useNavigate();
  const { id } = useParams();

  const {
    currentApplication,
    loading,
    fetchApplicationDetail,
  } = useInventoryStore();

  // 加载详情数据
  useEffect(() => {
    if (id) {
      fetchApplicationDetail(id).catch((error) => {
        message.error('获取应用系统详情失败: ' + (error.message || '未知错误'));
      });
    }
  }, [id, fetchApplicationDetail]);

  // 获取状态显示
  const getStatusTag = (status) => {
    const config = statusMap[status] || { label: status, color: 'default' };
    return <Tag color={config.color}>{config.label}</Tag>;
  };

  if (loading || !currentApplication) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/inventories')}>
            返回
          </Button>
          <Title level={4} style={{ margin: 0 }}>应用系统详情</Title>
        </Space>
      </Card>

      <Card
        extra={
          <Button
            type="primary"
            icon={<EditOutlined />}
            onClick={() => navigate(`/inventories/applications/${id}/edit`)}
          >
            编辑
          </Button>
        }
      >
        <Descriptions bordered column={2}>
          <Descriptions.Item label="应用名称">
            {currentApplication.app_name}
          </Descriptions.Item>
          <Descriptions.Item label="状态">
            {getStatusTag(currentApplication.status)}
          </Descriptions.Item>
          <Descriptions.Item label="业务负责人">
            {currentApplication.business_owner}
          </Descriptions.Item>
          <Descriptions.Item label="项目负责人">
            {currentApplication.project_owner}
          </Descriptions.Item>
          <Descriptions.Item label="主机名">
            {currentApplication.hostname || '-'}
          </Descriptions.Item>
          <Descriptions.Item label="上线时间">
            {currentApplication.launch_time || '-'}
          </Descriptions.Item>
          <Descriptions.Item label="创建时间">
            {currentApplication.created_at}
          </Descriptions.Item>
          <Descriptions.Item label="更新时间">
            {currentApplication.updated_at}
          </Descriptions.Item>
          <Descriptions.Item label="应用描述" span={2}>
            {currentApplication.app_description || '-'}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
};

export default ApplicationDetailView;
