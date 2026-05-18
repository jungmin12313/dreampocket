import os
import re
from playwright.async_api import async_playwright
from pypdf import PdfReader

class DocumentAnalyzer:
    async def extract_text_from_notice(self, source_url: str):
        if not source_url or source_url == "KOSAF" or not source_url.startswith("http"):
            return "유효한 공고 URL이 없습니다."
            
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            page = await browser.new_page()
            # Set a common User-Agent to avoid issues
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            print(f"Opening notice URL: {source_url}")
            try:
                await page.goto(source_url, wait_until="networkidle")
                
                # Get the core notice board content text
                # In standard KOSAF board views, contents are inside board_view, tbl_view, or similar.
                # To be robust, we'll grab from body but filter out menus.
                body_text = await page.locator("body").inner_text()
                
                # Clean up multiple newlines
                body_clean = re.sub(r'\n+', '\n', body_text)
                
                # Look for attachments
                attachments = []
                links = await page.query_selector_all("a")
                for link in links:
                    href = await link.get_attribute("href")
                    text = (await link.inner_text()).strip()
                    if href and (".pdf" in href.lower() or "file" in href.lower() or "download" in href.lower() or "attach" in href.lower()):
                        # Clean href
                        href_clean = href.replace("&amp;", "&")
                        full_href = href_clean if href_clean.startswith("http") else f"https://www.kosaf.go.kr{href_clean}"
                        attachments.append((text, full_href))
                
                combined_text = f"=== [공고 본문 내용] ===\n{body_clean}\n"
                if attachments:
                    combined_text += "\n=== [첨부파일 목록] ===\n"
                    for i, (name, url) in enumerate(attachments):
                        combined_text += f"[{i+1}] {name} -> {url}\n"
                        
                await browser.close()
                return combined_text
                
            except Exception as e:
                await browser.close()
                return f"Error extracting notice: {e}"

analyzer = DocumentAnalyzer()
