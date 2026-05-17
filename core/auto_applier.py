import asyncio
from playwright.async_api import async_playwright
from core.database import db

class ScholarshipApplier:
    async def fill_application_form(self, user_id: str, notice_url: str):
        user = db.get_user_profile(user_id)
        if not user:
            return "유저 프로필이 존재하지 않습니다."
            
        print(f"== [자동 신청 보조 세션 시작] ==")
        print(f"신청 대상자: {user['user_id']}")
        print(f"학점: {user['gpa']}, 전공: {user['major']}, 지역: {user['location']}")
        print(f"이동 URL: {notice_url}")
        print("사용자가 직접 보고 상호작용할 수 있도록 대화형(Headed) 브라우저를 가동합니다...")
        
        async with async_playwright() as p:
            # Launch headed browser so the user can see, login, and confirm inputs!
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Navigate to target notice/apply page
            await page.goto(notice_url)
            
            # Inject a helpful UI overlay notification inside the page to guide the user!
            try:
                await page.evaluate("""
                    const div = document.createElement('div');
                    div.style.position = 'fixed';
                    div.style.top = '10px';
                    div.style.right = '10px';
                    div.style.backgroundColor = '#0074b9';
                    div.style.color = 'white';
                    div.style.padding = '15px';
                    div.style.borderRadius = '8px';
                    div.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
                    div.style.zIndex = '99999';
                    div.style.fontFamily = 'sans-serif';
                    div.style.fontSize = '14px';
                    div.innerHTML = '🚀 <b>Antigravity AI 신청 보조 가동 중</b><br>로그인 및 본인인증 완료 후 신청 서류 양식을 채울 때 도우미로 작동합니다. 최종 제출 전 꼼꼼히 확인해 주세요!';
                    document.body.appendChild(div);
                """)
            except Exception:
                pass
                
            print("대화형 브라우저가 열렸습니다. 로그인과 자격 입력을 완료한 뒤 최종 수동 제출을 진행하세요.")
            print("브라우저 창을 닫으면 이 보조 세션이 자동으로 종료됩니다.")
            
            # Keep browser active until user closes it
            while True:
                try:
                    await asyncio.sleep(1)
                    if page.is_closed():
                        break
                except Exception:
                    break
                    
            await browser.close()
            return f"{user['user_id']}님의 장학금 신청 보조 세션이 안전하게 종료되었습니다."

applier = ScholarshipApplier()
