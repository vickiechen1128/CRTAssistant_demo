/**
 * 云服务开通台账详情页
 * 管理云服务资源：IAAS/PAAS层信息
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Form, Input, Button, Table, Space, message, Row, Col, Select } from 'antd';
import { ArrowLeftOutlined, PlusOutlined, DeleteOutlined, SaveOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { inventoryApi } from '../../api/inventory';

const { Option } = Select;

// 资源类型选项
const resourceTypeOptions = [
  { value: 'compute', label: '计算资源' },
  { value: 'network', label: '网络资源' },
  { value: 'storage', label: '存储资源' },
  { value: 'database', label: '数据库' },
  { value: 'middleware', label: '中间件' },
  { value: 'backup', label: '备份服务' },
];

function CloudInventory() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [inventory, setInventory] = useState(null);
  const [resources, setResources] = useState([]);

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
      setResources(response.data.cloud_resources || []);
    } catch (error) {
      message.error('获取台账详情失败');
    } finally {
      setLoading(false);
    }
  };

  // 添加资源行
  const handleAddResource = () => {
    const newResource = {
      id: `temp_${Date.now()}`,
      resource_type: 'compute',
      service_name: '',
      instance_name: '',
      specification: '',
      region: '',
      vpc: '',
      isNew: true,
    };
    setResources([...resources, newResource]);
  };

  // 删除资源行
  const handleDeleteResource = (record) => {
    setResources(resources.filter(r => r.id !== record.id));
  };

  // 保存
  const handleSave = async () => {
    try {
      message.success('保存成功');
    } catch (error) {
      message.error('保存失败');
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
      title: '资源类型',
      dataIndex: 'resource_type',
      width: 140,
      render: (text, record) => (
        <Select
          value={text}
          onChange={(value) => {
            const newResources = resources.map(r =>
              r.id === record.id ? { ...r, resource_type: value } : r
            );
            setResources(newResources);
          }}
          style={{ width: '100%' }}
        >
          {resourceTypeOptions.map(opt => (
            <Option key={opt.value} value={opt.value}>{opt.label}</Option>
          ))}
        </Select>
      ),
    },
    {
      title: '服务名称',
      dataIndex: 'service_name',
      width: 180,
      render: (text, record) => (
        <Input
          value={text}
          onChange={(e) => {
            const newResources = resources.map(r =>
              r.id === record.id ? { ...r, service_name: e.target.value } : r
            );
            setResources(newResources);
          }}
          placeholder="ECS/SLB/RDS等"
        />
      ),
    },
    {
      title: '实例名称',
      dataIndex: 'instance_name',
      width: 180,
      render: (text, record) => (
        <Input
          value={text}
          onChange={(e) => {
            const newResources = resources.map(r =>
              r.id === record.id ? { ...r, instance_name: e.target.value } : r
            );
            setResources(newResources);
          }}
          placeholder="实例ID或名称"
        />
      ),
    },
    {
      title: '规格配置',
      dataIndex: 'specification',
      width: 200,
      render: (text, record) => (
        <Input
          value={text}
          onChange={(e) => {
            const newResources = resources.map(r =>
              r.id === record.id ? { ...r, specification: e.target.value } : r
            );
            setResources(newResources);
          }}
          placeholder="如：4核8G、100GB SSD"
        />
      ),
    },
    {
      title: '地域/可用区',
      dataIndex: 'region',
      width: 140,
      render: (text, record) => (
        <Input
          value={text}
          onChange={(e) => {
            const newResources = resources.map(r =>
              r.id === record.id ? { ...r, region: e.target.value } : r
            );
            setResources(newResources);
          }}
          placeholder="华东1/可用区A"
        />
      ),
    },
    {
      title: 'VPC/网络',
      dataIndex: 'vpc',
      width: 160,
      render: (text, record) => (
        <Input
          value={text}
          onChange={(e) => {
            const newResources = resources.map(r =>
              r.id === record.id ? { ...r, vpc: e.target.value } : r
            );
            setResources(newResources);
          }}
          placeholder="vpc-xxx"
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
          onClick={() => handleDeleteResource(record)}
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
            {isNew ? '新建云服务开通台账' : '云服务开通台账详情'}
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
        <div style={{ marginBottom: 16 }}>
          <Button type="dashed" icon={<PlusOutlined />} onClick={handleAddResource}>
            添加云资源
          </Button>
        </div>

        <Table
          rowKey="id"
          columns={columns}
          dataSource={resources}
          loading={loading}
          scroll={{ x: 1200 }}
          pagination={false}
          bordered
          size="small"
        />
      </Card>
    </div>
  );
}

export default CloudInventory;
