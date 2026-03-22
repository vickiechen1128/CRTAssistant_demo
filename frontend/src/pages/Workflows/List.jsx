/**
 * 工作流模板列表页
 * 展示所有工作流模板，支持创建、编辑、删除
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Input,
  Select,
  Popconfirm,
  message,
  Row,
  Col
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  CopyOutlined
} from '@ant-design/icons';
import useWorkflowStore from '../../stores/workflowStore';

const { Search } = Input;
const { Option } = Select;

// 状态映射
const statusMap = {
  draft: { color: 'default', text: '草稿' },
  active: { color: 'success', text: '启用' },
  archived: { color: 'warning', text: '已归档' }
};

const WorkflowList = () => {
  const navigate = useNavigate();
  const {
    workflows,
    pagination,
    loading,
    fetchWorkflows,
    deleteWorkflow
  } = useWorkflowStore();

  const [filters, setFilters] = useState({
    keyword: '',
    is_preset: undefined
  });

  // 加载数据
  useEffect(() => {
    fetchWorkflows({
      page: 1,
      per_page: 20
    });
  }, []);

  // 处理搜索
  const handleSearch = () => {
    fetchWorkflows({
      page: 1,
      per_page: pagination.per_page,
      ...filters
    });
  };

  // 处理分页
  const handlePageChange = (page, pageSize) => {
    fetchWorkflows({
      page,
      per_page: pageSize,
      ...filters
    });
  };

  // 处理删除
  const handleDelete = async (id) => {
    const success = await deleteWorkflow(id);
    if (success) {
      message.success('删除成功');
    }
  };

  // 表格列定义
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 80
    },
    {
      title: '工作流名称',
      dataIndex: 'name',
      render: (text, record) => (
        <Space>
          <span>{text}</span>
          {record.is_preset && <Tag color="blue">预置</Tag>}
        </Space>
      )
    },
    {
      title: '描述',
      dataIndex: 'description',
      ellipsis: true
    },
    {
      title: '工作项数',
      dataIndex: 'work_item_count',
      width: 100,
      align: 'center'
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (status) => {
        const info = statusMap[status] || statusMap.draft;
        return <Tag color={info.color}>{info.text}</Tag>;
      }
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      width: 180,
      render: (text) => new Date(text).toLocaleString()
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/workflows/${record.id}`)}
          >
            查看
          </Button>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => navigate(`/workflows/${record.id}/edit`)}
            disabled={record.is_preset}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个工作流模板吗？"
            description="删除后无法恢复，且会影响已创建的实例。"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
            disabled={record.is_preset}
          >
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              disabled={record.is_preset}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div className="workflow-list-page">
      <Card>
        {/* 标题和操作栏 */}
        <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
          <Col>
            <h2 style={{ margin: 0 }}>工作流模板</h2>
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => navigate('/workflows/new')}
            >
              创建工作流
            </Button>
          </Col>
        </Row>

        {/* 筛选栏 */}
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={8}>
            <Search
              placeholder="搜索工作流名称"
              value={filters.keyword}
              onChange={(e) => setFilters({ ...filters, keyword: e.target.value })}
              onSearch={handleSearch}
              allowClear
            />
          </Col>
          <Col span={4}>
            <Select
              placeholder="是否预置"
              value={filters.is_preset}
              onChange={(value) => setFilters({ ...filters, is_preset: value })}
              style={{ width: '100%' }}
              allowClear
            >
              <Option value={true}>预置模板</Option>
              <Option value={false}>自定义</Option>
            </Select>
          </Col>
          <Col span={4}>
            <Button type="primary" onClick={handleSearch}>
              查询
            </Button>
          </Col>
        </Row>

        {/* 表格 */}
        <Table
          columns={columns}
          dataSource={workflows}
          rowKey="id"
          loading={loading}
          pagination={{
            current: pagination.page,
            pageSize: pagination.per_page,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: handlePageChange
          }}
        />
      </Card>
    </div>
  );
};

export default WorkflowList;
