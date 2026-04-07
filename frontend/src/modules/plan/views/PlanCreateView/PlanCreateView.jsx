/**
 * PlanCreateView 组件
 * 计划创建页面 - 使用多步骤表单
 */
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Button, Typography } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { usePlanStore } from '../../store';
import PlanStepsForm from '../../components/PlanStepsForm';

const { Title } = Typography;

/**
 * 计划创建页面
 */
const PlanCreateView = () => {
  const navigate = useNavigate();
  const { resetCreationStep } = usePlanStore();

  // 页面加载时重置创建状态
  useEffect(() => {
    resetCreationStep();
  }, []);

  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <Button 
            icon={<ArrowLeftOutlined />} 
            onClick={() => navigate('/plans')}
          >
            返回列表
          </Button>
          <Title level={4} style={{ margin: 0 }}>创建计划</Title>
        </div>
      </Card>

      <PlanStepsForm />
    </div>
  );
};

export default PlanCreateView;
