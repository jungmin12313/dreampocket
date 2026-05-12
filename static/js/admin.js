document.addEventListener("DOMContentLoaded", function () {
    // ----------------------------------------------------
    // DOM Elements
    // ----------------------------------------------------
    const mainRevenue = document.getElementById("main-revenue");
    const mainImpressions = document.getElementById("main-impressions");
    const mainClicks = document.getElementById("main-clicks");
    const mainCtr = document.getElementById("main-ctr");
    const mainEcpm = document.getElementById("main-ecpm");
    const mainLogFeed = document.getElementById("main-log-feed");
    const mainResetBtn = document.getElementById("main-reset-btn");

    // Live Tracking State (To compare increments)
    let previousStats = {
        impressions: 0,
        clicks: 0,
        revenue: 0
    };

    let isFirstLoad = true;

    // ----------------------------------------------------
    // Logger Helper
    // ----------------------------------------------------
    function addLogEntry(message, type = "info") {
        const li = document.createElement("li");
        li.className = "log-item";
        const now = new Date();
        const timeStr = now.toTimeString().split(" ")[0];
        
        if (type === "click") {
            li.innerHTML = `<span class="time">[${timeStr}]</span> <span class="click-event"><i class="fa-solid fa-fire"></i> <strong>${message}</strong></span>`;
        } else if (type === "impression") {
            li.innerHTML = `<span class="time">[${timeStr}]</span> <span style="color: #60a5fa;"><i class="fa-solid fa-eye"></i> ${message}</span>`;
        } else {
            li.innerHTML = `<span class="time">[${timeStr}]</span> <span>${message}</span>`;
        }
        
        mainLogFeed.insertBefore(li, mainLogFeed.firstChild);
        
        // Cap list length to 30 elements
        if (mainLogFeed.children.length > 30) {
            mainLogFeed.removeChild(mainLogFeed.lastChild);
        }
    }

    // ----------------------------------------------------
    // Stats Polling & Comparison Engine
    // ----------------------------------------------------
    function fetchAdminStats() {
        fetch("/api/stats")
            .then(res => res.json())
            .then(data => {
                const stats = data.ad_stats;
                const dbStats = data.scholarships;

                // Populate Stats
                mainRevenue.innerText = `₩${stats.revenue.toLocaleString()}`;
                mainImpressions.innerText = stats.impressions.toLocaleString();
                mainClicks.innerText = stats.clicks.toLocaleString();
                mainCtr.innerText = `${stats.ctr.toFixed(2)}%`;
                mainEcpm.innerText = `₩${stats.ecpm.toLocaleString()}`;

                if (isFirstLoad) {
                    previousStats = { ...stats };
                    isFirstLoad = false;
                    addLogEntry(`Publisher Admin session initialized. Connected to SQLite with ${dbStats.total} scholarship rules.`, "info");
                    addLogEntry(`Initial State loaded: Revenue ₩${stats.revenue.toLocaleString()}, Impressions ${stats.impressions}, Clicks ${stats.clicks}`, "info");
                    return;
                }

                // Check for Incremental updates (Smart Polling Logs)
                if (stats.impressions > previousStats.impressions) {
                    const diff = stats.impressions - previousStats.impressions;
                    addLogEntry(`Real-time traffic: +${diff} ad impression(s) detected. eCPM Revenue added (+${diff * 15} KRW).`, "impression");
                }

                if (stats.clicks > previousStats.clicks) {
                    const diffClicks = stats.clicks - previousStats.clicks;
                    const diffRev = stats.revenue - previousStats.revenue - ( (stats.impressions - previousStats.impressions) * 15 );
                    addLogEntry(`Monetization alert: Active banner click detected (+${diffClicks})! Simulated payout: +${diffRev > 0 ? diffRev : 150} KRW.`, "click");
                }

                // Update previous state reference
                previousStats = { ...stats };
            })
            .catch(err => {
                console.error("Admin stats fetching error:", err);
                addLogEntry("Connection warning: Failed to poll statistics from Flask backend.", "warning");
            });
    }

    // ----------------------------------------------------
    // Action Events
    // ----------------------------------------------------
    mainResetBtn.addEventListener("click", function () {
        if (confirm("정말로 모든 가상 광고 수익 및 노출 로그를 공장 초기화하시겠습니까?")) {
            fetch("/api/ad-reset", { method: "POST" })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        const stats = data.ad_stats;
                        previousStats = { ...stats };
                        
                        mainRevenue.innerText = "₩0";
                        mainImpressions.innerText = "0";
                        mainClicks.innerText = "0";
                        mainCtr.innerText = "0.00%";
                        mainEcpm.innerText = "₩0";
                        
                        mainLogFeed.innerHTML = "";
                        addLogEntry("System admin command: Monetization metrics successfully wiped and reset to 0.", "info");
                    }
                });
        }
    });

    // ----------------------------------------------------
    // Start Polling Engine
    // ----------------------------------------------------
    fetchAdminStats();
    // Poll stats every 2 seconds
    setInterval(fetchAdminStats, 2000);
});
