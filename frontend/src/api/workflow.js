/**
 * 工作流管理API
 * 处理工作流模板和实例的CRUD操作
 */

import request from './index';

/**
 * 获取工作流模板列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.per_page - 每页条数
 * @param {boolean} params.is_preset - 是否预置模板
 * @param {string} params.keyword - 关键词搜索
 */
export function getWorkflowList(params = {}) {
  return request({
    url: '/workflows',
    method: 'get',
    params
  });
}

/**
 * 创建工作流模板
 * @param {Object} data - 工作流数据
 */
export function createWorkflow(data) {
  return request({
    url: '/workflows',
    method: 'post',
    data
  });
}

/**
 * 获取工作流模板详情
 * @param {number} id - 工作流ID
 */
export function getWorkflowDetail(id) {
  return request({
    url: `/workflows/${id}`,
    method: 'get'
  });
}

/**
 * 更新工作流模板
 * @param {number} id - 工作流ID
 * @param {Object} data - 更新数据
 */
export function updateWorkflow(id, data) {
  return request({
    url: `/workflows/${id}`,
    method: 'put',
    data
  });
}

/**
 * 删除工作流模板
 * @param {number} id - 工作流ID
 */
export function deleteWorkflow(id) {
  return request({
    url: `/workflows/${id}`,
    method: 'delete'
  });
}

/**
 * 创建工作项
 * @param {number} workflowId - 工作流ID
 * @param {Object} data - 工作项数据
 */
export function createWorkItem(workflowId, data) {
  return request({
    url: `/workflows/${workflowId}/work-items`,
    method: 'post',
    data
  });
}

/**
 * 更新工作项
 * @param {number} workflowId - 工作流ID
 * @param {number} workItemId - 工作项ID
 * @param {Object} data - 更新数据
 */
export function updateWorkItem(workflowId, workItemId, data) {
  return request({
    url: `/workflows/${workflowId}/work-items/${workItemId}`,
    method: 'put',
    data
  });
}

/**
 * 删除工作项
 * @param {number} workflowId - 工作流ID
 * @param {number} workItemId - 工作项ID
 */
export function deleteWorkItem(workflowId, workItemId) {
  return request({
    url: `/workflows/${workflowId}/work-items/${workItemId}`,
    method: 'delete'
  });
}

// ==================== 工作流实例API ====================

/**
 * 获取工作流实例列表
 * @param {Object} params - 查询参数
 */
export function getWorkflowInstanceList(params = {}) {
  return request({
    url: '/workflow-instances',
    method: 'get',
    params
  });
}

/**
 * 创建工作流实例
 * @param {Object} data - 实例数据
 */
export function createWorkflowInstance(data) {
  return request({
    url: '/workflow-instances',
    method: 'post',
    data
  });
}

/**
 * 获取工作流实例详情
 * @param {string} instanceId - 实例ID
 */
export function getWorkflowInstanceDetail(instanceId) {
  return request({
    url: `/workflow-instances/${instanceId}`,
    method: 'get'
  });
}

/**
 * 执行工作项
 * @param {string} instanceId - 实例ID
 * @param {Object} data - 执行数据
 */
export function executeWorkItem(instanceId, data) {
  return request({
    url: `/workflow-instances/${instanceId}/execute`,
    method: 'post',
    data
  });
}

/**
 * 验收工作项
 * @param {string} instanceId - 实例ID
 * @param {Object} data - 验收数据
 */
export function verifyWorkItem(instanceId, data) {
  return request({
    url: `/workflow-instances/${instanceId}/verify`,
    method: 'post',
    data
  });
}

/**
 * 获取工作流进度
 * @param {string} instanceId - 实例ID
 */
export function getWorkflowProgress(instanceId) {
  return request({
    url: `/workflow-instances/${instanceId}/progress`,
    method: 'get'
  });
}

/**
 * 更新工作项进度
 * @param {string} instanceId - 实例ID
 * @param {number} workItemId - 工作项ID
 * @param {number} progress - 进度值(0-100)
 */
export function updateWorkItemProgress(instanceId, workItemId, progress) {
  return request({
    url: `/workflow-instances/${instanceId}/work-items/${workItemId}/progress`,
    method: 'put',
    params: { progress }
  });
}
