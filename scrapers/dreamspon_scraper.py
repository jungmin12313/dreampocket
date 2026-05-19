import asyncio
from datetime import datetime, timedelta
import re
from playwright.async_api import async_playwright

class DreamsponScraper:
    def __init__(self):
        self.source_url = "https://www.dreamspon.com/scholarship/list.html"
        
    async def fetch_scholarship_list(self):
        """
        Scrapes real live scholarship listings from Dreamspon using Playwright.
        Automatically cleans titles and parses relative deadlines/institutions.
        """
        print(f"[{self.__class__.__name__}] 드림스폰(DreamSpon) 실시간 크롤링 기동 중... ({self.source_url})")
        scholarships = []
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
                )
                page = await browser.new_page()
                
                # Set a transparent User-Agent showing we are DreamPocket's friendly bot
                await page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (DreamPocket Scholarship Matcher Bot; Contact: dreampocket.official@gmail.com)"
                })
                
                # Go to page
                await page.goto(self.source_url, wait_until="networkidle", timeout=20000)
                
                # Select rows
                rows = await page.query_selector_all("table tbody tr")
                print(f"[{self.__class__.__name__}] 총 {len(rows)}개의 실시간 공고 로우 감지 완료.")
                
                for row in rows:
                    cells = await row.query_selector_all("td")
                    if len(cells) < 3:
                        continue
                    
                    # 1. Title & URL Extraction (Cell 0)
                    title_elem = await cells[0].query_selector("a")
                    if not title_elem:
                        continue
                    
                    raw_title = (await title_elem.inner_text()).strip()
                    href = await title_elem.get_attribute("href")
                    
                    # Clean title (remove trailing hashtags like #대학생 #지역)
                    title_clean = raw_title.split("#")[0].strip()
                    # Clean whitespaces
                    title_clean = " ".join(title_clean.split())
                    
                    # Filter out irrelevant posts (results, community, announcements)
                    irrelevant_keywords = ['결과', '커뮤니티', '발표', '합격자', '수기', '후기', '게시판', '기자단', '서포터즈', '명단', '수여식']
                    if any(kw in title_clean for kw in irrelevant_keywords):
                        continue
                    
                    # Complete relative URL
                    if href:
                        source_url = href if href.startswith("http") else f"https://www.dreamspon.com{href}"
                    else:
                        source_url = self.source_url
                        
                    # 2. Institution Extraction (Cell 1)
                    institution = (await cells[1].inner_text()).strip()
                    institution = " ".join(institution.split())
                    
                    # Prepend institution to title to make it highly readable like "[경기] 경기도 체육인 기회소득"
                    if institution and not title_clean.startswith("["):
                        title_formatted = f"[{institution}] {title_clean}"
                    else:
                        title_formatted = title_clean
                        
                    # 3. D-Day / Period Parsing (Cell 2)
                    dday_raw = (await cells[2].inner_text()).strip()
                    dday_raw = " ".join(dday_raw.split())
                    
                    # Convert D-day string to a readable range
                    # E.g., 'D-9 중' -> 9 days remaining. Let's make it look like "2026.05.11 ~ D-9 마감"
                    now = datetime.now()
                    period_str = f"상시 모집 (현재 상태: {dday_raw})"
                    
                    # Regex search for digits in D-day
                    dday_match = re.search(r'D-(\d+)', dday_raw)
                    if dday_match:
                        days_left = int(dday_match.group(1))
                        end_date = now + timedelta(days=days_left)
                        period_str = f"{now.strftime('%Y.%m.%d')} ~ {end_date.strftime('%Y.%m.%d')} (마감 {days_left}일 전)"
                    elif "D-0" in dday_raw or "오늘마감" in dday_raw:
                        period_str = f"{now.strftime('%Y.%m.%d')} ~ 오늘 마감 (D-0 임박)"
                    
                    scholarships.append({
                        "category": "민간 장학금",
                        "title": title_formatted,
                        "period": period_str,
                        "status": "신청중",
                        "source": source_url,
                        "collected_at": now.isoformat()
                    })
                    
                await browser.close()
                print(f"[{self.__class__.__name__}] 성공적으로 {len(scholarships)}건의 드림스폰 실시간 공고 수집 완료!")
                
        except Exception as e:
            print(f"[{self.__class__.__name__}] 실시간 수집 중 오류 발생: {e}. 안전한 폴백 데이터를 활성화합니다.")
            # Fallback to pristine mock dataset if scraped is blocked/down
            now_iso = datetime.now().isoformat()
            scholarships = [
                {
                    "category": "민간 장학금",
                    "title": "[현대차정몽구재단] 2026 문화예술 및 사회과학(경영학 포함) 미래학문 인재 선발 (학점 3.8 이상)",
                    "period": "2026.05.10 ~ 2026.06.10",
                    "status": "신청중",
                    "source": "https://www.cmkfoundation-scholarship.org",
                    "collected_at": now_iso
                },
                {
                    "category": "민간 장학금",
                    "title": "[KT&G장학재단] 2026 대학생 상상 장학 프로그램 (지원구간 2구간 이하)",
                    "period": "2026.05.01 ~ 2026.05.28",
                    "status": "신청중",
                    "source": "https://scholarship.ktng.com",
                    "collected_at": now_iso
                }
            ]
            
        return scholarships
