/**
 * 任务详情页面
 * 展示任务基本信息、检查项、台账等
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Descriptions, Tag, Progress, Button, Tabs, Table, Space, message, Row, Col, Statistic, Timeline, Badge } from 'antd';
import { ArrowLeftOutlined, PlayCircleOutlined, CheckCircleOutlined, ClockCircleOutlined, FileTextOutlined, DatabaseOutlined, CloudOutlined, SafetyOutlined, ToolOutlined } from '@ant-design/icons';
import { taskApi } from '../../../api/tasks';
import { checklistApi } from '../../../api/checklist';
import { inventoryApi } from '../../../api/inventory';
import { verificationApi } from '../../../api/verification';
import DeliverableUpload from '../../../components/DeliverableUpload';
import DeliverableReview from '../../../components/DeliverableReview';

const { TabPane } = Tabs;

// 状态映射
const statusMap = {
  draft: { text: '草稿', color: 'default' },
  in_progress: { text: '进行中', color: 'processing' },
  pending_review: { text: '待审核', color: 'warning' },
  passed: { text: '已通过', color: 'success' },
  rejected: { text: '已驳回', color: 'error' },
};

// 管控维度映射
const dimensionMap = {
  inventory: '台账收集',
  baseline: '系统基线',
  deployment: '软件部署',
  security: '系统安全',
  monitoring: '监控告警',
};

function TaskDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [task, setTask] = useState(null);
  const [checklist, setChecklist] = useState([]);
  const [inventories, setInventories] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [expandedRowKeys, setExpandedRowKeys] = useState([]);
  const [reviewModalVisible, setReviewModalVisible] = useState(false);
  const [currentReviewItem, setCurrentReviewItem] = useState(null);

  useEffect(() => {
    if (id) {
      fetchTaskDetail();
      fetchChecklist();
      fetchInventories();
    }
  }, [id]);

  const fetchTaskDetail = async () => {
    setLoading(true);
    try {
      const response = await taskApi.get(id);
      setTask(response.data);
    } catch (error) {
      message.error('获取任务详情失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchChecklist = async () => {
    try {
      const response = await checklistApi.list({ task_id: id });
      setChecklist(response.data.items);
    } catch (error) {
      console.error('获取检查项失败:', error);
    }
  };

  const fetchInventories = async () => {
    try {
      const response = await inventoryApi.list(id);
      setInventories(response.data.items || []);
    } catch (error) {
      console.error('获取台账列表失败:', error);
    }
  };

  const handleStartTask = async () => {
    try {
      await taskApi.start(id);
      message.success('任务已启动');
      fetchTaskDetail();
    } catch (error) {
      message.error('启动任务失败');
    }
  };

  const handleVerifyItem = async (itemId, status) => {
    try {
      await checklistApi.verify(itemId, { status, remark: '' });
      message.success('操作成功');
      fetchChecklist();
      fetchTaskDetail();
    } catch (error) {
      message.error('操作失败');
    }
  };

  // 打开审核弹窗
  const handleOpenReview = (record) => {
    setCurrentReviewItem(record);
    setReviewModalVisible(true);
  };

  // 检查项表格列
  const checklistColumns = [
    {
      title: '检查项',
      dataIndex: 'item_name',
      render: (text, record) => (
        <div>
          <div>{text}</div>
          <div style={{ fontSize: 12, color: '#999' }}>{dimensionMap[record.control_dimension]}</div>
        </div>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (status) => {
        const config = statusMap[status] || { text: status, color: 'default' };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '负责人',
      dataIndex: ['assignee', 'real_name'],
      width: 100,
    },
    {
      title: '交付物',
      width: 100,
      render: (_, record) => (
        <span>
          {record.deliverable_count > 0 ? (
            <Tag color="blue">{record.deliverable_count} 个</Tag>
          ) : (
            <span style={{ color: '#999' }}>-</span>
          )}
        </span>
      ),
    },
    {
      title: '操作',
      width: 200,
      render: (_, record) => (
        <Space>
          <Button 
            type="link" 
            size="small"
            onClick={() => {
              const newKeys = expandedRowKeys.includes(record.id)
                ? expandedRowKeys.filter(key => key !== record.id)
                : [...expandedRowKeys, record.id];
              setExpandedRowKeys(newKeys);
            }}
          >
            {expandedRowKeys.includes(record.id) ? '收起' : '展开'}
          </Button>
          {record.status === 'pending' && (
            <Button 
              type="link" 
              size="small"
              onClick={() => handleVerifyItem(record.id, 'passed')}
            >
              确认
            </Button>
          )}
          {record.status === 'in_progress' && (
            <>
              <Button 
                type="link" 
                size="small"
                onClick={() => handleOpenReview(record)}
              >
                审核
              </Button>
            </>
          )}
        </Space>
      ),
    },
  ];

  // 展开行渲染 - 交付物上传区域
  const expandedRowRender = (record) => {
    return (
      <div style={{ padding: '16px 24px', background: '#fafafa' }}>
        <DeliverableUpload 
          checklistItemId={record.id}
          readOnly={record.status === 'passed' || record.status === 'rejected'}
          onUploadSuccess={() => {
            fetchChecklist();
          }}
        />
      </div>
    );
  };

  if (loading) {
    return <Card loading />;
  }

  if (!task) {
    return <div>任务不存在</div>;
  }

  return (
    <div>
      {/* 返回按钮 */}
      <Button 
        icon={<ArrowLeftOutlined />} 
        onClick={() => navigate('/admission-tasks')}
        style={{ marginBottom: 16 }}
      >
        返回列表
      </Button>

      {/* 任务标题 */}
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ margin: 0, marginBottom: 8 }}>
          {task.system_name} {task.version}
        </h2>
        <Space>
          <Tag color={statusMap[task.status]?.color}>
            {statusMap[task.status]?.text}
          </Tag>
          <span>任务编号: {task.task_no}</span>
        </Space>
      </div>

      {/* 启动按钮 */}
      {task.status === 'draft' && (
        <Button 
          type="primary" 
          icon={<PlayCircleOutlined />}
          onClick={handleStartTask}
          style={{ marginBottom: 16 }}
        >
          启动任务
        </Button>
      )}

      {/* Tab切换 */}
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="概览" key="overview">
          <Row gutter={[16, 16]}>
            {/* 基本信息 */}
            <Col span={24}>
              <Card title="基本信息">
                <Descriptions bordered column={2}>
                  <Descriptions.Item label="系统编码">{task.system_code}</Descriptions.Item>
                  <Descriptions.Item label="版本">{task.version}</Descriptions.Item>
                  <Descriptions.Item label="计划上线">{task.release_date}</Descriptions.Item>
                  <Descriptions.Item label="当前进度">
                    <Progress percent={task.progress} size="small" />
                  </Descriptions.Item>
                  <Descriptions.Item label="创建人">{task.creator?.real_name}</Descriptions.Item>
                  <Descriptions.Item label="负责人">{task.manager?.real_name}</Descriptions.Item>
                </Descriptions>
              </Card>
            </Col>

            {/* 进度追踪面板 */}
            <Col span={24}>
              <Card title="进度追踪">
                <Row gutter={16}>
                  {task.control_dimension_progress && Object.entries(task.control_dimension_progress).map(([dim, progress]) => {
                    const percent = progress.total > 0 ? Math.round(progress.completed / progress.total * 100) : 0;
                    const iconMap = {
                      inventory: <DatabaseOutlined />,
                      baseline: <ToolOutlined />,
                      deployment: <CloudOutlined />,
                      security: <SafetyOutlined />,
                      monitoring: <FileTextOutlined />,
                    };
                    return (
                      <Col span={12} md={8} lg={4} key={dim}>
                        <Card size="small" style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: 24, marginBottom: 8, color: percent === 100 ? '#52c41a' : '#1890ff' }}>
                            {iconMap[dim]}
                          </div>
                          <div style={{ fontSize: 12, color: '#666', marginBottom: 8 }}>{dimensionMap[dim]}</div>
                          <Progress 
                            percent={percent} 
                            size="small" 
                            status={percent === 100 ? 'success' : 'active'}
                          />
                          <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
                            {progress.completed}/{progress.total}
                          </div>
                        </Card>
                      </Col>
                    );
                  })}
                </Row>
              </Card>
            </Col>

            {/* 任务时间线 */}
            <Col span={24}>
              <Card title="任务进展">
                <Timeline mode="left">
                  <Timeline.Item dot={<CheckCircleOutlined style={{ color: '#52c41a' }} />}>
                    <div>任务创建</div>
                    <div style={{ fontSize: 12, color: '#999' }}>{task.created_at || '-'}</div>
                  </Timeline.Item>
                  <Timeline.Item dot={task.status !== 'draft' ? <CheckCircleOutlined style={{ color: '#52c41a' }} /> : <ClockCircleOutlined />}>
                    <div>任务启动</div>
                    <div style={{ fontSize: 12, color: '#999' }}>{task.started_at || '待启动'}</div>
                  </Timeline.Item>
                  <Timeline.Item dot={task.progress >= 50 ? <CheckCircleOutlined style={{ color: '#52c41a' }} /> : <ClockCircleOutlined />}>
                    <div>检查项执行中</div>
                    <div style={{ fontSize: 12, color: '#999' }}>当前进度 {task.progress || 0}%</div>
                  </Timeline.Item>
                  <Timeline.Item dot={task.status === 'passed' ? <CheckCircleOutlined style={{ color: '#52c41a' }} /> : <ClockCircleOutlined />}>
                    <div>任务完成</div>
                    <div style={{ fontSize: 12, color: '#999' }}>{task.status === 'passed' ? '已完成' : '待完成'}</div>
                  </Timeline.Item>
                </Timeline>
              </Card>
            </Col>
          </Row>
        </TabPane>

        <TabPane tab={`检查项 (${task.checklist_summary?.total || 0})`} key="checklist">
          <Card>
            <Table
              rowKey="id"
              columns={checklistColumns}
              dataSource={checklist}
              pagination={false}
              expandable={{
                expandedRowKeys,
                onExpandedRowsChange: setExpandedRowKeys,
                expandedRowRender,
              }}
            />
          </Card>
        </TabPane>

        <TabPane tab={`台账 (${inventories.length})`} key="inventories">
          <Card>
            <InventoryTab 
              inventories={inventories} 
              taskId={id}
              onRefresh={fetchInventories}
            />
          </Card>
        </TabPane>

        {/* 交付物Tab - 按检查项分组展示 */}
        <TabPane tab="交付物" key="deliverables">
          <Card>
            <DeliverablesTab checklist={checklist} taskId={id} />
          </Card>
        </TabPane>

        {/* 验证记录Tab */}
        <TabPane tab="验证记录" key="verification">
          <Card>
            <VerificationRecordsTab taskId={id} />
          </Card>
        </TabPane>
      </Tabs>

      {/* 交付物审核弹窗 */}
      <DeliverableReview
        visible={reviewModalVisible}
        checklistItemId={currentReviewItem?.id}
        checklistItemName={currentReviewItem?.item_name}
        deliverables={currentReviewItem?.deliverables || []}
        onCancel={() => {
          setReviewModalVisible(false);
          setCurrentReviewItem(null);
        }}
        onSuccess={() => {
          fetchChecklist();
          fetchTaskDetail();
        }}
      />
    </div>
  );
}

