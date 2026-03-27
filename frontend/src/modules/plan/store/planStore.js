/**
 * Plan 模块状态管理
 * 使用 Zustand 管理 Plan 业务状态
 */
import { create } from 'zustand';
import {
  getPlanList,
  getPlanDetail,
  createPlan,
  updatePlan,
  deletePlan,
  startPlan,
  completePlan,
  cancelPlan,
  linkInventory,
} from '../api';

export const usePlanStore = create((set, get) => ({
  // ========== 状态 ==========
  plans: [],
  currentPlan: null,
  pagination: {
    current: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0,
  },
  filters: {
    status: undefined,
    category: undefined,
    priority: undefined,
    keyword: '',
  },
  loading: false,
  submitting: false,

  // ========== Actions ==========

  /**
   * 设置筛选条件
   */
  setFilters: (filters) => {
    set((state) => ({
      filters: { ...state.filters, ...filters },
      pagination: { ...state.pagination, current: 1 },
    }));
  },

  /**
   * 重置筛选条件
   */
  resetFilters: () => {
    set({
      filters: {
        status: undefined,
        category: undefined,
        priority: undefined,
        keyword: '',
      },
      pagination: { ...get().pagination, current: 1 },
    });
  },

  /**
   * 设置分页
   */
  setPagination: (pagination) => {
    set((state) => ({
      pagination: { ...state.pagination, ...pagination },
    }));
  },

  /**
   * 获取计划列表
   */
  fetchPlans: async () => {
    set({ loading: true });
    try {
      const { filters, pagination } = get();
      const params = {
        ...filters,
        page: pagination.current,
        page_size: pagination.pageSize,
      };

      const response = await getPlanList(params);

      set({
        plans: response.items || [],
        pagination: {
          current: response.page || 1,
          pageSize: response.page_size || 20,
          total: response.total || 0,
          totalPages: response.total_pages || 0,
        },
      });

      return response;
    } catch (error) {
      console.error('获取计划列表失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 获取计划详情
   */
  fetchPlanDetail: async (id) => {
    set({ loading: true });
    try {
      const plan = await getPlanDetail(id);
      set({ currentPlan: plan });
      return plan;
    } catch (error) {
      console.error('获取计划详情失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 创建计划
   */
  createNewPlan: async (data) => {
    set({ submitting: true });
    try {
      const plan = await createPlan(data);
      // 刷新列表
      await get().fetchPlans();
      return plan;
    } catch (error) {
      console.error('创建计划失败:', error);
      throw error;
    } finally {
      set({ submitting: false });
    }
  },

  /**
   * 更新计划
   */
  updateExistingPlan: async (id, data) => {
    set({ submitting: true });
    try {
      const plan = await updatePlan(id, data);
      // 更新当前计划
      set({ currentPlan: plan });
      // 刷新列表
      await get().fetchPlans();
      return plan;
    } catch (error) {
      console.error('更新计划失败:', error);
      throw error;
    } finally {
      set({ submitting: false });
    }
  },

  /**
   * 删除计划
   */
  removePlan: async (id) => {
    set({ loading: true });
    try {
      await deletePlan(id);
      // 刷新列表
      await get().fetchPlans();
      // 如果当前正在查看该计划，清空
      if (get().currentPlan?.id === id) {
        set({ currentPlan: null });
      }
      return true;
    } catch (error) {
      console.error('删除计划失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 启动计划
   */
  startExistingPlan: async (id, data = {}) => {
    set({ loading: true });
    try {
      const plan = await startPlan(id, data);
      set({ currentPlan: plan });
      await get().fetchPlans();
      return plan;
    } catch (error) {
      console.error('启动计划失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 完成计划
   */
  completeExistingPlan: async (id, data = {}) => {
    set({ loading: true });
    try {
      const plan = await completePlan(id, data);
      set({ currentPlan: plan });
      await get().fetchPlans();
      return plan;
    } catch (error) {
      console.error('完成计划失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 取消计划
   */
  cancelExistingPlan: async (id, reason) => {
    set({ loading: true });
    try {
      const plan = await cancelPlan(id, { reason });
      set({ currentPlan: plan });
      await get().fetchPlans();
      return plan;
    } catch (error) {
      console.error('取消计划失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 关联台账到计划
   */
  linkInventoryToPlan: async (id, inventoryIds) => {
    set({ loading: true });
    try {
      const plan = await linkInventory(id, { inventory_ids: inventoryIds });
      set({ currentPlan: plan });
      await get().fetchPlans();
      return plan;
    } catch (error) {
      console.error('关联台账失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 清空当前计划
   */
  clearCurrentPlan: () => {
    set({ currentPlan: null });
  },
}));
