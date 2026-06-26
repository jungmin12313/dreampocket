import os
import sys
import json
import time
from duckduckgo_search import DDGS

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

TARGET_FILE = "data/target_sites.json"

# 17 Regional Foundations (Manually verified)
REGIONAL_FOUNDATIONS = [
    {"id": "seoul_foundation", "name": "서울인재육성재단", "url": "https://www.hissf.or.kr/info/notice", "category": "지자체 장학금", "region": "서울특별시"},
    {"id": "busan_foundation", "name": "부산청년플랫폼", "url": "https://www.busan.go.kr/young", "category": "지자체 장학금", "region": "부산광역시"},
    {"id": "daegu_foundation", "name": "대구교육재단", "url": "http://www.daeguedu.or.kr", "category": "지자체 장학금", "region": "대구광역시"},
    {"id": "incheon_foundation", "name": "인천인재평생교육진흥원", "url": "https://www.itle.or.kr", "category": "지자체 장학금", "region": "인천광역시"},
    {"id": "gwangju_foundation", "name": "광주평생교육진흥원", "url": "https://www.gie.kr/portal/schship/list.fm", "category": "지자체 장학금", "region": "광주광역시"},
    {"id": "daejeon_foundation", "name": "대전청년내일재단", "url": "https://www.dhrdf.or.kr", "category": "지자체 장학금", "region": "대전광역시"},
    {"id": "ulsan_foundation", "name": "울산인재평생교육진흥원", "url": "https://uill.uri.re.kr", "category": "지자체 장학금", "region": "울산광역시"},
    {"id": "sejong_foundation", "name": "세종인재평생교육진흥원", "url": "https://www.sjhle.or.kr", "category": "지자체 장학금", "region": "세종특별자치시"},
    {"id": "gyeonggi_foundation", "name": "경기교육장학재단", "url": "https://gesf.or.kr", "category": "지자체 장학금", "region": "경기도"},
    {"id": "gangwon_foundation", "name": "강원인재평생교육진흥원", "url": "https://www.gwd.go.kr", "category": "지자체 장학금", "region": "강원특별자치도"},
    {"id": "chungbuk_foundation", "name": "충북인재평생교육진흥원", "url": "https://www.cbitle.or.kr", "category": "지자체 장학금", "region": "충청북도"},
    {"id": "chungnam_foundation", "name": "충남인재평생교육진흥원", "url": "https://www.clehrd.or.kr", "category": "지자체 장학금", "region": "충청남도"},
    {"id": "jeonbuk_foundation", "name": "전북평생교육장학진흥원", "url": "https://www.jbiles.or.kr", "category": "지자체 장학금", "region": "전북특별자치도"},
    {"id": "jeonnam_foundation", "name": "전남인재평생교육진흥원", "url": "https://www.jntle.kr", "category": "지자체 장학금", "region": "전라남도"},
    {"id": "gyeongbuk_foundation", "name": "경북인재평생교육진흥원", "url": "https://www.gtlef.or.kr", "category": "지자체 장학금", "region": "경상북도"},
    {"id": "gyeongnam_foundation", "name": "경남인재육성재단", "url": "https://www.gninjae.or.kr", "category": "지자체 장학금", "region": "경상남도"},
    {"id": "jeju_foundation", "name": "제주인재평생교육진흥원", "url": "https://www.jiles.or.kr", "category": "지자체 장학금", "region": "제주특별자치도"}
]

# Sample Top Universities for phase 1 (Will scale to 300 later)
UNIVERSITIES = [
    "서울대학교", "연세대학교", "고려대학교", "서강대학교", "성균관대학교", 
    "한양대학교", "중앙대학교", "경희대학교", "한국외국어대학교", "서울시립대학교",
    "이화여자대학교", "건국대학교", "동국대학교", "홍익대학교", "국민대학교"
]

def discover_urls():
    print(f"[*] Starting Auto-Discovery Bot for {len(UNIVERSITIES)} Universities...")
    sites = list(REGIONAL_FOUNDATIONS)
    
    with DDGS() as ddgs:
        for univ in UNIVERSITIES:
            query = f"{univ} 장학 공지사항 site:ac.kr"
            print(f"  Searching: {query}")
            try:
                # Get top 3 results
                results = list(ddgs.text(query, max_results=3))
                found_url = None
                
                for r in results:
                    url = r.get("href", "")
                    if ".ac.kr" in url and ("notice" in url.lower() or "scholar" in url.lower() or "board" in url.lower() or "janghak" in url.lower()):
                        found_url = url
                        break
                
                # Fallback to first ac.kr link if no clear keyword match
                if not found_url and results:
                    found_url = results[0].get("href", "")
                
                if found_url:
                    sites.append({
                        "id": f"univ_{univ}",
                        "name": univ,
                        "url": found_url,
                        "category": "대학 장학금",
                        "region": "전국"
                    })
                    print(f"  [+] Found: {found_url}")
                else:
                    print(f"  [-] Failed to find URL for {univ}")
                    
                time.sleep(1.5) # Anti-ban delay
            except Exception as e:
                print(f"  [!] Error searching for {univ}: {e}")
                time.sleep(2)
                
    # Save to JSON
    with open(TARGET_FILE, "w", encoding="utf-8") as f:
        json.dump(sites, f, ensure_ascii=False, indent=4)
        
    print(f"[*] Discovery Complete! Saved {len(sites)} target URLs to {TARGET_FILE}.")

if __name__ == "__main__":
    discover_urls()
