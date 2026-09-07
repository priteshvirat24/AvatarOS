from typing import List, Literal
from pydantic import BaseModel, Field

class RightsRecord(BaseModel):
    rights_id: str
    character_id: str
    likeness_holder: str
    consent_scope: List[str] = Field(default_factory=lambda: ["marketing", "product_education"])
    consent_excludes: List[str] = Field(default_factory=lambda: ["political", "financial_endorsement"])
    territories: List[str] = Field(default_factory=lambda: ["IN", "US", "global_digital"])
    expiration: str = "2027-04-01"
    revocable: bool = True
    signature: str
    renewal_status: Literal["active", "pending_renewal", "expired", "revoked"] = "active"

    def is_valid_for_context(self, context: str, territory: str = "global_digital") -> bool:
        if self.renewal_status != "active":
            return False
        if any(excluded in context.lower() for excluded in self.consent_excludes):
            return False
        if not any(scope in context.lower() for scope in self.consent_scope):
            return False
        if territory not in self.territories and "global_digital" not in self.territories:
            return False
        return True
