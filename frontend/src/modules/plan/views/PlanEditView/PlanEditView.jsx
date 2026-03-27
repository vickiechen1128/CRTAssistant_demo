/**
 * PlanEditView 组件
 * 编辑计划页面
 */
import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, message, Spin, Alert, Space, Typography } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { usePlanStore } from '../../store';
import PlanForm from '../../components/PlanForm';
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
    loading,
    submitting,
    fetchPlanDetail,
    updateExistingPlan,
    clearCurrentPlan,
  } = usePlanStore();

  // 加载计划详情
  useEffect(() => {
    fetchPlanDetail(id);

    return () => {
      clearCurrentPlan();
    };
  }, [id]);

  // 处理提交
  const handleSubmit = async (values) => {
    try {
      await updateExistingPlan(id, values);
      message.success('计划更新成功');
      navigate(`/plans/${id}`);
    } catch (error) {
      message.error('更新失败：' + (error.message || '未知错误'));
    }
  };

  // 处理取消
  const handleCancel = () => {
    navigate(`/plans/${id}`);
  };

  // 准备初始值
  const prepareInitialValues = () => {
    if (!currentPlan) return {};

    return {
      name: currentPlan.name,
      category: currentPlan.category,
      priority: currentPlan.priority,
      description: currentPlan.description,
      planned_start_time: currentPlan.planned_start_time,
      planned_end_time: currentPlan.planned_end_time,
    };
  };

  // 检查是否可编辑
  const isEditable = currentPlan?.status === PlanStatus.DRAFT;

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
      <PlanForm
        initialValues={prepareInitialValues()}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        loading={submitting}
      />
    </div>
  );
};

export default PlanEditView;
