#!/usr/bin/env python3
"""
计划模块应用服务单元测试
测试PlanService的业务逻辑

运行方式:
    cd CRTAssistant_demo/backend
    python -m pytest tests/unit/test_plan_service.py -v
"""
import sys
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.modules.plan.application.plan_service import PlanService
from app.modules.plan.application.dtos.plan_dtos import (
    CreatePlanRequest,
    UpdatePlanRequest,
    PlanFilterRequest,
    PlanPreviewRequest,
    AffectedModuleItem,
    ApprovalFileDetail,
)
from app.modules.plan.domain.entities.plan import Plan
from app.modules.plan.domain.value_objects.category import Category
from app.modules.plan.domain.value_objects.priority import Priority
from app.modules.plan.domain.value_objects.plan_status import PlanStatus


class TestPlanService:
    """测试计划应用服务"""
    
    @pytest.fixture
    def mock_repository(self):
        """模拟仓储"""
        return Mock()
    
    @pytest.fixture
    def mock_domain_service(self):
        """模拟领域服务"""
        service = Mock()
        service.generate_data_tag.return_value = "NEW-20240115-001"
        service.get_next_sequence.return_value = 1
        return service
    
    @pytest.fixture
    def plan_service(self, mock_repository, mock_domain_service):
        """创建PlanService实例"""
        return PlanService(mock_repository, mock_domain_service)
    
    @pytest.fixture
    def sample_create_request(self):
        """示例创建请求"""
        return CreatePlanRequest(
            name="测试计划",
            category="new_system",
            priority="P1",
            description="这是一个测试计划",
            affected_modules=[
                AffectedModuleItem(
                    module_id="mod-001",
                    module_name="用户模块",
                    action="update"
                )
            ],
            related_inventory_ids=["inv-001", "inv-002"]
        )
    
    def test_create_plan(self, plan_service, mock_repository, mock_domain_service, sample_create_request):
        """测试创建计划"""
        # 使用真实的Plan对象作为返回值
        real_plan = Plan.create(
            name="测试计划",
            category=Category("new_system"),
            priority=Priority.from_string("P1"),
            data_tag="NEW-20240115-001",
            created_by="admin",
            description="这是一个测试计划"
        )
        real_plan.inventory_ids = ["inv-001", "inv-002"]
        
        mock_repository.save.return_value = real_plan
        
        # 执行测试
        result = plan_service.create_plan(sample_create_request, "admin")
        
        # 验证
        assert result.name == "测试计划"
        assert result.category == "new_system"
        assert result.priority == "P1"
        assert result.created_by == "admin"
        mock_repository.save.assert_called_once()
    
    def test_create_p0_plan(self, plan_service, mock_repository, sample_create_request):
        """测试创建P0优先级计划"""
        sample_create_request.priority = "P0"
        sample_create_request.category = "security_check"
        
        real_plan = Plan.create(
            name="测试计划",
            category=Category("security_check"),
            priority=Priority.from_string("P0"),
            data_tag="SEC-20240115-001",
            created_by="admin"
        )
        
        mock_repository.save.return_value = real_plan
        
        result = plan_service.create_plan(sample_create_request, "admin")
        
        assert result.priority == "P0"
        assert result.status == "PENDING"  # P0计划应为PENDING状态
    
    def test_get_plan(self, plan_service, mock_repository):
        """测试获取计划"""
        real_plan = Plan.create(
            name="测试计划",
            category=Category("new_system"),
            priority=Priority.from_string("P1"),
            data_tag="NEW-20240115-001",
            created_by="admin"
        )
        
        mock_repository.find_by_id.return_value = real_plan
        
        result = plan_service.get_plan("PLAN-20240115-0001")
        
        assert result.name == "测试计划"
        assert result.category == "new_system"
        mock_repository.find_by_id.assert_called_once_with("PLAN-20240115-0001")
    
    def test_get_plan_not_found(self, plan_service, mock_repository):
        """测试获取不存在的计划"""
        mock_repository.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Plan not found"):
            plan_service.get_plan("PLAN-NOT-EXIST")
    
    def test_delete_plan(self, plan_service, mock_repository):
        """测试删除计划"""
        real_plan = Plan.create(
            name="测试计划",
            category=Category("new_system"),
            priority=Priority.from_string("P1"),
            data_tag="NEW-20240115-001",
            created_by="admin"
        )
        
        mock_repository.find_by_id.return_value = real_plan
        mock_repository.delete.return_value = True
        
        result = plan_service.delete_plan("PLAN-20240115-0001", "admin")
        
        assert result is True
        mock_repository.delete.assert_called_once()
    
    def test_start_plan(self, plan_service, mock_repository):
        """测试启动计划"""
        real_plan = Plan.create(
            name="测试计划",
            category=Category("new_system"),
            priority=Priority.from_string("P0"),
            data_tag="NEW-20240115-001",
            created_by="admin"
        )
        
        mock_repository.find_by_id.return_value = real_plan
        mock_repository.save.return_value = real_plan
        
        result = plan_service.start_plan("PLAN-20240115-0001", "admin")
        
        assert real_plan.status.value == "IN_PROGRESS"
    
    def test_complete_plan(self, plan_service, mock_repository):
        """测试完成计划"""
        real_plan = Plan.create(
            name="测试计划",
            category=Category("new_system"),
            priority=Priority.from_string("P0"),
            data_tag="NEW-20240115-001",
            created_by="admin"
        )
        real_plan.start("admin")  # 先启动
        
        mock_repository.find_by_id.return_value = real_plan
        mock_repository.save.return_value = real_plan
        
        result = plan_service.complete_plan("PLAN-20240115-0001", "admin")
        
        assert real_plan.status.value == "COMPLETED"
    
    def test_cancel_plan(self, plan_service, mock_repository):
        """测试取消计划"""
        real_plan = Plan.create(
            name="测试计划",
            category=Category("new_system"),
            priority=Priority.from_string("P1"),
            data_tag="NEW-20240115-001",
            created_by="admin"
        )
        
        mock_repository.find_by_id.return_value = real_plan
        mock_repository.save.return_value = real_plan
        
        result = plan_service.cancel_plan("PLAN-20240115-0001", "admin", "取消原因")
        
        assert real_plan.status.value == "CANCELLED"
    
    def test_list_plans(self, plan_service, mock_repository):
        """测试查询计划列表"""
        real_plan = Plan.create(
            name="测试计划",
            category=Category("new_system"),
            priority=Priority.from_string("P1"),
            data_tag="NEW-20240115-001",
            created_by="admin"
        )
        
        mock_repository.find_all.return_value = ([real_plan], 1)
        
        filter_request = PlanFilterRequest(
            status="DRAFT",
            page=1,
            page_size=20
        )
        
        result = plan_service.list_plans(filter_request)
        
        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].name == "测试计划"
    
    def test_generate_plan_id(self, plan_service, mock_repository, mock_domain_service):
        """测试生成计划ID"""
        mock_domain_service.generate_plan_id.return_value = "PLAN-20240115-0001"
        mock_domain_service.generate_data_tag.return_value = "NEW-20240115-001"
        
        result = plan_service.generate_plan_id()
        
        assert result.plan_id.startswith("PLAN-")
        assert result.data_tag.startswith("NEW-")
    
    def test_preview_changes(self, plan_service, mock_repository):
        """测试预览计划变更"""
        preview_request = PlanPreviewRequest(
            name="预览测试计划",
            category="new_feature",
            affected_modules=[
                AffectedModuleItem(
                    module_id="mod-001",
                    module_name="用户模块",
                    action="create",
                    after_version="v1.0.0"
                )
            ],
            related_inventory_ids=["inv-001"]
        )
        
        result = plan_service.preview_changes(preview_request)
        
        assert result.plan_name == "预览测试计划"
        assert result.category == "new_feature"
        assert len(result.inventory_changes) == 1
        assert result.inventory_changes[0]["change_object"] == "用户模块"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
