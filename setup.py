#!/usr/bin/env python3
"""
Setup script for Issues & Insights Tracker
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"✅ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return False

def setup_backend():
    """Setup backend dependencies"""
    print("🔧 Setting up backend...")
    
    # Create necessary directories
    os.makedirs("backend/uploads", exist_ok=True)
    os.makedirs("backend/logs", exist_ok=True)
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "backend"):
        return False
    
    # Install test dependencies
    run_command("pip install pytest pytest-cov fastapi-testclient", "backend")
    
    return True

def setup_frontend():
    """Setup frontend dependencies"""
    print("🔧 Setting up frontend...")
    
    # Install Node.js dependencies
    if not run_command("npm install", "frontend"):
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Issues & Insights Tracker...")
    
    # Check if we're in the right directory
    if not (Path("backend") / "requirements.txt").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Setup backend
    if not setup_backend():
        print("❌ Backend setup failed")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed")
        sys.exit(1)
    
    print("\n✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the database: docker-compose up db -d")
    print("2. Run migrations: cd backend && alembic upgrade head")
    print("3. Start the application: docker-compose up")
    print("4. Visit http://localhost:3000")

if __name__ == "__main__":
    main() 