/**
 * 仪表盘API
 */

import apiClient from './index';

export const dashboardApi = {
  /**
   * 获取概览数据
   */
  getOverview: () => apiClient.get('/dashboard/overview'),

  /**
   * 获取任务统计
   */
  getTaskStats: () => apiClient.get('/dashboard/tasks'),
};
