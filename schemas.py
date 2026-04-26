from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DataEntryBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    data_type: str = Field(..., min_length=1, max_length=50)
    source: Optional[str] = Field(None, max_length=100)

class DataEntryCreate(DataEntryBase):
    pass

class DataEntryResponse(DataEntryBase):
    id: int
    content_hash: str
    similarity_score: Optional[float] = None
    is_duplicate: bool
    is_false_positive: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RedundancyCheckResult(BaseModel):
    is_duplicate: bool
    is_false_positive: bool
    similarity_score: float
    matched_entries: List[DataEntryResponse]
    recommendation: str

class ValidationResponse(BaseModel):
    is_valid: bool
    can_add: bool
    message: str
    redundancy_check: Optional[RedundancyCheckResult] = None

class StatisticsResponse(BaseModel):
    total_entries: int
    unique_entries: int
    duplicates_found: int
    false_positives: int
    data_type_distribution: dict
