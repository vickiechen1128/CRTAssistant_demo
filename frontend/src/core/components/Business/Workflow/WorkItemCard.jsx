/**
 * 工作项卡片组件
 * 展示单个工作项的信息和状态
 */

import React from 'react';
import { Card, Tag, Progress, Button, Space, Tooltip } from 'antd';
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  CloseCircleOutlined,
  UserOutlined,
  FieldTimeOutlined
} from '@ant-design/icons';

// 工作项状态映射
const statusMap = {
  pending: { color: 'default', text: '未开始', icon: <ClockCircleOutlined /> },
  in_progress: { color: 'processing', text: '进行中', icon: <PlayCircleOutlined /> },
  pending_review: { color: 'warning', text: '待验收', icon: <PauseCircleOutlined /> },
  completed: { color: 'success', text: '已完成', icon: <CheckCircleOutlined /> },
  rejected: { color: 'error', text: '已驳回', icon: <CloseCircleOutlined /> }
};

// 工作项类型映射
const typeMap = {
  resource_delivery: { color: 'blue', text: '资源交付' },
  inventory: { color: 'green', text: '台账' },
  permission_handover: { color: 'orange', text: '权限移交' },
  security_baseline: { color: 'red', text: '安全基线' },
  monitoring: { color: 'purple', text: '监控告警' },
  custom: { color: 'default', text: '自定义' }
};

const WorkItemCard = ({
  workItem,
  onExecute,
  onVerify,
  onView,
  showActions = true,
  isBlocked = false
}) => {
  const {
    id,
    name,
    description,
    work_item_type,
    status,
    progress = 0,
    assignee,
    estimated_duration,
    actual_duration,
    started_at,
    completed_at
  } = workItem;

  const statusInfo = statusMap[status] || statusMap.pending;
  const typeInfo = typeMap[work_item_type] || typeMap.custom;

  // 格式化时长
  const formatDuration = (minutes) => {
    if (!minutes) return '-';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}小时${mins > 0 ? `${mins}分钟` : ''}`;
    }
    return `${mins}分钟`;
  };

  return (
    <Card
      className={`work-item-card ${isBlocked ? 'blocked' : ''}`}
      size="small"
      title={
        <Space>
          <span className="work-item-name">{name}</span>
          <Tag color={typeInfo.color}>{typeInfo.text}</Tag>
          {isBlocked && <Tag color="error">阻塞</Tag>}
        </Space>
      }
      extra={
        showActions && (
          <Space>
            {status === 'pending' && !isBlocked && (
              <Button
                type="primary"
                size="small"
                icon={<PlayCircleOutlined />}
                onClick={() => onExecute?.(workItem)}
              >
                开始
              </Button>
            )}
            {status === 'in_progress' && (
              <Button
                type="primary"
                size="small"
                icon={<CheckCircleOutlined />}
                onClick={() => onVerify?.(workItem)}
              >
                提交验收
              </Button>
            )}
            {status === 'pending_review' && (
              <Button
                type="primary"
                size="small"
                icon={<CheckCircleOutlined />}
                onClick={() => onVerify?.(workItem)}
              >
                验收
              </Button>
            )}
            <Button
              size="small"
              onClick={() => onView?.(workItem)}
            >
              详情
            </Button>
          </Space>
        )
      }
    >
      <div className="work-item-content">
        {/* 描述 */}
        {description && (
          <p className="work-item-description">{description}</p>
        )}

        {/* 进度条 */}
        <div className="work-item-progress">
          <Progress
            percent={progress}
            size="small"
            status={status === 'rejected' ? 'exception' : 'active'}
            strokeColor={status === 'completed' ? '#52c41a' : undefined}
          />
        </div>

        {/* 状态和信息 */}
        <div className="work-item-footer">
          <Space wrap>
            <Tag icon={statusInfo.icon} color={statusInfo.color}>
              {statusInfo.text}
            </Tag>

            {assignee && (
              <Tooltip title="执行人">
                <Tag icon={<UserOutlined />}>
                  {assignee.real_name || '未分配'}
                </Tag>
              </Tooltip>
            )}

            {estimated_duration && (
              <Tooltip title="预估时长">
                <Tag icon={<FieldTimeOutlined />}>
                  预估: {formatDuration(estimated_duration)}
                </Tag>
              </Tooltip>
            )}

            {actual_duration && (
              <Tooltip title="实际耗时">
                <Tag>
                  实际: {formatDuration(actual_duration)}
                </Tag>
              </Tooltip>
            )}

            {started_at && (
              <span className="time-info">
                开始: {new Date(started_at).toLocaleString()}
              </span>
            )}

            {completed_at && (
              <span className="time-info">
                完成: {new Date(completed_at).toLocaleString()}
              </span>
            )}
          </Space>
        </div>
      </div>

      <style jsx>{`
        .work-item-card {
          margin-bottom: 16px;
          transition: all 0.3s;
        }

        .work-item-card.blocked {
          border-color: #ff4d4f;
          background-color: #fff1f0;
        }

        .work-item-card:hover {
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
        }

        .work-item-name {
          font-weight: 500;
          font-size: 14px;
        }

        .work-item-description {
          color: rgba(0, 0, 0, 0.45);
          margin-bottom: 12px;
          font-size: 13px;
        }

        .work-item-progress {
          margin-bottom: 12px;
        }

        .work-item-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 8px;
        }

        .time-info {
          font-size: 12px;
          color: rgba(0, 0, 0, 0.45);
        }
      `}</style>
    </Card>
  );
};

export default WorkItemCard;
