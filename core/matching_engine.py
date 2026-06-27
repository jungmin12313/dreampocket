import re
from core.database import db

class ScholarshipBrain:
    def calculate_score(self, user_profile, scholarship):
        score = 0
        reasons = []
        is_eligible = True
        gaps = []

        # Parse User Info
        user_major = user_profile.get('major', '').strip()
        user_loc = user_profile.get('location', '').strip()[:2]
        
        gpa_user = 0.0
        gpa_user_match = re.search(r'(\d+\.\d+|\d+)', user_profile.get('gpa', '0'))
        if gpa_user_match:
            gpa_user = float(gpa_user_match.group(1))
            
        income_user = 10
        if user_profile.get('income') and user_profile.get('income') != '모름':
            income_user_match = re.search(r'(\d+)', user_profile['income'])
            if income_user_match:
                income_user = int(income_user_match.group(1))

        # Parse Scholarship New Fields
        gpa_min = scholarship.get('gpa_min')
        if gpa_min is None: gpa_min = 0.0 # Fallback
        
        income_max = scholarship.get('income_max')
        if income_max is None: income_max = 10 # Fallback
        
        region_rule = scholarship.get('region_rule')
        if not region_rule: region_rule = 'nationwide'
        
        region_target = scholarship.get('region_target')
        
        major_rule = scholarship.get('major_rule')
        if not major_rule: major_rule = 'any'
        
        major_target = scholarship.get('major_target')
        
        # New Feature Fields
        is_duplicatable = scholarship.get('is_duplicatable')
        recruit_count = scholarship.get('recruit_count', 0)
        if recruit_count is None: recruit_count = 0
        difficulty = scholarship.get('difficulty')
        work_required = scholarship.get('work_required')
        
        # 1. Hard Filter Checks
        if gpa_user < gpa_min:
            is_eligible = False
            diff = round(gpa_min - gpa_user, 2)
            gaps.append(f"⚠️ 학점이 {diff}점 부족합니다. (요구: {gpa_min} 이상)")
        else:
            if gpa_min > 0:
                reasons.append(f"성적 조건 충족 (요구: {gpa_min} 이상)")
            
        if income_user > income_max:
            is_eligible = False
            gaps.append(f"⚠️ 소득분위 조건 초과 (요구: {income_max}구간 이하, 내 프로필: {income_user}구간)")
        else:
            if income_max < 10:
                reasons.append(f"소득분위 요건 충족 ({income_max}구간 이하)")

        # Region Hard Filter
        location_matches = False
        region_score = 0
        if region_rule in ['local', 'restricted'] and region_target:
            # Simple matching
            if user_loc and user_loc in region_target:
                location_matches = True
                region_score = 25
                reasons.append(f"거주지 지역({user_loc}) 일치")
            elif region_target in ['서울', '경기', '인천'] and user_loc in ['서울', '경기', '인천']:
                location_matches = True
                region_score = 10
                reasons.append("수도권 교차 지원 허용")
            else:
                is_eligible = False
                gaps.append(f"⚠️ 지역 제한 불일치 (필요지역: {region_target})")
        else:
            location_matches = True
            region_score = 10
            reasons.append("거주지 무관 (전국구)")

        # Major Scoring
        major_matches = False
        major_score = 0
        if major_rule in ['specific', 'field_group'] and major_target:
            if user_major and (user_major in major_target or major_target in user_major):
                major_matches = True
                major_score = 45
                reasons.append("전공 분야 일치")
            else:
                # Treated as a soft gap if restricted heavily
                major_score = 0
        else:
            major_matches = True
            major_score = 10
            reasons.append("전공 무관")

        # Sum up Score
        score += 20  # Base score
        
        if major_matches or location_matches:
            score += major_score + region_score
            
        if income_user <= 3:
            score += 20
            reasons.append("저소득층 우대 (+20점)")
            
        if gpa_user >= gpa_min + 0.5 and gpa_min > 0:
            score += 15
            reasons.append("학점 우수 (+15점)")
            
        # Next Level Filtering Logic
        if is_duplicatable == 1:
            score += 20
            reasons.append("중복 수혜 가능 (+20점)")
            
        if recruit_count > 50:
            score += 10
            reasons.append(f"대규모 선발 ({recruit_count}명, +10점)")
            
        if difficulty == 'Low':
            score += 5
            reasons.append("서류 간단함 (+5점)")
            
        if work_required == 1:
            score -= 10
            reasons.append("근로/의무 사항 있음 (-10점)")
            
        # Confidence logic
        analysis_status = scholarship.get('analysis_status', '미분석')
        confidence = 100 if analysis_status == 'AI 정밀 분석' else 60

        return {
            "score": score,
            "reasons": reasons,
            "is_eligible": is_eligible,
            "gaps": gaps,
            "is_potential": (score > 10 and not is_eligible),
            "confidence": confidence,
            "analysis_status": analysis_status,
            "is_verified": scholarship.get('is_verified', 0)
        }

    def get_matches(self, user_profile):
        if not user_profile: 
            return {"success_matches": [], "gap_matches": [], "total_potential_amount": 0}
            
        all_scholarships = db.get_all_scholarships()
        success_matches = []
        gap_matches = []
        total_potential_amount = 0
        
        for sch in all_scholarships:
            # Hard filter 1: Status and Loan flag
            if sch.get('status') in ['마감', '만료', '비활성'] or sch.get('is_closed') == 1 or sch.get('is_loan') == 1:
                continue
                
            analysis = self.calculate_score(user_profile, sch)
            
            # Amount fallback
            amount_est = 0
            
            # Check DB field 'benefit_amount' first
            db_amount = sch.get('benefit_amount', '')
            if db_amount:
                if '전액' in db_amount:
                    amount_est = 3500000
                else:
                    nums = re.findall(r'(\d+)', db_amount.replace(',', ''))
                    if nums:
                        val = int(nums[0])
                        if '억' in db_amount: val *= 100000000
                        elif '만' in db_amount or val < 10000: val *= 10000
                        amount_est = val

            if amount_est == 0:
                amount_match = re.search(r'(\d+)만\s*원?', sch['title'])
                if amount_match:
                    amount_est = int(amount_match.group(1)) * 10000
                elif '전액' in sch['title']:
                    amount_est = 3500000

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
                "is_verified": analysis['is_verified'],
                "ai_summary": sch.get('ai_summary', ''),
                "is_duplicatable": sch.get('is_duplicatable'),
                "recruit_count": sch.get('recruit_count', 0),
                "difficulty": sch.get('difficulty', ''),
                "work_required": sch.get('work_required', 0)
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