// 台账类型映射
const inventoryTypeMap = {
  server: { text: '应用系统台账', color: 'blue', icon: '🖥️' },
  cloud_resource: { text: '云服务开通台账', color: 'green', icon: '☁️' },
  account: { text: '系统账户台账', color: 'orange', icon: '👤' },
};

// 台账状态映射
const inventoryStatusMap = {
  draft: { text: '草稿', color: 'default' },
  filling: { text: '填写中', color: 'processing' },
  submitted: { text: '已提交', color: 'warning' },
  confirmed: { text: '已确认', color: 'success' },
  expired: { text: '已过期', color: 'error' },
};

// 台账Tab组件
function InventoryTab({ inventories, taskId, onRefresh }) {
  const navigate = useNavigate();

  // 按类型分组
  const groupedInventories = {
    server: inventories.filter(inv => inv.inventory_type === 'server'),
    cloud_resource: inventories.filter(inv => inv.inventory_type === 'cloud_resource'),
    account: inventories.filter(inv => inv.inventory_type === 'account'),
  };

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button 
          type="primary" 
          onClick={() => navigate(`/inventories/task/${taskId}`)}
        >
          管理台账
        </Button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
        {Object.entries(groupedInventories).map(([type, items]) => {
          const config = inventoryTypeMap[type];
          return (
            <Card 
              key={type}
              size="small"
              title={
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span>{config.icon}</span>
                  <span>{config.text}</span>
                  <Tag color={config.color}>{items.length}</Tag>
                </div>
              }
            >
              {items.length === 0 ? (
                <div style={{ textAlign: 'center', color: '#999', padding: '20px 0' }}>
                  暂无数据
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {items.slice(0, 3).map(inv => (
                    <div 
                      key={inv.id}
                      style={{ 
                        display: 'flex', 
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '8px 12px',
                        background: '#f5f5f5',
                        borderRadius: 4,
                        cursor: 'pointer',
                      }}
                      onClick={() => navigate(`/inventories/${inv.id}`)}
                    >
                      <span>台账 #{inv.id}</span>
                      <Tag color={inventoryStatusMap[inv.status]?.color}>
                        {inventoryStatusMap[inv.status]?.text}
                      </Tag>
                    </div>
                  ))}
                  {items.length > 3 && (
                    <div style={{ textAlign: 'center', color: '#999', fontSize: 12 }}>
                      还有 {items.length - 3} 条...
                    </div>
                  )}
                </div>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
}

// 交付物Tab组件 - 按检查项分组展示
function DeliverablesTab({ checklist, taskId }) {
  const [selectedItem, setSelectedItem] = useState(null);

  // 过滤有交付物的检查项
  const itemsWithDeliverables = checklist.filter(item => item.deliverable_count > 0);

  return (
    <div>
      <Row gutter={[16, 16]}>
        {/* 左侧检查项列表 */}
        <Col span={8}>
          <Card title="检查项" size="small">
            {itemsWithDeliverables.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
                暂无交付物
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {itemsWithDeliverables.map(item => (
                  <div
                    key={item.id}
                    onClick={() => setSelectedItem(item)}
                    style={{
                      padding: '12px 16px',
                      background: selectedItem?.id === item.id ? '#e6f7ff' : '#f5f5f5',
                      borderRadius: 4,
                      cursor: 'pointer',
                      borderLeft: selectedItem?.id === item.id ? '3px solid #1890ff' : '3px solid transparent',
                    }}
                  >
                    <div style={{ fontWeight: 500 }}>{item.item_name}</div>
                    <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
                      {dimensionMap[item.control_dimension]} · {item.deliverable_count} 个交付物
                    </div>
                    <div style={{ marginTop: 4 }}>
                      <Tag color={statusMap[item.status]?.color} size="small">
                        {statusMap[item.status]?.text}
                      </Tag>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </Col>

        {/* 右侧交付物详情 */}
        <Col span={16}>
          {selectedItem ? (
            <Card 
              title={
                <div>
                  <span>{selectedItem.item_name}</span>
                  <Tag color={statusMap[selectedItem.status]?.color} style={{ marginLeft: 8 }}>
                    {statusMap[selectedItem.status]?.text}
                  </Tag>
                </div>
              }
              size="small"
            >
              <DeliverableUpload 
                checklistItemId={selectedItem.id}
                readOnly={selectedItem.status === 'passed' || selectedItem.status === 'rejected'}
              />
            </Card>
          ) : (
            <Card>
              <div style={{ textAlign: 'center', padding: '80px 0', color: '#999' }}>
                <FileTextOutlined style={{ fontSize: 48, marginBottom: 16 }} />
                <p>请选择左侧检查项查看交付物</p>
              </div>
            </Card>
          )}
        </Col>
      </Row>
    </div>
  );
}

// 验证记录Tab组件
function VerificationRecordsTab({ taskId }) {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchRecords();
  }, [taskId]);

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const response = await verificationApi.listRecords({ task_id: taskId, limit: 100 });
      setRecords(response.data.items || []);
    } catch (error) {
      console.error('获取验证记录失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: '检查项',
      dataIndex: 'checklist_item_name',
      render: (text, record) => (
        <div>
          <div>{text}</div>
          <div style={{ fontSize: 12, color: '#999' }}>{dimensionMap[record.control_dimension]}</div>
        </div>
      ),
    },
    {
      title: '脚本名称',
      dataIndex: 'script_name',
    },
    {
      title: '执行状态',
      dataIndex: 'status',
      width: 100,
      render: (status) => {
        const config = {
          pending: { text: '等待中', color: 'default' },
          running: { text: '执行中', color: 'processing' },
          success: { text: '成功', color: 'success' },
          failed: { text: '失败', color: 'error' },
        }[status] || { text: status, color: 'default' };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '执行结果',
      dataIndex: 'result',
      render: (result) => (
        <span style={{ color: result === 'passed' ? '#52c41a' : '#ff4d4f' }}>
          {result === 'passed' ? '通过' : result === 'failed' ? '未通过' : '-'}
        </span>
      ),
    },
    {
      title: '执行时间',
      dataIndex: 'executed_at',
      width: 180,
    },
    {
      title: '操作',
      width: 100,
      render: (_, record) => (
        <Button type="link" size="small">查看详情</Button>
      ),
    },
  ];

  return (
    <div>
      <Table
        rowKey="id"
        columns={columns}
        dataSource={records}
        loading={loading}
        pagination={false}
        locale={{ emptyText: '暂无验证记录' }}
      />
    </div>
  );
}

export default TaskDetail;
