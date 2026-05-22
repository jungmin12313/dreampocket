import re
from core.database import db

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
            # 1. Exact or substring match in title
            if user_major in sch_title:
                major_matches = True
            # 2. Advanced semantic categorization
            elif sch_category == '전공' or any(k in sch_title for k in ['학과', '계열', '전공']):
                # Define major clusters
                is_sch_business = any(k in sch_title for k in ['경영', '경제', '상경', '회계', '세무', '비즈니스', '금융'])
                is_user_business = any(k in user_major for k in ['경영', '경제', '상경', '회계', '세무', '비즈니스', '무역', '유통', '마케팅', '금융'])
                
                is_sch_stem = any(k in sch_title for k in ['이공', '공학', 'IT', '컴퓨터', '과학', '수학', '기술', '기계', '전자', '전기', '화학', '생물', '소프트웨어', '개발', '정보', '신소재', '건축', '토목', '의학', '약학', '인공지능', 'AI'])
                is_user_stem = any(k in user_major for k in ['이공', '공학', 'IT', '컴퓨터', '과학', '수학', '기술', '기계', '전자', '전기', '화학', '생물', '소프트웨어', '개발', '정보', '신소재', '건축', '토목', '의학', '약학', '인공지능', 'AI', '넷', '웹', '앱'])
                
                is_sch_arts = any(k in sch_title for k in ['예능', '체능', '예술', '디자인', '음악', '미술', '체육', '스포츠'])
                is_user_arts = any(k in user_major for k in ['예능', '체능', '예술', '디자인', '음악', '미술', '체육', '스포츠', '만화', '영상', '연극', '무용'])
                
                is_sch_edu = any(k in sch_title for k in ['사범', '교육', '교대', '교직'])
                is_user_edu = any(k in user_major for k in ['사범', '교육', '교대', '교직', '국어교육', '영어교육', '수학교육', '유아교육'])

                # Match logic based on clusters
                if is_sch_business and is_user_business: major_matches = True
                elif is_sch_stem and is_user_stem: major_matches = True
                elif is_sch_arts and is_user_arts: major_matches = True
                elif is_sch_edu and is_user_edu: major_matches = True
                elif any(k in sch_title for k in ['전체', '무관', '공통']): major_matches = True
                else: major_matches = False
            else:
                major_matches = False

        # Smart regional matching logic
        user_loc = user_profile.get('location', '').strip()[:2] # e.g. "경기", "서울", "광주"
        
        # Comprehensive mapping of full/abbreviated region names to two-letter base
        region_mappings = {
            '서울특별시': '서울', '서울': '서울',
            '경기도': '경기', '경기': '경기',
            '인천광역시': '인천', '인천': '인천',
            '부산광역시': '부산', '부산': '부산',
            '대구광역시': '대구', '대구': '대구',
            '광주광역시': '광주', '광주': '광주',
            '대전광역시': '대전', '대전': '대전',
            '울산광역시': '울산', '울산': '울산',
            '세종특별자치시': '세종', '세종': '세종',
            '강원특별자치도': '강원', '강원도': '강원', '강원': '강원',
            '충청북도': '충북', '충북': '충북',
            '충청남도': '충남', '충남': '충남',
            '전라북도': '전북', '전북특별자치도': '전북', '전북': '전북',
            '전라남도': '전남', '전남': '전남',
            '경상북도': '경북', '경북': '경북',
            '경상남도': '경남', '경남': '경남',
            '제주특별자치도': '제주', '제주도': '제주', '제주': '제주'
        }

        # Map local sub-municipalities to their parent provinces
        sub_municipalities = {
            # 경기 (Gyeonggi)
            '성남': '경기', '고양': '경기', '수원': '경기', '용인': '경기', '부천': '경기', 
            '안산': '경기', '화성': '경기', '평택': '경기', '의정부': '경기', '시흥': '경기', 
            '김포': '경기', '광명': '경기', '군포': '경기', '오산': '경기', '이천': '경기', 
            '양주': '경기', '안성': '경기', '구리': '경기', '포천': '경기', '의왕': '경기', 
            '하남': '경기', '여주': '경기', '동두천': '경기', '과천': '경기', '양평': '경기', 
            '가평': '경기', '연천': '경기',
            # 인천 (Incheon)
            '강화': '인천', '옹진': '인천',
            # 강원 (Gangwon)
            '춘천': '강원', '원주': '강원', '강릉': '강원', '동해': '강원', '태백': '강원', 
            '속초': '강원', '삼척': '강원', '홍천': '강원', '횡성': '강원', '영월': '강원', 
            '평창': '강원', '정선': '강원', '철원': '강원', '화천': '강원', '양구': '강원', 
            '인제': '강원', '고성': '강원', '양양': '강원',
            # 충북 (Chungbuk)
            '청주': '충북', '충주': '충북', '제천': '충북', '보은': '충북', '옥천': '충북', 
            '영동': '충북', '증평': '충북', '진천': '충북', '괴산': '충북', '음성': '충북', 
            '단양': '충북',
            # 충남 (Chungnam)
            '천안': '충남', '공주': '충남', '보령': '충남', '아산': '충남', '서산': '충남', 
            '논산': '충남', '계룡': '충남', '당진': '충남', '금산': '충남', '부여': '충남', 
            '서천': '충남', '청양': '충남', '홍성': '충남', '예산': '충남', '태안': '충남',
            # 전북 (Jeonbuk)
            '전주': '전북', '군산': '전북', '익산': '전북', '정읍': '전북', '남원': '전북', 
            '김제': '전북', '완주': '전북', '진안': '전북', '무주': '전북', '장수': '전북', 
            '임실': '전북', '순창': '전북', '고창': '전북', '부안': '전북',
            # 전남 (Jeonnam)
            '목포': '전남', '여수': '전남', '순천': '전남', '나주': '전남', '광양': '전남', 
            '담양': '전남', '곡성': '전남', '구례': '전남', '고흥': '전남', '보성': '전남', 
            '화순': '전남', '장흥': '전남', '강진': '전남', '해남': '전남', '영암': '전남', 
            '무안': '전남', '함평': '전남', '영광': '전남', '장성': '전남', '완도': '전남', 
            '진도': '전남', '신안': '전남',
            # 경북 (Gyeongbuk)
            '포항': '경북', '경주': '경북', '김천': '경북', '안동': '경북', '구미': '경북', 
            '영주': '경북', '영천': '경북', '상주': '경북', '문경': '경북', '경산': '경북', 
            '의성': '경북', '청송': '경북', '영양': '경북', '영덕': '경북', '청도': '경북', 
            '고령': '경북', '성주': '경북', '칠곡': '경북', '예천': '경북', '봉화': '경북', 
            '울진': '경북', '울릉': '경북',
            # 경남 (Gyeongnam)
            '창원': '경남', '진주': '경남', '통영': '경남', '사천': '경남', '김해': '경남', 
            '밀양': '경남', '거제': '경남', '양산': '경남', '의령': '경남', '함안': '경남', 
            '창녕': '경남', '남해': '경남', '하동': '경남', '산청': '경남', '함양': '경남', 
            '거창': '경남', '합천': '경남'
        }

        # Check in region_restriction first if it exists in database
        db_region_restrict = scholarship.get('region_restriction')
        sch_region = None
        
        if db_region_restrict:
            for k, val in region_mappings.items():
                if k in db_region_restrict:
                    sch_region = val
                    break
            if not sch_region:
                for k, val in sub_municipalities.items():
                    if k in db_region_restrict:
                        sch_region = val
                        break

        # Fallback to Title parsing
        if not sch_region:
            sorted_region_keys = sorted(region_mappings.keys(), key=len, reverse=True)
            for k in sorted_region_keys:
                if k in sch_title:
                    sch_region = region_mappings[k]
                    break
                    
        if not sch_region:
            sorted_sub_keys = sorted(sub_municipalities.keys(), key=len, reverse=True)
            for k in sorted_sub_keys:
                if k in sch_title:
                    sch_region = sub_municipalities[k]
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
                    location_matches = True
                    region_score = 15
                    region_reason = "수도권 교차 지원 우대 (타 지역 대학생 전형)"
                else:
                    # 3. Strict local restriction mismatch
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
            score += 45 # Increased from 40
            reasons.append("전공 분야 최적 매칭")
        if location_matches and region_reason:
            score += region_score
            reasons.append(region_reason)

        score += 20  # Base score (up from 15)

        # Bonus: Category type bonus
        if sch_category == '국가 장학금' or '한국장학재단' in sch_title:
            score += 15
            reasons.append("국가 지원 (신뢰도 최상)")
        elif sch_category == '민간 장학금':
            score += 5
            reasons.append("민간 기업/재단 장학")
        elif sch_category in ['지역 장학금', '지자체 장학금']:
            score += 12 # Increased from 8
            reasons.append("지역 연고 우대 장학")

        # 2. GPA Requirement logic
        # Priority: Structured DB field -> Title Regex
        gpa_required = scholarship.get('gpa_limit')
        if gpa_required is None:
            gpa_match = re.search(r'학점\s*(\d+\.\d+|\d+)', scholarship['title'])
            if gpa_match:
                gpa_required = float(gpa_match.group(1))

        # Parse User GPA
        gpa_user = 0.0
        gpa_user_match = re.search(r'(\d+\.\d+|\d+)', user_profile['gpa'])
        if gpa_user_match:
            gpa_user = float(gpa_user_match.group(1))

        if gpa_required is not None:
            if gpa_user < gpa_required:
                is_eligible = False
                diff = round(gpa_required - gpa_user, 2)
                gaps.append(f"⚠️ 학점이 {diff}점 부족합니다. (요구: {gpa_required} 이상)")
            else:
                reasons.append(f"성적 조건 충족 (학점 {gpa_user} >= {gpa_required} 요구)")

        # 3. Income Requirement logic
        # Priority: Structured DB field -> Title Regex
        income_required = scholarship.get('income_limit')
        if income_required is None:
            income_match = re.search(r'(지원구간|소득\s*분위|분위|구간)\s*(\d+)', scholarship['title'])
            if income_match:
                income_required = int(income_match.group(2))

        # Parse User Income
        income_user = None
        if user_profile['income'] and user_profile['income'] != '모름':
            income_user_match = re.search(r'(\d+)', user_profile['income'])
            if income_user_match:
                income_user = int(income_user_match.group(1))

        if income_required is not None:
            if income_user is None:
                is_eligible = False
                gaps.append(f"ℹ️ 소득분위 {income_required}구간 이하 조건이 필요하나 현재 프로필이 '모름'입니다.")
            elif income_user > income_required:
                is_eligible = False
                gaps.append(f"⚠️ 소득분위 조건 초과 (요구: {income_required}구간 이하, 내 프로필: {income_user}구간)")
            else:
                reasons.append(f"소득분위 요건 충족 (내 분위 {income_user} <= {income_required}구간)")
                if income_user <= 3:
                    score += 15
                    reasons.append("저소득층 지원 우대 가중치 적용")

        # Confidence Calculation
        analysis_status = scholarship.get('analysis_status', '제목 분석')
        is_verified = scholarship.get('is_verified', 0)
        
        confidence = 65 # Base confidence for keyword matching
        if is_verified:
            confidence = 100
        elif analysis_status == 'AI 정밀 분석':
            confidence = 95
        elif gpa_required is not None or income_required is not None:
            confidence = 80 # Found specific numbers, higher trust

        return {
            "score": score,
            "reasons": reasons,
            "is_eligible": is_eligible,
            "gaps": gaps,
            "is_potential": (major_matches or location_matches),
            "confidence": confidence,
            "analysis_status": analysis_status,
            "is_verified": is_verified
        }

    def get_matches(self, user_id):
        user = db.get_user_profile(user_id)
        if not user: 
            return {"success_matches": [], "gap_matches": [], "total_potential_amount": 0}
            
        all_scholarships = db.get_all_scholarships()
        success_matches = []
        gap_matches = []
        total_potential_amount = 0
        
        for sch in all_scholarships:
            if sch.get('status') in ['마감', '만료', '비활성'] or sch.get('is_closed') == 1:
                continue
                
            analysis = self.calculate_score(user, sch)
            
            # Amount estimation (Prioritize enriched data)
            amount_est = 0
            if sch.get('benefit_amount'):
                # Extract numbers from benefit_amount string
                amount_str = sch['benefit_amount']
                if '전액' in amount_str:
                    amount_est = 3500000
                else:
                    nums = re.findall(r'(\d+)', amount_str.replace(',', ''))
                    if nums:
                        val = int(nums[0])
                        if '억' in amount_str: val *= 100000000
                        elif '만' in amount_str or val < 10000: val *= 10000
                        amount_est = val
            
            if amount_est == 0:
                amount_match = re.search(r'(\d+)만\s*원?', sch['title'])
                if amount_match:
                    amount_est = int(amount_match.group(1)) * 10000
                elif '전액' in sch['title']:
                    amount_est = 3500000
                # 기본값 500,000원은 제외 (허수 방지)

            item = {
                "id": sch['id'],
                "title": sch['title'], 
                "category": sch['category'],
                "score": analysis['score'],
                "reasons": analysis['reasons'], 
                "link": sch['source'], 
                "period": sch['period'],
                "amount_est": amount_est,
                "gaps": analysis['gaps'],
                "confidence": analysis['confidence'],
                "analysis_status": analysis['analysis_status'],
                "is_verified": analysis['is_verified']
            }
            
            if analysis['is_eligible'] and analysis['score'] >= 30:
                success_matches.append(item)
                total_potential_amount += amount_est
            elif not analysis['is_eligible'] and analysis['is_potential']:
                gap_matches.append(item)
                
        # Sort by score descending
        success_matches = sorted(success_matches, key=lambda x: x['score'], reverse=True)
        gap_matches = sorted(gap_matches, key=lambda x: x['score'], reverse=True)
        
        return {
            "success_matches": success_matches,
            "gap_matches": gap_matches,
            "total_potential_amount": total_potential_amount
        }

brain = ScholarshipBrain()
