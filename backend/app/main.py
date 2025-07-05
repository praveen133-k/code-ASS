from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import crud, models, schemas, deps
from .database import engine, SessionLocal
from .models import Base
from .logging import api_logger, auth_logger
from .metrics import get_metrics, update_issue_metrics, update_status_change_metrics, update_login_metrics
from .health import router as health_router
from .upload import save_upload_file, delete_upload_file, get_file_path
from fastapi import File, UploadFile
from fastapi.responses import FileResponse
import os
from datetime import timedelta

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Issues & Insights Tracker")

# Include routers
app.include_router(health_router, tags=["health"])

# Add metrics endpoint
@app.get("/metrics")
def metrics():
    return get_metrics()

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(deps.get_db)):
    auth_logger.info(f"Login attempt for user: {form_data.username}")
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        auth_logger.warning(f"Failed login attempt for user: {form_data.username}")
        update_login_metrics(success=False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=deps.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = deps.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    auth_logger.info(f"Successful login for user: {form_data.username}")
    update_login_metrics(success=True)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(deps.get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(deps.get_current_user)):
    return current_user

@app.post("/issues/", response_model=schemas.Issue)
def create_issue(issue: schemas.IssueCreate, current_user: models.User = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    api_logger.info(f"Creating issue: {issue.title} by user: {current_user.email}")
    created_issue = crud.create_issue(db=db, issue=issue, reporter_id=current_user.id)
    update_issue_metrics(severity=issue.severity, status=issue.status)
    api_logger.info(f"Issue created successfully: {created_issue.id}")
    return created_issue

@app.get("/issues/", response_model=list[schemas.Issue])
def read_issues(skip: int = 0, limit: int = 100, current_user: models.User = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    if current_user.role == models.UserRole.REPORTER:
        issues = crud.get_issues(db, skip=skip, limit=limit, user_id=current_user.id)
    else:
        issues = crud.get_issues(db, skip=skip, limit=limit)
    return issues

@app.get("/issues/{issue_id}", response_model=schemas.Issue)
def read_issue(issue_id: int, current_user: models.User = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    db_issue = crud.get_issue(db, issue_id=issue_id)
    if db_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    if current_user.role == models.UserRole.REPORTER and db_issue.reporter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return db_issue

@app.put("/issues/{issue_id}", response_model=schemas.Issue)
def update_issue(issue_id: int, issue: schemas.IssueUpdate, current_user: models.User = Depends(deps.require_admin_or_maintainer), db: Session = Depends(deps.get_db)):
    api_logger.info(f"Updating issue {issue_id} by user: {current_user.email}")
    db_issue = crud.get_issue(db, issue_id=issue_id)
    if db_issue is None:
        api_logger.warning(f"Issue not found: {issue_id}")
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Track status changes for metrics
    if issue.status and issue.status != db_issue.status:
        api_logger.info(f"Issue {issue_id} status changed from {db_issue.status} to {issue.status}")
        update_status_change_metrics(from_status=db_issue.status, to_status=issue.status)
    
    updated_issue = crud.update_issue(db=db, issue_id=issue_id, issue=issue)
    api_logger.info(f"Issue {issue_id} updated successfully")
    return updated_issue

@app.delete("/issues/{issue_id}")
def delete_issue(issue_id: int, current_user: models.User = Depends(deps.require_role(models.UserRole.ADMIN)), db: Session = Depends(deps.get_db)):
    db_issue = crud.get_issue(db, issue_id=issue_id)
    if db_issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    crud.delete_issue(db=db, issue_id=issue_id)
    return {"ok": True}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), current_user: models.User = Depends(deps.get_current_user)):
    """Upload a file for an issue"""
    api_logger.info(f"File upload requested by user: {current_user.email}")
    filename = await save_upload_file(file)
    return {"filename": filename, "message": "File uploaded successfully"}

@app.get("/files/{filename}")
async def get_file(filename: str):
    """Get uploaded file"""
    file_path = get_file_path(filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path) 