/**
 * 应用系统台账详情页
 * 管理服务器信息：IP、主机名、配置等
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Form, Input, Button, Table, Space, message, Row, Col, Select, InputNumber } from 'antd';
import { ArrowLeftOutlined, PlusOutlined, DeleteOutlined, SaveOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { inventoryApi } from '../../api/inventory';

const { Option } = Select;

// 环境选项
const environmentOptions = [
  { value: 'production', label: '生产环境' },
  { value: 'staging', label: '预发环境' },
  { value: 'test', label: '测试环境' },
];

function ServerInventory() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [inventory, setInventory] = useState(null);
  const [servers, setServers] = useState([]);
  const [editingKey, setEditingKey] = useState('');

  useEffect(() => {
    if (id && id !== 'create') {
      fetchInventory();
    }
  }, [id]);

  const fetchInventory = async () => {
    setLoading(true);
    try {
      const response = await inventoryApi.get(id);
      setInventory(response.data);
      setServers(response.data.servers || []);
    } catch (error) {
      message.error('获取台账详情失败');
    } finally {
      setLoading(false);
    }
  };

  // 添加服务器行
  const handleAddServer = () => {
    const newServer = {
      id: `temp_${Date.now()}`,
      ip_address: '',
      hostname: '',
      os_type: '',
      cpu_cores: null,
      memory_gb: null,
      disk_gb: null,
      purpose: '',
      system_belong: '',
      environment: 'production',
      responsible_person: '',
      isNew: true,
    };
    setServers([...servers, newServer]);
    setEditingKey(newServer.id);
  };

  // 删除服务器行
  const handleDeleteServer = (record) => {
    setServers(servers.filter(s => s.id !== record.id));
  };

  // 保存服务器信息
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      // TODO: 调用API保存数据
      message.success('保存成功');
      setEditingKey('');
    } catch (error) {
      console.error('保存失败:', error);
    }
  };

  // 提交台账
  const handleSubmit = async () => {
    try {
      await inventoryApi.submit(id);
      message.success('提交成功');
      fetchInventory();
    } catch (error) {
      message.error('提交失败');
    }
  };

  // 确认台账
  const handleConfirm = async () => {
    try {
      await inventoryApi.confirm(id);
      message.success('确认成功');
      fetchInventory();
    } catch (error) {
      message.error('确认失败');
    }
  };

  // 表格列定义
  const columns = [
    {
      title: 'IP地址',
      dataIndex: 'ip_address',
      width: 140,
      render: (text, record) => (
        <Input
          value={text}
          onChange={(e) => {
            const newServers = servers.map(s =>
              s.id === record.id ? { ...s, ip_address: e.target.value } : s
            );
            setServers(newServers);
          }}
          placeholder="192.168.1.1"
        />
      ),
    },
    {
      title: '主机名',
      dataIndex: 'hostname',
      width: 160,
      render: (text, record) => (
        <Input
          value={text}
          onChange={(e) => {
            const newServers = servers.map(s =>
              s.id === record.id ? { ...s, hostname: e.target.value } : s
            );
            setServers(newServers);
          }}
          placeholder="order-app-01"
        />
      ),
    },
    {
      title: '操作系统',
      dataIndex: 'os_type',
      width: 140,
      render: (text, record) => (
        <Input
          value={text}
          onChange={(e) => {
            const newServers = servers.map(s =>
              s.id === record.id ? { ...s, os_type: e.target.value } : s
            );
            setServers(newServers);
          }}
          placeholder="CentOS 7.9"
        />
      ),
    },
    {
      title: '配置',
      children: [
        {
          title: 'CPU(核)',
          dataIndex: 'cpu_cores',
          width: 80,
          render: (text, record) => (
            <InputNumber
              value={text}
              onChange={(value) => {
                const newServers = servers.map(s =>
                  s.id === record.id ? { ...s, cpu_cores: value } : s
                );
                setServers(newServers);
              }}
              min={1}
              style={{ width: '100%' }}
            />
          ),
        },
        {
          title: '内存(GB)',
          dataIndex: 'memory_gb',
          width: 80,
          render: (text, record) => (
            <InputNumber
              value={text}
              onChange={(value) => {
                const newServers = servers.map(s =>
                  s.id === record.id ? { ...s, memory_gb: value } : s
                );
                setServers(newServers);
              }}
              min={1}
              style={{ width: '100%' }}
            />
          ),
        },
        {
          title: '磁盘(GB)',
          dataIndex: 'disk_gb',
          width: 80,
          render: (text, record) => (
            <InputNumber
              value={text}
              onChange={(value) => {
                const newServers = servers.map(s =>
                  s.id === record.id ? { ...s, disk_gb: value } : s
                );
                setServers(newServers);
              }}
              min={1}
              style={{ width: '100%' }}
            />
          ),
        },
      ],
    },
    {
      title: '用途',
      dataIndex: 'purpose',
      width: 180,
      render: (text, record) => (
        <Input
          value={text}
          onChange={(e) => {
            const newServers = servers.map(s =>
              s.id === record.id ? { ...s, purpose: e.target.value } : s
            );
            setServers(newServers);
          }}
          placeholder="订单服务应用服务器"
        />
      ),
    },
    {
      title: '环境',
      dataIndex: 'environment',
      width: 120,
      render: (text, record) => (
        <Select
          value={text}
          onChange={(value) => {
            const newServers = servers.map(s =>
              s.id === record.id ? { ...s, environment: value } : s
            );
            setServers(newServers);
          }}
          style={{ width: '100%' }}
        >
          {environmentOptions.map(opt => (
            <Option key={opt.value} value={opt.value}>{opt.label}</Option>
          ))}
        </Select>
      ),
    },
    {
      title: '责任人',
      dataIndex: 'responsible_person',
      width: 120,
      render: (text, record) => (
        <Input
          value={text}
          onChange={(e) => {
            const newServers = servers.map(s =>
              s.id === record.id ? { ...s, responsible_person: e.target.value } : s
            );
            setServers(newServers);
          }}
          placeholder="张三"
        />
      ),
    },
    {
      title: '操作',
      width: 80,
      fixed: 'right',
      render: (_, record) => (
        <Button
          type="text"
          danger
          icon={<DeleteOutlined />}
          onClick={() => handleDeleteServer(record)}
        />
      ),
    },
  ];

  const isNew = id === 'create';

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate(-1)}
          >
            返回
          </Button>
          <h2 style={{ margin: 0 }}>
            {isNew ? '新建应用系统台账' : '应用系统台账详情'}
          </h2>
        </div>
        <Space>
          {!isNew && inventory?.status === 'draft' && (
            <Button type="primary" icon={<CheckCircleOutlined />} onClick={handleSubmit}>
              提交审核
            </Button>
          )}
          {!isNew && inventory?.status === 'submitted' && (
            <Button type="primary" icon={<CheckCircleOutlined />} onClick={handleConfirm}>
              确认台账
            </Button>
          )}
          <Button type="primary" icon={<SaveOutlined />} onClick={handleSave}>
            保存
          </Button>
        </Space>
      </div>

      <Card>
        <Form form={form} layout="vertical">
          <Row gutter={24}>
            <Col span={8}>
              <Form.Item label="所属系统" name="system_belong">
                <Input placeholder="订单管理系统" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item label="备注" name="remark">
                <Input.TextArea rows={1} placeholder="可选" />
              </Form.Item>
            </Col>
          </Row>
        </Form>

        <div style={{ marginBottom: 16 }}>
          <Button type="dashed" icon={<PlusOutlined />} onClick={handleAddServer}>
            添加服务器
          </Button>
        </div>

        <Table
          rowKey="id"
          columns={columns}
          dataSource={servers}
          loading={loading}
          scroll={{ x: 1400 }}
          pagination={false}
          bordered
          size="small"
        />
      </Card>
    </div>
  );
}

export default ServerInventory;
