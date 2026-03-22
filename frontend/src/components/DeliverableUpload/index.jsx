/**
 * 交付物上传组件
 * 支持Excel/Word/PDF/脚本文件上传
 */

import React, { useState, useEffect } from 'react';
import { Upload, Button, message, List, Tag, Space, Modal, Spin } from 'antd';
import { UploadOutlined, FileOutlined, EyeOutlined, DeleteOutlined, DownloadOutlined } from '@ant-design/icons';
import { deliverableApi } from '../../api/deliverable';

// 文件类型映射
const fileTypeMap = {
  'application/pdf': { color: 'red', label: 'PDF' },
  'application/msword': { color: 'blue', label: 'Word' },
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': { color: 'blue', label: 'Word' },
  'application/vnd.ms-excel': { color: 'green', label: 'Excel' },
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': { color: 'green', label: 'Excel' },
  'text/plain': { color: 'default', label: '文本' },
  'application/x-sh': { color: 'purple', label: '脚本' },
  'text/x-python': { color: 'purple', label: 'Python' },
};

// 获取文件类型显示
const getFileTypeDisplay = (mimeType, fileName) => {
  // 先根据mimeType匹配
  if (fileTypeMap[mimeType]) {
    return fileTypeMap[mimeType];
  }
  // 根据文件扩展名匹配
  const ext = fileName?.split('.').pop()?.toLowerCase();
  const extMap = {
    'pdf': { color: 'red', label: 'PDF' },
    'doc': { color: 'blue', label: 'Word' },
    'docx': { color: 'blue', label: 'Word' },
    'xls': { color: 'green', label: 'Excel' },
    'xlsx': { color: 'green', label: 'Excel' },
    'txt': { color: 'default', label: '文本' },
    'sh': { color: 'purple', label: '脚本' },
    'py': { color: 'purple', label: 'Python' },
    'log': { color: 'orange', label: '日志' },
  };
  return extMap[ext] || { color: 'default', label: '文件' };
};

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * 交付物上传组件
 * @param {Object} props
 * @param {number} props.checklistItemId - 关联的检查项ID
 * @param {boolean} props.readOnly - 是否只读模式
 * @param {number} props.maxCount - 最大上传数量
 * @param {number} props.maxSize - 最大文件大小(MB)
 * @param {Function} props.onUploadSuccess - 上传成功回调
 */
