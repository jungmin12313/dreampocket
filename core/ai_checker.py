import os
import json
import google.generativeai as genai
from core.database import Database

# Configure Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    
model = genai.GenerativeModel('gemini-2.5-flash')

def generate_eligibility_questions(sch_id: int) -> list:
    """
    Given a scholarship ID, fetch its AI summary and generate 1-2 critical Yes/No questions
    to verify specific eligibility constraints, excluding basic GPA/Income/Major checks.
    """
    db = Database()
    try:
        sch = db.execute_query('SELECT title, ai_summary, target FROM scholarships WHERE id = ?', (sch_id,), fetchone=True)
    except Exception:
        sch = None
        
    if not sch:
        return []
        
    title = sch[0]
    ai_summary = sch[1] or ""
    target_str = sch[2] or ""
    
    combined_text = f"제목: {title}\n요약: {ai_summary}\n대상: {target_str}"
    
    prompt = f"""
    당신은 장학금 자격 요건 검증 AI입니다.
    아래 장학금 공고문의 원문 요약을 읽고, 지원자가 반드시 확인해야 하는 '가장 까다로운 특수 조건' 1~2가지를 추출하세요.
    (예: 부모님의 거주지, 특정 질병 여부, 다자녀 여부, 특정 봉사활동 시간 등)
    
    주의사항:
    1. 성적(GPA), 소득분위, 전공, 학년에 대한 질문은 절대로 하지 마세요. (이미 시스템에서 필터링됨)
    2. 추출한 조건은 사용자가 '네' 또는 '아니오'로 답할 수 있는 구체적인 의문문으로 작성하세요.
    3. 특수 조건이 전혀 없고 기본 조건(성적/소득/학교)만 있다면 빈 배열을 반환하세요.
    4. 반드시 유효한 JSON 배열(Array of strings) 형태로만 응답하세요. 텍스트나 마크다운(```json 등)을 포함하지 마세요.
    
    [장학금 텍스트]
    {combined_text}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean markdown if present
        if text.startswith("```json"):
            text = text.replace("```json", "", 1)
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        questions = json.loads(text)
        if isinstance(questions, list):
            # Limit to max 2 questions
            return questions[:2]
        return []
    except Exception as e:
        print(f"AI Check generation error: {e}")
        return []
