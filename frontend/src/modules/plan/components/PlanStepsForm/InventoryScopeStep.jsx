/**
 * InventoryScopeStep 组件
 * Step 3: 选择涉及范围（台账和功能模块）
 * 改造后版本 - 对接真实台账管理API
 */
import React, { useEffect, useState } from 'react';
import {
  Card,
  Select,
  Button,
  Table,
  Space,
  Tag,
  Form,
  Input,
  Row,
  Col,
  message,
  Modal,
  Divider,
  Descriptions,
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  AppstoreOutlined,
  CodeOutlined,
  PlusCircleOutlined,
} from '@ant-design/icons';
import { usePlanStore } from '../../store';
import {
  categoryOptions,
  moduleActionOptions,
  PlanCategory,
  requiresInventorySelection,
  allowMultipleInventory,
} from '../../api/types';

const { Option } = Select;
const { confirm } = Modal;

/**
 * 涉及范围选择步骤组件
 * 改造点：
 * 1. 新系统上线时支持创建应用系统台账
 * 2. 功能模块对接真实台账API
 * 3. 支持从已有应用系统选择模块
 */
const InventoryScopeStep = ({ basicInfo }) => {
  const category = basicInfo?.category;

  const {
    creationData,
    inventoryList,
    appModules,
    fetchInventoryList,
    fetchAppModules,
    createInventoryApplication,
    setRelatedInventoryIds,
    addAffectedModule,
    updateAffectedModule,
    removeAffectedModule,
    clearAppModules,
  } = usePlanStore();

  const { relatedInventoryIds, affectedModules } = creationData;

  const [selectedApp, setSelectedApp] = useState(null);
  const [moduleFormVisible, setModuleFormVisible] = useState(false);
  const [editingModuleIndex, setEditingModuleIndex] = useState(null);
  const [moduleForm] = Form.useForm();

  // 新系统创建相关状态
  const [inventoryFormVisible, setInventoryFormVisible] = useState(false);
  const [inventoryForm] = Form.useForm();
  const [createdInventory, setCreatedInventory] = useState(null);

  // 模块选择相关状态（用于功能变更场景）
  const [selectedModules, setSelectedModules] = useState([]);
  const [moduleSelectVisible, setModuleSelectVisible] = useState(false);

  // 加载台账列表
  useEffect(() => {
    if (requiresInventorySelection(category)) {
      fetchInventoryList();
    }
  }, [category]);

  // 根据分类获取标题和说明
  const getScopeConfig = () => {
    switch (category) {
      case PlanCategory.NEW_SYSTEM:
        return {
          title: '新系统上线',
          description: '需要创建新的应用系统台账，可以添加功能模块、云资源和账号信息',
          showInventorySelect: false,
          showModuleCreate: true,
          showInventoryCreate: true,
        };
      case PlanCategory.NEW_FEATURE:
        return {
          title: '新功能上线',
          description: '选择已有应用系统，添加新的功能模块',
          showInventorySelect: true,
          showModuleCreate: true,
          singleInventory: true,
        };
      case PlanCategory.FUNC_CHANGE:
        return {
          title: '功能变更',
          description: '选择应用系统和功能模块，进行更新操作',
          showInventorySelect: true,
          showModuleSelect: true,
          showModuleCreate: false,
          singleInventory: true,
        };
      case PlanCategory.ARCH_CHANGE:
        return {
          title: '架构变更',
          description: '选择多个应用系统，可能涉及云资源/数据库变更',
          showInventorySelect: true,
          multipleInventory: true,
        };
      case PlanCategory.SECURITY_CHECK:
        return {
          title: '安全检查',
          description: '安全检查不需要关联台账，将针对指定范围进行安全扫描',
          showInventorySelect: false,
        };
      default:
        return {
          title: '选择涉及范围',
          description: '请选择计划涉及的台账范围',
          showInventorySelect: true,
        };
    }
  };

  const scopeConfig = getScopeConfig();

  // 处理应用系统选择
  const handleAppSelect = (value) => {
    if (allowMultipleInventory(category)) {
      setRelatedInventoryIds(value);
    } else {
      setRelatedInventoryIds(value ? [value] : []);
      setSelectedApp(value);
      if (value) {
        fetchAppModules(value);
      } else {
        clearAppModules();
        setSelectedModules([]);
      }
    }
  };

  // 创建应用系统台账（新系统上线场景）
  const handleCreateInventory = async (values) => {
    try {
      const inventoryData = {
        app_name: values.app_name,
        app_description: values.app_description || '',
        system_type: values.system_type || 'web',
        deploy_env: values.deploy_env || 'production',
        business_owner: values.business_owner || 'admin',
        project_owner: values.project_owner || 'admin',
        current_version: values.current_version || 'v1.0.0',
        launch_time: new Date().toISOString(),
      };

      const result = await createInventoryApplication(inventoryData);

      if (result && result.id) {
        setCreatedInventory(result);
        setRelatedInventoryIds([result.id]);
        message.success('应用系统台账创建成功');
        setInventoryFormVisible(false);
        inventoryForm.resetFields();
      }
    } catch (error) {
      message.error('创建应用系统台账失败: ' + (error.message || '未知错误'));
    }
  };

  // 添加/编辑模块
  const handleSaveModule = (values) => {
    const moduleData = {
      ...values,
      module_id: editingModuleIndex !== null
        ? affectedModules[editingModuleIndex].module_id
        : `temp-${Date.now()}`,
    };

    if (editingModuleIndex !== null) {
      updateAffectedModule(editingModuleIndex, moduleData);
      message.success('模块已更新');
    } else {
      addAffectedModule(moduleData);
      message.success('模块已添加');
    }

    setModuleFormVisible(false);
    setEditingModuleIndex(null);
    moduleForm.resetFields();
  };

  // 从已有应用系统选择模块
  const handleSelectExistingModules = () => {
    if (!selectedApp) {
      message.warning('请先选择应用系统');
      return;
    }
    setModuleSelectVisible(true);
  };

  // 确认选择已有模块
  const handleConfirmModuleSelection = () => {
    if (selectedModules.length === 0) {
      message.warning('请至少选择一个模块');
      return;
    }

    // 将选中的模块添加到 affectedModules
    selectedModules.forEach(module => {
      const moduleData = {
        module_id: module.module_code || module.id,
        module_name: module.module_name,
        action: 'update',
        before_version: module.version || 'v1.0.0',
        after_version: '',
        change_description: '',
      };
      addAffectedModule(moduleData);
    });

    message.success(`已添加 ${selectedModules.length} 个模块`);
    setModuleSelectVisible(false);
    setSelectedModules([]);
  };

  // 编辑模块
  const handleEditModule = (index) => {
    const module = affectedModules[index];
    setEditingModuleIndex(index);
    moduleForm.setFieldsValue(module);
    setModuleFormVisible(true);
  };

  // 删除模块
  const handleDeleteModule = (index) => {
    confirm({
      title: '确认删除模块？',
      content: '删除后无法恢复，是否继续？',
      okText: '确认删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: () => {
        removeAffectedModule(index);
        message.success('模块已删除');
      },
    });
  };

  // 模块表格列
  const moduleColumns = [
    {
      title: '模块名称',
      dataIndex: 'module_name',
      key: 'module_name',
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
      render: (action) => {
        const config = moduleActionOptions.find(opt => opt.value === action);
        return <Tag color={config?.color}>{config?.label}</Tag>;
      },
    },
    {
      title: '版本变更',
      key: 'version',
      render: (_, record) => (
        <span>
          {record.before_version || '-'}
          {' → '}
          {record.after_version || '-'}
        </span>
      ),
    },
    {
      title: '变更说明',
      dataIndex: 'change_description',
      key: 'change_description',
      ellipsis: true,
    },
    {
      title: '操作',
      key: 'operation',
      render: (_, record, index) => (
        <Space>
          <Button type="link" onClick={() => handleEditModule(index)}>
            编辑
          </Button>
          <Button type="link" danger onClick={() => handleDeleteModule(index)}>
            删除
          </Button>
        </Space>
      ),
    },
  ];

  // 已有模块选择表格列
  const existingModuleColumns = [
    {
      title: '模块名称',
      dataIndex: 'module_name',
      key: 'module_name',
    },
    {
      title: '模块编码',
      dataIndex: 'module_code',
      key: 'module_code',
    },
    {
      title: '当前版本',
      dataIndex: 'version',
      key: 'version',
      render: (version) => version || 'v1.0.0',
    },
    {
      title: '负责人',
      dataIndex: 'owner',
      key: 'owner',
    },
  ];

  // 如果没有需要选择台账的分类
  if (category === PlanCategory.SECURITY_CHECK) {
    return (
      <div>
        <Card>
          <h4>{scopeConfig.title}</h4>
          <p style={{ color: '#666' }}>{scopeConfig.description}</p>
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <Tag color="blue">安全检查</Tag>
            <p style={{ marginTop: 16, color: '#999' }}>
              安全检查将在计划执行时针对指定范围进行安全扫描
            </p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <h4>{scopeConfig.title}</h4>
        <p style={{ color: '#666' }}>{scopeConfig.description}</p>
      </Card>

      {/* 新系统上线：创建应用系统台账 */}
      {scopeConfig.showInventoryCreate && (
        <Card
          title="应用系统台账"
          style={{ marginBottom: 16 }}
          extra={
            !createdInventory && (
              <Button
                type="primary"
                icon={<PlusCircleOutlined />}
                onClick={() => setInventoryFormVisible(true)}
              >
                创建台账
              </Button>
            )
          }
        >
          {createdInventory ? (
            <Descriptions size="small" column={2}>
              <Descriptions.Item label="应用名称">{createdInventory.app_name}</Descriptions.Item>
              <Descriptions.Item label="系统类型">{createdInventory.system_type}</Descriptions.Item>
              <Descriptions.Item label="部署环境">{createdInventory.deploy_env}</Descriptions.Item>
              <Descriptions.Item label="当前版本">{createdInventory.current_version}</Descriptions.Item>
              <Descriptions.Item label="业务负责人">{createdInventory.business_owner}</Descriptions.Item>
              <Descriptions.Item label="项目负责人">{createdInventory.project_owner}</Descriptions.Item>
            </Descriptions>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
              请先创建应用系统台账
            </div>
          )}
        </Card>
      )}

      {/* 应用系统选择 */}
      {scopeConfig.showInventorySelect !== false && (
        <Card title="选择应用系统" style={{ marginBottom: 16 }}>
          <Select
            style={{ width: '100%' }}
            placeholder="请选择应用系统"
            value={allowMultipleInventory(category) ? relatedInventoryIds : relatedInventoryIds[0]}
            onChange={handleAppSelect}
            mode={allowMultipleInventory(category) ? 'multiple' : undefined}
            showSearch
            optionFilterProp="children"
          >
            {Array.isArray(inventoryList) && inventoryList.map((app) => (
              <Option key={app.id} value={app.id}>
                {app.app_name || app.name}
              </Option>
            ))}
          </Select>

          {relatedInventoryIds.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <Tag color="blue">已选择 {relatedInventoryIds.length} 个应用系统</Tag>
            </div>
          )}
        </Card>
      )}

      {/* 功能模块管理 */}
      {scopeConfig.showModuleCreate && (
        <Card
          title="功能模块"
          style={{ marginBottom: 16 }}
          extra={
            <Space>
              {scopeConfig.showModuleSelect && (
                <Button
                  icon={<AppstoreOutlined />}
                  onClick={handleSelectExistingModules}
                  disabled={!selectedApp}
                >
                  选择已有模块
                </Button>
              )}
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => {
                  setEditingModuleIndex(null);
                  moduleForm.resetFields();
                  setModuleFormVisible(true);
                }}
              >
                添加模块
              </Button>
            </Space>
          }
        >
          {affectedModules.length > 0 ? (
            <Table
              dataSource={affectedModules}
              columns={moduleColumns}
              rowKey="module_id"
              pagination={false}
              size="small"
            />
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
              暂无功能模块，请点击上方按钮添加
            </div>
          )}
        </Card>
      )}

      {/* 创建台账弹窗 */}
      <Modal
        title="创建应用系统台账"
        open={inventoryFormVisible}
        onCancel={() => setInventoryFormVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={inventoryForm}
          layout="vertical"
          onFinish={handleCreateInventory}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="app_name"
                label="应用名称"
                rules={[{ required: true, message: '请输入应用名称' }]}
              >
                <Input placeholder="例如：订单管理系统" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="system_type"
                label="系统类型"
                rules={[{ required: true, message: '请选择系统类型' }]}
              >
                <Select placeholder="请选择系统类型">
                  <Option value="web">Web应用</Option>
                  <Option value="mobile">移动应用</Option>
                  <Option value="desktop">桌面应用</Option>
                  <Option value="microservice">微服务</Option>
                  <Option value="other">其他</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="deploy_env"
                label="部署环境"
                rules={[{ required: true, message: '请选择部署环境' }]}
              >
                <Select placeholder="请选择部署环境">
                  <Option value="production">生产环境</Option>
                  <Option value="staging">预发环境</Option>
                  <Option value="testing">测试环境</Option>
                  <Option value="development">开发环境</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="current_version"
                label="当前版本"
              >
                <Input placeholder="例如：v1.0.0" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="business_owner"
                label="业务负责人"
              >
                <Input placeholder="业务负责人" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="project_owner"
                label="项目负责人"
              >
                <Input placeholder="项目负责人" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="app_description"
            label="应用描述"
          >
            <Input.TextArea
              rows={3}
              placeholder="描述应用系统的功能和用途"
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                创建
              </Button>
              <Button onClick={() => setInventoryFormVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 选择已有模块弹窗 */}
      <Modal
        title="选择功能模块"
        open={moduleSelectVisible}
        onCancel={() => setModuleSelectVisible(false)}
        onOk={handleConfirmModuleSelection}
        width={700}
      >
        <Table
          dataSource={appModules}
          columns={existingModuleColumns}
          rowKey="module_code"
          rowSelection={{
            type: 'checkbox',
            onChange: (selectedRowKeys, selectedRows) => {
              setSelectedModules(selectedRows);
            },
          }}
          pagination={false}
          size="small"
          locale={{
            emptyText: '该应用系统暂无功能模块',
          }}
        />
      </Modal>

      {/* 模块表单弹窗 */}
      {moduleFormVisible && (
        <Card style={{ marginTop: 16, backgroundColor: '#f5f5f5' }}>
          <h4>{editingModuleIndex !== null ? '编辑模块' : '添加模块'}</h4>
          <Form
            form={moduleForm}
            layout="vertical"
            onFinish={handleSaveModule}
            initialValues={{ action: 'create' }}
          >
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="module_name"
                  label="模块名称"
                  rules={[{ required: true, message: '请输入模块名称' }]}
                >
                  <Input placeholder="例如：支付网关" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="action"
                  label="操作类型"
                  rules={[{ required: true, message: '请选择操作类型' }]}
                >
                  <Select placeholder="请选择操作类型">
                    {moduleActionOptions.map((opt) => (
                      <Option key={opt.value} value={opt.value}>
                        {opt.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="before_version"
                  label="变更前版本"
                >
                  <Input placeholder="例如：v1.0.0" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="after_version"
                  label="变更后版本"
                >
                  <Input placeholder="例如：v2.0.0" />
                </Form.Item>
              </Col>
            </Row>

            <Form.Item
              name="change_description"
              label="变更说明"
            >
              <Input.TextArea
                rows={2}
                placeholder="描述本次变更的内容"
              />
            </Form.Item>

            <Form.Item>
              <Space>
                <Button type="primary" htmlType="submit">
                  保存
                </Button>
                <Button onClick={() => setModuleFormVisible(false)}>
                  取消
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>
      )}
    </div>
  );
};

export default InventoryScopeStep;
