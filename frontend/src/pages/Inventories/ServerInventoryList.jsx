/**
 * 应用系统台账列表页
 * 展示所有应用系统台账
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Table, Tag, Button, Space, message } from 'antd';
import { PlusOutlined, EyeOutlined } from '@ant-design/icons';
import { inventoryApi } from '../../api/inventory';

// 台账状态映射
const statusMap = {
  draft: { text: '草稿', color: 'default' },
  filling: { text: '填写中', color: 'processing' },
  submitted: { text: '已提交', color: 'warning' },
  confirmed: { text: '已确认', color: 'success' },
  expired: { text: '已过期', color: 'error' },
};

function ServerInventoryList() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [inventories, setInventories] = useState([]);

  useEffect(() => {
    fetchInventories();
  }, []);

  const fetchInventories = async () => {
    setLoading(true);
    try {
      // 获取所有 server 类型的台账
      const response = await inventoryApi.listByType('server');
      setInventories(response.data.items || []);
    } catch (error) {
      message.error('获取台账列表失败');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: '台账ID',
      dataIndex: 'id',
      width: 100,
    },
    {
      title: '任务编号',
      dataIndex: ['task', 'task_no'],
      width: 150,
    },
    {
      title: '系统名称',
      dataIndex: ['task', 'system_name'],
    },
    {
      title: '服务器数量',
      dataIndex: 'server_count',
      width: 120,
      render: (count) => count || 0,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 120,
      render: (status) => {
        const config = statusMap[status] || { text: status, color: 'default' };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '提交人',
      dataIndex: ['submitter', 'real_name'],
      width: 120,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      width: 180,
    },
    {
      title: '操作',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/inventories/${record.id}`)}
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
        title="应用系统台账"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/admission-tasks')}>
            从任务创建
          </Button>
        }
      >
        <Table
          rowKey="id"
          columns={columns}
          dataSource={inventories}
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
}

export default ServerInventoryList;
