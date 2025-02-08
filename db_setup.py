import sqlite3
import bcrypt
import logging
from pathlib import Path
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_database_directory():
    """Create the database directory if it doesn't exist"""
    try:
        # Create database directory
        db_dir = Path(Config.DB_PATH).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Database directory created at: {db_dir}")
        return True
    except Exception as e:
        logger.error(f"Failed to create database directory: {e}")
        return False

def init_database():
    """Initialize the database with required tables"""
    try:
        # Create database directory
        if not create_database_directory():
            return False

        # Connect to database (this will create it if it doesn't exist)
        conn = sqlite3.connect(Config.DB_PATH)
        cursor = conn.cursor()

        # Create users table
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

        # Create audit_log table
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

        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Create root user if it doesn't exist
        cursor.execute("SELECT 1 FROM users WHERE username = 'root'")
        if not cursor.fetchone():
            # Hash the password
            hashed_password = bcrypt.hashpw("root123".encode(), bcrypt.gensalt()).decode()
            
            # Insert root user
            cursor.execute('''
                INSERT INTO users (username, email, password, role, is_active)
                VALUES (?, ?, ?, ?, ?)
            ''', ('root', 'root@admin.com', hashed_password, 'Root', True))
            logger.info("Root user created successfully")

        # Commit changes and close connection
        conn.commit()
        conn.close()

        logger.info(f"Database initialized successfully at: {Config.DB_PATH}")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

if __name__ == "__main__":
    print("Starting database initialization...")
    if init_database():
        print(f"Database initialized successfully at: {Config.DB_PATH}")
        print("Root user credentials:")
        print("Username: root")
        print("Password: root123")
    else:
        print("Failed to initialize database. Check the logs for details.")
