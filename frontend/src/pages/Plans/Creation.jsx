/**
 * 计划创建页面
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Steps,
  Form,
  Input,
  Select,
  DatePicker,
  Button,
  Radio,
  Checkbox,
  Upload,
  Tag,
  Space,
  Divider,
  Alert,
  Table,
  Progress,
  Timeline,
  message,
} from 'antd';
import {
  ArrowLeftOutlined,
  SaveOutlined,
  SendOutlined,
  PlusOutlined,
  UploadOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  DesktopOutlined,
  CloudOutlined,
  DatabaseOutlined,
  AppstoreOutlined,
  SettingOutlined,
  ToolOutlined,
  SearchOutlined,
  DeleteOutlined,
} from '@ant-design/icons';

const { Step } = Steps;
const { Option } = Select;
const { TextArea } = Input;
const { RangePicker } = DatePicker;

// 计划分类选项
const categoryOptions = [
  {
    value: 'new_system',
    label: '新系统建设',
    icon: '🆕',
    desc: '全新业务系统的规划与建设',
    scope: '应用系统台账 + 云服务资源 + 系统账号',
  },
  {
    value: 'new_feature',
    label: '新功能上线',
    icon: '✨',
    desc: '现有系统新增功能模块',
    scope: '功能模块更新 + 云服务扩容',
  },
  {
    value: 'business_change',
    label: '业务变更',
    icon: '📊',
    desc: '业务流程调整或优化',
    scope: '功能模块变更 + 配置更新',
  },
  {
    value: 'db_change',
    label: '数据库变更',
    icon: '🗄️',
    desc: '数据库结构或数据迁移',
    scope: '数据库资源 + 相关应用',
  },
];

// 模拟应用系统数据
const mockApps = [
  { id: 'APP-001', name: '订单管理系统', modules: ['订单创建', '订单查询', '订单审核'], resources: ['ECS-001', 'RDS-001'] },
  { id: 'APP-002', name: '支付系统', modules: ['支付接口', '对账管理', '退款处理'], resources: ['ECS-002', 'RDS-002'] },
  { id: 'APP-003', name: '用户中心', modules: ['用户注册', '用户登录', '权限管理'], resources: ['ECS-003', 'Redis-001'] },
  { id: 'APP-004', name: '库存管理系统', modules: ['库存查询', '入库管理', '出库管理'], resources: ['ECS-004', 'RDS-003'] },
];

// 模拟云资源数据
const mockCloudResources = {
  compute: [
    { id: 'ECS-001', name: 'order-server-01', spec: '8C16G', ip: '192.168.1.101' },
    { id: 'ECS-002', name: 'payment-server-01', spec: '16C32G', ip: '192.168.1.102' },
  ],
  network: [
    { id: 'VPC-001', name: '生产环境VPC', cidr: '192.168.0.0/16' },
    { id: 'SLB-001', name: '公网负载均衡', type: 'ALB' },
  ],
  storage: [
    { id: 'OSS-001', name: '文件存储bucket', type: '标准存储' },
    { id: 'NAS-001', name: '共享存储', protocol: 'NFS' },
  ],
  software: [
    { id: 'RDS-001', name: '订单数据库', type: 'MySQL 8.0' },
    { id: 'Redis-001', name: '缓存集群', type: 'Redis 6.0' },
  ],
};

function PlanCreation() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedApps, setSelectedApps] = useState([]);
  const [selectedResources, setSelectedResources] = useState([]);
  const [scopeStep, setScopeStep] = useState('app');
  const [resourceTab, setResourceTab] = useState('compute');
  const [uploadedFiles, setUploadedFiles] = useState([]);

  // 步骤配置
  const steps = [
    { title: '基础信息', icon: <FileTextOutlined /> },
    { title: '范围选择', icon: <AppstoreOutlined /> },
    { title: '工作项确认', icon: <CheckCircleOutlined /> },
    { title: '审批材料', icon: <FileTextOutlined /> },
  ];

  // 下一步
  const nextStep = () => {
    form.validateFields().then(() => {
      setCurrentStep(currentStep + 1);
    });
  };

  // 上一步
  const prevStep = () => {
    setCurrentStep(currentStep - 1);
  };

  // 提交表单
  const handleSubmit = () => {
    message.success('计划创建成功！');
    navigate('/plans');
  };

  // 保存草稿
  const handleSaveDraft = () => {
    message.success('草稿已保存');
  };

  // 渲染步骤内容
  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div>
            <Divider orientation="left">计划基本信息</Divider>
            <Form.Item
              name="planName"
              label="计划名称"
              rules={[{ required: true, message: '请输入计划名称' }]}
            >
              <Input placeholder="请输入计划名称，如：订单管理系统V2.0上线" />
            </Form.Item>

            <Form.Item
              name="planDesc"
              label="计划描述"
            >
              <TextArea rows={4} placeholder="描述计划的目标、背景、预期效果等" />
            </Form.Item>

            <Form.Item
              name="timeRange"
              label="计划周期"
              rules={[{ required: true, message: '请选择计划周期' }]}
            >
              <RangePicker style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item
              name="priority"
              label="优先级"
              rules={[{ required: true, message: '请选择优先级' }]}
            >
              <Select placeholder="请选择优先级">
                <Option value="P0">
                  <Tag color="red">P0-紧急</Tag>
                </Option>
                <Option value="P1">
                  <Tag color="orange">P1-高</Tag>
                </Option>
                <Option value="P2">
                  <Tag color="gold">P2-中</Tag>
                </Option>
                <Option value="P3">
                  <Tag color="green">P3-低</Tag>
                </Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="manager"
              label="负责人"
              rules={[{ required: true, message: '请输入负责人' }]}
            >
              <Input placeholder="请输入负责人姓名" />
            </Form.Item>

            <Divider orientation="left">计划分类</Divider>
            <Form.Item
              name="category"
              rules={[{ required: true, message: '请选择计划分类' }]}
            >
              <Radio.Group
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                style={{ width: '100%' }}
              >
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16 }}>
                  {categoryOptions.map((cat) => (
                    <Radio.Button
                      key={cat.value}
                      value={cat.value}
                      style={{
                        height: 'auto',
                        padding: 20,
                        borderRadius: 8,
                        border: `2px solid ${selectedCategory === cat.value ? '#667eea' : '#e8e8e8'}`,
                        background: selectedCategory === cat.value ? '#f0f3ff' : 'white',
                      }}
                    >
                      <div style={{ textAlign: 'left' }}>
                        <div style={{ fontSize: 32, marginBottom: 8 }}>{cat.icon}</div>
                        <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>{cat.label}</div>
                        <div style={{ fontSize: 13, color: '#666', marginBottom: 12 }}>{cat.desc}</div>
                        <Tag color="blue">{cat.scope}</Tag>
                      </div>
                    </Radio.Button>
                  ))}
                </div>
              </Radio.Group>
            </Form.Item>
          </div>
        );

      case 1:
        return (
          <div>
            <Alert
              message="范围选择说明"
              description="根据计划类型，选择涉及的应用系统和云服务资源。系统将自动生成对应的工作项。"
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />

            {/* 范围选择步骤指示器 */}
            <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
              {['app', 'resource', 'confirm'].map((step, index) => (
                <Tag
                  key={step}
                  color={scopeStep === step ? '#667eea' : scopeStep === 'confirm' || (scopeStep === 'resource' && step === 'app') ? 'green' : 'default'}
                  style={{
                    padding: '6px 16px',
                    fontSize: 13,
                    cursor: 'pointer',
                  }}
                  onClick={() => setScopeStep(step)}
                >
                  {index + 1}. {step === 'app' ? '选择应用系统' : step === 'resource' ? '选择云资源' : '确认范围'}
                </Tag>
              ))}
            </div>

            {scopeStep === 'app' && (
              <div>
                <Card title="选择应用系统" style={{ marginBottom: 16 }}>
                  <Input.Search
                    placeholder="搜索应用系统"
                    prefix={<SearchOutlined />}
                    style={{ marginBottom: 16 }}
                  />
                  <div style={{ maxHeight: 400, overflow: 'auto' }}>
                    {mockApps.map((app) => (
                      <Card
                        key={app.id}
                        size="small"
                        style={{
                          marginBottom: 12,
                          border: selectedApps.find((a) => a.id === app.id)
                            ? '2px solid #667eea'
                            : '1px solid #e8e8e8',
                          background: selectedApps.find((a) => a.id === app.id) ? '#f0f3ff' : 'white',
                          cursor: 'pointer',
                        }}
                        onClick={() => {
                          if (selectedApps.find((a) => a.id === app.id)) {
                            setSelectedApps(selectedApps.filter((a) => a.id !== app.id));
                          } else {
                            setSelectedApps([...selectedApps, app]);
                          }
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                          <Checkbox checked={!!selectedApps.find((a) => a.id === app.id)} />
                          <div style={{ flex: 1 }}>
                            <div style={{ fontWeight: 500 }}>{app.name}</div>
                            <div style={{ fontSize: 12, color: '#999' }}>{app.id}</div>
                          </div>
                          <div style={{ display: 'flex', gap: 4 }}>
                            {app.modules.map((m) => (
                              <Tag key={m} size="small">{m}</Tag>
                            ))}
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                </Card>
                <Button type="primary" onClick={() => setScopeStep('resource')}>
                  下一步：选择云资源
                </Button>
              </div>
            )}

            {scopeStep === 'resource' && (
              <div>
                <Card
                  title="选择云服务资源"
                  tabList={[
                    { key: 'compute', tab: '计算资源' },
                    { key: 'network', tab: '网络资源' },
                    { key: 'storage', tab: '存储资源' },
                    { key: 'software', tab: 'PAAS软件' },
                  ]}
                  activeTabKey={resourceTab}
                  onTabChange={(key) => setResourceTab(key)}
                >
                  <div style={{ maxHeight: 400, overflow: 'auto' }}>
                    {mockCloudResources[resourceTab]?.map((resource) => (
                      <Card
                        key={resource.id}
                        size="small"
                        style={{
                          marginBottom: 12,
                          border: selectedResources.find((r) => r.id === resource.id)
                            ? '2px solid #667eea'
                            : '1px solid #e8e8e8',
                          background: selectedResources.find((r) => r.id === resource.id) ? '#f0f3ff' : 'white',
                          cursor: 'pointer',
                        }}
                        onClick={() => {
                          if (selectedResources.find((r) => r.id === resource.id)) {
                            setSelectedResources(selectedResources.filter((r) => r.id !== resource.id));
                          } else {
                            setSelectedResources([...selectedResources, resource]);
                          }
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                          <Checkbox checked={!!selectedResources.find((r) => r.id === resource.id)} />
                          <div style={{ flex: 1 }}>
                            <div style={{ fontWeight: 500 }}>{resource.name}</div>
                            <div style={{ fontSize: 12, color: '#999' }}>{resource.id}</div>
                          </div>
                          <Tag size="small">{resource.spec || resource.type || resource.cidr}</Tag>
                        </div>
                      </Card>
                    ))}
                  </div>
                </Card>
                <Space>
                  <Button onClick={() => setScopeStep('app')}>上一步</Button>
                  <Button type="primary" onClick={() => setScopeStep('confirm')}>
                    下一步：确认范围
                  </Button>
                </Space>
              </div>
            )}

            {scopeStep === 'confirm' && (
              <div>
                <Alert
                  message="范围确认"
                  description="请确认以下选择范围是否正确，确认后将生成对应的工作项。"
                  type="warning"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
                <Card title="已选择应用系统" style={{ marginBottom: 16 }}>
                  {selectedApps.length > 0 ? (
                    <Space wrap>
                      {selectedApps.map((app) => (
                        <Tag key={app.id} closable onClose={() => setSelectedApps(selectedApps.filter((a) => a.id !== app.id))}>
                          {app.name}
                        </Tag>
                      ))}
                    </Space>
                  ) : (
                    <span style={{ color: '#999' }}>未选择应用系统</span>
                  )}
                </Card>
                <Card title="已选择云资源">
                  {selectedResources.length > 0 ? (
                    <Space wrap>
                      {selectedResources.map((resource) => (
                        <Tag key={resource.id} closable onClose={() => setSelectedResources(selectedResources.filter((r) => r.id !== resource.id))}>
                          {resource.name}
                        </Tag>
                      ))}
                    </Space>
                  ) : (
                    <span style={{ color: '#999' }}>未选择云资源</span>
                  )}
                </Card>
                <div style={{ marginTop: 16 }}>
                  <Button onClick={() => setScopeStep('resource')}>返回修改</Button>
                </div>
              </div>
            )}
          </div>
        );

      case 2:
        return (
          <div>
            <Alert
              message="工作项预览"
              description="根据选择的范围，系统自动生成以下工作项。您可以在提交前进行确认。"
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />

            <Card title="应用系统工作项" style={{ marginBottom: 16 }}>
              <Timeline>
                {selectedApps.map((app, index) => (
                  <Timeline.Item key={app.id}>
                    <div style={{ fontWeight: 500 }}>{app.name} - 应用准入检查</div>
                    <div style={{ fontSize: 13, color: '#666', marginTop: 4 }}>
                      检查项：应用台账完整性、功能模块配置、基础资源就绪
                    </div>
                  </Timeline.Item>
                ))}
              </Timeline>
            </Card>

            <Card title="云服务资源工作项" style={{ marginBottom: 16 }}>
              <Timeline>
                {selectedResources.map((resource) => (
                  <Timeline.Item key={resource.id}>
                    <div style={{ fontWeight: 500 }}>{resource.name} - 资源准入检查</div>
                    <div style={{ fontSize: 13, color: '#666', marginTop: 4 }}>
                      检查项：资源配置合规性、安全组规则、监控告警配置
                    </div>
                  </Timeline.Item>
                ))}
              </Timeline>
            </Card>

            <Card title="通用工作项">
              <Timeline>
                <Timeline.Item>审批材料准备与上传</Timeline.Item>
                <Timeline.Item>变更评审会议</Timeline.Item>
                <Timeline.Item>上线前最终检查</Timeline.Item>
              </Timeline>
            </Card>
          </div>
        );

      case 3:
        return (
          <div>
            <Alert
              message="审批材料上传"
              description="请上传计划相关的审批材料，包括需求文档、设计文档、测试报告等。"
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />

            <Card title="材料上传" style={{ marginBottom: 16 }}>
              <Upload.Dragger
                multiple
                fileList={uploadedFiles}
                onChange={({ fileList }) => setUploadedFiles(fileList)}
                style={{ padding: 40 }}
              >
                <p className="ant-upload-drag-icon">
                  <UploadOutlined style={{ fontSize: 48, color: '#667eea' }} />
                </p>
                <p className="ant-upload-text">点击或拖拽文件到此处上传</p>
                <p className="ant-upload-hint">
                  支持 PDF、Word、Excel、图片等格式，单个文件不超过 50MB
                </p>
              </Upload.Dragger>
            </Card>

            {uploadedFiles.length > 0 && (
              <Card title="已上传文件">
                <Space direction="vertical" style={{ width: '100%' }}>
                  {uploadedFiles.map((file, index) => (
                    <div
                      key={index}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        padding: 12,
                        background: '#f5f7fa',
                        borderRadius: 6,
                      }}
                    >
                      <FileTextOutlined style={{ fontSize: 24, marginRight: 12, color: '#667eea' }} />
                      <div style={{ flex: 1 }}>
                        <div>{file.name}</div>
                        <div style={{ fontSize: 12, color: '#999' }}>
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </div>
                      </div>
                      <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={() => setUploadedFiles(uploadedFiles.filter((_, i) => i !== index))}
                      />
                    </div>
                  ))}
                </Space>
              </Card>
            )}

            <Card style={{ marginTop: 16, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
              <div style={{ fontSize: 14, marginBottom: 12, opacity: 0.9 }}>标签预览</div>
              <div
                style={{
                  background: 'rgba(255,255,255,0.15)',
                  padding: 12,
                  borderRadius: 6,
                  fontFamily: 'monospace',
                  fontSize: 14,
                }}
              >
                {`{
  "plan_id": "PLAN-${Date.now()}",
  "category": "${selectedCategory}",
  "apps": [${selectedApps.map((a) => `"${a.id}"`).join(', ')}],
  "resources": [${selectedResources.map((r) => `"${r.id}"`).join(', ')}],
  "status": "pending"
}`}
              </div>
            </Card>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div>
      {/* 页面标题 */}
      <Card style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: 20, fontWeight: 600, marginBottom: 4, display: 'flex', alignItems: 'center', gap: 12 }}>
              <div
                style={{
                  width: 44,
                  height: 44,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  borderRadius: 12,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 24,
                  color: 'white',
                }}
              >
                <PlusOutlined />
              </div>
              创建计划
            </div>
            <div style={{ fontSize: 13, color: '#666', marginLeft: 56 }}>
              计划管理 &gt; 创建
            </div>
          </div>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/plans')}>
            返回列表
          </Button>
        </div>
      </Card>

      {/* 步骤条 */}
      <Card style={{ marginBottom: 24 }}>
        <Steps current={currentStep}>
          {steps.map((step, index) => (
            <Step
              key={index}
              title={step.title}
              icon={step.icon}
            />
          ))}
        </Steps>
      </Card>

      {/* 表单内容 */}
      <Form form={form} layout="vertical">
        <Card>
          {renderStepContent()}

          {/* 操作按钮 */}
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 40, paddingTop: 24, borderTop: '1px solid #f0f0f0' }}>
            <div>
              {currentStep > 0 && (
                <Button onClick={prevStep} style={{ marginRight: 8 }}>
                  上一步
                </Button>
              )}
            </div>
            <Space>
              <Button icon={<SaveOutlined />} onClick={handleSaveDraft}>
                保存草稿
              </Button>
              {currentStep < steps.length - 1 ? (
                <Button type="primary" onClick={nextStep} style={{ background: '#667eea', borderColor: '#667eea' }}>
                  下一步
                </Button>
              ) : (
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={handleSubmit}
                  style={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    border: 'none',
                  }}
                >
                  提交计划
                </Button>
              )}
            </Space>
          </div>
        </Card>
      </Form>
    </div>
  );
}

export default PlanCreation;
