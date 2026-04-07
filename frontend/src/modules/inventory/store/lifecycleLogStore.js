/**
 * 生命周期日志状态管理
 * 使用 Zustand 管理生命周期日志业务状态
 */
import { create } from 'zustand';
import {
  createLifecycleLog,
  getLifecycleLogList,
  getLifecycleLogDetail,
  getApplicationTimeline,
  filterTimeline,
  getTimelineByPlan,
  getModuleTimeline,
  getLogStatistics,
  getLogTypes,
} from '../api';

export const useLifecycleLogStore = create((set, get) => ({
  // ========== 状态 ==========
  logs: [],
  timeline: [],
  currentLog: null,
  logTypes: [],
  statistics: null,
  
  loading: false,
  submitting: false,

  // ========== Actions ==========

  /**
   * 获取生命周期日志列表
   */
  fetchLogs: async (appId, params = {}) => {
    set({ loading: true });
    try {
      const response = await getLifecycleLogList(appId, params);
      set({ 
        logs: response.items || response || [],
      });
      return response;
    } catch (error) {
      console.error('获取生命周期日志列表失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 获取生命周期日志详情
   */
  fetchLogDetail: async (appId, logId) => {
    set({ loading: true });
    try {
      const log = await getLifecycleLogDetail(appId, logId);
      set({ currentLog: log });
      return log;
    } catch (error) {
      console.error('获取生命周期日志详情失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 创建生命周期日志
   */
  createLog: async (appId, data) => {
    set({ submitting: true });
    try {
      const log = await createLifecycleLog(appId, data);
      await get().fetchTimeline(appId);
      return log;
    } catch (error) {
      console.error('创建生命周期日志失败:', error);
      throw error;
    } finally {
      set({ submitting: false });
    }
  },

  /**
   * 获取应用时间线
   */
  fetchTimeline: async (appId, params = {}) => {
    set({ loading: true });
    try {
      const response = await getApplicationTimeline(appId, params);
      set({ 
        timeline: response.items || response || [],
      });
      return response;
    } catch (error) {
      console.error('获取时间线失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 筛选时间线
   */
  filterTimeline: async (appId, data) => {
    set({ loading: true });
    try {
      const response = await filterTimeline(appId, data);
      set({ 
        timeline: response.items || response || [],
      });
      return response;
    } catch (error) {
      console.error('筛选时间线失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 通过计划追溯时间线
   */
  fetchTimelineByPlan: async (appId, planId) => {
    set({ loading: true });
    try {
      const response = await getTimelineByPlan(appId, planId);
      set({ 
        timeline: response.items || response || [],
      });
      return response;
    } catch (error) {
      console.error('获取计划时间线失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 获取功能模块时间线
   */
  fetchModuleTimeline: async (appId, moduleId) => {
    set({ loading: true });
    try {
      const response = await getModuleTimeline(appId, moduleId);
      set({ 
        timeline: response.items || response || [],
      });
      return response;
    } catch (error) {
      console.error('获取模块时间线失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 获取日志统计
   */
  fetchStatistics: async (appId) => {
    try {
      const stats = await getLogStatistics(appId);
      set({ statistics: stats });
      return stats;
    } catch (error) {
      console.error('获取日志统计失败:', error);
      throw error;
    }
  },

  /**
   * 获取日志类型列表
   */
  fetchLogTypes: async (appId) => {
    try {
      const response = await getLogTypes(appId);
      set({ logTypes: response.types || [] });
      return response;
    } catch (error) {
      console.error('获取日志类型失败:', error);
      throw error;
    }
  },

  /**
   * 清空当前日志
   */
  clearCurrentLog: () => {
    set({ currentLog: null });
  },
}));
