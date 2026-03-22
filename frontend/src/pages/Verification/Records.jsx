/**
 * 验证记录页面
 */

import React, { useEffect, useState } from 'react';
import { Card, Table, Tag, Space, Button, Drawer, Descriptions, Timeline, message } from 'antd';
import { EyeOutlined, CheckCircleOutlined, CloseCircleOutlined, ClockCircleOutlined, LoadingOutlined } from '@ant-design/icons';
import { verificationApi } from '../../api/verification';

const statusMap = {
  pending: { text: '等待中', color: 'default', icon: <ClockCircleOutlined /> },
  running: { text: '执行中', color: 'processing', icon: <LoadingOutlined /> },
  success: { text: '成功', color: 'success', icon: <CheckCircleOutlined /> },
  failed: { text: '失败', color: 'error', icon: <CloseCircleOutlined /> },
  timeout: { text: '超时', color: 'warning', icon: <ClockCircleOutlined /> },
};

function Records() {
  const [loading, setLoading] = useState(false);
  const [records, setRecords] = useState([]);
  const [detailVisible, setDetailVisible] = useState(false);
  const [currentRecord, setCurrentRecord] = useState(null);

  useEffect(() => {
    fetchRecords();
  }, []);

  const fetchRecords = async () => {
    setLoading(true);
    try {
      // 这里需要一个任务ID，暂时获取所有记录
      const response = await verificationApi.listRecords({ limit: 100 });
      setRecords(response.data.items || []);
    } catch (error) {
      message.error('获取验证记录失败');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetail = async (record) => {
    try {
      const response = await verificationApi.getResult(record.execution_id);
      setCurrentRecord(response.data);
      setDetailVisible(true);
    } catch (error) {
      message.error('获取记录详情失败');
    }
  };

  const columns = [
    {
      title: '执行ID',
      dataIndex: 'execution_id',
      width: 200,
      ellipsis: true,
    },
    {
      title: '脚本名称',
      dataIndex: 'script_name',
    },
    {
      title: '目标服务器',
      dataIndex: 'target_server',
    },
    {
      title: '执行人',
      dataIndex: ['executor', 'real_name'],
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (status) => {
        const config = statusMap[status] || { text: status, color: 'default' };
        return <Tag color={config.color} icon={config.icon}>{config.text}</Tag>;
      },
    },
    {
      title: '执行时长',
      dataIndex: 'duration_seconds',
      width: 100,
      render: (seconds) => seconds ? `${seconds}秒` : '-',
    },
    {
      title: '开始时间',
      dataIndex: 'started_at',
      width: 180,
      render: (time) => time ? new Date(time).toLocaleString() : '-',
    },
    {
      title: '操作',
      width: 100,
      render: (_, record) => (
        <Button 
          type="link" 
          icon={<EyeOutlined />}
          onClick={() => handleViewDetail(record)}
        >
          查看
        </Button>
      ),
    },
  ];

  return (
    <div>
      <Card title="验证执行记录">
        <Table
          columns={columns}
          dataSource={records}
          rowKey="execution_id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* 记录详情抽屉 */}
      <Drawer
        title="执行详情"
        width={900}
        open={detailVisible}
        onClose={() => setDetailVisible(false)}
      >
        {currentRecord && (
          <>
            <Descriptions bordered column={2} style={{ marginBottom: 24 }}>
              <Descriptions.Item label="执行ID" span={2}>{currentRecord.execution_id}</Descriptions.Item>
              <Descriptions.Item label="目标服务器">{currentRecord.target_server}</Descriptions.Item>
              <Descriptions.Item label="执行人">
                {currentRecord.executor?.real_name}
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                <Tag color={statusMap[currentRecord.status]?.color}>
                  {statusMap[currentRecord.status]?.text}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="执行时长">
                {currentRecord.duration_seconds ? `${currentRecord.duration_seconds}秒` : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="开始时间">
                {currentRecord.started_at ? new Date(currentRecord.started_at).toLocaleString() : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="完成时间">
                {currentRecord.completed_at ? new Date(currentRecord.completed_at).toLocaleString() : '-'}
              </Descriptions.Item>
            </Descriptions>

            {/* 结果摘要 */}
            {currentRecord.result_summary && (
              <Card title="结果摘要" size="small" style={{ marginBottom: 24 }}>
                <Space size="large">
                  <span>总计: <strong>{currentRecord.result_summary.total}</strong></span>
                  <span style={{ color: '#52c41a' }}>
                    通过: <strong>{currentRecord.result_summary.passed}</strong>
                  </span>
                  <span style={{ color: '#f5222d' }}>
                    失败: <strong>{currentRecord.result_summary.failed}</strong>
                  </span>
                  <span style={{ color: '#faad14' }}>
                    警告: <strong>{currentRecord.result_summary.warning || 0}</strong>
                  </span>
                </Space>
              </Card>
            )}

            {/* 详细结果 */}
            {currentRecord.result_detail && currentRecord.result_detail.length > 0 && (
              <Card title="详细结果" size="small" style={{ marginBottom: 24 }}>
                <Timeline>
                  {currentRecord.result_detail.map((item, index) => (
                    <Timeline.Item
                      key={index}
                      color={item.status === 'passed' ? 'green' : item.status === 'failed' ? 'red' : 'orange'}
                    >
                      <div>
                        <strong>{item.check_item}</strong>
                        <Tag 
                          color={item.status === 'passed' ? 'success' : item.status === 'failed' ? 'error' : 'warning'}
                          style={{ marginLeft: 8 }}
                        >
                          {item.status === 'passed' ? '通过' : item.status === 'failed' ? '失败' : '警告'}
                        </Tag>
                      </div>
                      <div style={{ color: '#666', fontSize: 12, marginTop: 4 }}>
                        期望: {item.expected}
                      </div>
                      <div style={{ color: '#666', fontSize: 12 }}>
                        实际: {item.actual}
                      </div>
                      {item.suggestion && (
                        <div style={{ color: '#1890ff', fontSize: 12, marginTop: 4 }}>
                          建议: {item.suggestion}
                        </div>
                      )}
                    </Timeline.Item>
                  ))}
                </Timeline>
              </Card>
            )}

            {/* 输出日志 */}
            {currentRecord.output_log && (
              <Card title="输出日志" size="small">
                <pre style={{ 
                  background: '#f6f8fa', 
                  padding: 16, 
                  borderRadius: 6,
                  overflow: 'auto',
                  maxHeight: 300,
                  fontSize: 12
                }}>
                  <code>{currentRecord.output_log}</code>
                </pre>
              </Card>
            )}
          </>
        )}
      </Drawer>
    </div>
  );
}

export default Records;
