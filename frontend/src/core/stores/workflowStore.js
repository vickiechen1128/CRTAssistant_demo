/**
 * 工作流状态管理
 * 占位文件 - 待后续实现
 */
import { create } from 'zustand';

const useWorkflowStore = create((set, get) => ({
  // ==================== 状态 ====================
  workflows: [],
  currentWorkflow: null,
  instances: [],
  currentInstance: null,
  progress: null,
  loading: false,
  error: null,

  // ==================== 分页信息 ====================
  pagination: {
    page: 1,
    per_page: 20,
    total: 0,
    pages: 0
  },

  // ==================== Actions ====================
  fetchWorkflows: async (params = {}) => {
    console.log('fetchWorkflows 待实现', params);
  },

  fetchWorkflow: async (id) => {
    console.log('fetchWorkflow 待实现', id);
  },

  createWorkflow: async (data) => {
    console.log('createWorkflow 待实现', data);
  },

  updateWorkflow: async (id, data) => {
    console.log('updateWorkflow 待实现', id, data);
  },

  deleteWorkflow: async (id) => {
    console.log('deleteWorkflow 待实现', id);
  },

  startInstance: async (workflowId, context) => {
    console.log('startInstance 待实现', workflowId, context);
  },

  fetchInstance: async (instanceId) => {
    console.log('fetchInstance 待实现', instanceId);
  },

  submitTask: async (instanceId, nodeId, data) => {
    console.log('submitTask 待实现', instanceId, nodeId, data);
  },

  fetchProgress: async (instanceId) => {
    console.log('fetchProgress 待实现', instanceId);
  },
}));

export default useWorkflowStore;
