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
        total: 0
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
        
        if (type === "system") {
            li.innerHTML = `<span class="time">[${timeStr}]</span> <span style="color: #60a5fa;"><i class="fa-solid fa-server"></i> ${message}</span>`;
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
                const dbStats = data.scholarships;

                // Populate Stats
                if (mainRevenue) mainRevenue.innerText = dbStats.total;
                if (mainImpressions) mainImpressions.innerText = dbStats.last_updated;
                if (mainClicks) mainClicks.innerText = "정상 작동 중";
                if (mainCtr) mainCtr.innerText = "Connected";
                if (mainEcpm) mainEcpm.innerText = "0 errors";

                if (isFirstLoad) {
                    previousStats = { ...dbStats };
                    isFirstLoad = false;
                    addLogEntry(`Admin session initialized. Connected to SQLite with ${dbStats.total} scholarship rules.`, "info");
                    return;
                }

                // Check for Incremental updates (Smart Polling Logs)
                if (dbStats.total > previousStats.total) {
                    const diff = dbStats.total - previousStats.total;
                    addLogEntry(`Real-time update: +${diff} new scholarships processed.`, "system");
                }

                // Update previous state reference
                previousStats = { ...dbStats };
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
        if (confirm("DB 데이터 크롤링을 수동으로 재요청하시겠습니까? (이 작업은 시스템 리소스를 소모합니다)")) {
            addLogEntry("System admin command: Force refresh triggered.", "info");
            fetch("/api/admin/refresh", { method: "POST" })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        addLogEntry(`Refresh completed: ${data.message}`, "system");
                    } else {
                        addLogEntry(`Refresh failed: ${data.error}`, "warning");
                    }
                })
                .catch(err => {
                    addLogEntry("Force refresh request failed.", "warning");
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
