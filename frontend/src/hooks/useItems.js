import { useState, useEffect, useCallback } from 'react';
import { itemsApi } from '../services/api';

/**
 * Items 自定义 Hook
 * 管理 items 的状态和 CRUD 操作
 */
export function useItems() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 获取 items 列表
  const fetchItems = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await itemsApi.list();
      setItems(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // 初始加载
  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  // 创建 item
  const createItem = async (data) => {
    setError(null);
    try {
      const newItem = await itemsApi.create(data);
      setItems(prev => [newItem, ...prev]);
      return newItem;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  // 更新 item
  const updateItem = async (id, data) => {
    setError(null);
    try {
      const updatedItem = await itemsApi.update(id, data);
      setItems(prev => prev.map(item => 
        item.id === id ? updatedItem : item
      ));
      return updatedItem;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  // 删除 item
  const deleteItem = async (id) => {
    setError(null);
    try {
      await itemsApi.delete(id);
      setItems(prev => prev.filter(item => item.id !== id));
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  // 切换完成状态
  const toggleStatus = async (id) => {
    const item = items.find(i => i.id === id);
    if (!item) return;
    
    const newStatus = item.status === 'completed' ? 'pending' : 'completed';
    return updateItem(id, { status: newStatus });
  };

  return {
    items,
    loading,
    error,
    fetchItems,
    createItem,
    updateItem,
    deleteItem,
    toggleStatus,
  };
}
