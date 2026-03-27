/**
 * Axios 实例配置
 * 全局请求封装，统一处理拦截器
 */
import axios from 'axios';
import { message } from 'antd';

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    // 统一处理响应格式
    const { data } = response;
    
    // 如果后端返回的是标准格式 { success, data, message, error }
    if (data && typeof data === 'object' && 'success' in data) {
      if (!data.success) {
        // 业务错误
        message.error(data.error || data.message || '操作失败');
        return Promise.reject(new Error(data.error || data.message));
      }
      return data.data;
    }
    
    return data;
  },
  (error) => {
    // 统一处理 HTTP 错误
    const { response } = error;
    
    if (response) {
      switch (response.status) {
        case 401:
          message.error('登录已过期，请重新登录');
          localStorage.removeItem('token');
          window.location.href = '/login';
          break;
        case 403:
          message.error('没有权限执行此操作');
          break;
        case 404:
          message.error('请求的资源不存在');
          break;
        case 500:
          message.error('服务器内部错误');
          break;
        default:
          message.error(response.data?.error || '请求失败');
      }
    } else {
      message.error('网络连接失败');
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
