/**
 * Item 列表组件
 */
export function ItemList({ items, onToggle, onDelete, loading }) {
  if (items.length === 0) {
    return (
      <div className="card empty-state">
        <p>暂无数据，点击上方按钮添加</p>
      </div>
    );
  }

  return (
    <div className="items-list">
      {items.map(item => (
        <div 
          key={item.id} 
          className={`item-card ${item.status === 'completed' ? 'completed' : ''}`}
        >
          <div className="item-content">
            <h3>{item.title}</h3>
            {item.description && <p>{item.description}</p>}
            <div className="meta">
              <span className={`status-badge ${item.status}`}>
                {item.status === 'completed' ? '已完成' : '待处理'}
              </span>
              <span> | 创建: {new Date(item.created_at).toLocaleString('zh-CN')}</span>
            </div>
          </div>
          
          <div className="item-actions">
            <button
              className="btn btn-success"
              onClick={() => onToggle(item.id)}
              disabled={loading}
              style={{ fontSize: '0.75rem', padding: '0.375rem 0.75rem' }}
            >
              {item.status === 'completed' ? '标记待办' : '标记完成'}
            </button>
            <button
              className="btn btn-danger"
              onClick={() => onDelete(item.id)}
              disabled={loading}
            >
              删除
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
