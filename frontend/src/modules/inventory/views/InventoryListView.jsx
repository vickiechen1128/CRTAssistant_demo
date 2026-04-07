/**
 * InventoryListView 组件
 * 台账列表页面 - 支持应用系统、云资源、账号三种类型
 */
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Button,
  Table,
  Space,
  Input,
  Select,
  Tag,
  Tabs,
  Popconfirm,
  message,
  Row,
  Col,
  Statistic,
  Tooltip,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  CloudServerOutlined,
  AppstoreOutlined,
  SafetyOutlined,
} from '@ant-design/icons';
import { useInventoryStore } from '../store';

const { Option } = Select;
// 状态映射
const statusMap = {
  active: { label: '活跃', color: 'success' },
  inactive: { label: '停用', color: 'default' },
  archived: { label: '已归档', color: 'warning' },
  expired: { label: '已过期', color: 'error' },
};

// 资源类型映射
const resourceTypeMap = {
  ecs: { label: 'ECS', color: 'blue' },
  rds: { label: 'RDS', color: 'cyan' },
  oss: { label: 'OSS', color: 'purple' },
  slb: { label: 'SLB', color: 'orange' },
  vpc: { label: 'VPC', color: 'green' },
  redis: { label: 'Redis', color: 'red' },
  kafka: { label: 'Kafka', color: 'magenta' },
  elasticsearch: { label: 'Elasticsearch', color: 'geekblue' },
};

// 账号类型映射
const accountTypeMap = {
  system: { label: '系统账号', color: 'blue' },
  software: { label: '软件账号', color: 'green' },
  database: { label: '数据库账号', color: 'purple' },
};

// 权限级别映射
const permissionLevelMap = {
  admin: { label: '管理员', color: 'red' },
  operator: { label: '操作员', color: 'orange' },
  viewer: { label: '观察员', color: 'default' },
};

/**
 * InventoryListView 组件
 */