function DeliverableUpload({
  checklistItemId,
  readOnly = false,
  maxCount = 10,
  maxSize = 50,
  onUploadSuccess,
}) {
  const [fileList, setFileList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewFile, setPreviewFile] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  // 加载交付物列表
  useEffect(() => {
    if (checklistItemId) {
      fetchDeliverables();
    }
  }, [checklistItemId]);

  const fetchDeliverables = async () => {
    setLoading(true);
    try {
      const response = await deliverableApi.list({ checklist_item_id: checklistItemId });
      const items = response.data.items || [];
      // 转换为Upload组件需要的格式
      const formattedFiles = items.map(item => ({
        uid: item.id.toString(),
        id: item.id,
        name: item.file_name,
        size: item.file_size,
        type: getMimeType(item.file_type),
        file_type: item.file_type,
        description: item.description,
        uploader: item.uploader,
        uploaded_at: item.uploaded_at,
        status: 'done',
      }));
      setFileList(formattedFiles);
    } catch (error) {
      message.error('获取交付物列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 根据文件类型获取MIME类型
  const getMimeType = (fileType) => {
    const typeMap = {
      'pdf': 'application/pdf',
      'word': 'application/msword',
      'excel': 'application/vnd.ms-excel',
      'script': 'text/plain',
      'log': 'text/plain',
    };
    return typeMap[fileType] || 'application/octet-stream';
  };

  // 上传前检查
  const beforeUpload = (file) => {
    const isLtMaxSize = file.size / 1024 / 1024 < maxSize;
    if (!isLtMaxSize) {
      message.error(`文件大小不能超过 ${maxSize}MB!`);
      return Upload.LIST_IGNORE;
    }
    
    if (fileList.length >= maxCount) {
      message.error(`最多只能上传 ${maxCount} 个文件`);
      return Upload.LIST_IGNORE;
    }
    
    return true;
  };

  // 自定义上传
  const customRequest = async ({ file, onSuccess, onError }) => {
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('checklist_item_id', checklistItemId);
      
      const response = await deliverableApi.upload(formData);
      message.success('上传成功');
      onSuccess?.(response.data);
      onUploadSuccess?.(response.data);
      // 刷新列表
      fetchDeliverables();
    } catch (error) {
      message.error('上传失败: ' + (error.message || '未知错误'));
      onError?.(error);
    } finally {
      setUploading(false);
    }
  };

  // 预览文件
  const handlePreview = async (file) => {
    setPreviewFile(file);
    setPreviewVisible(true);
    
    // 如果是PDF或图片，加载内容
    if (file.type === 'application/pdf' || file.type?.startsWith('image/')) {
      setPreviewLoading(true);
      try {
        const response = await deliverableApi.download(file.id);
        const blob = new Blob([response]);
        const url = URL.createObjectURL(blob);
        setPreviewFile({ ...file, url });
      } catch (error) {
        message.error('加载文件失败');
      } finally {
        setPreviewLoading(false);
      }
    }
  };

  // 下载文件
  const handleDownload = async (file) => {
    try {
      const response = await deliverableApi.download(file.id);
      const blob = new Blob([response]);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = file.name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      message.error('下载失败');
    }
  };

  // 删除文件
  const handleDelete = (file) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除文件 "${file.name}" 吗？`,
      onOk: async () => {
        try {
          await deliverableApi.delete(file.id);
          message.success('删除成功');
          fetchDeliverables();
        } catch (error) {
          message.error('删除失败');
        }
      },
    });
  };

  // 上传配置
  const uploadProps = {
    name: 'file',
    customRequest,
    beforeUpload,
    fileList,
    multiple: true,
    maxCount,
    showUploadList: false,
    disabled: uploading || readOnly,
  };

  return (
    <Spin spinning={loading}>
      <div>
        {/* 上传按钮 */}
        {!readOnly && (
          <div style={{ marginBottom: 16 }}>
            <Upload {...uploadProps}>
              <Button icon={<UploadOutlined />} loading={uploading}>
                上传交付物
              </Button>
            </Upload>
            <span style={{ marginLeft: 8, color: '#999', fontSize: 12 }}>
              支持 PDF/Word/Excel/文本/脚本，单个文件最大 {maxSize}MB，最多 {maxCount} 个
            </span>
          </div>
        )}

        {/* 文件列表 */}
        <List
          bordered
          dataSource={fileList}
          locale={{ emptyText: '暂无交付物' }}
          renderItem={(file) => {
            const typeDisplay = getFileTypeDisplay(file.type, file.name);
            return (
              <List.Item
                actions={[
                  <Button
                    key="preview"
                    type="text"
                    size="small"
                    icon={<EyeOutlined />}
                    onClick={() => handlePreview(file)}
                  >
                    预览
                  </Button>,
                  <Button
                    key="download"
                    type="text"
                    size="small"
                    icon={<DownloadOutlined />}
                    onClick={() => handleDownload(file)}
                  >
                    下载
                  </Button>,
                  !readOnly && (
                    <Button
                      key="delete"
                      type="text"
                      size="small"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={() => handleDelete(file)}
                    >
                      删除
                    </Button>
                  ),
                ].filter(Boolean)}
              >
                <List.Item.Meta
                  avatar={<FileOutlined style={{ fontSize: 24, color: '#1890ff' }} />}
                  title={
                    <Space>
                      <span>{file.name}</span>
                      <Tag color={typeDisplay.color}>{typeDisplay.label}</Tag>
                    </Space>
                  }
                  description={
                    <Space size={16}>
                      <span>大小: {formatFileSize(file.size)}</span>
                      <span>上传人: {file.uploader?.real_name || '-'}</span>
                      <span>上传时间: {file.uploaded_at || '-'}</span>
                      {file.description && (
                        <span style={{ color: '#666' }}>备注: {file.description}</span>
                      )}
                    </Space>
                  }
                />
              </List.Item>
            );
          }}
        />

        {/* 预览弹窗 */}
        <Modal
          open={previewVisible}
          title={previewFile?.name}
          footer={null}
          onCancel={() => {
            setPreviewVisible(false);
            setPreviewFile(null);
          }}
          width={800}
        >
          <Spin spinning={previewLoading}>
            <div style={{ minHeight: 200, textAlign: 'center' }}>
              {previewFile?.type?.startsWith('image/') ? (
                <img
                  alt={previewFile.name}
                  style={{ maxWidth: '100%' }}
                  src={previewFile.url}
                />
              ) : previewFile?.type === 'application/pdf' ? (
                <iframe
                  src={previewFile.url}
                  style={{ width: '100%', height: 500 }}
                  title={previewFile.name}
                />
              ) : (
                <div style={{ padding: 40 }}>
                  <FileOutlined style={{ fontSize: 64, color: '#ccc' }} />
                  <p>该文件类型暂不支持在线预览</p>
                  <Button
                    type="primary"
                    icon={<DownloadOutlined />}
                    onClick={() => handleDownload(previewFile)}
                  >
                    下载查看
                  </Button>
                </div>
              )}
            </div>
          </Spin>
        </Modal>
      </div>
    </Spin>
  );
}

export default DeliverableUpload;
