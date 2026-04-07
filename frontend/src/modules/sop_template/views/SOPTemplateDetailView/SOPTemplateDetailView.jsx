import React, { useEffect } from 'react';
import {
  Card,
  Descriptions,
  Button,
  Space,
  Tag,
  Spin,
  Row,
  Col,
  Divider,
  Timeline,
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  CheckCircleOutlined,
  StopOutlined,
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { useSOPTemplateStore } from '../../store';

/**
 * SOP 模板详情页面
 */
const SOPTemplateDetailView = () => {
  const { templateId } = useParams();
  const navigate = useNavigate();
  
  const {
    currentTemplate,
    loading,
    fetchTemplateDetail,
    publishTemplate,
    deprecateTemplate,
  } = useSOPTemplateStore();

  // 加载模板详情
  useEffect(() => {
    if (templateId) {
      fetchTemplateDetail(templateId);
    }
  }, [templateId]);

  // 获取状态标签
  const getStatusTag = (status) => {
    const statusMap = {
      draft: { color: 'default', text: '草稿' },
      published: { color: 'success', text: '已发布' },
      deprecated: { color: 'error', text: '已弃用' },
    };
    const config = statusMap[status] || { color: 'default', text: status };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 获取类型标签
  const getTypeTag = (type) => {
    const typeMap = {
      standard_admission: { color: 'blue', text: '标准准入' },
      emergency_admission: { color: 'orange', text: '紧急准入' },
      change_management: { color: 'purple', text: '变更管理' },
    };
    const config = typeMap[type] || { color: 'default', text: type };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 发布模板
  const handlePublish = async () => {
    const result = await publishTemplate(templateId);
    if (result.success) {
      fetchTemplateDetail(templateId);
    }
  };

  // 弃用模板
  const handleDeprecate = async () => {
    const result = await deprecateTemplate(templateId, '手动弃用');
    if (result.success) {
      fetchTemplateDetail(templateId);
    }
  };

  if (loading || !currentTemplate) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        {/* 标题栏 */}
        <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
          <Col>
            <Space>
              <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate('/sop-templates')}
              >
                返回
              </Button>
              <h2 style={{ margin: 0 }}>SOP 模板详情</h2>
            </Space>
          </Col>
          <Col>
            <Space>
              {currentTemplate.status === 'draft' && (
                <Button
                  type="primary"
                  icon={<CheckCircleOutlined />}
                  onClick={handlePublish}
                >
                  发布
                </Button>
              )}
              {currentTemplate.status === 'published' && (
                <Button
                  danger
                  icon={<StopOutlined />}
                  onClick={handleDeprecate}
                >
                  弃用
                </Button>
              )}
              <Button
                icon={<EditOutlined />}
                onClick={() => navigate(`/sop-templates/${templateId}/edit`)}
              >
                编辑
              </Button>
            </Space>
          </Col>
        </Row>

        <Divider />

        {/* 基本信息 */}
        <Descriptions title="基本信息" bordered column={2}>
          <Descriptions.Item label="模板ID">
            {currentTemplate.template_id}
          </Descriptions.Item>
          <Descriptions.Item label="模板名称">
            {currentTemplate.name}
          </Descriptions.Item>
          <Descriptions.Item label="类型">
            {getTypeTag(currentTemplate.template_type)}
          </Descriptions.Item>
          <Descriptions.Item label="状态">
            {getStatusTag(currentTemplate.status)}
          </Descriptions.Item>
          <Descriptions.Item label="版本">
            v{currentTemplate.version}
          </Descriptions.Item>
          <Descriptions.Item label="审核矩阵">
            {currentTemplate.audit_matrix_config_id || '-'}
          </Descriptions.Item>
          <Descriptions.Item label="创建人">
            {currentTemplate.created_by}
          </Descriptions.Item>
          <Descriptions.Item label="创建时间">
            {currentTemplate.created_at ? new Date(currentTemplate.created_at).toLocaleString() : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="更新时间">
            {currentTemplate.updated_at ? new Date(currentTemplate.updated_at).toLocaleString() : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="描述" span={2}>
            {currentTemplate.description || '-'}
          </Descriptions.Item>
        </Descriptions>

        {/* 工作流节点 */}
        {currentTemplate.workflow_nodes && currentTemplate.workflow_nodes.length > 0 && (
          <>
            <Divider />
            <h3>工作流节点</h3>
            <Timeline mode="left">
              {currentTemplate.workflow_nodes.map((node, index) => (
                <Timeline.Item key={index}>
                  <Card size="small" title={`${node.sequence}. ${node.name}`}>
                    <p><strong>节点ID:</strong> {node.node_id}</p>
                    {node.entry_conditions && (
                      <p><strong>准入条件:</strong> {node.entry_conditions}</p>
                    )}
                    {node.exit_conditions && (
                      <p><strong>准出条件:</strong> {node.exit_conditions}</p>
                    )}
                    {node.work_items && node.work_items.length > 0 && (
                      <div>
                        <strong>工作项:</strong>
                        <ul>
                          {node.work_items.map((item, idx) => (
                            <li key={idx}>{item.name} ({item.category})</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </Card>
                </Timeline.Item>
              ))}
            </Timeline>
          </>
        )}
      </Card>
    </div>
  );
};

export default SOPTemplateDetailView;
