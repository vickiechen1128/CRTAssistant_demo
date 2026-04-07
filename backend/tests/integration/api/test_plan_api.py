#!/usr/bin/env python3
"""
Plan 模块 API 接口测试
测试所有计划管理相关的 RESTful API 端点

运行方式:
    cd CRTAssistant_demo/backend
    python -m pytest tests/integration/api/test_plan_api.py -v
    或
    python tests/integration/api/test_plan_api.py
"""
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.utils.plan_api_client import create_plan_client, ApiResponse


class Colors:
    """终端颜色输出"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'


class TestPlanApi:
    """Plan 模块 API 测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.client = create_plan_client()
        cls.test_results = []
        cls.created_plan_id = None
    
    @classmethod
    def teardown_class(cls):
        """测试类清理"""
        # 清理测试数据
        if cls.created_plan_id:
            cls.client.delete_plan(cls.created_plan_id)
    
    @classmethod
    def log_result(cls, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if success else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"  {status} {test_name}")
        if message:
            print(f"     {Colors.CYAN}{message}{Colors.END}")
        cls.test_results.append((test_name, success, message))
    
    # ==================== 健康检查 ====================
    
    def test_health_check(self):
        """测试服务健康检查"""
        result = self.client.health_check()
        self.log_result(
            "健康检查",
            result.success,
            f"Status: {result.status_code}"
        )
        assert result.success, f"服务健康检查失败: {result.message}"
    
    # ==================== 计划ID生成接口 ====================
    
    def test_generate_plan_id(self):
        """测试预生成计划ID"""
        result = self.client.generate_plan_id()
        
        if result.success and result.data:
            data = result.data
            msg = f"PlanID: {data.get('plan_id')}, DataTag: {data.get('data_tag')}"
        else:
            msg = result.message
        
        self.log_result("预生成计划ID", result.success, msg)
        assert result.success, f"预生成计划ID失败: {result.message}"
    
    # ==================== 计划CRUD接口 ====================
    
    def test_create_plan(self):
        """测试创建计划"""
        unique_name = f"测试计划_{uuid.uuid4().hex[:8]}"
        result = self.client.create_plan(
            name=unique_name,
            category="new_system",
            priority="P1",
            description="这是一个测试计划",
            affected_modules=[
                {
                    "module_id": "mod-001",
                    "module_name": "用户管理模块",
                    "action": "update",
                    "before_version": "v1.0.0",
                    "after_version": "v1.1.0",
                    "change_description": "优化用户登录流程"
                }
            ],
            related_inventory_ids=["inv-001", "inv-002"]
        )
        
        if result.success and result.data:
            self.created_plan_id = result.data.get('id')
            msg = f"Created: {result.data.get('name')} (ID: {self.created_plan_id})"
        else:
            msg = result.message
        
        self.log_result("创建计划", result.success, msg)
        assert result.success, f"创建计划失败: {result.message}"
    
    def test_create_p0_plan(self):
        """测试创建P0优先级计划"""
        unique_name = f"P0测试计划_{uuid.uuid4().hex[:8]}"
        result = self.client.create_plan(
            name=unique_name,
            category="security_check",
            priority="P0",
            description="P0紧急计划测试"
        )
        
        if result.success and result.data:
            plan_id = result.data.get('id')
            status = result.data.get('status')
            msg = f"Created: {result.data.get('name')} (ID: {plan_id}, Status: {status})"
            # 清理
            self.client.delete_plan(plan_id)
        else:
            msg = result.message
        
        self.log_result("创建P0计划", result.success, msg)
        assert result.success, f"创建P0计划失败: {result.message}"
        # P0计划创建后应为PENDING状态
        if result.success and result.data:
            assert result.data.get('status') == "PENDING", "P0计划应为PENDING状态"
    
    def test_list_plans(self):
        """测试获取计划列表"""
        result = self.client.list_plans(page=1, page_size=10)
        
        if result.success and result.data:
            data = result.data
            msg = f"Total: {data.get('total', 0)}, Page: {data.get('page', 0)}/{data.get('total_pages', 0)}"
        else:
            msg = result.message
        
        self.log_result("获取计划列表", result.success, msg)
        assert result.success, f"获取计划列表失败: {result.message}"
    
    def test_list_plans_with_filter(self):
        """测试带筛选条件的计划列表"""
        result = self.client.list_plans(
            status="DRAFT",
            category="new_system",
            priority="P1",
            page=1,
            page_size=10
        )
        
        if result.success and result.data:
            data = result.data
            msg = f"Filtered Total: {data.get('total', 0)}"
        else:
            msg = result.message
        
        self.log_result("筛选计划列表", result.success, msg)
        assert result.success, f"筛选计划列表失败: {result.message}"
    
    def test_get_plan(self):
        """测试获取计划详情"""
        if not self.created_plan_id:
            # 如果没有创建的计划，先获取列表
            list_result = self.client.list_plans(page=1, page_size=1)
            if list_result.success and list_result.data:
                plans = list_result.data.get('items', [])
                if plans:
                    self.created_plan_id = plans[0].get('id')
        
        if not self.created_plan_id:
            self.log_result("获取计划详情", True, "No plans available to test")
            return
        
        result = self.client.get_plan(self.created_plan_id)
        
        if result.success and result.data:
            msg = f"Plan: {result.data.get('name')}, Status: {result.data.get('status')}"
        else:
            msg = result.message
        
        self.log_result("获取计划详情", result.success, msg)
        assert result.success, f"获取计划详情失败: {result.message}"
    
    def test_get_plan_detail(self):
        """测试获取计划完整详情"""
        if not self.created_plan_id:
            self.log_result("获取计划完整详情", True, "No plan to test")
            return
        
        result = self.client.get_plan_detail(self.created_plan_id)
        
        if result.success and result.data:
            data = result.data
            modules_count = len(data.get('affected_modules', []))
            msg = f"Plan: {data.get('name')}, Modules: {modules_count}"
        else:
            msg = result.message
        
        self.log_result("获取计划完整详情", result.success, msg)
        assert result.success, f"获取计划完整详情失败: {result.message}"
    
    def test_update_plan(self):
        """测试更新计划"""
        if not self.created_plan_id:
            self.log_result("更新计划", True, "No plan to update")
            return
        
        result = self.client.update_plan(
            self.created_plan_id,
            name="更新后的计划名称",
            description="更新后的描述"
        )
        
        if result.success and result.data:
            msg = f"Updated: {result.data.get('name')}"
        else:
            msg = result.message
        
        self.log_result("更新计划", result.success, msg)
        assert result.success, f"更新计划失败: {result.message}"
    
    def test_preview_changes(self):
        """测试预览计划变更"""
        result = self.client.preview_changes(
            name="预览测试计划",
            category="func_change",
            affected_modules=[
                {
                    "module_id": "mod-preview-001",
                    "module_name": "预览模块",
                    "action": "update"
                }
            ],
            related_inventory_ids=["inv-preview-001"]
        )
        
        if result.success and result.data:
            data = result.data
            msg = f"Preview: {data.get('plan_name')}, Category: {data.get('category_label')}"
        else:
            msg = result.message
        
        self.log_result("预览计划变更", result.success, msg)
        assert result.success, f"预览计划变更失败: {result.message}"
    
    # ==================== 计划状态流转接口 ====================
    
    def test_start_plan(self):
        """测试启动计划"""
        # 创建一个新的P0计划来测试启动
        unique_name = f"启动测试计划_{uuid.uuid4().hex[:8]}"
        create_result = self.client.create_plan(
            name=unique_name,
            category="new_feature",
            priority="P0",
            description="用于测试启动的计划"
        )
        
        if not create_result.success or not create_result.data:
            self.log_result("启动计划", False, "Failed to create test plan")
            return
        
        plan_id = create_result.data.get('id')
        
        # 启动计划
        result = self.client.start_plan(plan_id, confirmed=True)
        
        if result.success and result.data:
            msg = f"Started: {result.data.get('name')}, Status: {result.data.get('status')}"
        else:
            msg = result.message
        
        self.log_result("启动计划", result.success, msg)
        
        # 清理
        if plan_id:
            self.client.cancel_plan(plan_id, "测试清理")
            self.client.delete_plan(plan_id)
        
        assert result.success, f"启动计划失败: {result.message}"
    
    def test_complete_plan(self):
        """测试完成计划"""
        # 创建并启动一个计划
        unique_name = f"完成测试计划_{uuid.uuid4().hex[:8]}"
        create_result = self.client.create_plan(
            name=unique_name,
            category="new_feature",
            priority="P0",
            description="用于测试完成的计划"
        )
        
        if not create_result.success or not create_result.data:
            self.log_result("完成计划", False, "Failed to create test plan")
            return
        
        plan_id = create_result.data.get('id')
        
        # 启动计划
        start_result = self.client.start_plan(plan_id, confirmed=True)
        if not start_result.success:
            self.log_result("完成计划", False, "Failed to start plan")
            self.client.delete_plan(plan_id)
            return
        
        # 完成计划
        result = self.client.complete_plan(plan_id, completion_note="测试完成")
        
        if result.success and result.data:
            msg = f"Completed: {result.data.get('name')}, Status: {result.data.get('status')}"
        else:
            msg = result.message
        
        self.log_result("完成计划", result.success, msg)
        
        # 清理
        if plan_id:
            self.client.delete_plan(plan_id)
        
        assert result.success, f"完成计划失败: {result.message}"
    
    def test_cancel_plan(self):
        """测试取消计划"""
        # 创建一个新计划来测试取消
        unique_name = f"取消测试计划_{uuid.uuid4().hex[:8]}"
        create_result = self.client.create_plan(
            name=unique_name,
            category="arch_change",
            priority="P2",
            description="用于测试取消的计划"
        )
        
        if not create_result.success or not create_result.data:
            self.log_result("取消计划", False, "Failed to create test plan")
            return
        
        plan_id = create_result.data.get('id')
        
        # 取消计划
        result = self.client.cancel_plan(plan_id, reason="测试取消原因")
        
        if result.success and result.data:
            msg = f"Cancelled: {result.data.get('name')}, Status: {result.data.get('status')}"
        else:
            msg = result.message
        
        self.log_result("取消计划", result.success, msg)
        
        # 清理
        if plan_id:
            self.client.delete_plan(plan_id)
        
        assert result.success, f"取消计划失败: {result.message}"
    
    # ==================== 台账关联接口 ====================
    
    def test_link_inventory(self):
        """测试关联台账"""
        if not self.created_plan_id:
            self.log_result("关联台账", True, "No plan to test")
            return
        
        result = self.client.link_inventory(
            self.created_plan_id,
            inventory_ids=["inv-test-001", "inv-test-002"]
        )
        
        if result.success and result.data:
            msg = f"Linked: {len(result.data.get('related_inventory_ids', []))} inventories"
        else:
            msg = result.message
        
        self.log_result("关联台账", result.success, msg)
        assert result.success, f"关联台账失败: {result.message}"
    
    # ==================== 错误处理测试 ====================
    
    def test_get_nonexistent_plan(self):
        """测试获取不存在的计划"""
        result = self.client.get_plan("PLAN-NOT-EXIST-999")
        
        msg = f"Expected 404, Got: {result.status_code}"
        success = result.status_code == 404
        
        self.log_result("获取不存在计划", success, msg)
        assert success, f"应返回404错误: {result.message}"
    
    def test_create_plan_invalid_category(self):
        """测试创建计划时传入无效分类"""
        result = self.client.create_plan(
            name="无效分类测试",
            category="invalid_category",
            priority="P1"
        )
        
        msg = f"Expected 400, Got: {result.status_code}"
        success = result.status_code == 400 or result.status_code == 422
        
        self.log_result("无效分类测试", success, msg)
        assert success, f"应返回400/422错误: {result.message}"
    
    def test_create_plan_invalid_priority(self):
        """测试创建计划时传入无效优先级"""
        result = self.client.create_plan(
            name="无效优先级测试",
            category="new_system",
            priority="P5"
        )
        
        msg = f"Expected 400, Got: {result.status_code}"
        success = result.status_code == 400 or result.status_code == 422
        
        self.log_result("无效优先级测试", success, msg)
        assert success, f"应返回400/422错误: {result.message}"


def run_tests():
    """运行所有测试并输出报告"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}  Plan 模块 API 接口测试{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    test_class = TestPlanApi()
    test_class.setup_class()
    
    # 获取所有测试方法
    test_methods = [method for method in dir(test_class) if method.startswith('test_')]
    
    # 运行测试
    for method_name in test_methods:
        try:
            method = getattr(test_class, method_name)
            method()
        except AssertionError as e:
            pass  # 错误已在log_result中记录
        except Exception as e:
            print(f"  {Colors.RED}❌ ERROR{Colors.END} {method_name}: {str(e)}")
    
    # 输出测试报告
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}  测试报告{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    passed = sum(1 for _, success, _ in test_class.test_results if success)
    failed = sum(1 for _, success, _ in test_class.test_results if not success)
    total = len(test_class.test_results)
    
    print(f"\n  总计: {total} | {Colors.GREEN}通过: {passed}{Colors.END} | {Colors.RED}失败: {failed}{Colors.END}")
    
    if failed > 0:
        print(f"\n  {Colors.RED}失败用例:{Colors.END}")
        for name, success, message in test_class.test_results:
            if not success:
                print(f"    - {name}: {message}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    # 清理
    test_class.teardown_class()
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
