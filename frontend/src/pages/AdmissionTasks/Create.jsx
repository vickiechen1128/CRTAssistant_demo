/**
 * 创建准入任务页面
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Form, Input, DatePicker, Button, message } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { taskApi } from '../../api/tasks';

function CreateTask() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const taskData = {
        system_name: values.system_name,
        system_code: values.system_code,
        version: values.version,
        release_date: values.release_date?.format('YYYY-MM-DD'),
        remark: values.remark,
      };
      
      const response = await taskApi.create(taskData);
      message.success('任务创建成功');
      navigate(`/admission-tasks/${response.data.id}`);
    } catch (error) {
      message.error('创建任务失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', alignItems: 'center', gap: 16 }}>
        <Button 
          icon={<ArrowLeftOutlined />} 
          onClick={() => navigate('/admission-tasks')}
        >
          返回
        </Button>
        <h2 style={{ margin: 0 }}>创建准入任务</h2>
      </div>

      <Card>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          style={{ maxWidth: 600 }}
        >
          <Form.Item
            name="system_name"
            label="系统名称"
            rules={[{ required: true, message: '请输入系统名称' }]}
          >
            <Input placeholder="请输入系统名称" />
          </Form.Item>

          <Form.Item
            name="system_code"
            label="系统代码"
            rules={[{ required: true, message: '请输入系统代码' }]}
          >
            <Input placeholder="请输入系统代码" />
          </Form.Item>

          <Form.Item
            name="version"
            label="版本号"
            rules={[{ required: true, message: '请输入版本号' }]}
          >
            <Input placeholder="例如: v1.0.0" />
          </Form.Item>

          <Form.Item
            name="release_date"
            label="计划上线日期"
            rules={[{ required: true, message: '请选择计划上线日期' }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="remark"
            label="备注"
          >
            <Input.TextArea rows={4} placeholder="请输入备注信息（可选）" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>
              创建任务
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}

export default CreateTask;
