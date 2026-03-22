/**
 * 交付物审核组件
 * 用于审核检查项的交付物
 */

import React, { useState } from 'react';
import { Modal, Button, Space, Tag, List, Radio, Input, message } from 'antd';
import { FileOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { checklistApi } from '../../api/checklist';

const { TextArea } = Input;

/**
 * 交付物审核组件
 * @param {Object} props
 * @param {boolean} props.visible - 是否显示
 * @param {number} props.checklistItemId - 检查项ID
 * @param {string} props.checklistItemName - 检查项名称
 * @param {Array} props.deliverables - 交付物列表
 * @param {Function} props.onCancel - 取消回调
 * @param {Function} props.onSuccess - 成功回调
 */
function DeliverableReview({
  visible,
  checklistItemId,
  checklistItemName,
  deliverables = [],
  onCancel,
  onSuccess,
}) {
  const [status, setStatus] = useState('passed');
  const [remark, setRemark] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!checklistItemId) return;
    
    setSubmitting(true);
    try {
      await checklistApi.verify(checklistItemId, {
        status,
        remark,
      });
      message.success('审核完成');
      onSuccess?.();
    } catch (error) {
      message.error('审核失败');
    } finally {
      setSubmitting(false);
    }
  };

  // 格式化文件大小
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Modal
      title={`审核交付物 - ${checklistItemName}`}
      open={visible}
      onCancel={onCancel}
      width={700}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          取消
        </Button>,
        <Button
          key="submit"
          type="primary"
          loading={submitting}
          onClick={handleSubmit}
        >
          提交审核
        </Button>,
      ]}
    >
      <div style={{ marginBottom: 24 }}>
        <h4>交付物列表</h4>
        <List
          bordered
          dataSource={deliverables}
          locale={{ emptyText: '暂无交付物' }}
          renderItem={(file) => (
            <List.Item
              actions={[
                <Button type="link" size="small" onClick={() => window.open(`/api/deliverables/${file.id}`, '_blank')}>
                  下载
                </Button>,
              ]}
            >
              <List.Item.Meta
                avatar={<FileOutlined style={{ fontSize: 24, color: '#1890ff' }} />}
                title={file.file_name}
                description={
                  <Space size={16}>
                    <span>大小: {formatFileSize(file.file_size)}</span>
                    <span>上传人: {file.uploader?.real_name || '-'}</span>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      </div>

      <div style={{ marginBottom: 16 }}>
        <h4>审核结果</h4>
        <Radio.Group value={status} onChange={(e) => setStatus(e.target.value)}>
          <Radio.Button value="passed">
            <CheckCircleOutlined style={{ color: '#52c41a' }} /> 通过
          </Radio.Button>
          <Radio.Button value="rejected">
            <CloseCircleOutlined style={{ color: '#ff4d4f' }} /> 驳回
          </Radio.Button>
        </Radio.Group>
      </div>

      <div>
        <h4>审核备注</h4>
        <TextArea
          rows={4}
          value={remark}
          onChange={(e) => setRemark(e.target.value)}
          placeholder="请输入审核意见..."
        />
      </div>
    </Modal>
  );
}

export default DeliverableReview;
