/**
 * 准入任务API
 */

import apiClient from './index';

export const taskApi = {
  /**
   * 获取任务列表
   * @param {Object} params - 查询参数
   */
  list: (params = {}) => apiClient.get('/admission-tasks', { params }),

  /**
   * 获取任务详情
   * @param {number} id - 任务ID
   */
  get: (id) => apiClient.get(`/admission-tasks/${id}`),

  /**
   * 创建任务
   * @param {Object} data - 任务数据
   */
  create: (data) => apiClient.post('/admission-tasks', data),

  /**
   * 更新任务
   * @param {number} id - 任务ID
   * @param {Object} data - 更新数据
   */
  update: (id, data) => apiClient.put(`/admission-tasks/${id}`, data),

  /**
   * 启动任务
   * @param {number} id - 任务ID
   */
  start: (id) => apiClient.post(`/admission-tasks/${id}/start`),
};
