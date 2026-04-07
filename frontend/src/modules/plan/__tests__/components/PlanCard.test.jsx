/**
 * PlanCard 组件测试
 */
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import PlanCard from '../../components/PlanCard/PlanCard';

// 模拟计划数据
const mockPlan = {
  id: 'PLAN-20240115-0001',
  data_tag: 'NEW-20240115-001',
  name: '测试计划',
  category: 'new_system',
  priority: 'P1',
  status: 'DRAFT',
  description: '这是一个测试计划的描述',
  planned_start_time: '2024-01-20T00:00:00Z',
  planned_end_time: '2024-02-20T00:00:00Z',
  inventory_ids: ['inv-001', 'inv-002'],
  is_overdue: false,
};

const mockOverduePlan = {
  ...mockPlan,
  is_overdue: true,
};

describe('PlanCard 组件', () => {
  it('应正确渲染计划卡片', () => {
    render(<PlanCard plan={mockPlan} />);

    // 验证计划名称显示
    expect(screen.getByText('测试计划')).toBeDefined();

    // 验证数据标签显示
    expect(screen.getByText('NEW-20240115-001')).toBeDefined();

    // 验证分类标签显示
    expect(screen.getByText('新系统上线')).toBeDefined();

    // 验证优先级标签显示
    expect(screen.getByText('P1 - 高优先级')).toBeDefined();
  });

  it('应显示计划描述', () => {
    render(<PlanCard plan={mockPlan} />);
    expect(screen.getByText('这是一个测试计划的描述')).toBeDefined();
  });

  it('应显示逾期标记', () => {
    render(<PlanCard plan={mockOverduePlan} />);
    expect(screen.getByText('逾期')).toBeDefined();
  });

  it('应显示计划时间', () => {
    render(<PlanCard plan={mockPlan} />);
    expect(screen.getByText(/计划开始:/)).toBeDefined();
    expect(screen.getByText(/计划结束:/)).toBeDefined();
  });

  it('应显示关联台账数量', () => {
    render(<PlanCard plan={mockPlan} />);
    expect(screen.getByText(/关联台账: 2 个/)).toBeDefined();
  });

  it('点击卡片应触发回调', () => {
    const handleClick = vi.fn();
    render(<PlanCard plan={mockPlan} onClick={handleClick} />);

    const card = screen.getByText('测试计划').closest('.ant-card');
    fireEvent.click(card);

    expect(handleClick).toHaveBeenCalledTimes(1);
    expect(handleClick).toHaveBeenCalledWith(mockPlan);
  });

  it('没有描述时不应显示描述区域', () => {
    const planWithoutDesc = { ...mockPlan, description: null };
    const { queryByText } = render(<PlanCard plan={planWithoutDesc} />);
    // 验证没有描述文本
    expect(queryByText('这是一个测试计划的描述')).toBeNull();
  });

  it('没有台账时不应显示台账信息', () => {
    const planWithoutInventory = { ...mockPlan, inventory_ids: [] };
    const { queryByText } = render(<PlanCard plan={planWithoutInventory} />);
    expect(queryByText(/关联台账/)).toBeNull();
  });
});
