import os
import sys
import re
import argparse
import logging
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("init_db")

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
SEED_PATH = os.path.join(os.path.dirname(__file__), 'database', 'seed.sql')
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'ai_hr_recruitment.db')

def split_sql_statements(sql_text):
    """Split SQL script by semicolons while respecting single-quoted strings."""
    statements = []
    current = []
    in_quote = False
    prev_char = ''
    
    for char in sql_text:
        if char == "'" and prev_char != '\\':
            in_quote = not in_quote
        if char == ';' and not in_quote:
            stmt = "".join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []
        else:
            current.append(char)
        prev_char = char
        
    last = "".join(current).strip()
    if last:
        statements.append(last)
    return statements

def init_mysql(host, port, user, password, db_name):
    """Initialize MySQL database using schema.sql and seed.sql."""
    import mysql.connector
    logger.info(f"Connecting to MySQL server at {host}:{port} with user '{user}'...")
    
    # 1. Connect without database to create DB if needed
    conn = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"Database `{db_name}` verified/created.")

    # 2. Connect to the specific database
    conn = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db_name
    )
    cursor = conn.cursor()

    # 3. Execute schema.sql
    logger.info("Applying schema definitions...")
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    clean_schema = "\n".join([line for line in schema_sql.splitlines() if not line.strip().startswith('--')])
    statements = split_sql_statements(clean_schema)
    for stmt in statements:
        if stmt.upper().startswith('USE ') or stmt.upper().startswith('CREATE DATABASE'):
            continue
        try:
            cursor.execute(stmt)
        except Exception as e:
            logger.warning(f"Schema statement warning: {e}")
    conn.commit()
    logger.info("Schema applied successfully.")

    # 4. Execute seed.sql
    logger.info("Seeding initial dataset...")
    with open(SEED_PATH, 'r', encoding='utf-8') as f:
        seed_sql = f.read()

    clean_seed = "\n".join([line for line in seed_sql.splitlines() if not line.strip().startswith('--')])
    seed_statements = split_sql_statements(clean_seed)
    for stmt in seed_statements:
        if stmt.upper().startswith('USE '):
            continue
        try:
            cursor.execute(stmt)
        except Exception as e:
            logger.warning(f"Seed statement warning: {e}")
    conn.commit()

    cursor.close()
    conn.close()
    logger.info(f"MySQL database '{db_name}' initialized and seeded successfully!")

