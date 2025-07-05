from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .deps import get_db
from .logging import api_logger
from .metrics import OPEN_ISSUES_BY_SEVERITY, OPEN_ISSUES_BY_STATUS
from . import models
from sqlalchemy import func, text

router = APIRouter()

@router.get("/health")
def health_check():
    """Basic health check endpoint"""
    api_logger.info("Health check requested")
    return {"status": "ok", "service": "issues-tracker-api"}

@router.get("/health/detailed")
def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with database connectivity and metrics"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        
        # Get basic metrics
        total_users = db.query(func.count(models.User.id)).scalar()
        total_issues = db.query(func.count(models.Issue.id)).scalar()
        
        # Get issues by severity
        severity_counts = db.query(
            models.Issue.severity,
            func.count(models.Issue.id)
        ).filter(models.Issue.status != 'DONE').group_by(models.Issue.severity).all()
        
        # Get issues by status
        status_counts = db.query(
            models.Issue.status,
            func.count(models.Issue.id)
        ).group_by(models.Issue.status).all()
        
        # Update Prometheus metrics
        for severity, count in severity_counts:
            OPEN_ISSUES_BY_SEVERITY.labels(severity=severity).set(count)
        
        for status, count in status_counts:
            OPEN_ISSUES_BY_STATUS.labels(status=status).set(count)
        
        api_logger.info("Detailed health check completed successfully")
        
        return {
            "status": "healthy",
            "database": "connected",
            "metrics": {
                "total_users": total_users,
                "total_issues": total_issues,
                "issues_by_severity": dict(severity_counts),
                "issues_by_status": dict(status_counts)
            }
        }
        
    except Exception as e:
        api_logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        } 