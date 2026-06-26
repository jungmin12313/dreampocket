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
        추출할 수 없는 정보는 null 또는 기본값으로 표시하세요.

        {{
            "region_rule": (string, "nationwide", "local", "restricted" 중 택1. 기본값 "nationwide"),
            "region_target": (string, local이나 restricted일 경우 지역명(예: "서울특별시"), 아니면 null),
            "major_rule": (string, "any", "specific", "field_group" 중 택1. 기본값 "any"),
            "major_target": (string, specific/field_group일 경우 제한전공명(예: "이공계열", "컴퓨터공학"), 아니면 null),
            "gpa_min": (float, 최소 요구 학점 숫자만, 없으면 0.0),
            "income_max": (int, 최대 요구 소득구간/분위 숫자만, 없으면 10),
            "ai_summary": (string, 공고에 대한 1줄 핵심 요약)
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
