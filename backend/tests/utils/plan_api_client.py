#!/usr/bin/env python3
"""
计划模块 API 测试客户端
提供计划管理相关的 API 测试接口调用方法
"""
import requests
import uuid
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ApiResponse:
    """API 响应包装类"""
    success: bool
    status_code: int
    data: Any
    message: str = ""


class PlanApiClient:
    """计划模块 API 测试客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    # ==================== 健康检查 ====================
    
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
    
    # ==================== 计划管理接口 ====================
    
    def create_plan(
        self,
        name: str,
        category: str,
        priority: str,
        description: Optional[str] = None,
        planned_start_time: Optional[datetime] = None,
        planned_end_time: Optional[datetime] = None,
        workflow_template_id: Optional[str] = None,
        template_type: Optional[str] = None,
        affected_modules: Optional[List[Dict]] = None,
        approval_files: Optional[List[Dict]] = None,
        related_inventory_ids: Optional[List[str]] = None,
        idempotency_key: Optional[str] = None
    ) -> ApiResponse:
        """创建计划"""
        payload = {
            "name": name,
            "category": category,
            "priority": priority,
            "description": description,
            "planned_start_time": planned_start_time.isoformat() if planned_start_time else None,
            "planned_end_time": planned_end_time.isoformat() if planned_end_time else None,
            "workflow_template_id": workflow_template_id,
            "template_type": template_type,
            "affected_modules": affected_modules or [],
            "approval_files": approval_files or [],
            "related_inventory_ids": related_inventory_ids or [],
            "idempotency_key": idempotency_key or str(uuid.uuid4())
        }
        # 移除 None 值
        payload = {k: v for k, v in payload.items() if v is not None}
        
        try:
            resp = self.session.post(
                f"{self.base_url}/plans",
                json=payload,
                timeout=10
            )
            return ApiResponse(
                success=resp.status_code == 200,
                status_code=resp.status_code,
                data=resp.json().get('data') if resp.status_code == 200 else None,
                message=resp.json().get('message', resp.text[:200]) if resp.status_code != 200 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))
    
    def list_plans(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> ApiResponse:
        """获取计划列表"""
        params = {"page": page, "page_size": page_size}
        if status:
            params["status"] = status
        if category:
            params["category"] = category
        if priority:
            params["priority"] = priority
        if keyword:
            params["keyword"] = keyword
        
        try:
            resp = self.session.get(
                f"{self.base_url}/plans",
                params=params,
                timeout=5
            )
            return ApiResponse(
                success=resp.status_code == 200,
                status_code=resp.status_code,
                data=resp.json().get('data') if resp.status_code == 200 else None,
                message=resp.text[:200] if resp.status_code != 200 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))
    
    def get_plan(self, plan_id: str) -> ApiResponse:
        """获取计划详情"""
        try:
            resp = self.session.get(
                f"{self.base_url}/plans/{plan_id}",
                timeout=5
            )
            return ApiResponse(
                success=resp.status_code == 200,
                status_code=resp.status_code,
                data=resp.json().get('data') if resp.status_code == 200 else None,
                message=resp.text[:200] if resp.status_code != 200 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))
    
    def get_plan_detail(self, plan_id: str) -> ApiResponse:
        """获取计划完整详情"""
        try:
            resp = self.session.get(
                f"{self.base_url}/plans/{plan_id}/detail",
                timeout=5
            )
            return ApiResponse(
                success=resp.status_code == 200,
                status_code=resp.status_code,
                data=resp.json().get('data') if resp.status_code == 200 else None,
                message=resp.text[:200] if resp.status_code != 200 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))
    
    def update_plan(
        self,
        plan_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        planned_start_time: Optional[datetime] = None,
        planned_end_time: Optional[datetime] = None,
        priority: Optional[str] = None,
        affected_modules: Optional[List[Dict]] = None
    ) -> ApiResponse:
        """更新计划"""
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if planned_start_time is not None:
            payload["planned_start_time"] = planned_start_time.isoformat()
        if planned_end_time is not None:
            payload["planned_end_time"] = planned_end_time.isoformat()
        if priority is not None:
            payload["priority"] = priority
        if affected_modules is not None:
            payload["affected_modules"] = affected_modules
        
        try:
            resp = self.session.put(
                f"{self.base_url}/plans/{plan_id}",
                json=payload,
                timeout=5
            )
            return ApiResponse(
                success=resp.status_code == 200,
                status_code=resp.status_code,
                data=resp.json().get('data') if resp.status_code == 200 else None,
                message=resp.text[:200] if resp.status_code != 200 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))
    
    def delete_plan(self, plan_id: str) -> ApiResponse:
        """删除计划"""
        try:
            resp = self.session.delete(
                f"{self.base_url}/plans/{plan_id}",
                timeout=5
            )
            return ApiResponse(
                success=resp.status_code == 200,
                status_code=resp.status_code,
                data=resp.json().get('data') if resp.status_code == 200 else None,
                message=resp.json().get('message', resp.text[:200]) if resp.status_code != 200 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))
    
    def generate_plan_id(self) -> ApiResponse:
        """预生成计划ID"""
        try:
            resp = self.session.get(
                f"{self.base_url}/plans/generate-id",
                timeout=5
            )
            return ApiResponse(
                success=resp.status_code == 200,
                status_code=resp.status_code,
                data=resp.json().get('data') if resp.status_code == 200 else None,
                message=resp.text[:200] if resp.status_code != 200 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))
    
    def preview_changes(
        self,
        name: str,
        category: str,
        affected_modules: Optional[List[Dict]] = None,
        related_inventory_ids: Optional[List[str]] = None
    ) -> ApiResponse:
        """预览计划变更"""
        payload = {
            "name": name,
            "category": category,
            "affected_modules": affected_modules or [],
            "related_inventory_ids": related_inventory_ids or []
        }
        
        try:
            resp = self.session.post(
                f"{self.base_url}/plans/preview",
                json=payload,
                timeout=5
            )
            return ApiResponse(
                success=resp.status_code == 200,
                status_code=resp.status_code,
                data=resp.json().get('data') if resp.status_code == 200 else None,
                message=resp.text[:200] if resp.status_code != 200 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))
    
    # ==================== 计划状态流转接口 ====================
    
    def start_plan(self, plan_id: str, confirmed: bool = False, confirmation_note: Optional[str] = None) -> ApiResponse:
        """启动计划"""
        payload = {"confirmed": confirmed}
        if confirmation_note:
            payload["confirmation_note"] = confirmation_note
        
        try:
            resp = self.session.post(
                f"{self.base_url}/plans/{plan_id}/start",
                json=payload,
                timeout=5
            )
            return ApiResponse(
                success=resp.status_code == 200,
                status_code=resp.status_code,
                data=resp.json().get('data') if resp.status_code == 200 else None,
                message=resp.json().get('message', resp.text[:200]) if resp.status_code != 200 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))
    
    def complete_plan(self, plan_id: str, completion_note: Optional[str] = None) -> ApiResponse:
        """完成计划"""
        payload = {}
        if completion_note:
            payload["completion_note"] = completion_note
        
        try:
            resp = self.session.post(
                f"{self.base_url}/plans/{plan_id}/complete",
                json=payload,
                timeout=5
            )
            return ApiResponse(
                success=resp.status_code == 200,
                status_code=resp.status_code,
                data=resp.json().get('data') if resp.status_code == 200 else None,
                message=resp.json().get('message', resp.text[:200]) if resp.status_code != 200 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))
    
    def cancel_plan(self, plan_id: str, reason: str) -> ApiResponse:
        """取消计划"""
        payload = {"reason": reason}
        
        try:
            resp = self.session.post(
                f"{self.base_url}/plans/{plan_id}/cancel",
                json=payload,
                timeout=5
            )
            return ApiResponse(
                success=resp.status_code == 200,
                status_code=resp.status_code,
                data=resp.json().get('data') if resp.status_code == 200 else None,
                message=resp.json().get('message', resp.text[:200]) if resp.status_code != 200 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))
    
    # ==================== 台账关联接口 ====================
    
    def link_inventory(self, plan_id: str, inventory_ids: List[str]) -> ApiResponse:
        """关联台账"""
        payload = {"inventory_ids": inventory_ids}
        
        try:
            resp = self.session.post(
                f"{self.base_url}/plans/{plan_id}/inventory",
                json=payload,
                timeout=5
            )
            return ApiResponse(
                success=resp.status_code == 200,
                status_code=resp.status_code,
                data=resp.json().get('data') if resp.status_code == 200 else None,
                message=resp.json().get('message', resp.text[:200]) if resp.status_code != 200 else ""
            )
        except Exception as e:
            return ApiResponse(success=False, status_code=0, data=None, message=str(e))


def create_plan_client(base_url: str = "http://localhost:8000/api/v1") -> PlanApiClient:
    """创建计划API客户端"""
    return PlanApiClient(base_url)
