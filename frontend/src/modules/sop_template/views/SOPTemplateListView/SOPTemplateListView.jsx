import React, { useEffect, useState } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Input,
  Select,
  message,
  Popconfirm,
  Tooltip,
  Row,
  Col,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  CopyOutlined,
  CheckCircleOutlined,
  StopOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useSOPTemplateStore } from '../../store';

const { Option } = Select;

/**
 * SOP 模板列表页面
 */
const SOPTemplateListView = () => {
  const navigate = useNavigate();
  const [searchKeyword, setSearchKeyword] = useState('');
  
  const {
    templates,
    loading,
    pagination,
    filters,
    setFilters,
    setPagination,
    fetchTemplates,
    deleteTemplate,
    publishTemplate,
    deprecateTemplate,
    cloneTemplate,
  } = useSOPTemplateStore();

  // 加载数据
  useEffect(() => {
    fetchTemplates();
  }, []);

  // 搜索
  const handleSearch = () => {
    setFilters({ ...filters, keyword: searchKeyword });
    fetchTemplates({ page: 1, keyword: searchKeyword });
  };

  // 分页变化
  const handleTableChange = (pagination) => {
    setPagination({
      current: pagination.current,
      pageSize: pagination.pageSize,
      total: pagination.total,
    });
    fetchTemplates({
      page: pagination.current,
      pageSize: pagination.pageSize,
    });
  };

  // 状态筛选
  const handleStatusChange = (value) => {
    setFilters({ ...filters, status: value });
    fetchTemplates({ page: 1, status: value });
  };

  // 类型筛选
  const handleTypeChange = (value) => {
    setFilters({ ...filters, templateType: value });
    fetchTemplates({ page: 1, template_type: value });
  };

  // 删除模板
  const handleDelete = async (templateId) => {
    const result = await deleteTemplate(templateId);
    if (result.success) {
      message.success('删除成功');
      fetchTemplates();
    } else {
      message.error(result.message);
    }
  };

  // 发布模板
  const handlePublish = async (templateId) => {
    const result = await publishTemplate(templateId);
    if (result.success) {
      message.success('发布成功');
      fetchTemplates();
    } else {
      message.error(result.message);
    }
  };

  // 弃用模板
  const handleDeprecate = async (templateId) => {
    const result = await deprecateTemplate(templateId, '手动弃用');
    if (result.success) {
      message.success('弃用成功');
      fetchTemplates();
    } else {
      message.error(result.message);
    }
  };

  // 克隆模板
  const handleClone = async (template) => {
    const result = await cloneTemplate(template.template_id, {
      new_template_id: `${template.template_id}_copy`,
      new_name: `${template.name}_副本`,
    });
    if (result.success) {
      message.success('克隆成功');
      fetchTemplates();
    } else {
      message.error(result.message);
    }
  };

  // 获取状态标签
  const getStatusTag = (status) => {
    const statusMap = {
      draft: { color: 'default', text: '草稿' },
      published: { color: 'success', text: '已发布' },
      deprecated: { color: 'error', text: '已弃用' },
    };
    const config = statusMap[status] || { color: 'default', text: status };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 获取类型标签
  const getTypeTag = (type) => {
    const typeMap = {
      standard_admission: { color: 'blue', text: '标准准入' },
      emergency_admission: { color: 'orange', text: '紧急准入' },
      change_management: { color: 'purple', text: '变更管理' },
    };
    const config = typeMap[type] || { color: 'default', text: type };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 表格列定义
  const columns = [
    {
      title: '模板ID',
      dataIndex: 'template_id',
      key: 'template_id',
      width: 180,
    },
    {
      title: '模板名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: '类型',
      dataIndex: 'template_type',
      key: 'template_type',
      width: 120,
      render: (type) => getTypeTag(type),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => getStatusTag(status),
    },
    {
      title: '版本',
      dataIndex: 'version',
      key: 'version',
      width: 80,
      render: (version) => `v${version}`,
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
      width: 250,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => navigate(`/sop-templates/${record.template_id}`)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => navigate(`/sop-templates/${record.template_id}/edit`)}
            />
          </Tooltip>
          <Tooltip title="克隆">
            <Button
              type="text"
              icon={<CopyOutlined />}
              onClick={() => handleClone(record)}
            />
          </Tooltip>
          {record.status === 'draft' && (
            <Tooltip title="发布">
              <Button
                type="text"
                icon={<CheckCircleOutlined />}
                onClick={() => handlePublish(record.template_id)}
              />
            </Tooltip>
          )}
          {record.status === 'published' && (
            <Tooltip title="弃用">
              <Button
                type="text"
                danger
                icon={<StopOutlined />}
                onClick={() => handleDeprecate(record.template_id)}
              />
            </Tooltip>
          )}
          <Popconfirm
            title="确认删除"
            description="确定要删除这个模板吗？此操作不可恢复。"
            onConfirm={() => handleDelete(record.template_id)}
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
            <h2 style={{ margin: 0 }}>工作流编排 (SOP模板)</h2>
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => navigate('/sop-templates/create')}
            >
              新建模板
            </Button>
          </Col>
        </Row>

        {/* 筛选栏 */}
        <Row gutter={16} style={{ marginBottom: 16 }}>
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
          <Col>
            <Select
              placeholder="模板类型"
              allowClear
              style={{ width: 150 }}
              onChange={handleTypeChange}
            >
              <Option value="standard_admission">标准准入</Option>
              <Option value="emergency_admission">紧急准入</Option>
              <Option value="change_management">变更管理</Option>
            </Select>
          </Col>
          <Col>
            <Select
              placeholder="状态"
              allowClear
              style={{ width: 120 }}
              onChange={handleStatusChange}
            >
              <Option value="draft">草稿</Option>
              <Option value="published">已发布</Option>
              <Option value="deprecated">已弃用</Option>
            </Select>
          </Col>
          <Col>
            <Button type="primary" onClick={handleSearch}>
              搜索
            </Button>
          </Col>
        </Row>

        {/* 表格 */}
        <Table
          columns={columns}
          dataSource={templates}
          rowKey="template_id"
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
          scroll={{ x: 1200 }}
        />
      </Card>
    </div>
  );
};

export default SOPTemplateListView;
