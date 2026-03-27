/**
 * 任务状态管理
 * 占位文件 - 待后续实现
 */
import { create } from 'zustand';

export const useTaskStore = create((set, get) => ({
  // 状态
  tasks: [],
  currentTask: null,
  pagination: null,
  isLoading: false,
  error: null,

  // Actions
  fetchTasks: async (params = {}) => {
    console.log('fetchTasks 待实现', params);
  },

  fetchTask: async (id) => {
    console.log('fetchTask 待实现', id);
  },

  createTask: async (data) => {
    console.log('createTask 待实现', data);
  },

  updateTask: async (id, data) => {
    console.log('updateTask 待实现', id, data);
  },

  deleteTask: async (id) => {
    console.log('deleteTask 待实现', id);
  },
}));

export default useTaskStore;
