"""
Pytest 配置文件
提供测试所需的 fixtures 和配置
"""
import pytest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.utils.api_client import create_test_client


@pytest.fixture(scope="session")
def api_client():
    """提供 API 测试客户端"""
    return create_test_client()


@pytest.fixture(scope="function")
def unique_app_name():
    """生成唯一的应用名称"""
    import uuid
    return f"测试应用_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="function")
def test_application(api_client, unique_app_name):
    """创建测试应用并在测试结束后清理"""
    result = api_client.create_application(
        app_name=unique_app_name,
        business_owner="测试负责人",
        project_owner="测试项目",
        app_description="测试用应用系统"
    )
    
    app_id = None
    if result.success and result.data:
        app_id = result.data.get('id')
    
    yield result.data
    
    # 清理
    if app_id:
        api_client.delete_application(app_id)
