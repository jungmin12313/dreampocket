import asyncio
from database import db
from agent_tools import get_user_and_matches

def main():
    print("Inserting test user profile...")
    test_user_id = "test_user_123"
    profile = {
        "gpa": "4.2",
        "income": "5",
        "location": "서울",
        "major": "컴퓨터공학"
    }
    db.save_user_profile(test_user_id, profile)
    print("Test user profile inserted successfully.")
    
    # Run match
    print(f"Running matches for user {test_user_id}...")
    match_result = get_user_and_matches(test_user_id)
    print("Match result:")
    import json
    print(json.dumps(match_result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
