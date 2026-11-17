import os
import sqlite3
import logging
from contextlib import contextmanager
from flask import g, has_app_context
from config import Config

logger = logging.getLogger(__name__)

# Try importing mysql.connector
try:
    import mysql.connector
    from mysql.connector import pooling
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    logger.warning("mysql.connector not installed; will use SQLite fallback")

_mysql_pool = None
_db_mode = None  # 'mysql' or 'sqlite'
_standalone_conn = None

def get_db_mode():
    global _db_mode, _mysql_pool
    if _db_mode is not None:
        return _db_mode
    
    # Check if user explicitly forced SQLite or if MySQL is unavailable
    if Config.USE_SQLITE_FALLBACK or not MYSQL_AVAILABLE:
        _db_mode = 'sqlite'
        return _db_mode
        
    try:
        # Test MySQL connection
        test_conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            connect_timeout=3
        )
        test_conn.close()
        _db_mode = 'mysql'
        logger.info(f"Connected to MySQL database '{Config.DB_NAME}' on {Config.DB_HOST}:{Config.DB_PORT}")
    except Exception as e:
        logger.warning(f"MySQL connection failed ({e}). Falling back to SQLite local database.")
        _db_mode = 'sqlite'
        
    return _db_mode

def get_mysql_pool():
    global _mysql_pool
    if _mysql_pool is None and get_db_mode() == 'mysql':
        try:
            _mysql_pool = pooling.MySQLConnectionPool(
                pool_name="interview_portal_pool",
                pool_size=5,
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                autocommit=True
            )
        except Exception as e:
            logger.error(f"Failed to create MySQL pool: {e}")
            raise
    return _mysql_pool

class SQLiteWrapper:
    """Wrapper around sqlite3 to simulate MySQL dictionary cursor and %s placeholders."""
    def __init__(self, conn):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row

    def _convert_sql(self, sql):
        # Convert %s placeholders to ? for sqlite3
        return sql.replace('%s', '?')

    def cursor(self, dictionary=True):
        return SQLiteCursorWrapper(self.conn.cursor(), self)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

class SQLiteCursorWrapper:
    def __init__(self, cur, wrapper):
        self.cur = cur
        self.wrapper = wrapper
        self.lastrowid = None
        self.rowcount = 0

    def execute(self, sql, params=None):
        converted_sql = self.wrapper._convert_sql(sql)
        if params is None:
            res = self.cur.execute(converted_sql)
        else:
            res = self.cur.execute(converted_sql, params)
        self.lastrowid = self.cur.lastrowid
        self.rowcount = self.cur.rowcount
        return res

    def executemany(self, sql, params_seq):
        converted_sql = self.wrapper._convert_sql(sql)
        res = self.cur.executemany(converted_sql, params_seq)
        self.rowcount = self.cur.rowcount
        return res

    def fetchone(self):
        row = self.cur.fetchone()
        if row is None:
            return None
        return dict(row)

    def fetchall(self):
        rows = self.cur.fetchall()
        return [dict(r) for r in rows]

    def close(self):
        self.cur.close()

def _create_raw_conn():
    mode = get_db_mode()
    if mode == 'mysql':
        pool = get_mysql_pool()
        return pool.get_connection()
    else:
        db_path = str(Config.SQLITE_DB_PATH)
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return SQLiteWrapper(conn)

def get_db():
    """Get database connection for current request context or standalone execution."""
    global _standalone_conn
    if has_app_context():
        if 'db' not in g:
            g.db = _create_raw_conn()
        return g.db
    else:
        # Running in script / test outside request
        if _standalone_conn is None:
            _standalone_conn = _create_raw_conn()
        return _standalone_conn

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass

def execute(sql, params=None):
    """Execute non-returning query (UPDATE, DELETE)."""
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute(sql, params or ())
        if hasattr(db, 'commit'):
            db.commit()
        return cur.rowcount
    finally:
        cur.close()

