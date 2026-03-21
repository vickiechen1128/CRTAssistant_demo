import { useState } from 'react';
import { useItems } from './hooks/useItems';
import { ItemForm } from './components/ItemForm';
import { ItemList } from './components/ItemList';
import { Message } from './components/Message';

/**
 * 主应用组件
 */
function App() {
  const { 
    items, 
    loading, 
    error, 
    createItem, 
    deleteItem, 
    toggleStatus 
  } = useItems();
  
  const [message, setMessage] = useState(null);
  const [messageType, setMessageType] = useState('info');

  // 显示消息
  const showMessage = (text, type = 'info') => {
    setMessage(text);
    setMessageType(type);
  };

  // 清除消息
  const clearMessage = () => {
    setMessage(null);
  };

  // 处理创建
  const handleCreate = async (data) => {
    try {
      await createItem(data);
      showMessage('Item 创建成功！', 'success');
    } catch (err) {
      showMessage(`创建失败: ${err.message}`, 'error');
    }
  };

  // 处理删除
  const handleDelete = async (id) => {
    if (!confirm('确定要删除这个 item 吗？')) return;
    
    try {
      await deleteItem(id);
      showMessage('Item 已删除', 'info');
    } catch (err) {
      showMessage(`删除失败: ${err.message}`, 'error');
    }
  };

  // 处理状态切换
  const handleToggle = async (id) => {
    try {
      await toggleStatus(id);
      showMessage('状态已更新', 'success');
    } catch (err) {
      showMessage(`更新失败: ${err.message}`, 'error');
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>🚀 CRTAssistant Demo</h1>
        <p>基于 FastAPI + React 的轻量级应用脚手架</p>
      </header>

      <Message 
        type={messageType} 
        message={message || error} 
        onClose={clearMessage}
        duration={3000}
      />

      <ItemForm 
        onSubmit={handleCreate} 
        loading={loading} 
      />

      <section>
        <h2 style={{ marginBottom: '1rem', fontSize: '1.125rem', color: 'var(--gray-700)' }}>
          Item 列表 ({items.length})
        </h2>
        
        {loading && items.length === 0 ? (
          <div className="loading">加载中...</div>
        ) : (
          <ItemList 
            items={items} 
            onToggle={handleToggle}
            onDelete={handleDelete}
            loading={loading}
          />
        )}
      </section>

      <footer style={{ marginTop: '3rem', textAlign: 'center', color: 'var(--gray-500)', fontSize: '0.75rem' }}>
        <p>Backend: FastAPI + SQLite | Frontend: React + Vite</p>
        <p style={{ marginTop: '0.25rem' }}>API Docs: <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noopener noreferrer">/docs</a></p>
      </footer>
    </div>
  );
}

export default App
