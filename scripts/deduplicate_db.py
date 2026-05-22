import sqlite3
import re
import sys
import os

# Add project root to sys.path to import Database
sys.path.insert(0, 'd:/bot')
from core.database import db

def deduplicate():
    db_path = "d:/bot/data/antigravity_bot.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT id, title, source, period FROM scholarships ORDER BY id ASC')
    rows = cursor.fetchall()

    seen_norms = {}
    duplicates_to_delete = []

    for row in rows:
        sch_id, title, source, period = row
        norm_title = db.normalize_title(title)
        
        if norm_title in seen_norms:
            duplicates_to_delete.append(sch_id)
            print(f"Duplicate found: '{title}' (Matches: '{seen_norms[norm_title]['title']}')")
        else:
            seen_norms[norm_title] = {
                'id': sch_id,
                'title': title
            }

    # Delete duplicates
    for del_id in duplicates_to_delete:
        cursor.execute('DELETE FROM scholarships WHERE id = ?', (del_id,))
    
    conn.commit()
    conn.close()

    print(f"\nDeduplication Complete. {len(duplicates_to_delete)} duplicate records removed.")

if __name__ == "__main__":
    deduplicate()
