import asyncio
import sys
from agent_tools import extract_notice_full_text

async def main():
    print("Testing extract_notice_full_text with scholarship ID 8...")
    try:
        # ID 8 corresponds to 푸른등대 기부장학금 notice
        text = await extract_notice_full_text(8)
        
        # Write to file in UTF-8
        with open("notice_extracted_8.txt", "w", encoding="utf-8") as f:
            f.write(text)
            
        print("\n=== SUCCESS! ===")
        print("Notice text successfully extracted and saved to 'notice_extracted_8.txt' in UTF-8!")
        print(f"Total extracted characters: {len(text)}")
        print("=================")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
