/**
 * 系统及软件账号台账创建页面
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
  Radio,
  DatePicker,
  Upload,
  message,
} from 'antd';
import {
  ArrowLeftOutlined,
  PlusOutlined,
  SaveOutlined,
  SafetyOutlined,
  InfoCircleOutlined,
  UploadOutlined,
  DownloadOutlined,
  DesktopOutlined,
  SettingOutlined,
} from '@ant-design/icons';

const { TextArea } = Input;
const { Option } = Select;
const { Dragger } = Upload;

// 账户类型选项
const accountTypes = [
  {
    value: 'system',
    label: '系统账户',
    icon: <DesktopOutlined style={{ fontSize: 32 }} />,
    desc: '操作系统层面的账户',
  },
  {
    value: 'software',
    label: '软件账户',
    icon: <SettingOutlined style={{ fontSize: 32 }} />,
    desc: '应用/数据库层面的账户',
  },
];

// 权限级别选项
const permissionLevels = [
  { value: 'admin', label: '管理员', color: '#ff4d4f' },
  { value: 'readwrite', label: '读写', color: '#faad14' },
  { value: 'readonly', label: '只读', color: '#52c41a' },
  { value: 'execute', label: '执行', color: '#1890ff' },
];

// 模拟应用系统数据
const mockApps = [
  { id: 'APP-001', name: '订单管理系统' },
  { id: 'APP-002', name: '支付系统' },
  { id: 'APP-003', name: '用户中心' },
  { id: 'APP-004', name: '库存管理系统' },
];

// 模拟服务器数据
const mockServers = [
  { id: 'ECS-001', name: 'order-server-01', ip: '192.168.1.101' },
  { id: 'ECS-002', name: 'payment-server-01', ip: '192.168.1.102' },
  { id: 'ECS-003', name: 'user-server-01', ip: '192.168.1.103' },
];

function AccountInventoryCreate() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [activeTab, setActiveTab] = useState('manual');
  const [selectedAccountType, setSelectedAccountType] = useState('system');
  const [selectedPermission, setSelectedPermission] = useState('admin');
  const [uploadedFiles, setUploadedFiles] = useState([]);

  // 提交表单
  const handleSubmit = () => {
    form.validateFields().then((values) => {
      console.log('表单数据:', { ...values, accountType: selectedAccountType, permission: selectedPermission });
      message.success('账号台账创建成功！');
      navigate('/inventories');
    });
  };

  // 保存草稿
  const handleSaveDraft = () => {
    message.success('草稿已保存');
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
                  background: 'linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%)',
                  borderRadius: 12,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 24,
                  color: 'white',
                }}
              >
                <SafetyOutlined />
              </div>
              <div>
                <div>创建与导入系统及软件账号台账</div>
                <div style={{ fontSize: 13, color: '#666', fontWeight: 'normal', marginTop: 4 }}>
                  台账管理 &gt; 系统及软件账号台账 &gt; 创建/导入
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
              background: activeTab === 'manual' ? 'linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%)' : 'transparent',
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
              background: activeTab === 'import' ? 'linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%)' : 'transparent',
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
              message="系统及软件账号台账记录服务器和软件的账户信息，包括权限级别、持有人、有效期、密码修改周期等安全相关信息。"
              type="info"
              showIcon
              icon={<InfoCircleOutlined />}
              style={{ marginBottom: 24 }}
            />

            <Divider orientation="left" style={{ fontSize: 16, fontWeight: 600 }}>
              关联信息
            </Divider>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
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

              <Form.Item
                name="serverId"
                label="选择服务器"
                rules={[{ required: true, message: '请选择服务器' }]}
              >
                <Select placeholder="请选择服务器">
                  {mockServers.map((server) => (
                    <Option key={server.id} value={server.id}>
                      {server.name} ({server.ip})
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </div>

            <Divider orientation="left" style={{ fontSize: 16, fontWeight: 600 }}>
              账户类型
            </Divider>

            <div style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
              {accountTypes.map((type) => (
                <Card
                  key={type.value}
                  hoverable
                  onClick={() => setSelectedAccountType(type.value)}
                  style={{
                    flex: 1,
                    border: selectedAccountType === type.value ? '2px solid #fc4a1a' : '2px solid #e8e8e8',
                    background: selectedAccountType === type.value ? 'linear-gradient(135deg, #fff7e6 0%, #fff2e8 100%)' : 'white',
                    cursor: 'pointer',
                    textAlign: 'center',
                  }}
                  bodyStyle={{ padding: 24 }}
                >
                  <div style={{ color: '#fc4a1a', marginBottom: 8 }}>{type.icon}</div>
                  <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>{type.label}</div>
                  <div style={{ fontSize: 12, color: '#999' }}>{type.desc}</div>
                </Card>
              ))}
            </div>

            <Divider orientation="left" style={{ fontSize: 16, fontWeight: 600 }}>
              账户信息
            </Divider>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
              <Form.Item
                name="accountName"
                label="账户名"
                rules={[{ required: true, message: '请输入账户名' }]}
              >
                <Input placeholder="如：root、order_app" />
              </Form.Item>

              <Form.Item
                label="权限级别"
                required
              >
                <div style={{ display: 'flex', gap: 12 }}>
                  {permissionLevels.map((perm) => (
                    <div
                      key={perm.value}
                      onClick={() => setSelectedPermission(perm.value)}
                      style={{
                        flex: 1,
                        padding: '12px',
                        border: `2px solid ${selectedPermission === perm.value ? perm.color : '#e8e8e8'}`,
                        borderRadius: 8,
                        textAlign: 'center',
                        cursor: 'pointer',
                        background: selectedPermission === perm.value ? `${perm.color}15` : 'white',
                        color: selectedPermission === perm.value ? perm.color : '#666',
                        fontWeight: selectedPermission === perm.value ? 500 : 'normal',
                        fontSize: 13,
                      }}
                    >
                      {perm.label}
                    </div>
                  ))}
                </div>
              </Form.Item>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
              <Form.Item
                name="holderName"
                label="持有人姓名"
                rules={[{ required: true, message: '请输入持有人姓名' }]}
              >
                <Input placeholder="持有人姓名" />
              </Form.Item>

              <Form.Item name="department" label="持有人部门">
                <Input placeholder="如：运维部" />
              </Form.Item>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
              <Form.Item name="passwordCycle" label="密码修改周期(天)">
                <Input type="number" defaultValue={90} />
              </Form.Item>

              <Form.Item
                name="expiryDate"
                label="有效期结束"
                rules={[{ required: true, message: '请选择有效期结束时间' }]}
              >
                <DatePicker showTime style={{ width: '100%' }} />
              </Form.Item>
            </div>

            <Form.Item name="remark" label="备注">
              <TextArea rows={3} placeholder="账户用途说明、特殊权限说明等" />
            </Form.Item>
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
                  background: 'linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%)',
                  border: 'none',
                }}
              >
                创建账号台账
              </Button>
            </div>
          </Card>
        </Form>
      )}

      {/* 批量导入 */}
      {activeTab === 'import' && (
        <Card>
          <Alert
            message="支持通过Excel文件批量导入系统及软件账号台账数据。请下载模板文件，按模板格式填写后上传。"
            type="info"
            showIcon
            icon={<InfoCircleOutlined />}
            style={{ marginBottom: 24 }}
          />

          <Form.Item
            name="importType"
            label="选择导入账户类型"
            rules={[{ required: true, message: '请选择导入类型' }]}
          >
            <Select placeholder="请选择导入类型">
              <Option value="system">系统账户（OS层：root、admin等）</Option>
              <Option value="software">软件账户（应用层：数据库账户、应用账户等）</Option>
              <Option value="all">全部账户类型</Option>
            </Select>
          </Form.Item>

          <Dragger
            fileList={uploadedFiles}
            onChange={({ fileList }) => setUploadedFiles(fileList)}
            style={{ padding: 40, marginBottom: 24 }}
          >
            <p className="ant-upload-drag-icon">
              <UploadOutlined style={{ fontSize: 48, color: '#fc4a1a' }} />
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
                background: 'linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%)',
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

export default AccountInventoryCreate;