const InventoryListView = () => {
  const navigate = useNavigate();
  const [searchKeyword, setSearchKeyword] = useState('');
  const [activeTab, setActiveTab] = useState('application');

  // 从 Store 获取状态和方法
  const {
    summary,
    applications,
    cloudResources,
    accounts,
    pagination,
    filters,
    loading,
    fetchSummary,
    fetchApplications,
    fetchCloudResources,
    fetchAccounts,
    setFilters,
    setPagination,
    removeApplication,
    removeCloudResource,
    removeAccount,
  } = useInventoryStore();

  // 初始加载
  useEffect(() => {
    fetchSummary();
  }, []);

  // 根据当前标签页加载数据
  useEffect(() => {
    if (activeTab === 'application') {
      fetchApplications();
    } else if (activeTab === 'cloud') {
      fetchCloudResources();
    } else if (activeTab === 'account') {
      fetchAccounts();
    }
  }, [activeTab, pagination.current, pagination.pageSize, filters]);

  // 处理搜索
  const handleSearch = () => {
    setFilters({ keyword: searchKeyword });
  };

  // 处理分页变化
  const handlePageChange = (page, pageSize) => {
    setPagination({ current: page, pageSize });
  };

  // 处理删除
  const handleDelete = async (id) => {
    try {
      if (activeTab === 'application') {
        await removeApplication(id);
      } else if (activeTab === 'cloud') {
        await removeCloudResource(id);
      } else if (activeTab === 'account') {
        await removeAccount(id);
      }
      message.success('删除成功');
    } catch (error) {
      message.error('删除失败: ' + (error.message || '未知错误'));
    }
  };

  // 处理标签切换
  const handleTabChange = (key) => {
    setActiveTab(key);
    setFilters({ type: key });
    setSearchKeyword('');
  };

  // 应用系统表格列
  const applicationColumns = [
    {
      title: '应用ID',
      dataIndex: 'id',
      key: 'id',
      width: 280,
      render: (id) => (
        <span style={{ fontFamily: 'monospace', fontSize: '12px', color: '#666' }}>{id}</span>
      ),
    },
    {
      title: '应用名称',
      dataIndex: 'app_name',
      key: 'app_name',
      render: (text, record) => (
        <a onClick={() => navigate(`/inventories/applications/${record.id}`)}>{text}</a>
      ),
    },
    {
      title: '业务负责人',
      dataIndex: 'business_owner',
      key: 'business_owner',
      width: 120,
    },
    {
      title: '项目负责责人',
      dataIndex: 'project_owner',
      key: 'project_owner',
      width: 120,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => {
        const config = statusMap[status] || { label: status, color: 'default' };
        return <Tag color={config.color}>{config.label}</Tag>;
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => navigate(`/inventories/applications/${record.id}`)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => navigate(`/inventories/applications/${record.id}/edit`)}
            />
          </Tooltip>
          <Popconfirm
            title="确认删除"
            description="删除后无法恢复，是否继续？"
            onConfirm={() => handleDelete(record.id)}
            okText="确认"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button type="text" danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 云资源表格列
  const cloudResourceColumns = [
    {
      title: '资源名称',
      dataIndex: 'resource_name',
      key: 'resource_name',
      render: (text, record) => (
        <a onClick={() => navigate(`/inventories/cloud-resources/${record.id}`)}>{text}</a>
      ),
    },
    {
      title: '资源类型',
      dataIndex: 'resource_type',
      key: 'resource_type',
      width: 120,
      render: (type) => {
        const config = resourceTypeMap[type] || { label: type, color: 'default' };
        return <Tag color={config.color}>{config.label}</Tag>;
      },
    },
    {
      title: '所属应用',
      dataIndex: 'app_name',
      key: 'app_name',
      render: (text) => text || '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => {
        const config = statusMap[status] || { label: status, color: 'default' };
        return <Tag color={config.color}>{config.label}</Tag>;
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => navigate(`/inventories/cloud-resources/${record.id}`)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => navigate(`/inventories/cloud-resources/${record.id}/edit`)}
            />
          </Tooltip>
          <Popconfirm
            title="确认删除"
            description="删除后无法恢复，是否继续？"
            onConfirm={() => handleDelete(record.id)}
            okText="确认"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button type="text" danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 账号表格列
  const accountColumns = [
    {
      title: '账号名称',
      dataIndex: 'account_name',
      key: 'account_name',
      render: (text, record) => (
        <a onClick={() => navigate(`/inventories/accounts/${record.id}`)}>{text}</a>
      ),
    },
    {
      title: '账号类型',
      dataIndex: 'account_type',
      key: 'account_type',
      width: 120,
      render: (type) => {
        const config = accountTypeMap[type] || { label: type, color: 'default' };
        return <Tag color={config.color}>{config.label}</Tag>;
      },
    },
    {
      title: '权限级别',
      dataIndex: 'permission_level',
      key: 'permission_level',
      width: 120,
      render: (level) => {
        const config = permissionLevelMap[level] || { label: level, color: 'default' };
        return <Tag color={config.color}>{config.label}</Tag>;
      },
    },
    {
      title: '持有人',
      dataIndex: 'holder_name',
      key: 'holder_name',
      width: 120,
    },
    {
      title: '有效期至',
      dataIndex: 'valid_until',
      key: 'valid_until',
      width: 120,
      render: (date) => {
        if (!date) return '-';
        const days = Math.ceil((new Date(date) - new Date()) / (1000 * 60 * 60 * 24));
        if (days < 0) return <Tag color="error">已过期</Tag>;
        if (days <= 30) return <Tag color="warning">{days}天后过期</Tag>;
        return date;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => {
        const config = statusMap[status] || { label: status, color: 'default' };
        return <Tag color={config.color}>{config.label}</Tag>;
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => navigate(`/inventories/accounts/${record.id}`)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => navigate(`/inventories/accounts/${record.id}/edit`)}
            />
          </Tooltip>
          <Popconfirm
            title="确认删除"
            description="删除后无法恢复，是否继续？"
            onConfirm={() => handleDelete(record.id)}
            okText="确认"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button type="text" danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 获取当前表格列和数据
  const getCurrentColumns = () => {
    switch (activeTab) {
      case 'application':
        return applicationColumns;
      case 'cloud':
        return cloudResourceColumns;
      case 'account':
        return accountColumns;
      default:
        return applicationColumns;
    }
  };

  const getCurrentData = () => {
    switch (activeTab) {
      case 'application':
        return applications;
      case 'cloud':
        return cloudResources;
      case 'account':
        return accounts;
      default:
        return applications;
    }
  };

  // 获取新增按钮链接
  const getCreatePath = () => {
    switch (activeTab) {
      case 'application':
        return '/inventories/applications/create';
      case 'cloud':
        return '/inventories/cloud-resources/create';
      case 'account':
        return '/inventories/accounts/create';
      default:
        return '/inventories/applications/create';
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="应用系统"
              value={summary?.application_count || 0}
              prefix={<AppstoreOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="云资源"
              value={summary?.cloud_resource_count || 0}
              prefix={<CloudServerOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="账号"
              value={summary?.account_count || 0}
              prefix={<SafetyOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 台账列表 */}
      <Card>
        <Tabs 
          activeKey={activeTab} 
          onChange={handleTabChange}
          items={[
            {
              key: 'application',
              label: <span><AppstoreOutlined /> 应用系统</span>,
            },
            {
              key: 'cloud',
              label: <span><CloudServerOutlined /> 云资源</span>,
            },
            {
              key: 'account',
              label: <span><SafetyOutlined /> 账号</span>,
            },
          ]}
        />

        {/* 搜索和操作栏 */}
        <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
          <Col>
            <Space>
              <Input
                placeholder="搜索关键词"
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                onPressEnter={handleSearch}
                style={{ width: 250 }}
                prefix={<SearchOutlined />}
                allowClear
              />
              <Button type="primary" onClick={handleSearch}>
                搜索
              </Button>
            </Space>
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => navigate(getCreatePath())}
            >
              新增
            </Button>
          </Col>
        </Row>

        {/* 数据表格 */}
        <Table
          columns={getCurrentColumns()}
          dataSource={getCurrentData()}
          rowKey="id"
          loading={loading}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: handlePageChange,
          }}
        />
      </Card>
    </div>
  );
};

export default InventoryListView;
