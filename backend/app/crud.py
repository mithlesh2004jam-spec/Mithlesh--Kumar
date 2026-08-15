
from sqlalchemy.orm import Session
from sqlalchemy import func

import models
import schemas


# -------------------------
# USERS
# -------------------------

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_users(db: Session):
    return db.query(models.User).all()


# -------------------------
# PROJECTS
# -------------------------

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(
        name=project.name,
        owner_id=project.owner_id
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project


def get_projects(db: Session):
    return db.query(models.Project).all()


# -------------------------
# TASKS
# -------------------------

def create_task(db: Session, task: schemas.TaskCreate):
    db_task = models.Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        status=task.status,
        project_id=task.project_id
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


def get_tasks(db: Session):
    return db.query(models.Task).all()


def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()


def update_task(
    db: Session,
    task_id: int,
    task: schemas.TaskCreate
):
    db_task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if db_task is None:
        return None

    db_task.title = task.title
    db_task.description = task.description
    db_task.priority = task.priority
    db_task.due_date = task.due_date
    db_task.status = task.status
    db_task.project_id = task.project_id

    db.commit()
    db.refresh(db_task)

    return db_task


def delete_task(db: Session, task_id: int):
    db_task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if db_task is None:
        return None

    db.delete(db_task)
    db.commit()

    return {"message": "Task deleted successfully"}


# -------------------------
# DASHBOARD STATISTICS
# -------------------------

def get_dashboard_stats(db: Session):
    total_projects = db.query(models.Project).count()
    total_tasks = db.query(models.Task).count()

    completed_tasks = db.query(models.Task).filter(
        models.Task.status == "completed"
    ).count()

    pending_tasks = db.query(models.Task).filter(
        models.Task.status == "pending"
    ).count()

    return {
        "total_projects": total_projects,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks
    }


# -------------------------
# SEARCH
# -------------------------

def search_tasks(db: Session, title: str):
    return db.query(models.Task).filter(
        models.Task.title.ilike(f"%{title}%")
    ).all()


# -------------------------
# PROJECT TASK STATISTICS
# -------------------------

def get_project_statistics(db: Session):
    results = (
        db.query(
            models.Project.id.label("project_id"),
            models.Project.name.label("project_name"),
            func.count(models.Task.id).label("task_count")
        )
        .outerjoin(
            models.Task,
            models.Project.id == models.Task.project_id
        )
        .group_by(
            models.Project.id,
            models.Project.name
        )
        .all()
    )

    return [
        {
            "project_id": row.project_id,
            "project_name": row.project_name,
            "task_count": row.task_count
        }
        for row in results
    ]