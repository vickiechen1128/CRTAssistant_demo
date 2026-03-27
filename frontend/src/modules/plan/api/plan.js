/**
 * Plan 模块 API 接口
 * 与后端 /api/v1/plans 对齐
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
 * 获取计划详情
 * @param {string} id - 计划ID
 * @returns {Promise<Object>}
 */
export const getPlanDetail = async (id) => {
  return apiClient.get(`${BASE_URL}/${id}`);
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
 * @returns {Promise<string>}
 */
export const generatePlanId = async () => {
  return apiClient.get(`${BASE_URL}/generate-id`);
};
