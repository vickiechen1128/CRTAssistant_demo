/**
 * ApprovalFilesStep 组件
 * Step 2: 上传审批材料
 */
import React from 'react';
import { Upload, Button, List, Tag, message } from 'antd';
import { UploadOutlined, FilePdfOutlined, FileImageOutlined, DeleteOutlined } from '@ant-design/icons';
import { usePlanStore } from '../../store';

/**
 * 审批材料上传步骤组件
 */
const ApprovalFilesStep = () => {
  const { creationData, addApprovalFile, removeApprovalFile } = usePlanStore();
  const { approvalFiles } = creationData;

  // 文件上传配置
  const uploadProps = {
    name: 'file',
    action: '/api/upload', // 实际上传地址
    headers: {
      authorization: 'authorization-text',
    },
    beforeUpload: (file) => {
      // 文件大小限制 20MB
      const isLt20M = file.size / 1024 / 1024 < 20;
      if (!isLt20M) {
        message.error('文件大小不能超过 20MB');
        return Upload.LIST_IGNORE;
      }
      
      // 文件类型限制
      const isValidType = 
        file.type === 'application/pdf' ||
        file.type.startsWith('image/');
      if (!isValidType) {
        message.error('只支持 PDF 和图片文件');
        return Upload.LIST_IGNORE;
      }
      
      return true;
    },
    onChange: (info) => {
      if (info.file.status === 'done') {
        // 上传成功，添加到列表
        const response = info.file.response;
        let fileDetail;
        
        // 处理后端返回的响应格式
        if (response && response.success && response.data) {
          // 标准响应格式: { success: true, data: { ... } }
          fileDetail = {
            file_name: response.data.file_name,
            file_url: response.data.file_url,
            file_size: response.data.file_size,
            uploaded_at: response.data.uploaded_at,
            file_id: response.data.file_id,
          };
        } else if (response && response.file_url) {
          // 直接返回文件信息的格式
          fileDetail = {
            file_name: response.file_name || info.file.name,
            file_url: response.file_url,
            file_size: response.file_size || info.file.size,
            uploaded_at: response.uploaded_at || new Date().toISOString(),
            file_id: response.file_id || info.file.uid,
          };
        } else {
          // 使用本地信息作为后备
          fileDetail = {
            file_name: info.file.name,
            file_url: URL.createObjectURL(info.file.originFileObj),
            file_size: info.file.size,
            uploaded_at: new Date().toISOString(),
            file_id: info.file.uid,
          };
        }
        
        addApprovalFile(fileDetail);
        message.success(`${info.file.name} 上传成功`);
      } else if (info.file.status === 'error') {
        const errorMsg = info.file.response?.message || info.file.error?.message || '未知错误';
        message.error(`${info.file.name} 上传失败: ${errorMsg}`);
      }
    },
    showUploadList: false,
  };

  // 格式化文件大小
  const formatFileSize = (size) => {
    if (size < 1024) return `${size} B`;
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(2)} KB`;
    return `${(size / (1024 * 1024)).toFixed(2)} MB`;
  };

  // 获取文件图标
  const getFileIcon = (fileName) => {
    if (fileName?.toLowerCase().endsWith('.pdf')) {
      return <FilePdfOutlined style={{ color: '#ff4d4f', fontSize: 24 }} />;
    }
    return <FileImageOutlined style={{ color: '#52c41a', fontSize: 24 }} />;
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h4>上传审批材料</h4>
        <p style={{ color: '#666' }}>
          请上传会议纪要、审批邮件等材料，支持 PDF、图片格式，单个文件不超过 20MB
        </p>
      </div>

      <Upload.Dragger {...uploadProps} style={{ marginBottom: 24 }}>
        <p className="ant-upload-drag-icon">
          <UploadOutlined />
        </p>
        <p className="ant-upload-text">点击或拖拽文件到此处上传</p>
        <p className="ant-upload-hint">
          支持 PDF、JPG、PNG 格式，单个文件不超过 20MB
        </p>
      </Upload.Dragger>

      {approvalFiles.length > 0 && (
        <div>
          <h4>已上传文件</h4>
          <List
            bordered
            dataSource={approvalFiles}
            renderItem={(file, index) => (
              <List.Item
                actions={[
                  <Button
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => removeApprovalFile(file.file_url)}
                  >
                    删除
                  </Button>,
                ]}
              >
                <List.Item.Meta
                  avatar={getFileIcon(file.file_name)}
                  title={file.file_name}
                  description={
                    <span>
                      <Tag>{formatFileSize(file.file_size)}</Tag>
                      <span style={{ color: '#999' }}>
                        {new Date(file.uploaded_at).toLocaleString('zh-CN')}
                      </span>
                    </span>
                  }
                />
              </List.Item>
            )}
          />
        </div>
      )}

      {approvalFiles.length === 0 && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
          请至少上传一个审批材料
        </div>
      )}
    </div>
  );
};

export default ApprovalFilesStep;
