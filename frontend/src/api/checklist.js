/**
 * 检查清单API
 */

import apiClient from './index';

export const checklistApi = {
  /**
   * 获取检查项列表
   * @param {Object} params - 查询参数
   */
  list: (params) => apiClient.get('/checklist-items', { params }),

  /**
   * 获取检查项详情
   * @param {number} id - 检查项ID
   */
  get: (id) => apiClient.get(`/checklist-items/${id}`),

  /**
   * 更新检查项
   * @param {number} id - 检查项ID
   * @param {Object} data - 更新数据
   */
  update: (id, data) => apiClient.put(`/checklist-items/${id}`, data),

  /**
   * 确认检查项
   * @param {number} id - 检查项ID
   * @param {Object} data - 确认数据 {status, remark}
   */
  verify: (id, data) => apiClient.post(`/checklist-items/${id}/verify`, data),
};
