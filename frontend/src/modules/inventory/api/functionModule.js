/**
 * 功能模块 API 接口
 * 与后端 /api/v1/inventory/applications/{app_id}/modules 对齐
 */
import { apiClient } from '../../../core/api';

const BASE_URL = '/inventory/applications';

/**
 * 创建功能模块
 * @param {string} appId - 应用系统ID
 * @param {Object} data - 功能模块数据
 * @returns {Promise<Object>}
 */
export const createFunctionModule = async (appId, data) => {
  return apiClient.post(`${BASE_URL}/${appId}/modules`, data);
};

/**
 * 获取功能模块列表
 * @param {string} appId - 应用系统ID
 * @param {Object} params - 查询参数 { status }
 * @returns {Promise<Object>}
 */
export const getFunctionModuleList = async (appId, params = {}) => {
  return apiClient.get(`${BASE_URL}/${appId}/modules`, { params });
};

/**
 * 获取功能模块树形结构
 * @param {string} appId - 应用系统ID
 * @returns {Promise<Array>}
 */
export const getFunctionModuleTree = async (appId) => {
  return apiClient.get(`${BASE_URL}/${appId}/modules/tree`);
};

/**
 * 获取功能模块详情
 * @param {string} appId - 应用系统ID
 * @param {string} moduleId - 功能模块ID
 * @returns {Promise<Object>}
 */
export const getFunctionModuleDetail = async (appId, moduleId) => {
  return apiClient.get(`${BASE_URL}/${appId}/modules/${moduleId}`);
};

/**
 * 更新功能模块
 * @param {string} appId - 应用系统ID
 * @param {string} moduleId - 功能模块ID
 * @param {Object} data - 更新数据
 * @returns {Promise<Object>}
 */
export const updateFunctionModule = async (appId, moduleId, data) => {
  return apiClient.put(`${BASE_URL}/${appId}/modules/${moduleId}`, data);
};

/**
 * 删除功能模块
 * @param {string} appId - 应用系统ID
 * @param {string} moduleId - 功能模块ID
 * @returns {Promise<Object>}
 */
export const deleteFunctionModule = async (appId, moduleId) => {
  return apiClient.delete(`${BASE_URL}/${appId}/modules/${moduleId}`);
};

/**
 * 更新功能模块状态
 * @param {string} appId - 应用系统ID
 * @param {string} moduleId - 功能模块ID
 * @param {string} status - 新状态 (draft/developing/testing/online/offline)
 * @returns {Promise<Object>}
 */
export const updateFunctionModuleStatus = async (appId, moduleId, status) => {
  return apiClient.patch(`${BASE_URL}/${appId}/modules/${moduleId}/status`, { status });
};

/**
 * 上线功能模块
 * @param {string} appId - 应用系统ID
 * @param {string} moduleId - 功能模块ID
 * @param {string} planId - 关联计划ID
 * @returns {Promise<Object>}
 */
export const launchFunctionModule = async (appId, moduleId, planId) => {
  return apiClient.post(`${BASE_URL}/${appId}/modules/${moduleId}/launch`, { plan_id: planId });
};

/**
 * 获取功能模块版本历史
 * @param {string} appId - 应用系统ID
 * @param {string} moduleCode - 模块编码
 * @returns {Promise<Object>}
 */
export const getFunctionModuleVersionHistory = async (appId, moduleCode) => {
  return apiClient.get(`${BASE_URL}/${appId}/modules/versions/${moduleCode}`);
};
