/**
 * 交付物API
 */

import apiClient from './index';

export const deliverableApi = {
  /**
   * 获取交付物列表
   * @param {Object} params - 查询参数
   * @param {number} params.task_id - 任务ID
   * @param {number} params.checklist_item_id - 检查项ID
   */
  list: (params = {}) => apiClient.get('/deliverables', { params }),

  /**
   * 上传交付物
   * @param {FormData} formData - 包含文件的表单数据
   */
  upload: (formData) => apiClient.post('/deliverables', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),

  /**
   * 下载交付物
   * @param {number} id - 交付物ID
   */
  download: (id) => apiClient.get(`/deliverables/${id}`, {
    responseType: 'blob',
  }),

  /**
   * 删除交付物
   * @param {number} id - 交付物ID
   */
  delete: (id) => apiClient.delete(`/deliverables/${id}`),
};
