from celery import shared_task
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from .database import SessionLocal
from .models import Issue, DailyStats, IssueStatus
from .logging import db_logger

@shared_task
def aggregate_daily_stats():
    """Aggregate issue counts by status into daily_stats table every 30 minutes"""
    db = SessionLocal()
    try:
        today = date.today()
        db_logger.info(f"Starting daily stats aggregation for {today}")
        
        # Check if stats already exist for today
        existing_stats = db.query(DailyStats).filter(
            func.date(DailyStats.date) == today
        ).first()
        
        if existing_stats:
            db_logger.info(f"Stats already exist for {today}, skipping aggregation")
            return {"status": "skipped", "reason": "already_exists"}
        
        # Get issue counts by status
        status_counts = db.query(
            Issue.status,
            func.count(Issue.id).label('count')
        ).group_by(Issue.status).all()
        
        # Create daily stats records
        for status, count in status_counts:
            daily_stat = DailyStats(
                date=datetime.now(),
                status=status,
                count=count
            )
            db.add(daily_stat)
        
        db.commit()
        db_logger.info(f"Daily stats aggregation completed for {today}")
        
        return {
            "status": "success",
            "date": today.isoformat(),
            "stats_created": len(status_counts)
        }
        
    except Exception as e:
        db_logger.error(f"Error in daily stats aggregation: {str(e)}")
        db.rollback()
        raise e
    finally:
        db.close()

@shared_task
def cleanup_old_logs():
    """Clean up old log files and database records"""
    db_logger.info("Starting cleanup of old logs and records")
    
    # This would typically clean up old log files and database records
    # For now, just log the task execution
    db_logger.info("Cleanup task completed")
    
    return {"status": "success", "task": "cleanup_old_logs"}

@shared_task
def send_notifications():
    """Send notifications for critical issues"""
    db = SessionLocal()
    try:
        # Find critical issues that are still open
        critical_issues = db.query(Issue).filter(
            Issue.severity == 'CRITICAL',
            Issue.status != IssueStatus.DONE
        ).all()
        
        if critical_issues:
            db_logger.warning(f"Found {len(critical_issues)} critical open issues")
            # Here you would implement actual notification sending
            # For now, just log the count
        
        return {
            "status": "success",
            "critical_issues_count": len(critical_issues)
        }
        
    except Exception as e:
        db_logger.error(f"Error in notification task: {str(e)}")
        raise e
    finally:
        db.close()

@shared_task
def update_metrics():
    """Update Prometheus metrics from database"""
    from .metrics import OPEN_ISSUES_BY_SEVERITY, OPEN_ISSUES_BY_STATUS
    
    db = SessionLocal()
    try:
        # Update severity metrics
        severity_counts = db.query(
            Issue.severity,
            func.count(Issue.id)
        ).filter(Issue.status != IssueStatus.DONE).group_by(Issue.severity).all()
        
        for severity, count in severity_counts:
            OPEN_ISSUES_BY_SEVERITY.labels(severity=severity).set(count)
        
        # Update status metrics
        status_counts = db.query(
            Issue.status,
            func.count(Issue.id)
        ).group_by(Issue.status).all()
        
        for status, count in status_counts:
            OPEN_ISSUES_BY_STATUS.labels(status=status).set(count)
        
        db_logger.info("Metrics updated successfully")
        return {"status": "success", "metrics_updated": True}
        
    except Exception as e:
        db_logger.error(f"Error updating metrics: {str(e)}")
        raise e
    finally:
        db.close() 