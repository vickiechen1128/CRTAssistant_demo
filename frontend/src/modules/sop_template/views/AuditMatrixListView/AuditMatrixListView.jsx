import React, { useEffect, useState } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Input,
  message,
  Popconfirm,
  Tooltip,
  Row,
  Col,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  StopOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import {
  getAuditMatrixList,
  deleteAuditMatrix,
  activateAuditMatrix,
  deactivateAuditMatrix,
} from '../../api';

/**
 * 审核矩阵配置列表页面
 */
const AuditMatrixListView = () => {
  const navigate = useNavigate();
  const [configs, setConfigs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });

  // 加载数据
  const fetchConfigs = async (params = {}) => {
    setLoading(true);
    try {
      const response = await getAuditMatrixList({
        keyword: searchKeyword,
        page: params.page || pagination.current,
        page_size: params.pageSize || pagination.pageSize,
        ...params,
      });
      
      if (response.data?.code === 200) {
        const { items, total, page, page_size } = response.data.data;
        setConfigs(items || []);
        setPagination({
          current: page,
          pageSize: page_size,
          total: total,
        });
      }
    } catch (error) {
      console.error('获取审核矩阵列表失败:', error);
      message.error('获取列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConfigs();
  }, []);

  // 搜索
  const handleSearch = () => {
    fetchConfigs({ page: 1, keyword: searchKeyword });
  };

  // 分页变化
  const handleTableChange = (pagination) => {
    setPagination({
      current: pagination.current,
      pageSize: pagination.pageSize,
      total: pagination.total,
    });
    fetchConfigs({
      page: pagination.current,
      pageSize: pagination.pageSize,
    });
  };

  // 删除配置
  const handleDelete = async (configId) => {
    try {
      const response = await deleteAuditMatrix(configId);
      if (response.data?.code === 200) {
        message.success('删除成功');
        fetchConfigs();
      } else {
        message.error(response.data?.message || '删除失败');
      }
    } catch (error) {
      console.error('删除审核矩阵失败:', error);
      message.error('删除失败');
    }
  };

  // 激活配置
  const handleActivate = async (configId) => {
    try {
      const response = await activateAuditMatrix(configId);
      if (response.data?.code === 200) {
        message.success('激活成功');
        fetchConfigs();
      } else {
        message.error(response.data?.message || '激活失败');
      }
    } catch (error) {
      console.error('激活审核矩阵失败:', error);
      message.error('激活失败');
    }
  };

  // 停用配置
  const handleDeactivate = async (configId) => {
    try {
      const response = await deactivateAuditMatrix(configId);
      if (response.data?.code === 200) {
        message.success('停用成功');
        fetchConfigs();
      } else {
        message.error(response.data?.message || '停用失败');
      }
    } catch (error) {
      console.error('停用审核矩阵失败:', error);
      message.error('停用失败');
    }
  };

  // 获取状态标签
  const getStatusTag = (isActive) => {
    return isActive ? 
      <Tag color="success">已激活</Tag> : 
      <Tag color="default">未激活</Tag>;
  };

  // 表格列定义
  const columns = [
    {
      title: '配置ID',
      dataIndex: 'config_id',
      key: 'config_id',
      width: 180,
    },
    {
      title: '配置名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (isActive) => getStatusTag(isActive),
    },
    {
      title: '规则数量',
      dataIndex: 'rules',
      key: 'rules',
      width: 100,
      render: (rules) => rules?.length || 0,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date) => date ? new Date(date).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => message.info('编辑功能待实现')}
            />
          </Tooltip>
          {!record.is_active ? (
            <Tooltip title="激活">
              <Button
                type="text"
                icon={<CheckCircleOutlined />}
                onClick={() => handleActivate(record.config_id)}
              />
            </Tooltip>
          ) : (
            <Tooltip title="停用">
              <Button
                type="text"
                danger
                icon={<StopOutlined />}
                onClick={() => handleDeactivate(record.config_id)}
              />
            </Tooltip>
          )}
          <Popconfirm
            title="确认删除"
            description="确定要删除这个配置吗？此操作不可恢复。"
            onConfirm={() => handleDelete(record.config_id)}
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

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        {/* 标题栏 */}
        <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
          <Col>
            <h2 style={{ margin: 0 }}>审核矩阵配置</h2>
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => message.info('创建功能待实现')}
            >
              新建配置
            </Button>
          </Col>
        </Row>

        {/* 筛选栏 */}
        <Row style={{ marginBottom: 16 }}>
          <Col>
            <Input
              placeholder="搜索关键词"
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              onPressEnter={handleSearch}
              prefix={<SearchOutlined />}
              style={{ width: 250 }}
            />
          </Col>
          <Col style={{ marginLeft: 8 }}>
            <Button type="primary" onClick={handleSearch}>
              搜索
            </Button>
          </Col>
        </Row>

        {/* 表格 */}
        <Table
          columns={columns}
          dataSource={configs}
          rowKey="config_id"
          loading={loading}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
          onChange={handleTableChange}
          scroll={{ x: 1000 }}
        />
      </Card>
    </div>
  );
};

export default AuditMatrixListView;
