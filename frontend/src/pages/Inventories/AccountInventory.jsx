/**
 * 系统账户台账详情页
 * 管理系统账户信息：账户名、权限、持有人、有效期等
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Form, Input, Button, Table, Space, message, Row, Col, Select, DatePicker } from 'antd';
import { ArrowLeftOutlined, PlusOutlined, DeleteOutlined, SaveOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { inventoryApi } from '../../api/inventory';
import dayjs from 'dayjs';

const { Option } = Select;

// 权限级别选项
const permissionOptions = [
  { value: 'admin', label: '管理员' },
  { value: 'operator', label: '运维人员' },
  { value: 'developer', label: '开发人员' },
  { value: 'readonly', label: '只读' },
];

function AccountInventory() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [inventory, setInventory] = useState(null);
  const [accounts, setAccounts] = useState([]);

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
      // 转换日期格式
      const accountsWithDate = (response.data.accounts || []).map(acc => ({
        ...acc,
        valid_until: acc.valid_until ? dayjs(acc.valid_until) : null,
      }));
      setAccounts(accountsWithDate);
    } catch (error) {
      message.error('获取台账详情失败');
    } finally {
      setLoading(false);
    }
  };

  // 添加账户行
  const handleAddAccount = () => {
    const newAccount = {
      id: `temp_${Date.now()}`,
      system_name: '',
      server_hostname: '',
      account_name: '',
      permission_level: 'readonly',
      holder_name: '',
      valid_until: null,
      contact_info: '',
      isNew: true,
    };
    setAccounts([...accounts, newAccount]);
  };

  // 删除账户行
  const handleDeleteAccount = (record) => {
    setAccounts(accounts.filter(a => a.id !== record.id));
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
      title: '系统名称',
      dataIndex: 'system_name',
      width: 160,
      render: (text, record) => (
        <Input
          value={text}
          onChange={(e) => {
            const newAccounts = accounts.map(a =>
              a.id === record.id ? { ...a, system_name: e.target.value } : a
            );
            setAccounts(newAccounts);
          }}
          placeholder="订单管理系统"
        />
      ),
    },
    {
      title: '服务器',
      dataIndex: 'server_hostname',
      width: 160,
      render: (text, record) => (
        <Input
          value={text}
          onChange={(e) => {
            const newAccounts = accounts.map(a =>
              a.id === record.id ? { ...a, server_hostname: e.target.value } : a
            );
            setAccounts(newAccounts);
          }}
          placeholder="order-app-01"
        />
      ),
    },
    {
      title: '账户名',
      dataIndex: 'account_name',
      width: 140,
      render: (text, record) => (
        <Input
          value={text}
          onChange={(e) => {
            const newAccounts = accounts.map(a =>
              a.id === record.id ? { ...a, account_name: e.target.value } : a
            );
            setAccounts(newAccounts);
          }}
          placeholder="deployuser"
        />
      ),
    },
    {
      title: '权限级别',
      dataIndex: 'permission_level',
      width: 140,
      render: (text, record) => (
        <Select
          value={text}
          onChange={(value) => {
            const newAccounts = accounts.map(a =>
              a.id === record.id ? { ...a, permission_level: value } : a
            );
            setAccounts(newAccounts);
          }}
          style={{ width: '100%' }}
        >
          {permissionOptions.map(opt => (
            <Option key={opt.value} value={opt.value}>{opt.label}</Option>
          ))}
        </Select>
      ),
    },
    {
      title: '持有人',
      dataIndex: 'holder_name',
      width: 120,
      render: (text, record) => (
        <Input
          value={text}
          onChange={(e) => {
            const newAccounts = accounts.map(a =>
              a.id === record.id ? { ...a, holder_name: e.target.value } : a
            );
            setAccounts(newAccounts);
          }}
          placeholder="张三"
        />
      ),
    },
    {
      title: '有效期至',
      dataIndex: 'valid_until',
      width: 160,
      render: (date, record) => (
        <DatePicker
          value={date}
          onChange={(value) => {
            const newAccounts = accounts.map(a =>
              a.id === record.id ? { ...a, valid_until: value } : a
            );
            setAccounts(newAccounts);
          }}
          style={{ width: '100%' }}
          placeholder="选择日期"
        />
      ),
    },
    {
      title: '联系方式',
      dataIndex: 'contact_info',
      width: 160,
      render: (text, record) => (
        <Input
          value={text}
          onChange={(e) => {
            const newAccounts = accounts.map(a =>
              a.id === record.id ? { ...a, contact_info: e.target.value } : a
            );
            setAccounts(newAccounts);
          }}
          placeholder="手机号或邮箱"
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
          onClick={() => handleDeleteAccount(record)}
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
            {isNew ? '新建系统账户台账' : '系统账户台账详情'}
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
          <Button type="dashed" icon={<PlusOutlined />} onClick={handleAddAccount}>
            添加账户
          </Button>
        </div>

        <Table
          rowKey="id"
          columns={columns}
          dataSource={accounts}
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

export default AccountInventory;
