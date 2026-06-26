import os
import sys
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database import db

def migrate():
    print("Starting DB migration to structured schema...")
    cursor = db.conn.cursor()
    
    cursor.execute("SELECT id, title, gpa_limit, income_limit, region_restriction, major_restriction FROM scholarships")
    rows = cursor.fetchall()
    
    updated = 0
    for row in rows:
        sch_id = row[0]
        title = row[1]
        gpa_old = row[2]
        income_old = row[3]
        region_old = row[4]
        major_old = row[5]
        
        gpa_min = gpa_old if gpa_old is not None else 0.0
        income_max = income_old if income_old is not None else 10
        
        region_rule = 'nationwide'
        region_target = None
        if region_old:
            region_rule = 'local'
            region_target = region_old
            
        major_rule = 'any'
        major_target = None
        if major_old:
            major_rule = 'specific'
            major_target = major_old
            
        cursor.execute('''
            UPDATE scholarships 
            SET gpa_min = ?, income_max = ?, region_rule = ?, region_target = ?, major_rule = ?, major_target = ?
            WHERE id = ?
        ''', (gpa_min, income_max, region_rule, region_target, major_rule, major_target, sch_id))
        updated += 1
        
    db.conn.commit()
    print(f"Migration completed. {updated} rows updated.")

if __name__ == "__main__":
    migrate()
