import re
from database import db

class ScholarshipBrain:
    def calculate_score(self, user_profile, scholarship):
        score = 0
        reasons = []
        is_eligible = True
        gaps = []

        # 1. Check primary matches: Major & Location
        major_matches = False
        user_major = user_profile.get('major', '').strip()
        sch_title = scholarship.get('title', '')
        sch_category = scholarship.get('category', '')

        if user_major:
            # 1. Exact or substring match in title (e.g. "컴퓨터" matches "컴퓨터공학과")
            if user_major in sch_title:
                major_matches = True
            # 2. Smart categorization mapping to prevent mismatching "경영" vs "컴퓨터" in generic "전공" categories
            elif sch_category == '전공':
                is_sch_business = any(k in sch_title for k in ['경영', '경제', '상경', '회계', '세무', '비즈니스'])
                is_user_business = any(k in user_major for k in ['경영', '경제', '상경', '회계', '세무', '비즈니스', '무역', '유통', '마케팅'])
                
                is_sch_stem = any(k in sch_title for k in ['이공', '공학', 'IT', '컴퓨터', '과학', '수학', '기술', '기계', '전자', '전기', '화학', '생물', '소프트웨어', '개발', '정보', '신소재', '건축', '토목', '의학', '약학'])
                is_user_stem = any(k in user_major for k in ['이공', '공학', 'IT', '컴퓨터', '과학', '수학', '기술', '기계', '전자', '전기', '화학', '생물', '소프트웨어', '개발', '정보', '신소재', '건축', '토목', '의학', '약학', '인공지능', 'AI', '넷', '웹', '앱'])

                if is_sch_business and not is_user_business:
                    major_matches = False
                elif is_sch_stem and not is_user_stem:
                    major_matches = False
                else:
                    major_matches = True
            else:
                major_matches = False

        # Smart regional matching logic
        user_loc = user_profile.get('location', '').strip()[:2] # e.g. "경기", "서울", "광주"
        
        # List of major regions in South Korea to detect regional restrictions
        regions_list = ['서울', '경기', '인천', '부산', '대구', '광주', '대전', '울산', '세종', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
        
        sch_region = None
        for r in regions_list:
            if r in sch_title:
                sch_region = r
                break
                
        # Map local sub-municipalities to their respective metropolitan/parent regions
        sub_municipalities = {
            '성남': '경기', '고양': '경기', '수원': '경기', '용인': '경기',
            '옹진': '인천', '성동': '서울', '창원': '경남', '전주': '전북',
            '청주': '충북', '천안': '충남'
        }
        for sub, parent in sub_municipalities.items():
            if sub in sch_title:
                sch_region = parent
                break

        location_matches = False
        region_score = 0
        region_reason = ""

        if sch_region:
            # The scholarship is region-specific
            if user_loc:
                if user_loc == sch_region:
                    # 1. Perfect residency/location match
                    location_matches = True
                    region_score = 30
                    region_reason = f"거주지 지역({user_loc}) 일치"
                elif sch_region in ['서울', '경기', '인천'] and user_loc in ['서울', '경기', '인천']:
                    # 2. Sudo-kwon (Metropolitan Area) cross-matching exception!
                    # e.g., Gyeonggi resident studying at a university in Seoul, or vice versa
                    location_matches = True
                    region_score = 15
                    region_reason = "수도권 교차 지원 우대 (타 지역 대학생 전형)"
                else:
                    # 3. Strict local restriction mismatch (e.g., Seoul resident trying to match Busan local fund)
                    is_eligible = False
                    gaps.append(
                        f"⚠️ 거주지역 제한 (본 공고는 [{sch_region}] 연고 학생을 위한 특화 공고입니다. "
                        f"내 프로필 지역 [{user_loc}]과 일치하지 않아 지원 요건에서 배제되었습니다.)"
                    )
            else:
                # If user did not provide a location, we allow matching but with no bonus score
                location_matches = False
        else:
            # 4. Region-agnostic national/corporate scholarship (e.g., KOSAF or Samsung Dream)
            location_matches = True
            region_score = 15
            region_reason = "전국구 공고 (거주지 무관 신청 가능)"

        if major_matches:
            score += 40
            reasons.append("전공 분야 일치")
        if location_matches and region_reason:
            score += region_score
            reasons.append(region_reason)

        score += 15  # Base score (up from 10)

        # Bonus: Category type bonus
        if sch_category == '국가 장학금':
            score += 10
            reasons.append("국가 장학금 (KOSAF 관리)")
        elif sch_category == '민간 장학금':
            score += 5
            reasons.append("민간 장학금 (기업/재단)")
        elif sch_category in ['지역 장학금', '지자체 장학금']:
            score += 8
            reasons.append("지역 장학금 (지자체 지원)")

        # 2. Parse GPA limits from scholarship title (e.g., "학점 3.0 이상")
        gpa_required = None
        gpa_match = re.search(r'학점\s*(\d+\.\d+|\d+)', scholarship['title'])
        if gpa_match:
            gpa_required = float(gpa_match.group(1))

        # Parse User GPA
        gpa_user = 0.0
        gpa_user_match = re.search(r'(\d+\.\d+|\d+)', user_profile['gpa'])
        if gpa_user_match:
            gpa_user = float(gpa_user_match.group(1))

        # Evaluate GPA requirement
        if gpa_required is not None:
            if gpa_user < gpa_required:
                is_eligible = False
                diff = round(gpa_required - gpa_user, 2)
                gaps.append(
                    f"⚠️ 학점이 {diff}점 부족합니다. "
                    f"이번 학기에 성적을 조금만 더 보완해서 {gpa_required} 이상을 맞추시면 다음 분기 선발에 바로 지원하실 수 있습니다! 힘내세요! 💪"
                )
            else:
                reasons.append(f"성적 조건 충족 (학점 {gpa_user} >= {gpa_required} 요구)")

        # 3. Parse Income limits from scholarship title (e.g., "지원구간 3구간 이하")
        income_required = None
        income_match = re.search(r'(지원구간|소득\s*분위|분위|구간)\s*(\d+)', scholarship['title'])
        if income_match:
            income_required = int(income_match.group(2))

        # Parse User Income
        income_user = None
        if user_profile['income'] and user_profile['income'] != '모름':
            income_user_match = re.search(r'(\d+)', user_profile['income'])
            if income_user_match:
                income_user = int(income_user_match.group(1))

        # Evaluate Income requirement
        if income_required is not None:
            if income_user is None:
                is_eligible = False
                gaps.append(
                    f"ℹ️ 소득분위 {income_required}구간 이하 조건이 필요하나, 현재 프로필이 '모름'으로 설정되어 있습니다. "
                    f"한국장학재단 지원구간이 산정되면 프로필 정보를 업데이트하여 신청 가능 여부를 확인해 보세요!"
                )
            elif income_user > income_required:
                is_eligible = False
                gaps.append(
                    f"⚠️ 소득분위 조건 초과 (요구: {income_required}구간 이하, 내 프로필: {income_user}구간). "
                    f"만약 가구원 변동 등이 있었다면 최신 소득분위 상태로 프로필을 새로고침해 보세요."
                )
            else:
                reasons.append(f"소득분위 요건 충족 (내 분위 {income_user} <= {income_required}구간 요구)")

        return {
            "score": score,
            "reasons": reasons,
            "is_eligible": is_eligible,
            "gaps": gaps,
            "is_potential": (major_matches or location_matches) # Potential close call
        }

    def get_matches(self, user_id):
        user = db.get_user_profile(user_id)
        if not user: 
            return {"success_matches": [], "gap_matches": []}
            
        all_scholarships = db.get_all_scholarships()
        success_matches = []
        gap_matches = []
        
        for sch in all_scholarships:
            # Skip closed, expired, or verified dead links
            if sch.get('status') in ['마감', '만료', '비활성']:
                continue
                
            analysis = self.calculate_score(user, sch)
            item = {
                "id": sch['id'],
                "title": sch['title'], 
                "score": analysis['score'],
                "reasons": analysis['reasons'], 
                "link": sch['source'], 
                "period": sch['period'],
                "gaps": analysis['gaps']
            }
            
            if analysis['is_eligible'] and analysis['score'] >= 30:
                success_matches.append(item)
            elif not analysis['is_eligible'] and analysis['is_potential']:
                gap_matches.append(item)
                
        # Sort by score descending
        success_matches = sorted(success_matches, key=lambda x: x['score'], reverse=True)
        gap_matches = sorted(gap_matches, key=lambda x: x['score'], reverse=True)
        
        return {
            "success_matches": success_matches,
            "gap_matches": gap_matches
        }

brain = ScholarshipBrain()
