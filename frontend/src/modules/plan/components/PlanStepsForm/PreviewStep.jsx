/**
 * PreviewStep 组件
 * Step 4: 预览确认变更内容
 * 改造后版本 - 添加数据同步信息展示
 */
import React, { useEffect, useState } from 'react';
import {
  Card,
  Descriptions,
  Tag,
  Table,
  Timeline,
  Alert,
  Spin,
  Space,
  Row,
  Col,
  Divider,
  Badge,
} from 'antd';
import {
  RocketOutlined,
  FileTextOutlined,
  AppstoreOutlined,
  CheckCircleOutlined,
  SyncOutlined,
  DatabaseOutlined,
  CloudSyncOutlined,
} from '@ant-design/icons';
import { usePlanStore } from '../../store';
import {
  categoryOptions,
  priorityOptions,
  moduleActionOptions,
  PlanCategory,
} from '../../api/types';

/**
 * 预览确认步骤组件
 * 改造点：
 * 1. 添加数据同步预览信息
 * 2. 显示台账变更详情
 * 3. 显示同步后的预期结果
 */
const PreviewStep = ({ basicInfo, loading: submitLoading }) => {
  const { creationData, previewData, fetchPreviewChanges, inventoryList } = usePlanStore();
  const { approvalFiles, affectedModules, relatedInventoryIds } = creationData;
  const [loading, setLoading] = useState(true);

  // 获取预览数据
  useEffect(() => {
    const loadPreview = async () => {
      setLoading(true);
      try {
        await fetchPreviewChanges({
          name: basicInfo?.name,
          category: basicInfo?.category,
          affected_modules: affectedModules,
          related_inventory_ids: relatedInventoryIds,
        });
      } catch (error) {
        console.error('获取预览失败:', error);
      } finally {
        setLoading(false);
      }
    };

    loadPreview();
  }, []);

  // 获取分类标签
  const getCategoryLabel = (category) => {
    const config = categoryOptions.find((opt) => opt.value === category);
    return config?.label || category;
  };

  // 获取优先级标签
  const getPriorityLabel = (priority) => {
    const config = priorityOptions.find((opt) => opt.value === priority);
    return config?.label || priority;
  };

  // 格式化日期
  const formatDate = (date) => {
    if (!date) return '-';
    return new Date(date).toLocaleString('zh-CN');
  };

  // 获取应用系统名称
  const getInventoryName = (id) => {
    const app = inventoryList.find((item) => item.id === id);
    return app?.app_name || app?.name || id;
  };

  // 模块表格列
  const moduleColumns = [
    {
      title: '模块名称',
      dataIndex: 'module_name',
      key: 'module_name',
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
      render: (action) => {
        const config = moduleActionOptions.find((opt) => opt.value === action);
        return <Tag color={config?.color}>{config?.label}</Tag>;
      },
    },
    {
      title: '版本变更',
      key: 'version',
      render: (_, record) => (
        <span>
          {record.before_version || '-'}
          {' → '}
          {record.after_version || '-'}
        </span>
      ),
    },
    {
      title: '变更说明',
      dataIndex: 'change_description',
      key: 'change_description',
      ellipsis: true,
    },
  ];

  // 获取数据同步预览信息
  const getSyncPreviewInfo = () => {
    const category = basicInfo?.category;

    switch (category) {
      case PlanCategory.NEW_SYSTEM:
        return {
          title: '新系统上线同步',
          description: '计划完成后将自动创建应用系统台账和功能模块',
          operations: [
            { type: 'create', label: '创建应用系统台账', icon: <DatabaseOutlined /> },
            { type: 'create', label: `创建 ${affectedModules.length} 个功能模块`, icon: <AppstoreOutlined /> },
            { type: 'log', label: '生成系统上线生命周期日志', icon: <RocketOutlined /> },
          ],
        };
      case PlanCategory.NEW_FEATURE:
        return {
          title: '新功能上线同步',
          description: '计划完成后将在选定应用系统中添加新功能模块',
          operations: [
            { type: 'create', label: `创建 ${affectedModules.length} 个功能模块`, icon: <AppstoreOutlined /> },
            { type: 'log', label: '生成功能上线生命周期日志', icon: <RocketOutlined /> },
          ],
        };
      case PlanCategory.FUNC_CHANGE:
        return {
          title: '功能变更同步',
          description: '计划完成后将更新选定功能模块的版本和状态',
          operations: [
            { type: 'update', label: `更新 ${affectedModules.length} 个功能模块`, icon: <SyncOutlined /> },
            { type: 'log', label: '生成功能变更生命周期日志', icon: <RocketOutlined /> },
          ],
        };
      case PlanCategory.ARCH_CHANGE:
        return {
          title: '架构变更同步',
          description: '计划完成后将更新应用系统架构信息和相关配置',
          operations: [
            { type: 'update', label: `更新 ${relatedInventoryIds.length} 个应用系统`, icon: <SyncOutlined /> },
            { type: 'log', label: '生成架构变更生命周期日志', icon: <RocketOutlined /> },
          ],
        };
      case PlanCategory.SECURITY_CHECK:
        return {
          title: '安全检查',
          description: '安全检查不会修改台账数据，仅记录检查结果',
          operations: [
            { type: 'log', label: '生成安全检查日志', icon: <RocketOutlined /> },
          ],
        };
      default:
        return null;
    }
  };

  const syncPreviewInfo = getSyncPreviewInfo();

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" tip="正在生成预览..." />
      </div>
    );
  }

  return (
    <div>
      {/* 计划信息摘要 */}
      <Card title="计划信息" style={{ marginBottom: 16 }}>
        <Descriptions bordered column={2} size="small">
          <Descriptions.Item label="计划名称">
            {basicInfo?.name}
          </Descriptions.Item>
          <Descriptions.Item label="计划分类">
            {getCategoryLabel(basicInfo?.category)}
          </Descriptions.Item>
          <Descriptions.Item label="优先级">
            <Tag
              color={
                priorityOptions.find((opt) => opt.value === basicInfo?.priority)
                  ?.color
              }
            >
              {getPriorityLabel(basicInfo?.priority)}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="执行时间">
            {formatDate(basicInfo?.planned_start_time)}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* 数据同步预览 */}
      {syncPreviewInfo && (
        <Card
          title={
            <Space>
              <CloudSyncOutlined />
              <span>数据同步预览</span>
            </Space>
          }
          style={{ marginBottom: 16 }}
        >
          <Alert
            message={syncPreviewInfo.title}
            description={syncPreviewInfo.description}
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
          <Timeline>
            {syncPreviewInfo.operations.map((op, index) => (
              <Timeline.Item key={index} dot={op.icon}>
                <Space>
                  <Badge
                    status={op.type === 'create' ? 'success' : op.type === 'update' ? 'processing' : 'default'}
                    text={op.label}
                  />
                </Space>
              </Timeline.Item>
            ))}
          </Timeline>
        </Card>
      )}

      {/* 关联应用系统 */}
      {relatedInventoryIds.length > 0 && (
        <Card title="关联应用系统" style={{ marginBottom: 16 }}>
          <Space wrap>
            {relatedInventoryIds.map((id) => (
              <Tag key={id} color="blue" icon={<DatabaseOutlined />}>
                {getInventoryName(id)}
              </Tag>
            ))}
          </Space>
        </Card>
      )}

      {/* 功能模块变更摘要 */}
      <Card title="功能模块变更" style={{ marginBottom: 16 }}>
        {affectedModules.length > 0 ? (
          <Table
            dataSource={affectedModules}
            columns={moduleColumns}
            rowKey="module_id"
            pagination={false}
            size="small"
          />
        ) : (
          <Alert
            message="未配置功能模块变更"
            description="本次计划不涉及功能模块的新增或变更"
            type="info"
            showIcon
          />
        )}
      </Card>

      {/* 生命周期日志预览 */}
      {previewData?.lifecycle_logs_preview?.length > 0 && (
        <Card title="将要生成的生命周期日志" style={{ marginBottom: 16 }}>
          <Timeline>
            {previewData.lifecycle_logs_preview.map((log, index) => (
              <Timeline.Item
                key={index}
                dot={<RocketOutlined style={{ color: '#52c41a' }} />}
              >
                <p style={{ marginBottom: 4 }}>
                  <Tag color="green">{log.log_type_label}</Tag>
                </p>
                <p>{log.event_title}</p>
              </Timeline.Item>
            ))}
          </Timeline>
        </Card>
      )}

      {/* 工作流检查项预览 */}
      {previewData?.workflow_preview?.check_items?.length > 0 && (
        <Card title="工作流检查项预览" style={{ marginBottom: 16 }}>
          <Row gutter={[16, 16]}>
            {previewData.workflow_preview.check_items.map((item, index) => (
              <Col span={12} key={index}>
                <Card size="small">
                  <Space>
                    <CheckCircleOutlined style={{ color: '#52c41a' }} />
                    <span>{item.name}</span>
                    {item.required && <Tag color="red">必填</Tag>}
                  </Space>
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {/* 审批材料确认 */}
      <Card title="审批材料">
        {approvalFiles.length > 0 ? (
          <Timeline>
            {approvalFiles.map((file, index) => (
              <Timeline.Item
                key={index}
                dot={<FileTextOutlined />}
              >
                <p>{file.file_name}</p>
                <p style={{ color: '#999', fontSize: 12 }}>
                  {(file.file_size / 1024 / 1024).toFixed(2)} MB
                </p>
              </Timeline.Item>
            ))}
          </Timeline>
        ) : (
          <Alert
            message="未上传审批材料"
            type="warning"
            showIcon
          />
        )}
      </Card>

      {/* 提交提示 */}
      <Alert
        style={{ marginTop: 16 }}
        message="确认提交"
        description="提交后将创建计划并生成PlanID，同时触发相应的工作流。计划完成后将自动同步数据到台账管理系统。请确认以上信息无误。"
        type="info"
        showIcon
      />
    </div>
  );
};

export default PreviewStep;
