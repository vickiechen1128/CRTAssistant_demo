/**
 * 创建工作流模板页
 * 支持创建工作流和定义工作项
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Form,
  Input,
  Button,
  Steps,
  message,
  Space,
  Row,
  Col,
  Select,
  InputNumber,
  Switch,
  Divider,
  List,
  Popconfirm
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  ArrowLeftOutlined,
  SaveOutlined,
  EditOutlined
} from '@ant-design/icons';
import useWorkflowStore from '../../stores/workflowStore';
import AcceptanceCriteriaForm from '../../components/Business/Workflow/AcceptanceCriteriaForm';

const { Step } = Steps;
const { TextArea } = Input;
const { Option } = Select;

// 工作项类型选项
const workItemTypes = [
  { value: 'resource_delivery', label: '基础资源标准化交付' },
  { value: 'inventory', label: '服务对象台账' },
  { value: 'permission_handover', label: '生产环境权限移交' },
  { value: 'security_baseline', label: '安全基线核验' },
  { value: 'monitoring', label: '监控告警配置确认' },
  { value: 'custom', label: '自定义工作项' }
];

const WorkflowCreate = () => {
  const navigate = useNavigate();
  const { createWorkflow, loading } = useWorkflowStore();

  const [currentStep, setCurrentStep] = useState(0);
  const [basicForm] = Form.useForm();
  const [workItemForm] = Form.useForm();

  const [workflowData, setWorkflowData] = useState({
    name: '',
    description: ''
  });

  const [workItems, setWorkItems] = useState([]);
  const [editingWorkItem, setEditingWorkItem] = useState(null);

  // 步骤内容
  const steps = [
    {
      title: '基本信息',
      content: 'basic'
    },
    {
      title: '工作项',
      content: 'workItems'
    },
    {
      title: '确认',
      content: 'confirm'
    }
  ];

  // 下一步
  const handleNext = async () => {
    if (currentStep === 0) {
      try {
        const values = await basicForm.validateFields();
        setWorkflowData(values);
        setCurrentStep(1);
      } catch (error) {
        console.error('表单验证失败:', error);
      }
    } else if (currentStep === 1) {
      if (workItems.length === 0) {
        message.warning('请至少添加一个工作项');
        return;
      }
      setCurrentStep(2);
    }
  };

  // 上一步
  const handlePrev = () => {
    setCurrentStep(currentStep - 1);
  };

  // 添加工作项
  const handleAddWorkItem = () => {
    setEditingWorkItem({
      name: '',
      description: '',
      work_item_type: 'custom',
      estimated_duration: 60,
      is_required: true,
      acceptance_criteria: []
    });
    workItemForm.resetFields();
  };

  // 编辑工作项
  const handleEditWorkItem = (index) => {
    const item = workItems[index];
    setEditingWorkItem({ ...item, index });
    workItemForm.setFieldsValue(item);
  };

  // 保存工作项
  const handleSaveWorkItem = async () => {
    try {
      const values = await workItemForm.validateFields();
      const newWorkItems = [...workItems];

      if (editingWorkItem && editingWorkItem.index !== undefined) {
        // 更新
        newWorkItems[editingWorkItem.index] = {
          ...newWorkItems[editingWorkItem.index],
          ...values
        };
      } else {
        // 新增
        newWorkItems.push({
          ...values,
          display_order: newWorkItems.length
        });
      }

      setWorkItems(newWorkItems);
      setEditingWorkItem(null);
      workItemForm.resetFields();
      message.success('保存成功');
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  // 删除工作项
  const handleDeleteWorkItem = (index) => {
    const newWorkItems = workItems.filter((_, i) => i !== index);
    // 重新排序
    newWorkItems.forEach((item, i) => {
      item.display_order = i;
    });
    setWorkItems(newWorkItems);
  };

  // 提交创建工作流
  const handleSubmit = async () => {
    const data = {
      ...workflowData,
      work_items: workItems
    };

    const result = await createWorkflow(data);
    if (result) {
      message.success('工作流模板创建成功');
      navigate('/workflows');
    }
  };

  // 渲染基本信息步骤
  const renderBasicStep = () => (
    <Form
      form={basicForm}
      layout="vertical"
      initialValues={workflowData}
    >
      <Form.Item
        name="name"
        label="工作流名称"
        rules={[{ required: true, message: '请输入工作流名称' }]}
      >
        <Input placeholder="请输入工作流名称" maxLength={100} />
      </Form.Item>

      <Form.Item
        name="description"
        label="工作流描述"
      >
        <TextArea
          rows={4}
          placeholder="请输入工作流描述，说明适用场景和注意事项"
        />
      </Form.Item>
    </Form>
  );

  // 渲染工作项步骤
  const renderWorkItemsStep = () => (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleAddWorkItem}
          disabled={editingWorkItem !== null}
        >
          添加工作项
        </Button>
      </div>

      {/* 工作项编辑表单 */}
      {editingWorkItem && (
        <Card
          title={editingWorkItem.index !== undefined ? '编辑工作项' : '添加工作项'}
          style={{ marginBottom: 16 }}
          extra={
            <Space>
              <Button type="primary" onClick={handleSaveWorkItem}>
                保存
              </Button>
              <Button onClick={() => setEditingWorkItem(null)}>
                取消
              </Button>
            </Space>
          }
        >
          <Form
            form={workItemForm}
            layout="vertical"
            initialValues={editingWorkItem}
          >
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="name"
                  label="工作项名称"
                  rules={[{ required: true, message: '请输入工作项名称' }]}
                >
                  <Input placeholder="例如：基础资源标准化交付" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="work_item_type"
                  label="工作项类型"
                  rules={[{ required: true, message: '请选择工作项类型' }]}
                >
                  <Select placeholder="选择工作项类型">
                    {workItemTypes.map(type => (
                      <Option key={type.value} value={type.value}>{type.label}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Form.Item
              name="description"
              label="工作项描述"
            >
              <TextArea
                rows={2}
                placeholder="描述该工作项的具体内容和目标"
              />
            </Form.Item>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="estimated_duration"
                  label="预估时长（分钟）"
                >
                  <InputNumber
                    min={1}
                    style={{ width: '100%' }}
                    placeholder="预估完成所需时间"
                  />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="is_required"
                  label="是否必填"
                  valuePropName="checked"
                >
                  <Switch checkedChildren="是" unCheckedChildren="否" />
                </Form.Item>
              </Col>
            </Row>

            <Divider orientation="left">验收标准</Divider>

            <Form.Item>
              <AcceptanceCriteriaForm
                value={editingWorkItem.acceptance_criteria || []}
                onChange={(criteria) => {
                  setEditingWorkItem({
                    ...editingWorkItem,
                    acceptance_criteria: criteria
                  });
                }}
              />
            </Form.Item>
          </Form>
        </Card>
      )}

      {/* 工作项列表 */}
      <List
        bordered
        dataSource={workItems}
        renderItem={(item, index) => (
          <List.Item
            actions={[
              <Button
                type="text"
                icon={<EditOutlined />}
                onClick={() => handleEditWorkItem(index)}
                disabled={editingWorkItem !== null}
              />,
              <Popconfirm
                title="确定要删除这个工作项吗？"
                onConfirm={() => handleDeleteWorkItem(index)}
                okText="确定"
                cancelText="取消"
              >
                <Button
                  type="text"
                  danger
                  icon={<DeleteOutlined />}
                  disabled={editingWorkItem !== null}
                />
              </Popconfirm>
            ]}
          >
            <List.Item.Meta
              title={
                <Space>
                  <span>{index + 1}. {item.name}</span>
                  <span style={{ color: '#999', fontSize: 12 }}>
                    ({workItemTypes.find(t => t.value === item.work_item_type)?.label || '自定义'})
                  </span>
                  {item.is_required && <span style={{ color: '#ff4d4f' }}>*</span>}
                </Space>
              }
              description={
                <Space direction="vertical" size={0}>
                  {item.description && <span>{item.description}</span>}
                  <span style={{ color: '#999', fontSize: 12 }}>
                    验收标准: {item.acceptance_criteria?.length || 0} 条
                    {item.estimated_duration && ` | 预估时长: ${item.estimated_duration}分钟`}
                  </span>
                </Space>
              }
            />
          </List.Item>
        )}
        locale={{ emptyText: '暂无工作项，请点击"添加工作项"按钮创建' }}
      />
    </div>
  );

  // 渲染确认步骤
  const renderConfirmStep = () => (
    <div>
      <Card title="基本信息" style={{ marginBottom: 16 }}>
        <p><strong>工作流名称：</strong>{workflowData.name}</p>
        <p><strong>描述：</strong>{workflowData.description || '无'}</p>
      </Card>

      <Card title={`工作项列表（共 ${workItems.length} 个）`}>
        <List
          dataSource={workItems}
          renderItem={(item, index) => (
            <List.Item>
              <List.Item.Meta
                title={
                  <Space>
                    <span>{index + 1}. {item.name}</span>
                    <span style={{ color: '#999', fontSize: 12 }}>
                      ({workItemTypes.find(t => t.value === item.work_item_type)?.label || '自定义'})
                    </span>
                  </Space>
                }
                description={
                  <Space direction="vertical" size={0}>
                    {item.description && <span>{item.description}</span>}
                    <span style={{ color: '#999', fontSize: 12 }}>
                      验收标准: {item.acceptance_criteria?.length || 0} 条
                      {item.estimated_duration && ` | 预估时长: ${item.estimated_duration}分钟`}
                      {item.is_required ? ' | 必填' : ' | 选填'}
                    </span>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      </Card>
    </div>
  );

  return (
    <div className="workflow-create-page">
      <Card>
        {/* 标题 */}
        <div style={{ marginBottom: 24 }}>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/workflows')}
            style={{ marginRight: 16 }}
          >
            返回
          </Button>
          <span style={{ fontSize: 20, fontWeight: 'bold' }}>创建工作流模板</span>
        </div>

        {/* 步骤条 */}
        <Steps current={currentStep} style={{ marginBottom: 24 }}>
          {steps.map(step => (
            <Step key={step.title} title={step.title} />
          ))}
        </Steps>

        {/* 步骤内容 */}
        <div className="steps-content" style={{ minHeight: 400 }}>
          {currentStep === 0 && renderBasicStep()}
          {currentStep === 1 && renderWorkItemsStep()}
          {currentStep === 2 && renderConfirmStep()}
        </div>

        {/* 操作按钮 */}
        <div className="steps-action" style={{ marginTop: 24, textAlign: 'center' }}>
          <Space>
            {currentStep > 0 && (
              <Button onClick={handlePrev}>
                上一步
              </Button>
            )}
            {currentStep < steps.length - 1 && (
              <Button type="primary" onClick={handleNext}>
                下一步
              </Button>
            )}
            {currentStep === steps.length - 1 && (
              <Button
                type="primary"
                icon={<SaveOutlined />}
                onClick={handleSubmit}
                loading={loading}
              >
                创建
              </Button>
            )}
          </Space>
        </div>
      </Card>
    </div>
  );
};

export default WorkflowCreate;
