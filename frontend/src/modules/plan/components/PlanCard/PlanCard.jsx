/**
 * PlanCard 组件
 * 计划卡片展示
 */
import React from 'react';
import { Card, Tag, Space, Typography, Tooltip } from 'antd';
import {
  CalendarOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import PlanStatusBadge from '../PlanStatusBadge';
import { categoryOptions, priorityOptions } from '../../api/types';

const { Text, Paragraph } = Typography;

/**
 * 获取分类配置
 */
const getCategoryConfig = (category) => {
  return categoryOptions.find((opt) => opt.value === category) || { label: category };
};

/**
 * 获取优先级配置
 */
const getPriorityConfig = (priority) => {
  return priorityOptions.find((opt) => opt.value === priority) || { label: priority, color: 'default' };
};

/**
 * 格式化日期
 */
const formatDate = (dateString) => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN');
};

/**
 * PlanCard 组件
 * @param {Object} props
 * @param {Object} props.plan - 计划数据
 * @param {Function} props.onClick - 点击回调
 */
const PlanCard = ({ plan, onClick }) => {
  const categoryConfig = getCategoryConfig(plan.category);
  const priorityConfig = getPriorityConfig(plan.priority);

  return (
    <Card
      hoverable
      onClick={() => onClick?.(plan)}
      style={{ marginBottom: 16 }}
      title={
        <Space>
          <Text strong>{plan.name}</Text>
          <Tag color="blue">{plan.data_tag}</Tag>
        </Space>
      }
      extra={<PlanStatusBadge status={plan.status} />}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="small">
        {/* 分类和优先级 */}
        <Space>
          <Tag>{categoryConfig.label}</Tag>
          <Tag color={priorityConfig.color}>{priorityConfig.label}</Tag>
          {plan.is_overdue && (
            <Tooltip title="已逾期">
              <Tag icon={<ExclamationCircleOutlined />} color="error">
                逾期
              </Tag>
            </Tooltip>
          )}
        </Space>

        {/* 描述 */}
        {plan.description && (
          <Paragraph
            ellipsis={{ rows: 2 }}
            style={{ marginBottom: 0, color: '#666' }}
          >
            {plan.description}
          </Paragraph>
        )}

        {/* 时间信息 */}
        <Space split={<Text type="secondary">|</Text>}>
          <Text type="secondary">
            <CalendarOutlined style={{ marginRight: 4 }} />
            计划开始: {formatDate(plan.planned_start_time)}
          </Text>
          {plan.planned_end_time && (
            <Text type="secondary">
              <ClockCircleOutlined style={{ marginRight: 4 }} />
              计划结束: {formatDate(plan.planned_end_time)}
            </Text>
          )}
        </Space>

        {/* 关联台账 */}
        {plan.inventory_ids && plan.inventory_ids.length > 0 && (
          <Text type="secondary">
            关联台账: {plan.inventory_ids.length} 个
          </Text>
        )}
      </Space>
    </Card>
  );
};

export default PlanCard;
