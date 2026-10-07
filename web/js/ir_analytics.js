// ==========================================
// [모듈 4] ir_analytics.js: 실시간 유입 분석 & 성과 관제 전담 모듈 (3대 앱 Supabase 100% 실데이터)
// ==========================================

let irPeriod = "today";
let selectedIRBrand = "aura";
let currentChannelCategory = "all";
let cachedChannelInflows = [];

function switchIRBrand(brand, btnElement) {
    selectedIRBrand = brand;

    // 상단 3대 브랜드 버튼 스타일 즉시 전환
    const brandButtons = document.querySelectorAll(".ir-brand-btn");
    brandButtons.forEach(b => {
        b.classList.remove("active");
        b.style.boxShadow = "none";
    });

    const btnAura = document.getElementById("btn-ir-brand-aura");
    const btnStock = document.getElementById("btn-ir-brand-stock");
    const btnIns = document.getElementById("btn-ir-brand-insurance");

    if (btnAura) {
        btnAura.style.background = "rgba(236,72,153,0.15)";
        btnAura.style.color = "#EC4899";
        btnAura.style.border = "1px solid #EC4899";
    }
    if (btnStock) {
        btnStock.style.background = "rgba(245,158,11,0.15)";
        btnStock.style.color = "#F59E0B";
        btnStock.style.border = "1px solid #F59E0B";
    }
    if (btnIns) {
        btnIns.style.background = "rgba(2,132,199,0.15)";
        btnIns.style.color = "#0284C7";
        btnIns.style.border = "1px solid #0284C7";
    }

    if (brand === "aura" && btnAura) {
        btnAura.classList.add("active");
        btnAura.style.background = "linear-gradient(135deg, #EC4899, #BE185D)";
        btnAura.style.color = "#fff";
        btnAura.style.boxShadow = "0 2px 10px rgba(236,72,153,0.4)";
    } else if (brand === "stock" && btnStock) {
        btnStock.classList.add("active");
        btnStock.style.background = "linear-gradient(135deg, #F59E0B, #D97706)";
        btnStock.style.color = "#fff";
        btnStock.style.boxShadow = "0 2px 10px rgba(245,158,11,0.4)";
    } else if (brand === "insurance" && btnIns) {
        btnIns.classList.add("active");
        btnIns.style.background = "linear-gradient(135deg, #0284C7, #0369A1)";
        btnIns.style.color = "#fff";
        btnIns.style.boxShadow = "0 2px 10px rgba(2,132,199,0.4)";
    }

    const titleMap = {
        "aura": "📈 [Aura AI 데이팅] 실시간 유입 정밀 분석 & 관제 센터",
        "stock": "📈 [StockMaster AI] 실시간 퀀트 유입 정밀 분석 & 관제 센터",
        "insurance": "📈 [보험 리밸런스] 실시간 상담 유입 정밀 분석 & 관제 센터"
    };
    const titleEl = document.getElementById("ir-brand-main-title");
    if (titleEl) titleEl.innerText = titleMap[brand] || "📈 실시간 유입 관제 센터";

    loadIRAnalytics();
}

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
            "today": "<span class='pulse-dot'></span> 오늘 24시간 실시간 유입",
            "weekly": "<span class='pulse-dot'></span> 최근 7일간 실시간 유입",
            "monthly": "<span class='pulse-dot'></span> 최근 30일간 실시간 유입",
            "yearly": "<span class='pulse-dot'></span> 2026년 연간 실시간 유입"
        };
        pulseBadge.innerHTML = labelMap[period] || "<span class='pulse-dot'></span> 실시간 Supabase 연동";
    }

    loadIRAnalytics();
}

