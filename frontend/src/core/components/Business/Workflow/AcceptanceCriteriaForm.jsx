/**
 * 验收标准表单组件
 * 用于创建和编辑验收标准
 * 注意：此组件不使用 Form，避免嵌套表单问题
 */

import React, { useState } from 'react';
import {
  Input,
  Switch,
  Select,
  Button,
  Space,
  Card,
  List,
  Popconfirm,
  message,
  Row,
  Col
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
  CheckOutlined,
  CloseOutlined
} from '@ant-design/icons';

const { TextArea } = Input;
const { Option } = Select;

const AcceptanceCriteriaForm = ({
  value = [],
  onChange,
  readOnly = false,
  showImport = false,
  onImport
}) => {
  const [editingIndex, setEditingIndex] = useState(-1);
  const [criteriaList, setCriteriaList] = useState(value);

  // 当前编辑的数据
  const [editForm, setEditForm] = useState({
    content: '',
    criteria_type: 'manual',
    is_required: true,
    auto_check_script: ''
  });

  // 验收类型选项
  const criteriaTypes = [
    { value: 'manual', label: '人工验收' },
    { value: 'auto', label: '自动验收' }
  ];

  // 添加验收标准
  const handleAdd = () => {
    setEditingIndex(criteriaList.length);
    setEditForm({
      content: '',
      criteria_type: 'manual',
      is_required: true,
      auto_check_script: ''
    });
  };

  // 编辑验收标准
  const handleEdit = (index) => {
    setEditingIndex(index);
    const item = criteriaList[index];
    setEditForm({
      content: item.content || '',
      criteria_type: item.criteria_type || 'manual',
      is_required: item.is_required !== false,
      auto_check_script: item.auto_check_script || ''
    });
  };

  // 保存验收标准
  const handleSave = () => {
    // 验证
    if (!editForm.content.trim()) {
      message.error('请输入验收内容');
      return;
    }

    if (editForm.criteria_type === 'auto' && !editForm.auto_check_script.trim()) {
      message.error('请输入自动检查脚本');
      return;
    }

    const newList = [...criteriaList];

    if (editingIndex >= 0 && editingIndex < newList.length) {
      // 更新现有项
      newList[editingIndex] = { ...newList[editingIndex], ...editForm };
    } else {
      // 添加新项
      newList.push({
        id: Date.now(), // 临时ID
        ...editForm,
        display_order: newList.length
      });
    }

    setCriteriaList(newList);
    onChange?.(newList);
    setEditingIndex(-1);
    setEditForm({
      content: '',
      criteria_type: 'manual',
      is_required: true,
      auto_check_script: ''
    });
    message.success('保存成功');
  };

  // 取消编辑
  const handleCancel = () => {
    setEditingIndex(-1);
    setEditForm({
      content: '',
      criteria_type: 'manual',
      is_required: true,
      auto_check_script: ''
    });
  };

  // 删除验收标准
  const handleDelete = (index) => {
    const newList = criteriaList.filter((_, i) => i !== index);
    // 重新排序
    newList.forEach((item, i) => {
      item.display_order = i;
    });
    setCriteriaList(newList);
    onChange?.(newList);
    message.success('删除成功');
  };

  // 从模板导入
  const handleImport = () => {
    onImport?.();
  };

  // 渲染编辑表单
  const renderEditForm = () => (
    <Card
      size="small"
      title={editingIndex >= 0 && editingIndex < criteriaList.length ? '编辑验收标准' : '添加验收标准'}
      style={{ marginBottom: 16 }}
    >
      <div style={{ marginBottom: 16 }}>
        <label style={{ display: 'block', marginBottom: 8 }}>
          <span style={{ color: '#ff4d4f' }}>*</span> 验收内容
        </label>
        <TextArea
          rows={2}
          placeholder="请输入验收标准内容，例如：服务器已按标准配置分区"
          value={editForm.content}
          onChange={(e) => setEditForm({ ...editForm, content: e.target.value })}
        />
      </div>

      <div style={{ marginBottom: 16 }}>
        <label style={{ display: 'block', marginBottom: 8 }}>
          <span style={{ color: '#ff4d4f' }}>*</span> 验收类型
        </label>
        <Select
          placeholder="选择验收类型"
          value={editForm.criteria_type}
          onChange={(value) => setEditForm({ ...editForm, criteria_type: value })}
          style={{ width: '100%' }}
        >
          {criteriaTypes.map(type => (
            <Option key={type.value} value={type.value}>{type.label}</Option>
          ))}
        </Select>
      </div>

      {editForm.criteria_type === 'auto' && (
        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', marginBottom: 8 }}>
            <span style={{ color: '#ff4d4f' }}>*</span> 自动检查脚本
          </label>
          <TextArea
            rows={4}
            placeholder="请输入自动检查脚本内容"
            value={editForm.auto_check_script}
            onChange={(e) => setEditForm({ ...editForm, auto_check_script: e.target.value })}
          />
        </div>
      )}

      <div style={{ marginBottom: 16 }}>
        <label style={{ display: 'block', marginBottom: 8 }}>是否必填</label>
        <Switch
          checked={editForm.is_required}
          onChange={(checked) => setEditForm({ ...editForm, is_required: checked })}
          checkedChildren="是"
          unCheckedChildren="否"
        />
      </div>

      <Space>
        <Button type="primary" icon={<CheckOutlined />} onClick={handleSave}>
          保存
        </Button>
        <Button icon={<CloseOutlined />} onClick={handleCancel}>
          取消
        </Button>
      </Space>
    </Card>
  );

  return (
    <div className="acceptance-criteria-form">
      {/* 操作按钮 */}
      {!readOnly && (
        <div className="form-actions" style={{ marginBottom: 16 }}>
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAdd}
              disabled={editingIndex >= 0}
            >
              添加验收标准
            </Button>
            {showImport && (
              <Button onClick={handleImport}>
                从模板导入
              </Button>
            )}
          </Space>
        </div>
      )}

      {/* 编辑表单 */}
      {editingIndex >= 0 && renderEditForm()}

      {/* 验收标准列表 */}
      <List
        className="criteria-list"
        itemLayout="horizontal"
        dataSource={criteriaList}
        renderItem={(item, index) => (
          <List.Item
            actions={
              !readOnly
                ? [
                    <Button
                      type="text"
                      icon={<EditOutlined />}
                      onClick={() => handleEdit(index)}
                      disabled={editingIndex >= 0}
                    />,
                    <Popconfirm
                      title="确定要删除这个验收标准吗？"
                      onConfirm={() => handleDelete(index)}
                      okText="确定"
                      cancelText="取消"
                    >
                      <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        disabled={editingIndex >= 0}
                      />
                    </Popconfirm>
                  ]
                : []
            }
          >
            <List.Item.Meta
              title={
                <Space>
                  <span>{index + 1}. {item.content}</span>
                  {item.is_required && <span style={{ color: '#ff4d4f' }}>*</span>}
                </Space>
              }
              description={
                <Space size={16}>
                  <span>
                    类型: {item.criteria_type === 'auto' ? '自动验收' : '人工验收'}
                  </span>
                  {item.criteria_type === 'auto' && item.auto_check_script && (
                    <span style={{ color: '#1890ff' }}>已配置脚本</span>
                  )}
                </Space>
              }
            />
          </List.Item>
        )}
        locale={{ emptyText: '暂无验收标准' }}
      />
    </div>
  );
};

export default AcceptanceCriteriaForm;
