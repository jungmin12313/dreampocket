import json
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from app import app

client = app.test_client()

test_payload = {
    "gpa": "3.5",
    "income": "8",
    "location": "서울",
    "major": "컴퓨터공학과"
}

print("Running local test for /api/match...")
response = client.post('/api/match', json=test_payload)
print(f"Status Code: {response.status_code}")

try:
    data = response.get_json()
    if data.get('success'):
        results = data.get('results', {})
        print(f"✅ Success Matches: {len(results.get('success_matches', []))}건")
        print(f"✅ Gap Matches: {len(results.get('gap_matches', []))}건")
        print(f"✅ Total Potential Amount: {results.get('total_potential_amount', 0):,}원")
        
        if results.get('success_matches'):
            print("\n[Sample Success Match]")
            print(json.dumps(results['success_matches'][0], indent=2, ensure_ascii=False))
    else:
        print("❌ API returned error:", data.get('error'))
except Exception as e:
    print(f"❌ Error parsing response: {e}")
    print(response.data.decode('utf-8'))
