/**
 * PlanStatusBadge 组件
 * 显示计划状态标签
 */
import React from 'react';
import { Tag } from 'antd';
import { statusOptions } from '../../api/types';

/**
 * 获取状态配置
 * @param {string} status - 状态值
 * @returns {Object} - 状态配置
 */
const getStatusConfig = (status) => {
  const config = statusOptions.find((opt) => opt.value === status);
  return (
    config || {
      label: status,
      color: 'default',
    }
  );
};

/**
 * PlanStatusBadge 组件
 * @param {Object} props
 * @param {string} props.status - 状态值
 * @param {boolean} props.showDot - 是否显示圆点
 */
const PlanStatusBadge = ({ status, showDot = true }) => {
  const config = getStatusConfig(status);

  return (
    <Tag color={config.color}>
      {showDot && (
        <span
          style={{
            display: 'inline-block',
            width: 6,
            height: 6,
            borderRadius: '50%',
            backgroundColor: 'currentColor',
            marginRight: 6,
            opacity: 0.8,
          }}
        />
      )}
      {config.label}
    </Tag>
  );
};

export default PlanStatusBadge;
