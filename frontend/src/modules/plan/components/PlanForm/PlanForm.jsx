/**
 * PlanForm 组件
 * 创建/编辑计划表单（向导式）
 */
import React, { useState, useEffect } from 'react';
import {
  Form,
  Input,
  Select,
  DatePicker,
  Button,
  Steps,
  Card,
  Upload,
  message,
  Space,
  Alert,
  Radio,
} from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import {
  categoryOptions,
  priorityOptions,
  PlanCategory,
} from '../../api/types';

const { TextArea } = Input;
const { Option } = Select;
const { Step } = Steps;
const { Dragger } = Upload;

/**
 * PlanForm 组件
 * @param {Object} props
 * @param {Object} props.initialValues - 初始值
 * @param {Function} props.onSubmit - 提交回调
 * @param {Function} props.onCancel - 取消回调
 * @param {boolean} props.loading - 加载状态
 */
const PlanForm = ({ initialValues = {}, onSubmit, onCancel, loading = false }) => {
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [category, setCategory] = useState(initialValues.category);
  const [fileList, setFileList] = useState([]);

  // 步骤配置
  const steps = [
    { title: '基本信息', key: 'basic' },
    { title: '审批材料', key: 'files' },
    { title: '选择范围', key: 'scope' },
  ];

  // 处理分类变化
  const handleCategoryChange = (value) => {
    setCategory(value);
    form.setFieldsValue({ category: value });
  };

  // 下一步
  const handleNext = async () => {
    try {
      if (currentStep === 0) {
        // 验证第一步
        await form.validateFields([
          'name',
          'category',
          'priority',
          'planned_start_time',
        ]);
      } else if (currentStep === 1) {
        // 验证第二步 - 至少上传一个文件
        if (fileList.length === 0) {
          message.error('请至少上传一个审批材料');
          return;
        }
      }
      setCurrentStep(currentStep + 1);
    } catch (error) {
      console.error('验证失败:', error);
    }
  };

  // 上一步
  const handlePrev = () => {
    setCurrentStep(currentStep - 1);
  };

  // 提交
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();

      // 组装提交数据 - 与后端 CreatePlanSchema 对齐
      const submitData = {
        name: values.name,
        category: values.category,
        priority: values.priority,
        description: values.description,
        planned_start_time: values.planned_start_time?.toISOString(),
        planned_end_time: values.planned_end_time?.toISOString(),
      };

      onSubmit?.(submitData);
    } catch (error) {
      console.error('提交失败:', error);
    }
  };

  // 获取操作类型
  const getActionType = (cat) => {
    const mapping = {
      [PlanCategory.NEW_SYSTEM]: 'create_new',
      [PlanCategory.NEW_FEATURE]: 'select_and_edit',
      [PlanCategory.FUNC_CHANGE]: 'select_existing',
      [PlanCategory.ARCH_CHANGE]: 'select_existing',
      [PlanCategory.SECURITY_CHECK]: 'security_scan',
    };
    return mapping[cat] || 'select_existing';
  };

  // 上传配置
  const uploadProps = {
    name: 'file',
    multiple: true,
    action: '/api/upload', // 上传接口地址
    maxCount: 5,
    fileList,
    onChange: ({ fileList: newFileList }) => {
      setFileList(newFileList);
    },
    beforeUpload: (file) => {
      const isLt20M = file.size / 1024 / 1024 < 20;
      if (!isLt20M) {
        message.error('文件大小不能超过 20MB');
        return false;
      }
      return true;
    },
  };

  // 渲染步骤内容
  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <Form.Item
              name="name"
              label="计划名称"
              rules={[
                { required: true, message: '请输入计划名称' },
                { max: 200, message: '计划名称不能超过200字符' },
              ]}
            >
              <Input placeholder="请输入计划名称，如：订单系统v2.0上线" />
            </Form.Item>

            <Form.Item
              name="category"
              label="计划分类"
              rules={[{ required: true, message: '请选择计划分类' }]}
            >
              <Select
                placeholder="请选择计划分类"
                onChange={handleCategoryChange}
              >
                {categoryOptions.map((opt) => (
                  <Option key={opt.value} value={opt.value}>
                    {opt.label}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item
              name="priority"
              label="优先级"
              rules={[{ required: true, message: '请选择优先级' }]}
            >
              <Select placeholder="请选择优先级">
                {priorityOptions.map((opt) => (
                  <Option key={opt.value} value={opt.value}>
                    {opt.label}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item
              name="planned_start_time"
              label="计划开始时间"
              rules={[
                { required: true, message: '请选择计划开始时间' },
                {
                  validator: (_, value) => {
                    if (value && value.isBefore(dayjs())) {
                      return Promise.reject('计划开始时间必须大于当前时间');
                    }
                    return Promise.resolve();
                  },
                },
              ]}
            >
              <DatePicker
                showTime
                style={{ width: '100%' }}
                placeholder="请选择计划开始时间"
              />
            </Form.Item>

            <Form.Item name="planned_end_time" label="计划结束时间">
              <DatePicker
                showTime
                style={{ width: '100%' }}
                placeholder="请选择计划结束时间（可选）"
              />
            </Form.Item>

            <Form.Item name="description" label="计划说明">
              <TextArea
                rows={4}
                placeholder="请输入计划说明（可选）"
                maxLength={2000}
                showCount
              />
            </Form.Item>
          </Space>
        );

      case 1:
        return (
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <Alert
              message="审批材料要求"
              description="请上传会议纪要、审批邮件等审批材料，支持 PDF、图片格式，单个文件不超过 20MB"
              type="info"
              showIcon
            />

            <Form.Item
              required
              validateStatus={fileList.length === 0 ? 'error' : ''}
              help={fileList.length === 0 ? '请至少上传一个审批材料' : ''}
            >
              <Dragger {...uploadProps}>
                <p className="ant-upload-drag-icon">
                  <InboxOutlined />
                </p>
                <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
                <p className="ant-upload-hint">
                  支持单个或批量上传，文件大小不超过 20MB
                </p>
              </Dragger>
            </Form.Item>

            {fileList.length > 0 && (
              <Alert
                message={`已上传 ${fileList.length} 个文件`}
                type="success"
                showIcon
              />
            )}
          </Space>
        );

      case 2:
        return renderScopeStep();

      default:
        return null;
    }
  };

  // 渲染第三步 - 选择范围
  const renderScopeStep = () => {
    // 根据分类显示不同的界面
    switch (category) {
      case PlanCategory.NEW_SYSTEM:
        return (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Alert
              message="新系统上线"
              description="您需要填写新增应用系统台账信息"
              type="info"
              showIcon
            />
            <Form.Item
              name={['inventory_data', 'app_name']}
              label="应用系统名称"
              rules={[{ required: true, message: '请输入应用系统名称' }]}
            >
              <Input placeholder="请输入应用系统名称" />
            </Form.Item>
            <Form.Item
              name={['inventory_data', 'app_description']}
              label="应用描述"
            >
              <TextArea placeholder="请输入应用描述" rows={3} />
            </Form.Item>
          </Space>
        );

      case PlanCategory.SECURITY_CHECK:
        return (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Alert
              message="安全检查"
              description="安全检查不需要关联台账，请选择检查范围"
              type="info"
              showIcon
            />
            <Form.Item
              name={['inventory_data', 'scan_scope']}
              label="检查范围"
              rules={[{ required: true, message: '请选择检查范围' }]}
            >
              <Radio.Group>
                <Radio value="global">全系统安全扫描</Radio>
                <Radio value="targeted">指定范围检查</Radio>
              </Radio.Group>
            </Form.Item>
          </Space>
        );

      default:
        return (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Alert
              message="选择台账"
              description="请选择涉及的台账系统"
              type="info"
              showIcon
            />
            <Form.Item
              name={['inventory_data', 'selected_app_ids']}
              label="选择应用系统"
              rules={[{ required: true, message: '请至少选择一个应用系统' }]}
            >
              <Select
                mode="multiple"
                placeholder="请选择应用系统"
                style={{ width: '100%' }}
              >
                {/* 这里应该从接口获取台账列表 */}
                <Option value="app-001">订单系统</Option>
                <Option value="app-002">支付系统</Option>
                <Option value="app-003">用户中心</Option>
              </Select>
            </Form.Item>
          </Space>
        );
    }
  };

  return (
    <Card>
      <Steps current={currentStep} style={{ marginBottom: 24 }}>
        {steps.map((step) => (
          <Step key={step.key} title={step.title} />
        ))}
      </Steps>

      <Form
        form={form}
        layout="vertical"
        initialValues={initialValues}
        style={{ maxWidth: 600, margin: '0 auto' }}
      >
        {renderStepContent()}

        <Form.Item style={{ marginTop: 24 }}>
          <Space>
            {currentStep > 0 && (
              <Button onClick={handlePrev}>上一步</Button>
            )}
            {currentStep < steps.length - 1 && (
              <Button type="primary" onClick={handleNext}>
                下一步
              </Button>
            )}
            {currentStep === steps.length - 1 && (
              <Button
                type="primary"
                onClick={handleSubmit}
                loading={loading}
              >
                提交创建
              </Button>
            )}
            <Button onClick={onCancel}>取消</Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default PlanForm;
