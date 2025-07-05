#!/usr/bin/env python3
"""
Simple test runner for the backend
"""
import subprocess
import sys
import os

def run_tests():
    """Run backend tests"""
    try:
        # Install test dependencies if not already installed
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov", "fastapi-testclient"], check=True)
        
        # Run tests
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v", "--cov=app", "--cov-report=html"], cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_tests() 