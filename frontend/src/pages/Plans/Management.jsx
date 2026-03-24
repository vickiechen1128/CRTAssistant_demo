/**
 * 计划管理页面
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Row,
  Col,
  Statistic,
  Button,
  Table,
  Tag,
  Space,
  Input,
  Select,
  DatePicker,
  Progress,
  Badge,
  Tooltip,
  Modal,
  Tabs,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  ScheduleOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  PauseCircleOutlined,
  BookOutlined,
  DatabaseOutlined,
  CloudOutlined,
  UserOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
} from '@ant-design/icons';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { TabPane } = Tabs;

// 模拟数据
const mockStats = {
  total: 156,
  pending: 23,
  processing: 45,
  completed: 88,
  completionRate: 78,
};

const mockPlans = [
  {
    id: 'PLAN-2024-001',
    name: '订单管理系统V2.0上线',
    category: 'new_system',
    priority: 'P0',
    status: 'processing',
    progress: 65,
    startDate: '2024-03-01',
    endDate: '2024-04-15',
    manager: '张三',
    inventories: ['app', 'cloud', 'account'],
  },
  {
    id: 'PLAN-2024-002',
    name: '支付接口优化升级',
    category: 'new_feature',
    priority: 'P1',
    status: 'pending',
    progress: 0,
    startDate: '2024-03-15',
    endDate: '2024-04-30',
    manager: '李四',
    inventories: ['app', 'cloud'],
  },
  {
    id: 'PLAN-2024-003',
    name: '数据库迁移项目',
    category: 'db_change',
    priority: 'P0',
    status: 'completed',
    progress: 100,
    startDate: '2024-02-01',
    endDate: '2024-02-28',
    manager: '王五',
    inventories: ['cloud', 'account'],
  },
  {
    id: 'PLAN-2024-004',
    name: '用户中心功能增强',
    category: 'business_change',
    priority: 'P2',
    status: 'processing',
    progress: 45,
    startDate: '2024-03-10',
    endDate: '2024-05-10',
    manager: '赵六',
    inventories: ['app'],
  },
];

const categoryMap = {
  new_system: { text: '新系统建设', color: 'blue' },
  new_feature: { text: '新功能上线', color: 'green' },
  business_change: { text: '业务变更', color: 'orange' },
  db_change: { text: '数据库变更', color: 'purple' },
};

const priorityMap = {
  P0: { color: 'red', text: 'P0-紧急' },
  P1: { color: 'orange', text: 'P1-高' },
  P2: { color: 'gold', text: 'P2-中' },
  P3: { color: 'green', text: 'P3-低' },
};

const statusMap = {
  pending: { color: 'blue', text: '待启动', icon: <ClockCircleOutlined /> },
  processing: { color: 'gold', text: '进行中', icon: <ScheduleOutlined /> },
  completed: { color: 'green', text: '已完成', icon: <CheckCircleOutlined /> },
};

const inventoryIcons = {
  app: { icon: <DatabaseOutlined />, color: '#667eea', name: '应用' },
  cloud: { icon: <CloudOutlined />, color: '#11998e', name: '云服务' },
  account: { icon: <UserOutlined />, color: '#fc4a1a', name: '账号' },
};

function PlanManagement() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [inventoryModalVisible, setInventoryModalVisible] = useState(false);
  const [selectedInventoryType, setSelectedInventoryType] = useState('app');

  // 统计卡片数据
  const statCards = [
    {
      title: '计划总数',
      value: mockStats.total,
      icon: <ScheduleOutlined style={{ color: '#667eea' }} />,
      trend: '+12%',
      trendUp: true,
    },
    {
      title: '待启动',
      value: mockStats.pending,
      icon: <ClockCircleOutlined style={{ color: '#1890ff' }} />,
      trend: '-5%',
      trendUp: false,
    },
    {
      title: '进行中',
      value: mockStats.processing,
      icon: <ScheduleOutlined style={{ color: '#faad14' }} />,
      trend: '+8%',
      trendUp: true,
    },
    {
      title: '已完成',
      value: mockStats.completed,
      icon: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
      trend: '+15%',
      trendUp: true,
    },
    {
      title: '完成率',
      value: `${mockStats.completionRate}%`,
      icon: <Progress type="circle" percent={mockStats.completionRate} size={24} />,
      trend: '+5%',
      trendUp: true,
    },
  ];

  // 表格列定义
  const columns = [
    {
      title: '计划名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 500, color: '#333' }}>{text}</div>
          <div style={{ fontSize: 12, color: '#999', fontFamily: 'monospace' }}>
            {record.id}
          </div>
        </div>
      ),
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (category) => (
        <Tag color={categoryMap[category]?.color}>
          {categoryMap[category]?.text}
        </Tag>
      ),
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (priority) => (
        <Tag color={priorityMap[priority]?.color}>
          {priority}
        </Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => (
        <Tag icon={statusMap[status]?.icon} color={statusMap[status]?.color}>
          {statusMap[status]?.text}
        </Tag>
      ),
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      width: 150,
      render: (progress) => (
        <Progress
          percent={progress}
          size="small"
          status={progress === 100 ? 'success' : 'active'}
          strokeColor={progress === 100 ? '#52c41a' : '#667eea'}
        />
      ),
    },
    {
      title: '时间范围',
      key: 'dateRange',
      width: 180,
      render: (_, record) => (
        <div style={{ fontSize: 13 }}>
          <div>{record.startDate}</div>
          <div style={{ color: '#999' }}>至 {record.endDate}</div>
        </div>
      ),
    },
    {
      title: '负责人',
      dataIndex: 'manager',
      key: 'manager',
      width: 100,
    },
    {
      title: '关联台账',
      key: 'inventories',
      width: 150,
      render: (_, record) => (
        <Space size={4}>
          {record.inventories.map((inv) => (
            <Tooltip key={inv} title={inventoryIcons[inv]?.name}>
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: 6,
                  background: `${inventoryIcons[inv]?.color}15`,
                  color: inventoryIcons[inv]?.color,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 14,
                  cursor: 'pointer',
                }}
              >
                {inventoryIcons[inv]?.icon}
              </div>
            </Tooltip>
          ))}
        </Space>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看">
            <Button
              type="primary"
              size="small"
              icon={<EyeOutlined />}
              style={{ background: '#667eea' }}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button size="small" icon={<EditOutlined />} />
          </Tooltip>
          <Tooltip title="删除">
            <Button
              danger
              size="small"
              icon={<DeleteOutlined />}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  // 台账管理模态框中的表格数据
  const inventoryTableData = [
    {
      key: '1',
      id: 'APP-001',
      name: '订单管理系统',
      type: 'app',
      status: 'active',
      updateTime: '2024-03-20',
    },
    {
      key: '2',
      id: 'CLOUD-001',
      name: '生产环境ECS',
      type: 'cloud',
      status: 'active',
      updateTime: '2024-03-19',
    },
    {
      key: '3',
      id: 'ACC-001',
      name: 'root账户',
      type: 'account',
      status: 'active',
      updateTime: '2024-03-18',
    },
  ];

  const inventoryColumns = [
    {
      title: '台账ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: '台账名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Badge status={status === 'active' ? 'success' : 'default'} text={status === 'active' ? '启用' : '停用'} />
      ),
    },
    {
      title: '更新时间',
      dataIndex: 'updateTime',
      key: 'updateTime',
    },
    {
      title: '操作',
      key: 'action',
      render: () => (
        <Space>
          <Button type="link" size="small">查看</Button>
          <Button type="link" size="small">编辑</Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      {/* 页面标题栏 */}
      <Card style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <ScheduleOutlined style={{ fontSize: 24, color: '#667eea' }} />
            <span style={{ fontSize: 20, fontWeight: 600 }}>计划管理</span>
          </div>
          <Space>
            <Button
              icon={<BookOutlined />}
              onClick={() => setInventoryModalVisible(true)}
            >
              台账管理
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => navigate('/plans/new')}
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
              }}
            >
              创建计划
            </Button>
          </Space>
        </div>
      </Card>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        {statCards.map((card, index) => (
          <Col span={4} key={index}>
            <Card hoverable>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ fontSize: 13, color: '#666', marginBottom: 8 }}>{card.title}</div>
                  <div style={{ fontSize: 28, fontWeight: 700, color: '#333' }}>{card.value}</div>
                  <div
                    style={{
                      fontSize: 12,
                      color: card.trendUp ? '#52c41a' : '#ff4d4f',
                      marginTop: 8,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 4,
                    }}
                  >
                    {card.trendUp ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                    {card.trend}
                  </div>
                </div>
                <div style={{ fontSize: 24 }}>{card.icon}</div>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* 图表区域 */}
      <Row gutter={20} style={{ marginBottom: 24 }}>
        <Col span={16}>
          <Card title="计划趋势统计">
            <div
              style={{
                height: 200,
                background: 'linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%)',
                borderRadius: 8,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#999',
              }}
            >
              计划趋势图表区域
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Card title="计划分类占比">
            <div
              style={{
                height: 200,
                background: 'linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%)',
                borderRadius: 8,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#999',
              }}
            >
              分类饼图区域
            </div>
          </Card>
        </Col>
      </Row>

      {/* 台账管理入口卡片 */}
      <Card style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div style={{ fontSize: 16, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
            <BookOutlined />
            台账管理入口
          </div>
        </div>
        <Row gutter={16}>
          <Col span={8}>
            <Card
              hoverable
              onClick={() => navigate('/inventories/app/create')}
              style={{ border: '2px solid #e8e8e8', cursor: 'pointer' }}
              bodyStyle={{ padding: 20 }}
            >
              <div style={{ fontSize: 32, marginBottom: 12 }}>🖥️</div>
              <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 8 }}>应用系统台账</div>
              <div style={{ fontSize: 12, color: '#666', marginBottom: 12, lineHeight: 1.5 }}>
                应用名称、功能模块、主机名、URL、负责人、上线时间等基础信息
              </div>
              <div style={{ fontSize: 24, fontWeight: 700, color: '#667eea' }}>18</div>
              <div style={{ fontSize: 12, color: '#999' }}>个应用系统</div>
            </Card>
          </Col>
          <Col span={8}>
            <Card
              hoverable
              onClick={() => navigate('/inventories/cloud/create')}
              style={{ border: '2px solid #e8e8e8', cursor: 'pointer' }}
              bodyStyle={{ padding: 20 }}
            >
              <div style={{ fontSize: 32, marginBottom: 12 }}>☁️</div>
              <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 8 }}>云服务开通台账</div>
              <div style={{ fontSize: 12, color: '#666', marginBottom: 12, lineHeight: 1.5 }}>
                IAAS资源（计算/网络/存储/备份）和PAAS软件（中间件/数据库/缓存）
              </div>
              <div style={{ fontSize: 24, fontWeight: 700, color: '#11998e' }}>56</div>
              <div style={{ fontSize: 12, color: '#999' }}>个云资源</div>
            </Card>
          </Col>
          <Col span={8}>
            <Card
              hoverable
              onClick={() => navigate('/inventories/account/create')}
              style={{ border: '2px solid #e8e8e8', cursor: 'pointer' }}
              bodyStyle={{ padding: 20 }}
            >
              <div style={{ fontSize: 32, marginBottom: 12 }}>🔐</div>
              <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 8 }}>系统及软件账号台账</div>
              <div style={{ fontSize: 12, color: '#666', marginBottom: 12, lineHeight: 1.5 }}>
                服务器和软件的账户信息，包括权限级别、持有人、有效期、密码修改周期
              </div>
              <div style={{ fontSize: 24, fontWeight: 700, color: '#fc4a1a' }}>42</div>
              <div style={{ fontSize: 12, color: '#999' }}>个账号</div>
            </Card>
          </Col>
        </Row>
      </Card>

      {/* 筛选区域 */}
      <Card style={{ marginBottom: 20 }}>
        <Space wrap style={{ width: '100%' }}>
          <Input
            placeholder="搜索计划名称/ID"
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 240 }}
          />
          <Select
            placeholder="计划分类"
            value={categoryFilter}
            onChange={setCategoryFilter}
            style={{ width: 140 }}
            allowClear
          >
            <Option value="new_system">新系统建设</Option>
            <Option value="new_feature">新功能上线</Option>
            <Option value="business_change">业务变更</Option>
            <Option value="db_change">数据库变更</Option>
          </Select>
          <Select
            placeholder="优先级"
            value={priorityFilter}
            onChange={setPriorityFilter}
            style={{ width: 120 }}
            allowClear
          >
            <Option value="P0">P0-紧急</Option>
            <Option value="P1">P1-高</Option>
            <Option value="P2">P2-中</Option>
            <Option value="P3">P3-低</Option>
          </Select>
          <Select
            placeholder="状态"
            value={statusFilter}
            onChange={setStatusFilter}
            style={{ width: 120 }}
            allowClear
          >
            <Option value="pending">待启动</Option>
            <Option value="processing">进行中</Option>
            <Option value="completed">已完成</Option>
          </Select>
          <RangePicker placeholder={['开始日期', '结束日期']} />
          <Button icon={<ReloadOutlined />}>重置</Button>
          <Button type="primary" style={{ background: '#667eea', borderColor: '#667eea' }}>
            查询
          </Button>
        </Space>
      </Card>

      {/* 计划列表 */}
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div style={{ fontSize: 16, fontWeight: 600 }}>计划列表</div>
          <Space>
            <Button>导出</Button>
            <Button>批量操作</Button>
          </Space>
        </div>
        <Table
          columns={columns}
          dataSource={mockPlans}
          rowKey="id"
          loading={loading}
          pagination={{
            total: mockPlans.length,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>

      {/* 台账管理模态框 */}
      <Modal
        title="台账管理"
        open={inventoryModalVisible}
        onCancel={() => setInventoryModalVisible(false)}
        width={1000}
        footer={[
          <Button key="close" onClick={() => setInventoryModalVisible(false)}>
            关闭
          </Button>,
        ]}
      >
        <Tabs activeKey={selectedInventoryType} onChange={setSelectedInventoryType}>
          <TabPane tab="应用系统台账" key="app">
            <Table
              columns={inventoryColumns}
              dataSource={inventoryTableData.filter((item) => item.type === 'app')}
              size="small"
              pagination={{ pageSize: 5 }}
            />
          </TabPane>
          <TabPane tab="云服务台账" key="cloud">
            <Table
              columns={inventoryColumns}
              dataSource={inventoryTableData.filter((item) => item.type === 'cloud')}
              size="small"
              pagination={{ pageSize: 5 }}
            />
          </TabPane>
          <TabPane tab="系统账号台账" key="account">
            <Table
              columns={inventoryColumns}
              dataSource={inventoryTableData.filter((item) => item.type === 'account')}
              size="small"
              pagination={{ pageSize: 5 }}
            />
          </TabPane>
        </Tabs>
      </Modal>
    </div>
  );
}

export default PlanManagement;
