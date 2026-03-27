"""
台账管理模块DTOs
数据传输对象，用于应用层与接口层之间的数据传递
"""
from .inventory_dtos import (
    # 应用系统DTOs
    CreateApplicationDTO,
    UpdateApplicationDTO,
    ApplicationResponseDTO,
    FunctionModuleDTO,
    # 云资源DTOs
    CreateCloudResourceDTO,
    UpdateCloudResourceDTO,
    CloudResourceResponseDTO,
    # 账号DTOs
    CreateAccountDTO,
    UpdateAccountDTO,
    AccountResponseDTO,
    ExtendValidityDTO,
    # 通用DTOs
    InventorySummaryDTO,
    PlanLinkDTO,
    PaginationDTO,
)

__all__ = [
    'CreateApplicationDTO',
    'UpdateApplicationDTO',
    'ApplicationResponseDTO',
    'FunctionModuleDTO',
    'CreateCloudResourceDTO',
    'UpdateCloudResourceDTO',
    'CloudResourceResponseDTO',
    'CreateAccountDTO',
    'UpdateAccountDTO',
    'AccountResponseDTO',
    'ExtendValidityDTO',
    'InventorySummaryDTO',
    'PlanLinkDTO',
    'PaginationDTO',
]
