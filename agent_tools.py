from database import db
from matching_engine import brain
from kosaf_scraper import KosafScraper
from seoul_scraper import SeoulScraper
from gwangju_scraper import GwangjuScraper
from dreamspon_scraper import DreamsponScraper
from regional_aggregator import RegionalAggregatorScraper
from document_analyzer import analyzer
from auto_applier import applier

def get_user_and_matches(user_id: str):
    user = db.get_user_profile(user_id)
    if not user: return f"User {user_id}의 프로필이 없습니다."
    return {"user_profile": user, "recommended_scholarships": brain.get_matches(user_id)}

async def refresh_scholarship_data():
    results = []
    
    # 1. Run KOSAF Scraper
    try:
        kosaf = KosafScraper()
        kosaf_results = await kosaf.fetch_scholarship_list()
        results.extend(kosaf_results)
    except Exception as e:
        print(f"Error running KosafScraper: {e}")
        
    # 2. Run Seoul Scraper
    try:
        seoul = SeoulScraper()
        seoul_results = await seoul.fetch_scholarship_list()
        results.extend(seoul_results)
    except Exception as e:
        print(f"Error running SeoulScraper: {e}")
        
    # 3. Run Gwangju Scraper (New)
    try:
        gwangju = GwangjuScraper()
        gwangju_results = await gwangju.fetch_scholarship_list()
        results.extend(gwangju_results)
    except Exception as e:
        print(f"Error running GwangjuScraper: {e}")
        
    # 4. Run Dreamspon Scraper (New)
    try:
        dreamspon = DreamsponScraper()
        dreamspon_results = await dreamspon.fetch_scholarship_list()
        results.extend(dreamspon_results)
    except Exception as e:
        print(f"Error running DreamsponScraper: {e}")
        
    # 5. Run Regional Aggregator Scraper (New - 17 Provinces)
    try:
        regional = RegionalAggregatorScraper()
        regional_results = await regional.fetch_scholarship_list()
        results.extend(regional_results)
    except Exception as e:
        print(f"Error running RegionalAggregatorScraper: {e}")
        
    db.save_scholarships(results)
    return f"{len(results)}건의 신규 공고가 업데이트되었습니다."

async def extract_notice_full_text(scholarship_id: int):
    # Retrieve scholarship by id
    cursor = db.conn.cursor()
    cursor.execute("SELECT source, title FROM scholarships WHERE id = ?", (scholarship_id,))
    row = cursor.fetchone()
    if not row:
        return f"ID {scholarship_id}에 해당하는 공고가 없습니다."
    
    source_url, title = row
    print(f"== [{title}] 공고 정밀 분석을 위한 텍스트 수집을 시작합니다... ==")
    text = await analyzer.extract_text_from_notice(source_url)
    return text

async def start_apply_session(user_id: str, scholarship_id: int):
    # Retrieve scholarship by id
    cursor = db.conn.cursor()
    cursor.execute("SELECT source, title FROM scholarships WHERE id = ?", (scholarship_id,))
    row = cursor.fetchone()
    if not row:
        return f"ID {scholarship_id}에 해당하는 공고가 없습니다."
        
    source_url, title = row
    print(f"== [{title}] 공고 자동 양식 작성 보조 세션을 가동합니다... ==")
    result = await applier.fill_application_form(user_id, source_url)
    return result
