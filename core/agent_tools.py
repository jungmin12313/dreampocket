from core.database import db
from core.matching_engine import brain
from scrapers.kosaf_scraper import KosafScraper
from scrapers.seoul_scraper import SeoulScraper
from scrapers.gwangju_scraper import GwangjuScraper
from scrapers.regional_aggregator import RegionalAggregatorScraper
from scrapers.campuspick_scraper import CampusPickScraper
from scrapers.universal_scraper import UniversalScraper
from scrapers.mega_scraper import MegaScraper
from core.document_analyzer import analyzer
from core.auto_applier import applier
from core.link_validator import validator
import asyncio

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
        
        
    # 4. Run Regional Aggregator Scraper (New - 17 Provinces)
    # [FIX] 대표님 실용주의 지침에 따라 가짜 더미 데이터 수집기 가동 중지. 
    # 향후 실제 사이트 300개 리스트업 기반 스크래퍼로 대체 예정.
    try:
        regional = RegionalAggregatorScraper()
        regional_results = await regional.fetch_scholarship_list()
        results.extend(regional_results)
    except Exception as e:
        print(f"Error running RegionalAggregatorScraper: {e}")
        
    # 5. Run Universal Scraper (Auto-Discovery based 300+ sites)
    try:
        univ_scraper = UniversalScraper()
        univ_results = await univ_scraper.fetch_scholarship_list()
        results.extend(univ_results)
    except Exception as e:
        print(f"Error running UniversalScraper: {e}")
        
    # 6. Run CampusPick Scraper (New)
    try:
        campuspick = CampusPickScraper()
        campuspick_results = await campuspick.fetch_scholarship_list()
        results.extend(campuspick_results)
    except Exception as e:
        print(f"Error running CampusPickScraper: {e}")
        
    # 7. Run Mega Scraper (AI Bypass Hardcoded Megas)
    try:
        mega = MegaScraper()
        mega_results = await mega.scrape()
        results.extend(mega_results)
    except Exception as e:
        print(f"Error running MegaScraper: {e}")
        
    # Apply loan keywords filter at collection time
    LOAN_KEYWORDS = ['대출', '학자금대출', '생활비대출', '융자', '이자', '저금리', '금리', '상환', '보증', '담보']
    for item in results:
        title = item.get('title', '')
        if any(kw in title for kw in LOAN_KEYWORDS):
            item['is_loan'] = 1
        else:
            item['is_loan'] = 0
            
    db.save_scholarships(results)
    
    # 5.5. Link Validation for all active scholarships
    try:
        print("[Auto-Refresh] Starting link validation for active scholarships...")
        all_schs = db.get_all_scholarships()
        active_schs = [s for s in all_schs if s.get('status') not in ['마감', '만료', '비활성'] and not s.get('is_closed')]
        
        if active_schs:
            tasks = [validator.is_link_valid(s['source']) for s in active_schs]
            validity_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            cursor = db.conn.cursor()
            invalid_count = 0
            for i, s in enumerate(active_schs):
                is_valid = validity_results[i]
                if isinstance(is_valid, Exception) or not is_valid:
                    cursor.execute("UPDATE scholarships SET status = '마감', is_closed = 1 WHERE id = ?", (s['id'],))
                    invalid_count += 1
            db.conn.commit()
            print(f"[Auto-Refresh] Link validation complete. Marked {invalid_count} scholarships as dead/closed.")
    except Exception as e:
        print(f"Error during link validation: {e}")
    
    
    # 6. Run AI Enrichment for newly collected data
    try:
        from scripts.ai_enrichment import enrich_scholarships
        # Process up to 30 items to stay within reasonable limits during auto-refresh
        await enrich_scholarships(limit=30)
    except Exception as e:
        print(f"Error during auto-enrichment: {e}")
        
    return f"{len(results)}건의 신규 공고가 업데이트 및 AI 정밀 분석되었습니다."

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
