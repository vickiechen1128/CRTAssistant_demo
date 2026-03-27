/**
 * 认证相关 API
 */
import apiClient from './axios';

export const authApi = {
  /**
   * 用户登录
   */
  login: async (credentials) => {
    const response = await apiClient.post('/auth/login', credentials);
    return response.data;
  },

  /**
   * 获取当前用户信息
   */
  getMe: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  /**
   * 用户登出
   */
  logout: async () => {
    const response = await apiClient.post('/auth/logout');
    return response.data;
  },
};

export default authApi;
