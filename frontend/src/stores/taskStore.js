/**
 * 任务状态管理
 */

import { create } from 'zustand';
import { taskApi } from '../api/tasks';

export const useTaskStore = create((set, get) => ({
  // 状态
  tasks: [],
  currentTask: null,
  pagination: null,
  isLoading: false,
  error: null,

  // Actions
  fetchTasks: async (params = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response = await taskApi.list(params);
      set({
        tasks: response.data.items,
        pagination: response.data.pagination,
        isLoading: false,
      });
    } catch (error) {
      set({ error: error.message, isLoading: false });
    }
  },

  fetchTask: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const response = await taskApi.get(id);
      set({
        currentTask: response.data,
        isLoading: false,
      });
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      return null;
    }
  },

  createTask: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const response = await taskApi.create(data);
      set({ isLoading: false });
      return response.data;
    } catch (error) {
      set({ error: error.message, isLoading: false });
      return null;
    }
  },

  startTask: async (id) => {
    try {
      await taskApi.start(id);
      // 刷新当前任务
      get().fetchTask(id);
      return true;
    } catch (error) {
      set({ error: error.message });
      return false;
    }
  },

  clearCurrentTask: () => set({ currentTask: null }),
  clearError: () => set({ error: null }),
}));
