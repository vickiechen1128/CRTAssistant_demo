/**
 * 应用系统台账创建页面
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Form,
  Input,
  Button,
  DatePicker,
  Space,
  Tag,
  Select,
  Alert,
  Divider,
  Table,
  message,
} from 'antd';
import {
  ArrowLeftOutlined,
  PlusOutlined,
  SaveOutlined,
  DeleteOutlined,
  DesktopOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';

const { TextArea } = Input;
const { Option } = Select;

function AppInventoryCreate() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [modules, setModules] = useState([
    { id: 1, name: '', description: '', launchDate: null, status: 'active' },
  ]);

  // 添加功能模块
  const addModule = () => {
    const newId = modules.length > 0 ? Math.max(...modules.map((m) => m.id)) + 1 : 1;
    setModules([
      ...modules,
      { id: newId, name: '', description: '', launchDate: null, status: 'active' },
    ]);
  };

  // 删除功能模块
  const removeModule = (id) => {
    if (modules.length === 1) {
      message.warning('至少保留一个功能模块');
      return;
    }
    setModules(modules.filter((m) => m.id !== id));
  };

  // 更新模块字段
  const updateModule = (id, field, value) => {
    setModules(
      modules.map((m) => (m.id === id ? { ...m, [field]: value } : m))
    );
  };

  // 提交表单
  const handleSubmit = () => {
    form.validateFields().then((values) => {
      console.log('表单数据:', { ...values, modules });
      message.success('应用系统台账创建成功！');
      navigate('/inventories');
    });
  };

  // 保存草稿
  const handleSaveDraft = () => {
    message.success('草稿已保存');
  };

  return (
    <div>
      {/* 页面标题 */}
      <Card style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div
              style={{
                fontSize: 20,
                fontWeight: 600,
                marginBottom: 4,
                display: 'flex',
                alignItems: 'center',
                gap: 12,
              }}
            >
              <div
                style={{
                  width: 44,
                  height: 44,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  borderRadius: 12,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 24,
                  color: 'white',
                }}
              >
                <DesktopOutlined />
              </div>
              <div>
                <div>创建应用系统台账</div>
                <div style={{ fontSize: 13, color: '#666', fontWeight: 'normal', marginTop: 4 }}>
                  台账管理 &gt; 应用系统台账 &gt; 创建
                </div>
              </div>
            </div>
          </div>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/inventories')}>
            返回列表
          </Button>
        </div>
      </Card>

      {/* 提示信息 */}
      <Alert
        message="创建应用系统台账后，系统将自动生成唯一台账ID。该台账可在创建计划时被引用，系统会自动将计划ID关联到台账的 related_plan_ids 字段中。"
        type="info"
        showIcon
        icon={<InfoCircleOutlined />}
        style={{ marginBottom: 24 }}
      />

      {/* 表单 */}
      <Form form={form} layout="vertical">
        <Card style={{ marginBottom: 24 }}>
          <Divider orientation="left" style={{ fontSize: 16, fontWeight: 600 }}>
            <span
              style={{
                width: 28,
                height: 28,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                borderRadius: 6,
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 14,
                marginRight: 8,
              }}
            >
              1
            </span>
            基本信息
          </Divider>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
            <Form.Item
              name="appName"
              label="应用名称"
              rules={[{ required: true, message: '请输入应用系统名称' }]}
            >
              <Input placeholder="请输入应用系统名称，如：订单管理系统" />
            </Form.Item>

            <Form.Item name="hostname" label="主机名">
              <Input placeholder="如：order-server-01" />
            </Form.Item>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
            <Form.Item name="url" label="应用地址URL">
              <Input placeholder="https://order.example.com" />
            </Form.Item>

            <Form.Item
              name="launchTime"
              label="系统上线时间"
              rules={[{ required: true, message: '请选择系统上线时间' }]}
            >
              <DatePicker showTime style={{ width: '100%' }} />
            </Form.Item>
          </div>

          <Form.Item name="description" label="应用情况说明">
            <TextArea
              rows={4}
              placeholder="描述应用系统的业务功能、使用场景、重要性等级等"
            />
          </Form.Item>
        </Card>

        <Card style={{ marginBottom: 24 }}>
          <Divider orientation="left" style={{ fontSize: 16, fontWeight: 600 }}>
            <span
              style={{
                width: 28,
                height: 28,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                borderRadius: 6,
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 14,
                marginRight: 8,
              }}
            >
              2
            </span>
            负责人信息
          </Divider>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
            <Form.Item
              name="businessManager"
              label="业务负责人"
              rules={[{ required: true, message: '请输入业务负责人姓名' }]}
            >
              <Input placeholder="业务负责人姓名" />
            </Form.Item>

            <Form.Item
              name="businessContact"
              label="业务负责人联系方式"
              rules={[{ required: true, message: '请输入业务负责人联系方式' }]}
            >
              <Input placeholder="邮箱或电话" />
            </Form.Item>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
            <Form.Item
              name="projectManager"
              label="项目负责人"
              rules={[{ required: true, message: '请输入项目负责人姓名' }]}
            >
              <Input placeholder="项目负责人姓名" />
            </Form.Item>

            <Form.Item
              name="projectContact"
              label="项目负责人联系方式"
              rules={[{ required: true, message: '请输入项目负责人联系方式' }]}
            >
              <Input placeholder="邮箱或电话" />
            </Form.Item>
          </div>
        </Card>

        <Card style={{ marginBottom: 24 }}>
          <Divider orientation="left" style={{ fontSize: 16, fontWeight: 600 }}>
            <span
              style={{
                width: 28,
                height: 28,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                borderRadius: 6,
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 14,
                marginRight: 8,
              }}
            >
              3
            </span>
            功能模块信息
          </Divider>

          <div
            style={{
              background: '#f8f9fa',
              borderRadius: 12,
              padding: 24,
              border: '1px dashed #d9d9d9',
            }}
          >
            {modules.map((module, index) => (
              <Card
                key={module.id}
                size="small"
                style={{ marginBottom: 12, border: '1px solid #e8e8e8' }}
                title={
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: '#667eea', fontWeight: 600 }}>模块 {index + 1}</span>
                    <Button
                      type="text"
                      danger
                      size="small"
                      icon={<DeleteOutlined />}
                      onClick={() => removeModule(module.id)}
                    >
                      删除
                    </Button>
                  </div>
                }
              >
                <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 2fr 1fr auto', gap: 12 }}>
                  <Input
                    placeholder="模块名称"
                    value={module.name}
                    onChange={(e) => updateModule(module.id, 'name', e.target.value)}
                  />
                  <Input
                    placeholder="模块描述"
                    value={module.description}
                    onChange={(e) => updateModule(module.id, 'description', e.target.value)}
                  />
                  <DatePicker
                    placeholder="上线日期"
                    style={{ width: '100%' }}
                    value={module.launchDate}
                    onChange={(date) => updateModule(module.id, 'launchDate', date)}
                  />
                  <Select
                    value={module.status}
                    onChange={(value) => updateModule(module.id, 'status', value)}
                    style={{ width: 100 }}
                  >
                    <Option value="active">启用</Option>
                    <Option value="inactive">停用</Option>
                  </Select>
                </div>
              </Card>
            ))}

            <Button
              type="dashed"
              block
              icon={<PlusOutlined />}
              onClick={addModule}
              style={{
                border: '2px dashed #667eea',
                color: '#667eea',
                height: 48,
              }}
            >
              添加功能模块
            </Button>
          </div>
        </Card>

        {/* 表单操作 */}
        <Card>
          <div
            style={{
              display: 'flex',
              justifyContent: 'flex-end',
              gap: 12,
            }}
          >
            <Button onClick={() => navigate('/inventories')}>取消</Button>
            <Button icon={<SaveOutlined />} onClick={handleSaveDraft}>
              保存草稿
            </Button>
            <Button
              type="primary"
              onClick={handleSubmit}
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
              }}
            >
              创建台账
            </Button>
          </div>
        </Card>
      </Form>
    </div>
  );
}

export default AppInventoryCreate;
