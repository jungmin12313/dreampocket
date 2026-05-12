import asyncio
import sys
from agent_tools import refresh_scholarship_data

async def main():
    print("Refreshing scholarship data...")
    try:
        result = await refresh_scholarship_data()
        print(f"SUCCESS: {result}")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
