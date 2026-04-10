"""
SOP 模板领域事件
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SOPTemplateCreatedEvent:
    """SOP 模板创建事件"""
    template_id: str
    name: str
    template_type: str
    version: str
    created_by: str
    occurred_at: datetime = datetime.utcnow()


@dataclass
class SOPTemplatePublishedEvent:
    """SOP 模板发布事件"""
    template_id: str
    version: str
    published_by: str
    occurred_at: datetime = datetime.utcnow()


@dataclass
class SOPTemplateDeprecatedEvent:
    """SOP 模板弃用事件"""
    template_id: str
    version: str
    deprecated_by: str
    reason: Optional[str] = None
    occurred_at: datetime = datetime.utcnow()


@dataclass
class SOPTemplateClonedEvent:
    """SOP 模板克隆事件"""
    source_template_id: str
    source_version: str
    new_version: str
    cloned_by: str
    occurred_at: datetime = datetime.utcnow()
