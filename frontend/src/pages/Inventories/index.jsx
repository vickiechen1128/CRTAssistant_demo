/**
 * 台账管理主页面
 * 展示任务的三类台账：应用系统、云服务、系统账户
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Tabs, Button, Table, Tag, Space, message } from 'antd';
import { ArrowLeftOutlined, PlusOutlined, EyeOutlined } from '@ant-design/icons';
import { inventoryApi } from '../../api/inventory';

const { TabPane } = Tabs;

// 台账类型映射
const inventoryTypeMap = {
  server: { text: '应用系统台账', color: 'blue' },
  cloud_resource: { text: '云服务开通台账', color: 'green' },
  account: { text: '系统账户台账', color: 'orange' },
};

// 台账状态映射
const statusMap = {
  draft: { text: '草稿', color: 'default' },
  filling: { text: '填写中', color: 'processing' },
  submitted: { text: '已提交', color: 'warning' },
  confirmed: { text: '已确认', color: 'success' },
  expired: { text: '已过期', color: 'error' },
};

function Inventories() {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [inventories, setInventories] = useState([]);
  const [activeTab, setActiveTab] = useState('server');

  useEffect(() => {
    if (taskId) {
      fetchInventories();
    }
  }, [taskId]);

  const fetchInventories = async () => {
    setLoading(true);
    try {
      const response = await inventoryApi.list(taskId);
      setInventories(response.data.items || []);
    } catch (error) {
      message.error('获取台账列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取指定类型的台账
  const getInventoryByType = (type) => {
    return inventories.filter(inv => inv.inventory_type === type);
  };

  // 表格列定义
  const columns = [
    {
      title: '台账类型',
      dataIndex: 'inventory_type',
      width: 150,
      render: (type) => {
        const config = inventoryTypeMap[type] || { text: type, color: 'default' };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
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
            icon={<EyeOutlined />}
            onClick={() => navigate(`/inventories/${record.id}`)}
          >
            查看
          </Button>
        </Space>
      ),
    },
  ];

  // 渲染台账列表
  const renderInventoryList = (type) => {
    const typeInventories = getInventoryByType(type);
    
    return (
      <div>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
          <span>
            共 <strong>{typeInventories.length}</strong> 条记录
          </span>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate(`/inventories/${taskId}/${type}/create`)}
          >
            新建台账
          </Button>
        </div>
        <Table
          rowKey="id"
          columns={columns}
          dataSource={typeInventories}
          loading={loading}
          pagination={false}
        />
      </div>
    );
  };

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', alignItems: 'center', gap: 16 }}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate(`/admission-tasks/${taskId}`)}
        >
          返回任务详情
        </Button>
        <h2 style={{ margin: 0 }}>台账管理</h2>
      </div>

      <Card>
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="应用系统台账" key="server">
            {renderInventoryList('server')}
          </TabPane>
          <TabPane tab="云服务开通台账" key="cloud_resource">
            {renderInventoryList('cloud_resource')}
          </TabPane>
          <TabPane tab="系统账户台账" key="account">
            {renderInventoryList('account')}
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
}

export default Inventories;
