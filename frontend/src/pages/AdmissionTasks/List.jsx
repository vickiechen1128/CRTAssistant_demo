/**
 * 准入任务列表页面
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, Button, Tag, Space, Input, Select, Card } from 'antd';
import { PlusOutlined, EyeOutlined } from '@ant-design/icons';
import { taskApi } from '../../api/tasks';

const { Option } = Select;

// 状态映射
const statusMap = {
  draft: { text: '草稿', color: 'default' },
  in_progress: { text: '进行中', color: 'processing' },
  pending_review: { text: '待审核', color: 'warning' },
  approving: { text: '审批中', color: 'warning' },
  passed: { text: '已通过', color: 'success' },
  rejected: { text: '已驳回', color: 'error' },
  cancelled: { text: '已取消', color: 'default' },
};

function TaskList() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });
  const [filters, setFilters] = useState({
    status: undefined,
    system_name: '',
  });

  useEffect(() => {
    fetchTasks();
  }, [pagination.current, filters]);

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const params = {
        page: pagination.current,
        per_page: pagination.pageSize,
        ...filters,
      };
      const response = await taskApi.list(params);
      setData(response.data.items);
      setPagination({
        ...pagination,
        total: response.data.pagination.total,
      });
    } catch (error) {
      console.error('获取任务列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTableChange = (newPagination) => {
    setPagination({
      ...pagination,
      current: newPagination.current,
    });
  };

  const columns = [
    {
      title: '任务编号',
      dataIndex: 'task_no',
      width: 160,
    },
    {
      title: '系统名称',
      dataIndex: 'system_name',
      render: (text, record) => (
        <div>
          <div>{text}</div>
          <div style={{ fontSize: 12, color: '#999' }}>{record.system_code}</div>
        </div>
      ),
    },
    {
      title: '版本',
      dataIndex: 'version',
      width: 100,
    },
    {
      title: '计划上线',
      dataIndex: 'release_date',
      width: 120,
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
      title: '进度',
      dataIndex: 'progress',
      width: 100,
      render: (progress) => `${progress}%`,
    },
    {
      title: '负责人',
      dataIndex: ['manager', 'real_name'],
      width: 100,
    },
    {
      title: '操作',
      width: 100,
      render: (_, record) => (
        <Button 
          type="link" 
          icon={<EyeOutlined />}
          onClick={() => navigate(`/admission-tasks/${record.id}`)}
        >
          查看
        </Button>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between' }}>
        <h2 style={{ margin: 0 }}>准入任务管理</h2>
        <Button 
          type="primary" 
          icon={<PlusOutlined />}
          onClick={() => navigate('/admission-tasks/new')}
        >
          创建任务
        </Button>
      </div>

      {/* 筛选 */}
      <Card style={{ marginBottom: 24 }}>
        <Space>
          <Input.Search
            placeholder="搜索系统名称"
            value={filters.system_name}
            onChange={(e) => setFilters({ ...filters, system_name: e.target.value })}
            onSearch={fetchTasks}
            style={{ width: 200 }}
          />
          <Select
            placeholder="状态筛选"
            value={filters.status}
            onChange={(value) => setFilters({ ...filters, status: value })}
            style={{ width: 120 }}
            allowClear
          >
            {Object.entries(statusMap).map(([key, { text }]) => (
              <Option key={key} value={key}>{text}</Option>
            ))}
          </Select>
        </Space>
      </Card>

      {/* 表格 */}
      <Table
        rowKey="id"
        columns={columns}
        dataSource={data}
        loading={loading}
        pagination={{
          ...pagination,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
        }}
        onChange={handleTableChange}
      />
    </div>
  );
}

export default TaskList;
