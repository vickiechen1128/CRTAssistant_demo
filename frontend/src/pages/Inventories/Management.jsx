/**
 * 台账管理页面
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Row,
  Col,
  Button,
  Table,
  Tag,
  Space,
  Input,
  Select,
  Badge,
  Tooltip,
  Tabs,
  Statistic,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  BookOutlined,
  DatabaseOutlined,
  CloudOutlined,
  UserOutlined,
  DesktopOutlined,
  SettingOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  ImportOutlined,
} from '@ant-design/icons';

const { Option } = Select;
const { TabPane } = Tabs;

// 模拟应用系统台账数据
const mockAppInventories = [
  {
    id: 'APP-001',
    name: '订单管理系统',
    hostname: 'order-server-01',
    url: 'https://order.example.com',
    manager: '张三',
    modules: 5,
    status: 'active',
    updateTime: '2024-03-20',
  },
  {
    id: 'APP-002',
    name: '支付系统',
    hostname: 'payment-server-01',
    url: 'https://payment.example.com',
    manager: '李四',
    modules: 3,
    status: 'active',
    updateTime: '2024-03-19',
  },
  {
    id: 'APP-003',
    name: '用户中心',
    hostname: 'user-server-01',
    url: 'https://user.example.com',
    manager: '王五',
    modules: 4,
    status: 'inactive',
    updateTime: '2024-03-15',
  },
];

// 模拟云服务台账数据
const mockCloudInventories = [
  {
    id: 'ECS-001',
    name: 'order-server-01',
    type: 'ECS',
    spec: '8C16G',
    ip: '192.168.1.101',
    os: 'CentOS 7.9',
    status: 'running',
    updateTime: '2024-03-20',
  },
  {
    id: 'ECS-002',
    name: 'payment-server-01',
    type: 'ECS',
    spec: '16C32G',
    ip: '192.168.1.102',
    os: 'CentOS 7.9',
    status: 'running',
    updateTime: '2024-03-19',
  },
  {
    id: 'RDS-001',
    name: 'order-database',
    type: 'RDS',
    spec: 'MySQL 8.0',
    ip: '192.168.2.101',
    os: '-',
    status: 'running',
    updateTime: '2024-03-18',
  },
];

// 模拟账号台账数据
const mockAccountInventories = [
  {
    id: 'ACC-001',
    account: 'root',
    type: 'system',
    permission: 'admin',
    holder: '张三',
    department: '运维部',
    expiryDate: '2024-12-31',
    status: 'active',
    updateTime: '2024-03-20',
  },
  {
    id: 'ACC-002',
    account: 'order_app',
    type: 'software',
    permission: 'readwrite',
    holder: '李四',
    department: '开发部',
    expiryDate: '2024-06-30',
    status: 'active',
    updateTime: '2024-03-19',
  },
  {
    id: 'ACC-003',
    account: 'db_reader',
    type: 'software',
    permission: 'readonly',
    holder: '王五',
    department: '数据部',
    expiryDate: '2024-09-30',
    status: 'inactive',
    updateTime: '2024-03-15',
  },
];

const statusMap = {
  active: { text: '启用', color: 'success' },
  inactive: { text: '停用', color: 'default' },
  running: { text: '运行中', color: 'success' },
  stopped: { text: '已停止', color: 'default' },
};

const permissionMap = {
  admin: { text: '管理员', color: 'red' },
  readwrite: { text: '读写', color: 'orange' },
  readonly: { text: '只读', color: 'green' },
  execute: { text: '执行', color: 'blue' },
};

function InventoryManagement() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('app');
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // 台账类型卡片数据
  const inventoryCards = [
    {
      key: 'app',
      title: '应用系统台账',
      icon: <DatabaseOutlined style={{ fontSize: 28, color: 'white' }} />,
      iconBg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      count: 18,
      label: '个应用系统',
      desc: '应用名称、功能模块、主机名、URL、负责人、上线时间等基础信息',
      stats: [
        { label: '本月新增', value: 3 },
        { label: '待更新', value: 2 },
      ],
      color: '#667eea',
    },
    {
      key: 'cloud',
      title: '云服务开通台账',
      icon: <CloudOutlined style={{ fontSize: 28, color: 'white' }} />,
      iconBg: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
      count: 56,
      label: '个云资源',
      desc: 'IAAS资源（计算/网络/存储/备份）和PAAS软件（中间件/数据库/缓存）',
      stats: [
        { label: 'IAAS', value: 32 },
        { label: 'PAAS', value: 24 },
      ],
      color: '#11998e',
    },
    {
      key: 'account',
      title: '系统及软件账号台账',
      icon: <UserOutlined style={{ fontSize: 28, color: 'white' }} />,
      iconBg: 'linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%)',
      count: 42,
      label: '个账号',
      desc: '服务器和软件的账户信息，包括权限级别、持有人、有效期、密码修改周期',
      stats: [
        { label: '系统账户', value: 18 },
        { label: '软件账户', value: 24 },
      ],
      color: '#fc4a1a',
    },
  ];

  // 应用系统台账列
  const appColumns = [
    {
      title: '应用名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 500 }}>{text}</div>
          <div style={{ fontSize: 12, color: '#999', fontFamily: 'monospace' }}>{record.id}</div>
        </div>
      ),
    },
    {
      title: '主机名',
      dataIndex: 'hostname',
      key: 'hostname',
    },
    {
      title: '访问地址',
      dataIndex: 'url',
      key: 'url',
      render: (url) => (
        <a href={url} target="_blank" rel="noopener noreferrer">{url}</a>
      ),
    },
    {
      title: '负责人',
      dataIndex: 'manager',
      key: 'manager',
    },
    {
      title: '功能模块',
      dataIndex: 'modules',
      key: 'modules',
      render: (modules) => (
        <Tag color="blue">{modules} 个模块</Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => (
        <Badge status={statusMap[status]?.color} text={statusMap[status]?.text} />
      ),
    },
    {
      title: '更新时间',
      dataIndex: 'updateTime',
      key: 'updateTime',
      width: 120,
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: () => (
        <Space size="small">
          <Tooltip title="查看">
            <Button type="primary" size="small" icon={<EyeOutlined />} style={{ background: '#667eea' }} />
          </Tooltip>
          <Tooltip title="编辑">
            <Button size="small" icon={<EditOutlined />} />
          </Tooltip>
          <Tooltip title="删除">
            <Button danger size="small" icon={<DeleteOutlined />} />
          </Tooltip>
        </Space>
      ),
    },
  ];

  // 云服务台账列
  const cloudColumns = [
    {
      title: '资源名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 500 }}>{text}</div>
          <div style={{ fontSize: 12, color: '#999', fontFamily: 'monospace' }}>{record.id}</div>
        </div>
      ),
    },
    {
      title: '资源类型',
      dataIndex: 'type',
      key: 'type',
      render: (type) => (
        <Tag color="cyan">{type}</Tag>
      ),
    },
    {
      title: '规格',
      dataIndex: 'spec',
      key: 'spec',
    },
    {
      title: 'IP地址',
      dataIndex: 'ip',
      key: 'ip',
    },
    {
      title: '操作系统',
      dataIndex: 'os',
      key: 'os',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => (
        <Badge status={statusMap[status]?.color} text={statusMap[status]?.text} />
      ),
    },
    {
      title: '更新时间',
      dataIndex: 'updateTime',
      key: 'updateTime',
      width: 120,
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: () => (
        <Space size="small">
          <Tooltip title="查看">
            <Button type="primary" size="small" icon={<EyeOutlined />} style={{ background: '#11998e' }} />
          </Tooltip>
          <Tooltip title="编辑">
            <Button size="small" icon={<EditOutlined />} />
          </Tooltip>
          <Tooltip title="删除">
            <Button danger size="small" icon={<DeleteOutlined />} />
          </Tooltip>
        </Space>
      ),
    },
  ];

  // 账号台账列
  const accountColumns = [
    {
      title: '账户名',
      dataIndex: 'account',
      key: 'account',
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 500, fontFamily: 'monospace' }}>{text}</div>
          <div style={{ fontSize: 12, color: '#999' }}>{record.id}</div>
        </div>
      ),
    },
    {
      title: '账户类型',
      dataIndex: 'type',
      key: 'type',
      render: (type) => (
        <Tag color={type === 'system' ? 'purple' : 'blue'}>
          {type === 'system' ? '系统账户' : '软件账户'}
        </Tag>
      ),
    },
    {
      title: '权限级别',
      dataIndex: 'permission',
      key: 'permission',
      render: (permission) => (
        <Tag color={permissionMap[permission]?.color}>
          {permissionMap[permission]?.text}
        </Tag>
      ),
    },
    {
      title: '持有人',
      dataIndex: 'holder',
      key: 'holder',
    },
    {
      title: '部门',
      dataIndex: 'department',
      key: 'department',
    },
    {
      title: '有效期至',
      dataIndex: 'expiryDate',
      key: 'expiryDate',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => (
        <Badge status={statusMap[status]?.color} text={statusMap[status]?.text} />
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: () => (
        <Space size="small">
          <Tooltip title="查看">
            <Button type="primary" size="small" icon={<EyeOutlined />} style={{ background: '#fc4a1a' }} />
          </Tooltip>
          <Tooltip title="编辑">
            <Button size="small" icon={<EditOutlined />} />
          </Tooltip>
          <Tooltip title="删除">
            <Button danger size="small" icon={<DeleteOutlined />} />
          </Tooltip>
        </Space>
      ),
    },
  ];

  const getColumns = () => {
    switch (activeTab) {
      case 'app':
        return appColumns;
      case 'cloud':
        return cloudColumns;
      case 'account':
        return accountColumns;
      default:
        return appColumns;
    }
  };

  const getData = () => {
    switch (activeTab) {
      case 'app':
        return mockAppInventories;
      case 'cloud':
        return mockCloudInventories;
      case 'account':
        return mockAccountInventories;
      default:
        return mockAppInventories;
    }
  };

  const handleCreate = () => {
    switch (activeTab) {
      case 'app':
        navigate('/inventories/app/create');
        break;
      case 'cloud':
        navigate('/inventories/cloud/create');
        break;
      case 'account':
        navigate('/inventories/account/create');
        break;
    }
  };

  return (
    <div>
      {/* 页面标题 */}
      <Card style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div
              style={{
                width: 44,
                height: 44,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                borderRadius: 12,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 24,
                color: 'white',
              }}
            >
              <BookOutlined />
            </div>
            <span style={{ fontSize: 20, fontWeight: 600 }}>台账管理</span>
          </div>
          <Space>
            <Button icon={<ImportOutlined />}>批量导入</Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleCreate}
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
              }}
            >
              新增台账
            </Button>
          </Space>
        </div>
      </Card>

      {/* 台账类型卡片 */}
      <Row gutter={20} style={{ marginBottom: 24 }}>
        {inventoryCards.map((card) => (
          <Col span={8} key={card.key}>
            <Card
              hoverable
              onClick={() => setActiveTab(card.key)}
              style={{
                border: activeTab === card.key ? `2px solid ${card.color}` : '2px solid transparent',
                background: activeTab === card.key ? `linear-gradient(135deg, ${card.color}08 0%, ${card.color}15 100%)` : 'white',
                cursor: 'pointer',
                position: 'relative',
                overflow: 'hidden',
              }}
              bodyStyle={{ padding: 24 }}
            >
              <div
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  height: 4,
                  background: card.iconBg,
                }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16, marginTop: 4 }}>
                <div
                  style={{
                    width: 56,
                    height: 56,
                    background: card.iconBg,
                    borderRadius: 14,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  {card.icon}
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: 36, fontWeight: 700, color: '#333', lineHeight: 1 }}>{card.count}</div>
                  <div style={{ fontSize: 13, color: '#999', marginTop: 4 }}>{card.label}</div>
                </div>
              </div>
              <div style={{ fontSize: 18, fontWeight: 600, color: '#333', marginBottom: 8 }}>{card.title}</div>
              <div style={{ fontSize: 13, color: '#666', lineHeight: 1.6, marginBottom: 16 }}>{card.desc}</div>
              <div style={{ display: 'flex', gap: 16, paddingTop: 16, borderTop: '1px solid #f0f0f0' }}>
                {card.stats.map((stat, index) => (
                  <div key={index} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, color: '#666' }}>
                    <span>{stat.label}:</span>
                    <span style={{ fontWeight: 600, color: '#333' }}>{stat.value}</span>
                  </div>
                ))}
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* 内容Tab */}
      <Card style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 8 }}>
          {[
            { key: 'app', label: '应用系统台账', icon: <DatabaseOutlined /> },
            { key: 'cloud', label: '云服务台账', icon: <CloudOutlined /> },
            { key: 'account', label: '系统账号台账', icon: <UserOutlined /> },
          ].map((tab) => (
            <Button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              style={{
                padding: '10px 20px',
                borderRadius: 8,
                background: activeTab === tab.key ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'transparent',
                color: activeTab === tab.key ? 'white' : '#666',
                border: activeTab === tab.key ? 'none' : '1px solid #d9d9d9',
              }}
            >
              <Space>
                {tab.icon}
                {tab.label}
              </Space>
            </Button>
          ))}
        </div>
      </Card>

      {/* 筛选区域 */}
      <Card style={{ marginBottom: 20 }}>
        <Space wrap style={{ width: '100%' }}>
          <Input
            placeholder="搜索台账名称/ID"
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 240 }}
          />
          <Select
            placeholder="状态"
            value={statusFilter}
            onChange={setStatusFilter}
            style={{ width: 140 }}
            allowClear
          >
            <Option value="active">启用</Option>
            <Option value="inactive">停用</Option>
          </Select>
          <Button icon={<ReloadOutlined />}>重置</Button>
          <Button type="primary" style={{ background: '#667eea', borderColor: '#667eea' }}>
            查询
          </Button>
        </Space>
      </Card>

      {/* 数据表格 */}
      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div style={{ fontSize: 16, fontWeight: 600 }}>
            {activeTab === 'app' && '应用系统台账列表'}
            {activeTab === 'cloud' && '云服务台账列表'}
            {activeTab === 'account' && '系统账号台账列表'}
          </div>
          <Space>
            <Button>导出</Button>
            <Button>批量操作</Button>
          </Space>
        </div>
        <Table
          columns={getColumns()}
          dataSource={getData()}
          rowKey="id"
          pagination={{
            total: getData().length,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>
    </div>
  );
}

export default InventoryManagement;
