from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Issue metrics
ISSUE_CREATED = Counter(
    'issues_created_total',
    'Total number of issues created',
    ['severity', 'status']
)

ISSUE_STATUS_CHANGED = Counter(
    'issue_status_changes_total',
    'Total number of issue status changes',
    ['from_status', 'to_status']
)

# User metrics
USER_LOGIN_ATTEMPTS = Counter(
    'user_login_attempts_total',
    'Total number of login attempts',
    ['success']
)

# Database metrics
DB_OPERATION_DURATION = Histogram(
    'database_operation_duration_seconds',
    'Database operation duration in seconds',
    ['operation', 'table']
)

# Active users gauge
ACTIVE_USERS = Gauge(
    'active_users_current',
    'Current number of active users'
)

# Open issues by severity gauge
OPEN_ISSUES_BY_SEVERITY = Gauge(
    'open_issues_by_severity',
    'Number of open issues by severity',
    ['severity']
)

# Open issues by status gauge
OPEN_ISSUES_BY_STATUS = Gauge(
    'open_issues_by_status',
    'Number of open issues by status',
    ['status']
)

def get_metrics():
    """Return Prometheus metrics"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

class MetricsMiddleware:
    """Middleware to collect request metrics"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        method = scope["method"]
        path = scope["path"]
        
        # Start timing
        start_time = time.time()
        
        # Track request
        REQUEST_COUNT.labels(method=method, endpoint=path, status="pending").inc()
        
        # Process request
        try:
            await self.app(scope, receive, send)
            status = "200"  # Default success status
        except Exception as e:
            status = "500"
            raise e
        finally:
            # Record metrics
            duration = time.time() - start_time
            REQUEST_DURATION.labels(method=method, endpoint=path).observe(duration)
            REQUEST_COUNT.labels(method=method, endpoint=path, status=status).inc()

def update_issue_metrics(severity, status):
    """Update issue-related metrics"""
    ISSUE_CREATED.labels(severity=severity, status=status).inc()
    OPEN_ISSUES_BY_SEVERITY.labels(severity=severity).inc()
    OPEN_ISSUES_BY_STATUS.labels(status=status).inc()

def update_status_change_metrics(from_status, to_status):
    """Update status change metrics"""
    ISSUE_STATUS_CHANGED.labels(from_status=from_status, to_status=to_status).inc()
    OPEN_ISSUES_BY_STATUS.labels(status=from_status).dec()
    OPEN_ISSUES_BY_STATUS.labels(status=to_status).inc()

def update_login_metrics(success):
    """Update login attempt metrics"""
    USER_LOGIN_ATTEMPTS.labels(success=str(success).lower()).inc()
    if success:
        ACTIVE_USERS.inc()

def update_logout_metrics():
    """Update logout metrics"""
    ACTIVE_USERS.dec() 