import React from 'react';
import {
  Card,
  Form,
  Input,
  Select,
  Button,
  Space,
  message,
  Row,
  Col,
  Divider,
} from 'antd';
import {
  SaveOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useSOPTemplateStore } from '../../store';

const { Option } = Select;
const { TextArea } = Input;

/**
 * SOP 模板创建页面
 */
const SOPTemplateCreateView = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const { createTemplate, loading } = useSOPTemplateStore();

  // 提交表单
  const handleSubmit = async (values) => {
    // 构建请求数据
    const data = {
      template_id: values.template_id,
      name: values.name,
      template_type: values.template_type,
      description: values.description,
      audit_matrix_config_id: values.audit_matrix_config_id,
      workflow_nodes: [], // 简化版本，不创建节点
    };

    const result = await createTemplate(data);
    if (result.success) {
      message.success('创建成功');
      navigate('/sop-templates');
    } else {
      message.error(result.message);
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        {/* 标题栏 */}
        <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
          <Col>
            <Space>
              <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate('/sop-templates')}
              >
                返回
              </Button>
              <h2 style={{ margin: 0 }}>新建 SOP 模板</h2>
            </Space>
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={() => form.submit()}
              loading={loading}
            >
              保存
            </Button>
          </Col>
        </Row>

        <Divider />

        {/* 表单 */}
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          style={{ maxWidth: 800 }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="template_id"
                label="模板ID"
                rules={[
                  { required: true, message: '请输入模板ID' },
                  { pattern: /^[a-z0-9_]+$/, message: '只能包含小写字母、数字和下划线' },
                ]}
              >
                <Input placeholder="例如: standard_admission_v1" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="name"
                label="模板名称"
                rules={[{ required: true, message: '请输入模板名称' }]}
              >
                <Input placeholder="例如: 标准准入模板" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="template_type"
                label="模板类型"
                rules={[{ required: true, message: '请选择模板类型' }]}
              >
                <Select placeholder="选择模板类型">
                  <Option value="standard_admission">标准准入</Option>
                  <Option value="emergency_admission">紧急准入</Option>
                  <Option value="change_management">变更管理</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="audit_matrix_config_id"
                label="审核矩阵配置"
              >
                <Select placeholder="选择审核矩阵配置" allowClear>
                  <Option value="default">默认配置</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="description"
            label="模板描述"
          >
            <TextArea
              rows={4}
              placeholder="请输入模板描述..."
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SaveOutlined />}
                loading={loading}
              >
                保存
              </Button>
              <Button onClick={() => navigate('/sop-templates')}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default SOPTemplateCreateView;
