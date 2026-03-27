"""
SOP 模板引擎 - 领域事件
"""
from .sop_template_events import (
    SOPTemplateCreatedEvent,
    SOPTemplatePublishedEvent,
    SOPTemplateDeprecatedEvent,
    SOPTemplateClonedEvent,
)

__all__ = [
    'SOPTemplateCreatedEvent',
    'SOPTemplatePublishedEvent',
    'SOPTemplateDeprecatedEvent',
    'SOPTemplateClonedEvent',
]
