from database.db_operations import get_db_connection
import bcrypt
from datetime import datetime

class User:
    def __init__(self, id, username, email, role, is_active=True):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.is_active = is_active

    @staticmethod
    def create(username: str, email: str, password: str, role: str) -> tuple:
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO users (username, email, password, role)
                    VALUES (?, ?, ?, ?)
                ''', (username, email, hashed_password, role))
                conn.commit()
                return True, "User created successfully"
            except sqlite3.IntegrityError:
                return False, "Username or email already exists"

    def has_permission(self, permission: str) -> bool:
        return (permission in Config.ROLES_HIERARCHY[self.role] or 
                "ALL" in Config.ROLES_HIERARCHY[self.role])