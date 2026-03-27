/**
 * Inventory 模块 API 接口
 * 与后端 /api/v1/inventory 对齐
 */
import { apiClient } from '../../../core/api';

const BASE_URL = '/inventory';

// ==================== 汇总统计接口 ====================

/**
 * 获取台账汇总统计
 * @returns {Promise<Object>}
 */
export const getInventorySummary = async () => {
  return apiClient.get(`${BASE_URL}/summary`);
};

// ==================== 应用系统接口 ====================

/**
 * 创建应用系统
 * @param {Object} data - 应用系统数据
 * @returns {Promise<Object>}
 */
export const createApplication = async (data) => {
  return apiClient.post(`${BASE_URL}/applications`, data);
};

/**
 * 获取应用系统列表
 * @param {Object} params - 查询参数 { status, keyword, page, size }
 * @returns {Promise<Object>}
 */
export const getApplicationList = async (params = {}) => {
  return apiClient.get(`${BASE_URL}/applications`, { params });
};

/**
 * 获取应用系统详情
 * @param {string} id - 应用系统ID
 * @returns {Promise<Object>}
 */
export const getApplicationDetail = async (id) => {
  return apiClient.get(`${BASE_URL}/applications/${id}`);
};

/**
 * 更新应用系统
 * @param {string} id - 应用系统ID
 * @param {Object} data - 更新数据
 * @returns {Promise<Object>}
 */
export const updateApplication = async (id, data) => {
  return apiClient.put(`${BASE_URL}/applications/${id}`, data);
};

/**
 * 删除应用系统
 * @param {string} id - 应用系统ID
 * @returns {Promise<Object>}
 */
export const deleteApplication = async (id) => {
  return apiClient.delete(`${BASE_URL}/applications/${id}`);
};

/**
 * 变更应用系统状态
 * @param {string} id - 应用系统ID
 * @param {string} status - 新状态 (active/inactive/archived)
 * @returns {Promise<Object>}
 */
export const changeApplicationStatus = async (id, status) => {
  return apiClient.patch(`${BASE_URL}/applications/${id}/status`, null, {
    params: { new_status: status }
  });
};

// ==================== 云资源接口 ====================

/**
 * 创建云资源
 * @param {Object} data - 云资源数据
 * @returns {Promise<Object>}
 */
export const createCloudResource = async (data) => {
  return apiClient.post(`${BASE_URL}/cloud-resources`, data);
};

/**
 * 获取云资源列表
 * @param {Object} params - 查询参数 { app_id, resource_type, keyword, page, size }
 * @returns {Promise<Object>}
 */
export const getCloudResourceList = async (params = {}) => {
  return apiClient.get(`${BASE_URL}/cloud-resources`, { params });
};

/**
 * 获取云资源详情
 * @param {string} id - 云资源ID
 * @returns {Promise<Object>}
 */
export const getCloudResourceDetail = async (id) => {
  return apiClient.get(`${BASE_URL}/cloud-resources/${id}`);
};

/**
 * 更新云资源
 * @param {string} id - 云资源ID
 * @param {Object} data - 更新数据
 * @returns {Promise<Object>}
 */
export const updateCloudResource = async (id, data) => {
  return apiClient.put(`${BASE_URL}/cloud-resources/${id}`, data);
};

/**
 * 删除云资源
 * @param {string} id - 云资源ID
 * @returns {Promise<Object>}
 */
export const deleteCloudResource = async (id) => {
  return apiClient.delete(`${BASE_URL}/cloud-resources/${id}`);
};

// ==================== 账号接口 ====================

/**
 * 创建账号
 * @param {Object} data - 账号数据
 * @returns {Promise<Object>}
 */
export const createAccount = async (data) => {
  return apiClient.post(`${BASE_URL}/accounts`, data);
};

/**
 * 获取账号列表
 * @param {Object} params - 查询参数 { app_id, account_type, status, permission_level, keyword, page, size }
 * @returns {Promise<Object>}
 */
export const getAccountList = async (params = {}) => {
  return apiClient.get(`${BASE_URL}/accounts`, { params });
};

/**
 * 获取账号详情
 * @param {string} id - 账号ID
 * @returns {Promise<Object>}
 */
export const getAccountDetail = async (id) => {
  return apiClient.get(`${BASE_URL}/accounts/${id}`);
};

/**
 * 更新账号
 * @param {string} id - 账号ID
 * @param {Object} data - 更新数据
 * @returns {Promise<Object>}
 */
export const updateAccount = async (id, data) => {
  return apiClient.put(`${BASE_URL}/accounts/${id}`, data);
};

/**
 * 删除账号
 * @param {string} id - 账号ID
 * @returns {Promise<Object>}
 */
export const deleteAccount = async (id) => {
  return apiClient.delete(`${BASE_URL}/accounts/${id}`);
};

/**
 * 获取即将过期的账号
 * @param {number} days - 即将过期的天数 (默认30天)
 * @returns {Promise<Array>}
 */
export const getExpiringAccounts = async (days = 30) => {
  return apiClient.get(`${BASE_URL}/accounts/expiring`, { params: { days } });
};

/**
 * 延长账号有效期
 * @param {string} id - 账号ID
 * @param {number} days - 延长的天数
 * @returns {Promise<Object>}
 */
export const extendAccountValidity = async (id, days) => {
  return apiClient.post(`${BASE_URL}/accounts/${id}/extend`, { days });
};

// ==================== 计划关联接口 ====================

/**
 * 关联计划到台账
 * @param {string} type - 台账类型 (application/cloud_resource/account)
 * @param {string} id - 台账ID
 * @param {string} planId - 计划ID
 * @returns {Promise<Object>}
 */
export const linkPlanToInventory = async (type, id, planId) => {
  return apiClient.post(`${BASE_URL}/${type}/${id}/link-plan`, { plan_id: planId });
};

/**
 * 解除计划与台账的关联
 * @param {string} type - 台账类型 (application/cloud_resource/account)
 * @param {string} id - 台账ID
 * @param {string} planId - 计划ID
 * @returns {Promise<Object>}
 */
export const unlinkPlanFromInventory = async (type, id, planId) => {
  return apiClient.post(`${BASE_URL}/${type}/${id}/unlink-plan`, { plan_id: planId });
};
