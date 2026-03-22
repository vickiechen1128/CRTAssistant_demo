/**
 * 认证相关API
 */

import apiClient from './index';

export const authApi = {
  /**
   * 用户登录
   * @param {Object} credentials - 登录凭证
   * @param {string} credentials.username - 用户名
   * @param {string} credentials.password - 密码
   */
  login: (credentials) => {
    // 使用form-data格式
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    return apiClient.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },

  /**
   * 获取当前用户信息
   */
  getMe: () => apiClient.get('/auth/me'),

  /**
   * 用户登出
   */
  logout: () => apiClient.post('/auth/logout'),
};
