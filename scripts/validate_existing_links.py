import sys
import os
import asyncio

# Ensure project root is in PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import db
from core.link_validator import validator

async def main():
    print("Starting bulk link validation...")
    
    # Get all active scholarships
    scholarships = db.get_all_scholarships()
    active_scholarships = [s for s in scholarships if s.get('status') not in ['마감', '만료', '비활성'] and not s.get('is_closed')]
    
    print(f"Found {len(active_scholarships)} active scholarships to validate.")
    
    if not active_scholarships:
        print("No active scholarships to check.")
        return

    # Check them concurrently
    tasks = []
    for s in active_scholarships:
        tasks.append(validator.is_link_valid(s['source']))
        
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    cursor = db.conn.cursor()
    invalid_count = 0
    
    for i, s in enumerate(active_scholarships):
        is_valid = results[i]
        
        # If it raised an exception or returned False, it's invalid
        if isinstance(is_valid, Exception) or not is_valid:
            print(f"[DEAD LINK] {s['title']} -> {s['source']}")
            
            # Update DB to mark it as closed/dead
            cursor.execute('''
                UPDATE scholarships 
                SET status = '마감', is_closed = 1
                WHERE id = ?
            ''', (s['id'],))
            invalid_count += 1
            
    db.conn.commit()
    print(f"Validation complete. Marked {invalid_count} scholarships as dead/closed.")

if __name__ == "__main__":
    asyncio.run(main())
