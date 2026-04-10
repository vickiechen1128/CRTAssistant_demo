"""
功能模块API Schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, validator


class FunctionModuleBaseSchema(BaseModel):
    """功能模块基础Schema"""
    module_code: str = Field(..., max_length=50, description="模块编码")
    module_name: str = Field(..., max_length=100, description="模块名称")
    version: str = Field(default="1.0.0", max_length=20, description="版本号")
    description: Optional[str] = Field(None, description="模块描述")


class FunctionModuleCreateSchema(FunctionModuleBaseSchema):
    """创建功能模块请求Schema"""
    parent_module_id: Optional[str] = Field(None, description="父模块ID")
    related_plan_id: Optional[str] = Field(None, description="关联计划ID")


class FunctionModuleUpdateSchema(BaseModel):
    """更新功能模块请求Schema"""
    module_name: Optional[str] = Field(None, max_length=100, description="模块名称")
    description: Optional[str] = Field(None, description="模块描述")
    parent_module_id: Optional[str] = Field(None, description="父模块ID")


class UpdateModuleStatusSchema(BaseModel):
    """更新功能模块状态请求Schema"""
    status: str = Field(
        ...,
        pattern="^(draft|developing|testing|online|offline)$",
        description="状态: draft/developing/testing/online/offline"
    )


class LaunchModuleSchema(BaseModel):
    """上线功能模块请求Schema"""
    plan_id: str = Field(..., description="关联计划ID")


class FunctionModuleResponseSchema(BaseModel):
    """功能模块响应Schema"""
    id: str
    app_id: str
    module_code: str
    module_name: str
    version: str
    status: str
    status_display: str
    parent_module_id: Optional[str]
    related_plan_id: Optional[str]
    launch_time: Optional[str]
    description: Optional[str]
    child_count: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class FunctionModuleTreeSchema(BaseModel):
    """功能模块树形Schema"""
    id: str
    module_code: str
    module_name: str
    version: str
    status: str
    status_display: str
    children: List['FunctionModuleTreeSchema'] = []

    class Config:
        from_attributes = True


class FunctionModuleListResponseSchema(BaseModel):
    """功能模块列表响应Schema"""
    items: List[FunctionModuleResponseSchema]
    total: int


class FunctionModuleVersionHistorySchema(BaseModel):
    """功能模块版本历史Schema"""
    versions: List[FunctionModuleResponseSchema]


class ModuleStatusTransitionSchema(BaseModel):
    """模块状态转换信息"""
    current_status: str
    allowed_transitions: List[Dict[str, str]]
