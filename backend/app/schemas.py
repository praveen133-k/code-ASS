from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .models import UserRole, IssueStatus, IssueSeverity

class UserBase(BaseModel):
    email: str
    role: UserRole = UserRole.REPORTER

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    google_id: Optional[str] = None
    class Config:
        from_attributes = True

class IssueBase(BaseModel):
    title: str
    description: str
    severity: IssueSeverity
    status: IssueStatus = IssueStatus.OPEN

class IssueCreate(IssueBase):
    pass

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[IssueSeverity] = None
    status: Optional[IssueStatus] = None

class Issue(IssueBase):
    id: int
    file_path: Optional[str] = None
    reporter_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class DailyStats(BaseModel):
    id: int
    date: datetime
    status: IssueStatus
    count: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str 