def init_sqlite():
    """Initialize local SQLite database as an immediate working store."""
    import sqlite3
    logger.info(f"Setting up resilient local database store at {SQLITE_DB_PATH}...")
    os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()

    # SQLite Schema
    tables = [
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'HR Manager',
            company TEXT DEFAULT 'Acme Corporation',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        """CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            department TEXT NOT NULL,
            location TEXT NOT NULL,
            employment_type TEXT DEFAULT 'Full Time',
            experience_required TEXT NOT NULL,
            min_salary REAL,
            max_salary REAL,
            description TEXT NOT NULL,
            education_requirements TEXT,
            responsibilities TEXT,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );""",
        """CREATE TABLE IF NOT EXISTS job_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            is_required BOOLEAN DEFAULT 1,
            category TEXT DEFAULT 'General',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
        );""",
        """CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            location TEXT,
            current_title TEXT,
            years_experience REAL DEFAULT 0.0,
            recruitment_status TEXT DEFAULT 'New',
            ai_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        """CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER DEFAULT 0,
            file_type TEXT NOT NULL,
            extracted_text TEXT,
            raw_json TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
        );""",
        """CREATE TABLE IF NOT EXISTS candidate_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            proficiency TEXT DEFAULT 'Intermediate',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
        );""",
        """CREATE TABLE IF NOT EXISTS candidate_experience (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            is_current BOOLEAN DEFAULT 0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
        );""",
        """CREATE TABLE IF NOT EXISTS candidate_education (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            degree TEXT NOT NULL,
            institution TEXT NOT NULL,
            field_of_study TEXT,
            graduation_year TEXT,
            grade TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
        );""",
        """CREATE TABLE IF NOT EXISTS candidate_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            project_title TEXT NOT NULL,
            description TEXT,
            technologies_used TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
        );""",
        """CREATE TABLE IF NOT EXISTS candidate_certifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            issuing_organization TEXT,
            issue_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
        );""",
        """CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Applied',
            notes TEXT,
            UNIQUE(job_id, candidate_id),
            FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
        );""",
        """CREATE TABLE IF NOT EXISTS candidate_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            overall_score REAL DEFAULT 0.0,
            skills_score REAL DEFAULT 0.0,
            experience_score REAL DEFAULT 0.0,
            education_score REAL DEFAULT 0.0,
            project_score REAL DEFAULT 0.0,
            preferred_skills_score REAL DEFAULT 0.0,
            matched_skills TEXT,
            missing_skills TEXT,
            partial_skills TEXT,
            strengths TEXT,
            weaknesses TEXT,
            ai_explanation TEXT,
            recommendation TEXT DEFAULT 'Needs Review',
            computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(job_id, candidate_id),
            FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
        );""",
        """CREATE TABLE IF NOT EXISTS interview_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            difficulty TEXT DEFAULT 'Medium',
            question_text TEXT NOT NULL,
            expected_skills TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
        );""",
        """CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            scheduled_date TEXT NOT NULL,
            scheduled_time TEXT NOT NULL,
            interview_type TEXT DEFAULT 'Technical',
            interviewer_name TEXT NOT NULL,
            status TEXT DEFAULT 'Scheduled',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
            FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
        );""",
        """CREATE TABLE IF NOT EXISTS interview_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL UNIQUE,
            candidate_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            technical_score INTEGER DEFAULT 3,
            communication_score INTEGER DEFAULT 3,
            problem_solving_score INTEGER DEFAULT 3,
            project_knowledge_score INTEGER DEFAULT 3,
            role_fit_score INTEGER DEFAULT 3,
            confidence_score INTEGER DEFAULT 3,
            overall_score REAL DEFAULT 60.0,
            strengths TEXT,
            weaknesses TEXT,
            notes TEXT,
            final_recommendation TEXT DEFAULT 'Consider',
            evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
            FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
        );"""
    ]

    for tbl_sql in tables:
        cursor.execute(tbl_sql)

    # SQLite Seed conversion
    with open(SEED_PATH, 'r', encoding='utf-8') as f:
        seed_content = f.read()

    clean_seed = "\n".join([line for line in seed_content.splitlines() if not line.strip().startswith('--')])
    statements = split_sql_statements(clean_seed)
    for stmt in statements:
        if stmt.upper().startswith('USE '):
            continue
        # Replace MySQL specific syntax for SQLite
        sqlite_stmt = re.sub(r'ON DUPLICATE KEY UPDATE.*$', '', stmt, flags=re.DOTALL)
        sqlite_stmt = sqlite_stmt.replace('TRUE', '1').replace('FALSE', '0')
        sqlite_stmt = sqlite_stmt.replace('INSERT INTO', 'INSERT OR REPLACE INTO')
        try:
            cursor.execute(sqlite_stmt)
        except Exception as e:
            logger.warning(f"SQLite seed statement warning: {e}")

    conn.commit()
    conn.close()
    logger.info("Local database store initialized and seeded with all demo data.")

def main():
    parser = argparse.ArgumentParser(description="Initialize AI HR Recruitment Database")
    parser.add_argument("--host", default=Config.DB_HOST, help="MySQL Host")
    parser.add_argument("--port", type=int, default=Config.DB_PORT, help="MySQL Port")
    parser.add_argument("--user", default=Config.DB_USER, help="MySQL User")
    parser.add_argument("--password", default=Config.DB_PASSWORD, help="MySQL Password")
    parser.add_argument("--database", default=Config.DB_NAME, help="MySQL Database Name")
    parser.add_argument("--sqlite-only", action="store_true", help="Force SQLite setup only")
    args = parser.parse_args()

    print("\n" + "="*60)
    print("  AI HR RECRUITMENT ASSISTANT - DATABASE INITIALIZER")
    print("="*60 + "\n")

    mysql_success = False
    if not args.sqlite_only:
        try:
            init_mysql(args.host, args.port, args.user, args.password, args.database)
            mysql_success = True
        except Exception as e:
            logger.warning(f"Could not initialize MySQL: {e}")
            logger.info("Falling back to initializing local database store so you can test immediately...")

    # Always ensure local DB is also initialized as fallback backup
    init_sqlite()

    print("\n" + "="*60)
    print("  DATABASE INITIALIZATION COMPLETE!")
    print("="*60)
    if mysql_success:
        print(f"  Status: Active on MySQL database '{args.database}' at {args.host}:{args.port}")
    else:
        print(f"  Status: Active on resilient local database store (fallback)")
        print(f"  Tip: To switch to MySQL, update DB_PASSWORD in .env and rerun:")
        print(f"       python init_db.py --password YOUR_MYSQL_PASSWORD")
    print("\n  Default Demo Logins:")
    print("  1. Admin:     admin@recruitment.ai         | Password: Admin@123")
    print("  2. Recruiter: sarah.recruiter@recruitment.ai | Password: Recruiter@123")
    print("  3. Partner:   michael.hr@recruitment.ai      | Password: Recruiter@123")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
