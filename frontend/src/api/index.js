/**
 * API客户端配置
 * 使用axios封装，统一处理请求/响应
 */

import axios from 'axios';

// 创建axios实例
const apiClient = axios.create({
  baseURL: '/api',  // Vite代理配置
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加Token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    console.log(`请求 ${config.url}, token:`, token ? '存在' : '不存在');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 统一错误处理
apiClient.interceptors.response.use(
  (response) => {
    // 直接返回data部分
    return response.data;
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response;
      
      // 401未授权，清除token并跳转登录
      if (status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        return Promise.reject(new Error('登录已过期，请重新登录'));
      }
      
      // 返回后端错误信息
      return Promise.reject(new Error(data?.message || '请求失败'));
    }
    
    return Promise.reject(new Error('网络错误'));
  }
);

export default apiClient;
