"""
SOP 模板仓储实现
使用 SQLAlchemy 实现领域仓储接口
"""
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from ...domain.entities.sop_template import SOPTemplate
from ...domain.entities.workflow_node import WorkflowNode
from ...domain.entities.work_item_template import WorkItemTemplate
from ...domain.value_objects.template_type import TemplateType
from ...domain.value_objects.template_status import TemplateStatus
from ...domain.value_objects.audit_level import AuditLevel
from ...domain.value_objects.work_item_category import WorkItemCategory
from ...domain.repositories.sop_template_repository import SOPTemplateRepository
from .models.sop_template_model import (
    SOPTemplateModel,
    WorkflowNodeModel,
    WorkItemTemplateModel,
)


class SOPTemplateRepositoryImpl(SOPTemplateRepository):
    """
    SOP 模板仓储 SQLAlchemy 实现
    
    职责：
    1. 领域对象与数据库模型的转换
    2. 数据库操作的具体实现
    """
    
    def __init__(self, db_session: Session):
        self._session = db_session
    
    def save(self, template: SOPTemplate) -> SOPTemplate:
        """保存模板（包含级联保存）"""
        # 查找现有记录
        db_template = self._session.query(SOPTemplateModel).filter_by(id=template.id).first()
        
        if db_template:
            # 更新
            self._update_model(db_template, template)
        else:
            # 创建
            db_template = self._to_model(template)
            self._session.add(db_template)
        
        self._session.commit()
        self._session.refresh(db_template)
        
        return self._to_entity(db_template)
    
    def find_by_id(self, template_id: str) -> Optional[SOPTemplate]:
        """根据ID查找模板（含完整结构）"""
        db_template = self._session.query(SOPTemplateModel).filter_by(id=template_id).first()
        return self._to_entity(db_template) if db_template else None
    
    def find_by_template_id(self, template_id: str) -> Optional[SOPTemplate]:
        """根据业务ID查找模板"""
        db_template = self._session.query(SOPTemplateModel).filter_by(template_id=template_id).first()
        return self._to_entity(db_template) if db_template else None
    
    def find_active_by_type(self, template_type: TemplateType) -> Optional[SOPTemplate]:
        """查找指定类型的活跃模板"""
        db_template = self._session.query(SOPTemplateModel).filter_by(
            template_type=template_type.value,
            status='active'
        ).first()
        return self._to_entity(db_template) if db_template else None
    
    def find_all(
        self,
        template_type: Optional[TemplateType] = None,
        status: Optional[TemplateStatus] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[SOPTemplate], int]:
        """查询模板列表"""
        query = self._session.query(SOPTemplateModel)
        
        # 应用筛选条件
        if template_type:
            query = query.filter(SOPTemplateModel.template_type == template_type.value)
        
        if status:
            query = query.filter(SOPTemplateModel.status == status.value)
        
        if keyword:
            query = query.filter(
                func.lower(SOPTemplateModel.name).contains(keyword.lower()) |
                func.lower(SOPTemplateModel.template_id).contains(keyword.lower())
            )
        
        # 获取总数
        total = query.count()
        
        # 分页
        db_templates = query.order_by(SOPTemplateModel.created_at.desc()).offset(skip).limit(limit).all()
        
        templates = [self._to_entity(t, include_nodes=False) for t in db_templates]
        return templates, total
    
    def delete(self, template_id: str) -> bool:
        """删除模板"""
        db_template = self._session.query(SOPTemplateModel).filter_by(id=template_id).first()
        if not db_template:
            return False
        
        self._session.delete(db_template)
        self._session.commit()
        return True
    
    def exists(self, template_id: str) -> bool:
        """检查模板是否存在"""
        return self._session.query(SOPTemplateModel).filter_by(template_id=template_id).first() is not None
    
    def exists_active_version(self, template_id: str, exclude_id: Optional[str] = None) -> bool:
        """检查是否存在活跃版本"""
        query = self._session.query(SOPTemplateModel).filter_by(
            template_id=template_id,
            status='active'
        )
        if exclude_id:
            query = query.filter(SOPTemplateModel.id != exclude_id)
        return query.first() is not None
    
    def find_by_template_id_and_version(self, template_id: str, version: str) -> Optional[SOPTemplate]:
        """根据模板ID和版本号查找"""
        db_template = self._session.query(SOPTemplateModel).filter_by(
            template_id=template_id,
            version=version
        ).first()
        return self._to_entity(db_template) if db_template else None
    
    def _to_model(self, template: SOPTemplate) -> SOPTemplateModel:
        """领域对象转数据库模型"""
        db_template = SOPTemplateModel(
            id=template.id,
            template_id=template.template_id,
            name=template.name,
            template_type=template.template_type.value,
            description=template.description,
            version=template.version,
            status=template.status.value,
            audit_matrix_config_id=template.audit_matrix_config_id,
            parent_work_items_config=template.parent_work_items_config,
            created_by=template.created_by,
            created_at=template.created_at,
            updated_at=template.updated_at,
            published_at=template.published_at,
            deprecated_at=template.deprecated_at,
        )
        
        # 级联创建流程节点
        for node in template.workflow_nodes:
            db_node = self._node_to_model(node, template.id)
            db_template.workflow_nodes.append(db_node)
        
        return db_template
    
    def _update_model(self, db_template: SOPTemplateModel, template: SOPTemplate) -> None:
        """更新数据库模型"""
        db_template.name = template.name
        db_template.description = template.description
        db_template.status = template.status.value
        db_template.audit_matrix_config_id = template.audit_matrix_config_id
        db_template.parent_work_items_config = template.parent_work_items_config
        db_template.updated_at = template.updated_at
        db_template.published_at = template.published_at
        db_template.deprecated_at = template.deprecated_at
        
        # 更新流程节点（简化处理：删除后重建）
        if template.workflow_nodes:
            # 删除现有节点
            for db_node in list(db_template.workflow_nodes):
                self._session.delete(db_node)
            db_template.workflow_nodes.clear()
            
            # 重新创建
            for node in template.workflow_nodes:
                db_node = self._node_to_model(node, template.id)
                db_template.workflow_nodes.append(db_node)
    
    def _node_to_model(self, node: WorkflowNode, template_id: str) -> WorkflowNodeModel:
        """流程节点转数据库模型"""
        db_node = WorkflowNodeModel(
            id=node.id,
            node_id=node.node_id,
            name=node.name,
            sequence=node.sequence,
            entry_conditions=node.entry_conditions,
            exit_conditions=node.exit_conditions,
            mandatory_rules=node.mandatory_rules,
            sop_template_id=template_id,
            created_at=node.created_at,
            updated_at=node.updated_at,
        )
        
        # 创建工作项映射（用于处理父子关系）
        work_item_map = {}
        
        # 先创建所有工作项（不含父级关联）
        for work_item in node.work_items:
            db_work_item = WorkItemTemplateModel(
                id=work_item.id,
                template_id=work_item.template_id,
                name=work_item.name,
                category=work_item.category.value,
                sequence=work_item.sequence,
                description=work_item.description,
                audit_level=work_item.audit_level.value,
                deliverables_config=work_item.deliverables_config,
                acceptance_criteria_config=work_item.acceptance_criteria_config,
                execution_steps_config=work_item.execution_steps_config,
                sop_template_id=template_id,
                workflow_node_id=node.id,
                parent_template_id=None,  # 先设为 None
                status=work_item.status,
                created_at=work_item.created_at,
                updated_at=work_item.updated_at,
            )
            work_item_map[work_item.id] = (db_work_item, work_item)
        
        # 再设置父级关联
        for db_work_item, work_item in work_item_map.values():
            if work_item.parent_template_id:
                db_work_item.parent_template_id = work_item.parent_template_id
            db_node.work_items.append(db_work_item)
        
        return db_node
    
    def _to_entity(
        self,
        db_template: SOPTemplateModel,
        include_nodes: bool = True
    ) -> SOPTemplate:
        """数据库模型转领域对象"""
        template = SOPTemplate(
            id=db_template.id,
            template_id=db_template.template_id,
            name=db_template.name,
            template_type=TemplateType(db_template.template_type),
            description=db_template.description,
            version=db_template.version,
            status=TemplateStatus(db_template.status),
            audit_matrix_config_id=db_template.audit_matrix_config_id,
            parent_work_items_config=db_template.parent_work_items_config or [],
            created_by=db_template.created_by,
            created_at=db_template.created_at,
            updated_at=db_template.updated_at,
            published_at=db_template.published_at,
            deprecated_at=db_template.deprecated_at,
        )
        
        # 转换流程节点
        if include_nodes and db_template.workflow_nodes:
            for db_node in db_template.workflow_nodes:
                node = self._node_to_entity(db_node)
                template.workflow_nodes.append(node)
        
        return template
    
    def _node_to_entity(self, db_node: WorkflowNodeModel) -> WorkflowNode:
        """数据库模型转流程节点实体"""
        node = WorkflowNode(
            id=db_node.id,
            node_id=db_node.node_id,
            name=db_node.name,
            sequence=db_node.sequence,
            entry_conditions=db_node.entry_conditions or [],
            exit_conditions=db_node.exit_conditions or [],
            mandatory_rules=db_node.mandatory_rules or {},
            sop_template_id=db_node.sop_template_id,
            created_at=db_node.created_at,
            updated_at=db_node.updated_at,
        )
        
        # 构建工作项映射（用于处理父子关系）
        work_item_map = {}
        
        # 先创建所有工作项
        for db_work_item in db_node.work_items:
            work_item = self._work_item_to_entity(db_work_item)
            work_item_map[db_work_item.id] = work_item
        
        # 再建立父子关系
        for db_work_item in db_node.work_items:
            work_item = work_item_map[db_work_item.id]
            if db_work_item.parent_template_id:
                # 这是子工作项，需要设置 parent
                work_item.parent_template_id = db_work_item.parent_template_id
                # 找到父级并添加到 children
                parent = work_item_map.get(db_work_item.parent_template_id)
                if parent:
                    parent.children.append(work_item)
            else:
                # 这是父工作项，直接添加到节点
                node.work_items.append(work_item)
        
        return node
    
    def _work_item_to_entity(self, db_work_item: WorkItemTemplateModel) -> WorkItemTemplate:
        """数据库模型转工作项实体"""
        return WorkItemTemplate(
            id=db_work_item.id,
            template_id=db_work_item.template_id,
            name=db_work_item.name,
            category=WorkItemCategory(db_work_item.category),
            sequence=db_work_item.sequence,
            description=db_work_item.description,
            audit_level=AuditLevel(db_work_item.audit_level),
            deliverables_config=db_work_item.deliverables_config or [],
            acceptance_criteria_config=db_work_item.acceptance_criteria_config or [],
            execution_steps_config=db_work_item.execution_steps_config or [],
            sop_template_id=db_work_item.sop_template_id,
            workflow_node_id=db_work_item.workflow_node_id,
            parent_template_id=db_work_item.parent_template_id,
            status=db_work_item.status,
            created_at=db_work_item.created_at,
            updated_at=db_work_item.updated_at,
            children=[],  # 由调用方填充
        )
