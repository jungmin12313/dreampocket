import json
import os
from datetime import datetime
import asyncio
from core.link_extractor import link_extractor

TARGET_FILE = "data/target_sites.json"

class UniversalScraper:
    def __init__(self):
        self.sites = []
        self._load_sites()
        
    def _load_sites(self):
        if os.path.exists(TARGET_FILE):
            try:
                with open(TARGET_FILE, "r", encoding="utf-8") as f:
                    self.sites = json.load(f)
                print(f"[UniversalScraper] Loaded {len(self.sites)} target sites.")
            except Exception as e:
                print(f"[UniversalScraper] Error loading target sites: {e}")
        else:
            print(f"[UniversalScraper] Target file {TARGET_FILE} not found. Please run url_discovery_bot.py first.")

    async def fetch_scholarship_list(self):
        if not self.sites:
            return []
            
        print(f"[{self.__class__.__name__}] 300+ 범용 사이트 순회 수집 시작...")
        
        all_results = []
        today = datetime.now()
        
        # To avoid overwhelming memory, we process one site at a time
        for site in self.sites:
            try:
                links = await link_extractor.extract_notice_links(site['url'])
                
                for link in links:
                    # Create basic scaffold. AI enrichment will fill the rest later.
                    item = {
                        "category": site.get("category", "일반 장학금"),
                        "title": f"[{site['name']}] {link['title']}",
                        "period": "상세 공고 참조",
                        "status": "진행중",
                        "source": link['url'],
                        "collected_at": today.isoformat()
                    }
                    all_results.append(item)
                    
                # Short delay between sites
                await asyncio.sleep(1.0)
                
            except Exception as e:
                print(f"[UniversalScraper] Error processing {site['name']}: {e}")
                
        print(f"[{self.__class__.__name__}] 총 {len(all_results)}개의 범용 공고글 스크랩 완료.")
        return all_results
