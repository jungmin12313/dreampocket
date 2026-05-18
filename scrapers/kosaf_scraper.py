import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
from core.database import db

class KosafScraper:
    async def fetch_scholarship_list(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            # Set a transparent User-Agent showing we are DreamPocket's friendly bot
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (DreamPocket Scholarship Matcher Bot; Contact: dreampocket.official@gmail.com)"
            })
            url = "https://www.kosaf.go.kr/ko/notice.do?ctgrId1=0000000002"
            await page.goto(url, wait_until="networkidle")
            
            rows = await page.query_selector_all("table.t-viewz tbody tr")
            scholarships = []
            for row in rows:
                cells = await row.query_selector_all("td")
                if len(cells) < 4: continue
                title_element = await cells[1].query_selector("a")
                if not title_element: continue
                
                title_text = (await title_element.inner_text()).strip()
                # Clean up title if there are multiple spaces/newlines
                title_text = " ".join(title_text.split())
                
                href = await title_element.get_attribute("href")
                if href and href.startswith("?"):
                    # Replace HTML entities if any
                    href_clean = href.replace("&amp;", "&")
                    source_url = f"https://www.kosaf.go.kr/ko/notice.do{href_clean}"
                else:
                    source_url = "KOSAF"
                
                post_date = (await cells[2].inner_text()).strip()
                
                scholarships.append({
                    "category": "장학금",
                    "title": title_text,
                    "period": post_date,
                    "status": "진행중",
                    "source": source_url,
                    "collected_at": datetime.now().isoformat()
                })
            await browser.close()
            return scholarships
