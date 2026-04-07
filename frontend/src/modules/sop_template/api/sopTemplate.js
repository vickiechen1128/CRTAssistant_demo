/**
 * SOP 模板 API
 */
import { apiClient } from '../../../core/api';

/**
 * 获取 SOP 模板列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export const getSOPTemplateList = (params = {}) => {
  return apiClient.get('/sop-templates', { params });
};

/**
 * 获取 SOP 模板详情
 * @param {string} templateId - 模板 ID
 * @returns {Promise}
 */
export const getSOPTemplateDetail = (templateId) => {
  return apiClient.get(`/sop-templates/${templateId}`);
};

/**
 * 创建 SOP 模板
 * @param {Object} data - 模板数据
 * @returns {Promise}
 */
export const createSOPTemplate = (data) => {
  return apiClient.post('/sop-templates', data);
};

/**
 * 更新 SOP 模板
 * @param {string} templateId - 模板 ID
 * @param {Object} data - 模板数据
 * @returns {Promise}
 */
export const updateSOPTemplate = (templateId, data) => {
  return apiClient.put(`/sop-templates/${templateId}`, data);
};

/**
 * 删除 SOP 模板
 * @param {string} templateId - 模板 ID
 * @returns {Promise}
 */
export const deleteSOPTemplate = (templateId) => {
  return apiClient.delete(`/sop-templates/${templateId}`);
};

/**
 * 发布 SOP 模板
 * @param {string} templateId - 模板 ID
 * @returns {Promise}
 */
export const publishSOPTemplate = (templateId) => {
  return apiClient.post(`/sop-templates/${templateId}/publish`, {});
};

/**
 * 弃用 SOP 模板
 * @param {string} templateId - 模板 ID
 * @param {string} reason - 弃用原因
 * @returns {Promise}
 */
export const deprecateSOPTemplate = (templateId, reason) => {
  return apiClient.post(`/sop-templates/${templateId}/deprecate`, { reason });
};

/**
 * 克隆 SOP 模板
 * @param {string} templateId - 模板 ID
 * @param {Object} data - 克隆数据
 * @returns {Promise}
 */
export const cloneSOPTemplate = (templateId, data) => {
  return apiClient.post(`/sop-templates/${templateId}/clone`, data);
};

/**
 * 根据类型获取活跃模板
 * @param {string} templateType - 模板类型
 * @returns {Promise}
 */
export const getActiveTemplateByType = (templateType) => {
  return apiClient.get(`/sop-templates/by-type/${templateType}`);
};
