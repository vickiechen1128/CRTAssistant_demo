/**
 * Plan 模块状态管理
 * 使用 Zustand 管理 Plan 业务状态
 */
import { create } from 'zustand';
import {
  getPlanList,
  getPlan,
  getPlanDetail,
  createPlan,
  updatePlan,
  deletePlan,
  startPlan,
  completePlan,
  cancelPlan,
  linkInventory,
  generatePlanId,
  previewPlanChanges,
  getInventoryList,
  getAppModules,
  createInventory,
} from '../api';

export const usePlanStore = create((set, get) => ({
  // ========== 状态 ==========
  plans: [],
  currentPlan: null,
  currentPlanDetail: null,
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
  
  // 创建计划相关状态
  creationStep: 0,
  creationData: {
    basicInfo: {},
    approvalFiles: [],
    affectedModules: [],
    relatedInventoryIds: [],
  },
  previewData: null,
  
  // 台账选择相关
  inventoryList: [],
  appModules: [],

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
   * 获取计划基本信息
   */
  fetchPlan: async (id) => {
    set({ loading: true });
    try {
      const plan = await getPlan(id);
      set({ currentPlan: plan });
      return plan;
    } catch (error) {
      console.error('获取计划失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 获取计划详情（包含完整关联信息）
   */
  fetchPlanDetail: async (id) => {
    set({ loading: true });
    try {
      const detail = await getPlanDetail(id);
      set({ 
        currentPlan: detail,
        currentPlanDetail: detail 
      });
      return detail;
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
        set({ currentPlan: null, currentPlanDetail: null });
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
   * PRD v3.1: IN_PROGRESS 状态的计划不允许取消
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
      // 处理 PRD v3.1 特定的错误
      if (error.response?.data?.detail?.error === 'CANNOT_CANCEL_IN_PROGRESS_PLAN') {
        const errorMessage = error.response.data.detail.message || '计划已启动，不允许取消';
        throw new Error(errorMessage);
      }
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
    set({ currentPlan: null, currentPlanDetail: null });
  },

  // ========== 创建计划相关 Actions ==========

  /**
   * 设置创建步骤
   */
  setCreationStep: (step) => {
    set({ creationStep: step });
  },

  /**
   * 重置创建步骤
   */
  resetCreationStep: () => {
    set({ 
      creationStep: 0,
      creationData: {
        basicInfo: {},
        approvalFiles: [],
        affectedModules: [],
        relatedInventoryIds: [],
      },
      previewData: null,
    });
  },

  /**
   * 更新创建数据
   */
  setCreationData: (data) => {
    set((state) => ({
      creationData: { ...state.creationData, ...data },
    }));
  },

  /**
   * 添加审批文件
   */
  addApprovalFile: (file) => {
    set((state) => ({
      creationData: {
        ...state.creationData,
        approvalFiles: [...state.creationData.approvalFiles, file],
      },
    }));
  },

  /**
   * 移除审批文件
   */
  removeApprovalFile: (fileUrl) => {
    set((state) => ({
      creationData: {
        ...state.creationData,
        approvalFiles: state.creationData.approvalFiles.filter(
          (f) => f.file_url !== fileUrl
        ),
      },
    }));
  },

  /**
   * 添加受影响模块
   */
  addAffectedModule: (module) => {
    set((state) => ({
      creationData: {
        ...state.creationData,
        affectedModules: [...state.creationData.affectedModules, module],
      },
    }));
  },

  /**
   * 更新受影响模块
   */
  updateAffectedModule: (index, module) => {
    set((state) => {
      const modules = [...state.creationData.affectedModules];
      modules[index] = { ...modules[index], ...module };
      return {
        creationData: {
          ...state.creationData,
          affectedModules: modules,
        },
      };
    });
  },

  /**
   * 移除受影响模块
   */
  removeAffectedModule: (index) => {
    set((state) => ({
      creationData: {
        ...state.creationData,
        affectedModules: state.creationData.affectedModules.filter((_, i) => i !== index),
      },
    }));
  },

  /**
   * 设置关联台账
   */
  setRelatedInventoryIds: (ids) => {
    set((state) => ({
      creationData: {
        ...state.creationData,
        relatedInventoryIds: ids,
      },
    }));
  },

  /**
   * 预生成 PlanID
   */
  fetchGeneratedPlanId: async () => {
    try {
      const result = await generatePlanId();
      return result;
    } catch (error) {
      console.error('生成PlanID失败:', error);
      throw error;
    }
  },

  /**
   * 预览计划变更
   */
  fetchPreviewChanges: async (data) => {
    set({ loading: true });
    try {
      const preview = await previewPlanChanges(data);
      set({ previewData: preview });
      return preview;
    } catch (error) {
      console.error('获取预览失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  // ========== 台账选择相关 Actions ==========

  /**
   * 获取台账列表
   */
  fetchInventoryList: async (params = {}) => {
    set({ loading: true });
    try {
      const result = await getInventoryList(params);
      // 后端返回格式: { items: [...], page, size, total, total_pages }
      const list = result?.items || [];
      set({ inventoryList: list });
      return result;
    } catch (error) {
      console.error('获取台账列表失败:', error);
      set({ inventoryList: [] });
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 获取应用系统的功能模块
   */
  fetchAppModules: async (appId) => {
    try {
      const result = await getAppModules(appId);
      set({ appModules: result.items || result || [] });
      return result;
    } catch (error) {
      console.error('获取功能模块失败:', error);
      throw error;
    }
  },

  /**
   * 清空应用模块列表
   */
  clearAppModules: () => {
    set({ appModules: [] });
  },

  /**
   * 创建应用系统台账（新系统上线场景）
   * @param {Object} data - 应用系统数据
   * @returns {Promise<Object>}
   */
  createInventoryApplication: async (data) => {
    set({ loading: true });
    try {
      const result = await createInventory(data);
      // 刷新台账列表
      await get().fetchInventoryList();
      return result;
    } catch (error) {
      console.error('创建应用系统台账失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },
}));
