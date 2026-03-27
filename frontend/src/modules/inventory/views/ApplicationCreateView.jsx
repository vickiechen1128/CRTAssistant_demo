/**
 * ApplicationCreateView 组件
 * 创建应用系统页面
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Button,
  Form,
  Input,
  DatePicker,
  message,
  Space,
  Typography,
} from 'antd';
import { ArrowLeftOutlined, SaveOutlined } from '@ant-design/icons';
import { useInventoryStore } from '../store';

const { Title } = Typography;
const { TextArea } = Input;

/**
 * ApplicationCreateView 组件
 */
const ApplicationCreateView = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);

  const { createNewApplication } = useInventoryStore();

  // 处理表单提交
  const handleSubmit = async (values) => {
    setSubmitting(true);
    try {
      const data = {
        ...values,
        launch_time: values.launch_time?.format('YYYY-MM-DD'),
      };
      await createNewApplication(data);
      message.success('应用系统创建成功');
      navigate('/inventories');
    } catch (error) {
      message.error('创建失败: ' + (error.message || '未知错误'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/inventories')}>
            返回
          </Button>
          <Title level={4} style={{ margin: 0 }}>创建应用系统</Title>
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

export default ApplicationCreateView;
