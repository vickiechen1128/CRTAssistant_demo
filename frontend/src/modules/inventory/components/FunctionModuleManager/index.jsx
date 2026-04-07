/**
 * FunctionModuleManager 组件
 * 功能模块管理组件 - 在应用详情页中使用
 */
import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Table,
  Tag,
  Space,
  Modal,
  Form,
  Input,
  Select,
  Tree,
  message,
  Popconfirm,
  Tooltip,
  Typography,
  Badge,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  BranchesOutlined,
  RocketOutlined,
  HistoryOutlined,
} from '@ant-design/icons';
import { useFunctionModuleStore } from '../../store/functionModuleStore';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

// 状态映射
const statusMap = {
  draft: { label: '草稿', color: 'default' },
  developing: { label: '开发中', color: 'processing' },
  testing: { label: '测试中', color: 'warning' },
  online: { label: '已上线', color: 'success' },
  offline: { label: '已下线', color: 'error' },
};

// 状态流转选项
const statusTransitions = {
  draft: ['developing'],
  developing: ['testing', 'draft'],
  testing: ['online', 'developing'],
  online: ['offline'],
  offline: ['online'],
};

/**
 * FunctionModuleManager 组件
 */
const FunctionModuleManager = ({ appId, relatedPlanId }) => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [currentModule, setCurrentModule] = useState(null);
  const [viewMode, setViewMode] = useState('table'); // 'table' | 'tree'
  const [form] = Form.useForm();

  const {
    modules,
    moduleTree,
    loading,
    fetchModules,
    fetchModuleTree,
    createModule,
    updateModule,
    deleteModule,
    updateModuleStatus,
    launchModule,
  } = useFunctionModuleStore();

  // 加载功能模块列表
  useEffect(() => {
    if (appId) {
      fetchModules(appId);
    }
  }, [appId, fetchModules]);

  // 获取状态标签
  const getStatusTag = (status) => {
    const config = statusMap[status] || { label: status, color: 'default' };
    return <Tag color={config.color}>{config.label}</Tag>;
  };

  // 打开创建模态框
  const handleCreate = () => {
    setIsEditMode(false);
    setCurrentModule(null);
    form.resetFields();
    if (relatedPlanId) {
      form.setFieldsValue({ related_plan_id: relatedPlanId });
    }
    setIsModalVisible(true);
  };

  // 打开编辑模态框
  const handleEdit = (record) => {
    setIsEditMode(true);
    setCurrentModule(record);
    form.setFieldsValue({
      module_code: record.module_code,
      module_name: record.module_name,
      version: record.version,
      description: record.description,
      parent_module_id: record.parent_module_id,
    });
    setIsModalVisible(true);
  };

  // 提交表单
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (isEditMode && currentModule) {
        await updateModule(appId, currentModule.id, values);
        message.success('功能模块更新成功');
      } else {
        await createModule(appId, values);
        message.success('功能模块创建成功');
      }
      
      setIsModalVisible(false);
      fetchModules(appId);
    } catch (error) {
      message.error('操作失败: ' + (error.message || '未知错误'));
    }
  };

  // 删除功能模块
  const handleDelete = async (moduleId) => {
    try {
      await deleteModule(appId, moduleId);
      message.success('功能模块删除成功');
      fetchModules(appId);
    } catch (error) {
      message.error('删除失败: ' + (error.message || '未知错误'));
    }
  };

  // 更新状态
  const handleStatusChange = async (moduleId, newStatus) => {
    try {
      await updateModuleStatus(appId, moduleId, newStatus);
      message.success('状态更新成功');
      fetchModules(appId);
    } catch (error) {
      message.error('状态更新失败: ' + (error.message || '未知错误'));
    }
  };

  // 上线功能模块
  const handleLaunch = async (moduleId) => {
    try {
      await launchModule(appId, moduleId, relatedPlanId);
      message.success('功能模块上线成功');
      fetchModules(appId);
    } catch (error) {
      message.error('上线失败: ' + (error.message || '未知错误'));
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '模块编码',
      dataIndex: 'module_code',
      key: 'module_code',
      width: 150,
    },
    {
      title: '模块名称',
      dataIndex: 'module_name',
      key: 'module_name',
      width: 200,
    },
    {
      title: '版本',
      dataIndex: 'version',
      key: 'version',
      width: 100,
      render: (version) => <Tag color="blue">{version}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => getStatusTag(status),
    },
    {
      title: '上线时间',
      dataIndex: 'launch_time',
      key: 'launch_time',
      width: 150,
      render: (time) => time || '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 250,
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          
          {/* 状态流转按钮 */}
          {record.status === 'testing' && (
            <Tooltip title="上线">
              <Button
                type="text"
                icon={<RocketOutlined style={{ color: '#52c41a' }} />}
                onClick={() => handleLaunch(record.id)}
              />
            </Tooltip>
          )}
          
          {/* 状态变更下拉 */}
          <Select
            size="small"
            style={{ width: 100 }}
            placeholder="变更状态"
            value={record.status}
            onChange={(value) => handleStatusChange(record.id, value)}
            disabled={record.status === 'online'}
          >
            {Object.entries(statusMap).map(([key, config]) => (
              <Option key={key} value={key}>
                {config.label}
              </Option>
            ))}
          </Select>
          
          <Popconfirm
            title="确定删除此功能模块吗？"
            description="删除后不可恢复"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="text" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 树形数据转换
  const convertToTreeData = (data) => {
    return data.map((item) => ({
      title: (
        <Space>
          <Text strong>{item.module_name}</Text>
          <Tag size="small">{item.version}</Tag>
          {getStatusTag(item.status)}
        </Space>
      ),
      key: item.id,
      children: item.children ? convertToTreeData(item.children) : [],
    }));
  };

  return (
    <Card
      title={
        <Space>
          <BranchesOutlined />
          <span>功能模块管理</span>
          <Badge count={modules.length} style={{ backgroundColor: '#1890ff' }} />
        </Space>
      }
      extra={
        <Space>
          <Button
            type={viewMode === 'table' ? 'primary' : 'default'}
            size="small"
            onClick={() => setViewMode('table')}
          >
            列表
          </Button>
          <Button
            type={viewMode === 'tree' ? 'primary' : 'default'}
            size="small"
            onClick={() => {
              setViewMode('tree');
              fetchModuleTree(appId);
            }}
          >
            树形
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
          >
            新增模块
          </Button>
        </Space>
      }
    >
      {viewMode === 'table' ? (
        <Table
          columns={columns}
          dataSource={modules}
          rowKey="id"
          loading={loading}
          pagination={false}
          size="small"
        />
      ) : (
        <Tree
          treeData={convertToTreeData(moduleTree)}
          defaultExpandAll
          showLine
          showIcon
        />
      )}

      {/* 创建/编辑模态框 */}
      <Modal
        title={isEditMode ? '编辑功能模块' : '新增功能模块'}
        open={isModalVisible}
        onOk={handleSubmit}
        onCancel={() => setIsModalVisible(false)}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
        >
          {!isEditMode && (
            <Form.Item
              name="module_code"
              label="模块编码"
              rules={[
                { required: true, message: '请输入模块编码' },
                { pattern: /^[a-z0-9_]+$/, message: '只能使用小写字母、数字和下划线' },
              ]}
            >
              <Input placeholder="例如: order_module" />
            </Form.Item>
          )}
          
          <Form.Item
            name="module_name"
            label="模块名称"
            rules={[{ required: true, message: '请输入模块名称' }]}
          >
            <Input placeholder="请输入模块名称" />
          </Form.Item>
          
          {!isEditMode && (
            <Form.Item
              name="version"
              label="版本号"
              initialValue="1.0.0"
              rules={[{ required: true, message: '请输入版本号' }]}
            >
              <Input placeholder="例如: 1.0.0" />
            </Form.Item>
          )}
          
          <Form.Item
            name="parent_module_id"
            label="父模块"
          >
            <Select placeholder="选择父模块（可选）" allowClear>
              {modules.map((m) => (
                <Option key={m.id} value={m.id}>
                  {m.module_name} ({m.module_code})
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item
            name="description"
            label="模块描述"
          >
            <TextArea rows={3} placeholder="请输入模块描述" />
          </Form.Item>
          
          {relatedPlanId && (
            <Form.Item
              name="related_plan_id"
              label="关联计划"
            >
              <Input disabled value={relatedPlanId} />
            </Form.Item>
          )}
        </Form>
      </Modal>
    </Card>
  );
};

export default FunctionModuleManager;
