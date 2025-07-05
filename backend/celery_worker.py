#!/usr/bin/env python3
"""
Celery worker for background tasks
"""
from app.celery_app import celery_app

if __name__ == "__main__":
    celery_app.start() 