/**
 * SOP 模板状态管理
 */
import { create } from 'zustand';
import {
  getSOPTemplateList,
  getSOPTemplateDetail,
  createSOPTemplate,
  updateSOPTemplate,
  deleteSOPTemplate,
  publishSOPTemplate,
  deprecateSOPTemplate,
  cloneSOPTemplate,
} from '../api';

export const useSOPTemplateStore = create((set, get) => ({
  // 状态
  templates: [],
  currentTemplate: null,
  loading: false,
  pagination: {
    current: 1,
    pageSize: 20,
    total: 0,
  },
  filters: {
    templateType: undefined,
    status: undefined,
    keyword: '',
  },

  // 设置状态
  setTemplates: (templates) => set({ templates }),
  setCurrentTemplate: (template) => set({ currentTemplate: template }),
  setLoading: (loading) => set({ loading }),
  setPagination: (pagination) => set({ pagination }),
  setFilters: (filters) => set({ filters }),

  // 获取模板列表
  fetchTemplates: async (params = {}) => {
    set({ loading: true });
    try {
      const { filters, pagination } = get();
      const response = await getSOPTemplateList({
        template_type: filters.templateType,
        status: filters.status,
        keyword: filters.keyword,
        page: params.page || pagination.current,
        page_size: params.pageSize || pagination.pageSize,
        ...params,
      });
      
      if (response.data?.code === 200) {
        const { items, total, page, page_size } = response.data.data;
        set({
          templates: items || [],
          pagination: {
            current: page,
            pageSize: page_size,
            total: total,
          },
        });
        return items;
      }
      return [];
    } catch (error) {
      console.error('获取 SOP 模板列表失败:', error);
      return [];
    } finally {
      set({ loading: false });
    }
  },

  // 获取模板详情
  fetchTemplateDetail: async (templateId) => {
    set({ loading: true });
    try {
      const response = await getSOPTemplateDetail(templateId);
      if (response.data?.code === 200) {
        set({ currentTemplate: response.data.data });
        return response.data.data;
      }
      return null;
    } catch (error) {
      console.error('获取 SOP 模板详情失败:', error);
      return null;
    } finally {
      set({ loading: false });
    }
  },

  // 创建模板
  createTemplate: async (data) => {
    set({ loading: true });
    try {
      const response = await createSOPTemplate(data);
      if (response.data?.code === 200) {
        return { success: true, data: response.data.data };
      }
      return { success: false, message: response.data?.message || '创建失败' };
    } catch (error) {
      console.error('创建 SOP 模板失败:', error);
      return { success: false, message: error.response?.data?.detail || '创建失败' };
    } finally {
      set({ loading: false });
    }
  },

  // 更新模板
  updateTemplate: async (templateId, data) => {
    set({ loading: true });
    try {
      const response = await updateSOPTemplate(templateId, data);
      if (response.data?.code === 200) {
        return { success: true, data: response.data.data };
      }
      return { success: false, message: response.data?.message || '更新失败' };
    } catch (error) {
      console.error('更新 SOP 模板失败:', error);
      return { success: false, message: error.response?.data?.detail || '更新失败' };
    } finally {
      set({ loading: false });
    }
  },

  // 删除模板
  deleteTemplate: async (templateId) => {
    set({ loading: true });
    try {
      const response = await deleteSOPTemplate(templateId);
      if (response.data?.code === 200) {
        return { success: true };
      }
      return { success: false, message: response.data?.message || '删除失败' };
    } catch (error) {
      console.error('删除 SOP 模板失败:', error);
      return { success: false, message: error.response?.data?.detail || '删除失败' };
    } finally {
      set({ loading: false });
    }
  },

  // 发布模板
  publishTemplate: async (templateId) => {
    set({ loading: true });
    try {
      const response = await publishSOPTemplate(templateId);
      if (response.data?.code === 200) {
        return { success: true, data: response.data.data };
      }
      return { success: false, message: response.data?.message || '发布失败' };
    } catch (error) {
      console.error('发布 SOP 模板失败:', error);
      return { success: false, message: error.response?.data?.detail || '发布失败' };
    } finally {
      set({ loading: false });
    }
  },

  // 弃用模板
  deprecateTemplate: async (templateId, reason) => {
    set({ loading: true });
    try {
      const response = await deprecateSOPTemplate(templateId, reason);
      if (response.data?.code === 200) {
        return { success: true, data: response.data.data };
      }
      return { success: false, message: response.data?.message || '弃用失败' };
    } catch (error) {
      console.error('弃用 SOP 模板失败:', error);
      return { success: false, message: error.response?.data?.detail || '弃用失败' };
    } finally {
      set({ loading: false });
    }
  },

  // 克隆模板
  cloneTemplate: async (templateId, data) => {
    set({ loading: true });
    try {
      const response = await cloneSOPTemplate(templateId, data);
      if (response.data?.code === 200) {
        return { success: true, data: response.data.data };
      }
      return { success: false, message: response.data?.message || '克隆失败' };
    } catch (error) {
      console.error('克隆 SOP 模板失败:', error);
      return { success: false, message: error.response?.data?.detail || '克隆失败' };
    } finally {
      set({ loading: false });
    }
  },

  // 重置状态
  resetState: () => set({
    templates: [],
    currentTemplate: null,
    loading: false,
    pagination: {
      current: 1,
      pageSize: 20,
      total: 0,
    },
    filters: {
      templateType: undefined,
      status: undefined,
      keyword: '',
    },
  }),
}));
