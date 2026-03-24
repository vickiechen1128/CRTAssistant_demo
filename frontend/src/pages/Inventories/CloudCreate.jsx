/**
 * 云服务台账创建页面
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Form,
  Input,
  Button,
  Select,
  Space,
  Tag,
  Alert,
  Divider,
  Tabs,
  Upload,
  message,
  Radio,
} from 'antd';
import {
  ArrowLeftOutlined,
  PlusOutlined,
  SaveOutlined,
  CloudOutlined,
  InfoCircleOutlined,
  UploadOutlined,
  DownloadOutlined,
  DesktopOutlined,
  GlobalOutlined,
  DatabaseOutlined,
  SettingOutlined,
} from '@ant-design/icons';

const { TextArea } = Input;
const { Option } = Select;
const { TabPane } = Tabs;
const { Dragger } = Upload;

// 资源类型选项
const resourceTypes = [
  { value: 'compute', label: '计算资源', icon: <DesktopOutlined />, color: '#667eea' },
  { value: 'network', label: '网络资源', icon: <GlobalOutlined />, color: '#11998e' },
  { value: 'storage', label: '存储资源', icon: <DatabaseOutlined />, color: '#faad14' },
  { value: 'software', label: 'PAAS软件', icon: <SettingOutlined />, color: '#722ed1' },
];

// 模拟应用系统数据
const mockApps = [
  { id: 'APP-001', name: '订单管理系统' },
  { id: 'APP-002', name: '支付系统' },
  { id: 'APP-003', name: '用户中心' },
  { id: 'APP-004', name: '库存管理系统' },
];

function CloudInventoryCreate() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [activeTab, setActiveTab] = useState('manual');
  const [selectedResourceType, setSelectedResourceType] = useState('compute');
  const [uploadedFiles, setUploadedFiles] = useState([]);

  // 提交表单
  const handleSubmit = () => {
    form.validateFields().then((values) => {
      console.log('表单数据:', values);
      message.success('云服务台账创建成功！');
      navigate('/inventories');
    });
  };

  // 保存草稿
  const handleSaveDraft = () => {
    message.success('草稿已保存');
  };

  // 渲染资源类型选择卡片
  const renderResourceTypeCards = () => (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
      {resourceTypes.map((type) => (
        <Card
          key={type.value}
          hoverable
          onClick={() => setSelectedResourceType(type.value)}
          style={{
            border: selectedResourceType === type.value ? `2px solid ${type.color}` : '2px solid #e8e8e8',
            background: selectedResourceType === type.value ? `linear-gradient(135deg, ${type.color}08 0%, ${type.color}15 100%)` : 'white',
            cursor: 'pointer',
            textAlign: 'center',
          }}
          bodyStyle={{ padding: 20 }}
        >
          <div style={{ fontSize: 32, marginBottom: 8, color: type.color }}>{type.icon}</div>
          <div style={{ fontSize: 14, fontWeight: 600 }}>{type.label}</div>
        </Card>
      ))}
    </div>
  );

  // 渲染计算资源表单
  const renderComputeForm = () => (
    <>
      <Divider orientation="left">计算资源信息</Divider>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
        <Form.Item
          name="instanceName"
          label="实例名称"
          rules={[{ required: true, message: '请输入实例名称' }]}
        >
          <Input placeholder="如：order-app-server-01" />
        </Form.Item>

        <Form.Item
          name="instanceId"
          label="实例ID"
          rules={[{ required: true, message: '请输入实例ID' }]}
        >
          <Input placeholder="如：i-1234567890abcdef" />
        </Form.Item>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
        <Form.Item
          name="spec"
          label="实例规格"
          rules={[{ required: true, message: '请输入实例规格' }]}
        >
          <Input placeholder="如：8C16G" />
        </Form.Item>

        <Form.Item name="cpu" label="CPU核数">
          <Input type="number" placeholder="8" />
        </Form.Item>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
        <Form.Item name="memory" label="内存(GB)">
          <Input type="number" placeholder="16" />
        </Form.Item>

        <Form.Item name="osType" label="操作系统类型">
          <Select placeholder="请选择">
            <Option value="Linux">Linux</Option>
            <Option value="Windows">Windows</Option>
          </Select>
        </Form.Item>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
        <Form.Item name="osVersion" label="操作系统版本">
          <Input placeholder="如：CentOS 7.9" />
        </Form.Item>

        <Form.Item name="module" label="所属功能模块">
          <Select placeholder="选择功能模块">
            <Option value="module-001">订单创建</Option>
            <Option value="module-002">订单查询</Option>
          </Select>
        </Form.Item>
      </div>
    </>
  );

  // 渲染网络资源表单
  const renderNetworkForm = () => (
    <>
      <Divider orientation="left">网络资源信息</Divider>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
        <Form.Item
          name="resourceName"
          label="资源名称"
          rules={[{ required: true, message: '请输入资源名称' }]}
        >
          <Input placeholder="如：生产环境VPC" />
        </Form.Item>

        <Form.Item
          name="resourceType"
          label="资源类型"
          rules={[{ required: true, message: '请选择资源类型' }]}
        >
          <Select placeholder="请选择">
            <Option value="VPC">VPC</Option>
            <Option value="SLB">负载均衡</Option>
            <Option value="EIP">弹性IP</Option>
            <Option value="NAT">NAT网关</Option>
          </Select>
        </Form.Item>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
        <Form.Item name="cidr" label="CIDR网段">
          <Input placeholder="如：192.168.0.0/16" />
        </Form.Item>

        <Form.Item name="bandwidth" label="带宽(Mbps)">
          <Input type="number" placeholder="100" />
        </Form.Item>
      </div>
    </>
  );

  // 渲染存储资源表单
  const renderStorageForm = () => (
    <>
      <Divider orientation="left">存储资源信息</Divider>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
        <Form.Item
          name="storageName"
          label="存储名称"
          rules={[{ required: true, message: '请输入存储名称' }]}
        >
          <Input placeholder="如：文件存储bucket" />
        </Form.Item>

        <Form.Item
          name="storageType"
          label="存储类型"
          rules={[{ required: true, message: '请选择存储类型' }]}
        >
          <Select placeholder="请选择">
            <Option value="OSS">对象存储OSS</Option>
            <Option value="NAS">文件存储NAS</Option>
            <Option value="EBS">块存储EBS</Option>
          </Select>
        </Form.Item>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
        <Form.Item name="capacity" label="容量(GB)">
          <Input type="number" placeholder="1000" />
        </Form.Item>

        <Form.Item name="storageClass" label="存储类型">
          <Select placeholder="请选择">
            <Option value="standard">标准存储</Option>
            <Option value="ia">低频访问</Option>
            <Option value="archive">归档存储</Option>
          </Select>
        </Form.Item>
      </div>
    </>
  );

  // 渲染PAAS软件表单
  const renderSoftwareForm = () => (
    <>
      <Divider orientation="left">PAAS软件信息</Divider>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
        <Form.Item
          name="softwareName"
          label="软件名称"
          rules={[{ required: true, message: '请输入软件名称' }]}
        >
          <Input placeholder="如：订单数据库" />
        </Form.Item>

        <Form.Item
          name="softwareType"
          label="软件类型"
          rules={[{ required: true, message: '请选择软件类型' }]}
        >
          <Select placeholder="请选择">
            <Option value="MySQL">MySQL</Option>
            <Option value="PostgreSQL">PostgreSQL</Option>
            <Option value="Redis">Redis</Option>
            <Option value="MongoDB">MongoDB</Option>
            <Option value="Kafka">Kafka</Option>
            <Option value="RabbitMQ">RabbitMQ</Option>
          </Select>
        </Form.Item>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
        <Form.Item name="version" label="版本号">
          <Input placeholder="如：8.0.28" />
        </Form.Item>

        <Form.Item name="instanceSpec" label="实例规格">
          <Input placeholder="如：4C8G" />
        </Form.Item>
      </div>
    </>
  );

  // 渲染资源表单
  const renderResourceForm = () => {
    switch (selectedResourceType) {
      case 'compute':
        return renderComputeForm();
      case 'network':
        return renderNetworkForm();
      case 'storage':
        return renderStorageForm();
      case 'software':
        return renderSoftwareForm();
      default:
        return renderComputeForm();
    }
  };

  return (
    <div>
      {/* 页面标题 */}
      <Card style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div
              style={{
                fontSize: 20,
                fontWeight: 600,
                marginBottom: 4,
                display: 'flex',
                alignItems: 'center',
                gap: 12,
              }}
            >
              <div
                style={{
                  width: 44,
                  height: 44,
                  background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
                  borderRadius: 12,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 24,
                  color: 'white',
                }}
              >
                <CloudOutlined />
              </div>
              <div>
                <div>创建与导入云服务台账</div>
                <div style={{ fontSize: 13, color: '#666', fontWeight: 'normal', marginTop: 4 }}>
                  台账管理 &gt; 云服务台账 &gt; 创建/导入
                </div>
              </div>
            </div>
          </div>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/inventories')}>
            返回列表
          </Button>
        </div>
      </Card>

      {/* 内容Tab */}
      <Card style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', gap: 8 }}>
          <Button
            onClick={() => setActiveTab('manual')}
            style={{
              padding: '12px 24px',
              borderRadius: 8,
              background: activeTab === 'manual' ? 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)' : 'transparent',
              color: activeTab === 'manual' ? 'white' : '#666',
              border: activeTab === 'manual' ? 'none' : '1px solid #d9d9d9',
            }}
          >
            <Space>
              <PlusOutlined />
              手动录入
            </Space>
          </Button>
          <Button
            onClick={() => setActiveTab('import')}
            style={{
              padding: '12px 24px',
              borderRadius: 8,
              background: activeTab === 'import' ? 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)' : 'transparent',
              color: activeTab === 'import' ? 'white' : '#666',
              border: activeTab === 'import' ? 'none' : '1px solid #d9d9d9',
            }}
          >
            <Space>
              <UploadOutlined />
              批量导入
            </Space>
          </Button>
        </div>
      </Card>

      {/* 手动录入 */}
      {activeTab === 'manual' && (
        <Form form={form} layout="vertical">
          <Card style={{ marginBottom: 24 }}>
            <Alert
              message="云服务台账分为 IAAS资源（计算/网络/存储/备份）和 PAAS软件（中间件/数据库/缓存）两大类。创建后可在应用系统台账中关联使用。"
              type="info"
              showIcon
              icon={<InfoCircleOutlined />}
              style={{ marginBottom: 24 }}
            />

            <Divider orientation="left" style={{ fontSize: 16, fontWeight: 600 }}>
              关联应用系统
            </Divider>

            <Form.Item
              name="appId"
              label="选择应用系统"
              rules={[{ required: true, message: '请选择应用系统' }]}
            >
              <Select placeholder="请选择应用系统">
                {mockApps.map((app) => (
                  <Option key={app.id} value={app.id}>
                    {app.name}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            <Divider orientation="left" style={{ fontSize: 16, fontWeight: 600 }}>
              选择资源类型
            </Divider>

            {renderResourceTypeCards()}

            {renderResourceForm()}
          </Card>

          {/* 表单操作 */}
          <Card>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
              <Button onClick={() => navigate('/inventories')}>取消</Button>
              <Button icon={<SaveOutlined />} onClick={handleSaveDraft}>
                保存草稿
              </Button>
              <Button
                type="primary"
                onClick={handleSubmit}
                style={{
                  background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
                  border: 'none',
                }}
              >
                创建资源台账
              </Button>
            </div>
          </Card>
        </Form>
      )}

      {/* 批量导入 */}
      {activeTab === 'import' && (
        <Card>
          <Alert
            message="支持通过Excel文件批量导入云服务台账数据。请下载模板文件，按模板格式填写后上传。"
            type="info"
            showIcon
            icon={<InfoCircleOutlined />}
            style={{ marginBottom: 24 }}
          />

          <Form.Item
            name="importType"
            label="选择导入资源类型"
            rules={[{ required: true, message: '请选择导入类型' }]}
          >
            <Select placeholder="请选择导入类型">
              <Option value="compute">计算资源（ECS/VM）</Option>
              <Option value="network">网络资源（VPC/SLB/EIP）</Option>
              <Option value="storage">存储资源（OSS/NAS/EBS）</Option>
              <Option value="software">PAAS软件（RDS/Redis/MQ）</Option>
              <Option value="all">全部资源类型</Option>
            </Select>
          </Form.Item>

          <Dragger
            fileList={uploadedFiles}
            onChange={({ fileList }) => setUploadedFiles(fileList)}
            style={{ padding: 40, marginBottom: 24 }}
          >
            <p className="ant-upload-drag-icon">
              <UploadOutlined style={{ fontSize: 48, color: '#11998e' }} />
            </p>
            <p className="ant-upload-text">点击或拖拽Excel文件到此处上传</p>
            <p className="ant-upload-hint">支持 .xlsx, .xls 格式文件，单个文件不超过 10MB</p>
          </Dragger>

          <div style={{ textAlign: 'center', paddingTop: 16, borderTop: '1px solid #e8e8e8' }}>
            <Button type="link" icon={<DownloadOutlined />}>
              下载导入模板
            </Button>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 24 }}>
            <Button onClick={() => navigate('/inventories')}>取消</Button>
            <Button
              type="primary"
              style={{
                background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
                border: 'none',
              }}
            >
              开始导入
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}

export default CloudInventoryCreate;
