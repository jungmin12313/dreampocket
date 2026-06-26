import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import db

def clean_database():
    print("[DB Clean] Starting Database Cleanup...")
    
    # 1. Remove Dreamspon
    rows = db.execute_query("SELECT count(*) as cnt FROM scholarships WHERE source LIKE '%dreamspon%'", fetchone=True)
    cnt = rows[0] if isinstance(rows, tuple) else rows['cnt']
    print(f"[DB Clean] Found {cnt} Dreamspon scholarships to delete.")
    
    db.execute_query("DELETE FROM scholarships WHERE source LIKE '%dreamspon%'", commit=True)
    
    # 1.5. Remove 15 Mock Regional Data (더미 데이터 삭제)
    mock_keywords = [
        '[부산인재]', '[대구재단]', '[인천재단]', '[대전청년]', '[울산재단]', 
        '[세종인재]', '[경기교육장학재단]', '[강원인재]', '[충북인재]', 
        '[충남진흥]', '[전북장학진흥]', '[전북인재]', '[전남진흥]', '[경북재단]', 
        '[경남재단]', '[제주진흥]'
    ]
    for kw in mock_keywords:
        db.execute_query("DELETE FROM scholarships WHERE title LIKE ?", (f'%{kw}%',), commit=True)
    
    print("[DB Clean] Removed mock regional scholarships.")
    
    # 2. Remove Duplicates by title
    all_schs = db.execute_query("SELECT id, title, collected_at FROM scholarships", fetchall=True)
    
    title_map = {}
    for sch in all_schs:
        s_id = sch['id'] if isinstance(sch, dict) else sch[0]
        s_title = sch['title'] if isinstance(sch, dict) else sch[1]
        s_date = sch['collected_at'] if isinstance(sch, dict) else sch[2]
        
        norm_t = db.normalize_title(s_title)
        if norm_t not in title_map:
            title_map[norm_t] = []
        title_map[norm_t].append({"id": s_id, "date": s_date})
    
    to_delete = []
    for norm_t, items in title_map.items():
        if len(items) > 1:
            # Sort by date descending
            items.sort(key=lambda x: x['date'], reverse=True)
            # Keep the first (latest), mark others for deletion
            for old_item in items[1:]:
                to_delete.append(old_item['id'])
                
    if to_delete:
        print(f"[DB Clean] Found {len(to_delete)} duplicate scholarships. Deleting...")
        for id_val in to_delete:
            db.execute_query("DELETE FROM scholarships WHERE id = ?", (id_val,), commit=True)
            
    print("[DB Clean] Cleanup Complete!")

if __name__ == "__main__":
    clean_database()
