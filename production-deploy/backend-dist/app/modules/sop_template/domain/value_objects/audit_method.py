"""
审核方式值对象
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class AuditMethod:
    """
    审核方式值对象
    
    - self_review: 自查
    - script_auto: 脚本自动核验
    - expert_manual: 专家人工审核
    - ai_assist: AI辅助核验
    """
    value: str
    
    VALID_METHODS = {
        "self_review",
        "script_auto",
        "expert_manual",
        "ai_assist"
    }
    
    def __post_init__(self):
        if self.value not in self.VALID_METHODS:
            raise ValueError(f"Invalid audit method: {self.value}")
    
    @classmethod
    def self_review(cls) -> "AuditMethod":
        return cls("self_review")
    
    @classmethod
    def script_auto(cls) -> "AuditMethod":
        return cls("script_auto")
    
    @classmethod
    def expert_manual(cls) -> "AuditMethod":
        return cls("expert_manual")
    
    @classmethod
    def ai_assist(cls) -> "AuditMethod":
        return cls("ai_assist")
    
    @property
    def display_name(self) -> str:
        """获取显示名称"""
        mapping = {
            "self_review": "自查",
            "script_auto": "脚本自动核验",
            "expert_manual": "专家人工审核",
            "ai_assist": "AI辅助核验",
        }
        return mapping.get(self.value, self.value)
    
    @property
    def is_automated(self) -> bool:
        """是否为自动化审核"""
        return self.value in {"script_auto", "ai_assist"}
    
    @property
    def requires_human(self) -> bool:
        """是否需要人工参与"""
        return self.value in {"self_review", "expert_manual"}
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AuditMethod):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
