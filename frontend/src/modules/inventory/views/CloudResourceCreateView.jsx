/**
 * CloudResourceCreateView 组件
 * 创建云资源页面
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Button,
  Form,
  Input,
  Select,
  message,
  Space,
  Typography,
} from 'antd';
import { ArrowLeftOutlined, SaveOutlined } from '@ant-design/icons';
import { useInventoryStore } from '../store';

const { Title } = Typography;
const { Option } = Select;

// 资源类型选项
const resourceTypeOptions = [
  { value: 'ecs', label: 'ECS' },
  { value: 'rds', label: 'RDS' },
  { value: 'oss', label: 'OSS' },
  { value: 'slb', label: 'SLB' },
  { value: 'vpc', label: 'VPC' },
  { value: 'redis', label: 'Redis' },
  { value: 'kafka', label: 'Kafka' },
  { value: 'elasticsearch', label: 'Elasticsearch' },
];

/**
 * CloudResourceCreateView 组件
 */
const CloudResourceCreateView = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);

  const { createNewCloudResource } = useInventoryStore();

  // 处理表单提交
  const handleSubmit = async (values) => {
    setSubmitting(true);
    try {
      await createNewCloudResource(values);
      message.success('云资源创建成功');
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
          <Title level={4} style={{ margin: 0 }}>创建云资源</Title>
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
            name="app_id"
            label="关联应用"
            rules={[{ required: true, message: '请选择关联应用' }]}
          >
            <Input placeholder="请输入应用ID" />
          </Form.Item>

          <Form.Item
            name="resource_type"
            label="资源类型"
            rules={[{ required: true, message: '请选择资源类型' }]}
          >
            <Select placeholder="请选择资源类型">
              {resourceTypeOptions.map((option) => (
                <Option key={option.value} value={option.value}>
                  {option.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="resource_name"
            label="资源名称"
            rules={[{ required: true, message: '请输入资源名称' }]}
          >
            <Input placeholder="请输入资源名称" maxLength={100} />
          </Form.Item>

          <Form.Item name="configuration" label="资源配置">
            <Input.TextArea
              placeholder="请输入资源配置（JSON格式）"
              rows={4}
            />
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

export default CloudResourceCreateView;
