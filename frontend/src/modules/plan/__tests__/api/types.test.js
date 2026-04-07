/**
 * Plan 模块类型定义测试
 * 测试常量、枚举和工具函数
 */
import { describe, it, expect } from 'vitest';
import {
  PlanCategory,
  PlanPriority,
  PlanStatus,
  ModuleAction,
  categoryOptions,
  priorityOptions,
  statusOptions,
  moduleActionOptions,
  getCategoryConfig,
  getPriorityConfig,
  getStatusConfig,
  getModuleActionConfig,
  getInventoryActionType,
  requiresInventorySelection,
  allowMultipleInventory,
} from '../../api/types';

describe('Plan 类型定义', () => {
  describe('PlanCategory', () => {
    it('应包含所有有效的分类', () => {
      expect(PlanCategory.NEW_SYSTEM).toBe('new_system');
      expect(PlanCategory.NEW_FEATURE).toBe('new_feature');
      expect(PlanCategory.FUNC_CHANGE).toBe('func_change');
      expect(PlanCategory.ARCH_CHANGE).toBe('arch_change');
      expect(PlanCategory.SECURITY_CHECK).toBe('security_check');
    });
  });

  describe('PlanPriority', () => {
    it('应包含所有有效的优先级', () => {
      expect(PlanPriority.P0).toBe('P0');
      expect(PlanPriority.P1).toBe('P1');
      expect(PlanPriority.P2).toBe('P2');
      expect(PlanPriority.P3).toBe('P3');
    });
  });

  describe('PlanStatus', () => {
    it('应包含所有有效的状态', () => {
      expect(PlanStatus.DRAFT).toBe('DRAFT');
      expect(PlanStatus.PENDING).toBe('PENDING');
      expect(PlanStatus.IN_PROGRESS).toBe('IN_PROGRESS');
      expect(PlanStatus.COMPLETED).toBe('COMPLETED');
      expect(PlanStatus.CANCELLED).toBe('CANCELLED');
    });
  });

  describe('ModuleAction', () => {
    it('应包含所有有效的操作类型', () => {
      expect(ModuleAction.CREATE).toBe('create');
      expect(ModuleAction.UPDATE).toBe('update');
      expect(ModuleAction.DELETE).toBe('delete');
    });
  });

  describe('getCategoryConfig', () => {
    it('应返回正确的分类配置', () => {
      const config = getCategoryConfig('new_system');
      expect(config).toBeDefined();
      expect(config.label).toBe('新系统上线');
      expect(config.code).toBe('NEW');
    });

    it('无效分类应返回默认值', () => {
      const config = getCategoryConfig('invalid');
      expect(config).toBeUndefined();
    });
  });

  describe('getPriorityConfig', () => {
    it('应返回正确的优先级配置', () => {
      const config = getPriorityConfig('P0');
      expect(config).toBeDefined();
      expect(config.label).toBe('P0 - 最高优先级');
      expect(config.color).toBe('red');
    });

    it('P1 优先级应返回橙色', () => {
      const config = getPriorityConfig('P1');
      expect(config.color).toBe('orange');
    });
  });

  describe('getStatusConfig', () => {
    it('应返回正确的状态配置', () => {
      const draft = getStatusConfig('DRAFT');
      expect(draft.label).toBe('草稿');
      expect(draft.color).toBe('default');

      const completed = getStatusConfig('COMPLETED');
      expect(completed.label).toBe('已完成');
      expect(completed.color).toBe('success');
    });
  });

  describe('getModuleActionConfig', () => {
    it('应返回正确的操作配置', () => {
      const create = getModuleActionConfig('create');
      expect(create.label).toBe('新增');
      expect(create.color).toBe('green');

      const deleteAction = getModuleActionConfig('delete');
      expect(deleteAction.label).toBe('删除');
      expect(deleteAction.color).toBe('red');
    });
  });

  describe('getInventoryActionType', () => {
    it('新系统上线应返回 create_new', () => {
      expect(getInventoryActionType('new_system')).toBe('create_new');
    });

    it('新功能上线应返回 select_and_edit', () => {
      expect(getInventoryActionType('new_feature')).toBe('select_and_edit');
    });

    it('功能变更应返回 select_existing', () => {
      expect(getInventoryActionType('func_change')).toBe('select_existing');
    });

    it('安全检查应返回 security_scan', () => {
      expect(getInventoryActionType('security_check')).toBe('security_scan');
    });
  });

  describe('requiresInventorySelection', () => {
    it('安全检查不需要选择台账', () => {
      expect(requiresInventorySelection('security_check')).toBe(false);
    });

    it('其他分类需要选择台账', () => {
      expect(requiresInventorySelection('new_system')).toBe(true);
      expect(requiresInventorySelection('new_feature')).toBe(true);
      expect(requiresInventorySelection('func_change')).toBe(true);
    });
  });

  describe('allowMultipleInventory', () => {
    it('功能变更和架构变更允许多选', () => {
      expect(allowMultipleInventory('func_change')).toBe(true);
      expect(allowMultipleInventory('arch_change')).toBe(true);
    });

    it('新系统上线不允许多选', () => {
      expect(allowMultipleInventory('new_system')).toBe(false);
    });
  });
});
