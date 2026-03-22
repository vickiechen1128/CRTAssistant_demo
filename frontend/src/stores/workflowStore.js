/**
 * 工作流状态管理
 * 使用Zustand管理工作流相关的状态
 */

import { create } from 'zustand';
import * as workflowApi from '../api/workflow';

const useWorkflowStore = create((set, get) => ({
  // ==================== 状态 ====================
  workflows: [],
  currentWorkflow: null,
  instances: [],
  currentInstance: null,
  progress: null,
  loading: false,
  error: null,

  // ==================== 分页信息 ====================
  pagination: {
    page: 1,
    per_page: 20,
    total: 0,
    pages: 0
  },

  // ==================== Actions ====================

  /**
   * 获取工作流模板列表
   */
  fetchWorkflows: async (params = {}) => {
    set({ loading: true, error: null });
    try {
      const response = await workflowApi.getWorkflowList(params);
      if (response.data.code === 0) {
        set({
          workflows: response.data.data.items,
          pagination: response.data.data.pagination,
          loading: false
        });
      } else {
        set({ error: response.data.message, loading: false });
      }
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  /**
   * 创建工作流模板
   */
  createWorkflow: async (data) => {
    set({ loading: true, error: null });
    try {
      const response = await workflowApi.createWorkflow(data);
      if (response.data.code === 0) {
        // 刷新列表
        get().fetchWorkflows();
        set({ loading: false });
        return response.data.data;
      } else {
        set({ error: response.data.message, loading: false });
        return null;
      }
    } catch (error) {
      set({ error: error.message, loading: false });
      return null;
    }
  },

  /**
   * 获取工作流详情
   */
  fetchWorkflowDetail: async (id) => {
    set({ loading: true, error: null });
    try {
      const response = await workflowApi.getWorkflowDetail(id);
      if (response.data.code === 0) {
        set({
          currentWorkflow: response.data.data,
          loading: false
        });
        return response.data.data;
      } else {
        set({ error: response.data.message, loading: false });
        return null;
      }
    } catch (error) {
      set({ error: error.message, loading: false });
      return null;
    }
  },

  /**
   * 更新工作流
   */
  updateWorkflow: async (id, data) => {
    set({ loading: true, error: null });
    try {
      const response = await workflowApi.updateWorkflow(id, data);
      if (response.data.code === 0) {
        // 刷新当前工作流
        get().fetchWorkflowDetail(id);
        set({ loading: false });
        return response.data.data;
      } else {
        set({ error: response.data.message, loading: false });
        return null;
      }
    } catch (error) {
      set({ error: error.message, loading: false });
      return null;
    }
  },

  /**
   * 删除工作流
   */
  deleteWorkflow: async (id) => {
    set({ loading: true, error: null });
    try {
      const response = await workflowApi.deleteWorkflow(id);
      if (response.data.code === 0) {
        // 刷新列表
        get().fetchWorkflows();
        set({ loading: false });
        return true;
      } else {
        set({ error: response.data.message, loading: false });
        return false;
      }
    } catch (error) {
      set({ error: error.message, loading: false });
      return false;
    }
  },

  // ==================== 工作流实例 Actions ====================

  /**
   * 获取工作流实例列表
   */
  fetchInstances: async (params = {}) => {
    set({ loading: true, error: null });
    try {
      const response = await workflowApi.getWorkflowInstanceList(params);
      if (response.data.code === 0) {
        set({
          instances: response.data.data.items,
          pagination: response.data.data.pagination,
          loading: false
        });
      } else {
        set({ error: response.data.message, loading: false });
      }
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  /**
   * 创建工作流实例
   */
  createInstance: async (data) => {
    set({ loading: true, error: null });
    try {
      const response = await workflowApi.createWorkflowInstance(data);
      if (response.data.code === 0) {
        set({ loading: false });
        return response.data.data;
      } else {
        set({ error: response.data.message, loading: false });
        return null;
      }
    } catch (error) {
      set({ error: error.message, loading: false });
      return null;
    }
  },

  /**
   * 获取工作流实例详情
   */
  fetchInstanceDetail: async (instanceId) => {
    set({ loading: true, error: null });
    try {
      const response = await workflowApi.getWorkflowInstanceDetail(instanceId);
      if (response.data.code === 0) {
        set({
          currentInstance: response.data.data,
          loading: false
        });
        return response.data.data;
      } else {
        set({ error: response.data.message, loading: false });
        return null;
      }
    } catch (error) {
      set({ error: error.message, loading: false });
      return null;
    }
  },

  /**
   * 执行工作项
   */
  executeWorkItem: async (instanceId, data) => {
    set({ loading: true, error: null });
    try {
      const response = await workflowApi.executeWorkItem(instanceId, data);
      if (response.data.code === 0) {
        // 刷新实例详情
        get().fetchInstanceDetail(instanceId);
        set({ loading: false });
        return response.data.data;
      } else {
        set({ error: response.data.message, loading: false });
        return null;
      }
    } catch (error) {
      set({ error: error.message, loading: false });
      return null;
    }
  },

  /**
   * 验收工作项
   */
  verifyWorkItem: async (instanceId, data) => {
    set({ loading: true, error: null });
    try {
      const response = await workflowApi.verifyWorkItem(instanceId, data);
      if (response.data.code === 0) {
        // 刷新实例详情
        get().fetchInstanceDetail(instanceId);
        set({ loading: false });
        return response.data.data;
      } else {
        set({ error: response.data.message, loading: false });
        return null;
      }
    } catch (error) {
      set({ error: error.message, loading: false });
      return null;
    }
  },

  /**
   * 获取工作流进度
   */
  fetchProgress: async (instanceId) => {
    set({ loading: true, error: null });
    try {
      const response = await workflowApi.getWorkflowProgress(instanceId);
      if (response.data.code === 0) {
        set({
          progress: response.data.data,
          loading: false
        });
        return response.data.data;
      } else {
        set({ error: response.data.message, loading: false });
        return null;
      }
    } catch (error) {
      set({ error: error.message, loading: false });
      return null;
    }
  },

  /**
   * 更新工作项进度
   */
  updateWorkItemProgress: async (instanceId, workItemId, progress) => {
    set({ loading: true, error: null });
    try {
      const response = await workflowApi.updateWorkItemProgress(instanceId, workItemId, progress);
      if (response.data.code === 0) {
        // 刷新实例详情
        get().fetchInstanceDetail(instanceId);
        set({ loading: false });
        return response.data.data;
      } else {
        set({ error: response.data.message, loading: false });
        return null;
      }
    } catch (error) {
      set({ error: error.message, loading: false });
      return null;
    }
  },

  // ==================== 辅助方法 ====================

  /**
   * 清除当前工作流
   */
  clearCurrentWorkflow: () => {
    set({ currentWorkflow: null });
  },

  /**
   * 清除当前实例
   */
  clearCurrentInstance: () => {
    set({ currentInstance: null, progress: null });
  },

  /**
   * 清除错误
   */
  clearError: () => {
    set({ error: null });
  }
}));

export default useWorkflowStore;
