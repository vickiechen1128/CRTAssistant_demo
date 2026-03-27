/**
 * Inventory 模块状态管理
 * 使用 Zustand 管理台账业务状态
 */
import { create } from 'zustand';
import {
  getInventorySummary,
  getApplicationList,
  getApplicationDetail,
  createApplication,
  updateApplication,
  deleteApplication,
  changeApplicationStatus,
  getCloudResourceList,
  getCloudResourceDetail,
  createCloudResource,
  updateCloudResource,
  deleteCloudResource,
  getAccountList,
  getAccountDetail,
  createAccount,
  updateAccount,
  deleteAccount,
  getExpiringAccounts,
  extendAccountValidity,
  linkPlanToInventory,
  unlinkPlanFromInventory,
} from '../api';

export const useInventoryStore = create((set, get) => ({
  // ========== 状态 ==========
  summary: null,
  
  // 应用系统
  applications: [],
  currentApplication: null,
  
  // 云资源
  cloudResources: [],
  currentCloudResource: null,
  
  // 账号
  accounts: [],
  currentAccount: null,
  expiringAccounts: [],
  
  // 分页和筛选
  pagination: {
    current: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0,
  },
  filters: {
    type: 'application', // application | cloud | account
    status: undefined,
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
   * 设置分页
   */
  setPagination: (pagination) => {
    set((state) => ({
      pagination: { ...state.pagination, ...pagination },
    }));
  },

  /**
   * 获取台账汇总统计
   */
  fetchSummary: async () => {
    try {
      const summary = await getInventorySummary();
      set({ summary });
      return summary;
    } catch (error) {
      console.error('获取台账汇总失败:', error);
      throw error;
    }
  },

  // ========== 应用系统操作 ==========

  /**
   * 获取应用系统列表
   */
  fetchApplications: async () => {
    set({ loading: true });
    try {
      const { filters, pagination } = get();
      const params = {
        status: filters.status,
        keyword: filters.keyword,
        page: pagination.current,
        size: pagination.pageSize,
      };

      const response = await getApplicationList(params);

      set({
        applications: response.data || [],
        pagination: {
          current: response.page || 1,
          pageSize: response.size || 20,
          total: response.total || 0,
          totalPages: response.total_pages || 0,
        },
      });

      return response;
    } catch (error) {
      console.error('获取应用系统列表失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 获取应用系统详情
   */
  fetchApplicationDetail: async (id) => {
    set({ loading: true });
    try {
      const application = await getApplicationDetail(id);
      set({ currentApplication: application });
      return application;
    } catch (error) {
      console.error('获取应用系统详情失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 创建应用系统
   */
  createNewApplication: async (data) => {
    set({ submitting: true });
    try {
      const application = await createApplication(data);
      await get().fetchApplications();
      return application;
    } catch (error) {
      console.error('创建应用系统失败:', error);
      throw error;
    } finally {
      set({ submitting: false });
    }
  },

  /**
   * 更新应用系统
   */
  updateExistingApplication: async (id, data) => {
    set({ submitting: true });
    try {
      const application = await updateApplication(id, data);
      set({ currentApplication: application });
      await get().fetchApplications();
      return application;
    } catch (error) {
      console.error('更新应用系统失败:', error);
      throw error;
    } finally {
      set({ submitting: false });
    }
  },

  /**
   * 删除应用系统
   */
  removeApplication: async (id) => {
    try {
      await deleteApplication(id);
      await get().fetchApplications();
    } catch (error) {
      console.error('删除应用系统失败:', error);
      throw error;
    }
  },

  /**
   * 变更应用系统状态
   */
  changeApplicationStatusById: async (id, status) => {
    try {
      const application = await changeApplicationStatus(id, status);
      set({ currentApplication: application });
      await get().fetchApplications();
      return application;
    } catch (error) {
      console.error('变更应用系统状态失败:', error);
      throw error;
    }
  },

  // ========== 云资源操作 ==========

  /**
   * 获取云资源列表
   */
  fetchCloudResources: async () => {
    set({ loading: true });
    try {
      const { filters, pagination } = get();
      const params = {
        resource_type: filters.resource_type,
        keyword: filters.keyword,
        page: pagination.current,
        size: pagination.pageSize,
      };

      const response = await getCloudResourceList(params);

      set({
        cloudResources: response.data || [],
        pagination: {
          current: response.page || 1,
          pageSize: response.size || 20,
          total: response.total || 0,
          totalPages: response.total_pages || 0,
        },
      });

      return response;
    } catch (error) {
      console.error('获取云资源列表失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 获取云资源详情
   */
  fetchCloudResourceDetail: async (id) => {
    set({ loading: true });
    try {
      const resource = await getCloudResourceDetail(id);
      set({ currentCloudResource: resource });
      return resource;
    } catch (error) {
      console.error('获取云资源详情失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 创建云资源
   */
  createNewCloudResource: async (data) => {
    set({ submitting: true });
    try {
      const resource = await createCloudResource(data);
      await get().fetchCloudResources();
      return resource;
    } catch (error) {
      console.error('创建云资源失败:', error);
      throw error;
    } finally {
      set({ submitting: false });
    }
  },

  /**
   * 更新云资源
   */
  updateExistingCloudResource: async (id, data) => {
    set({ submitting: true });
    try {
      const resource = await updateCloudResource(id, data);
      set({ currentCloudResource: resource });
      await get().fetchCloudResources();
      return resource;
    } catch (error) {
      console.error('更新云资源失败:', error);
      throw error;
    } finally {
      set({ submitting: false });
    }
  },

  /**
   * 删除云资源
   */
  removeCloudResource: async (id) => {
    try {
      await deleteCloudResource(id);
      await get().fetchCloudResources();
    } catch (error) {
      console.error('删除云资源失败:', error);
      throw error;
    }
  },

  // ========== 账号操作 ==========

  /**
   * 获取账号列表
   */
  fetchAccounts: async () => {
    set({ loading: true });
    try {
      const { filters, pagination } = get();
      const params = {
        account_type: filters.account_type,
        status: filters.status,
        permission_level: filters.permission_level,
        keyword: filters.keyword,
        page: pagination.current,
        size: pagination.pageSize,
      };

      const response = await getAccountList(params);

      set({
        accounts: response.data || [],
        pagination: {
          current: response.page || 1,
          pageSize: response.size || 20,
          total: response.total || 0,
          totalPages: response.total_pages || 0,
        },
      });

      return response;
    } catch (error) {
      console.error('获取账号列表失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 获取账号详情
   */
  fetchAccountDetail: async (id) => {
    set({ loading: true });
    try {
      const account = await getAccountDetail(id);
      set({ currentAccount: account });
      return account;
    } catch (error) {
      console.error('获取账号详情失败:', error);
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  /**
   * 创建账号
   */
  createNewAccount: async (data) => {
    set({ submitting: true });
    try {
      const account = await createAccount(data);
      await get().fetchAccounts();
      return account;
    } catch (error) {
      console.error('创建账号失败:', error);
      throw error;
    } finally {
      set({ submitting: false });
    }
  },

  /**
   * 更新账号
   */
  updateExistingAccount: async (id, data) => {
    set({ submitting: true });
    try {
      const account = await updateAccount(id, data);
      set({ currentAccount: account });
      await get().fetchAccounts();
      return account;
    } catch (error) {
      console.error('更新账号失败:', error);
      throw error;
    } finally {
      set({ submitting: false });
    }
  },

  /**
   * 删除账号
   */
  removeAccount: async (id) => {
    try {
      await deleteAccount(id);
      await get().fetchAccounts();
    } catch (error) {
      console.error('删除账号失败:', error);
      throw error;
    }
  },

  /**
   * 获取即将过期的账号
   */
  fetchExpiringAccounts: async (days = 30) => {
    try {
      const accounts = await getExpiringAccounts(days);
      set({ expiringAccounts: accounts });
      return accounts;
    } catch (error) {
      console.error('获取即将过期账号失败:', error);
      throw error;
    }
  },

  /**
   * 延长账号有效期
   */
  extendAccountValidityById: async (id, days) => {
    try {
      const account = await extendAccountValidity(id, days);
      set({ currentAccount: account });
      await get().fetchAccounts();
      return account;
    } catch (error) {
      console.error('延长账号有效期失败:', error);
      throw error;
    }
  },

  // ========== 计划关联操作 ==========

  /**
   * 关联计划到台账
   */
  linkPlan: async (type, id, planId) => {
    try {
      await linkPlanToInventory(type, id, planId);
    } catch (error) {
      console.error('关联计划失败:', error);
      throw error;
    }
  },

  /**
   * 解除计划与台账的关联
   */
  unlinkPlan: async (type, id, planId) => {
    try {
      await unlinkPlanFromInventory(type, id, planId);
    } catch (error) {
      console.error('解除计划关联失败:', error);
      throw error;
    }
  },
}));
