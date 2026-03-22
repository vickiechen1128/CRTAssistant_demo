/**
 * 验证API
 */

import apiClient from './index';

export const verificationApi = {
  /**
   * 获取脚本列表
   */
  listScripts: () => apiClient.get('/verification/scripts'),

  /**
   * 获取脚本详情
   * @param {number} id - 脚本ID
   */
  getScript: (id) => apiClient.get(`/verification/scripts/${id}`),

  /**
   * 执行验证
   * @param {Object} data - 执行参数
   */
  execute: (data) => apiClient.post('/verification/execute', data),

  /**
   * 获取执行结果
   * @param {string} executionId - 执行ID
   */
  getResult: (executionId) => apiClient.get(`/verification/execute/${executionId}`),

  /**
   * 获取执行记录列表
   * @param {Object} params - 查询参数
   */
  listRecords: (params) => apiClient.get('/verification/records', { params }),
};
