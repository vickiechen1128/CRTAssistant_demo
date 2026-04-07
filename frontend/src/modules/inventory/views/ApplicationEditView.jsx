/**
 * ApplicationEditView 组件
 * 编辑应用系统页面
 */
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Card,
  Button,
  Form,
  Input,
  DatePicker,
  Select,
  message,
  Space,
  Typography,
  Spin,
} from 'antd';
import { ArrowLeftOutlined, SaveOutlined } from '@ant-design/icons';
import { useInventoryStore } from '../store';
import dayjs from 'dayjs';

const { Title } = Typography;
const { TextArea } = Input;
const { Option } = Select;

// 状态选项
const statusOptions = [
  { value: 'active', label: '活跃' },
  { value: 'inactive', label: '停用' },
  { value: 'archived', label: '已归档' },
];

/**
 * ApplicationEditView 组件
 */
const ApplicationEditView = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  const {
    currentApplication,
    fetchApplicationDetail,
    updateExistingApplication,
  } = useInventoryStore();

  // 加载详情数据
  useEffect(() => {
    if (id) {
      fetchApplicationDetail(id)
        .then(() => {
          setLoading(false);
        })
        .catch((error) => {
          message.error('获取应用系统详情失败: ' + (error.message || '未知错误'));
          setLoading(false);
        });
    }
  }, [id, fetchApplicationDetail]);

  // 设置表单初始值
  useEffect(() => {
    if (currentApplication) {
      form.setFieldsValue({
        app_name: currentApplication.app_name,
        business_owner: currentApplication.business_owner,
        project_owner: currentApplication.project_owner,
        app_description: currentApplication.app_description,
        hostname: currentApplication.hostname,
        app_url: currentApplication.app_url,
        status: currentApplication.status,
        launch_time: currentApplication.launch_time ? dayjs(currentApplication.launch_time) : null,
      });
    }
  }, [currentApplication, form]);

  // 处理表单提交
  const handleSubmit = async (values) => {
    setSubmitting(true);
    try {
      const data = {
        ...values,
        launch_time: values.launch_time?.format('YYYY-MM-DD'),
      };
      await updateExistingApplication(id, data);
      message.success('应用系统更新成功');
      navigate('/inventories');
    } catch (error) {
      message.error('更新失败: ' + (error.message || '未知错误'));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/inventories')}>
            返回
          </Button>
          <Title level={4} style={{ margin: 0 }}>编辑应用系统</Title>
        </Space>
      </Card>

      <Card>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          style={{ maxWidth: 600 }}
        >
          <Form.Item
            name="app_name"
            label="应用名称"
            rules={[{ required: true, message: '请输入应用名称' }]}
          >
            <Input placeholder="请输入应用名称" maxLength={100} />
          </Form.Item>

          <Form.Item
            name="business_owner"
            label="业务负责人"
            rules={[{ required: true, message: '请输入业务负责人' }]}
          >
            <Input placeholder="请输入业务负责人" maxLength={50} />
          </Form.Item>

          <Form.Item
            name="project_owner"
            label="项目负责人"
            rules={[{ required: true, message: '请输入项目负责人' }]}
          >
            <Input placeholder="请输入项目负责人" maxLength={50} />
          </Form.Item>

          <Form.Item
            name="status"
            label="状态"
            rules={[{ required: true, message: '请选择状态' }]}
          >
            <Select placeholder="请选择状态">
              {statusOptions.map((option) => (
                <Option key={option.value} value={option.value}>
                  {option.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="app_description" label="应用描述">
            <TextArea placeholder="请输入应用描述" rows={4} />
          </Form.Item>

          <Form.Item name="hostname" label="主机名">
            <Input placeholder="请输入主机名" maxLength={100} />
          </Form.Item>

          <Form.Item name="app_url" label="应用URL">
            <Input placeholder="请输入应用URL" maxLength={500} />
          </Form.Item>

          <Form.Item name="launch_time" label="上线时间">
            <DatePicker style={{ width: '100%' }} placeholder="选择上线时间" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={submitting} icon={<SaveOutlined />}>
                保存
              </Button>
              <Button onClick={() => navigate('/inventories')}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default ApplicationEditView;
