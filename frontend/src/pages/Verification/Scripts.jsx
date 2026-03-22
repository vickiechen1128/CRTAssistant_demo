/**
 * 验证脚本管理页面
 */

import React, { useEffect, useState } from 'react';
import { Card, Table, Button, Space, Tag, Modal, Form, Input, Select, message, Drawer, Descriptions } from 'antd';
import { PlusOutlined, PlayCircleOutlined, EyeOutlined, CodeOutlined } from '@ant-design/icons';
import { verificationApi } from '../../api/verification';

const { TextArea } = Input;
const { Option } = Select;

function Scripts() {
  const [loading, setLoading] = useState(false);
  const [scripts, setScripts] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [detailVisible, setDetailVisible] = useState(false);
  const [currentScript, setCurrentScript] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchScripts();
  }, []);

  const fetchScripts = async () => {
    setLoading(true);
    try {
      const response = await verificationApi.listScripts();
      setScripts(response.data.items || []);
    } catch (error) {
      message.error('获取脚本列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetail = async (record) => {
    try {
      const response = await verificationApi.getScript(record.id);
      setCurrentScript(response.data);
      setDetailVisible(true);
    } catch (error) {
      message.error('获取脚本详情失败');
    }
  };

  const columns = [
    {
      title: '脚本名称',
      dataIndex: 'script_name',
      render: (text, record) => (
        <Space>
          <CodeOutlined />
          <span>{text}</span>
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'script_type',
      width: 100,
      render: (type) => (
        <Tag color={type === 'bash' ? 'blue' : 'green'}>{type}</Tag>
      ),
    },
    {
      title: '版本',
      dataIndex: 'version',
      width: 80,
    },
    {
      title: '适用系统',
      dataIndex: 'applicable_os',
      ellipsis: true,
    },
    {
      title: '超时时间',
      dataIndex: 'timeout_seconds',
      width: 100,
      render: (seconds) => `${seconds}秒`,
    },
    {
      title: '操作',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button 
            type="link" 
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            查看
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card
        title="验证脚本管理"
        extra={
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={() => {
              setCurrentScript(null);
              form.resetFields();
              setModalVisible(true);
            }}
          >
            新建脚本
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={scripts}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* 脚本详情抽屉 */}
      <Drawer
        title="脚本详情"
        width={800}
        open={detailVisible}
        onClose={() => setDetailVisible(false)}
      >
        {currentScript && (
          <>
            <Descriptions bordered column={2} style={{ marginBottom: 24 }}>
              <Descriptions.Item label="脚本名称">{currentScript.script_name}</Descriptions.Item>
              <Descriptions.Item label="脚本类型">
                <Tag color={currentScript.script_type === 'bash' ? 'blue' : 'green'}>
                  {currentScript.script_type}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="版本">{currentScript.version}</Descriptions.Item>
              <Descriptions.Item label="超时时间">{currentScript.timeout_seconds}秒</Descriptions.Item>
              <Descriptions.Item label="适用系统" span={2}>{currentScript.applicable_os}</Descriptions.Item>
              <Descriptions.Item label="描述" span={2}>{currentScript.description}</Descriptions.Item>
            </Descriptions>
            
            <Card title="脚本内容" size="small">
              <pre style={{ 
                background: '#f6f8fa', 
                padding: 16, 
                borderRadius: 6,
                overflow: 'auto',
                maxHeight: 400
              }}>
                <code>{currentScript.content}</code>
              </pre>
            </Card>
          </>
        )}
      </Drawer>
    </div>
  );
}

export default Scripts;
