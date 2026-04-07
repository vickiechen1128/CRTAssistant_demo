/**
 * 功能模块状态管理
 * 使用 Zustand 管理功能模块业务状态
 */
import { create } from 'zustand';
import {
  createFunctionModule,
  getFunctionModuleList,
  getFunctionModuleTree,
  getFunctionModuleDetail,
  updateFunctionModule,
  deleteFunctionModule,
  updateFunctionModuleStatus,
  launchFunctionModule,
  getFunctionModuleVersionHistory,
} from '../api';

export const useFunctionModuleStore = create((set, get) => ({
  // ========== 状态 ==========
  modules: [],
  moduleTree: [],
  currentModule: null,
  versionHistory: [],
  
  loading: false,
  submitting: false,

  // ========== Actions ==========

  /**
   * 获取功能模块列表
   */
  fetchModules: async (appId, status) => {
    set({ loading: true });
    try {
      const params = status ? { status } : {};
      const response = await getFunctionModuleList(appId, params);
      set({ 
        modules: response.items || response || [],
      });
      return response;
    } catch (error) {
      console.error('获取功能模块列表失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 获取功能模块树形结构
   */
  fetchModuleTree: async (appId) => {
    set({ loading: true });
    try {
      const response = await getFunctionModuleTree(appId);
      set({ moduleTree: response || [] });
      return response;
    } catch (error) {
      console.error('获取功能模块树失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 获取功能模块详情
   */
  fetchModuleDetail: async (appId, moduleId) => {
    set({ loading: true });
    try {
      const module = await getFunctionModuleDetail(appId, moduleId);
      set({ currentModule: module });
      return module;
    } catch (error) {
      console.error('获取功能模块详情失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 创建功能模块
   */
  createModule: async (appId, data) => {
    set({ submitting: true });
    try {
      const module = await createFunctionModule(appId, data);
      await get().fetchModules(appId);
      return module;
    } catch (error) {
      console.error('创建功能模块失败:', error);
      throw error;
    } finally {
      set({ submitting: false });
    }
  },

  /**
   * 更新功能模块
   */
  updateModule: async (appId, moduleId, data) => {
    set({ submitting: true });
    try {
      const module = await updateFunctionModule(appId, moduleId, data);
      set({ currentModule: module });
      await get().fetchModules(appId);
      return module;
    } catch (error) {
      console.error('更新功能模块失败:', error);
      throw error;
    } finally {
      set({ submitting: false });
    }
  },

  /**
   * 删除功能模块
   */
  deleteModule: async (appId, moduleId) => {
    try {
      await deleteFunctionModule(appId, moduleId);
      await get().fetchModules(appId);
    } catch (error) {
      console.error('删除功能模块失败:', error);
      throw error;
    }
  },

  /**
   * 更新功能模块状态
   */
  updateModuleStatus: async (appId, moduleId, status) => {
    set({ submitting: true });
    try {
      const module = await updateFunctionModuleStatus(appId, moduleId, status);
      await get().fetchModules(appId);
      return module;
    } catch (error) {
      console.error('更新功能模块状态失败:', error);
      throw error;
    } finally {
      set({ submitting: false });
    }
  },

  /**
   * 上线功能模块
   */
  launchModule: async (appId, moduleId, planId) => {
    set({ submitting: true });
    try {
      const module = await launchFunctionModule(appId, moduleId, planId);
      await get().fetchModules(appId);
      return module;
    } catch (error) {
      console.error('上线功能模块失败:', error);
      throw error;
    } finally {
      set({ submitting: false });
    }
  },

  /**
   * 获取功能模块版本历史
   */
  fetchVersionHistory: async (appId, moduleCode) => {
    set({ loading: true });
    try {
      const response = await getFunctionModuleVersionHistory(appId, moduleCode);
      set({ versionHistory: response.versions || [] });
      return response;
    } catch (error) {
      console.error('获取版本历史失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 清空当前模块
   */
  clearCurrentModule: () => {
    set({ currentModule: null });
  },
}));
