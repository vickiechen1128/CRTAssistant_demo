/**
 * 审核矩阵 API
 */
import { apiClient } from '../../../core/api';

/**
 * 获取审核矩阵配置列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export const getAuditMatrixList = (params = {}) => {
  return apiClient.get('/audit-matrix-configs', { params });
};

/**
 * 获取审核矩阵配置详情
 * @param {string} configId - 配置 ID
 * @returns {Promise}
 */
export const getAuditMatrixDetail = (configId) => {
  return apiClient.get(`/audit-matrix-configs/${configId}`);
};

/**
 * 创建审核矩阵配置
 * @param {Object} data - 配置数据
 * @returns {Promise}
 */
export const createAuditMatrix = (data) => {
  return apiClient.post('/audit-matrix-configs', data);
};

/**
 * 更新审核矩阵配置
 * @param {string} configId - 配置 ID
 * @param {Object} data - 配置数据
 * @returns {Promise}
 */
export const updateAuditMatrix = (configId, data) => {
  return apiClient.put(`/audit-matrix-configs/${configId}`, data);
};

/**
 * 删除审核矩阵配置
 * @param {string} configId - 配置 ID
 * @returns {Promise}
 */
export const deleteAuditMatrix = (configId) => {
  return apiClient.delete(`/audit-matrix-configs/${configId}`);
};

/**
 * 激活审核矩阵配置
 * @param {string} configId - 配置 ID
 * @returns {Promise}
 */
export const activateAuditMatrix = (configId) => {
  return apiClient.post(`/audit-matrix-configs/${configId}/activate`, {});
};

/**
 * 停用审核矩阵配置
 * @param {string} configId - 配置 ID
 * @returns {Promise}
 */
export const deactivateAuditMatrix = (configId) => {
  return apiClient.post(`/audit-matrix-configs/${configId}/deactivate`, {});
};

/**
 * 添加审核规则
 * @param {string} configId - 配置 ID
 * @param {Object} data - 规则数据
 * @returns {Promise}
 */
export const addAuditRule = (configId, data) => {
  return apiClient.post(`/audit-matrix-configs/${configId}/rules`, data);
};

/**
 * 更新审核规则
 * @param {string} configId - 配置 ID
 * @param {string} ruleId - 规则 ID
 * @param {Object} data - 规则数据
 * @returns {Promise}
 */
export const updateAuditRule = (configId, ruleId, data) => {
  return apiClient.put(`/audit-matrix-configs/${configId}/rules/${ruleId}`, data);
};

/**
 * 删除审核规则
 * @param {string} configId - 配置 ID
 * @param {string} ruleId - 规则 ID
 * @returns {Promise}
 */
export const deleteAuditRule = (configId, ruleId) => {
  return apiClient.delete(`/audit-matrix-configs/${configId}/rules/${ruleId}`);
};
