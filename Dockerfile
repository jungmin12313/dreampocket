# 1. Playwright와 시스템 브라우저 패키지가 사전 설치된 공식 Python 이미지 사용
FROM mcr.microsoft.com/playwright/python:v1.50.0-jammy

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 전체 소스코드 복사
COPY . .

# 5. Flask 구동 포트 노출 (Render가 주입하는 $PORT 환경변수 바인딩을 위해 쉘 형태로 실행)
CMD gunicorn app:app --workers 1 --timeout 120 --bind 0.0.0.0:$PORT
