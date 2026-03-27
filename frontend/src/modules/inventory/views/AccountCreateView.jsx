/**
 * AccountCreateView 组件
 * 创建账号页面
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Button,
  Form,
  Input,
  Select,
  DatePicker,
  InputNumber,
  message,
  Space,
  Typography,
} from 'antd';
import { ArrowLeftOutlined, SaveOutlined } from '@ant-design/icons';
import { useInventoryStore } from '../store';

const { Title } = Typography;
const { Option } = Select;

// 账号类型选项
const accountTypeOptions = [
  { value: 'system', label: '系统账号' },
  { value: 'software', label: '软件账号' },
  { value: 'database', label: '数据库账号' },
];

// 权限级别选项
const permissionLevelOptions = [
  { value: 'admin', label: '管理员' },
  { value: 'operator', label: '操作员' },
  { value: 'viewer', label: '观察员' },
];

/**
 * AccountCreateView 组件
 */
const AccountCreateView = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);

  const { createNewAccount } = useInventoryStore();

  // 处理表单提交
  const handleSubmit = async (values) => {
    setSubmitting(true);
    try {
      const data = {
        ...values,
        valid_from: values.valid_from?.format('YYYY-MM-DD'),
        valid_until: values.valid_until?.format('YYYY-MM-DD'),
      };
      await createNewAccount(data);
      message.success('账号创建成功');
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
          <Title level={4} style={{ margin: 0 }}>创建账号</Title>
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
            name="account_type"
            label="账号类型"
            rules={[{ required: true, message: '请选择账号类型' }]}
          >
            <Select placeholder="请选择账号类型">
              {accountTypeOptions.map((option) => (
                <Option key={option.value} value={option.value}>
                  {option.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="account_name"
            label="账号名称"
            rules={[{ required: true, message: '请输入账号名称' }]}
          >
            <Input placeholder="请输入账号名称" maxLength={100} />
          </Form.Item>

          <Form.Item
            name="permission_level"
            label="权限级别"
            rules={[{ required: true, message: '请选择权限级别' }]}
          >
            <Select placeholder="请选择权限级别">
              {permissionLevelOptions.map((option) => (
                <Option key={option.value} value={option.value}>
                  {option.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="holder_name"
            label="持有人"
            rules={[{ required: true, message: '请输入持有人' }]}
          >
            <Input placeholder="请输入持有人" maxLength={50} />
          </Form.Item>

          <Form.Item
            name="valid_from"
            label="有效期开始"
            rules={[{ required: true, message: '请选择有效期开始时间' }]}
          >
            <DatePicker style={{ width: '100%' }} placeholder="选择有效期开始时间" />
          </Form.Item>

          <Form.Item
            name="valid_until"
            label="有效期结束"
            rules={[{ required: true, message: '请选择有效期结束时间' }]}
          >
            <DatePicker style={{ width: '100%' }} placeholder="选择有效期结束时间" />
          </Form.Item>

          <Form.Item
            name="password_change_cycle"
            label="密码修改周期（天）"
            initialValue={90}
          >
            <InputNumber min={1} max={365} style={{ width: '100%' }} />
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

export default AccountCreateView;
