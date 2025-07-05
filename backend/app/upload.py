import os
import uuid
from fastapi import UploadFile, HTTPException
from pathlib import Path
from .logging import api_logger

# Upload configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg', '.gif'}

# Create upload directory if it doesn't exist
Path(UPLOAD_DIR).mkdir(exist_ok=True)

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return Path(filename).suffix.lower()

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS

async def save_upload_file(upload_file: UploadFile) -> str:
    """Save uploaded file and return the file path"""
    try:
        # Validate file
        if not upload_file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        if not is_allowed_file(upload_file.filename):
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Generate unique filename
        file_extension = get_file_extension(upload_file.filename)
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Check file size
        content = await upload_file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        api_logger.info(f"File uploaded successfully: {unique_filename}")
        return unique_filename
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Error saving file: {str(e)}")
        raise HTTPException(status_code=500, detail="Error saving file")

def delete_upload_file(filename: str) -> bool:
    """Delete uploaded file"""
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            api_logger.info(f"File deleted: {filename}")
            return True
        return False
    except Exception as e:
        api_logger.error(f"Error deleting file {filename}: {str(e)}")
        return False

def get_file_path(filename: str) -> str:
    """Get full file path for a filename"""
    return os.path.join(UPLOAD_DIR, filename)

def file_exists(filename: str) -> bool:
    """Check if file exists"""
    file_path = os.path.join(UPLOAD_DIR, filename)
    return os.path.exists(file_path) 