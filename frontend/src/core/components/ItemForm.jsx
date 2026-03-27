import { useState } from 'react';

/**
 * Item 创建表单组件
 */
export function ItemForm({ onSubmit, loading }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    
    onSubmit({ title: title.trim(), description: description.trim() });
    setTitle('');
    setDescription('');
  };

  return (
    <form onSubmit={handleSubmit} className="card">
      <div className="form-group">
        <label htmlFor="title">标题 *</label>
        <input
          id="title"
          type="text"
          className="input"
          placeholder="输入标题..."
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={loading}
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="description">描述</label>
        <textarea
          id="description"
          className="textarea"
          placeholder="输入描述（可选）..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          disabled={loading}
          rows={3}
        />
      </div>
      
      <div className="btn-row">
        <button 
          type="submit" 
          className="btn btn-primary"
          disabled={loading || !title.trim()}
        >
          {loading ? '提交中...' : '添加 Item'}
        </button>
      </div>
    </form>
  );
}
