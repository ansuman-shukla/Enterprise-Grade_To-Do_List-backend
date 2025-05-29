from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class Priority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class TaskCreateNLP(BaseModel):
    """Model for natural language task input"""
    text: str = Field(..., min_length=1, max_length=500, description="Natural language task description")


class TaskCreateStructured(BaseModel):
    """Model for structured task data from LLM or direct input"""
    task_name: str = Field(..., min_length=1, max_length=200)
    assignee: Optional[str] = Field(None, max_length=100)
    due_date_time: Optional[datetime] = None
    priority: Priority = Field(default=Priority.P3)
    original_text: Optional[str] = Field(None, max_length=500)


class TaskUpdate(BaseModel):
    """Model for updating existing tasks"""
    task_name: Optional[str] = Field(None, min_length=1, max_length=200)
    assignee: Optional[str] = Field(None, max_length=100)
    due_date_time: Optional[datetime] = None
    priority: Optional[Priority] = None


class TaskResponse(BaseModel):
    """Model for task responses to frontend"""
    id: str = Field(..., description="Task ID")
    task_name: str
    assignee: Optional[str] = None
    due_date_time: Optional[datetime] = None
    priority: Priority
    original_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GeminiResponse(BaseModel):
    """Model for Gemini LLM response"""
    task_name: str
    assignee: Optional[str] = None
    due_date_time: Optional[str] = None  # Will be parsed to datetime
    priority_hint: Optional[str] = None


class APIResponse(BaseModel):
    """Standard API response model"""
    success: bool
    message: str
    data: Optional[dict] = None
