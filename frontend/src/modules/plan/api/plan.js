/**
 * Plan 模块 API 接口
 * 与后端 /api/plans 对齐
 */
import { apiClient } from '../../../core/api';

const BASE_URL = '/plans';

/**
 * 创建计划
 * @param {Object} data - 计划数据
 * @returns {Promise<Object>}
 */
export const createPlan = async (data) => {
  return apiClient.post(BASE_URL, data);
};

/**
 * 获取计划列表
 * @param {Object} params - 查询参数
 * @returns {Promise<Object>}
 */
export const getPlanList = async (params = {}) => {
  return apiClient.get(BASE_URL, { params });
};

/**
 * 获取计划基本信息
 * @param {string} id - 计划ID
 * @returns {Promise<Object>}
 */
export const getPlan = async (id) => {
  return apiClient.get(`${BASE_URL}/${id}`);
};

/**
 * 获取计划详情（包含完整关联信息）
 * @param {string} id - 计划ID
 * @returns {Promise<Object>}
 */
export const getPlanDetail = async (id) => {
  return apiClient.get(`${BASE_URL}/${id}/detail`);
};

/**
 * 更新计划
 * @param {string} id - 计划ID
 * @param {Object} data - 更新数据
 * @returns {Promise<Object>}
 */
export const updatePlan = async (id, data) => {
  return apiClient.put(`${BASE_URL}/${id}`, data);
};

/**
 * 删除计划
 * @param {string} id - 计划ID
 * @returns {Promise<boolean>}
 */
export const deletePlan = async (id) => {
  return apiClient.delete(`${BASE_URL}/${id}`);
};

/**
 * 启动计划
 * @param {string} id - 计划ID
 * @param {Object} data - 启动参数
 * @returns {Promise<Object>}
 */
export const startPlan = async (id, data = {}) => {
  return apiClient.post(`${BASE_URL}/${id}/start`, data);
};

/**
 * 完成计划
 * @param {string} id - 计划ID
 * @param {Object} data - 完成参数
 * @returns {Promise<Object>}
 */
export const completePlan = async (id, data = {}) => {
  return apiClient.post(`${BASE_URL}/${id}/complete`, data);
};

/**
 * 取消计划
 * @param {string} id - 计划ID
 * @param {Object} data - 取消参数
 * @returns {Promise<Object>}
 */
export const cancelPlan = async (id, data) => {
  return apiClient.post(`${BASE_URL}/${id}/cancel`, data);
};

/**
 * 关联台账
 * @param {string} id - 计划ID
 * @param {Object} data - 关联数据
 * @returns {Promise<Object>}
 */
export const linkInventory = async (id, data) => {
  return apiClient.post(`${BASE_URL}/${id}/inventory`, data);
};

/**
 * 预生成 PlanID
 * @returns {Promise<Object>}
 */
export const generatePlanId = async () => {
  return apiClient.get(`${BASE_URL}/generate-id`);
};

/**
 * 预览计划变更
 * @param {Object} data - 预览数据
 * @returns {Promise<Object>}
 */
export const previewPlanChanges = async (data) => {
  return apiClient.post(`${BASE_URL}/preview`, data);
};

/**
 * 上传审批材料
 * @param {File} file - 文件对象
 * @returns {Promise<Object>}
 */
export const uploadApprovalFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  return apiClient.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

/**
 * 获取台账列表（用于选择）
 * @param {Object} params - 查询参数
 * @returns {Promise<Object>}
 */
export const getInventoryList = async (params = {}) => {
  return apiClient.get('/inventory/applications', { params });
};

/**
 * 获取应用系统的功能模块列表
 * @param {string} appId - 应用系统ID
 * @returns {Promise<Object>}
 */
export const getAppModules = async (appId) => {
  return apiClient.get(`/inventory/applications/${appId}/modules`);
};

/**
 * 创建应用系统台账
 * @param {Object} data - 应用系统数据
 * @returns {Promise<Object>}
 */
export const createInventory = async (data) => {
  return apiClient.post('/inventory/applications', data);
};
