import google.generativeai as genai
import json
import os
import re

class ScholarshipAIParser:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None

    def parse_scholarship_details(self, raw_text):
        """
        Parses raw scholarship text into structured data using Gemini.
        """
        if not self.model:
            return {"error": "API Key not configured"}

        prompt = f"""
        당신은 장학금 공고 분석 전문가입니다. 아래 장학금 공고 텍스트를 읽고 반드시 다음 JSON 형식으로만 응답하세요.
        추출할 수 없는 정보는 null로 표시하세요.

        {{
            "gpa_limit": (float, 예: 3.5),
            "income_limit": (int, 소득구간 숫자만, 예: 8),
            "major_restriction": (string, 예: "공학계열", "인문계열" 또는 "전체"),
            "region_restriction": (string, 예: "서울특별시", "경기도" 또는 "전국"),
            "benefit_type": "등록금" 또는 "생활비" 또는 "기타",
            "benefit_amount": (string, 예: "전액", "100만원", "실비지원"),
            "application_link": (string, 온라인 신청 페이지 URL),
            "is_closed": (boolean, 모집종료 여부)
        }}

        공고 텍스트:
        ---
        {raw_text[:4000]}  # Limit text length
        ---
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return {"error": "Could not parse AI response"}
        except Exception as e:
            return {"error": str(e)}

# Global instance
ai_parser = ScholarshipAIParser()
