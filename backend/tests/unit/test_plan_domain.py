#!/usr/bin/env python3
"""
计划模块领域层单元测试
测试领域对象、值对象、领域服务

运行方式:
    cd CRTAssistant_demo/backend
    python -m pytest tests/unit/test_plan_domain.py -v
"""
import sys
import pytest
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.modules.plan.domain.value_objects.category import Category
from app.modules.plan.domain.value_objects.priority import Priority
from app.modules.plan.domain.value_objects.plan_status import PlanStatus
from app.modules.plan.domain.value_objects.affected_module import AffectedModule
from app.modules.plan.domain.value_objects.plan_id import PlanId
from app.modules.plan.domain.value_objects.template_type import TemplateType
from app.modules.plan.domain.entities.plan import Plan


class TestCategory:
    """测试分类值对象"""
    
    def test_category_creation(self):
        """测试分类创建"""
        category = Category("new_system")
        assert category.value == "new_system"
        assert category.label == "新系统上线"
        assert category.inventory_action == "create_new"
    
    def test_category_invalid(self):
        """测试无效分类"""
        with pytest.raises(ValueError):
            Category("invalid_category")
    
    def test_all_categories(self):
        """测试所有预定义分类"""
        categories = ["new_system", "new_feature", "func_change", "arch_change", "security_check"]
        for cat in categories:
            category = Category(cat)
            assert category.value == cat
    
    def test_category_equality(self):
        """测试分类相等性"""
        cat1 = Category("new_system")
        cat2 = Category("new_system")
        cat3 = Category("new_feature")
        assert cat1 == cat2
        assert cat1 != cat3


class TestPriority:
    """测试优先级值对象"""
    
    def test_priority_creation(self):
        """测试优先级创建"""
        p0 = Priority.from_string("P0")
        assert p0.level == 0
        assert p0.is_p0 is True
        assert p0.label == "P0 - 最高优先级"
        
        p1 = Priority.from_string("P1")
        assert p1.level == 1
        assert p1.is_p0 is False
    
    def test_priority_invalid(self):
        """测试无效优先级"""
        with pytest.raises(ValueError):
            Priority.from_string("P5")
    
    def test_priority_comparison(self):
        """测试优先级比较"""
        p0 = Priority.from_string("P0")
        p1 = Priority.from_string("P1")
        p2 = Priority.from_string("P2")
        
        assert p0 < p1
        assert p1 < p2
        assert p0.level < p2.level


class TestPlanStatus:
    """测试计划状态值对象"""
    
    def test_status_creation(self):
        """测试状态创建"""
        draft = PlanStatus.draft()
        assert draft.value == "DRAFT"
        assert draft.is_editable is True
        
        in_progress = PlanStatus.in_progress()
        assert in_progress.value == "IN_PROGRESS"
        assert in_progress.is_editable is False
    
    def test_status_transitions(self):
        """测试状态流转"""
        draft = PlanStatus.draft()
        pending = PlanStatus.pending()
        in_progress = PlanStatus.in_progress()
        completed = PlanStatus.completed()
        cancelled = PlanStatus.cancelled()
        
        # 可启动的状态
        assert pending.is_startable is True
        assert draft.is_startable is True  # DRAFT也可以启动
        assert in_progress.is_startable is False
        
        # 可取消的状态
        assert draft.is_cancellable is True
        assert completed.is_cancellable is False


class TestAffectedModule:
    """测试受影响功能模块值对象"""
    
    def test_module_creation(self):
        """测试模块创建"""
        module = AffectedModule(
            module_id="mod-001",
            module_name="用户管理模块",
            action="update",
            before_version="v1.0.0",
            after_version="v1.1.0",
            change_description="优化用户登录流程"
        )
        assert module.module_id == "mod-001"
        assert module.module_name == "用户管理模块"
        assert module.action == "update"
    
    def test_module_to_dict(self):
        """测试模块转字典"""
        module = AffectedModule(
            module_id="mod-001",
            module_name="用户管理模块",
            action="create"
        )
        data = module.to_dict()
        assert data["module_id"] == "mod-001"
        assert data["action"] == "create"


class TestPlanId:
    """测试计划ID值对象"""
    
    def test_plan_id_generation(self):
        """测试计划ID生成"""
        date = datetime(2024, 1, 15)
        plan_id = PlanId.generate(date, 1)
        assert plan_id.value == "PLAN-20240115-0001"
        
        plan_id2 = PlanId.generate(date, 42)
        assert plan_id2.value == "PLAN-20240115-0042"
    
    def test_plan_id_parsing(self):
        """测试计划ID解析"""
        plan_id = PlanId("PLAN-20240115-0001")
        assert plan_id.date_part == "20240115"
        assert plan_id.sequence_number == 1


