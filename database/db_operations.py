import sqlite3
from contextlib import contextmanager
import logging
from pathlib import Path
import sys

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))
from config import Config

logger = logging.getLogger(__name__)

@contextmanager
def get_db_connection():
    conn = None
    try:
        # Ensure database directory exists
        Path(Config.DB_PATH).parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(Config.DB_PATH)
        conn.row_factory = sqlite3.Row
        yield conn
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def init_database():
    """Initialize the database and create tables"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    failed_login_attempts INTEGER DEFAULT 0
                )
            ''')
            
            # Create root user if not exists
            cursor.execute("SELECT 1 FROM users WHERE username = 'root'")
            if not cursor.fetchone():
                import bcrypt
                hashed_password = bcrypt.hashpw("root123".encode(), bcrypt.gensalt()).decode()
                cursor.execute('''
                    INSERT INTO users (username, email, password, role, is_active)
                    VALUES (?, ?, ?, ?, ?)
                ''', ('root', 'root@admin.com', hashed_password, 'Root', True))
            
            # Audit log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

# Initialize database when module is imported
try:
    init_database()
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")