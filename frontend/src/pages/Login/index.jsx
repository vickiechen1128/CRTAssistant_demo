/**
 * 登录页面
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useAuthStore } from '../../stores';

function Login() {
  const navigate = useNavigate();
  const { login, isLoading } = useAuthStore();
  const [form] = Form.useForm();

  const handleSubmit = async (values) => {
    console.log('开始登录:', values.username);
    const success = await login(values);
    console.log('登录结果:', success);
    
    // 检查token是否保存成功
    const savedToken = localStorage.getItem('access_token');
    console.log('保存的token:', savedToken ? '存在' : '不存在');
    
    if (success && savedToken) {
      message.success('登录成功');
      console.log('准备跳转到首页');
      navigate('/');
    } else {
      message.error('登录失败，请检查用户名和密码');
    }
  };

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#f0f2f5'
    }}>
      <Card 
        title="仿真运维经理" 
        style={{ width: 400 }}
        headStyle={{ textAlign: 'center', fontSize: 20 }}
      >
        <Form
          form={form}
          name="login"
          onFinish={handleSubmit}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input 
              prefix={<UserOutlined />} 
              placeholder="用户名" 
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password 
              prefix={<LockOutlined />} 
              placeholder="密码" 
            />
          </Form.Item>

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={isLoading}
              block
            >
              登录
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center', color: '#999', fontSize: 12 }}>
          默认账号: admin / admin123
        </div>
      </Card>
    </div>
  );
}

export default Login;
