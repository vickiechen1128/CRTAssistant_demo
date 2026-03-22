/**
 * 工作流进度展示组件
 * 展示整体进度和各工作项状态
 */

import React, { useEffect, useState } from 'react';
import { Card, Progress, Timeline, Statistic, Row, Col, Tag, Alert } from 'antd';
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  CloseCircleOutlined,
  FlagOutlined,
  WarningOutlined
} from '@ant-design/icons';
import useWorkflowStore from '../../../stores/workflowStore';

// 状态图标映射
const statusIconMap = {
  pending: <ClockCircleOutlined />,
  in_progress: <PlayCircleOutlined />,
  pending_review: <PauseCircleOutlined />,
  completed: <CheckCircleOutlined />,
  rejected: <CloseCircleOutlined />
};

// 状态颜色映射
const statusColorMap = {
  pending: 'gray',
  in_progress: 'blue',
  pending_review: 'orange',
  completed: 'green',
  rejected: 'red'
};

// 状态文本映射
const statusTextMap = {
  pending: '未开始',
  in_progress: '进行中',
  pending_review: '待验收',
  completed: '已完成',
  rejected: '已驳回'
};

const WorkflowProgress = ({ instanceId }) => {
  const { progress, fetchProgress, loading } = useWorkflowStore();
  const [refreshInterval, setRefreshInterval] = useState(null);

  useEffect(() => {
    if (instanceId) {
      fetchProgress(instanceId);

      // 设置定时刷新（每30秒）
      const interval = setInterval(() => {
        fetchProgress(instanceId);
      }, 30000);

      setRefreshInterval(interval);

      return () => {
        if (interval) {
          clearInterval(interval);
        }
      };
    }
  }, [instanceId]);

  if (!progress) {
    return <Card loading={loading}>加载中...</Card>;
  }

  const {
    overall_progress,
    status,
    work_items = [],
    critical_path = [],
    blocked_items = [],
    estimated_completion
  } = progress;

  // 统计各状态工作项数量
  const statusCount = work_items.reduce((acc, item) => {
    acc[item.status] = (acc[item.status] || 0) + 1;
    return acc;
  }, {});

  const totalItems = work_items.length;
  const completedItems = statusCount.completed || 0;

  // 格式化预估完成时间
  const formatEstimatedTime = (time) => {
    if (!time) return '计算中...';
    return new Date(time).toLocaleString();
  };

  return (
    <div className="workflow-progress">
      {/* 整体进度 */}
      <Card title="整体进度" className="progress-overview">
        <Row gutter={24} align="middle">
          <Col span={8}>
            <Progress
              type="circle"
              percent={overall_progress}
              width={120}
              strokeColor={{
                '0%': '#108ee9',
                '100%': '#87d068',
              }}
              format={(percent) => (
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{percent}%</div>
                  <div style={{ fontSize: '12px', color: '#999' }}>完成度</div>
                </div>
              )}
            />
          </Col>
          <Col span={16}>
            <Row gutter={16}>
              <Col span={8}>
                <Statistic
                  title="总工作项"
                  value={totalItems}
                  suffix="个"
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="已完成"
                  value={completedItems}
                  suffix={`/ ${totalItems}`}
                  valueStyle={{ color: '#3f8600' }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="预估完成"
                  value={formatEstimatedTime(estimated_completion)}
                  valueStyle={{ fontSize: '14px' }}
                />
              </Col>
            </Row>

            {/* 状态分布 */}
            <div className="status-distribution" style={{ marginTop: 16 }}>
              <Row gutter={[8, 8]}>
                {Object.entries(statusCount).map(([status, count]) => (
                  <Col key={status}>
                    <Tag
                      icon={statusIconMap[status]}
                      color={statusColorMap[status]}
                    >
                      {statusTextMap[status]}: {count}
                    </Tag>
                  </Col>
                ))}
              </Row>
            </div>
          </Col>
        </Row>
      </Card>

      {/* 警告信息 */}
      {blocked_items.length > 0 && (
        <Alert
          message="阻塞提醒"
          description={`有 ${blocked_items.length} 个工作项因前置依赖未完成而阻塞，请优先处理`}
          type="warning"
          showIcon
          icon={<WarningOutlined />}
          style={{ marginTop: 16, marginBottom: 16 }}
        />
      )}

      {/* 工作项时间线 */}
      <Card title="工作项进度" className="work-items-timeline" style={{ marginTop: 16 }}>
        <Timeline mode="left">
          {work_items.map((item, index) => {
            const isCritical = critical_path.includes(item.id);
            const isBlocked = blocked_items.includes(item.id);

            return (
              <Timeline.Item
                key={item.id}
                dot={statusIconMap[item.status]}
                color={statusColorMap[item.status]}
                label={
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: 'bold' }}>{item.name}</div>
                    <div style={{ fontSize: '12px', color: '#999' }}>
                      {item.progress}%
                    </div>
                  </div>
                }
              >
                <div className="timeline-item-content">
                  <div className="item-header">
                    <Tag color={statusColorMap[item.status]}>
                      {statusTextMap[item.status]}
                    </Tag>
                    {isCritical && (
                      <Tag icon={<FlagOutlined />} color="red">
                        关键路径
                      </Tag>
                    )}
                    {isBlocked && (
                      <Tag icon={<WarningOutlined />} color="orange">
                        阻塞
                      </Tag>
                    )}
                  </div>

                  <Progress
                    percent={item.progress}
                    size="small"
                    status={item.status === 'rejected' ? 'exception' : 'active'}
                    strokeColor={item.status === 'completed' ? '#52c41a' : undefined}
                  />

                  {(item.started_at || item.completed_at) && (
                    <div className="item-time" style={{ fontSize: '12px', color: '#999', marginTop: 8 }}>
                      {item.started_at && (
                        <span>开始: {new Date(item.started_at).toLocaleString()}</span>
                      )}
                      {item.completed_at && (
                        <span style={{ marginLeft: 16 }}>
                          完成: {new Date(item.completed_at).toLocaleString()}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </Timeline.Item>
            );
          })}
        </Timeline>
      </Card>

      <style jsx>{`
        .workflow-progress {
          padding: 0;
        }

        .progress-overview {
          margin-bottom: 16px;
        }

        .timeline-item-content {
          padding: 8px 0;
        }

        .item-header {
          margin-bottom: 8px;
        }
      `}</style>
    </div>
  );
};

export default WorkflowProgress;
