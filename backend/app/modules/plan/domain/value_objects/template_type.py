"""
工作流模板类型值对象
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateType:
    """工作流模板类型值对象"""
    value: str
    
    VALID_TEMPLATES = {
        "new_system_onboarding",
        "feature_release",
        "feature_modification",
        "architecture_change",
        "security_audit"
    }
    
    CATEGORY_MAPPING = {
        "new_system": "new_system_onboarding",
        "new_feature": "feature_release",
        "func_change": "feature_modification",
        "arch_change": "architecture_change",
        "security_check": "security_audit"
    }
    
    def __post_init__(self):
        if self.value not in self.VALID_TEMPLATES:
            raise ValueError(f"Invalid template type: {self.value}")
    
    @classmethod
    def from_category(cls, category: str) -> "TemplateType":
        template = cls.CATEGORY_MAPPING.get(category)
        if not template:
            raise ValueError(f"No template mapping for category: {category}")
        return cls(template)
    
    def __str__(self) -> str:
        return self.value
