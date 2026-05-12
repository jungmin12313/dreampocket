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

    // Step 1: GPA Range display updater
    gpaInput.addEventListener("input", function () {
        gpaVal.innerText = `${parseFloat(gpaInput.value).toFixed(2)} / 4.5`;
    });

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
        surveyScreen.classList.remove("active");
        analysisLoaderScreen.classList.add("active");

        // Prepare match request data
        const payload = {
            gpa: gpaInput.value,
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
    backModifyBtn.addEventListener("click", function () {
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
        // Reserved for future monetization integrations
    }

    // ----------------------------------------------------
    // Dynamic Listings Rendering
    // ----------------------------------------------------
    function renderResults(results) {
        const successes = results.success_matches || [];
        const gaps = results.gap_matches || [];

        // Update counts
        successBadge.innerText = successes.length;
        gapsBadge.innerText = gaps.length;

        // Render success matches
        if (successes.length === 0) {
            successList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">😢</div>
                    <div class="empty-title">매칭된 우수 장학금이 없습니다</div>
                    <div class="empty-desc">조건에 딱 맞는 공고가 모집 전이거나 마감되었습니다. 소득 기준이나 거주지 정보를 조정하여 다시 분석해 보세요.</div>
                </div>
            `;
        } else {
            let html = "";
            successes.forEach((sch, idx) => {
                const reasonsHtml = sch.reasons.map(r => `<span class="reason-badge">✓ ${r}</span>`).join("");
                html += `
                    <div class="scholarship-card">
                        <div class="card-main">
                            <div class="card-top-row">
                                <span class="category-tag">${sch.category || '일반'}</span>
                                <span class="match-score-tag">매칭 점수: ${sch.score}점</span>
                            </div>
                            <h3 class="sch-title">${sch.title}</h3>
                            <div class="sch-detail-item">
                                <i class="fa-solid fa-calendar-days"></i>
                                <span>&nbsp;신청 기간: <strong>${sch.period}</strong></span>
                            </div>
                            <div class="card-reasons">
                                ${reasonsHtml}
                            </div>
                        </div>
                        <div class="card-action">
                            <a href="${sch.link}" target="_blank" class="apply-btn">
                                <span>공고 보기</span>
                                <i class="fa-solid fa-arrow-up-right-from-square"></i>
                            </a>
                        </div>
                    </div>
                `;
            });
            successList.innerHTML = html;
        }

        // Render gap matches
        if (gaps.length === 0) {
            gapsList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🎉</div>
                    <div class="empty-title">조건 미달 공고가 없습니다!</div>
                    <div class="empty-desc">현재 설정한 프로필은 탐색 범위 내 모든 가능성 있는 장학공고 기준 최고 수준의 스펙 상태입니다!</div>
                </div>
            `;
        } else {
            let html = "";
            gaps.forEach((sch) => {
                const gapsHtml = sch.gaps.map(g => `<div>${g}</div>`).join("");
                html += `
                    <div class="scholarship-card gap-card">
                        <div class="card-main">
                            <div class="card-top-row">
                                <span class="category-tag">${sch.category || '일반'}</span>
                                <span class="match-score-tag" style="background: rgba(245,158,11,0.08); color: var(--warning); border-color: rgba(245,158,11,0.15);">아까운 미달</span>
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
                            <a href="${sch.link}" target="_blank" class="apply-btn">
                                <span>요강 분석</span>
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
    // Startup initialization
    // ----------------------------------------------------
    function initStats() {
        fetch("/api/stats")
            .then(res => res.json())
            .then(data => {
                totalSchCount.innerText = data.scholarships.total;
                lastUpdateTime.innerText = `최근 분석: ${data.scholarships.last_updated}`;
            })
            .catch(err => {
                console.error("Init stats error:", err);
                lastUpdateTime.innerText = "DB 연결 대기중";
            });
    }

    // Exec
    populateMajors();
    initStats();
    bindAdClicks();

    // Hero 섹션 실제 공고 수 연동
    fetch("/api/stats")
        .then(res => res.json())
        .then(data => {
            const heroCount = document.getElementById("hero-sch-count");
            const heroTime = document.getElementById("hero-update-time");
            if (heroCount) heroCount.innerText = data.scholarships.total + "개";
            if (heroTime) {
                // 최근 업데이트 시간 간략 표시 (날짜만)
                const t = data.scholarships.last_updated || "";
                heroTime.innerText = t.length >= 10 ? t.substring(0, 10) : (t || "--");
            }
        })
        .catch(() => {
            const heroCount = document.getElementById("hero-sch-count");
            if (heroCount) heroCount.innerText = "--";
        });
});
