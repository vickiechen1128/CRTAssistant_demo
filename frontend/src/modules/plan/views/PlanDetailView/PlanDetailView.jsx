/**
 * PlanDetailView 组件
 * 计划详情页面
 */
import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Descriptions,
  Tag,
  Space,
  Button,
  Spin,
  message,
  Tabs,
  Timeline,
  Table,
  Typography,
} from 'antd';
import {
  EditOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons';
import { usePlanStore } from '../../store';
import PlanStatusBadge from '../../components/PlanStatusBadge';
import {
  categoryOptions,
  priorityOptions,
  PlanStatus,
} from '../../api/types';

const { TabPane } = Tabs;
const { Title } = Typography;

/**
 * PlanDetailView 组件
 */
const PlanDetailView = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const {
    currentPlan,
    loading,
    fetchPlanDetail,
    startExistingPlan,
    completeExistingPlan,
    cancelExistingPlan,
    clearCurrentPlan,
  } = usePlanStore();

  // 加载计划详情
  useEffect(() => {
    fetchPlanDetail(id);

    // 清理
    return () => {
      clearCurrentPlan();
    };
  }, [id]);

  // 获取分类标签
  const getCategoryLabel = (category) => {
    const config = categoryOptions.find((opt) => opt.value === category);
    return config?.label || category;
  };

  // 获取优先级标签
  const getPriorityLabel = (priority) => {
    const config = priorityOptions.find((opt) => opt.value === priority);
    return config?.label || priority;
  };

  // 格式化日期
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('zh-CN');
  };

  // 处理启动
  const handleStart = async () => {
    try {
      await startExistingPlan(id);
      message.success('计划已启动');
    } catch (error) {
      message.error('启动失败');
    }
  };

  // 处理完成
  const handleComplete = async () => {
    try {
      await completeExistingPlan(id);
      message.success('计划已完成');
    } catch (error) {
      message.error('操作失败');
    }
  };

  // 处理取消
  const handleCancel = async () => {
    try {
      await cancelExistingPlan(id, '手动取消');
      message.success('计划已取消');
    } catch (error) {
      message.error('取消失败');
    }
  };

  // 渲染操作按钮
  const renderActions = () => {
    if (!currentPlan) return null;

    const { status } = currentPlan;
    const isDraft = status === PlanStatus.DRAFT;
    const isPending = status === PlanStatus.PENDING;
    const isInProgress = status === PlanStatus.IN_PROGRESS;

    return (
      <Space>
        {isDraft && (
          <Button
            icon={<EditOutlined />}
            onClick={() => navigate(`/plans/${id}/edit`)}
          >
            编辑
          </Button>
        )}

        {(isDraft || isPending) && (
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={handleStart}
          >
            启动计划
          </Button>
        )}

        {isInProgress && (
          <Button
            type="primary"
            icon={<CheckCircleOutlined />}
            onClick={handleComplete}
          >
            完成计划
          </Button>
        )}

        {(isDraft || isPending || isInProgress) && (
          <Button
            danger
            icon={<CloseCircleOutlined />}
            onClick={handleCancel}
          >
            取消计划
          </Button>
        )}
      </Space>
    );
  };

  if (loading || !currentPlan) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Space>
            <Button 
              icon={<ArrowLeftOutlined />} 
              onClick={() => navigate('/plans')}
            >
              返回
            </Button>
            <Title level={4} style={{ margin: 0 }}>{currentPlan.name}</Title>
            <Tag>{currentPlan.data_tag}</Tag>
            <PlanStatusBadge status={currentPlan.status} />
          </Space>
          <div style={{ marginLeft: 'auto' }}>{renderActions()}</div>
        </Space>
      </Card>

      <Tabs defaultActiveKey="overview">
        <TabPane tab="概览" key="overview">
          <Card>
            <Descriptions title="基本信息" bordered column={2}>
              <Descriptions.Item label="计划名称">
                {currentPlan.name}
              </Descriptions.Item>
              <Descriptions.Item label="数据标签">
                {currentPlan.data_tag}
              </Descriptions.Item>
              <Descriptions.Item label="计划分类">
                {getCategoryLabel(currentPlan.category)}
              </Descriptions.Item>
              <Descriptions.Item label="优先级">
                <Tag
                  color={
                    priorityOptions.find(
                      (opt) => opt.value === currentPlan.priority
                    )?.color
                  }
                >
                  {getPriorityLabel(currentPlan.priority)}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="计划开始时间">
                {formatDate(currentPlan.planned_start_time)}
              </Descriptions.Item>
              <Descriptions.Item label="计划结束时间">
                {formatDate(currentPlan.planned_end_time)}
              </Descriptions.Item>
              <Descriptions.Item label="实际开始时间">
                {formatDate(currentPlan.actual_start_time)}
              </Descriptions.Item>
              <Descriptions.Item label="实际结束时间">
                {formatDate(currentPlan.actual_end_time)}
              </Descriptions.Item>
              <Descriptions.Item label="创建人">
                {currentPlan.created_by}
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">
                {formatDate(currentPlan.created_at)}
              </Descriptions.Item>
            </Descriptions>

            {currentPlan.description && (
              <Descriptions title="计划说明" style={{ marginTop: 24 }}>
                <Descriptions.Item>
                  {currentPlan.description}
                </Descriptions.Item>
              </Descriptions>
            )}
          </Card>
        </TabPane>

        <TabPane tab="台账范围" key="inventory">
          <Card>
            {currentPlan.inventory_ids && currentPlan.inventory_ids.length > 0 ? (
              <Table
                dataSource={currentPlan.inventory_ids.map((id, index) => ({
                  key: index,
                  id,
                  name: `应用系统 ${id}`,
                }))}
                columns={[
                  { title: '台账ID', dataIndex: 'id' },
                  { title: '应用名称', dataIndex: 'name' },
                ]}
                pagination={false}
              />
            ) : (
              <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                未关联台账
              </div>
            )}
          </Card>
        </TabPane>

        <TabPane tab="审批材料" key="files">
          <Card>
            {currentPlan.approval_files && currentPlan.approval_files.length > 0 ? (
              <Timeline>
                {currentPlan.approval_files.map((file, index) => (
                  <Timeline.Item key={index}>
                    <a href={file.file_url} target="_blank" rel="noopener noreferrer">
                      {file.file_name}
                    </a>
                    <span style={{ marginLeft: 16, color: '#999' }}>
                      {formatDate(file.uploaded_at)}
                    </span>
                  </Timeline.Item>
                ))}
              </Timeline>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                无审批材料
              </div>
            )}
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default PlanDetailView;
