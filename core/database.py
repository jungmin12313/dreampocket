import sqlite3
from datetime import datetime
import os
import re

class ScholarshipDB:
    def __init__(self, db_name="data/antigravity_bot.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def normalize_title(self, title):
        if not title: return ""
        # 1. Remove brackets and contents like [기관명], (2026), <공지>
        title = re.sub(r'\[.*?\]|\(.*?\)|\<.*?\>', '', title)
        # 2. Remove common words that vary
        words_to_remove = ['2026', '2026년', '상반기', '하반기', '신청', '가능', '선발', '안내', '공고', '제\d+기']
        for word in words_to_remove:
            title = re.sub(r'\b' + word + r'\b', '', title)
        # 3. Remove all non-alphanumeric characters and whitespaces
        title = re.sub(r'[^가-힣a-zA-Z0-9]', '', title)
        return title

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                gpa TEXT,
                income TEXT,
                location TEXT,
                major TEXT,
                subscribed INTEGER DEFAULT 1,
                updated_at TIMESTAMP
            )
        ''')
        # Migrate existing users table to add subscribed column
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN subscribed INTEGER DEFAULT 1')
        except sqlite3.OperationalError:
            pass # Column already exists
            
        cursor.execute('''
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
                UNIQUE(title, period)
            )
        ''')
        
        # Add new columns if they don't exist (Migration)
        new_columns = [
            ('gpa_limit', 'REAL'),
            ('income_limit', 'INTEGER'),
            ('is_verified', 'INTEGER DEFAULT 0'),
            ('analysis_status', "TEXT DEFAULT '제목 분석'"),
            ('last_health_check', 'TIMESTAMP'),
            ('major_restriction', 'TEXT'),
            ('region_restriction', 'TEXT'),
            ('benefit_type', 'TEXT'),
            ('benefit_amount', 'TEXT'),
            ('application_link', 'TEXT'),
            ('is_closed', 'INTEGER DEFAULT 0')
        ]
        for col_name, col_type in new_columns:
            try:
                cursor.execute(f'ALTER TABLE scholarships ADD COLUMN {col_name} {col_type}')
            except sqlite3.OperationalError:
                pass # Column already exists

        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notified_scholarships (
                user_id TEXT,
                scholarship_id INTEGER,
                notified_at TIMESTAMP,
                PRIMARY KEY(user_id, scholarship_id)
            )
        ''')
        self.conn.commit()

    def save_user_profile(self, user_id, profile_data):
        cursor = self.conn.cursor()
        # Preserve existing subscribed status if user already exists
        cursor.execute('SELECT subscribed FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        subscribed = row[0] if row else 1
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, gpa, income, location, major, subscribed, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, profile_data['gpa'], profile_data['income'], 
              profile_data['location'], profile_data['major'], subscribed, datetime.now()))
        self.conn.commit()

    def save_scholarships(self, scholarship_list):
        cursor = self.conn.cursor()
        for item in scholarship_list:
            try:
                # To prevent duplicates, we first check if the source URL already exists.
                # If source is the same, it's definitely the same scholarship (unless it's a generic notice board URL).
                is_generic_url = item.get('source', '').endswith(('/notice', '/list.html', '/notice.do')) or '?' not in item.get('source', '')
                
                existing = None
                if not is_generic_url:
                    cursor.execute('SELECT id FROM scholarships WHERE source = ?', (item.get('source'),))
                    existing = cursor.fetchone()
                
                # Intelligent Title Deduplication
                if not existing:
                    new_norm = self.normalize_title(item.get('title', ''))
                    
                    # Fetch all existing titles to find a fuzzy match
                    # (In a huge DB this might be slow, but for a few hundred it's instant)
                    cursor.execute('SELECT id, title FROM scholarships')
                    for row in cursor.fetchall():
                        db_id, db_title = row
                        if self.normalize_title(db_title) == new_norm:
                            existing = (db_id,)
                            break
                
                if existing:
                    # Update existing record with the new period and other details
                    cursor.execute('''
                        UPDATE scholarships SET
                            category = ?, period = ?, status = ?, source = ?, collected_at = ?,
                            last_health_check = ?, is_closed = 0
                        WHERE id = ?
                    ''', (
                        item.get('category'), item.get('period'), item.get('status'),
                        item.get('source'), item.get('collected_at'), datetime.now(),
                        existing[0]
                    ))
                else:
                    cursor.execute('''
                        INSERT INTO scholarships (
                            category, title, period, status, source, collected_at,
                            gpa_limit, income_limit, is_verified, analysis_status, last_health_check,
                            major_restriction, region_restriction, benefit_type, benefit_amount, 
                            application_link, is_closed
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item.get('category'), item.get('title'), item.get('period'), 
                        item.get('status'), item.get('source'), item.get('collected_at'),
                        item.get('gpa_limit'), item.get('income_limit'), 
                        item.get('is_verified', 0), item.get('analysis_status', '제목 분석'),
                        item.get('last_health_check', datetime.now()),
                        item.get('major_restriction'), item.get('region_restriction'),
                        item.get('benefit_type'), item.get('benefit_amount'),
                        item.get('application_link'), item.get('is_closed', 0)
                    ))
            except Exception as e:
                print(f"Error saving scholarship: {e}")
        self.conn.commit()

    def set_subscription(self, user_id, status):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE users SET subscribed = ? WHERE user_id = ?
        ''', (1 if status else 0, user_id))
        self.conn.commit()

    def get_user_profile(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT user_id, gpa, income, location, major, subscribed FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
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
        cursor = self.conn.cursor()
        cursor.execute('SELECT user_id, gpa, income, location, major, subscribed FROM users WHERE subscribed = 1')
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def update_enriched_scholarship(self, scholarship_id, data):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE scholarships 
            SET gpa_limit = ?, 
                income_limit = ?, 
                major_restriction = ?, 
                region_restriction = ?, 
                benefit_type = ?, 
                benefit_amount = ?, 
                application_link = ?, 
                is_closed = ?,
                analysis_status = ?,
                is_verified = ?,
                last_health_check = ?
            WHERE id = ?
        ''', (
            data.get('gpa_limit'),
            data.get('income_limit'),
            data.get('major_restriction'),
            data.get('region_restriction'),
            data.get('benefit_type'),
            data.get('benefit_amount'),
            data.get('application_link'),
            1 if data.get('is_closed') else 0,
            'AI 정밀 분석',
            1,
            datetime.now().isoformat(),
            scholarship_id
        ))
        self.conn.commit()

    def update_scholarship_status(self, scholarship_id, status):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE scholarships 
            SET status = ?, last_health_check = ? 
            WHERE id = ?
        ''', (status, datetime.now().isoformat(), scholarship_id))
        self.conn.commit()

    def get_all_scholarships(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM scholarships ORDER BY collected_at DESC')
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def is_scholarship_notified(self, user_id, scholarship_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1 FROM notified_scholarships WHERE user_id = ? AND scholarship_id = ?', (user_id, scholarship_id))
        return cursor.fetchone() is not None

    def mark_scholarship_notified(self, user_id, scholarship_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO notified_scholarships (user_id, scholarship_id, notified_at)
                VALUES (?, ?, ?)
            ''', (user_id, scholarship_id, datetime.now()))
            self.conn.commit()
        except Exception as e:
            print(f"Error marking notification: {e}")

db = ScholarshipDB()

