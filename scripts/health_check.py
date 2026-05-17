import sys
import os
import requests
from datetime import datetime

# Add root directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import db

def run_health_check():
    print(f"[{datetime.now()}] Starting Scholarship Health Check...")
    scholarships = db.get_all_scholarships()
    
    updated_count = 0
    dead_links = 0
    
    for sch in scholarships:
        if sch.get("status") in ["마감", "비활성"]:
            continue
            
        url = sch.get("source")
        if not url: continue
        
        try:
            # Check only headers first for efficiency
            response = requests.head(url, timeout=10, allow_redirects=True)
            
            # If head fails or 404, try a full GET
            if response.status_code >= 400:
                response = requests.get(url, timeout=10)
            
            status = "진행중"
            # Keyword detection for closing
            if response.status_code == 200:
                content = response.text
                closing_keywords = ["마감되었습니다", "종료되었습니다", "존재하지 않는 페이지", "올해 사업 종료"]
                if any(kw in content for kw in closing_keywords):
                    status = "마감"
                    updated_count += 1
            else:
                status = "비활성" # Broken link
                dead_links += 1
                
            # Update DB with check time and new status
            db.update_scholarship_status(sch["id"], status)
            
        except Exception as e:
            print(f"Error checking {url}: {e}")
            db.update_scholarship_status(sch["id"], "비활성")
            dead_links += 1

    print(f"Health Check Completed: {updated_count} closed, {dead_links} dead links found.")

if __name__ == "__main__":
    run_health_check()
