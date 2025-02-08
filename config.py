from decouple import config
from pathlib import Path

# Create database directory if it doesn't exist
Path("database").mkdir(exist_ok=True)

class Config:
    # Use absolute path for database
    DB_PATH = str(Path(__file__).parent / "database" / "users.db")
    SECRET_KEY = config('SECRET_KEY', default='your-secret-key-change-in-production')
    JWT_EXPIRY_HOURS = config('JWT_EXPIRY_HOURS', default=24, cast=int)
    
    ROLES_HIERARCHY = {
        "Root": ["ALL"],
        "Admin": ["VIEW_USERS", "ADD_USER", "EDIT_USER", "DELETE_USER", "VIEW_LOGS"],
        "Manager": ["VIEW_USERS", "ADD_USER", "EDIT_USER", "VIEW_LOGS"],
        "User": ["VIEW_PROFILE", "EDIT_PROFILE"],
        "Viewer": ["VIEW_PROFILE"]
    }