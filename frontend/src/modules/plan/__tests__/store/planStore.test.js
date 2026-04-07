/**
 * PlanStore 状态管理测试
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { usePlanStore } from '../../store/planStore';

// 模拟 API 调用
vi.mock('../../api', () => ({
  getPlanList: vi.fn(),
  getPlan: vi.fn(),
  getPlanDetail: vi.fn(),
  createPlan: vi.fn(),
  updatePlan: vi.fn(),
  deletePlan: vi.fn(),
  startPlan: vi.fn(),
  completePlan: vi.fn(),
  cancelPlan: vi.fn(),
  linkInventory: vi.fn(),
  generatePlanId: vi.fn(),
  previewPlanChanges: vi.fn(),
  getInventoryList: vi.fn(),
  getAppModules: vi.fn(),
}));

import {
  getPlanList,
  getPlan,
  createPlan,
  updatePlan,
  deletePlan,
} from '../../api';

describe('PlanStore', () => {
  beforeEach(() => {
    // 重置 store 状态
    usePlanStore.setState({
      plans: [],
      currentPlan: null,
      currentPlanDetail: null,
      pagination: {
        current: 1,
        pageSize: 20,
        total: 0,
        totalPages: 0,
      },
      filters: {
        status: undefined,
        category: undefined,
        priority: undefined,
        keyword: '',
      },
      loading: false,
      submitting: false,
      creationStep: 0,
      creationData: {
        basicInfo: {},
        approvalFiles: [],
        affectedModules: [],
        relatedInventoryIds: [],
      },
      previewData: null,
      inventoryList: [],
      appModules: [],
    });

    // 清除所有 mock
    vi.clearAllMocks();
  });

  describe('状态管理', () => {
    it('应正确设置筛选条件', () => {
      const store = usePlanStore.getState();

      store.setFilters({ status: 'DRAFT', category: 'new_system' });

      const state = usePlanStore.getState();
      expect(state.filters.status).toBe('DRAFT');
      expect(state.filters.category).toBe('new_system');
      expect(state.pagination.current).toBe(1); // 重置到第一页
    });

    it('应正确重置筛选条件', () => {
      const store = usePlanStore.getState();

      store.setFilters({ status: 'DRAFT' });
      store.resetFilters();

      const state = usePlanStore.getState();
      expect(state.filters.status).toBeUndefined();
      expect(state.filters.keyword).toBe('');
    });

    it('应正确设置分页', () => {
      const store = usePlanStore.getState();

      store.setPagination({ current: 2, pageSize: 10 });

      const state = usePlanStore.getState();
      expect(state.pagination.current).toBe(2);
      expect(state.pagination.pageSize).toBe(10);
    });
  });

  describe('创建计划相关', () => {
    it('应正确设置创建步骤', () => {
      const store = usePlanStore.getState();

      store.setCreationStep(2);

      expect(usePlanStore.getState().creationStep).toBe(2);
    });

    it('应正确更新创建数据', () => {
      const store = usePlanStore.getState();

      store.setCreationData({ basicInfo: { name: '测试计划' } });

      const state = usePlanStore.getState();
      expect(state.creationData.basicInfo.name).toBe('测试计划');
    });

    it('应正确添加审批文件', () => {
      const store = usePlanStore.getState();

      store.addApprovalFile({ file_name: 'test.pdf', file_url: '/uploads/test.pdf' });

      const state = usePlanStore.getState();
      expect(state.creationData.approvalFiles).toHaveLength(1);
      expect(state.creationData.approvalFiles[0].file_name).toBe('test.pdf');
    });

    it('应正确移除审批文件', () => {
      const store = usePlanStore.getState();

      store.addApprovalFile({ file_name: 'test1.pdf', file_url: '/uploads/test1.pdf' });
      store.addApprovalFile({ file_name: 'test2.pdf', file_url: '/uploads/test2.pdf' });
      store.removeApprovalFile('/uploads/test1.pdf');

      const state = usePlanStore.getState();
      expect(state.creationData.approvalFiles).toHaveLength(1);
      expect(state.creationData.approvalFiles[0].file_name).toBe('test2.pdf');
    });

    it('应正确添加受影响模块', () => {
      const store = usePlanStore.getState();

      store.addAffectedModule({
        module_id: 'mod-001',
        module_name: '用户模块',
        action: 'update',
      });

      const state = usePlanStore.getState();
      expect(state.creationData.affectedModules).toHaveLength(1);
      expect(state.creationData.affectedModules[0].module_name).toBe('用户模块');
    });

    it('应正确更新受影响模块', () => {
      const store = usePlanStore.getState();

      store.addAffectedModule({
        module_id: 'mod-001',
        module_name: '用户模块',
        action: 'update',
      });
      store.updateAffectedModule(0, { module_name: '订单模块' });

      const state = usePlanStore.getState();
      expect(state.creationData.affectedModules[0].module_name).toBe('订单模块');
    });

    it('应正确移除受影响模块', () => {
      const store = usePlanStore.getState();

      store.addAffectedModule({ module_id: 'mod-001', module_name: '模块1', action: 'create' });
      store.addAffectedModule({ module_id: 'mod-002', module_name: '模块2', action: 'update' });
      store.removeAffectedModule(0);

      const state = usePlanStore.getState();
      expect(state.creationData.affectedModules).toHaveLength(1);
      expect(state.creationData.affectedModules[0].module_name).toBe('模块2');
    });

    it('应正确重置创建步骤', () => {
      const store = usePlanStore.getState();

      store.setCreationStep(2);
      store.setCreationData({ basicInfo: { name: '测试' } });
      store.resetCreationStep();

      const state = usePlanStore.getState();
      expect(state.creationStep).toBe(0);
      expect(state.creationData.basicInfo).toEqual({});
      expect(state.creationData.approvalFiles).toHaveLength(0);
    });
  });

  describe('API 集成', () => {
    it('fetchPlans 应正确获取计划列表', async () => {
      const mockResponse = {
        items: [
          { id: '1', name: '计划1' },
          { id: '2', name: '计划2' },
        ],
        total: 2,
        page: 1,
        page_size: 20,
        total_pages: 1,
      };

      getPlanList.mockResolvedValue(mockResponse);

      const store = usePlanStore.getState();
      const result = await store.fetchPlans();

      const state = usePlanStore.getState();
      expect(state.plans).toHaveLength(2);
      expect(state.plans[0].name).toBe('计划1');
      expect(state.pagination.total).toBe(2);
      expect(getPlanList).toHaveBeenCalled();
    });

    it('fetchPlan 应正确获取单个计划', async () => {
      const mockPlan = { id: '1', name: '测试计划' };
      getPlan.mockResolvedValue(mockPlan);

      const store = usePlanStore.getState();
      const result = await store.fetchPlan('1');

      const state = usePlanStore.getState();
      expect(state.currentPlan).toEqual(mockPlan);
      expect(getPlan).toHaveBeenCalledWith('1');
    });

    it('createNewPlan 应正确创建计划', async () => {
      const newPlan = { id: '3', name: '新计划' };
      createPlan.mockResolvedValue(newPlan);
      getPlanList.mockResolvedValue({ items: [newPlan], total: 1 });

      const store = usePlanStore.getState();
      const result = await store.createNewPlan({ name: '新计划' });

      expect(createPlan).toHaveBeenCalledWith({ name: '新计划' });
      expect(getPlanList).toHaveBeenCalled(); // 创建后刷新列表
    });

    it('updateExistingPlan 应正确更新计划', async () => {
      const updatedPlan = { id: '1', name: '更新后的计划' };
      updatePlan.mockResolvedValue(updatedPlan);
      getPlanList.mockResolvedValue({ items: [updatedPlan], total: 1 });

      const store = usePlanStore.getState();
      const result = await store.updateExistingPlan('1', { name: '更新后的计划' });

      expect(updatePlan).toHaveBeenCalledWith('1', { name: '更新后的计划' });
      const state = usePlanStore.getState();
      expect(state.currentPlan).toEqual(updatedPlan);
    });

    it('removePlan 应正确删除计划', async () => {
      deletePlan.mockResolvedValue(true);
      getPlanList.mockResolvedValue({ items: [], total: 0 });

      const store = usePlanStore.getState();
      await store.removePlan('1');

      expect(deletePlan).toHaveBeenCalledWith('1');
      expect(getPlanList).toHaveBeenCalled();
    });

    it('删除当前计划时应清空 currentPlan', async () => {
      deletePlan.mockResolvedValue(true);
      getPlanList.mockResolvedValue({ items: [], total: 0 });

      // 先设置当前计划
      usePlanStore.setState({ currentPlan: { id: '1', name: '测试' } });

      const store = usePlanStore.getState();
      await store.removePlan('1');

      const state = usePlanStore.getState();
      expect(state.currentPlan).toBeNull();
    });
  });

  describe('加载状态', () => {
    it('fetchPlans 应设置 loading 状态', async () => {
      getPlanList.mockResolvedValue({ items: [], total: 0 });

      const store = usePlanStore.getState();
      const promise = store.fetchPlans();

      // 验证 loading 为 true
      expect(usePlanStore.getState().loading).toBe(true);

      await promise;

      // 验证 loading 为 false
      expect(usePlanStore.getState().loading).toBe(false);
    });

    it('createNewPlan 应设置 submitting 状态', async () => {
      createPlan.mockResolvedValue({});
      getPlanList.mockResolvedValue({ items: [], total: 0 });

      const store = usePlanStore.getState();
      const promise = store.createNewPlan({});

      expect(usePlanStore.getState().submitting).toBe(true);

      await promise;

      expect(usePlanStore.getState().submitting).toBe(false);
    });
  });
});
