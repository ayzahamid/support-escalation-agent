from pydantic import BaseModel
from typing import Optional
from enum import Enum


class QueryCategory(str, Enum):
    technical = "technical"
    billing = "billing"
    general = "general"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class RelevanceResult(BaseModel):
    relevant: bool
    reason: str


class ClassificationResult(BaseModel):
    category: QueryCategory
    priority: Priority
    summary: str


class SupportResult(BaseModel):
    response: str
    resolved: bool
    resolution_note: str
    tools_used: bool = False


class _EscalationLLMOutput(BaseModel):
    escalation_message: str
    recommended_action: str
    urgency: str


class EscalationResult(BaseModel):
    ticket_id: str
    escalation_message: str
    recommended_action: str
    urgency: str


class SupportRequest(BaseModel):
    query: str


class PipelineResponse(BaseModel):
    status: str
    category: Optional[str] = None
    priority: Optional[str] = None
    response: Optional[str] = None
    tools_used: Optional[bool] = None
    ticket_id: Optional[str] = None
    escalation_message: Optional[str] = None
    recommended_action: Optional[str] = None
    urgency: Optional[str] = None
    reason: Optional[str] = None
