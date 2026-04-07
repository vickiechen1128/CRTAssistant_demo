/**
 * PlanEditView 组件
 * 编辑计划页面 - 使用多步骤表单
 */
import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, message, Spin, Alert, Space, Typography } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { usePlanStore } from '../../store';
import PlanStepsForm from '../../components/PlanStepsForm';
import { PlanStatus } from '../../api/types';

const { Title } = Typography;

/**
 * PlanEditView 组件
 */
const PlanEditView = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const {
    currentPlan,
    currentPlanDetail,
    loading,
    fetchPlanDetail,
    clearCurrentPlan,
    resetCreationStep,
  } = usePlanStore();

  // 加载计划详情
  useEffect(() => {
    // 重置创建步骤
    resetCreationStep();
    fetchPlanDetail(id);

    return () => {
      clearCurrentPlan();
    };
  }, [id, resetCreationStep, fetchPlanDetail, clearCurrentPlan]);

  // 检查是否可编辑
  const isEditable = currentPlan?.status === PlanStatus.DRAFT;

  // 准备编辑数据
  const prepareEditData = () => {
    if (!currentPlan) return null;

    return {
      name: currentPlan.name,
      category: currentPlan.category,
      priority: currentPlan.priority,
      description: currentPlan.description,
      planned_start_time: currentPlan.planned_start_time,
      planned_end_time: currentPlan.planned_end_time,
      approval_files: currentPlanDetail?.approval_files || [],
      affected_modules: currentPlanDetail?.affected_modules || [],
      related_inventory_ids: currentPlanDetail?.related_inventory_ids || currentPlan.inventory_ids || [],
    };
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!isEditable) {
    return (
      <div>
        <Card style={{ marginBottom: 16 }}>
          <Space>
            <Button 
              icon={<ArrowLeftOutlined />} 
              onClick={() => navigate(`/plans/${id}`)}
            >
              返回
            </Button>
            <Title level={4} style={{ margin: 0 }}>编辑计划</Title>
          </Space>
        </Card>
        <Alert
          message="无法编辑"
          description="只有草稿状态的计划可以编辑"
          type="warning"
          showIcon
        />
      </div>
    );
  }

  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Button 
            icon={<ArrowLeftOutlined />} 
            onClick={() => navigate(`/plans/${id}`)}
          >
            返回
          </Button>
          <Title level={4} style={{ margin: 0 }}>编辑计划</Title>
          <span style={{ color: '#999' }}>{currentPlan?.name}</span>
        </Space>
      </Card>
      <PlanStepsForm
        mode="edit"
        planId={id}
        initialData={prepareEditData()}
      />
    </div>
  );
};

export default PlanEditView;
