import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.link_extractor import link_extractor
from core.document_analyzer import analyzer
from core.ai_parser import ai_parser

async def test_pipeline():
    # 1. 대상 사이트: 부산대학교 장학공지
    target_url = "https://www.pusan.ac.kr/kor/CMS/Board/Board.do?mCode=MN100"
    print(f"=== 1. 게시판 링크 추출 테스트 ===")
    print(f"접속 대상: {target_url}")
    
    links = await link_extractor.extract_notice_links(target_url)
    if not links:
        print("게시물 링크를 찾지 못했습니다.")
        return
        
    print(f"\n추출된 게시물 링크 수: {len(links)}개")
    for i, link in enumerate(links[:3]):
        print(f" [{i+1}] {link['title']}\n     -> {link['url']}")
        
    # 2. 첫 번째 공고글 본문 추출 테스트
    first_link = links[0]['url']
    first_title = links[0]['title']
    print(f"\n=== 2. 본문 내용 (Raw Text) 추출 테스트 ===")
    print(f"타겟 공고: {first_title}")
    
    raw_text = await analyzer.extract_text_from_notice(first_link)
    print(f"추출된 텍스트 길이: {len(raw_text)} 자")
    print(f"본문 앞부분 미리보기:\n{raw_text[:300]}...\n")
    
    # 3. AI 파서 핵심 정보(성적/소득/지역) 추출 테스트
    print(f"=== 3. AI 핵심 조건 정밀 분석 테스트 ===")
    enriched_data = ai_parser.parse_scholarship_details(raw_text)
    
    print("AI 분석 결과 (JSON):")
    for k, v in enriched_data.items():
        print(f" - {k}: {v}")
        
    # 4. 중복 방지 로직 (설명용 출력)
    print(f"\n=== 4. 중복(도배) 방지 로직 테스트 ===")
    print(f"현재 DB는 공고글의 고유 URL('{first_link}')을 기본 키(Unique Key)로 사용합니다.")
    print("AI가 날짜를 잘못 인식하거나 업데이트 날짜가 바뀌더라도, URL이 동일하면 무조건 '덮어쓰기(UPDATE)' 처리되므로 똑같은 공고가 2개 생성되지 않습니다.")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
