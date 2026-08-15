
"""
main.py
-------
TaskFlow FastAPI application
"""

import time
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import models
from . import schemas

from .algorithms import (
    insertion_sort,
    binary_search,
    linear_search,
    PRIORITY_RANK,
)

from .ai_quickadd import parse_task


# ============================================================
# DATABASE
# ============================================================

Base.metadata.create_all(bind=engine)


# ============================================================
# APP
# ============================================================

app = FastAPI(title="TaskFlow API")


# ============================================================
# CORS
# ============================================================

FRONTEND_ORIGIN = "http://127.0.0.1:5500"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_ORIGIN,
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Content-Type",
        "Authorization",
    ],
)


# ============================================================
# MIDDLEWARE
# ============================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()

    response = await call_next(request)

    duration_ms = (time.perf_counter() - start) * 1000

    print(
        f"{request.method} "
        f"{request.url.path} "
        f"completed in {duration_ms:.2f}ms"
    )

    return response


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "TaskFlow API is running"
    }


# ============================================================
# USERS
# ============================================================

@app.post(
    "/users",
    response_model=schemas.UserOut,
    status_code=201
)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    existing = (
        db.query(models.User)
        .filter(models.User.email == user.email)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=422,
            detail="Email already registered"
        )

    db_user = models.User(
        email=user.email
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@app.get(
    "/users",
    response_model=List[schemas.UserOut]
)
def list_users(
    db: Session = Depends(get_db)
):
    return db.query(models.User).all()


# ============================================================
# PROJECTS
# ============================================================

@app.post(
    "/projects",
    response_model=schemas.ProjectOut,
    status_code=201
)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db)
):
    owner = (
        db.query(models.User)
        .filter(models.User.id == project.owner_id)
        .first()
    )

    if not owner:
        raise HTTPException(
            status_code=422,
            detail="owner_id does not reference an existing user"
        )

    db_project = models.Project(
        name=project.name,
        owner_id=project.owner_id
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project


@app.get(
    "/projects",
    response_model=List[schemas.ProjectOut]
)
def list_projects(
    db: Session = Depends(get_db)
):
    return db.query(models.Project).all()


# ============================================================
# PROJECT STATISTICS
# ============================================================

@app.get(
    "/projects/{project_id}/stats",
    response_model=schemas.ProjectStats
)
def project_stats(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = (
        db.query(models.Project)
        .filter(models.Project.id == project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    total_tasks = (
        db.query(func.count(models.Task.id))
        .filter(models.Task.project_id == project_id)
        .scalar()
    )

    rows = (
        db.query(
            models.Task.status,
            func.count(models.Task.id)
        )
        .filter(models.Task.project_id == project_id)
        .group_by(models.Task.status)
        .all()
    )

    by_status = {
        status: count
        for status, count in rows
    }

    return schemas.ProjectStats(
        project_id=project.id,
        project_name=project.name,
        total_tasks=total_tasks or 0,
        by_status=by_status,
    )


# ============================================================
# TASKS - CREATE
# ============================================================

@app.post(
    "/tasks",
    response_model=schemas.TaskOut,
    status_code=201
)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db)
):
    project = (
        db.query(models.Project)
        .filter(models.Project.id == task.project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=422,
            detail="project_id does not reference an existing project"
        )

    db_task = models.Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        status=task.status or "pending",
        project_id=task.project_id,
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


# ============================================================
# TASKS - LIST / SORT
#
# IMPORTANT:
# This route comes BEFORE /tasks/{task_id}
# ============================================================

@app.get(
    "/tasks",
    response_model=List[schemas.TaskOut]
)
def list_tasks(
    sort: Optional[str] = None,
    db: Session = Depends(get_db)
):
    tasks = db.query(models.Task).all()

    if sort is None:
        return tasks

    if sort not in ["priority", "due_date"]:
        raise HTTPException(
            status_code=422,
            detail="sort must be 'priority' or 'due_date'"
        )

    records = [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "due_date": task.due_date or "",
            "status": task.status,
            "project_id": task.project_id,
        }
        for task in tasks
    ]

    if sort == "priority":

        for record in records:
            record["priority_rank"] = PRIORITY_RANK.get(
                record["priority"],
                2
            )

        insertion_sort(
            records,
            key="priority_rank"
        )

        for record in records:
            record.pop("priority_rank", None)

    elif sort == "due_date":

        insertion_sort(
            records,
            key="due_date"
        )

    return records


# ============================================================
# TASKS - SORTED ENDPOINT
# ============================================================

@app.get(
    "/tasks/sorted",
    response_model=List[schemas.TaskOut]
)
def sorted_tasks(
    sort: str = "priority",
    db: Session = Depends(get_db)
):
    tasks = db.query(models.Task).all()

    records = [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "due_date": task.due_date or "",
            "status": task.status,
            "project_id": task.project_id,
        }
        for task in tasks
    ]

    if sort == "priority":

        for record in records:
            record["priority_rank"] = PRIORITY_RANK.get(
                record["priority"],
                2
            )

        insertion_sort(
            records,
            key="priority_rank"
        )

        for record in records:
            record.pop("priority_rank", None)

    elif sort == "due_date":

        insertion_sort(
            records,
            key="due_date"
        )

    else:
        raise HTTPException(
            status_code=422,
            detail="sort must be 'priority' or 'due_date'"
        )

    return records


# ============================================================
# TASK SEARCH
#
# IMPORTANT:
# This comes BEFORE /tasks/{task_id}
# ============================================================

@app.get(
    "/tasks/search",
    response_model=schemas.TaskOut
)
def search_tasks(
    title: str,
    algo: str = "binary",
    db: Session = Depends(get_db)
):
    tasks = db.query(models.Task).all()

    index = [
        {
            "id": task.id,
            "title": task.title
        }
        for task in tasks
    ]

    if algo == "binary":

        insertion_sort(
            index,
            key="title"
        )

        found_idx = binary_search(
            index,
            title,
            key="title"
        )

    elif algo == "linear":

        found_idx = linear_search(
            index,
            title,
            key="title"
        )

    else:
        raise HTTPException(
            status_code=422,
            detail="algo must be 'binary' or 'linear'"
        )

    if found_idx is None or found_idx == -1:
        raise HTTPException(
            status_code=404,
            detail="No task with that exact title"
        )

    task_id = index[found_idx]["id"]

    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


# ============================================================
# TASK - GET BY ID
#
# This comes AFTER /tasks/search and /tasks/sorted
# ============================================================

@app.get(
    "/tasks/{task_id}",
    response_model=schemas.TaskOut
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


# ============================================================
# TASK - UPDATE
# ============================================================

@app.put(
    "/tasks/{task_id}",
    response_model=schemas.TaskOut
)
def update_task(
    task_id: int,
    update: schemas.TaskUpdate,
    db: Session = Depends(get_db)
):
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    update_data = update.model_dump(
        exclude_unset=True
    )

    if "project_id" in update_data:

        project = (
            db.query(models.Project)
            .filter(
                models.Project.id == update_data["project_id"]
            )
            .first()
        )

        if not project:
            raise HTTPException(
                status_code=422,
                detail="project_id does not reference an existing project"
            )

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


# ============================================================
# TASK - DELETE
# ============================================================

@app.delete(
    "/tasks/{task_id}",
    status_code=200
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()

    return {
        "detail": "Task deleted",
        "id": task_id
    }


# ============================================================
# AI QUICK ADD
# ============================================================

@app.post(
    "/tasks/quick-add",
    response_model=schemas.TaskOut,
    status_code=201
)
def quick_add_task(
    payload: schemas.QuickAddIn,
    db: Session = Depends(get_db)
):
    project = (
        db.query(models.Project)
        .filter(
            models.Project.id == payload.project_id
        )
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=422,
            detail="project_id does not reference an existing project"
        )

    parsed = parse_task(
        payload.description
    )

    db_task = models.Task(
        title=parsed["title"],
        priority=parsed["priority"],
        due_date=parsed.get("due_date_hint"),
        status="pending",
        project_id=payload.project_id,
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task