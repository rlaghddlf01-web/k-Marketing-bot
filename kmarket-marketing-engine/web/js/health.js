// ==========================================
// [모듈 5] health.js: 헬스케어 & 맥박 관제 전담 모듈
// ==========================================

async function loadHealthStatus(btn) {
    if (btn) animateRefreshBtn(btn, "시스템 맥박이 새로고침되었습니다! 🩺");
    try {
        const res = await fetch("/api/health");
        const data = await res.json();

        const isKM = currentBrand === "kmarket";
        const panelTitle = document.getElementById("health-panel-title");
        const panelDesc = document.getElementById("health-panel-desc");
        if (panelTitle) {
            panelTitle.innerText = isKM ? "🩺 [K-Market 전담] 실시간 헬스케어 & 맥박 관제 센터" : "🩺 [EasyTax 전담] 국세청 세무 헬스케어 & 맥박 관제 센터";
        }
        if (panelDesc) {
            panelDesc.innerText = isKM
                ? "270개 실물 매물 0원 나눔 숏폼, 17개국 텔레그램, 페이스북 50만 그룹 등 K-Market 8대 전용 채널의 맥박을 실시간 감시합니다."
                : "조특법 90% 소득세 감면, D-2 알바 3.3% 환급, Anti-Ban 공인 세무 등 EasyTax 8대 전용 채널의 맥박을 실시간 감시합니다.";
        }

        const headerBadge = document.getElementById("header-health-score");
        if (headerBadge) {
            headerBadge.innerText = `${data.health_score || 100}% ${data.overall_status === 'healthy' ? '정상 🟢' : '주의 🟡'}`;
        }

        // 🧠 핵심 두뇌 카드
        const brainGrid = document.getElementById("health-brain-grid");
        if (brainGrid && data.brain) {
            const brainItems = [
                {
                    name: isKM ? "K-Market Gemini 생성 엔진" : "EasyTax 조특법 법률 AI 엔진",
                    icon: "🧠",
                    status: data.brain.gemini_ai?.status || "ok",
                    message: isKM ? "0원 나눔 실물 매물 카피 생성 엔진 가동" : "국세청 팩트 법률 & 세무 카피 엔진 가동",
                    ping: data.brain.gemini_ai?.ping_ms || 120
                },
                {
                    name: isKM ? "K-Market 무인 자율주행 봇" : "EasyTax 세금환급 무인 전담 봇",
                    icon: "🐍",
                    status: isKM ? (isKMarketRunning ? "ok" : "idle") : (isEasyTaxRunning ? "ok" : "idle"),
                    message: isKM 
                        ? (isKMarketRunning ? "24시간 0원 나눔 봇 회전 중 🟢" : "K-Market 봇 대기 중")
                        : (isEasyTaxRunning ? "24시간 세무 환급 봇 회전 중 🟢" : "EasyTax 봇 대기 중")
                },
                {
                    name: isKM ? "Supabase (kmarket_golden_copies)" : "Supabase (easytax_golden_copies)",
                    icon: "🗄️",
                    status: data.brain.supabase_db?.status || "ok",
                    message: isKM ? "K-Market S등급 골든카피 테이블 연동" : "EasyTax S등급 세무카피 테이블 연동"
                }
            ];

            brainGrid.innerHTML = brainItems.map(b => {
                const isOk = b.status === "ok";
                const badgeColor = isOk ? "background:rgba(16,185,129,0.15);color:#34d399;" : "background:rgba(245,158,11,0.15);color:#fbbf24;";
                const statusText = isOk ? "🟢 정상 맥박" : "⚪ 대기/로컬모드";
                const topBorder = isKM ? "#10b981" : "#f59e0b";

                return `
                    <div class="stat-card" style="border-top: 3px solid ${topBorder};">
                        <div class="stat-icon ${isKM ? 'green' : 'gold'}">${b.icon}</div>
                        <div class="stat-info" style="width:100%;">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <span class="stat-label">${b.name}</span>
                                <span style="${badgeColor}padding:2px 8px;border-radius:10px;font-size:11px;font-weight:700;">${statusText}</span>
                            </div>
                            <h3 class="stat-value" style="font-size:13px;color:#f8fafc;margin:6px 0;">${b.message}</h3>
                            ${b.ping ? `<span style="font-size:11px;color:var(--text-secondary);">⚡ 핑 응답속도: ${b.ping} ms</span>` : ''}
                        </div>
                    </div>
                `;
            }).join("");
        }

        // 📡 8대 채널 맥박
        const channelsGrid = document.getElementById("health-channels-grid");
        const targetChannels = isKM ? data.kmarket_channels : data.easytax_channels;

        if (channelsGrid && targetChannels) {
            channelsGrid.innerHTML = Object.entries(targetChannels).map(([k, ch]) => {
                const isOk = ch.status === "ok";
                const borderCol = isOk ? (isKM ? "#10b981" : "#f59e0b") : "rgba(255,255,255,0.1)";
                const badgeStyle = isOk ? "background:rgba(16,185,129,0.15);color:#34d399;" : "background:rgba(245,158,11,0.15);color:#fbbf24;";
                const badgeLabel = isOk ? "🟢 정상 가동" : "🟡 대기 중";
                const countColor = isKM ? "#34d399" : "#fbbf24";

                return `
                    <div class="action-card" style="border-top:3px solid ${borderCol};">
                        <div class="action-header">
                            <span class="action-emoji">${ch.icon}</span>
                            <div style="width:100%;">
                                <div style="display:flex;justify-content:space-between;align-items:center;">
                                    <h4>${ch.name}</h4>
                                    <span style="${badgeStyle}padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;">${badgeLabel}</span>
                                </div>
                                <p style="margin-top:4px;font-size:11px;color:#94a3b8;">${ch.api_type}</p>
                            </div>
                        </div>
                        <div style="font-size:11px;color:var(--text-secondary);margin:8px 0;background:rgba(255,255,255,0.02);padding:6px;border-radius:6px;">
                            💡 <strong>맥박 진단:</strong> ${ch.diagnostic}
                        </div>
                        <div style="font-size:11px;color:${countColor};">
                            📊 오늘 처리: ${ch.daily_count}건 • ${ch.last_published}
                        </div>
                    </div>
                `;
            }).join("");
        }
    } catch (e) {
        console.error("Health status load error:", e);
    }
}

async function runFullHealthDiagnostic() {
    appendLog("[Diagnosis] 전체 시스템 1초 정밀 자가진단 실행 중...", "info");
    showToast("시스템 전체 자가진단을 시작합니다...");
    try {
        const res = await fetch("/api/health/run-diagnostic", { method: "POST" });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Success] ${data.message}`, "success");
            showToast(data.message);
            loadHealthStatus();
        }
    } catch (e) {
        appendLog(`[Error] 자가진단 요청 통신 실패: ${e}`, "error");
    }
}

window.loadHealthStatus = loadHealthStatus;
window.runFullHealthDiagnostic = runFullHealthDiagnostic;
