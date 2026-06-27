document.addEventListener("DOMContentLoaded", function () {
    // ----------------------------------------------------
    // DOM Elements
    // ----------------------------------------------------
    // Screens
    const introScreen = document.getElementById("intro-screen");
    const surveyScreen = document.getElementById("survey-screen");
    const analysisLoaderScreen = document.getElementById("analysis-loader-screen");
    const resultsScreen = document.getElementById("results-screen");

    // Stepper elements
    const startSurveyBtn = document.getElementById("start-survey-btn");
    const stepperForm = document.getElementById("matching-stepper-form");
    const prevStepBtn = document.getElementById("prev-step-btn");
    const nextStepBtn = document.getElementById("next-step-btn");
    const progressFill = document.getElementById("progress-fill");
    const stepCounterText = document.getElementById("step-counter-text");
    const loaderTitle = document.getElementById("loader-title");
    const backModifyBtn = document.getElementById("back-modify-btn");

    // Inputs & Val Display
    const gpaInput = document.getElementById("gpa-input");
    const gpaVal = document.getElementById("gpa-val");
    const incomeInput = document.getElementById("income-input");
    const locationInput = document.getElementById("location-input");
    const majorCategory = document.getElementById("major-category");
    const majorInput = document.getElementById("major-input");

    // Stats & Tabs in Results Dashboard
    const totalSchCount = document.getElementById("total-sch-count");
    const lastUpdateTime = document.getElementById("last-update-time");
    const successBadge = document.getElementById("success-badge");
    const gapsBadge = document.getElementById("gaps-badge");
    const tabSuccess = document.getElementById("tab-success");
    const tabGaps = document.getElementById("tab-gaps");
    const contentSuccess = document.getElementById("content-success");
    const contentGaps = document.getElementById("content-gaps");
    const successList = document.getElementById("success-list");
    const gapsList = document.getElementById("gaps-list");

    // ----------------------------------------------------
    // State Variables
    // ----------------------------------------------------
    let currentStep = 1;
    const totalSteps = 4;

    // Standard Academic Major Mapping (Seoul-based University Standard)
    const ACADEMIC_MAJOR_MAP = {
        "공과대학": [
            { text: "컴퓨터공학과", val: "컴퓨터공학과" },
            { text: "소프트웨어학과", val: "소프트웨어학과" },
            { text: "전자정보공학과", val: "전자공학과" },
            { text: "전기공학과", val: "전기공학과" },
            { text: "기계공학과", val: "기계공학과" },
            { text: "화학공학과", val: "화학공학과" },
            { text: "신소재공학과", val: "신소재공학과" },
            { text: "건축공학과", val: "건축공학과" },
            { text: "산업경영공학과", val: "산업공학과" }
        ],
        "경영대학 / 상경대학": [
            { text: "경영학과", val: "경영학과" },
            { text: "경제학과", val: "경제학과" },
            { text: "통계학과", val: "통계학과" },
            { text: "글로벌경영학과", val: "경영학과" },
            { text: "금융학부", val: "경영학과" },
            { text: "세무회계학과", val: "경영학과" }
        ],
        "사회과학대학": [
            { text: "정치외교학과", val: "정치외교학과" },
            { text: "행정학과", val: "행정학과" },
            { text: "사회학과", val: "사회학과" },
            { text: "미디어커뮤니케이션학과 (언론정보)", val: "언론정보학과" },
            { text: "심리학과", val: "심리학과" },
            { text: "사회복지학과", val: "사회복지학과" }
        ],
        "인문대학": [
            { text: "국어국문학과", val: "국어국문학과" },
            { text: "영어영문학과", val: "영어영문학과" },
            { text: "사학과", val: "사학과" },
            { text: "철학과", val: "철학과" },
            { text: "독어독문학과", val: "국어국문학과" },
            { text: "불어불문학과", val: "국어국문학과" }
        ],
        "자연과학대학": [
            { text: "수학과", val: "수학과" },
            { text: "물리학과", val: "물리학과" },
            { text: "화학과", val: "화학과" },
            { text: "생명과학과", val: "생명과학과" },
            { text: "천문우주학과", val: "물리학과" }
        ],
        "사범대학": [
            { text: "교육학과", val: "교육학과" },
            { text: "국어교육과", val: "국어교육과" },
            { text: "영어교육과", val: "영어교육과" },
            { text: "수학교육과", val: "수학교육과" },
            { text: "체육교육과", val: "체육학과" }
        ],
        "의과대학 / 약학대학": [
            { text: "의학과 (의예과)", val: "의학과" },
            { text: "약학과", val: "약학과" },
            { text: "간호학과", val: "간호학과" },
            { text: "수의학과", val: "의학과" },
            { text: "한의학과", val: "의학과" }
        ],
        "예술·체육대학": [
            { text: "체육학과 (스포츠과학)", val: "체육학과" },
            { text: "산업디자인학과", val: "디자인학과" },
            { text: "시각디자인학과", val: "디자인학과" },
            { text: "음악학과 (성악/기악)", val: "음악학과" },
            { text: "동양화과 / 서양화과", val: "미술학과" },
            { text: "연극영화학과", val: "연극영화과" }
        ],
        "자유전공학부": [
            { text: "자유전공학부 (인문계열)", val: "자유전공" },
            { text: "자유전공학부 (자연계열)", val: "자유전공" },
            { text: "융합전공학부", val: "일반" },
            { text: "인공지능융합학과", val: "컴퓨터공학과" }
        ]
    };

    // ----------------------------------------------------
    // Welcome Screen Transition
    // ----------------------------------------------------
    startSurveyBtn.addEventListener("click", function () {
        introScreen.classList.remove("active");
        surveyScreen.classList.add("active");
        updateStepperUI();
    });

    // ----------------------------------------------------
    // Stepper Navigation Core Logic
    // ----------------------------------------------------
    function updateStepperUI() {
        // Toggle step active states
        const stepCards = document.querySelectorAll(".step-card");
        stepCards.forEach(card => {
            if (parseInt(card.getAttribute("data-step")) === currentStep) {
                card.classList.add("active");
            } else {
                card.classList.remove("active");
            }
        });

        // Update progress line & text counter
        const progressPercent = (currentStep / totalSteps) * 100;
        progressFill.style.width = `${progressPercent}%`;
        stepCounterText.innerText = `${currentStep} / ${totalSteps} 단계`;

        // Update buttons footer layout
        if (currentStep === 1) {
            prevStepBtn.classList.add("hidden");
        } else {
            prevStepBtn.classList.remove("hidden");
        }

        if (currentStep === totalSteps) {
            nextStepBtn.innerHTML = `<span>내 드림포켓 열어보기 🔮</span>`;
            nextStepBtn.classList.add("next-btn-submit");
        } else {
            nextStepBtn.innerHTML = `<span>다음</span> <i class="fa-solid fa-arrow-right"></i>`;
            nextStepBtn.classList.remove("next-btn-submit");
        }
    }

    function nextStep() {
        if (currentStep < totalSteps) {
            currentStep++;
            updateStepperUI();
        } else {
            submitSurvey();
        }
    }

    function prevStep() {
        if (currentStep > 1) {
            currentStep--;
            updateStepperUI();
        }
    }

    nextStepBtn.addEventListener("click", nextStep);
    prevStepBtn.addEventListener("click", prevStep);

    // ----------------------------------------------------
    // Step Inputs Interaction Logic
    // ----------------------------------------------------

    // GPA Scale Selection
    const scaleBtns = document.querySelectorAll(".scale-btn");
    let currentScale = 4.5;
    
    scaleBtns.forEach(btn => {
        btn.addEventListener("click", function() {
            scaleBtns.forEach(b => b.classList.remove("active"));
            this.classList.add("active");
            currentScale = parseFloat(this.dataset.scale);
            
            // Update slider max and UI
            gpaInput.max = currentScale;
            let val = parseFloat(gpaInput.value);
            if (val > currentScale) {
                val = currentScale;
                gpaInput.value = val;
            }
            gpaVal.innerText = `${val.toFixed(2)} / ${currentScale}`;
            
            const trackFill = document.querySelector(".gpa-slider-track-fill");
            if(trackFill) {
                const percent = (val / currentScale) * 100;
                trackFill.style.width = `${percent}%`;
            }
        });
    });

    // Income Modal Controls
    const incomeModal = document.getElementById("income-modal");
    const openIncomeModal = document.getElementById("open-income-modal");
    const closeIncomeModal = document.querySelector(".close-modal");
    
    if (openIncomeModal) {
        openIncomeModal.addEventListener("click", function(e) {
            e.preventDefault();
            incomeModal.classList.add("active");
        });
    }
    
    if (closeIncomeModal) {
        closeIncomeModal.addEventListener("click", function() {
            incomeModal.classList.remove("active");
        });
    }

    // Step 1: GPA Range display updater
    gpaInput.addEventListener("input", function (e) {
        const val = parseFloat(e.target.value).toFixed(2);
        gpaVal.innerText = `${val} / ${currentScale}`;
        
        // Update track fill if present
        const trackFill = document.querySelector(".gpa-slider-track-fill");
        if(trackFill) {
            const percent = (val / currentScale) * 100;
            trackFill.style.width = `${percent}%`;
        }
    });

    function getNormalizedGPA() {
        const rawGpa = parseFloat(gpaInput.value);
        // Normalize to 4.5 scale for engine consistency
        return ((rawGpa / currentScale) * 4.5).toFixed(2);
    }

    // Step 2: One-touch Income Bracket Selection & Auto-advance
    const incomeBtns = document.querySelectorAll(".income-step-wrapper .grid-btn");
    incomeBtns.forEach(btn => {
        btn.addEventListener("click", function () {
            incomeBtns.forEach(b => b.classList.remove("active"));
            this.classList.add("active");
            
            const val = this.getAttribute("data-val");
            incomeInput.value = val;
            
            // Auto advance step with 150ms delays for extremely satisfying feedback!
            setTimeout(() => {
                nextStep();
            }, 180);
        });
    });

    // Step 3: One-touch Location Selection & Auto-advance
    const locationBtns = document.querySelectorAll(".location-step-wrapper .grid-btn");
    locationBtns.forEach(btn => {
        btn.addEventListener("click", function () {
            locationBtns.forEach(b => b.classList.remove("active"));
            this.classList.add("active");
            
            const loc = this.getAttribute("data-loc");
            locationInput.value = loc;
            
            // Auto advance
            setTimeout(() => {
                nextStep();
            }, 180);
        });
    });

    // Step 4: Populate Majors dynamically
    function populateMajors() {
        const category = majorCategory.value;
        const majors = ACADEMIC_MAJOR_MAP[category] || [];
        
        majorInput.innerHTML = "";
        majors.forEach(major => {
            const opt = document.createElement("option");
            opt.value = major.val;
            opt.innerText = major.text;
            majorInput.appendChild(opt);
        });
    }

    majorCategory.addEventListener("change", populateMajors);

    // ----------------------------------------------------
    // Interstitial AI Analysis Loader & Backend fetch
    // ----------------------------------------------------
    function submitSurvey() {
        // 1. Enter Loader Screen
        introScreen.classList.remove("active");
        surveyScreen.classList.remove("active");
        analysisLoaderScreen.classList.add("active");

        // Prepare match request data
        const payload = {
            gpa: getNormalizedGPA(),
            income: incomeInput.value === "모름" ? "모름" : `${incomeInput.value}구간`,
            location: locationInput.value,
            major: majorInput.value
        };

        // Trigger rolling analysis titles to build amazing Fintech style UX!
        const analysisTexts = [
            "사용자 조건 정밀 판독 중...",
            "소득 연계 분위 및 거주 지역 매칭 중...",
            "장학 요강 적합도 및 가중치 분석 중...",
            "최적 맞춤 드림포켓 정렬 중..."
        ];

        let index = 0;
        const textInterval = setInterval(() => {
            if (index < analysisTexts.length - 1) {
                index++;
                loaderTitle.innerText = analysisTexts[index];
            }
        }, 400);

        // Call Flask Matching API
        fetch("/api/match", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            // Keep loader on screen for at least 1500ms for premium psychological "AI calculation" feedback
            setTimeout(() => {
                clearInterval(textInterval);
                if (data.success) {
                    renderResults(data.results);
                    
                    // Exit Loader, open Fullscreen results page!
                    analysisLoaderScreen.classList.remove("active");
                    resultsScreen.classList.add("active");
                } else {
                    showToast("드림포켓을 여는데 에러가 발생했습니다. DB를 확인하세요.");
                    // Rollback to survey
                    analysisLoaderScreen.classList.remove("active");
                    surveyScreen.classList.add("active");
                }
            }, 1500);
        })
        .catch(err => {
            clearInterval(textInterval);
            console.error("Match error:", err);
            showToast("네트워크 연결 오류가 발생했습니다.");
            analysisLoaderScreen.classList.remove("active");
            surveyScreen.classList.add("active");
        });
    }

    // Back & Modify button
    backModifyBtn.addEventListener("click", function (e) {
        if (window.IS_SHARED_RESULT) {
            e.preventDefault();
            window.location.href = "/";
            return;
        }
        resultsScreen.classList.remove("active");
        surveyScreen.classList.add("active");
        currentStep = 1;
        updateStepperUI();
    });

    // ----------------------------------------------------
    // Tab Controller
    // ----------------------------------------------------
    tabSuccess.addEventListener("click", function () {
        tabSuccess.classList.add("active");
        tabGaps.classList.remove("active");
        contentSuccess.classList.add("active");
        contentGaps.classList.remove("active");
    });

    tabGaps.addEventListener("click", function () {
        tabGaps.classList.add("active");
        tabSuccess.classList.remove("active");
        contentGaps.classList.add("active");
        contentSuccess.classList.remove("active");
    });

    // ----------------------------------------------------
    // Ad simulation logic
    // ----------------------------------------------------
    function showToast(message, isClick = false) {
        const container = document.getElementById("toast-container");
        const toast = document.createElement("div");
        toast.className = `toast ${isClick ? 'toast-click' : ''}`;
        toast.innerHTML = `<i class="fa-solid ${isClick ? 'fa-wallet' : 'fa-circle-check'}"></i> <span>${message}</span>`;
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = "toast-in 0.3s reverse forwards";
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);
    }

    function bindAdClicks() {
        // Disabled ad simulation logic for frontend per admin request
        return;
    }

    // ----------------------------------------------------
    // Dynamic Listings Rendering & Animations
    // ----------------------------------------------------
    // Returns { diffDays, html } — diffDays = null if date unparseable
    function parseDDay(periodStr) {
        if (!periodStr) return { diffDays: null, html: '' };
        const parts = periodStr.split('~');
        let endStr = parts.length > 1 ? parts[1].trim() : parts[0].trim();
        const dateMatch = endStr.match(/(\d{4})[-./](\d{1,2})[-./](\d{1,2})/);
        if (!dateMatch) return { diffDays: null, html: '' };
        const year = parseInt(dateMatch[1]);
        const month = parseInt(dateMatch[2]) - 1;
        const day = parseInt(dateMatch[3]);
        const endDate = new Date(year, month, day);
        if (isNaN(endDate.getTime())) return { diffDays: null, html: '' };
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        endDate.setHours(0, 0, 0, 0);
        const diffTime = endDate - today;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        let html = '';
        if (diffDays < 0) {
            html = `<span class="d-day-tag" style="background-color: #ef4444; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-left: 6px;">마감</span>`;
        } else if (diffDays === 0) {
            html = `<span class="d-day-tag" style="background-color: #ef4444; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-left: 6px;">D-Day</span>`;
        } else if (diffDays <= 7) {
            html = `<span class="d-day-tag" style="background-color: #f97316; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-left: 6px;">D-${diffDays}</span>`;
        } else {
            html = `<span class="d-day-tag" style="background-color: #3b82f6; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-left: 6px;">D-${diffDays}</span>`;
        }
        return { diffDays, html };
    }

    function calculateDDay(periodStr) {
        return parseDDay(periodStr).html;
    }

    // 대출 관련 키워드
    const LOAN_KEYWORDS = ['대출', '학자금대출', '생활비대출', '융자', '이자', '저금리', '금리', '상환', '보증', '담보'];
    function isLoanRelated(title) {
        return LOAN_KEYWORDS.some(k => title.includes(k));
    }

    function animateValue(obj, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            const val = Math.floor(progress * (end - start) + start);
            obj.innerHTML = val.toLocaleString() + "원";
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    function shareResults() {
        const payload = {
            gpa: gpaInput.value,
            income: incomeInput.value,
            location: locationInput.value,
            major: majorInput.value
        };
        const encoded = btoa(encodeURIComponent(JSON.stringify(payload)));
        const url = `${window.location.origin}${window.location.pathname}?p=${encoded}`;
        
        navigator.clipboard.writeText(url).then(() => {
            showToast("결과 공유 링크가 복사되었습니다! 🔗", true);
        }).catch(err => {
            console.error("Share error:", err);
            showToast("링크 복사에 실패했습니다.");
        });
    }

    document.getElementById("share-link-btn").addEventListener("click", shareResults);

    // MATCH 점수 구성 설명 (툴팁용)
    const MATCH_SCORE_BREAKDOWN = [
        { label: '기본 매칭 점수', score: '+20', desc: '모든 공고에 부여되는 기본 점수' },
        { label: '전공 분야 일치', score: '+45', desc: '내 전공과 공고 대상 전공이 매칭될 때' },
        { label: '거주 지역 일치', score: '+30', desc: '내 거주지와 공고 대상 지역이 정확히 일치할 때' },
        { label: '수도권 교차 지원', score: '+15', desc: '서울/경기/인천 수도권 교차 지원 허용 공고' },
        { label: '전국구 공고', score: '+15', desc: '지역 제한 없이 전국 어디서나 신청 가능한 공고' },
        { label: '국가 장학금 가산', score: '+15', desc: '한국장학재단 등 국가 지원 공신력 가산' },
        { label: '지역 장학금 가산', score: '+12', desc: '지자체 특화 장학금 지역 연고 우대 가산' },
        { label: '민간 장학금 가산', score: '+5', desc: '기업/재단 민간 장학금 가산' },
        { label: '저소득층 우대', score: '+15', desc: '소득분위 3구간 이하 저소득 우대 장학금 가산' },
    ];

    function buildMatchTooltip() {
        return MATCH_SCORE_BREAKDOWN.map(item =>
            `<div class="match-tip-row"><span class="match-tip-label">${item.label}</span><span class="match-tip-score">${item.score}점</span><span class="match-tip-desc">${item.desc}</span></div>`
        ).join('');
    }

    function renderResults(results) {
        let successes = results.success_matches || [];
        let gaps = results.gap_matches || [];

        // ──────────────────────────────────────────────
        // 1. 대출 관련 장학금 제거
        // ──────────────────────────────────────────────
        successes = successes.filter(sch => !isLoanRelated(sch.title));
        gaps = gaps.filter(sch => !isLoanRelated(sch.title));

        // ──────────────────────────────────────────────
        // 2. 마감 장학금 처리: success → gaps 이동, 7일 초과 마감은 완전 제거
        // ──────────────────────────────────────────────
        const stillActiveSuccesses = [];
        const movedToGaps = [];

        successes.forEach(sch => {
            const { diffDays } = parseDDay(sch.period);
            if (diffDays !== null) {
                if (diffDays < 0) {
                    // 마감됨 → 7일 이내 마감이면 gaps로 이동, 그 이상이면 제거
                    const daysAgo = Math.abs(diffDays);
                    if (daysAgo <= 7) {
                        // 7일 이내 마감된 공고 → gaps 탭으로 이동
                        movedToGaps.push({ ...sch, _movedFromSuccess: true });
                    }
                    // 7일 초과 마감 → 완전 제거 (아무것도 하지 않음)
                } else {
                    stillActiveSuccesses.push(sch);
                }
            } else {
                // 기간 파싱 불가 → 유효한 것으로 간주
                stillActiveSuccesses.push(sch);
            }
        });

        // gaps도 7일 초과 마감 제거
        const filteredGaps = gaps.filter(sch => {
            const { diffDays } = parseDDay(sch.period);
            if (diffDays !== null && diffDays < -7) return false; // 7일 초과 마감 제거
            return true;
        });

        // 마감된 success 공고를 gaps 앞에 추가
        const allGaps = [...movedToGaps, ...filteredGaps];

        // ──────────────────────────────────────────────
        // 3. 정렬: 점수 내림차순 → 마감 임박 순 (D-day 오름차순)
        // ──────────────────────────────────────────────
        function sortScholarships(list) {
            return list.sort((a, b) => {
                if (b.score !== a.score) return b.score - a.score;
                const dA = parseDDay(a.period).diffDays;
                const dB = parseDDay(b.period).diffDays;
                if (dA === null && dB === null) return 0;
                if (dA === null) return 1;
                if (dB === null) return -1;
                // D-day가 작은(임박한) 것 우선, 단 마감된 것(음수)은 뒤로
                if (dA >= 0 && dB >= 0) return dA - dB;
                if (dA >= 0) return -1;
                if (dB >= 0) return 1;
                return dB - dA;
            });
        }

        sortScholarships(stillActiveSuccesses);
        sortScholarships(allGaps);

        // ──────────────────────────────────────────────
        // 4. 보수적 수혜 가능 총액 계산
        //    - 금액이 명시된 공고 또는 is_verified인 공고만 합산
        //    - 기본값(500,000원) 공고는 제외하여 과대평가 방지
        // ──────────────────────────────────────────────
        let conservativeTotal = 0;
        stillActiveSuccesses.forEach(sch => {
            const amt = sch.amount_est || 0;
            // 명시된 금액이 있는 경우만 합산 (기본값 500,000 제외)
            if (amt > 0 && amt !== 500000) {
                conservativeTotal += amt;
            }
        });

        // Update counts
        successBadge.innerText = stillActiveSuccesses.length;
        gapsBadge.innerText = allGaps.length;

        // Animate total potential amount (보수적 총액)
        const totalAmountDisplay = document.getElementById("total-potential-amount");
        animateValue(totalAmountDisplay, 0, conservativeTotal, 1000);

        // ──────────────────────────────────────────────
        // 정렬 기준 안내 배너
        // ──────────────────────────────────────────────
        const sortInfoHtml = `
            <div class="sort-info-banner">
                <i class="fa-solid fa-arrow-up-wide-short"></i>
                <span>정렬 기준: <strong>MATCH 점수 높은 순</strong> → <strong>마감 임박 순</strong> (장학금·전공장학금·민간장학금 통합 적용)</span>
            </div>
        `;

        // ──────────────────────────────────────────────
        // 5. 성공 카드 렌더링
        // ──────────────────────────────────────────────
        const tooltipHtml = buildMatchTooltip();

        if (stillActiveSuccesses.length === 0) {
            successList.innerHTML = `
                ${sortInfoHtml}
                <div class="empty-state">
                    <div class="empty-icon">😢</div>
                    <div class="empty-title">매칭된 우수 장학금이 없습니다</div>
                    <div class="empty-desc">조건에 딱 맞는 공고가 모집 전이거나 마감되었습니다. 소득 기준이나 거주지 정보를 조정하여 다시 분석해 보세요.</div>
                </div>
            `;
        } else {
            let html = sortInfoHtml;
            stillActiveSuccesses.forEach((sch, idx) => {
                const specificTooltipHtml = sch.reasons.map(r => `<div class="match-tip-row" style="padding: 4px 0; color: #e2e8f0; font-size: 0.8rem;"><i class="fa-solid fa-check" style="color:var(--success); margin-right:6px;"></i><span class="match-tip-label">${r}</span></div>`).join("");
                const displayScore = Math.min(sch.score, 100);
                const offset = 100 - displayScore;

                // Highlight Badge (중복 수혜 / 생활비 지원)
                const highlightBadge = sch.is_duplicatable === 1
                    ? `<span class="category-tag" style="background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); color: #fff; border: none; font-weight: 700; box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);">✨ 생활비·중복수혜</span>`
                    : `<span class="category-tag">${sch.category || '일반'}</span>`;

                // Minimalist Metadata line
                let metadataArr = [];
                if (sch.recruit_count > 0) metadataArr.push(`🔥 ${sch.recruit_count}명 선발`);
                if (sch.difficulty === 'Low') metadataArr.push(`🟢 서류 간단`);
                else if (sch.difficulty === 'High') metadataArr.push(`🔴 자소서/추천서 필요`);
                if (sch.work_required === 1) metadataArr.push(`⚠️ 근로/의무 있음`);
                else if (sch.work_required === 0) metadataArr.push(`순수 장학금`);
                
                const metadataHtml = metadataArr.length > 0
                    ? `<div style="font-size: 0.75rem; color: #94a3b8; margin-top: 12px; font-weight: 500;">${metadataArr.join(' &nbsp;•&nbsp; ')}</div>`
                    : '';

                // 링크가 공고 직접 URL인지 확인
                const isDreamspon = sch.link && sch.link.includes("dreamspon.com");
                const linkWarningHtml = isDreamspon
                    ? `<div class="dreamspon-login-notice"><i class="fa-solid fa-lock"></i> <span>공고 페이지 로그인 필요</span></div>`
                    : '';

                // 금액 표시
                const amtDisplay = (sch.amount_est && sch.amount_est !== 500000)
                    ? `<div class="sch-detail-item"><i class="fa-solid fa-won-sign" style="color:var(--success)"></i><span>&nbsp;예상 혜택: <strong>${sch.amount_est.toLocaleString()}원</strong></span></div>`
                    : '';

                html += `
                    <div class="scholarship-card">
                        <div class="match-gauge-wrap">
                            <div class="circular-gauge" data-tooltip="match">
                                <svg viewBox="0 0 36 36">
                                    <path class="bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                                    <path class="progress" style="stroke-dashoffset: ${offset};" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                                </svg>
                                <span class="gauge-val">${sch.score}</span>
                            </div>
                            <span class="gauge-label">Match <i class="fa-solid fa-circle-info match-info-icon"></i></span>
                            <div class="match-score-tooltip">
                                <div class="match-tooltip-title">📊 MATCH 점수 구성 내역</div>
                                ${specificTooltipHtml}
                                <div class="match-tooltip-note" style="margin-top:8px;">※ 최대 점수 범위 초과 시 100으로 표시됩니다</div>
                            </div>
                        </div>
                        <div class="card-main">
                            <div class="trust-badge-row">
                                ${highlightBadge}
                                ${calculateDDay(sch.period)}
                            </div>
                            <h3 class="sch-title">${sch.title}</h3>
                            <div class="sch-detail-item">
                                <i class="fa-solid fa-calendar-days" style="color:var(--primary)"></i>
                                <span>&nbsp;신청 기간: <strong>${sch.period}</strong></span>
                            </div>
                            ${amtDisplay}
                            ${metadataHtml}
                        </div>
                        <div class="card-action">
                            ${linkWarningHtml}
                            <a href="${sch.link}" target="_blank" rel="noopener noreferrer" class="apply-btn">
                                <span>공식 공고 바로가기</span>
                                <i class="fa-solid fa-arrow-up-right-from-square"></i>
                            </a>
        </div>
                    </div>
                `;
            });
            successList.innerHTML = html;
        }

        // ──────────────────────────────────────────────
        // 6. 조건 미달 (gaps) 카드 렌더링
        // ──────────────────────────────────────────────
        if (allGaps.length === 0) {
            gapsList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🎉</div>
                    <div class="empty-title">조건 미달 공고가 없습니다!</div>
                    <div class="empty-desc">현재 설정한 프로필은 탐색 범위 내 모든 가능성 있는 장학공고 기준 최고 수준의 스펙 상태입니다!</div>
                </div>
            `;
        } else {
            let html = '';
            allGaps.forEach((sch) => {
                const gapsHtml = sch.gaps && sch.gaps.length > 0
                    ? sch.gaps.map(g => `<div>${g}</div>`).join("")
                    : '<div>ℹ️ 해당 장학금의 신청 기간이 마감되었습니다. 다음 공고를 기다려보세요.</div>';

                const isDreamspon = sch.link && sch.link.includes("dreamspon.com");
                const linkWarningHtml = isDreamspon
                    ? `<div class="dreamspon-login-notice"><i class="fa-solid fa-lock"></i> <span>공고 페이지 로그인 필요</span></div>`
                    : '';

                const isMovedFromSuccess = sch._movedFromSuccess;
                const tagLabel = isMovedFromSuccess ? '기간 마감' : '아까운 미달';
                const tagStyle = isMovedFromSuccess
                    ? 'background: rgba(239,68,68,0.08); color: #ef4444; border-color: rgba(239,68,68,0.15);'
                    : 'background: rgba(245,158,11,0.08); color: var(--warning); border-color: rgba(245,158,11,0.15);';

                html += `
                    <div class="scholarship-card gap-card">
                        <div class="card-main">
                            <div class="card-top-row">
                                <div>
                                    <span class="category-tag">${sch.category || '일반'}</span>
                                    ${calculateDDay(sch.period)}
                                </div>
                                <span class="match-score-tag" style="${tagStyle}">${tagLabel}</span>
                            </div>
                            <h3 class="sch-title">${sch.title}</h3>
                            <div class="sch-detail-item">
                                <i class="fa-solid fa-calendar-days"></i>
                                <span>&nbsp;신청 기간: <strong>${sch.period}</strong></span>
                            </div>
                            <div class="card-gaps">
                                <i class="fa-solid fa-lightbulb" style="margin-right: 6px; flex-shrink: 0;"></i>
                                <div>${gapsHtml}</div>
                            </div>
                        </div>
                        <div class="card-action">
                            ${linkWarningHtml}
                            <a href="${sch.link}" target="_blank" rel="noopener noreferrer" class="apply-btn">
                                <span>공식 공고 확인</span>
                                <i class="fa-solid fa-arrow-up-right-from-square"></i>
                            </a>
                        </div>
                    </div>
                `;
            });
            gapsList.innerHTML = html;
        }

        // Wire fresh clicks
        bindAdClicks();
    }

    // ----------------------------------------------------
    // Startup initialization & URL Restoration
    // ----------------------------------------------------
    function initFromUrl() {
        const params = new URLSearchParams(window.location.search);
        const p = params.get("p");
        if (p) {
            try {
                const decoded = JSON.parse(decodeURIComponent(atob(p)));
                // Update inputs
                gpaInput.value = decoded.gpa || "3.5";
                gpaVal.innerText = `${parseFloat(gpaInput.value).toFixed(2)} / 4.5`;
                incomeInput.value = decoded.income || "1";
                locationInput.value = decoded.location || "";
                majorInput.value = decoded.major || "";
                
                // Show shared banner and customize backModifyBtn
                window.IS_SHARED_RESULT = true;
                const banner = document.getElementById("shared-result-banner");
                if (banner) banner.style.display = "block";
                
                if (backModifyBtn) {
                    backModifyBtn.innerHTML = `<i class="fa-solid fa-house"></i> <span>나도 매칭해보기</span>`;
                }

                // Update Location button active states
                const locationBtns = document.querySelectorAll(".location-step-wrapper .grid-btn");
                locationBtns.forEach(btn => {
                    if (btn.getAttribute("data-loc") === decoded.location) {
                        btn.classList.add("active");
                    } else {
                        btn.classList.remove("active");
                    }
                });

                // Update Income button active states
                const incomeBtns = document.querySelectorAll(".income-step-wrapper .grid-btn");
                incomeBtns.forEach(btn => {
                    if (btn.getAttribute("data-val") === decoded.income) {
                        btn.classList.add("active");
                    } else {
                        btn.classList.remove("active");
                    }
                });
                
                // Immediately submit
                submitSurvey();
                showToast("공유된 장학금 매칭 결과를 불러왔습니다. ✨");
            } catch (e) {
                console.error("URL Restoration failed:", e);
            }
        }
    }

    function initPresets() {
        if (window.PRESET_REGION) {
            locationInput.value = window.PRESET_REGION;
            // Update UI
            const locationBtns = document.querySelectorAll(".location-step-wrapper .grid-btn");
            locationBtns.forEach(btn => {
                if (btn.getAttribute("data-loc") === window.PRESET_REGION) {
                    btn.classList.add("active");
                } else {
                    btn.classList.remove("active");
                }
            });
            // Automatically open stepper
            introScreen.classList.remove("active");
            surveyScreen.classList.add("active");
            currentStep = 3; // jump to region step
            updateStepperUI();
        }
        if (window.PRESET_MAJOR) {
            // Find which category this major belongs to
            let foundCategory = "공과대학";
            for (const [cat, majors] of Object.entries(ACADEMIC_MAJOR_MAP)) {
                if (majors.some(m => m.val === window.PRESET_MAJOR)) {
                    foundCategory = cat;
                    break;
                }
            }
            majorCategory.value = foundCategory;
            populateMajors();
            majorInput.value = window.PRESET_MAJOR;
            
            // Automatically open stepper
            introScreen.classList.remove("active");
            surveyScreen.classList.add("active");
            currentStep = 4; // jump to major step
            updateStepperUI();
        }
    }

    function initStats() {
        fetch("/api/stats")
            .then(res => res.json())
            .then(data => {
                const totalSchCount = document.getElementById("total-sch-count");
                const lastUpdateTime = document.getElementById("last-update-time");
                if (totalSchCount) totalSchCount.innerText = data.scholarships.total;
                if (lastUpdateTime) lastUpdateTime.innerText = `최근 분석: ${data.scholarships.last_updated}`;
            })
            .catch(err => {
                console.error("Init stats error:", err);
            });
    }

    // Exec
    populateMajors();
    initStats();
    initFromUrl();
    initPresets();
    bindAdClicks();

    // Hero stats
    fetch("/api/stats")
        .then(res => res.json())
        .then(data => {
            const heroCount = document.getElementById("hero-sch-count");
            const heroTime = document.getElementById("hero-update-time");
            if (heroCount) heroCount.innerText = data.scholarships.total + "개";
            if (heroTime) {
                const t = data.scholarships.last_updated || "";
                heroTime.innerText = t.length >= 10 ? t.substring(0, 10) : (t || "--");
            }
        })
        .catch(() => {});

    // ----------------------------------------------------
    // Notification Subscribe Logic
    // ----------------------------------------------------
    const subscribeModal = document.getElementById("subscribe-modal");
    const openSubscribeBtn = document.getElementById("open-subscribe-modal");
    const closeSubscribeBtn = document.getElementById("close-subscribe-modal");
    const subscribeForm = document.getElementById("subscribe-form");

    if (openSubscribeBtn && subscribeModal && closeSubscribeBtn) {
        openSubscribeBtn.addEventListener("click", () => {
            // Preview the conditions currently selected
            const previewEl = document.getElementById("sub-cond-preview");
            if (previewEl) {
                let currentGPA = gpaVal ? gpaVal.innerText : "입력 학점";
                let currentIncome = incomeInput ? (incomeInput.value === "모름" ? "소득모름" : incomeInput.value + "구간") : "입력 소득";
                let currentLoc = locationInput ? (locationInput.value || "전국") : "입력 지역";
                previewEl.innerText = `[${currentLoc} / ${currentIncome} / ${currentGPA}]`;
            }
            subscribeModal.classList.add("active");
        });

        closeSubscribeBtn.addEventListener("click", () => {
            subscribeModal.classList.remove("active");
        });
    }

    if (subscribeForm) {
        subscribeForm.addEventListener("submit", function(e) {
            e.preventDefault();
            const phone = document.getElementById("sub-phone").value;
            const agree = document.getElementById("sub-agree").checked;

            if (!agree) {
                showToast("개인정보 수집에 동의해주세요.");
                return;
            }

            const payload = {
                phone: phone,
                gpa: getNormalizedGPA(),
                income: incomeInput.value,
                location: locationInput.value,
                major: majorInput.value
            };

            const submitBtn = subscribeForm.querySelector("button[type='submit']");
            const originalText = submitBtn.innerText;
            submitBtn.innerText = "신청 중...";
            submitBtn.disabled = true;

            fetch("/api/subscribe", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                submitBtn.innerText = originalText;
                submitBtn.disabled = false;
                
                if (data.success) {
                    showToast("알림톡 신청이 완료되었습니다! 🎉");
                    subscribeModal.classList.remove("active");
                    subscribeForm.reset();
                } else {
                    showToast(data.message || "오류가 발생했습니다. 다시 시도해주세요.");
                }
            })
            .catch(err => {
                console.error(err);
                submitBtn.innerText = originalText;
                submitBtn.disabled = false;
                showToast("네트워크 오류가 발생했습니다.");
            });
        });
    }

    // ----------------------------------------------------
    // Bookmark (찜하기) Logic
    // ----------------------------------------------------
    window.isBookmarked = function(id) {
        let saved = JSON.parse(localStorage.getItem('saved_scholarships') || '[]');
        return saved.some(s => s.id === id);
    };

    window.toggleBookmark = function(id, title, period, link) {
        let saved = JSON.parse(localStorage.getItem('saved_scholarships') || '[]');
        const idx = saved.findIndex(s => s.id === id);
        if (idx > -1) {
            saved.splice(idx, 1);
            showToast("보관함에서 삭제되었습니다.");
        } else {
            saved.push({ id, title, period, link, savedAt: new Date().toISOString() });
            showToast("❤️ 보관함에 저장되었습니다!");
        }
        localStorage.setItem('saved_scholarships', JSON.stringify(saved));
        updateSavedBadge();
        
        // Toggle button visual state
        const btn = document.querySelector(`.scholarship-card[data-sch-id="${id}"] .bookmark-btn`);
        if (btn) {
            btn.style.color = window.isBookmarked(id) ? '#ef4444' : 'rgba(255,255,255,0.5)';
        }
    };

    function updateSavedBadge() {
        const badge = document.getElementById('saved-badge');
        if (!badge) return;
        let saved = JSON.parse(localStorage.getItem('saved_scholarships') || '[]');
        if (saved.length > 0) {
            badge.innerText = saved.length;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    }

    const openSavedBtn = document.getElementById('open-saved-btn');
    const closeSavedBtn = document.getElementById('close-saved-btn');
    const savedPanel = document.getElementById('saved-panel');
    const savedOverlay = document.getElementById('saved-panel-overlay');

    if (openSavedBtn && savedPanel) {
        openSavedBtn.addEventListener('click', () => {
            renderSavedList();
            savedPanel.style.right = '0';
            savedOverlay.style.display = 'block';
        });
        closeSavedBtn.addEventListener('click', () => {
            savedPanel.style.right = '-400px';
            savedOverlay.style.display = 'none';
        });
        savedOverlay.addEventListener('click', () => {
            savedPanel.style.right = '-400px';
            savedOverlay.style.display = 'none';
        });
    }

    function renderSavedList() {
        const listEl = document.getElementById('saved-list');
        let saved = JSON.parse(localStorage.getItem('saved_scholarships') || '[]');
        
        if (saved.length === 0) {
            listEl.innerHTML = `
                <div style="text-align: center; color: var(--text-secondary); margin-top: 50px; font-size: 0.9rem;">
                    <i class="fa-regular fa-folder-open" style="font-size: 2rem; margin-bottom: 10px; opacity: 0.5;"></i><br>
                    아직 찜한 장학금이 없습니다.
                </div>
            `;
            return;
        }

        // Sort by period roughly
        saved.sort((a, b) => a.period.localeCompare(b.period));

        let html = '';
        saved.forEach(s => {
            html += `
                <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); position: relative;">
                    <button onclick="toggleBookmark(${s.id}, '', '', '')" style="position: absolute; top: 10px; right: 10px; background: none; border: none; color: #ef4444; font-size: 1.1rem; cursor: pointer;"><i class="fa-solid fa-heart"></i></button>
                    <h4 style="font-size: 0.95rem; margin-bottom: 8px; padding-right: 20px;">${s.title}</h4>
                    <div style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 10px;"><i class="fa-regular fa-calendar"></i> ${s.period}</div>
                    <a href="${s.link}" target="_blank" style="display: inline-block; font-size: 0.8rem; background: var(--primary); color: #fff; text-decoration: none; padding: 4px 10px; border-radius: 4px;">공고 보기</a>
                </div>
            `;
        });
        listEl.innerHTML = html;
        
        // Re-bind delete buttons to update panel immediately
        listEl.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', () => setTimeout(renderSavedList, 50));
        });
    }

    updateSavedBadge();

    // ----------------------------------------------------
    // AI Eligibility Check Logic
    // ----------------------------------------------------
    const aiModal = document.getElementById('ai-modal-overlay');
    const closeAiModalBtn = document.getElementById('close-ai-modal-btn');
    const aiChatBox = document.getElementById('ai-chat-box');
    const aiControls = document.getElementById('ai-chat-controls');
    
    let currentAiQuestions = [];
    let currentQuestionIndex = 0;
    
    window.openAiCheckModal = function(schId, title) {
        if (!aiModal) return;
        aiModal.style.display = 'flex';
        aiChatBox.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 150px; gap: 15px;">
                <div class="loader-spinner" style="border-top-color: #c084fc;"></div>
                <span style="color: #cbd5e1; font-size: 0.9rem;">"${title}"<br>공고문 킬러 조건 분석 중...</span>
            </div>
        `;
        aiControls.style.display = 'none';

        fetch('/api/ai-check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: schId })
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                aiChatBox.innerHTML = `<div style="color: #f87171; text-align: center;">오류: ${data.error}</div>`;
                return;
            }
            currentAiQuestions = data.questions || [];
            currentQuestionIndex = 0;
            if (currentAiQuestions.length > 0) {
                renderNextAiQuestion();
            } else {
                aiChatBox.innerHTML = `<div style="text-align: center; color: #4ade80;">이 장학금은 별도의 까다로운 특수 조건이 없습니다!<br>기본 성적/소득 요건만 맞다면 바로 지원해보세요.</div>`;
            }
        })
        .catch(err => {
            aiChatBox.innerHTML = `<div style="color: #f87171; text-align: center;">네트워크 오류가 발생했습니다.</div>`;
        });
    };

    if (closeAiModalBtn) {
        closeAiModalBtn.addEventListener('click', () => {
            aiModal.style.display = 'none';
        });
    }

    function renderNextAiQuestion() {
        if (currentQuestionIndex >= currentAiQuestions.length) {
            // All questions answered positively!
            addChatMessage("AI", "🎉 완벽합니다! 모든 특수 자격 요건을 충족합니다. 최종 합격 확률이 매우 높으니 지금 바로 지원하세요!", "#4ade80");
            aiControls.style.display = 'none';
            return;
        }

        const q = currentAiQuestions[currentQuestionIndex];
        if (currentQuestionIndex === 0) {
            aiChatBox.innerHTML = ''; // Clear loading
        }
        
        addChatMessage("AI", q);
        aiControls.style.display = 'flex';
    }

    function addChatMessage(sender, text, color = "#fff") {
        const msgDiv = document.createElement("div");
        msgDiv.style.padding = "12px 15px";
        msgDiv.style.borderRadius = "12px";
        msgDiv.style.maxWidth = "85%";
        msgDiv.style.fontSize = "0.95rem";
        msgDiv.style.lineHeight = "1.4";
        
        if (sender === "AI") {
            msgDiv.style.background = "rgba(139, 92, 246, 0.2)";
            msgDiv.style.border = "1px solid rgba(139, 92, 246, 0.3)";
            msgDiv.style.alignSelf = "flex-start";
            msgDiv.style.color = color;
            msgDiv.innerHTML = `<i class="fa-solid fa-robot" style="margin-right: 6px; opacity: 0.7;"></i> ${text}`;
        } else {
            msgDiv.style.background = "rgba(255, 255, 255, 0.1)";
            msgDiv.style.alignSelf = "flex-end";
            msgDiv.style.color = "#e2e8f0";
            msgDiv.innerText = text;
        }
        
        aiChatBox.appendChild(msgDiv);
        aiChatBox.scrollTop = aiChatBox.scrollHeight;
    }

    document.querySelectorAll('.ai-answer-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const ans = e.target.getAttribute('data-answer');
            const ansText = ans === 'yes' ? "네, 그렇습니다." : "아니오.";
            addChatMessage("User", ansText);
            
            aiControls.style.display = 'none';
            
            setTimeout(() => {
                if (ans === 'no') {
                    addChatMessage("AI", "⚠️ 아쉽지만 해당 요건을 충족하지 못해 합격 확률이 낮습니다. 다른 장학금을 추천해 드릴게요!", "#f87171");
                } else {
                    currentQuestionIndex++;
                    renderNextAiQuestion();
                }
            }, 600);
        });
    });

});
