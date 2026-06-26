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
        당신은 장학금 공고 분석 전문가입니다. 
        아래 텍스트는 웹페이지에서 무작위로 긁어온 순수 텍스트(Raw Text)이므로, 과거 게시물 날짜나 불필요한 배너 내용이 섞여 있을 수 있습니다.
        당신의 임무는 조손가정, 다자녀 같은 마이너한 자격 조건은 모두 무시하고 오직 **[지역, 전공, 성적, 소득분위]** 핵심 4가지만 정확히 뽑아내는 것입니다.

        [추출 규칙]
        1. 지역: 지원 자격에 특정 시/도(예: 광주, 전남) 거주 제한이 있다면 "local", "restricted"로 설정하고 지역명을 기재. 제한이 없으면 "nationwide".
        2. 전공: 특정 단과대/학과 제한이 없으면 "any". 있으면 "specific" 또는 "field_group" 후 타겟 전공 기재.
        3. 성적(GPA): 텍스트 내 수많은 숫자 중 **반드시 '지원 자격' 근처에 있는 학점 숫자(예: 3.0 이상)**만 추출. 없으면 0.0
        4. 소득분위: **반드시 '지원 자격' 근처에 있는 소득구간 상한선(예: 8분위 이하 -> 8)**만 추출. 없으면 10
        
        반드시 다음 JSON 형식으로만 응답하세요. 백틱(`)이나 마크다운 없이 순수 JSON만 출력하세요.
        {{
            "region_rule": "nationwide", "local", "restricted" 중 택1,
            "region_target": "지역명(예: 광주광역시) 또는 null",
            "major_rule": "any", "specific", "field_group" 중 택1,
            "major_target": "전공명(예: 상경계열) 또는 null",
            "gpa_min": 최소학점(숫자, 예: 3.5),
            "income_max": 최대소득구간(숫자, 예: 8),
            "ai_summary": "1줄 요약"
        }}

        공고 텍스트:
        ---
        {raw_text[:4000]}
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
