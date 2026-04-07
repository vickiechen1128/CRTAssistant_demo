/**
 * PlanStepsForm 组件
 * 多步骤计划创建/编辑表单
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Steps,
  Card,
  Button,
  Form,
  message,
  Space,
  Modal,
} from 'antd';
import {
  LeftOutlined,
  RightOutlined,
  CheckOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { usePlanStore } from '../../store';
import { PlanCreationSteps } from '../../api/types';
import BasicInfoStep from './BasicInfoStep';
import ApprovalFilesStep from './ApprovalFilesStep';
import InventoryScopeStep from './InventoryScopeStep';
import PreviewStep from './PreviewStep';

const { Step } = Steps;
const { confirm } = Modal;

/**
 * 多步骤计划创建/编辑表单组件
 * @param {Object} props
 * @param {string} props.mode - 'create' | 'edit'
 * @param {Object} props.initialData - 编辑模式下的初始数据
 * @param {string} props.planId - 编辑模式下的计划ID
 */
const PlanStepsForm = ({ mode = 'create', initialData = null, planId = null }) => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const isEditMode = mode === 'edit';

  const {
    creationStep,
    creationData,
    submitting,
    setCreationStep,
    setCreationData,
    resetCreationStep,
    createNewPlan,
    updateExistingPlan,
    addApprovalFile,
  } = usePlanStore();

  const [basicInfo, setBasicInfo] = useState({});
  const [currentStep, setCurrentStep] = useState(0);

  // 同步外部步骤状态
  useEffect(() => {
    setCurrentStep(creationStep);
  }, [creationStep]);

  // 编辑模式：加载初始数据
  useEffect(() => {
    if (isEditMode && initialData) {
      // 转换日期字符串为 dayjs 对象
      const formattedData = {
        ...initialData,
        planned_start_time: initialData.planned_start_time
          ? dayjs(initialData.planned_start_time)
          : null,
        planned_end_time: initialData.planned_end_time
          ? dayjs(initialData.planned_end_time)
          : null,
      };

      setBasicInfo(formattedData);
      form.setFieldsValue(formattedData);

      // 设置创建数据
      setCreationData({
        basicInfo: formattedData,
        approvalFiles: initialData.approval_files || [],
        affectedModules: initialData.affected_modules || [],
        relatedInventoryIds: initialData.related_inventory_ids || [],
      });
    }
  }, [isEditMode, initialData, form, setCreationData]);

  // 步骤配置
  const steps = [
    {
      title: '基本信息',
      description: '填写计划名称、分类等',
      component: <BasicInfoStep form={form} />,
      validate: async () => {
        try {
          const values = await form.validateFields();
          setBasicInfo(values);
          setCreationData({ basicInfo: values });
          return true;
        } catch (error) {
          return false;
        }
      },
    },
    {
      title: '审批材料',
      description: '上传审批文件',
      component: <ApprovalFilesStep />,
      validate: () => {
        if (creationData.approvalFiles.length === 0) {
          message.warning('请至少上传一个审批材料');
          return false;
        }
        return true;
      },
    },
    {
      title: '涉及范围',
      description: '选择台账和功能模块',
      component: <InventoryScopeStep basicInfo={basicInfo} />,
      validate: () => {
        // 安全检查不需要验证
        if (basicInfo.category === 'security_check') {
          return true;
        }

        // 新系统上线至少需要填写一些信息
        if (basicInfo.category === 'new_system') {
          if (creationData.affectedModules.length === 0) {
            message.warning('请至少添加一个功能模块');
            return false;
          }
          return true;
        }

        // 其他类型需要选择应用系统
        if (creationData.relatedInventoryIds.length === 0) {
          message.warning('请至少选择一个应用系统');
          return false;
        }

        return true;
      },
    },
    {
      title: '预览确认',
      description: '确认变更内容',
      component: <PreviewStep basicInfo={basicInfo} loading={submitting} />,
      validate: () => true,
    },
  ];

  // 下一步
  const handleNext = async () => {
    const isValid = await steps[currentStep].validate();
    if (isValid) {
      const nextStep = currentStep + 1;
      setCurrentStep(nextStep);
      setCreationStep(nextStep);
    }
  };

  // 上一步
  const handlePrev = () => {
    const prevStep = currentStep - 1;
    setCurrentStep(prevStep);
    setCreationStep(prevStep);
  };

  // 提交创建
  const handleCreateSubmit = async () => {
    confirm({
      title: '确认创建计划？',
      icon: <ExclamationCircleOutlined />,
      content: '提交后将创建计划并生成唯一的PlanID，同时触发相应的工作流。',
      okText: '确认创建',
      cancelText: '再检查一下',
      onOk: async () => {
        try {
          const submitData = {
            name: basicInfo.name,
            category: basicInfo.category,
            priority: basicInfo.priority,
            description: basicInfo.description,
            planned_start_time: basicInfo.planned_start_time?.toISOString(),
            planned_end_time: basicInfo.planned_end_time?.toISOString(),
            approval_files: creationData.approvalFiles,
            affected_modules: creationData.affectedModules,
            related_inventory_ids: creationData.relatedInventoryIds,
          };

          const plan = await createNewPlan(submitData);
          message.success(`计划创建成功！PlanID: ${plan.id}`);

          // 重置创建状态
          resetCreationStep();
          form.resetFields();

          // 跳转到计划详情页
          navigate(`/plans/${plan.id}`);
        } catch (error) {
          message.error('创建计划失败：' + (error.message || '未知错误'));
        }
      },
    });
  };

  // 提交更新
  const handleUpdateSubmit = async () => {
    confirm({
      title: '确认更新计划？',
      icon: <ExclamationCircleOutlined />,
      content: '提交后将更新计划信息。',
      okText: '确认更新',
      cancelText: '再检查一下',
      onOk: async () => {
        try {
          const submitData = {
            name: basicInfo.name,
            category: basicInfo.category,
            priority: basicInfo.priority,
            description: basicInfo.description,
            planned_start_time: basicInfo.planned_start_time?.toISOString(),
            planned_end_time: basicInfo.planned_end_time?.toISOString(),
            approval_files: creationData.approvalFiles,
            affected_modules: creationData.affectedModules,
            related_inventory_ids: creationData.relatedInventoryIds,
          };

          await updateExistingPlan(planId, submitData);
          message.success('计划更新成功！');

          // 重置创建状态
          resetCreationStep();
          form.resetFields();

          // 跳转到计划详情页
          navigate(`/plans/${planId}`);
        } catch (error) {
          message.error('更新计划失败：' + (error.message || '未知错误'));
        }
      },
    });
  };

  // 取消
  const handleCancel = () => {
    const title = isEditMode ? '确认取消编辑？' : '确认取消创建？';
    const content = isEditMode
      ? '取消后将返回计划详情页。'
      : '取消后已填写的信息将丢失，确定要取消吗？';

    confirm({
      title,
      icon: <ExclamationCircleOutlined />,
      content,
      okText: '确认取消',
      okType: 'danger',
      cancelText: isEditMode ? '继续编辑' : '继续创建',
      onOk: () => {
        resetCreationStep();
        form.resetFields();
        navigate(isEditMode ? `/plans/${planId}` : '/plans');
      },
    });
  };

  return (
    <Card>
      {/* 步骤条 */}
      <Steps
        current={currentStep}
        items={PlanCreationSteps.map((step, index) => ({
          title: step.title,
          description: step.description,
        }))}
        style={{ marginBottom: 40 }}
      />

      {/* 步骤内容 */}
      <div style={{ minHeight: 400, marginBottom: 40 }}>
        {steps[currentStep].component}
      </div>

      {/* 操作按钮 */}
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <Button onClick={handleCancel}>
          取消
        </Button>

        <Space>
          {currentStep > 0 && (
            <Button icon={<LeftOutlined />} onClick={handlePrev}>
              上一步
            </Button>
          )}

          {currentStep < steps.length - 1 && (
            <Button type="primary" icon={<RightOutlined />} onClick={handleNext}>
              下一步
            </Button>
          )}

          {currentStep === steps.length - 1 && (
            <Button
              type="primary"
              icon={<CheckOutlined />}
              onClick={isEditMode ? handleUpdateSubmit : handleCreateSubmit}
              loading={submitting}
            >
              {isEditMode ? '确认更新' : '确认创建'}
            </Button>
          )}
        </Space>
      </div>
    </Card>
  );
};

export default PlanStepsForm;
