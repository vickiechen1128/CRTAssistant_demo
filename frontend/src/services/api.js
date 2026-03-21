/**
 * API 服务封装
 * 统一处理与后端 FastAPI 的通信
 */

const API_BASE_URL = import.meta.env.DEV ? '/api' : '';

/**
 * 统一的请求封装
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };
  
  if (config.body && typeof config.body === 'object') {
    config.body = JSON.stringify(config.body);
  }
  
  const response = await fetch(url, config);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  
  // 204 No Content
  if (response.status === 204) {
    return null;
  }
  
  return response.json();
}

/**
 * Items API
 */
export const itemsApi = {
  /** 获取所有 items */
  list: () => request('/items'),
  
  /** 获取单个 item */
  get: (id) => request(`/items/${id}`),
  
  /** 创建 item */
  create: (data) => request('/items', {
    method: 'POST',
    body: data,
  }),
  
  /** 更新 item */
  update: (id, data) => request(`/items/${id}`, {
    method: 'PUT',
    body: data,
  }),
  
  /** 删除 item */
  delete: (id) => request(`/items/${id}`, {
    method: 'DELETE',
  }),
};

/**
 * 健康检查
 */
export const healthApi = {
  check: () => request('/health'),
};
