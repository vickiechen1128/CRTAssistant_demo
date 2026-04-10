"""
审核矩阵应用服务
"""
from datetime import datetime
from typing import List, Optional

from ..domain.entities.audit_matrix_config import AuditMatrixConfig
from ..domain.entities.audit_rule import AuditRule
from ..domain.value_objects.audit_level import AuditLevel
from ..domain.value_objects.audit_method import AuditMethod
from ..domain.repositories.audit_matrix_repository import AuditMatrixRepository
from .dtos.audit_matrix_dtos import (
    CreateAuditMatrixRequest,
    UpdateAuditMatrixRequest,
    AuditMatrixResponse,
    AuditMatrixListResponse,
    AuditMatrixFilterRequest,
    AuditRuleRequest,
    AuditRuleResponse,
)


class AuditMatrixService:
    """
    审核矩阵应用服务
    
    职责：
    1. 管理审核矩阵配置的CRUD
    2. 管理审核规则的CRUD
    3. 处理业务规则校验
    """
    
    def __init__(self, matrix_repository: AuditMatrixRepository):
        self._repository = matrix_repository
    
    def create_matrix(
        self,
        request: CreateAuditMatrixRequest,
        created_by: str
    ) -> AuditMatrixResponse:
        """创建审核矩阵配置"""
        # 生成配置ID（如果未提供）
        config_id = request.config_id or self._generate_config_id()
        
        # 检查是否已存在
        if self._repository.exists(config_id):
            raise ValueError(f"Config ID already exists: {config_id}")
        
        # 创建领域对象
        config = AuditMatrixConfig.create(
            config_id=config_id,
            name=request.name,
            created_by=created_by,
            description=request.description,
        )
        
        # 添加规则
        if request.rules:
            for rule_req in request.rules:
                rule = self._create_rule_from_request(rule_req, config.id)
                config.add_rule(rule)
        
        # 如果没有规则，添加默认规则
        if not config.rules:
            self._add_default_rules(config)
        
        # 持久化
        saved_config = self._repository.save(config)
        
        return self._to_response(saved_config)
    
    def _create_rule_from_request(
        self,
        request: AuditRuleRequest,
        config_id: str
    ) -> AuditRule:
        """从请求创建审核规则"""
        audit_level = AuditLevel(request.audit_level)
        primary_method = AuditMethod(request.primary_method)
        secondary_method = None
        if request.secondary_method:
            secondary_method = AuditMethod(request.secondary_method)
        
        return AuditRule.create(
            audit_level=audit_level,
            primary_method=primary_method,
            config_id=config_id,
            secondary_method=secondary_method,
            sampling_ratio=request.sampling_ratio,
            auto_pass_threshold=request.auto_pass_threshold,
            mandatory_reviewer_role=request.mandatory_reviewer_role,
            escalation_rule=request.escalation_rule,
        )
    
    def _add_default_rules(self, config: AuditMatrixConfig) -> None:
        """添加默认规则"""
        # 普通项规则
        normal_rule = AuditRule.create_normal_rule(
            primary_method=AuditMethod.self_review(),
            secondary_method=AuditMethod.script_auto(),
            config_id=config.id,
        )
        config.add_rule(normal_rule)
        
        # 关键项规则
        critical_rule = AuditRule.create_critical_rule(
            primary_method=AuditMethod.expert_manual(),
            secondary_method=AuditMethod.ai_assist(),
            mandatory_reviewer_role="ops_manager",
            config_id=config.id,
        )
        config.add_rule(critical_rule)
    
    def update_matrix(
        self,
        config_id: str,
        request: UpdateAuditMatrixRequest,
        updated_by: str
    ) -> AuditMatrixResponse:
        """更新审核矩阵配置"""
        config = self._repository.find_by_id(config_id)
        if not config:
            raise ValueError(f"Audit matrix not found: {config_id}")
        
        # 更新领域对象
        config.update(
            name=request.name,
            description=request.description,
        )
        
        # 持久化
        saved_config = self._repository.save(config)
        
        return self._to_response(saved_config)
    
    def get_matrix(self, config_id: str) -> AuditMatrixResponse:
        """获取审核矩阵详情"""
        config = self._repository.find_by_id(config_id)
        if not config:
            raise ValueError(f"Audit matrix not found: {config_id}")
        
        return self._to_response(config)
    
    def list_matrices(
        self,
        filter_request: AuditMatrixFilterRequest
    ) -> AuditMatrixListResponse:
        """查询审核矩阵列表"""
        # 查询
        skip = (filter_request.page - 1) * filter_request.page_size
        configs, total = self._repository.find_all(
            status=filter_request.status,
            keyword=filter_request.keyword,
            skip=skip,
            limit=filter_request.page_size
        )
        
        # 构建响应
        total_pages = (total + filter_request.page_size - 1) // filter_request.page_size
        
        return AuditMatrixListResponse(
            items=[self._to_response(c) for c in configs],
            total=total,
            page=filter_request.page,
            page_size=filter_request.page_size,
            total_pages=total_pages
        )
    
    def delete_matrix(self, config_id: str, deleted_by: str) -> bool:
        """删除审核矩阵配置"""
        config = self._repository.find_by_id(config_id)
        if not config:
            raise ValueError(f"Audit matrix not found: {config_id}")
        
        # 检查是否被模板引用
        if self._repository.is_referenced_by_template(config_id):
            raise ValueError("Cannot delete audit matrix that is referenced by templates")
        
        return self._repository.delete(config_id)
    
    def add_rule(
        self,
        config_id: str,
        request: AuditRuleRequest,
        added_by: str
    ) -> AuditMatrixResponse:
        """添加审核规则"""
        config = self._repository.find_by_id(config_id)
        if not config:
            raise ValueError(f"Audit matrix not found: {config_id}")
        
        # 检查是否已存在该等级的规则
        existing = config.get_rule_by_level(AuditLevel(request.audit_level))
        if existing:
            raise ValueError(f"Rule for audit level {request.audit_level} already exists")
        
        # 创建规则
        rule = self._create_rule_from_request(request, config.id)
        config.add_rule(rule)
        
        # 持久化
        saved_config = self._repository.save(config)
        
        return self._to_response(saved_config)
    
    def update_rule(
        self,
        config_id: str,
        rule_id: str,
        request: AuditRuleRequest,
        updated_by: str
    ) -> AuditMatrixResponse:
        """更新审核规则"""
        config = self._repository.find_by_id(config_id)
        if not config:
            raise ValueError(f"Audit matrix not found: {config_id}")
        
        # 查找规则
        rule = None
        for r in config.rules:
            if r.id == rule_id:
                rule = r
                break
        
        if not rule:
            raise ValueError(f"Rule not found: {rule_id}")
        
        # 更新规则
        secondary_method = None
        if request.secondary_method:
            secondary_method = AuditMethod(request.secondary_method)
        
        rule.update(
            primary_method=AuditMethod(request.primary_method),
            secondary_method=secondary_method,
            sampling_ratio=request.sampling_ratio,
            auto_pass_threshold=request.auto_pass_threshold,
            mandatory_reviewer_role=request.mandatory_reviewer_role,
            escalation_rule=request.escalation_rule,
        )
        
        # 持久化
        saved_config = self._repository.save(config)
        
        return self._to_response(saved_config)
    
    def delete_rule(
        self,
        config_id: str,
        rule_id: str,
        deleted_by: str
    ) -> AuditMatrixResponse:
        """删除审核规则"""
        config = self._repository.find_by_id(config_id)
        if not config:
            raise ValueError(f"Audit matrix not found: {config_id}")
        
        # 删除规则
        if not config.remove_rule(rule_id):
            raise ValueError(f"Rule not found: {rule_id}")
        
        # 持久化
        saved_config = self._repository.save(config)
        
        return self._to_response(saved_config)
    
    def activate_matrix(self, config_id: str, activated_by: str) -> AuditMatrixResponse:
        """激活审核矩阵"""
        config = self._repository.find_by_id(config_id)
        if not config:
            raise ValueError(f"Audit matrix not found: {config_id}")
        
        config.activate()
        
        # 持久化
        saved_config = self._repository.save(config)
        
        return self._to_response(saved_config)
    
    def deactivate_matrix(self, config_id: str, deactivated_by: str) -> AuditMatrixResponse:
        """停用审核矩阵"""
        config = self._repository.find_by_id(config_id)
        if not config:
            raise ValueError(f"Audit matrix not found: {config_id}")
        
        config.deactivate()
        
        # 持久化
        saved_config = self._repository.save(config)
        
        return self._to_response(saved_config)
    
    def _generate_config_id(self) -> str:
        """生成配置ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        return f"MATRIX-{timestamp}"
    
    def _to_response(self, config: AuditMatrixConfig) -> AuditMatrixResponse:
        """转换为响应DTO"""
        return AuditMatrixResponse(
            id=config.id,
            config_id=config.config_id,
            name=config.name,
            description=config.description,
            status=config.status,
            rules_count=len(config.rules),
            rules=[self._to_rule_response(r) for r in config.rules],
            created_by=config.created_by,
            created_at=config.created_at,
            updated_at=config.updated_at,
        )
    
    def _to_rule_response(self, rule: AuditRule) -> AuditRuleResponse:
        """转换为规则响应DTO"""
        return AuditRuleResponse(
            id=rule.id,
            audit_level=rule.audit_level.value,
            audit_level_display=rule.audit_level.display_name,
            primary_method=rule.primary_method.value,
            primary_method_display=rule.primary_method.display_name,
            secondary_method=rule.secondary_method.value if rule.secondary_method else None,
            secondary_method_display=rule.secondary_method.display_name if rule.secondary_method else None,
            sampling_ratio=rule.sampling_ratio,
            auto_pass_threshold=rule.auto_pass_threshold,
            mandatory_reviewer_role=rule.mandatory_reviewer_role,
            escalation_rule=rule.escalation_rule,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
        )
