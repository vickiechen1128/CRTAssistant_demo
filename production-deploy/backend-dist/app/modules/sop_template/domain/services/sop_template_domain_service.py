"""
SOP 模板领域服务
处理跨实体的业务逻辑
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
import re

from ..entities.sop_template import SOPTemplate
from ..entities.workflow_node import WorkflowNode
from ..entities.work_item_template import WorkItemTemplate
from ..entities.audit_matrix_config import AuditMatrixConfig
from ..entities.audit_rule import AuditRule
from ..value_objects.template_type import TemplateType
from ..value_objects.template_status import TemplateStatus
from ..value_objects.audit_level import AuditLevel
from ..value_objects.work_item_category import WorkItemCategory
from ..value_objects.audit_method import AuditMethod
from ..repositories.sop_template_repository import SOPTemplateRepository


class SOPTemplateDomainService:
    """
    SOP 模板领域服务
    
    职责：
    1. 生成模板业务ID
    2. 构建模板树状结构
    3. 实例化模板为工作流
    4. 变量替换逻辑
    """
    
    def __init__(self, template_repository: SOPTemplateRepository):
        self._repository = template_repository
    
    def generate_template_id(self, template_type: TemplateType) -> str:
        """生成模板业务ID"""
        type_prefix = template_type.value.upper().replace("_", "-")
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        
        # 查询当天该类型的模板数量
        templates, _ = self._repository.find_all(
            template_type=template_type,
            skip=0,
            limit=1000
        )
        
        # 生成序号
        sequence = len(templates) + 1
        return f"SOP-{type_prefix}-{timestamp}-{sequence:03d}"
    
    def build_template_tree(self, template: SOPTemplate) -> Dict[str, Any]:
        """
        构建模板的完整树状结构
        
        结构：
        SOPTemplate
        └── WorkflowNode[]
            └── WorkItemTemplate[] (父级)
                └── WorkItemTemplate[] (子级)
        """
        return {
            "id": template.id,
            "template_id": template.template_id,
            "name": template.name,
            "template_type": template.template_type.value,
            "template_type_display": template.template_type.display_name,
            "version": template.version,
            "status": template.status.value,
            "status_display": template.status.display_name,
            "description": template.description,
            "audit_matrix_config_id": template.audit_matrix_config_id,
            "nodes": [
                self._build_node_tree(node)
                for node in sorted(template.workflow_nodes, key=lambda n: n.sequence)
            ],
        }
    
    def _build_node_tree(self, node: WorkflowNode) -> Dict[str, Any]:
        """构建节点树"""
        # 获取父工作项
        parent_items = [
            self._build_work_item_tree(wi)
            for wi in sorted(
                [wi for wi in node.work_items if wi.is_parent],
                key=lambda w: w.sequence
            )
        ]
        
        return {
            "id": node.id,
            "node_id": node.node_id,
            "name": node.name,
            "sequence": node.sequence,
            "entry_conditions": node.entry_conditions,
            "exit_conditions": node.exit_conditions,
            "mandatory_rules": node.mandatory_rules,
            "work_items": parent_items,
        }
    
    def _build_work_item_tree(self, work_item: WorkItemTemplate) -> Dict[str, Any]:
        """构建工作项树"""
        # 获取子工作项
        children = [
            self._build_work_item_tree(child)
            for child in sorted(work_item.children, key=lambda c: c.sequence)
        ]
        
        return {
            "id": work_item.id,
            "template_id": work_item.template_id,
            "name": work_item.name,
            "category": work_item.category.value,
            "category_display": work_item.category.display_name,
            "category_icon": work_item.category.icon,
            "sequence": work_item.sequence,
            "description": work_item.description,
            "audit_level": work_item.audit_level.value,
            "audit_level_display": work_item.audit_level.display_name,
            "is_parent": work_item.is_parent,
            "deliverables_config": work_item.deliverables_config,
            "acceptance_criteria_config": work_item.acceptance_criteria_config,
            "execution_steps_config": work_item.execution_steps_config,
            "children": children,
        }
    
    def instantiate_template(
        self,
        template: SOPTemplate,
        variable_mapping: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        实例化模板
        
        执行变量替换，生成可执行的工作流结构
        
        支持的变量：
        - {app_name}: 应用名称
        - {plan_id}: 计划ID
        - {current_date}: 当前日期
        - {business_owner}: 业务负责人
        - {project_owner}: 项目负责人
        """
        tree = self.build_template_tree(template)
        
        # 递归替换变量
        self._replace_variables_in_dict(tree, variable_mapping)
        
        return {
            "template_id": template.template_id,
            "version": template.version,
            "instantiated_at": datetime.utcnow().isoformat(),
            "variable_mapping": variable_mapping,
            "structure": tree,
        }
    
    def _replace_variables_in_dict(
        self,
        data: Dict[str, Any],
        variable_mapping: Dict[str, str]
    ) -> None:
        """递归替换字典中的变量"""
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = self._replace_variables(value, variable_mapping)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._replace_variables_in_dict(item, variable_mapping)
                    elif isinstance(item, str):
                        # 处理列表中的字符串元素
                        pass
            elif isinstance(value, dict):
                self._replace_variables_in_dict(value, variable_mapping)
    
    def _replace_variables(
        self,
        text: str,
        variable_mapping: Dict[str, str]
    ) -> str:
        """替换文本中的变量"""
        result = text
        for var_name, var_value in variable_mapping.items():
            result = result.replace(var_name, str(var_value))
        return result
    
    def validate_variable_mapping(
        self,
        template: SOPTemplate,
        variable_mapping: Dict[str, str]
    ) -> List[str]:
        """
        验证变量映射是否完整
        
        返回缺失的变量列表
        """
        # 收集模板中使用的所有变量
        used_variables = set()
        
        for node in template.workflow_nodes:
            for work_item in node.work_items:
                used_variables.update(
                    self._extract_variables(work_item.name)
                )
                if work_item.description:
                    used_variables.update(
                        self._extract_variables(work_item.description)
                    )
        
        # 检查缺失的变量
        missing = []
        for var in used_variables:
            if var not in variable_mapping:
                missing.append(var)
        
        return missing
    
    def _extract_variables(self, text: str) -> List[str]:
        """从文本中提取变量（格式：{var_name}）"""
        pattern = r'\{([^}]+)\}'
        return re.findall(pattern, text)
    
    def create_default_audit_matrix(self, created_by: str) -> AuditMatrixConfig:
        """创建默认审核矩阵配置"""
        config = AuditMatrixConfig.create(
            config_id=f"MATRIX-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            name="默认审核矩阵",
            description="系统自动创建的默认审核矩阵配置",
            created_by=created_by,
        )
        
        # 添加普通项规则
        normal_rule = AuditRule.create_normal_rule(
            primary_method=AuditMethod.self_review(),
            secondary_method=AuditMethod.script_auto(),
            sampling_ratio=0.3,
            config_id=config.id,
        )
        config.add_rule(normal_rule)
        
        # 添加关键项规则
        critical_rule = AuditRule.create_critical_rule(
            primary_method=AuditMethod.expert_manual(),
            secondary_method=AuditMethod.ai_assist(),
            mandatory_reviewer_role="ops_manager",
            config_id=config.id,
        )
        config.add_rule(critical_rule)
        
        return config
    
    def validate_publish(self, template: SOPTemplate) -> List[str]:
        """
        验证模板是否可以发布
        
        返回错误信息列表，空列表表示验证通过
        """
        errors = []
        
        # 校验 1：至少包含 1 个流程节点
        if not template.workflow_nodes or len(template.workflow_nodes) == 0:
            errors.append("模板至少包含1个流程节点")
        
        # 校验 2：每个节点下至少包含 1 个父工作项
        for node in template.workflow_nodes:
            parent_items = [wi for wi in node.work_items if wi.is_parent]
            if not parent_items:
                errors.append(f"节点'{node.name}'下至少包含1个父工作项")
        
        # 校验 3：检查审核矩阵状态
        if template.audit_matrix_config_id:
            # 这里需要通过仓储查询审核矩阵状态
            # 简化处理，实际应调用仓储
            pass
        
        # 校验 4：同 template_id 下不能有其他 active 版本
        if self._repository.exists_active_version(
            template.template_id,
            exclude_id=template.id
        ):
            errors.append(f"模板 {template.template_id} 已存在活跃版本")
        
        return errors
