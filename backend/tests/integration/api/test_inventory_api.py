#!/usr/bin/env python3
"""
Inventory 模块 API 接口测试
测试所有台账管理相关的 RESTful API 端点

运行方式:
    cd CRTAssistant_demo/backend
    python -m pytest tests/integration/api/test_inventory_api.py -v
    或
    python tests/integration/api/test_inventory_api.py
"""
import sys
import uuid
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.utils.api_client import create_test_client, ApiResponse


class Colors:
    """终端颜色输出"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'


class TestInventoryApi:
    """Inventory 模块 API 测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        cls.client = create_test_client()
        cls.test_results = []
        cls.created_app_id = None
    
    @classmethod
    def teardown_class(cls):
        """测试类清理"""
        # 清理测试数据
        if cls.created_app_id:
            cls.client.delete_application(cls.created_app_id)
    
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
    
    # ==================== 台账汇总接口 ====================
    
    def test_get_inventory_summary(self):
        """测试获取台账汇总统计"""
        result = self.client.get_inventory_summary()
        
        if result.success and result.data:
            data = result.data
            msg = f"Apps: {data.get('application_count', 0)}, " \
                  f"Resources: {data.get('cloud_resource_count', 0)}, " \
                  f"Accounts: {data.get('account_count', 0)}"
        else:
            msg = result.message
        
        self.log_result("台账汇总接口", result.success, msg)
        assert result.success, f"获取台账汇总失败: {result.message}"
    
    # ==================== 应用系统接口 ====================
    
    def test_create_application(self):
        """测试创建应用系统"""
        unique_name = f"测试应用_{uuid.uuid4().hex[:8]}"
        result = self.client.create_application(
            app_name=unique_name,
            business_owner="张三",
            project_owner="李四",
            app_description="这是一个测试应用系统",
            hostname="test-server-01",
            app_url="http://test.example.com"
        )
        
        if result.success and result.data:
            self.created_app_id = result.data.get('id')
            msg = f"Created: {result.data.get('app_name')} (ID: {self.created_app_id[:8]}...)"
        else:
            msg = result.message
        
        self.log_result("创建应用系统", result.success, msg)
        assert result.success, f"创建应用系统失败: {result.message}"
    
    def test_list_applications(self):
        """测试获取应用系统列表"""
        result = self.client.list_applications(page=1, size=10)
        
        if result.success and result.data:
            data = result.data
            msg = f"Total: {data.get('total', 0)}, Page: {data.get('page', 0)}/{data.get('total_pages', 0)}"
        else:
            msg = result.message
        
        self.log_result("获取应用系统列表", result.success, msg)
        assert result.success, f"获取应用系统列表失败: {result.message}"
    
    def test_get_application_detail(self):
        """测试获取应用系统详情"""
        # 如果没有创建的应用，先获取列表
        if not self.created_app_id:
            list_result = self.client.list_applications(page=1, size=1)
            if list_result.success and list_result.data:
                apps = list_result.data.get('data', [])
                if apps:
                    self.created_app_id = apps[0].get('id')
        
        if not self.created_app_id:
            self.log_result("获取应用系统详情", True, "No apps available to test")
            return
        
        result = self.client.get_application(self.created_app_id)
        
        if result.success and result.data:
            msg = f"App: {result.data.get('app_name')}, Status: {result.data.get('status')}"
        else:
            msg = result.message
        
        self.log_result("获取应用系统详情", result.success, msg)
        assert result.success, f"获取应用系统详情失败: {result.message}"
    
    def test_update_application(self):
        """测试更新应用系统"""
        if not self.created_app_id:
            self.log_result("更新应用系统", True, "No app to update")
            return
        
        result = self.client.update_application(
            self.created_app_id,
            app_description="Updated description",
            hostname="updated-server-01"
        )
        
        if result.success and result.data:
            msg = f"Updated: {result.data.get('app_name')}"
        else:
            msg = result.message
        
        self.log_result("更新应用系统", result.success, msg)
        assert result.success, f"更新应用系统失败: {result.message}"
    
    # ==================== 云资源接口 ====================
    
    def test_list_cloud_resources(self):
        """测试获取云资源列表"""
        result = self.client.list_cloud_resources(page=1, size=10)
        
        if result.success and result.data:
            msg = f"Total: {result.data.get('total', 0)}"
        else:
            msg = result.message
        
        self.log_result("获取云资源列表", result.success, msg)
        assert result.success, f"获取云资源列表失败: {result.message}"
    
    # ==================== 账号接口 ====================
    
    def test_list_accounts(self):
        """测试获取账号列表"""
        result = self.client.list_accounts(page=1, size=10)
        
        if result.success and result.data:
            msg = f"Total: {result.data.get('total', 0)}"
        else:
            msg = result.message
        
        self.log_result("获取账号列表", result.success, msg)
        assert result.success, f"获取账号列表失败: {result.message}"


def run_tests():
    """运行所有测试并输出报告"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}  Inventory 模块 API 接口测试{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    test_class = TestInventoryApi()
    test_class.setup_class()
    
    # 获取所有测试方法
    test_methods = [
        method for method in dir(test_class)
        if method.startswith('test_') and callable(getattr(test_class, method))
    ]
    
    passed = 0
    failed = 0
    
    for method_name in test_methods:
        try:
            method = getattr(test_class, method_name)
            method()
            passed += 1
        except AssertionError as e:
            print(f"     {Colors.RED}Assertion Error: {e}{Colors.END}")
            failed += 1
        except Exception as e:
            print(f"     {Colors.RED}Exception: {e}{Colors.END}")
            failed += 1
    
    test_class.teardown_class()
    
    # 输出测试报告
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}  测试报告{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"  {Colors.GREEN}通过: {passed}{Colors.END}")
    print(f"  {Colors.RED}失败: {failed}{Colors.END}")
    print(f"  {Colors.YELLOW}总计: {passed + failed}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