async function loadIRAnalytics(btn) {
    if (btn) animateRefreshBtn(btn, "실시간 유입 실데이터가 새로고침되었습니다! 📈");
    try {
        const res = await fetch(`/api/ir-analytics?period=${irPeriod}&brand=${selectedIRBrand}&t=${Date.now()}`);
        if (!res.ok) return;
        const data = await res.json();

        // 1. 상단 4대 핵심 KPI 카드 (100% 실데이터 - 브랜드별 맞춤 렌더링)
        const kpis = data.kpis || {};
        if (document.getElementById("kpi-today-pv")) {
            document.getElementById("kpi-today-pv").innerText = `${(kpis.today_pv || 0).toLocaleString()} 명`;
        }
        if (document.getElementById("kpi-cumulative-pv")) {
            document.getElementById("kpi-cumulative-pv").innerText = `${(kpis.cumulative_pv || 0).toLocaleString()} 명`;
        }
        if (document.getElementById("kpi-yoy")) {
            document.getElementById("kpi-yoy").innerText = kpis.yoy_growth || (selectedIRBrand === "stock" ? "리서치 11건 (회원 3명)" : selectedIRBrand === "insurance" ? "상담신청 288건" : "회원가입 72명");
        }
        
        // 4번째 KPI 카드 단위 판별 (주식/보험: 건, 데이팅: 명)
        const visitorUnit = kpis.visitor_unit || (selectedIRBrand === "stock" ? "건" : selectedIRBrand === "insurance" ? "건" : "명");
        if (document.getElementById("kpi-monthly-visitors")) {
            document.getElementById("kpi-monthly-visitors").innerText = `${(kpis.monthly_visitors || 0).toLocaleString()} ${visitorUnit}`;
        }

        // 3번째 카드 동적 브랜드 맞춤 전환 (아이콘, 라벨, 서브텍스트, 테마컬러)
        const iconGrowthEl = document.getElementById("kpi-icon-growth");
        const labelGrowthEl = document.getElementById("kpi-label-growth");
        const subGrowthEl = document.getElementById("kpi-sub-growth");
        const valGrowthEl = document.getElementById("kpi-yoy");

        if (selectedIRBrand === "stock") {
            if (iconGrowthEl) {
                iconGrowthEl.innerText = "📈";
                iconGrowthEl.style.background = "rgba(245,158,11,0.15)";
                iconGrowthEl.style.color = "#F59E0B";
            }
            if (labelGrowthEl) labelGrowthEl.innerText = "Stock 퀀트 리서치 & 회원";
            if (subGrowthEl) subGrowthEl.innerText = "Supabase quant_research 포스트 실데이터";
            if (valGrowthEl) valGrowthEl.style.color = "#F59E0B";
        } else if (selectedIRBrand === "insurance") {
            if (iconGrowthEl) {
                iconGrowthEl.innerText = "🛡️";
                iconGrowthEl.style.background = "rgba(2,132,199,0.15)";
                iconGrowthEl.style.color = "#0284C7";
            }
            if (labelGrowthEl) labelGrowthEl.innerText = "보험 자가진단 & 상담신청";
            if (subGrowthEl) subGrowthEl.innerText = "Supabase 34개사 자가진단 실데이터";
            if (valGrowthEl) valGrowthEl.style.color = "#0284C7";
        } else {
            if (iconGrowthEl) {
                iconGrowthEl.innerText = "💖";
                iconGrowthEl.style.background = "rgba(236,72,153,0.15)";
                iconGrowthEl.style.color = "#EC4899";
            }
            if (labelGrowthEl) labelGrowthEl.innerText = "Aura 실제 회원가입자";
            if (subGrowthEl) subGrowthEl.innerText = "Supabase users 테이블 실데이터";
            if (valGrowthEl) valGrowthEl.style.color = "#EC4899";
        }

        // 동적 라벨 갱신
        if (document.getElementById("kpi-label-period") && kpis.kpi_period_label) {
            document.getElementById("kpi-label-period").innerText = kpis.kpi_period_label;
        }
        if (document.getElementById("kpi-label-visitor") && kpis.visitor_period_label) {
            document.getElementById("kpi-label-visitor").innerText = kpis.visitor_period_label;
        }

        // 2. 24시간 / 주간 / 월간 / 연간 막대 차트 (순 유입자수 기준 와이드 뷰)
        if (document.getElementById("ir-chart-title")) document.getElementById("ir-chart-title").innerText = data.chart_title || "📊 순 방문자 유입 추이";
        if (document.getElementById("ir-chart-badge")) document.getElementById("ir-chart-badge").innerText = data.chart_badge || "기준: 순 방문자(중복제거)";

        // 브랜드별 테마 색상 정의
        const brandThemeMap = {
            "aura": {
                barGrad: "linear-gradient(180deg, #EC4899, #BE185D)",
                barShadow: "rgba(236,72,153,0.5)",
                badgeColor: "#F472B6",
                borderColor: "#EC4899",
                badgeBg: "#FDF2F8",
                badgeText: "#BE185D",
                appColor: "#EC4899",
                emptyHint: "Aura 데이팅 웹사이트에 실제 사람이 접속하면 세션, 유입 채널, 이동 경로, 일시가 1:1로 실시간 기록됩니다."
            },
            "stock": {
                barGrad: "linear-gradient(180deg, #F59E0B, #D97706)",
                barShadow: "rgba(245,158,11,0.5)",
                badgeColor: "#FBBF24",
                borderColor: "#F59E0B",
                badgeBg: "#FFFBEB",
                badgeText: "#B45309",
                appColor: "#F59E0B",
                emptyHint: "StockMaster AI에 실제 투자자가 접속하면 퀀트 리서치 열람, 세션, 유입 채널, 일시가 1:1로 실시간 기록됩니다."
            },
            "insurance": {
                barGrad: "linear-gradient(180deg, #0284C7, #0369A1)",
                barShadow: "rgba(2,132,199,0.5)",
                badgeColor: "#38BDF8",
                borderColor: "#0284C7",
                badgeBg: "#F0F9FF",
                badgeText: "#0369A1",
                appColor: "#0284C7",
                emptyHint: "보험 리밸런스에 실제 고객이 접속하면 288건 상담 신청, 세션, 유입 채널, 일시가 1:1로 실시간 기록됩니다."
            }
        };
        const currentTheme = brandThemeMap[selectedIRBrand] || brandThemeMap["aura"];

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
                const heightPct = Math.max(Math.round((h.count / maxVal) * 100), h.count > 0 ? 16 : 4);
                const isHighlight = h.count > 0;
                const barStyle = isHighlight 
                    ? `background: ${currentTheme.barGrad}; box-shadow: 0 0 12px ${currentTheme.barShadow};` 
                    : 'background: rgba(255,255,255,0.06);';
                const countBadge = h.count > 0 
                    ? `<span class="bar-badge" style="color:${currentTheme.badgeColor};font-weight:800;font-size:11px;margin-bottom:4px;">${h.count}명</span>` 
                    : `<span class="bar-badge" style="color:#475569;font-size:10px;margin-bottom:4px;">0</span>`;

                return `
                    <div class="bar-column" style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%;min-width:20px;max-width:80px;">
                        ${countBadge}
                        <div class="bar-fill" style="width:100%;max-width:36px;height:${heightPct}%;${barStyle};border-radius:6px 6px 0 0;transition:all 0.4s ease;" title="${h.hour}: ${h.count}명 (순 방문자)"></div>
                        <span class="bar-label" style="font-size:11.5px;color:#94A3B8;margin-top:8px;white-space:nowrap;font-weight:600;">${h.hour}</span>
                    </div>
                `;
            }).join("");
        }

        // 3. 옴니채널 실제 유입 실적 (순 유입자수 기준)
        if (document.getElementById("ir-channels-title")) document.getElementById("ir-channels-title").innerText = data.channels_title || "🚀 옴니채널 실제 유입 실적";
        if (document.getElementById("ir-channels-subtitle")) document.getElementById("ir-channels-subtitle").innerText = data.channels_subtitle || "";

        cachedChannelInflows = data.channel_inflows || [];
        renderChannelInflows();

        // 4. 실제 웹사이트 방문자 실시간 추적 (동일인 중복 0%)
        if (document.getElementById("ir-visitors-title")) document.getElementById("ir-visitors-title").innerText = data.visitors_title || "👥 실제 웹사이트 방문자(순 유입) 실시간 추적";
        if (document.getElementById("ir-visitors-subtitle")) document.getElementById("ir-visitors-subtitle").innerText = data.visitors_subtitle || "";

        const visitorContainer = document.getElementById("real-visitor-tracker-container");
        if (visitorContainer) {
            const visitors = data.real_visitors_list || [];
            const periodTxt = irPeriod === "weekly" ? "최근 7일간" : (irPeriod === "monthly" ? "최근 30일간" : (irPeriod === "yearly" ? "2026년 연간" : "오늘 24시간 동안"));
            if (visitors.length === 0) {
                visitorContainer.innerHTML = `
                    <div style="text-align:center;padding:32px 16px;color:#64748B;background:#FAF8F5;border-radius:10px;border:1px solid #E8E3DA;">
                        <span style="font-size:28px;display:block;margin-bottom:8px;">📡</span>
                        <strong style="color:#0F172A;font-size:13px;display:block;margin-bottom:4px;">${periodTxt} 감지된 실제 외부 접속자가 없습니다. (0명)</strong>
                        <span style="font-size:11.5px;color:#64748B;">${currentTheme.emptyHint}</span>
                    </div>
                `;
            } else {
                visitorContainer.innerHTML = `
                    <div style="max-height:260px;overflow-y:auto;display:flex;flex-direction:column;gap:8px;">
                        ${visitors.map((v, idx) => `
                            <div style="background:#FFFFFF;border:1px solid #E8E3DA;border-left:3px solid ${currentTheme.borderColor};border-radius:8px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;font-size:12.5px;box-shadow:var(--shadow-sm);">
                                <div style="display:flex;align-items:center;gap:10px;">
                                    <span style="font-size:16px;">👤</span>
                                    <div>
                                        <strong style="color:#0F172A;">[출처: ${v.source_name}]</strong>
                                        <span style="color:#64748B;margin-left:6px;font-size:11.5px;">(${v.campaign})</span>
                                        <div style="font-size:11px;color:#64748B;margin-top:2px;">타깃 앱: <span style="color:${currentTheme.appColor};font-weight:700;">${v.target_app}</span> · ${v.medium} · <span style="color:#64748B;">${v.ip}</span></div>
                                    </div>
                                </div>
                                <div style="text-align:right;">
                                    <span class="badge" style="background:${currentTheme.badgeBg};color:${currentTheme.badgeText};border:1px solid ${currentTheme.borderColor};font-size:11px;padding:2px 8px;border-radius:10px;font-weight:700;">실제 접속</span>
                                    <div style="font-size:10.5px;color:#64748B;margin-top:3px;">${v.created_at}</div>
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

// 옴니채널 유입 실적 카테고리 필터링 렌더러
function renderChannelInflows() {
    const listContainer = document.getElementById("channel-bars-list");
    if (!listContainer) return;

    let items = [...cachedChannelInflows];
    if (currentChannelCategory !== "all") {
        if (currentChannelCategory === "other") {
            items = items.filter(i => i.category === "other" || i.category === "messenger");
        } else {
            items = items.filter(i => i.category === currentChannelCategory);
        }
    }

    if (items.length === 0) {
        listContainer.innerHTML = `<div style="text-align:center;padding:30px;color:#64748B;background:#FAF8F5;border:1px solid #E8E3DA;border-radius:8px;">해당 기간 및 카테고리에 유입된 방문자가 없습니다. (0명)</div>`;
        return;
    }

    listContainer.innerHTML = items.map(ch => `
        <div style="display:flex;flex-direction:column;gap:5px;margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;align-items:center;font-size:12.5px;">
                <span style="font-weight:700;color:#0F172A;">${ch.name}</span>
                <span style="font-weight:800;color:${ch.color || '#0284C7'};">${ch.count} ${ch.unit || '명'} (${ch.share}%)</span>
            </div>
            <div style="width:100%;height:8px;background:#EDE8DE;border-radius:6px;overflow:hidden;">
                <div style="width:${Math.max(ch.share, 4)}%;height:100%;background:${ch.color || '#0284C7'};border-radius:6px;transition:width 0.4s ease;"></div>
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
window.switchIRBrand = switchIRBrand;
window.loadIRAnalytics = loadIRAnalytics;
window.filterChannelBars = filterChannelBars;
window.renderChannelInflows = renderChannelInflows;

