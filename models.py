from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SeverityLevel(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class IncidentStatus(str, Enum):
    ACTIVE = "active"
    ANALYZING = "analyzing"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class LogEntry(BaseModel):
    timestamp: datetime
    level: str
    message: str
    service: str
    metadata: Optional[Dict[str, Any]] = None


class Incident(BaseModel):
    id: str
    service: str
    severity: SeverityLevel
    status: IncidentStatus
    timestamp: datetime
    description: str
    log_entries: List[LogEntry]
    tags: Optional[List[str]] = []
    assigned_to: Optional[str] = None


class SimilarIncident(BaseModel):
    id: str
    similarity_score: float
    resolution: str
    mttr: str
    resolution_date: datetime


class AIAnalysis(BaseModel):
    incident_id: str
    confidence: float = Field(ge=0, le=100)
    severity_assessment: str
    root_cause: str
    recommendations: List[str]
    business_impact: str
    escalation_path: str
    similar_incidents: List[SimilarIncident]
    reasoning_chain: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FeedbackRequest(BaseModel):
    incident_id: str
    analysis_id: str
    is_correct: bool
    user_id: str
    comments: Optional[str] = None


class AnalysisRequest(BaseModel):
    app_id: Optional[str] = None
    log_data: List[Dict[str, Any]]
    service_name: str
    severity_hint: Optional[SeverityLevel] = None
    documentation: Optional[str] = None