import sqlite3
from datetime import datetime

class ScholarshipDB:
    def __init__(self, db_name="antigravity_bot.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

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
                UNIQUE(title, period)
            )
        ''')
        
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
                cursor.execute('''
                    INSERT OR IGNORE INTO scholarships (category, title, period, status, source, collected_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (item['category'], item['title'], item['period'], 
                      item['status'], item['source'], item['collected_at']))
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

