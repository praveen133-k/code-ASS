from sqlalchemy.orm import Session
from typing import Optional
from . import models, schemas
from passlib.context import CryptContext
from .logging import db_logger
import time

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# User CRUD
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    start_time = time.time()
    db_logger.info(f"Creating user: {user.email}")
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    duration = time.time() - start_time
    db_logger.info(f"User created successfully: {db_user.id} in {duration:.3f}s")
    return db_user

# Issue CRUD
def get_issue(db: Session, issue_id: int):
    return db.query(models.Issue).filter(models.Issue.id == issue_id).first()

def get_issues(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[int] = None):
    query = db.query(models.Issue)
    if user_id:
        query = query.filter(models.Issue.reporter_id == user_id)
    return query.offset(skip).limit(limit).all()

def create_issue(db: Session, issue: schemas.IssueCreate, reporter_id: int):
    start_time = time.time()
    db_logger.info(f"Creating issue: {issue.title} by reporter: {reporter_id}")
    issue_data = issue.dict()
    issue_data['reporter_id'] = reporter_id
    db_issue = models.Issue(**issue_data)
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    duration = time.time() - start_time
    db_logger.info(f"Issue created successfully: {db_issue.id} in {duration:.3f}s")
    return db_issue

def update_issue(db: Session, issue_id: int, issue: schemas.IssueUpdate):
    start_time = time.time()
    db_logger.info(f"Updating issue: {issue_id}")
    db_issue = get_issue(db, issue_id)
    if db_issue:
        update_data = issue.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_issue, field, value)
        db.commit()
        db.refresh(db_issue)
        duration = time.time() - start_time
        db_logger.info(f"Issue updated successfully: {issue_id} in {duration:.3f}s")
    else:
        db_logger.warning(f"Issue not found for update: {issue_id}")
    return db_issue

def delete_issue(db: Session, issue_id: int):
    db_issue = get_issue(db, issue_id)
    if db_issue:
        db.delete(db_issue)
        db.commit()
    return db_issue 