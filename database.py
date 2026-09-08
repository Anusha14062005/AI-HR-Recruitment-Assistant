import os
import sqlite3
import logging
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("Database")

# Global pool / connection holder
_mysql_pool = None
_db_mode = None  # 'mysql' or 'sqlite'
_sqlite_path = os.path.join(os.path.dirname(__file__), 'database', 'ai_hr_recruitment.db')

def init_db_connection():
    """Attempt connection to MySQL; fallback to SQLite if credentials fail or server unreachable."""
    global _mysql_pool, _db_mode
    
    # Try MySQL first if credentials or host configured
    try:
        import mysql.connector
        from mysql.connector import pooling
        
        pool_config = {
    "pool_name": "hr_recruitment_pool",
    "pool_size": 5,
    "pool_reset_session": True,
    "host": Config.DB_HOST,
    "port": Config.DB_PORT,
    "user": Config.DB_USER,
    "password": "2006",
    "database": "recruitment",
    "charset": "utf8mb4"
}
        
        _mysql_pool = pooling.MySQLConnectionPool(**pool_config)
        
        # Test connection
        conn = _mysql_pool.get_connection()
        conn.close()
        _db_mode = 'mysql'
        logger.info(f"Connected to MySQL database '{Config.DB_NAME}' at {Config.DB_HOST}:{Config.DB_PORT}")
        return True
        
    except Exception as e:
        logger.warning(
            f"MySQL connection to '{Config.DB_NAME}' failed: {e}.\n"
            f">> NOTICE: To use MySQL, set DB_PASSWORD in your .env file and run 'python init_db.py'.\n"
            f">> Seamlessly activating resilient local database fallback so application runs immediately."
        )
        _db_mode = 'sqlite'
        os.makedirs(os.path.dirname(_sqlite_path), exist_ok=True)
        return False

def get_db_mode():
    """Return current active database mode ('mysql' or 'sqlite')."""
    global _db_mode
    if _db_mode is None:
        init_db_connection()
    return _db_mode

def get_connection():
    """Get a raw connection depending on the active engine."""
    mode = get_db_mode()
    if mode == 'mysql':
        import mysql.connector
        return _mysql_pool.get_connection()
    else:
        conn = sqlite3.connect(_sqlite_path)
        conn.row_factory = sqlite3.Row
        return conn

def _format_sql_for_engine(query: str) -> str:
    """Format placeholder and dialect syntax if using SQLite."""
    if get_db_mode() == 'sqlite':
        import re
        q = query.replace('%s', '?')
        if 'ON DUPLICATE KEY UPDATE' in q.upper():
            q = re.sub(r'\s*ON DUPLICATE KEY UPDATE.*$', '', q, flags=re.DOTALL | re.IGNORECASE)
            q = re.sub(r'INSERT\s+INTO', 'INSERT OR REPLACE INTO', q, flags=re.IGNORECASE)
        return q
    return query

def execute_query(query: str, params=None, commit: bool = True):
    """Execute a parameterized query (UPDATE, DELETE, etc.)."""
    mode = get_db_mode()
    sql = _format_sql_for_engine(query)
    params = params or ()
    
    if mode == 'mysql':
        conn = _mysql_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, params)
            if commit:
                conn.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conn.close()
    else:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            if commit:
                conn.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conn.close()

def execute_insert(query: str, params=None):
    """Execute an INSERT query and return the last generated primary key."""
    mode = get_db_mode()
    sql = _format_sql_for_engine(query)
    params = params or ()
    
    if mode == 'mysql':
        conn = _mysql_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()
    else:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()

def fetch_one(query: str, params=None):
    """Execute a SELECT query and return a single row as a dictionary."""
    mode = get_db_mode()
    sql = _format_sql_for_engine(query)
    params = params or ()
    
    if mode == 'mysql':
        conn = _mysql_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, params)
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
    else:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            cursor.close()
            conn.close()

def fetch_all(query: str, params=None):
    """Execute a SELECT query and return all matching rows as a list of dictionaries."""
    mode = get_db_mode()
    sql = _format_sql_for_engine(query)
    params = params or ()
    
    if mode == 'mysql':
        conn = _mysql_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, params)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    else:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
        finally:
            cursor.close()
            conn.close()
