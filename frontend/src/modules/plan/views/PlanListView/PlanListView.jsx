/**
 * PlanListView 组件
 * 计划列表页面
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
  Tooltip,
  Popconfirm,
  message,
  Row,
  Col,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import { usePlanStore } from '../../store';
import PlanStatusBadge from '../../components/PlanStatusBadge';
import {
  categoryOptions,
  priorityOptions,
  statusOptions,
  PlanStatus,
} from '../../api/types';

const { Option } = Select;

/**
 * PlanListView 组件
 */
const PlanListView = () => {
  const navigate = useNavigate();
  const [searchKeyword, setSearchKeyword] = useState('');

  // 从 Store 获取状态和方法
  const {
    plans,
    pagination,
    filters,
    loading,
    fetchPlans,
    setFilters,
    setPagination,
    removePlan,
    startExistingPlan,
    completeExistingPlan,
    cancelExistingPlan,
  } = usePlanStore();

  // 初始加载
  useEffect(() => {
    fetchPlans();
  }, [pagination.current, pagination.pageSize, filters]);

  // 处理搜索
  const handleSearch = () => {
    setFilters({ keyword: searchKeyword });
  };

  // 处理筛选变化
  const handleFilterChange = (key, value) => {
    setFilters({ [key]: value });
  };

  // 处理分页变化
  const handlePageChange = (page, pageSize) => {
    setPagination({ current: page, pageSize });
  };

  // 处理删除
  const handleDelete = async (id) => {
    try {
      await removePlan(id);
      message.success('计划已删除');
    } catch (error) {
      message.error('删除失败');
    }
  };

  // 处理启动
  const handleStart = async (id) => {
    try {
      await startExistingPlan(id);
      message.success('计划已启动');
    } catch (error) {
      message.error('启动失败');
    }
  };

  // 处理完成
  const handleComplete = async (id) => {
    try {
      await completeExistingPlan(id);
      message.success('计划已完成');
    } catch (error) {
      message.error('操作失败');
    }
  };

  // 处理取消
  const handleCancel = async (id) => {
    try {
      await cancelExistingPlan(id, '手动取消');
      message.success('计划已取消');
    } catch (error) {
      message.error('取消失败');
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '数据标签',
      dataIndex: 'data_tag',
      key: 'data_tag',
      width: 150,
    },
    {
      title: '计划名称',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
      render: (text, record) => (
        <a onClick={() => navigate(`/plans/${record.id}`)}>{text}</a>
      ),
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (category) => {
        const config = categoryOptions.find((opt) => opt.value === category);
        return config?.label || category;
      },
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (priority) => {
        const config = priorityOptions.find((opt) => opt.value === priority);
        return <Tag color={config?.color}>{priority}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => <PlanStatusBadge status={status} />,
    },
    {
      title: '计划开始时间',
      dataIndex: 'planned_start_time',
      key: 'planned_start_time',
      width: 180,
      render: (time) =>
        time ? new Date(time).toLocaleString('zh-CN') : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_, record) => {
        const { status, id } = record;
        const isDraft = status === PlanStatus.DRAFT;
        const isPending = status === PlanStatus.PENDING;
        const isInProgress = status === PlanStatus.IN_PROGRESS;

        return (
          <Space size="small">
            <Tooltip title="查看">
              <Button
                type="text"
                icon={<EyeOutlined />}
                onClick={() => navigate(`/plans/${id}`)}
              />
            </Tooltip>

            {isDraft && (
              <Tooltip title="编辑">
                <Button
                  type="text"
                  icon={<EditOutlined />}
                  onClick={() => navigate(`/plans/${id}/edit`)}
                />
              </Tooltip>
            )}

            {(isDraft || isPending) && (
              <Tooltip title="启动">
                <Button
                  type="text"
                  icon={<PlayCircleOutlined />}
                  onClick={() => handleStart(id)}
                />
              </Tooltip>
            )}

            {isInProgress && (
              <Tooltip title="完成">
                <Button
                  type="text"
                  icon={<CheckCircleOutlined />}
                  onClick={() => handleComplete(id)}
                />
              </Tooltip>
            )}

            {(isDraft || isPending || isInProgress) && (
              <Tooltip title="取消">
                <Popconfirm
                  title="确定要取消此计划吗？"
                  onConfirm={() => handleCancel(id)}
                  okText="确定"
                  cancelText="取消"
                >
                  <Button type="text" icon={<CloseCircleOutlined />} danger />
                </Popconfirm>
              </Tooltip>
            )}

            {isDraft && (
              <Tooltip title="删除">
                <Popconfirm
                  title="确定要删除此计划吗？"
                  onConfirm={() => handleDelete(id)}
                  okText="确定"
                  cancelText="取消"
                >
                  <Button type="text" icon={<DeleteOutlined />} danger />
                </Popconfirm>
              </Tooltip>
            )}
          </Space>
        );
      },
    },
  ];

  return (
    <Card
      title="计划管理"
      extra={
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/plans/create')}
        >
          创建计划
        </Button>
      }
    >
      {/* 筛选区域 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Input.Search
            placeholder="搜索计划名称或标签"
            value={searchKeyword}
            onChange={(e) => setSearchKeyword(e.target.value)}
            onSearch={handleSearch}
            enterButton={<SearchOutlined />}
          />
        </Col>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Select
            placeholder="筛选状态"
            style={{ width: '100%' }}
            allowClear
            value={filters.status}
            onChange={(value) => handleFilterChange('status', value)}
          >
            {statusOptions.map((opt) => (
              <Option key={opt.value} value={opt.value}>
                {opt.label}
              </Option>
            ))}
          </Select>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Select
            placeholder="筛选分类"
            style={{ width: '100%' }}
            allowClear
            value={filters.category}
            onChange={(value) => handleFilterChange('category', value)}
          >
            {categoryOptions.map((opt) => (
              <Option key={opt.value} value={opt.value}>
                {opt.label}
              </Option>
            ))}
          </Select>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Select
            placeholder="筛选优先级"
            style={{ width: '100%' }}
            allowClear
            value={filters.priority}
            onChange={(value) => handleFilterChange('priority', value)}
          >
            {priorityOptions.map((opt) => (
              <Option key={opt.value} value={opt.value}>
                {opt.label}
              </Option>
            ))}
          </Select>
        </Col>
      </Row>

      {/* 表格 */}
      <Table
        columns={columns}
        dataSource={plans}
        rowKey="id"
        loading={loading}
        pagination={{
          current: pagination.current,
          pageSize: pagination.pageSize,
          total: pagination.total,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条记录`,
          onChange: handlePageChange,
        }}
        scroll={{ x: 1200 }}
      />
    </Card>
  );
};

export default PlanListView;
