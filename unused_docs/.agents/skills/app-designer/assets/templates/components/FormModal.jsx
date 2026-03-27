/**
 * 表单弹窗组件模板
 * 支持: 创建/编辑模式、表单验证、加载状态
 */

import { useState, useEffect } from 'react';

export function FormModal({
  isOpen,
  onClose,
  onSubmit,
  title = '表单',
  initialData = {},
  loading = false,
  children
}) {
  const [formData, setFormData] = useState(initialData);

  useEffect(() => {
    setFormData(initialData);
  }, [initialData, isOpen]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit?.(formData);
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{title}</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {typeof children === 'function' 
              ? children(formData, handleChange) 
              : children
            }
          </div>
          
          <div className="modal-footer">
            <button 
              type="button" 
              className="btn btn-secondary" 
              onClick={onClose}
              disabled={loading}
            >
              取消
            </button>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? '提交中...' : '确定'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// 使用示例
export function FormModalExample() {
  const [isOpen, setIsOpen] = useState(false);

  const handleSubmit = async (data) => {
    console.log('提交数据:', data);
    // await api.createItem(data);
    setIsOpen(false);
  };

  return (
    <>
      <button className="btn btn-primary" onClick={() => setIsOpen(true)}>
        新建
      </button>
      
      <FormModal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        onSubmit={handleSubmit}
        title="新建 Item"
        initialData={{ name: '', description: '' }}
      >
        {(formData, handleChange) => (
          <>
            <div className="form-group">
              <label>名称 *</label>
              <input
                type="text"
                className="input"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>描述</label>
              <textarea
                className="textarea"
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                rows={3}
              />
            </div>
          </>
        )}
      </FormModal>
    </>
  );
}
