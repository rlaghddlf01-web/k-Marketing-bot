// ==========================================
// [모듈 4] ir_analytics.js: 실시간 유입 분석 & IR 관제 전담 모듈 (100% 순수 실데이터)
// ==========================================

let irPeriod = "today";
let currentChannelCategory = "all";
let cachedChannelInflows = [];

function switchPeriod(period, btnElement) {
    irPeriod = period;
    
    // 버튼 UI 활성화 상태 즉시 전환
    const buttons = document.querySelectorAll(".period-btn");
    buttons.forEach(b => b.classList.remove("active"));
    if (btnElement) {
        btnElement.classList.add("active");
    } else {
        const targetBtn = document.querySelector(`.period-btn[onclick*="${period}"]`);
        if (targetBtn) targetBtn.classList.add("active");
    }

    // 상단 라이브 펄스 배지 텍스트 실시간 전환
    const pulseBadge = document.querySelector(".badge-live-pulse");
    if (pulseBadge) {
        const labelMap = {
            "today": "<span class='pulse-dot'></span> 오늘 24시간 실시간",
            "weekly": "<span class='pulse-dot'></span> 최근 7일간 실시간",
            "monthly": "<span class='pulse-dot'></span> 최근 30일간 실시간",
            "yearly": "<span class='pulse-dot'></span> 2026년 연간 실시간"
        };
        pulseBadge.innerHTML = labelMap[period] || "<span class='pulse-dot'></span> 실시간 DB 연동";
    }

    loadIRAnalytics();
}

async function loadIRAnalytics(btn) {
    if (btn) animateRefreshBtn(btn, "IR 관제 실데이터가 새로고침되었습니다! 📈");
    try {
        const res = await fetch(`/api/ir-analytics?period=${irPeriod}&brand=${currentBrand}&t=${Date.now()}`);
        if (!res.ok) return;
        const data = await res.json();

        // 1. 상단 4대 핵심 KPI 카드 (100% 실데이터)
        const kpis = data.kpis || {};
        if (document.getElementById("kpi-today-pv")) {
            document.getElementById("kpi-today-pv").innerText = `${(kpis.today_pv || 0).toLocaleString()} 건`;
        }
        if (document.getElementById("kpi-cumulative-pv")) {
            document.getElementById("kpi-cumulative-pv").innerText = `${(kpis.cumulative_pv || 0).toLocaleString()} 건`;
        }
        if (document.getElementById("kpi-yoy")) {
            document.getElementById("kpi-yoy").innerText = kpis.yoy_growth || "100% 실시간 DB 연동";
        }
        if (document.getElementById("kpi-monthly-visitors")) {
            document.getElementById("kpi-monthly-visitors").innerText = `${(kpis.monthly_visitors || 0).toLocaleString()} 명`;
        }

        // 2. 24시간 / 주간 / 월간 / 연간 막대 차트 (전체 폭 100% 균등 분배 와이드 뷰)
        if (document.getElementById("ir-chart-title")) document.getElementById("ir-chart-title").innerText = data.chart_title || "📊 콘텐츠 배포 추이";
        if (document.getElementById("ir-chart-badge")) document.getElementById("ir-chart-badge").innerText = data.chart_badge || "기준: 실시간 DB";

        const barChartContainer = document.getElementById("hourly-bar-chart");
        if (barChartContainer && data.hourly_data) {
            const maxVal = Math.max(...data.hourly_data.map(h => h.count || 0), 1);
            
            barChartContainer.style.display = "flex";
            barChartContainer.style.width = "100%";
            barChartContainer.style.justifyContent = "space-around";
            barChartContainer.style.alignItems = "flex-end";
            barChartContainer.style.height = "160px";
            barChartContainer.style.padding = "10px 10px 0 10px";
            barChartContainer.style.gap = "8px";
            barChartContainer.style.minWidth = data.hourly_data.length > 12 ? "700px" : "100%";

            barChartContainer.innerHTML = data.hourly_data.map(h => {
                const heightPct = Math.max(Math.round((h.count / maxVal) * 100), h.count > 0 ? 14 : 4);
                const isHighlight = h.count > 0;
                const barStyle = isHighlight 
                    ? 'background: linear-gradient(180deg, #10B981, #059669); box-shadow: 0 0 12px rgba(16,185,129,0.5);' 
                    : 'background: rgba(255,255,255,0.06);';
                const countBadge = h.count > 0 
                    ? `<span class="bar-badge" style="color:#34D399;font-weight:800;font-size:11px;margin-bottom:4px;">${h.count}</span>` 
                    : `<span class="bar-badge" style="color:#475569;font-size:10px;margin-bottom:4px;">0</span>`;

                return `
                    <div class="bar-column" style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%;min-width:20px;max-width:80px;">
                        ${countBadge}
                        <div class="bar-fill" style="width:100%;max-width:36px;height:${heightPct}%;${barStyle};border-radius:6px 6px 0 0;transition:all 0.4s ease;" title="${h.hour}: ${h.count}건"></div>
                        <span class="bar-label" style="font-size:11.5px;color:#94A3B8;margin-top:8px;white-space:nowrap;font-weight:600;">${h.hour}</span>
                    </div>
                `;
            }).join("");
        }

        // 3. 옴니채널 실제 콘텐츠 제작·송출 실적 (기간별 + 카테고리별 실시간 반영)
        if (document.getElementById("ir-channels-title")) document.getElementById("ir-channels-title").innerText = data.channels_title || "🚀 옴니채널 실제 배포 실적";
        if (document.getElementById("ir-channels-subtitle")) document.getElementById("ir-channels-subtitle").innerText = data.channels_subtitle || "";

        cachedChannelInflows = data.channel_inflows || [];
        renderChannelInflows();

        // 4. 실제 웹사이트 방문자(UTM 유입) 실시간 추적 (가짜 목록 0%)
        if (document.getElementById("ir-visitors-title")) document.getElementById("ir-visitors-title").innerText = data.visitors_title || "👥 실제 웹사이트 방문자(UTM 유입) 실시간 추적";
        if (document.getElementById("ir-visitors-subtitle")) document.getElementById("ir-visitors-subtitle").innerText = data.visitors_subtitle || "";

        const visitorContainer = document.getElementById("real-visitor-tracker-container");
        if (visitorContainer) {
            const visitors = data.real_visitors_list || [];
            const periodTxt = irPeriod === "weekly" ? "최근 7일간" : (irPeriod === "monthly" ? "최근 30일간" : (irPeriod === "yearly" ? "2026년 연간" : "오늘 24시간 동안"));
            if (visitors.length === 0) {
                visitorContainer.innerHTML = `
                    <div style="text-align:center;padding:32px 16px;color:#64748b;background:#090C19;border-radius:10px;border:1px solid #1E2442;">
                        <span style="font-size:28px;display:block;margin-bottom:8px;">📡</span>
                        <strong style="color:#94A3B8;font-size:13px;display:block;margin-bottom:4px;">${periodTxt} 감지된 실제 외부 접속자가 없습니다. (0명)</strong>
                        <span style="font-size:11.5px;color:#64748b;">마케팅 봇이 배포한 링크(/track?utm_source=...)를 통해 실제 사람이 접속하면 IP, 출처, 일시가 1:1로 실시간 기록됩니다.</span>
                    </div>
                `;
            } else {
                visitorContainer.innerHTML = `
                    <div style="max-height:260px;overflow-y:auto;display:flex;flex-direction:column;gap:8px;">
                        ${visitors.map((v, idx) => `
                            <div style="background:#090C19;border:1px solid #1E2442;border-left:3px solid #10B981;border-radius:8px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;font-size:12.5px;">
                                <div style="display:flex;align-items:center;gap:10px;">
                                    <span style="font-size:16px;">👤</span>
                                    <div>
                                        <strong style="color:#F8FAFC;">[출처: ${v.source_name}]</strong>
                                        <span style="color:#94A3B8;margin-left:6px;font-size:11.5px;">(캠페인: ${v.campaign})</span>
                                        <div style="font-size:11px;color:#64748b;margin-top:2px;">목적지: <span style="color:#A78BFA;">${v.target_app}</span> · IP: <span style="color:#CBD5E1;">${v.ip}</span></div>
                                    </div>
                                </div>
                                <div style="text-align:right;">
                                    <span class="badge" style="background:rgba(16,185,129,0.15);color:#34D399;font-size:11px;padding:2px 8px;border-radius:10px;font-weight:700;">실제 접속</span>
                                    <div style="font-size:10.5px;color:#94A3B8;margin-top:3px;">${v.created_at}</div>
                                </div>
                            </div>
                        `).join("")}
                    </div>
                `;
            }
        }

    } catch (e) {
        console.error("IR Analytics load error:", e);
    }
}

