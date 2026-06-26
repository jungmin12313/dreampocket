import json
import os

target_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "target_sites.json")

new_targets = [
    { "id": "found_asan", "name": "아산사회복지재단", "url": "https://www.asanfoundation.or.kr", "category": "민간 장학금", "region": "전국" },
    { "id": "found_lotte", "name": "롯데장학재단", "url": "https://www.lottefoundation.or.kr/lt001/menu002001.do?hash=tab-1", "category": "민간 장학금", "region": "전국" },
    { "id": "found_kwanjeong", "name": "관정이종환교육재단", "url": "http://www.ikef.or.kr", "category": "민간 장학금", "region": "전국" },
    { "id": "found_posco", "name": "포스코청암재단", "url": "https://www.postf.org", "category": "민간 장학금", "region": "전국" },
    { "id": "found_hyundai", "name": "현대차 정몽구 재단", "url": "https://www.hyundai-cmkfoundation.org", "category": "민간 장학금", "region": "전국" },
    { "id": "found_samsung", "name": "삼성꿈장학재단", "url": "https://www.sdream.or.kr", "category": "민간 장학금", "region": "전국" },
    { "id": "found_stx", "name": "STX장학재단", "url": "http://www.stxfoundation.or.kr", "category": "민간 장학금", "region": "전국" },
    { "id": "found_ilju", "name": "일주학술문화재단", "url": "https://www.iljufoundation.org", "category": "민간 장학금", "region": "전국" },
    { "id": "found_wooyang", "name": "우양재단", "url": "https://www.wooyang.org", "category": "민간 장학금", "region": "전국" },
    { "id": "found_kosaf", "name": "한국장학재단 공지사항", "url": "https://www.kosaf.go.kr", "category": "국가/민간 장학금", "region": "전국" },
    
    { "id": "univ_sogang", "name": "서강대학교", "url": "https://www.sogang.ac.kr/front/boardlist.do?bbsConfigFK=141", "category": "대학 장학금", "region": "서울특별시" },
    { "id": "univ_cau", "name": "중앙대학교", "url": "https://www.cau.ac.kr/cms/FR_CON/index.do?MENU_ID=100", "category": "대학 장학금", "region": "서울특별시" },
    { "id": "univ_khu", "name": "경희대학교", "url": "https://www.khu.ac.kr/kor/notice/list.do?category=SCHOLARSHIP", "category": "대학 장학금", "region": "서울특별시" },
    { "id": "univ_hufs", "name": "한국외국어대학교", "url": "https://www.hufs.ac.kr/hufs/11440/subview.do", "category": "대학 장학금", "region": "서울특별시" },
    { "id": "univ_uos", "name": "서울시립대학교", "url": "https://www.uos.ac.kr/korNotice/list.do?list_id=FA1", "category": "대학 장학금", "region": "서울특별시" },
    { "id": "univ_ewha", "name": "이화여자대학교", "url": "https://www.ewha.ac.kr/ewha/news/scholarship.do", "category": "대학 장학금", "region": "서울특별시" },
    { "id": "univ_konkuk", "name": "건국대학교", "url": "https://www.konkuk.ac.kr/konkuk/2056/subview.do", "category": "대학 장학금", "region": "서울특별시" },
    { "id": "univ_dongguk", "name": "동국대학교", "url": "https://www.dongguk.edu/article/HAKSANOTICE/list", "category": "대학 장학금", "region": "서울특별시" },
    { "id": "univ_hongik", "name": "홍익대학교", "url": "https://www.hongik.ac.kr/kr/life/scholarship-notice.do", "category": "대학 장학금", "region": "서울특별시" },
    { "id": "univ_kookmin", "name": "국민대학교", "url": "https://www.kookmin.ac.kr/user/kmuNews/notice/4/index.do", "category": "대학 장학금", "region": "서울특별시" },
    { "id": "univ_ssu", "name": "숭실대학교", "url": "https://scatch.ssu.ac.kr/공지사항/", "category": "대학 장학금", "region": "서울특별시" },
    { "id": "univ_sejong", "name": "세종대학교", "url": "https://board.sejong.ac.kr/boardlist.do?bbsConfigFK=334", "category": "대학 장학금", "region": "서울특별시" },
    { "id": "univ_dankook", "name": "단국대학교", "url": "https://www.dankook.ac.kr/web/kor/-39", "category": "대학 장학금", "region": "경기도" },
    { "id": "univ_gachon", "name": "가천대학교", "url": "https://www.gachon.ac.kr/kor/7350/subview.do", "category": "대학 장학금", "region": "경기도" },
    { "id": "univ_ajou", "name": "아주대학교", "url": "https://www.ajou.ac.kr/kr/ajou/notice.do?mode=list&srCategoryId1=312", "category": "대학 장학금", "region": "경기도" }
]

def main():
    if not os.path.exists(target_file):
        print(f"File not found: {target_file}")
        return
        
    with open(target_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # check for duplicates by id
    existing_ids = {item["id"] for item in data}
    
    added_count = 0
    for target in new_targets:
        if target["id"] not in existing_ids:
            data.append(target)
            added_count += 1
            
    if added_count > 0:
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Successfully added {added_count} targets. Total targets: {len(data)}")
    else:
        print("No new targets added. They might already exist.")

if __name__ == "__main__":
    main()
