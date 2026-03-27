/**
 * PlanCreateView 组件
 * 创建计划页面
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Button, message, Space, Typography } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { usePlanStore } from '../../store';
import PlanForm from '../../components/PlanForm';

const { Title } = Typography;

/**
 * PlanCreateView 组件
 */
const PlanCreateView = () => {
  const navigate = useNavigate();
  const { createNewPlan, submitting } = usePlanStore();

  // 处理提交
  const handleSubmit = async (values) => {
    try {
      await createNewPlan(values);
      message.success('计划创建成功');
      navigate('/plans');
    } catch (error) {
      message.error('创建失败：' + (error.message || '未知错误'));
    }
  };

  // 处理取消
  const handleCancel = () => {
    navigate('/plans');
  };

  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Button 
            icon={<ArrowLeftOutlined />} 
            onClick={() => navigate('/plans')}
          >
            返回
          </Button>
          <Title level={4} style={{ margin: 0 }}>创建计划</Title>
        </Space>
      </Card>
      <PlanForm
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        loading={submitting}
      />
    </div>
  );
};

export default PlanCreateView;