class TestTemplateType:
    """测试模板类型值对象"""
    
    def test_template_from_category(self):
        """测试从分类获取模板类型"""
        template = TemplateType.from_category("new_system")
        assert template.value == "new_system_onboarding"

        template = TemplateType.from_category("security_check")
        assert template.value == "security_audit"


class TestPlanEntity:
    """测试计划实体"""
    
    def test_plan_creation(self):
        """测试计划创建"""
        plan = Plan.create(
            name="测试计划",
            category=Category("new_system"),
            priority=Priority.from_string("P1"),
            data_tag="NEW-20240115-001",
            created_by="admin",
            description="这是一个测试计划"
        )
        
        assert plan.name == "测试计划"
        assert plan.category.value == "new_system"
        assert plan.priority.level == 1
        assert plan.status.value == "DRAFT"
        assert plan.created_by == "admin"
        assert plan.id.startswith("PLAN-")
    
    def test_p0_plan_creation(self):
        """测试P0计划创建（应为PENDING状态）"""
        plan = Plan.create(
            name="P0紧急计划",
            category=Category("security_check"),
            priority=Priority.from_string("P0"),
            data_tag="SEC-20240115-001",
            created_by="admin"
        )
        
        assert plan.priority.is_p0 is True
        assert plan.status.value == "PENDING"
    
    def test_plan_update(self):
        """测试计划更新"""
        plan = Plan.create(
            name="原始名称",
            category=Category("new_feature"),
            priority=Priority.from_string("P2"),
            data_tag="FEAT-20240115-001",
            created_by="admin"
        )
        
        plan.update(
            name="更新后的名称",
            description="更新描述"
        )
        
        assert plan.name == "更新后的名称"
        assert plan.description == "更新描述"
    
    def test_plan_update_in_non_editable_status(self):
        """测试非编辑状态下更新计划（应失败）"""
        plan = Plan.create(
            name="测试计划",
            category=Category("new_feature"),
            priority=Priority.from_string("P2"),
            data_tag="FEAT-20240115-001",
            created_by="admin"
        )
        
        # 模拟启动计划
        plan.start("admin")
        
        with pytest.raises(ValueError, match="Cannot update plan"):
            plan.update(name="新名称")
    
    def test_plan_start(self):
        """测试启动计划"""
        plan = Plan.create(
            name="测试计划",
            category=Category("new_feature"),
            priority=Priority.from_string("P0"),
            data_tag="FEAT-20240115-001",
            created_by="admin"
        )

        # P0计划创建后应为PENDING状态
        assert plan.status.value == "PENDING"

        plan.start("admin")

        assert plan.status.value == "IN_PROGRESS"
        assert plan.actual_start_time is not None
    
    def test_plan_complete(self):
        """测试完成计划"""
        plan = Plan.create(
            name="测试计划",
            category=Category("new_feature"),
            priority=Priority.from_string("P0"),
            data_tag="FEAT-20240115-001",
            created_by="admin"
        )
        
        plan.start("admin")
        plan.complete("admin")
        
        assert plan.status.value == "COMPLETED"
        assert plan.actual_end_time is not None
    
    def test_plan_cancel(self):
        """测试取消计划"""
        plan = Plan.create(
            name="测试计划",
            category=Category("new_feature"),
            priority=Priority.from_string("P2"),
            data_tag="FEAT-20240115-001",
            created_by="admin"
        )
        
        plan.cancel("admin", "计划取消原因")
        
        assert plan.status.value == "CANCELLED"
    
    def test_plan_priority_change_to_p0(self):
        """测试优先级变更为P0（DRAFT不能直接转到PENDING，需要先启动）"""
        plan = Plan.create(
            name="测试计划",
            category=Category("new_feature"),
            priority=Priority.from_string("P2"),
            data_tag="FEAT-20240115-001",
            created_by="admin"
        )

        # P2计划创建后应为DRAFT状态
        assert plan.status.value == "DRAFT"

        # DRAFT状态不能直接转到PENDING，会抛出异常
        # 这是符合业务规则的：只有新创建的P0计划才是PENDING状态
        with pytest.raises(ValueError, match="Invalid status transition"):
            plan.update(priority=Priority.from_string("P0"))
    
    def test_affected_modules(self):
        """测试受影响功能模块"""
        modules = [
            AffectedModule(
                module_id="mod-001",
                module_name="用户模块",
                action="update",
                after_version="v2.0.0"
            ),
            AffectedModule(
                module_id="mod-002",
                module_name="订单模块",
                action="create"
            )
        ]
        
        plan = Plan.create(
            name="测试计划",
            category=Category("func_change"),
            priority=Priority.from_string("P1"),
            data_tag="CHANGE-20240115-001",
            created_by="admin",
            affected_modules=modules
        )
        
        assert len(plan.affected_modules) == 2
        assert plan.affected_modules[0].module_name == "用户模块"
        assert plan.affected_modules[1].action == "create"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
