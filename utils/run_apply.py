import asyncio
import sys
from agent_tools import start_apply_session

async def main():
    try:
        # Launch headed application assistant for user_chat and scholarship ID 8
        await start_apply_session("user_chat", 8)
    except Exception as e:
        print(f"Error starting application session: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
