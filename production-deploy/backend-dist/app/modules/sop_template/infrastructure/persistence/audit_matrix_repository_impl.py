"""
审核矩阵仓储实现
使用 SQLAlchemy 实现领域仓储接口
"""
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func

from ...domain.entities.audit_matrix_config import AuditMatrixConfig
from ...domain.entities.audit_rule import AuditRule
from ...domain.value_objects.audit_level import AuditLevel
from ...domain.value_objects.audit_method import AuditMethod
from ...domain.repositories.audit_matrix_repository import AuditMatrixRepository
from .models.audit_matrix_model import AuditMatrixConfigModel, AuditRuleModel
from .models.sop_template_model import SOPTemplateModel


class AuditMatrixRepositoryImpl(AuditMatrixRepository):
    """
    审核矩阵仓储 SQLAlchemy 实现
    """
    
    def __init__(self, db_session: Session):
        self._session = db_session
    
    def save(self, config: AuditMatrixConfig) -> AuditMatrixConfig:
        """保存审核矩阵配置"""
        # 查找现有记录
        db_config = self._session.query(AuditMatrixConfigModel).filter_by(id=config.id).first()
        
        if db_config:
            # 更新
            self._update_model(db_config, config)
        else:
            # 创建
            db_config = self._to_model(config)
            self._session.add(db_config)
        
        self._session.commit()
        self._session.refresh(db_config)
        
        return self._to_entity(db_config)
    
    def find_by_id(self, config_id: str) -> Optional[AuditMatrixConfig]:
        """根据ID查找配置"""
        db_config = self._session.query(AuditMatrixConfigModel).filter_by(id=config_id).first()
        return self._to_entity(db_config) if db_config else None
    
    def find_by_config_id(self, config_id: str) -> Optional[AuditMatrixConfig]:
        """根据业务ID查找配置"""
        db_config = self._session.query(AuditMatrixConfigModel).filter_by(config_id=config_id).first()
        return self._to_entity(db_config) if db_config else None
    
    def find_all(
        self,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[AuditMatrixConfig], int]:
        """查询配置列表"""
        query = self._session.query(AuditMatrixConfigModel)
        
        # 应用筛选条件
        if status:
            query = query.filter(AuditMatrixConfigModel.status == status)
        
        if keyword:
            query = query.filter(
                func.lower(AuditMatrixConfigModel.name).contains(keyword.lower()) |
                func.lower(AuditMatrixConfigModel.config_id).contains(keyword.lower())
            )
        
        # 获取总数
        total = query.count()
        
        # 分页
        db_configs = query.order_by(AuditMatrixConfigModel.created_at.desc()).offset(skip).limit(limit).all()
        
        configs = [self._to_entity(c) for c in db_configs]
        return configs, total
    
    def delete(self, config_id: str) -> bool:
        """删除配置"""
        db_config = self._session.query(AuditMatrixConfigModel).filter_by(id=config_id).first()
        if not db_config:
            return False
        
        self._session.delete(db_config)
        self._session.commit()
        return True
    
    def exists(self, config_id: str) -> bool:
        """检查配置是否存在"""
        return self._session.query(AuditMatrixConfigModel).filter_by(config_id=config_id).first() is not None
    
    def is_referenced_by_template(self, config_id: str) -> bool:
        """检查是否被模板引用"""
        return self._session.query(SOPTemplateModel).filter_by(
            audit_matrix_config_id=config_id
        ).first() is not None
    
    def _to_model(self, config: AuditMatrixConfig) -> AuditMatrixConfigModel:
        """领域对象转数据库模型"""
        db_config = AuditMatrixConfigModel(
            id=config.id,
            config_id=config.config_id,
            name=config.name,
            description=config.description,
            status=config.status,
            created_by=config.created_by,
            created_at=config.created_at,
            updated_at=config.updated_at,
        )
        
        # 级联创建规则
        for rule in config.rules:
            db_rule = self._rule_to_model(rule, config.id)
            db_config.rules.append(db_rule)
        
        return db_config
    
    def _update_model(self, db_config: AuditMatrixConfigModel, config: AuditMatrixConfig) -> None:
        """更新数据库模型"""
        db_config.name = config.name
        db_config.description = config.description
        db_config.status = config.status
        db_config.updated_at = config.updated_at
        
        # 更新规则（简化处理：删除后重建）
        if config.rules:
            # 删除现有规则
            for db_rule in list(db_config.rules):
                self._session.delete(db_rule)
            db_config.rules.clear()
            
            # 重新创建
            for rule in config.rules:
                db_rule = self._rule_to_model(rule, config.id)
                db_config.rules.append(db_rule)
    
    def _rule_to_model(self, rule: AuditRule, config_id: str) -> AuditRuleModel:
        """审核规则转数据库模型"""
        return AuditRuleModel(
            id=rule.id,
            audit_level=rule.audit_level.value,
            primary_method=rule.primary_method.value,
            secondary_method=rule.secondary_method.value if rule.secondary_method else None,
            sampling_ratio=rule.sampling_ratio,
            auto_pass_threshold=rule.auto_pass_threshold,
            mandatory_reviewer_role=rule.mandatory_reviewer_role,
            escalation_rule=rule.escalation_rule,
            config_id=config_id,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
        )
    
    def _to_entity(self, db_config: AuditMatrixConfigModel) -> AuditMatrixConfig:
        """数据库模型转领域对象"""
        config = AuditMatrixConfig(
            id=db_config.id,
            config_id=db_config.config_id,
            name=db_config.name,
            description=db_config.description,
            status=db_config.status,
            created_by=db_config.created_by,
            created_at=db_config.created_at,
            updated_at=db_config.updated_at,
        )
        
        # 转换规则
        for db_rule in db_config.rules:
            rule = self._rule_to_entity(db_rule)
            config.rules.append(rule)
        
        return config
    
    def _rule_to_entity(self, db_rule: AuditRuleModel) -> AuditRule:
        """数据库模型转审核规则实体"""
        return AuditRule(
            id=db_rule.id,
            audit_level=AuditLevel(db_rule.audit_level),
            primary_method=AuditMethod(db_rule.primary_method),
            secondary_method=AuditMethod(db_rule.secondary_method) if db_rule.secondary_method else None,
            sampling_ratio=float(db_rule.sampling_ratio) if db_rule.sampling_ratio else 0.3,
            auto_pass_threshold=float(db_rule.auto_pass_threshold) if db_rule.auto_pass_threshold else None,
            mandatory_reviewer_role=db_rule.mandatory_reviewer_role,
            escalation_rule=db_rule.escalation_rule,
            config_id=db_rule.config_id,
            created_at=db_rule.created_at,
            updated_at=db_rule.updated_at,
        )
