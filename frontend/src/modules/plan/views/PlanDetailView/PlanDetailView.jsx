/**
 * PlanDetailView 组件
 * 计划详情页面（优化版）
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
  Badge,
  Row,
  Col,
  Divider,
} from 'antd';
import {
  EditOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ArrowLeftOutlined,
  AppstoreOutlined,
  FileTextOutlined,
  HistoryOutlined,
  RocketOutlined,
  TagOutlined,
} from '@ant-design/icons';
import { usePlanStore } from '../../store';
import PlanStatusBadge from '../../components/PlanStatusBadge';
import {
  categoryOptions,
  priorityOptions,
  PlanStatus,
  moduleActionOptions,
  getModuleActionConfig,
} from '../../api/types';

const { TabPane } = Tabs;
const { Title, Text } = Typography;

/**
 * 计划详情页面
 */
const PlanDetailView = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const {
    currentPlan,
    currentPlanDetail,
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

        {/* PRD v3.1: IN_PROGRESS 状态不允许取消 */}
        {(isDraft || isPending) && (
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

  // 使用详细的计划数据
  const plan = currentPlanDetail || currentPlan;

  if (loading || !plan) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  // 模块表格列
  const moduleColumns = [
    {
      title: '模块名称',
      dataIndex: 'module_name',
      key: 'module_name',
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
      render: (action) => {
        const config = getModuleActionConfig(action);
        return <Tag color={config?.color}>{config?.label}</Tag>;
      },
    },
    {
      title: '版本变更',
      key: 'version',
      render: (_, record) => (
        <span>
          {record.before_version || '-'}
          {' → '}
          {record.after_version || '-'}
        </span>
      ),
    },
    {
      title: '变更说明',
      dataIndex: 'change_description',
      key: 'change_description',
      ellipsis: true,
    },
  ];

  return (
    <div>
      {/* 头部信息 */}
      <Card style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Space>
            <Button 
              icon={<ArrowLeftOutlined />} 
              onClick={() => navigate('/plans')}
            >
              返回
            </Button>
            <Title level={4} style={{ margin: 0 }}>{plan.name}</Title>
            <Tag icon={<TagOutlined />}>{plan.data_tag}</Tag>
            <PlanStatusBadge status={plan.status} />
          </Space>
          <div style={{ marginLeft: 'auto' }}>{renderActions()}</div>
        </Space>
      </Card>

      <Tabs defaultActiveKey="overview">
        {/* 概览 Tab */}
        <TabPane 
          tab={<span><AppstoreOutlined />概览</span>} 
          key="overview"
        >
          <Row gutter={[16, 16]}>
            <Col span={16}>
              <Card title="基本信息">
                <Descriptions bordered column={2} size="small">
                  <Descriptions.Item label="计划名称">
                    {plan.name}
                  </Descriptions.Item>
                  <Descriptions.Item label="数据标签">
                    {plan.data_tag}
                  </Descriptions.Item>
                  <Descriptions.Item label="计划分类">
                    {getCategoryLabel(plan.category)}
                  </Descriptions.Item>
                  <Descriptions.Item label="优先级">
                    <Tag
                      color={
                        priorityOptions.find(
                          (opt) => opt.value === plan.priority
                        )?.color
                      }
                    >
                      {getPriorityLabel(plan.priority)}
                    </Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="模板类型">
                    {plan.template_type}
                  </Descriptions.Item>
                  <Descriptions.Item label="状态">
                    <PlanStatusBadge status={plan.status} />
                  </Descriptions.Item>
                  <Descriptions.Item label="计划开始时间">
                    {formatDate(plan.planned_start_time)}
                  </Descriptions.Item>
                  <Descriptions.Item label="计划结束时间">
                    {formatDate(plan.planned_end_time)}
                  </Descriptions.Item>
                  <Descriptions.Item label="实际开始时间">
                    {formatDate(plan.actual_start_time)}
                  </Descriptions.Item>
                  <Descriptions.Item label="实际结束时间">
                    {formatDate(plan.actual_end_time)}
                  </Descriptions.Item>
                  <Descriptions.Item label="创建人">
                    {plan.created_by}
                  </Descriptions.Item>
                  <Descriptions.Item label="创建时间">
                    {formatDate(plan.created_at)}
                  </Descriptions.Item>
                </Descriptions>

                {plan.description && (
                  <>
                    <Divider />
                    <Descriptions title="计划说明">
                      <Descriptions.Item>
                        {plan.description}
                      </Descriptions.Item>
                    </Descriptions>
                  </>
                )}
              </Card>
            </Col>
            
            <Col span={8}>
              <Card title="统计信息">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Text>关联应用系统</Text>
                    <Badge 
                      count={plan.related_inventory_ids?.length || 0} 
                      style={{ backgroundColor: '#52c41a' }} 
                    />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Text>影响功能模块</Text>
                    <Badge 
                      count={plan.affected_modules_count || 0} 
                      style={{ backgroundColor: '#1890ff' }} 
                    />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Text>审批材料</Text>
                    <Badge 
                      count={plan.approval_files?.length || 0} 
                      style={{ backgroundColor: '#faad14' }} 
                    />
                  </div>
                </Space>
              </Card>
            </Col>
          </Row>
        </TabPane>

        {/* 台账范围 Tab */}
        <TabPane 
          tab={<span><AppstoreOutlined />台账范围</span>} 
          key="inventory"
        >
          <Card title="关联应用系统">
            {plan.related_applications && plan.related_applications.length > 0 ? (
              <Table
                dataSource={plan.related_applications}
                rowKey="id"
                columns={[
                  { title: '应用名称', dataIndex: 'app_name' },
                  { title: '系统类型', dataIndex: 'system_type' },
                  { title: '业务负责人', dataIndex: 'business_owner' },
                  { title: '项目负责人', dataIndex: 'project_owner' },
                  { title: '状态', dataIndex: 'status' },
                  {
                    title: '操作',
                    render: (_, record) => (
                      <Button type="link" onClick={() => navigate(record.view_url)}>
                        查看详情
                      </Button>
                    ),
                  },
                ]}
                pagination={false}
              />
            ) : plan.related_inventory_ids && plan.related_inventory_ids.length > 0 ? (
              <Table
                dataSource={plan.related_inventory_ids.map((id, index) => ({
                  key: index,
                  id,
                  name: `应用系统 ${id}`,
                }))}
                rowKey="id"
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

          {/* 影响功能模块 */}
          {plan.affected_modules && plan.affected_modules.length > 0 && (
            <Card title="影响功能模块" style={{ marginTop: 16 }}>
              <Table
                dataSource={plan.affected_modules}
                columns={moduleColumns}
                rowKey="module_id"
                pagination={false}
              />
            </Card>
          )}
        </TabPane>

        {/* 生命周期 Tab */}
        <TabPane 
          tab={<span><HistoryOutlined />生命周期</span>} 
          key="lifecycle"
        >
          <Card>
            {plan.lifecycle_logs && plan.lifecycle_logs.length > 0 ? (
              <Timeline mode="left">
                {plan.lifecycle_logs.map((log, index) => (
                  <Timeline.Item
                    key={index}
                    dot={<RocketOutlined style={{ color: '#52c41a' }} />}
                    label={formatDate(log.operation_time)}
                  >
                    <Card size="small" style={{ marginBottom: 8 }}>
                      <p style={{ marginBottom: 4 }}>
                        <Tag color="green">{log.log_type_label}</Tag>
                      </p>
                      <p style={{ fontWeight: 'bold' }}>{log.event_title}</p>
                      {log.module_name && (
                        <p style={{ color: '#666' }}>
                          模块: {log.module_name}
                        </p>
                      )}
                      <p style={{ color: '#999', fontSize: 12 }}>
                        操作人: {log.operator}
                      </p>
                    </Card>
                  </Timeline.Item>
                ))}
              </Timeline>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                暂无生命周期日志
              </div>
            )}
          </Card>
        </TabPane>

        {/* 审批材料 Tab */}
        <TabPane 
          tab={<span><FileTextOutlined />审批材料</span>} 
          key="files"
        >
          <Card>
            {plan.approval_files && plan.approval_files.length > 0 ? (
              <Timeline>
                {plan.approval_files.map((file, index) => (
                  <Timeline.Item key={index}>
                    <Card size="small">
                      <p>
                        <a href={file.file_url} target="_blank" rel="noopener noreferrer">
                          {file.file_name}
                        </a>
                      </p>
                      <p style={{ color: '#999', fontSize: 12 }}>
                        {(file.file_size / 1024 / 1024).toFixed(2)} MB · 
                        {formatDate(file.uploaded_at)}
                      </p>
                    </Card>
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

        {/* 工作流 Tab */}
        {plan.workflow && (
          <TabPane 
            tab={<span><RocketOutlined />工作流</span>} 
            key="workflow"
          >
            <Card title="工作流信息">
              <Descriptions bordered column={1} size="small">
                <Descriptions.Item label="模板类型">
                  {plan.workflow.template_type}
                </Descriptions.Item>
                <Descriptions.Item label="进度">
                  {plan.workflow.progress}%
                </Descriptions.Item>
              </Descriptions>
              
              {plan.workflow.work_items && plan.workflow.work_items.length > 0 && (
                <>
                  <Divider />
                  <Table
                    dataSource={plan.workflow.work_items}
                    rowKey="id"
                    columns={[
                      { title: '检查项', dataIndex: 'name' },
                      { title: '状态', dataIndex: 'status' },
                      { title: '负责人', dataIndex: 'assignee' },
                    ]}
                    pagination={false}
                  />
                </>
              )}
            </Card>
          </TabPane>
        )}
      </Tabs>
    </div>
  );
};

export default PlanDetailView;
