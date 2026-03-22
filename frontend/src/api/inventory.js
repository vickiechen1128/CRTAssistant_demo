/**
 * 台账API
 */

import apiClient from './index';

export const inventoryApi = {
  /**
   * 获取任务台账列表
   * @param {number} taskId - 任务ID
   */
  list: (taskId) => apiClient.get('/inventories', { params: { task_id: taskId } }),

  /**
   * 按类型获取台账列表
   * @param {string} type - 台账类型 (server/cloud_resource/account)
   */
  listByType: (type) => apiClient.get('/inventories', { params: { inventory_type: type } }),

  /**
   * 获取台账详情
   * @param {number} id - 台账ID
   */
  get: (id) => apiClient.get(`/inventories/${id}`),

  /**
   * 创建台账
   * @param {Object} data - 台账数据
   */
  create: (data) => apiClient.post('/inventories', data),

  /**
   * 提交台账审核
   * @param {number} id - 台账ID
   */
  submit: (id) => apiClient.post(`/inventories/${id}/submit`),

  /**
   * 确认台账
   * @param {number} id - 台账ID
   */
  confirm: (id) => apiClient.post(`/inventories/${id}/confirm`),
};
