/**
 * ApplicationDetailViewEnhanced 组件
 * 增强版应用系统详情页面 - 集成功能模块管理和生命周期日志
 */
import React, { useEffect, useState } from 'react';
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
  Tabs,
  Row,
  Col,
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  BranchesOutlined,
  HistoryOutlined,
  CloudServerOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { useInventoryStore } from '../store';
import { FunctionModuleManager, LifecycleLogViewer } from '../components';

const { Title } = Typography;
const { TabPane } = Tabs;

// 状态映射
const statusMap = {
  active: { label: '活跃', color: 'success' },
  inactive: { label: '停用', color: 'default' },
  archived: { label: '已归档', color: 'warning' },
  expired: { label: '已过期', color: 'error' },
};

/**
 * ApplicationDetailViewEnhanced 组件
 */
const ApplicationDetailViewEnhanced = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [activeTab, setActiveTab] = useState('overview');

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
      {/* 顶部导航 */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/inventories')}>
            返回
          </Button>
          <Title level={4} style={{ margin: 0 }}>
            {currentApplication.app_name}
          </Title>
          {getStatusTag(currentApplication.status)}
          <Button
            type="primary"
            icon={<EditOutlined />}
            onClick={() => navigate(`/inventories/applications/${id}/edit`)}
          >
            编辑
          </Button>
        </Space>
      </Card>

      {/* 标签页内容 */}
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        type="card"
      >
        {/* 概览标签 */}
        <TabPane
          tab={
            <span>
              <CloudServerOutlined />
              概览
            </span>
          }
          key="overview"
        >
          <Row gutter={[16, 16]}>
            <Col span={24}>
              <Card title="基本信息">
                <Descriptions bordered column={2}>
                  <Descriptions.Item label="应用ID">
                    <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>{currentApplication.id}</span>
                  </Descriptions.Item>
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
                  <Descriptions.Item label="应用URL">
                    {currentApplication.app_url ? (
                      <a href={currentApplication.app_url} target="_blank" rel="noopener noreferrer">
                        {currentApplication.app_url}
                      </a>
                    ) : (
                      '-'
                    )}
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
                  <Descriptions.Item label="关联计划">
                    {currentApplication.related_plan_ids?.length > 0 ? (
                      <Space size="small">
                        {currentApplication.related_plan_ids.map((planId) => (
                          <Tag key={planId} color="blue">
                            {planId}
                          </Tag>
                        ))}
                      </Space>
                    ) : (
                      '-'
                    )}
                  </Descriptions.Item>
                  <Descriptions.Item label="应用描述" span={2}>
                    {currentApplication.app_description || '-'}
                  </Descriptions.Item>
                </Descriptions>
              </Card>
            </Col>
          </Row>
        </TabPane>

        {/* 功能模块标签 */}
        <TabPane
          tab={
            <span>
              <BranchesOutlined />
              功能模块
            </span>
          }
          key="modules"
        >
          <FunctionModuleManager 
            appId={id} 
            relatedPlanId={currentApplication.related_plan_ids?.[0]}
          />
        </TabPane>

        {/* 生命周期日志标签 */}
        <TabPane
          tab={
            <span>
              <HistoryOutlined />
              生命周期日志
            </span>
          }
          key="logs"
        >
          <LifecycleLogViewer appId={id} />
        </TabPane>

        {/* 云资源标签 */}
        <TabPane
          tab={
            <span>
              <CloudServerOutlined />
              云资源
            </span>
          }
          key="resources"
        >
          <Card title="云资源列表">
            <div style={{ textAlign: 'center', padding: 40 }}>
              <p>云资源管理功能开发中...</p>
              <Button type="primary" onClick={() => navigate(`/inventories/cloud-resources/create?app_id=${id}`)}>
                添加云资源
              </Button>
            </div>
          </Card>
        </TabPane>

        {/* 账号标签 */}
        <TabPane
          tab={
            <span>
              <UserOutlined />
              账号
            </span>
          }
          key="accounts"
        >
          <Card title="系统账号列表">
            <div style={{ textAlign: 'center', padding: 40 }}>
              <p>账号管理功能开发中...</p>
              <Button type="primary" onClick={() => navigate(`/inventories/accounts/create?app_id=${id}`)}>
                添加账号
              </Button>
            </div>
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default ApplicationDetailViewEnhanced;
