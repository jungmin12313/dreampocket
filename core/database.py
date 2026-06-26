import sqlite3
import os
import re
from datetime import datetime

try:
    import psycopg2
    from psycopg2 import pool
except ImportError:
    psycopg2 = None

class ScholarshipDB:
    def __init__(self, db_name="data/antigravity_bot.db"):
        self.db_url = os.environ.get("DATABASE_URL")
        self.is_postgres = bool(self.db_url)
        
        if self.is_postgres:
            if not psycopg2:
                raise ImportError("psycopg2 is required for PostgreSQL. Please install psycopg2-binary.")
            print("[DB] Initializing PostgreSQL Connection Pool...")
            self.pool = psycopg2.pool.SimpleConnectionPool(1, 20, self.db_url)
        else:
            print("[DB] Initializing SQLite Connection...")
            self.db_name = db_name
            self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
            
        self.create_tables()

    def get_connection(self):
        if self.is_postgres:
            return self.pool.getconn()
        return self.conn

    def release_connection(self, conn):
        if self.is_postgres:
            self.pool.putconn(conn)

    def execute_query(self, query, params=None, fetchone=False, fetchall=False, commit=False):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if self.is_postgres:
                # 1. Parameter Substitution
                query = query.replace('?', '%s')
                
                # 2. Syntax Translation for Postgres
                query = query.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
                
                # Handle SQLite UPSERT syntaxes
                if 'INSERT OR REPLACE INTO users' in query:
                    query = query.replace('INSERT OR REPLACE INTO users', 'INSERT INTO users')
                    query += " ON CONFLICT (user_id) DO UPDATE SET gpa=EXCLUDED.gpa, income=EXCLUDED.income, location=EXCLUDED.location, major=EXCLUDED.major, subscribed=EXCLUDED.subscribed, updated_at=EXCLUDED.updated_at"
                
                if 'INSERT OR IGNORE INTO notified_scholarships' in query:
                    query = query.replace('INSERT OR IGNORE INTO notified_scholarships', 'INSERT INTO notified_scholarships')
                    query += " ON CONFLICT DO NOTHING"

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            if commit:
                conn.commit()
                
            if fetchone:
                return cursor.fetchone()
            if fetchall:
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()
            self.release_connection(conn)

    def normalize_title(self, title):
        if not title: return ""
        title = re.sub(r'\[.*?\]|\(.*?\)|\<.*?\>', '', title)
        words_to_remove = ['2026', '2026년', '상반기', '하반기', '신청', '가능', '선발', '안내', '공고', '제\d+기']
        for word in words_to_remove:
            title = re.sub(r'\b' + word + r'\b', '', title)
        title = re.sub(r'[^가-힣a-zA-Z0-9]', '', title)
        return title

    def create_tables(self):
        self.execute_query('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                gpa TEXT,
                income TEXT,
                location TEXT,
                major TEXT,
                subscribed INTEGER DEFAULT 1,
                updated_at TIMESTAMP
            )
        ''', commit=True)
        
        try:
            self.execute_query('ALTER TABLE users ADD COLUMN subscribed INTEGER DEFAULT 1', commit=True)
        except Exception:
            pass # Column exists
            
        self.execute_query('''
            CREATE TABLE IF NOT EXISTS scholarships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                title TEXT,
                period TEXT,
                status TEXT,
                source TEXT,
                collected_at TIMESTAMP,
                gpa_limit REAL,
                income_limit INTEGER,
                is_verified INTEGER DEFAULT 0,
                analysis_status TEXT DEFAULT '제목 분석',
                last_health_check TIMESTAMP,
                major_restriction TEXT,
                region_restriction TEXT,
                benefit_type TEXT,
                benefit_amount TEXT,
                application_link TEXT,
                is_closed INTEGER DEFAULT 0,
                region_rule TEXT DEFAULT 'nationwide',
                region_target TEXT,
                major_rule TEXT DEFAULT 'any',
                major_target TEXT,
                gpa_min REAL DEFAULT 0.0,
                income_max INTEGER DEFAULT 10,
                is_loan INTEGER DEFAULT 0,
                ai_summary TEXT,
                UNIQUE(title, period)
            )
        ''', commit=True)
        
        self.execute_query('''
            CREATE TABLE IF NOT EXISTS notified_scholarships (
                user_id TEXT,
                scholarship_id INTEGER,
                notified_at TIMESTAMP,
                PRIMARY KEY(user_id, scholarship_id)
            )
        ''', commit=True)

    def save_user_profile(self, user_id, profile_data):
        row = self.execute_query('SELECT subscribed FROM users WHERE user_id = ?', (user_id,), fetchone=True)
        subscribed = row[0] if row else 1
        
        self.execute_query('''
            INSERT OR REPLACE INTO users (user_id, gpa, income, location, major, subscribed, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, profile_data['gpa'], profile_data['income'], 
              profile_data['location'], profile_data['major'], subscribed, datetime.now()), commit=True)

    def save_scholarships(self, scholarship_list):
        for item in scholarship_list:
            try:
                is_generic_url = item.get('source', '').endswith(('/notice', '/list.html', '/notice.do')) or '?' not in item.get('source', '')
                
                existing = None
                if not is_generic_url:
                    existing = self.execute_query('SELECT id FROM scholarships WHERE source = ?', (item.get('source'),), fetchone=True)
                
                if not existing:
                    new_norm = self.normalize_title(item.get('title', ''))
                    rows = self.execute_query('SELECT id, title FROM scholarships', fetchall=True)
                    for row in rows:
                        if self.normalize_title(row['title']) == new_norm:
                            existing = (row['id'],)
                            break
                
                if existing:
                    scholarship_id = existing[0] if isinstance(existing, tuple) else existing['id']
                    self.execute_query('''
                        UPDATE scholarships SET
                            category = ?, period = ?, status = ?, source = ?, collected_at = ?,
                            last_health_check = ?, is_closed = 0, is_loan = ?
                        WHERE id = ?
                    ''', (
                        item.get('category'), item.get('period'), item.get('status'),
                        item.get('source'), item.get('collected_at'), datetime.now(),
                        item.get('is_loan', 0), scholarship_id
                    ), commit=True)
                else:
                    self.execute_query('''
                        INSERT INTO scholarships (
                            category, title, period, status, source, collected_at,
                            gpa_limit, income_limit, is_verified, analysis_status, last_health_check,
                            major_restriction, region_restriction, benefit_type, benefit_amount, 
                            application_link, is_closed, is_loan
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item.get('category'), item.get('title'), item.get('period'), 
                        item.get('status'), item.get('source'), item.get('collected_at'),
                        item.get('gpa_limit'), item.get('income_limit'), 
                        item.get('is_verified', 0), item.get('analysis_status', '제목 분석'),
                        item.get('last_health_check', datetime.now()),
                        item.get('major_restriction'), item.get('region_restriction'),
                        item.get('benefit_type'), item.get('benefit_amount'),
                        item.get('application_link'), item.get('is_closed', 0),
                        item.get('is_loan', 0)
                    ), commit=True)
            except Exception as e:
                print(f"Error saving scholarship: {e}")

    def set_subscription(self, user_id, status):
        self.execute_query('''
            UPDATE users SET subscribed = ? WHERE user_id = ?
        ''', (1 if status else 0, user_id), commit=True)

    def get_user_profile(self, user_id):
        row = self.execute_query('SELECT user_id, gpa, income, location, major, subscribed FROM users WHERE user_id = ?', (user_id,), fetchone=True)
        if row:
            return {
                "user_id": row[0], 
                "gpa": row[1], 
                "income": row[2], 
                "location": row[3], 
                "major": row[4],
                "subscribed": row[5]
            }
        return None

    def get_subscribed_users(self):
        return self.execute_query('SELECT user_id, gpa, income, location, major, subscribed FROM users WHERE subscribed = 1', fetchall=True)

    def update_enriched_scholarship(self, scholarship_id, data):
        self.execute_query('''
            UPDATE scholarships 
            SET gpa_min = ?, 
                income_max = ?, 
                major_rule = ?, 
                major_target = ?, 
                region_rule = ?, 
                region_target = ?, 
                ai_summary = ?, 
                is_closed = ?,
                analysis_status = ?,
                is_verified = ?,
                last_health_check = ?
            WHERE id = ?
        ''', (
            data.get('gpa_min', 0.0),
            data.get('income_max', 10),
            data.get('major_rule', 'any'),
            data.get('major_target'),
            data.get('region_rule', 'nationwide'),
            data.get('region_target'),
            data.get('ai_summary'),
            1 if data.get('is_closed') else 0,
            'AI 정밀 분석',
            1,
            datetime.now().isoformat(),
            scholarship_id
        ), commit=True)

    def update_scholarship_status(self, scholarship_id, status):
        self.execute_query('''
            UPDATE scholarships 
            SET status = ?, last_health_check = ? 
            WHERE id = ?
        ''', (status, datetime.now().isoformat(), scholarship_id), commit=True)

    def get_all_scholarships(self):
        return self.execute_query('SELECT * FROM scholarships ORDER BY collected_at DESC', fetchall=True)

    def is_scholarship_notified(self, user_id, scholarship_id):
        row = self.execute_query('SELECT 1 FROM notified_scholarships WHERE user_id = ? AND scholarship_id = ?', (user_id, scholarship_id), fetchone=True)
        return row is not None

    def mark_scholarship_notified(self, user_id, scholarship_id):
        try:
            self.execute_query('''
                INSERT OR IGNORE INTO notified_scholarships (user_id, scholarship_id, notified_at)
                VALUES (?, ?, ?)
            ''', (user_id, scholarship_id, datetime.now()), commit=True)
        except Exception as e:
            print(f"Error marking notification: {e}")

db = ScholarshipDB()
