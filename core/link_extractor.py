import re
from playwright.async_api import async_playwright
import urllib.parse

class UniversalLinkExtractor:
    async def extract_notice_links(self, board_url: str):
        print(f"[LinkExtractor] Extracting from: {board_url}")
        if not board_url or not board_url.startswith("http"):
            return []
            
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            page = await browser.new_page()
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            try:
                await page.goto(board_url, wait_until="networkidle", timeout=15000)
                links = await page.query_selector_all("a")
                
                extracted = []
                for link in links:
                    href = await link.get_attribute("href")
                    text = (await link.inner_text()).strip()
                    
                    if not href or len(text) < 5:
                        continue
                        
                    # Filter logic: Likely a notice link
                    href_lower = href.lower()
                    is_notice = False
                    
                    # 1. Contains common article identifiers
                    if any(kw in href_lower for kw in ['article', 'id=', 'idx=', 'seq=', 'no=', 'view', 'read']):
                        is_notice = True
                    
                    # 2. Text contains scholarship keywords
                    if any(kw in text for kw in ['장학', '모집', '안내', '선발', '신청']):
                        is_notice = True
                        
                    # Exclude common false positives (pagination, login, file downloads)
                    if any(kw in href_lower for kw in ['page=', 'login', 'download', '.pdf', '.hwp', '.zip']):
                        is_notice = False
                    if text.isdigit() or text in ['다음', '이전', 'Next', 'Prev']:
                        is_notice = False
                        
                    if is_notice:
                        # Make absolute URL
                        full_url = urllib.parse.urljoin(board_url, href)
                        extracted.append({"title": text, "url": full_url})
                        
                await browser.close()
                
                # Deduplicate by URL
                seen = set()
                unique_links = []
                for item in extracted:
                    if item['url'] not in seen:
                        seen.add(item['url'])
                        unique_links.append(item)
                        
                print(f"[LinkExtractor] Found {len(unique_links)} potential notice links.")
                return unique_links
                
            except Exception as e:
                print(f"[LinkExtractor] Error extracting {board_url}: {e}")
                await browser.close()
                return []

link_extractor = UniversalLinkExtractor()
