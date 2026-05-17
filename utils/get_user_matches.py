import json
from core.database import db
from core.agent_tools import get_user_and_matches

def main():
    user_id = "user_chat"
    profile = {
        "gpa": "2.75",
        "income": "모름",
        "location": "광주",
        "major": "경영학부"
    }
    db.save_user_profile(user_id, profile)
    print("User profile saved successfully.")
    
    # Fetch all scholarships to analyze
    scholarships = db.get_all_scholarships()
    print(f"Total scholarships available in DB: {len(scholarships)}")
    
    # We will print all scholarships in JSON format so our orchestrator can read them
    print("SCHOLARSHIP_DATA_START")
    print(json.dumps(scholarships, indent=2, ensure_ascii=False))
    print("SCHOLARSHIP_DATA_END")
    
    # Also get matches from matching engine
    matches = get_user_and_matches(user_id)
    print("MATCHES_DATA_START")
    print(json.dumps(matches, indent=2, ensure_ascii=False))
    print("MATCHES_DATA_END")

if __name__ == "__main__":
    main()
