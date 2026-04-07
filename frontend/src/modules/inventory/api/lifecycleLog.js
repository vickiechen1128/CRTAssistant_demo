/**
 * 生命周期日志 API 接口
 * 与后端 /api/v1/inventory/applications/{app_id} 对齐
 */
import { apiClient } from '../../../core/api';

const BASE_URL = '/inventory/applications';

/**
 * 创建生命周期日志
 * @param {string} appId - 应用系统ID
 * @param {Object} data - 日志数据
 * @returns {Promise<Object>}
 */
export const createLifecycleLog = async (appId, data) => {
  return apiClient.post(`${BASE_URL}/${appId}/logs`, data);
};

/**
 * 获取生命周期日志列表
 * @param {string} appId - 应用系统ID
 * @param {Object} params - 查询参数 { log_type, limit, offset }
 * @returns {Promise<Object>}
 */
export const getLifecycleLogList = async (appId, params = {}) => {
  return apiClient.get(`${BASE_URL}/${appId}/logs`, { params });
};

/**
 * 获取生命周期日志详情
 * @param {string} appId - 应用系统ID
 * @param {string} logId - 日志ID
 * @returns {Promise<Object>}
 */
export const getLifecycleLogDetail = async (appId, logId) => {
  return apiClient.get(`${BASE_URL}/${appId}/logs/${logId}`);
};

/**
 * 获取应用时间线
 * @param {string} appId - 应用系统ID
 * @param {Object} params - 查询参数 { log_type, start_time, end_time, limit }
 * @returns {Promise<Object>}
 */
export const getApplicationTimeline = async (appId, params = {}) => {
  return apiClient.get(`${BASE_URL}/${appId}/logs/timeline`, { params });
};

/**
 * 筛选时间线
 * @param {string} appId - 应用系统ID
 * @param {Object} data - 筛选条件 { log_type, start_time, end_time, limit }
 * @returns {Promise<Object>}
 */
export const filterTimeline = async (appId, data) => {
  return apiClient.post(`${BASE_URL}/${appId}/logs/timeline/filter`, data);
};

/**
 * 通过计划追溯时间线（双向追溯）
 * @param {string} appId - 应用系统ID
 * @param {string} planId - 计划ID
 * @returns {Promise<Object>}
 */
export const getTimelineByPlan = async (appId, planId) => {
  return apiClient.get(`${BASE_URL}/${appId}/logs/timeline/by-plan/${planId}`);
};

/**
 * 获取功能模块时间线
 * @param {string} appId - 应用系统ID
 * @param {string} moduleId - 功能模块ID
 * @returns {Promise<Object>}
 */
export const getModuleTimeline = async (appId, moduleId) => {
  return apiClient.get(`${BASE_URL}/${appId}/logs/timeline/by-module/${moduleId}`);
};

/**
 * 获取日志统计
 * @param {string} appId - 应用系统ID
 * @returns {Promise<Object>}
 */
export const getLogStatistics = async (appId) => {
  return apiClient.get(`${BASE_URL}/${appId}/logs/statistics/overview`);
};

/**
 * 获取日志类型列表
 * @param {string} appId - 应用系统ID
 * @returns {Promise<Object>}
 */
export const getLogTypes = async (appId) => {
  return apiClient.get(`${BASE_URL}/${appId}/logs/types/list`);
};