// 옴니채널 실적 카테고리 필터링 렌더러
function renderChannelInflows() {
    const listContainer = document.getElementById("channel-bars-list");
    if (!listContainer) return;

    let items = [...cachedChannelInflows];
    if (currentChannelCategory !== "all") {
        items = items.filter(i => i.category === currentChannelCategory);
    }

    if (items.length === 0) {
        listContainer.innerHTML = `<div style="text-align:center;padding:30px;color:#64748b;background:#090C19;border-radius:8px;">해당 기간 및 카테고리에 발행된 콘텐츠가 없습니다. (0건)</div>`;
        return;
    }

    listContainer.innerHTML = items.map(ch => `
        <div style="display:flex;flex-direction:column;gap:5px;margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;align-items:center;font-size:12.5px;">
                <span style="font-weight:700;color:#F8FAFC;">${ch.name}</span>
                <span style="font-weight:800;color:#38BDF8;">${ch.count} 건 (${ch.share}%)</span>
            </div>
            <div style="width:100%;height:8px;background:rgba(255,255,255,0.06);border-radius:6px;overflow:hidden;">
                <div style="width:${Math.max(ch.share, 4)}%;height:100%;background:${ch.color};border-radius:6px;transition:width 0.4s ease;"></div>
            </div>
        </div>
    `).join("");
}

// 채널 카테고리 필터 탭 클릭 핸들러
function filterChannelBars(category, btn) {
    currentChannelCategory = category;
    document.querySelectorAll(".channel-filter-tabs .filter-tab").forEach(b => b.classList.remove("active"));
    if (btn) btn.classList.add("active");
    renderChannelInflows();
}

window.switchPeriod = switchPeriod;
window.loadIRAnalytics = loadIRAnalytics;
window.filterChannelBars = filterChannelBars;
window.renderChannelInflows = renderChannelInflows;
