import asyncio
import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import db
from core.document_analyzer import analyzer
from core.ai_parser import ai_parser

async def enrich_scholarships(limit=20):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] AI data enrichment started... (Max {limit})")
    
    # Get scholarships that need enrichment
    # Criteria: analysis_status != 'AI 정밀 분석' AND is_verified = 0
    cursor = db.conn.cursor()
    cursor.execute('''
        SELECT id, source, title 
        FROM scholarships 
        WHERE (analysis_status != 'AI 정밀 분석' OR analysis_status IS NULL) 
        AND (is_verified = 0 OR is_verified IS NULL)
        AND source != 'KOSAF' AND source LIKE 'http%'
        ORDER BY collected_at DESC
        LIMIT ?
    ''', (limit,))
    
    targets = cursor.fetchall()
    
    if not targets:
        print("Done. No new scholarships need enrichment.")
        return

    print(f"Total {len(targets)} scholarships to analyze.")
    
    processed_count = 0
    for sch_id, source_url, title in targets:
        print(f"\n--- [{processed_count + 1}/{len(targets)}] Analyzing: {title} ---")
        
        try:
            # 1. Extract text from notice
            print(f"  Searching text from: {source_url}")
            raw_text = await analyzer.extract_text_from_notice(source_url)
            
            if "Error" in raw_text or "유효한" in raw_text:
                print(f"  Failed to collect text: {raw_text}")
                continue
                
            # 2. Parse using AI
            print(f"  Requesting AI analysis (Gemini)...")
            enriched_data = ai_parser.parse_scholarship_details(raw_text)
            
            if "error" in enriched_data:
                if "429" in str(enriched_data['error']):
                    print(f"  Rate limit hit. Waiting 30 seconds...")
                    await asyncio.sleep(30)
                    enriched_data = ai_parser.parse_scholarship_details(raw_text)
                    if "error" in enriched_data:
                        print(f"  AI analysis failed after retry: {enriched_data['error']}")
                        continue
                else:
                    print(f"  AI analysis failed: {enriched_data['error']}")
                    continue
                
            # 3. Update Database
            print(f"  Updating DB...")
            db.update_enriched_scholarship(sch_id, enriched_data)
            
            print(f"  Success: {enriched_data.get('benefit_amount', 'N/A')} | {enriched_data.get('benefit_type', 'Other')}")
            processed_count += 1
            
            # Longer sleep to avoid rate limiting
            await asyncio.sleep(10)
            
        except Exception as e:
            print(f"  Error occurred ({title}): {e}")

    print(f"\nDone. Total {processed_count} scholarships enriched.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Scholarship Enrichment")
    parser.add_argument("--limit", type=int, default=10, help="Max items to process")
    args = parser.parse_args()
    
    asyncio.run(enrich_scholarships(limit=args.limit))
