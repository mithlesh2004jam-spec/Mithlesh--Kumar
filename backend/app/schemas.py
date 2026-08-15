
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict


# ============================================================
# USER SCHEMAS
# ============================================================

class UserCreate(BaseModel):
    email: str


class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


# Compatibility name
UserResponse = UserOut


# ============================================================
# PROJECT SCHEMAS
# ============================================================

class ProjectCreate(BaseModel):
    name: str
    owner_id: int


class ProjectOut(BaseModel):
    id: int
    name: str
    owner_id: int

    class Config:
        from_attributes = True


# Compatibility name
ProjectResponse = ProjectOut


# ============================================================
# TASK SCHEMAS
# ============================================================

class TaskCreate(BaseModel):
    title: str

    description: Optional[str] = None

    priority: str = Field(
        default="medium",
        pattern="^(low|medium|high)$"
    )

    due_date: Optional[str] = None

    status: str = "pending"

    project_id: int

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if not value.strip():
            raise ValueError("Title cannot be blank")

        return value


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    priority: str
    due_date: Optional[str] = None
    status: str
    project_id: int

    class Config:
        from_attributes = True


# Compatibility name
TaskResponse = TaskOut


# ============================================================
# TASK UPDATE
# ============================================================

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = Field(
        default=None,
        pattern="^(low|medium|high)$"
    )
    due_date: Optional[str] = None
    status: Optional[str] = None
    project_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if value is not None and not value.strip():
            raise ValueError("Title cannot be blank")

        return value


# ============================================================
# PROJECT STATISTICS
# ============================================================

class ProjectStats(BaseModel):
    project_id: int
    project_name: str
    total_tasks: int
    by_status: Dict[str, int]


# ============================================================
# AI QUICK ADD
# ============================================================

class QuickAddIn(BaseModel):
    description: str
    project_id: int

    @field_validator("description")
    @classmethod
    def validate_description(cls, value):
        if not value.strip():
            raise ValueError("Description cannot be blank")

        return value