"""
API 测试客户端
提供统一的 API 测试接口调用方法
"""
import requests
import uuid
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class ApiResponse:
    """API 响应包装类"""
    success: bool
    status_code: int
    data: Any
    message: str = ""


class InventoryApiClient:
    """台账模块 API 测试客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def health_check(self) -> ApiResponse:
        """健康检查"""
        try:
            resp = self.session.get(f"{self.base_url.replace('/api/v1', '')}/health", timeout=5)
            return ApiResponse(
                success=resp.status_code == 200,
                status_code=resp.status_code,
                data=resp.json() if resp.status_code == 200 else None,
                message="Service is healthy" if resp.status_code == 200 else resp.text
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))
    
    # ==================== 台账汇总接口 ====================
    
    def get_inventory_summary(self) -> ApiResponse:
        """获取台账汇总统计"""
        try:
            resp = self.session.get(f"{self.base_url}/inventory/summary", timeout=5)
            return ApiResponse(
                success=resp.status_code == 200,
                status_code=resp.status_code,
                data=resp.json() if resp.status_code == 200 else None,
                message=resp.text[:200] if resp.status_code != 200 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))
    
    # ==================== 应用系统接口 ====================
    
    def create_application(
        self,
        app_name: str,
        business_owner: str,
        project_owner: str,
        app_description: Optional[str] = None,
        hostname: Optional[str] = None,
        app_url: Optional[str] = None,
        function_modules: Optional[List[Dict]] = None,
        launch_time: Optional[str] = None
    ) -> ApiResponse:
        """创建应用系统"""
        payload = {
            "app_name": app_name,
            "business_owner": business_owner,
            "project_owner": project_owner,
            "app_description": app_description,
            "hostname": hostname,
            "app_url": app_url,
            "function_modules": function_modules,
            "launch_time": launch_time
        }
        # 移除 None 值
        payload = {k: v for k, v in payload.items() if v is not None}
        
        try:
            resp = self.session.post(
                f"{self.base_url}/inventory/applications",
                json=payload,
                timeout=5
            )
            return ApiResponse(
                success=resp.status_code == 201,
                status_code=resp.status_code,
                data=resp.json() if resp.status_code == 201 else None,
                message=resp.text[:200] if resp.status_code != 201 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))
    
    def list_applications(
        self,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> ApiResponse:
        """获取应用系统列表"""
        params = {"page": page, "size": size}
        if status:
            params["status"] = status
        if keyword:
            params["keyword"] = keyword
        
        try:
            resp = self.session.get(
                f"{self.base_url}/inventory/applications",
                params=params,
                timeout=5
            )
            return ApiResponse(
                success=resp.status_code == 200,
                status_code=resp.status_code,
                data=resp.json() if resp.status_code == 200 else None,
                message=resp.text[:200] if resp.status_code != 200 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))
    
    def get_application(self, app_id: str) -> ApiResponse:
        """获取应用系统详情"""
        try:
            resp = self.session.get(
                f"{self.base_url}/inventory/applications/{app_id}",
                timeout=5
            )
            return ApiResponse(
                success=resp.status_code == 200,
                status_code=resp.status_code,
                data=resp.json() if resp.status_code == 200 else None,
                message=resp.text[:200] if resp.status_code != 200 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))
    
    def update_application(self, app_id: str, **kwargs) -> ApiResponse:
        """更新应用系统"""
        try:
            resp = self.session.put(
                f"{self.base_url}/inventory/applications/{app_id}",
                json=kwargs,
                timeout=5
            )
            return ApiResponse(
                success=resp.status_code == 200,
                status_code=resp.status_code,
                data=resp.json() if resp.status_code == 200 else None,
                message=resp.text[:200] if resp.status_code != 200 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))
    
    def delete_application(self, app_id: str) -> ApiResponse:
        """删除应用系统"""
        try:
            resp = self.session.delete(
                f"{self.base_url}/inventory/applications/{app_id}",
                timeout=5
            )
            return ApiResponse(
                success=resp.status_code == 204,
                status_code=resp.status_code,
                data=None,
                message=resp.text[:200] if resp.status_code != 204 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))
    
    # ==================== 云资源接口 ====================
    
    def list_cloud_resources(
        self,
        app_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> ApiResponse:
        """获取云资源列表"""
        params = {"page": page, "size": size}
        if app_id:
            params["app_id"] = app_id
        if resource_type:
            params["resource_type"] = resource_type
        if keyword:
            params["keyword"] = keyword
        
        try:
            resp = self.session.get(
                f"{self.base_url}/inventory/cloud-resources",
                params=params,
                timeout=5
            )
            return ApiResponse(
                success=resp.status_code == 200,
                status_code=resp.status_code,
                data=resp.json() if resp.status_code == 200 else None,
                message=resp.text[:200] if resp.status_code != 200 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))
    
    # ==================== 账号接口 ====================
    
    def list_accounts(
        self,
        app_id: Optional[str] = None,
        account_type: Optional[str] = None,
        status: Optional[str] = None,
        permission_level: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> ApiResponse:
        """获取账号列表"""
        params = {"page": page, "size": size}
        if app_id:
            params["app_id"] = app_id
        if account_type:
            params["account_type"] = account_type
        if status:
            params["status"] = status
        if permission_level:
            params["permission_level"] = permission_level
        if keyword:
            params["keyword"] = keyword
        
        try:
            resp = self.session.get(
                f"{self.base_url}/inventory/accounts",
                params=params,
                timeout=5
            )
            return ApiResponse(
                success=resp.status_code == 200,
                status_code=resp.status_code,
                data=resp.json() if resp.status_code == 200 else None,
                message=resp.text[:200] if resp.status_code != 200 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))


def create_test_client(base_url: str = "http://localhost:8000/api/v1") -> InventoryApiClient:
    """创建测试客户端的工厂函数"""
    return InventoryApiClient(base_url)
