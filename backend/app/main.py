
import os
import time
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    create_engine,
    func,
)
from sqlalchemy.orm import declarative_base, relationship, Session, sessionmaker


# ============================================================
# DATABASE
# ============================================================

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./taskflow.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


# ============================================================
# DATABASE MODELS
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)

    projects = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan",
    )


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="projects")
    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
    )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    priority = Column(String, nullable=False, default="medium")
    due_date = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending")
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    project = relationship("Project", back_populates="tasks")


Base.metadata.create_all(bind=engine)


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="TaskFlow API",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

FRONTEND_ORIGIN = os.getenv(
    "FRONTEND_ORIGIN",
    "https://taskflow-frontend-9m9w.onrender.com",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_ORIGIN,
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST LOGGING MIDDLEWARE
# ============================================================

@app.middleware("http")
async def logging_middleware(request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    elapsed = time.perf_counter() - start_time

    print(
        f"{request.method} {request.url.path} "
        f"- {response.status_code} "
        f"- {elapsed:.4f}s"
    )

    return response


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# PYDANTIC SCHEMAS
# ============================================================

class UserCreate(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        value = value.strip().lower()

        if "@" not in value:
            raise ValueError("Invalid email address")

        return value


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str


class ProjectCreate(BaseModel):
    name: str
    owner_id: int


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    owner_id: int


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[str] = None
    status: str = "pending"
    project_id: int

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Title cannot be blank")

        return value

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value):
        value = value.lower()

        if value not in {"low", "medium", "high"}:
            raise ValueError(
                "Priority must be low, medium, or high"
            )

        return value


class TaskUpdate(TaskCreate):
    pass


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    priority: str
    due_date: Optional[str]
    status: str
    project_id: int


class QuickAddRequest(BaseModel):
    description: str
    project_id: int


class ProjectStatistics(BaseModel):
    project_id: int
    total_tasks: int
    pending_tasks: int
    completed_tasks: int


# ============================================================
# ROOT / HEALTH
# ============================================================

@app.get("/")
def root():
    return {
        "message": "TaskFlow API is running",
        "status": "ok",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# ============================================================
# USERS
# ============================================================

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    new_user = User(email=user.email)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
):
    return db.query(User).all()


# ============================================================
# PROJECTS
# ============================================================

@app.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=201,
)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
):
    owner = (
        db.query(User)
        .filter(User.id == project.owner_id)
        .first()
    )

    if not owner:
        raise HTTPException(
            status_code=404,
            detail="Owner not found",
        )

    new_project = Project(
        name=project.name,
        owner_id=project.owner_id,
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


@app.get(
    "/projects",
    response_model=list[ProjectResponse],
)
def list_projects(
    db: Session = Depends(get_db),
):
    return db.query(Project).all()


# ============================================================
# ALGORITHMS
# ============================================================

PRIORITY_RANK = {
    "low": 1,
    "medium": 2,
    "high": 3,
}


def insertion_sort(records, key):
    for i in range(1, len(records)):
        current = records[i]
        current_key = key(current)

        j = i - 1

        while j >= 0 and key(records[j]) > current_key:
            records[j + 1] = records[j]
            j -= 1

        records[j + 1] = current

    return records

def linear_search(records, target_value, key):
    target = target_value.strip().lower()

    for record in records:
        value = key(record)

        if value and value.strip().lower() == target:
            return record

    return None


def binary_search(sorted_records, target_value, key):
    left = 0
    right = len(sorted_records) - 1

    while left <= right:
        middle = (left + right) // 2
        value = key(sorted_records[middle])

        if value == target_value:
            return sorted_records[middle]

        if value < target_value:
            left = middle + 1
        else:
            right = middle - 1

    return None


# ============================================================
# TASK CRUD
# ============================================================

@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=201,
)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
):
    project = (
        db.query(Project)
        .filter(Project.id == task.project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    new_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        status=task.status,
        project_id=task.project_id,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@app.get(
    "/tasks",
    response_model=list[TaskResponse],
)
def list_tasks(
    sort: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    tasks = db.query(Task).all()

    if sort == "priority":
        insertion_sort(
            tasks,
            lambda task: PRIORITY_RANK.get(
                task.priority,
                2,
            ),
        )

    return tasks


@app.get(
    "/tasks/search",
    response_model=Optional[TaskResponse],
)
def search_tasks(
    title: str,
    algo: str = "linear",
    db: Session = Depends(get_db),
):
    tasks = db.query(Task).all()

    if algo == "linear":
        result = linear_search(
            tasks,
            title,
            lambda task: task.title,
        )

    elif algo == "binary":
        insertion_sort(
            tasks,
            lambda task: task.title,
        )

        result = binary_search(
            tasks,
            title,
            lambda task: task.title,
        )

    else:
        raise HTTPException(
            status_code=400,
            detail="Algorithm must be binary or linear",
        )

    return result


@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@app.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    project = (
        db.query(Project)
        .filter(Project.id == task_data.project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    task.title = task_data.title
    task.description = task_data.description
    task.priority = task_data.priority
    task.due_date = task_data.due_date
    task.status = task_data.status
    task.project_id = task_data.project_id

    db.commit()
    db.refresh(task)

    return task


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully",
        "id": task_id,
    }


# ============================================================
# PROJECT STATISTICS
# ============================================================

@app.get(
    "/projects/{project_id}/statistics",
    response_model=ProjectStatistics,
)
def project_statistics(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    total_tasks = (
        db.query(func.count(Task.id))
        .filter(Task.project_id == project_id)
        .scalar()
    )

    pending_tasks = (
        db.query(func.count(Task.id))
        .filter(
            Task.project_id == project_id,
            Task.status == "pending",
        )
        .scalar()
    )

    completed_tasks = (
        db.query(func.count(Task.id))
        .filter(
            Task.project_id == project_id,
            Task.status == "completed",
        )
        .scalar()
    )

    return ProjectStatistics(
        project_id=project_id,
        total_tasks=total_tasks or 0,
        pending_tasks=pending_tasks or 0,
        completed_tasks=completed_tasks or 0,
    )


# ============================================================
# AI QUICK-ADD
# ============================================================

def parse_quick_add(description: str):
    text = description.strip()
    lower = text.lower()

    priority = "medium"

    if any(word in lower for word in ["urgent", "asap", "critical"]):
        priority = "high"

    elif any(word in lower for word in ["low priority", "not urgent"]):
        priority = "low"

    due_date_hint = None

    if "today" in lower:
        due_date_hint = "today"

    elif "tomorrow" in lower:
        due_date_hint = "tomorrow"

    title = text

    for marker in [
        " urgent",
        " asap",
        " today",
        " tomorrow",
        " high priority",
        " low priority",
    ]:
        index = lower.find(marker)

        if index > 0:
            title = text[:index].strip()
            break

    return {
        "title": title or text,
        "priority": priority,
        "due_date_hint": due_date_hint,
    }


@app.post(
    "/tasks/quick-add",
    response_model=TaskResponse,
    status_code=201,
)
def quick_add_task(
    request: QuickAddRequest,
    db: Session = Depends(get_db),
):
    project = (
        db.query(Project)
        .filter(Project.id == request.project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    parsed = parse_quick_add(request.description)

    new_task = Task(
        title=parsed["title"],
        description=request.description,
        priority=parsed["priority"],
        due_date=parsed["due_date_hint"],
        status="pending",
        project_id=request.project_id,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task