def execute_insert(sql, params=None):
    """Execute INSERT query and return new row ID."""
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute(sql, params or ())
        if hasattr(db, 'commit'):
            db.commit()
        return cur.lastrowid
    finally:
        cur.close()

def query_all(sql, params=None):
    """Execute SELECT and return list of dictionaries."""
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute(sql, params or ())
        return cur.fetchall()
    finally:
        cur.close()

def query_one(sql, params=None):
    """Execute SELECT and return single dictionary or None."""
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute(sql, params or ())
        return cur.fetchone()
    finally:
        cur.close()

def init_db(app=None):
    """Initialize database tables according to schema."""
    mode = get_db_mode()
    schema_path = Config.BASE_DIR / "schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"schema.sql not found at {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    if mode == 'mysql':
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        cur = conn.cursor()
        # Run statements separated by semicolons
        statements = schema_sql.split(";")
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                cur.execute(stmt)
        conn.commit()
        cur.close()
        conn.close()
        logger.info("MySQL tables initialized successfully.")
    else:
        # SQLite initialization: translate schema to SQLite syntax
        db_path = str(Config.SQLITE_DB_PATH)
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        
        # Remove CREATE DATABASE, USE, and inline INDEX definitions for SQLite
        lines = []
        for line in schema_sql.splitlines():
            line_clean = line.strip()
            if line_clean.upper().startswith("CREATE DATABASE") or line_clean.upper().startswith("USE "):
                continue
            # Remove inline INDEX lines inside CREATE TABLE for SQLite
            if line_clean.upper().startswith("INDEX ") or line_clean.upper().startswith("KEY "):
                continue
            if line_clean.upper().startswith("UNIQUE KEY"):
                # Convert 'UNIQUE KEY uq_name (col1, col2)' -> 'UNIQUE (col1, col2)'
                import re
                line = re.sub(r'UNIQUE\s+KEY\s+\w+\s*(\([^)]+\))', r'UNIQUE \1', line, flags=re.IGNORECASE)
            lines.append(line)
        cleaned_sql = "\n".join(lines)
        
        # Clean trailing commas before closing parenthesis
        import re
        cleaned_sql = re.sub(r',\s*\n\s*\)', '\n)', cleaned_sql)
        
        # Replace MySQL specific types for SQLite
        cleaned_sql = cleaned_sql.replace("AUTO_INCREMENT", "AUTOINCREMENT")
        cleaned_sql = cleaned_sql.replace("MEDIUMTEXT", "TEXT")
        cleaned_sql = cleaned_sql.replace("DECIMAL(5,2)", "REAL")
        cleaned_sql = cleaned_sql.replace("DECIMAL(8,6)", "REAL")
        cleaned_sql = cleaned_sql.replace("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", "CURRENT_TIMESTAMP")
        cleaned_sql = re.sub(r'ENGINE=InnoDB[^;]*', '', cleaned_sql)
        cleaned_sql = re.sub(r'COLLATE\s+\w+', '', cleaned_sql)
        cleaned_sql = re.sub(r'CHARACTER\s+SET\s+\w+', '', cleaned_sql)
        
        # Replace ENUM(...) with VARCHAR(50)
        cleaned_sql = re.sub(r'ENUM\([^)]+\)', 'VARCHAR(50)', cleaned_sql, flags=re.IGNORECASE)
        # Convert INT PRIMARY KEY AUTOINCREMENT
        cleaned_sql = re.sub(r'INT\s+AUTOINCREMENT\s+PRIMARY\s+KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT', cleaned_sql, flags=re.IGNORECASE)
        cleaned_sql = re.sub(r'INT\s+PRIMARY\s+KEY\s+AUTOINCREMENT', 'INTEGER PRIMARY KEY AUTOINCREMENT', cleaned_sql, flags=re.IGNORECASE)
        
        statements = cleaned_sql.split(";")
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                try:
                    conn.execute(stmt)
                except Exception as e:
                    logger.warning(f"SQLite init notice on stmt: {stmt[:60]}... -> {e}")
        conn.commit()
        conn.close()
        logger.info(f"SQLite fallback database initialized at {db_path}")
