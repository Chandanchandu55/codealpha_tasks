from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    is_admin: bool = False

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    api_key: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class CapabilityCodeCreate(BaseModel):
    permissions: List[str] = Field(..., min_items=1)
    expires_in_minutes: Optional[int] = Field(60, ge=1, le=1440)  # Max 24 hours
    max_uses: Optional[int] = Field(1, ge=1, le=100)

class CapabilityCodeResponse(BaseModel):
    code: str
    code_hash: str
    permissions: List[str]
    expires_at: datetime
    max_uses: int
    use_count: int
    is_active: bool
    
    class Config:
        from_attributes = True

class SQLQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000)
    capability_code: Optional[str] = None
    
class SQLQueryResponse(BaseModel):
    is_safe: bool
    risk_score: int
    severity: str
    detected_patterns: List[str]
    sanitized_query: Optional[str] = None
    blocked_reason: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None
    
class SQLInjectionAttemptResponse(BaseModel):
    id: int
    ip_address: str
    query_attempt: str
    detected_patterns: List[str]
    risk_score: int
    is_blocked: bool
    blocked_reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class SecurityEventCreate(BaseModel):
    event_type: str
    severity: str
    description: str
    ip_address: str
    details: Optional[Dict[str, Any]] = None

class SecurityEventResponse(BaseModel):
    id: int
    event_type: str
    severity: str
    description: str
    ip_address: str
    details: Optional[Dict[str, Any]]
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class AccessLogResponse(BaseModel):
    id: int
    ip_address: str
    endpoint: str
    method: str
    status_code: int
    response_time_ms: Optional[int]
    user_agent: Optional[str]
    capability_code_used: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class SystemStats(BaseModel):
    total_users: int
    active_users: int
    total_capability_codes: int
    active_capability_codes: int
    total_injection_attempts: int
    blocked_attempts: int
    recent_events: List[SecurityEventResponse]
    
class SecurityDashboard(BaseModel):
    stats: SystemStats
    recent_attempts: List[SQLInjectionAttemptResponse]
    recent_logs: List[AccessLogResponse]
    high_risk_events: List[SecurityEventResponse]
