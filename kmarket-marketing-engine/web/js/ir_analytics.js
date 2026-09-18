// ==========================================
// [모듈 4] ir_analytics.js: 실시간 유입 분석 & IR 관제 전담 모듈 (100% 순수 실데이터)
// ==========================================

let irPeriod = "today"; // today(시간별), daily(날짜별), weekly(주간별), monthly(월별), yearly(년도별)
let irBrand = "all";    // all(전체통합), kmarket, easytax
let irChartMode = "visitor"; // visitor(실제 유입자 수), marketing(콘텐츠 배포 수)
let irVisitorCategory = "all";
let cachedIRData = null;

// 1. 기간 선택 핸들러 (시간별, 날짜별, 주간별, 월별, 년도별)
function switchPeriod(period, btnElement) {
    irPeriod = period;
    
    // 버튼 UI 활성화 상태 전환
    const buttons = document.querySelectorAll(".period-button-group .period-btn");
    buttons.forEach(b => b.classList.remove("active"));
    if (btnElement) {
        btnElement.classList.add("active");
    } else {
        const targetBtn = document.querySelector(`.period-btn[onclick*="${period}"]`);
        if (targetBtn) targetBtn.classList.add("active");
    }

    // 상단 라이브 펄스 배지 텍스트 실시간 전환
    const pulseBadge = document.getElementById("ir-live-pulse-badge");
    if (pulseBadge) {
        const labelMap = {
            "today": "<span class='pulse-dot'></span> 오늘 24시간 시간별 실시간",
            "daily": "<span class='pulse-dot'></span> 최근 14일 날짜별 실시간",
            "weekly": "<span class='pulse-dot'></span> 최근 8주 주간별 실시간",
            "monthly": "<span class='pulse-dot'></span> 2026년 1~12월 월별 실시간",
            "yearly": "<span class='pulse-dot'></span> 2024~2027 연도별(IR) 실시간"
        };
        pulseBadge.innerHTML = labelMap[period] || "<span class='pulse-dot'></span> 실시간 DB 연동";
    }

    loadIRAnalytics();
}

// 2. IR 전용 브랜드 스위처 (전체 통합 / K-Market / EasyTax)
function switchIRBrand(brand, btnElement) {
    irBrand = brand;

    const brandBtns = document.querySelectorAll(".ir-brand-btn");
    brandBtns.forEach(b => {
        b.classList.remove("active");
        b.style.background = "transparent";
        b.style.color = "#94A3B8";
    });

    if (btnElement) {
        btnElement.classList.add("active");
        if (brand === "kmarket") {
            btnElement.style.background = "#7C3AED";
            btnElement.style.color = "#FFFFFF";
        } else if (brand === "easytax") {
            btnElement.style.background = "linear-gradient(135deg, #F59E0B, #D97706)";
            btnElement.style.color = "#FFFFFF";
        } else {
            btnElement.style.background = "#3B82F6";
            btnElement.style.color = "#FFFFFF";
        }
    }

    loadIRAnalytics();
}

// 3. 차트 모드 전환 (실제 유입자 수 vs 콘텐츠 배포 수)
function switchChartMode(mode, btnElement) {
    irChartMode = mode;
    const vBtn = document.getElementById("chart-mode-visitor");
    const mBtn = document.getElementById("chart-mode-marketing");

    if (vBtn && mBtn) {
        if (mode === "visitor") {
            vBtn.style.background = "#10B981";
            vBtn.style.color = "#FFFFFF";
            mBtn.style.background = "transparent";
            mBtn.style.color = "#94A3B8";
        } else {
            mBtn.style.background = "#8B5CF6";
            mBtn.style.color = "#FFFFFF";
            vBtn.style.background = "transparent";
            vBtn.style.color = "#94A3B8";
        }
    }

    if (cachedIRData) {
        renderBarChart();
    }
}

// 4. 메인 데이터 로더
async function loadIRAnalytics(btn) {
    if (btn) animateRefreshBtn(btn, "실시간 유입자 & IR 관제 실데이터 갱신 완료! 📈");
    try {
        const res = await fetch(`/api/ir-analytics?period=${irPeriod}&brand=${irBrand}&t=${Date.now()}`);
        if (!res.ok) return;
        const data = await res.json();
        cachedIRData = data;

        // 4-1. 6대 핵심 KPI 카드 렌더링
        const kpis = data.kpis || {};
        const pLabel = data.period_label || "선택 기간";

        const labelVis = document.getElementById("kpi-label-period-visitors");
        if (labelVis) labelVis.innerText = `${pLabel} 실제 유입자`;

        const valVis = document.getElementById("kpi-period-visitors");
        if (valVis) valVis.innerText = `${(kpis.period_visitors || 0).toLocaleString()} 명`;

        const kmVis = document.getElementById("kpi-km-visitors");
        if (kmVis) kmVis.innerText = `${(kpis.km_visitors || 0).toLocaleString()} 명`;

        const taxVis = document.getElementById("kpi-tax-visitors");
        if (taxVis) taxVis.innerText = `${(kpis.tax_visitors || 0).toLocaleString()} 명`;

        const topCh = document.getElementById("kpi-top-channel");
        if (topCh) topCh.innerText = kpis.top_channel || "실시간 집계 중";

        const topCo = document.getElementById("kpi-top-country");
        if (topCo) topCo.innerText = kpis.top_country || "17개국 분산";

        const cumPv = document.getElementById("kpi-cumulative-pv");
        if (cumPv) cumPv.innerText = `${(kpis.cumulative_pv || 0).toLocaleString()} 건`;

        // 4-2. 차트 제목 및 배지
        const chartTitle = document.getElementById("ir-chart-title");
        if (chartTitle) chartTitle.innerText = data.chart_title || "📊 유입 및 배포 추이";

        const chartBadge = document.getElementById("ir-chart-badge");
        if (chartBadge) chartBadge.innerText = data.chart_badge || `기준: ${data.brand_name_kr} 실데이터`;

        // 4-3. 막대 차트 렌더링
        renderBarChart();

        // 4-4. 10대 채널 실시간 랭킹 렌더링
        renderChannelRankings(data.channel_rankings || []);

        // 4-5. 17개국 국가별 유입 분포 렌더링
        renderCountryDistribution(data.country_distribution || []);

        // 4-6. 실제 방문자 라이브 피드 렌더링
        renderLiveVisitors();

    } catch (e) {
        console.error("IR Analytics load error:", e);
    }
}

// 5. 5단 기간별 정밀 막대그래프 렌더러
function renderBarChart() {
    if (!cachedIRData) return;
    const barChartContainer = document.getElementById("hourly-bar-chart");
    if (!barChartContainer) return;

    const chartList = irChartMode === "visitor" 
        ? (cachedIRData.visitor_chart_data || cachedIRData.hourly_data || [])
        : (cachedIRData.marketing_chart_data || []);

    const maxVal = Math.max(...chartList.map(h => h.count || 0), 1);
    const brand = cachedIRData.brand || "all";

    barChartContainer.style.display = "flex";
    barChartContainer.style.width = "100%";
    barChartContainer.style.justifyContent = "space-around";
    barChartContainer.style.alignItems = "flex-end";
    barChartContainer.style.height = "180px";
    barChartContainer.style.padding = "10px 10px 0 10px";
    barChartContainer.style.gap = "6px";
    barChartContainer.style.minWidth = chartList.length > 14 ? "800px" : (chartList.length > 7 ? "550px" : "100%");

    barChartContainer.innerHTML = chartList.map(h => {
        const heightPct = Math.max(Math.round((h.count / maxVal) * 100), h.count > 0 ? 14 : 4);
        const isHighlight = h.count > 0;

        let barColor = 'background: rgba(255,255,255,0.06);';
        let badgeColor = '#475569';

        if (isHighlight) {
            if (irChartMode === "visitor") {
                if (brand === "kmarket") {
                    barColor = 'background: linear-gradient(180deg, #10B981, #059669); box-shadow: 0 0 12px rgba(16,185,129,0.4);';
                    badgeColor = '#34D399';
                } else if (brand === "easytax") {
                    barColor = 'background: linear-gradient(180deg, #F59E0B, #D97706); box-shadow: 0 0 12px rgba(245,158,11,0.4);';
                    badgeColor = '#FBBF24';
                } else {
                    barColor = 'background: linear-gradient(180deg, #38BDF8, #2563EB); box-shadow: 0 0 12px rgba(56,189,248,0.4);';
                    badgeColor = '#38BDF8';
                }
            } else {
                barColor = 'background: linear-gradient(180deg, #A78BFA, #7C3AED); box-shadow: 0 0 12px rgba(167,139,250,0.4);';
                badgeColor = '#C4B5FD';
            }
        }

        const countBadge = `<span class="bar-badge" style="color:${badgeColor};font-weight:800;font-size:11px;margin-bottom:4px;">${h.count}</span>`;
        const unit = irChartMode === "visitor" ? "명" : "건";

        return `
            <div class="bar-column" style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%;min-width:18px;max-width:70px;">
                ${countBadge}
                <div class="bar-fill" style="width:100%;max-width:32px;height:${heightPct}%;${barColor};border-radius:6px 6px 0 0;transition:all 0.4s ease;cursor:pointer;" title="${h.label || h.hour}: ${h.count}${unit}"></div>
                <span class="bar-label" style="font-size:11px;color:#94A3B8;margin-top:8px;white-space:nowrap;font-weight:600;">${h.label || h.hour}</span>
            </div>
        `;
    }).join("");
}

// 6. 10대 채널별 실시간 랭킹 렌더러 (기간 및 브랜드 100% 동기화)
function renderChannelRankings(rankings) {
    const container = document.getElementById("channel-rankings-container");
    if (!container) return;

    const pLabel = cachedIRData ? (cachedIRData.period_label || "선택 기간") : "실시간";
    const bName = cachedIRData ? (cachedIRData.brand_name_kr || "전체 브랜드") : "전체";

    // 헤더 타이틀 및 배지 동적 업데이트
    const titleElem = document.getElementById("ir-channels-ranking-title");
    const subElem = document.getElementById("ir-channels-ranking-subtitle");
    const badgeElem = document.getElementById("ir-channels-ranking-badge");

    if (titleElem) titleElem.innerText = `🚀 [${bName}] 10대 채널별 유입 랭킹 (${pLabel})`;
    if (subElem) subElem.innerText = `${pLabel} 동안 [${bName}] 플랫폼별 실제 접속자 점유율`;
    if (badgeElem) badgeElem.innerText = `${pLabel} 실데이터`;

    if (!rankings || rankings.length === 0) {
        container.innerHTML = `
            <div style="text-align:center; padding:28px 12px; color:#64748B; font-size:12px; background:#090C19; border-radius:8px; border:1px dashed #1E2442;">
                <span style="font-size:20px; display:block; margin-bottom:4px;">📡</span>
                <strong>${pLabel} 동안 감지된 [${bName}] 유입 채널이 없습니다. (0건)</strong>
            </div>
        `;
        return;
    }

    container.innerHTML = rankings.map(ch => `
        <div style="background:#090C19; border:1px solid #1E2442; border-radius:8px; padding:8px 12px; display:flex; flex-direction:column; gap:4px;">
            <div style="display:flex; justify-content:space-between; align-items:center; font-size:12px;">
                <div style="display:flex; align-items:center; gap:6px;">
                    <span style="font-size:14px;">${ch.icon}</span>
                    <strong style="color:#F8FAFC;">${ch.name}</strong>
                </div>
                <span style="font-weight:800; color:${ch.color}; font-size:12px;">${ch.count}명 (${ch.share}%)</span>
            </div>
            <div style="width:100%; height:5px; background:rgba(255,255,255,0.06); border-radius:4px; overflow:hidden;">
                <div style="width:${Math.max(ch.share, 4)}%; height:100%; background:${ch.color}; border-radius:4px; transition:width 0.4s ease;"></div>
            </div>
        </div>
    `).join("");
}

// 7. 17개국 글로벌 국가별 유입 분포 렌더러 (기간 및 브랜드 100% 동기화)
function renderCountryDistribution(countries) {
    const container = document.getElementById("country-distribution-container");
    if (!container) return;

    const pLabel = cachedIRData ? (cachedIRData.period_label || "선택 기간") : "실시간";
    const bName = cachedIRData ? (cachedIRData.brand_name_kr || "전체 브랜드") : "전체";

    // 헤더 타이틀 및 배지 동적 업데이트
    const titleElem = document.getElementById("ir-country-dist-title");
    const subElem = document.getElementById("ir-country-dist-subtitle");
    const badgeElem = document.getElementById("ir-country-dist-badge");

    if (titleElem) titleElem.innerText = `🌐 [${bName}] 17개국 글로벌 국가별 유입 분포 (${pLabel})`;
    if (subElem) subElem.innerText = `${pLabel} 동안 [${bName}] 외국인 타깃 국가별 실시간 유입 비중`;
    if (badgeElem) badgeElem.innerText = `${pLabel} 17개국`;

    if (!countries || countries.length === 0) {
        container.innerHTML = `
            <div style="text-align:center; padding:28px 12px; color:#64748B; font-size:12px; background:#090C19; border-radius:8px; border:1px dashed #1E2442;">
                <span style="font-size:20px; display:block; margin-bottom:4px;">🌍</span>
                <strong>${pLabel} 동안 감지된 [${bName}] 타깃 국가 유입이 없습니다. (0명)</strong>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap:6px;">
            ${countries.map(c => `
                <div style="background:#090C19; border:1px solid #1E2442; border-radius:8px; padding:6px 10px; display:flex; justify-content:space-between; align-items:center; font-size:11.5px;">
                    <div style="display:flex; align-items:center; gap:5px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                        <span style="font-size:14px;">${c.flag}</span>
                        <span style="color:#CBD5E1; font-weight:600;">${c.country}</span>
                    </div>
                    <strong style="color:#34D399; font-size:11px; margin-left:4px;">${c.count}명 (${c.share || 0}%)</strong>
                </div>
            `).join("")}
        </div>
    `;
}

// 8. 초정밀 실시간 라이브 피드 렌더러 (K-Market & EasyTax 100% 독립 분리)
function renderLiveVisitors() {
    const container = document.getElementById("real-visitor-tracker-container");
    if (!container || !cachedIRData) return;

    const searchInput = document.getElementById("visitor-search-input");
    const query = searchInput ? searchInput.value.toLowerCase().trim() : "";
    const pLabel = cachedIRData.period_label || "오늘 24시간 동안";

    const titleElem = document.getElementById("ir-visitors-title");
    const subtitleElem = document.getElementById("ir-visitors-subtitle");

    // 브랜드별 전용 타이틀 및 설명문 동적 업데이트
    if (irBrand === "kmarket") {
        if (titleElem) titleElem.innerHTML = `🛒 [K-Market] 실제 웹사이트 방문자(UTM 유입) 실시간 추적 (${pLabel})`;
        if (subtitleElem) subtitleElem.innerText = `배포된 링크를 클릭하고 [K-Market]에 실제로 접속한 진짜 사람의 ${pLabel} 실시간 기록입니다. (실물 매물 탐색 & 다국어 번역 채팅)`;
    } else if (irBrand === "easytax") {
        if (titleElem) titleElem.innerHTML = `💰 [EasyTax] 국세청 세무 환급 신청 & 감면 실시간 추적 (${pLabel})`;
        if (subtitleElem) subtitleElem.innerText = `조특법 90% 감면 및 3.3% 환급 모의계산을 완료하고 [EasyTax]에 신청서를 접수한 실제 신청자 실시간 기록입니다.`;
    } else {
        if (titleElem) titleElem.innerHTML = `🌐 [K-Market & EasyTax] 듀얼 브랜드 실시간 유입 & 환급 신청 통합 피드 (${pLabel})`;
        if (subtitleElem) subtitleElem.innerText = `[K-Market] 실시간 방문자와 [EasyTax] 국세청 환급 신청자를 완벽히 분리하여 1:1 실시간 기록합니다.`;
    }

    const filterFn = (list) => {
        let items = list || [];
        if (irVisitorCategory !== "all") {
            items = items.filter(v => (v.source_name || "").toLowerCase().includes(irVisitorCategory.toLowerCase()));
        }
        if (query) {
            items = items.filter(v => 
                (v.country || "").toLowerCase().includes(query) ||
                (v.source_name || "").toLowerCase().includes(query) ||
                (v.campaign || "").toLowerCase().includes(query) ||
                (v.ip || "").toLowerCase().includes(query) ||
                (v.target_app || "").toLowerCase().includes(query) ||
                (v.action_stage || "").toLowerCase().includes(query)
            );
        }
        return items;
    };

    const renderCard = (v) => {
        const isKM = (v.brand || "").toLowerCase() === "kmarket";
        const bBg = isKM ? "rgba(124, 58, 237, 0.2)" : "rgba(245, 158, 11, 0.2)";
        const bCol = isKM ? "#C4B5FD" : "#FDE68A";
        const bBorder = isKM ? "#7C3AED" : "#F59E0B";
        const bIcon = v.brand_icon || (isKM ? "🛒" : "💰");
        const bLabel = v.brand_label || (isKM ? "K-Market" : "EasyTax");
        const actionCol = isKM ? "#34D399" : "#FBBF24";

        return `
            <div style="background:#090C19; border:1px solid #1E2442; border-left:4px solid ${bBorder}; border-radius:10px; padding:12px 14px; display:flex; justify-content:space-between; align-items:center; font-size:12.5px; transition:background 0.2s;" onmouseover="this.style.background='#13172E'" onmouseout="this.style.background='#090C19'">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:22px;">${v.channel_icon || "🔗"}</span>
                    <div>
                        <div style="display:flex; align-items:center; gap:8px; margin-bottom:3px; flex-wrap:wrap;">
                            <span style="background:${bBg}; color:${bCol}; border:1px solid ${bBorder}; font-size:11px; padding:1px 7px; border-radius:6px; font-weight:800;">
                                ${bIcon} ${bLabel}
                            </span>
                            <strong style="color:#F8FAFC; font-size:13px;">[출처: ${v.source_name}]</strong>
                            <span style="color:#38BDF8; font-size:12px; font-weight:700;">${v.lang_label || v.country || "글로벌"}</span>
                            <span style="color:#94A3B8; font-size:11.5px;">(${v.campaign})</span>
                        </div>
                        <div style="font-size:11.5px; color:#64748B; display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                            <span>목적지: <strong style="color:#A78BFA;">${v.target_app}</strong></span>
                            <span>·</span>
                            <span style="color:${actionCol}; font-weight:700;">⚡ ${v.action_stage || "접속 완료"}</span>
                            <span>·</span>
                            <span>상태: <span style="color:#CBD5E1;">${v.ip}</span></span>
                        </div>
                    </div>
                </div>
                <div style="text-align:right; min-width:130px;">
                    <span class="badge" style="background:${isKM ? 'rgba(16,185,129,0.15)' : 'rgba(245,158,11,0.15)'}; color:${isKM ? '#34D399' : '#FBBF24'}; font-size:11px; padding:3px 8px; border-radius:10px; font-weight:800; border:1px solid ${isKM ? 'rgba(16,185,129,0.3)' : 'rgba(245,158,11,0.3)'};">
                        ${isKM ? '🟢 실제 방문' : '💰 환급 신청 접수'}
                    </span>
                    <div style="font-size:11px; color:#94A3B8; margin-top:4px;">${v.created_at}</div>
                </div>
            </div>
        `;
    };

    // 1. 전체 브랜드 통합 모드 (K-Market 패널과 EasyTax 패널 듀얼 렌더링)
    if (irBrand === "all") {
        const kmList = filterFn(cachedIRData.km_visitors_list || []);
        const taxList = filterFn(cachedIRData.tax_visitors_list || []);

        container.innerHTML = `
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
                <!-- 좌측: K-Market 전용 실시간 방문자 -->
                <div style="background:#090C19; border:1px solid #1E2442; border-radius:12px; padding:16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; padding-bottom:8px; border-bottom:1px solid #1E2442;">
                        <div style="display:flex; align-items:center; gap:6px;">
                            <span style="font-size:18px;">🛒</span>
                            <strong style="color:#A78BFA; font-size:14px;">K-Market 실시간 웹 방문자</strong>
                        </div>
                        <span class="badge" style="background:rgba(124,58,237,0.2); color:#C4B5FD; font-size:11px; padding:2px 8px; border-radius:6px; font-weight:700;">
                            ${kmList.length}명 감지됨
                        </span>
                    </div>
                    <div style="max-height:340px; overflow-y:auto; display:flex; flex-direction:column; gap:8px;">
                        ${kmList.length === 0 ? `
                            <div style="text-align:center; padding:24px 8px; color:#64748B; font-size:12px;">
                                ${pLabel} 동안 감지된 K-Market 유입자가 없습니다.
                            </div>
                        ` : kmList.map(v => renderCard(v)).join("")}
                    </div>
                </div>

                <!-- 우측: EasyTax 전용 실시간 환급 신청자 -->
                <div style="background:#090C19; border:1px solid #1E2442; border-radius:12px; padding:16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; padding-bottom:8px; border-bottom:1px solid #1E2442;">
                        <div style="display:flex; align-items:center; gap:6px;">
                            <span style="font-size:18px;">💰</span>
                            <strong style="color:#FBBF24; font-size:14px;">EasyTax 실시간 환급 신청자</strong>
                        </div>
                        <span class="badge" style="background:rgba(245,158,11,0.2); color:#FDE68A; font-size:11px; padding:2px 8px; border-radius:6px; font-weight:700;">
                            ${taxList.length}명 접수됨
                        </span>
                    </div>
                    <div style="max-height:340px; overflow-y:auto; display:flex; flex-direction:column; gap:8px;">
                        ${taxList.length === 0 ? `
                            <div style="text-align:center; padding:24px 8px; color:#64748B; font-size:12px;">
                                ${pLabel} 동안 감지된 EasyTax 환급 신청자가 없습니다.
                            </div>
                        ` : taxList.map(v => renderCard(v)).join("")}
                    </div>
                </div>
            </div>
        `;
        return;
    }

    // 2. 단일 브랜드 선택 모드 (K-Market 단독 또는 EasyTax 단독)
    const targetList = irBrand === "kmarket" 
        ? filterFn(cachedIRData.km_visitors_list || cachedIRData.real_visitors_list || [])
        : filterFn(cachedIRData.tax_visitors_list || cachedIRData.real_visitors_list || []);

    if (targetList.length === 0) {
        const brandKr = irBrand === "kmarket" ? "K-Market" : "EasyTax";
        container.innerHTML = `
            <div style="text-align:center; padding:36px 16px; color:#64748b; background:#090C19; border-radius:12px; border:1px solid #1E2442;">
                <span style="font-size:32px; display:block; margin-bottom:8px;">📡</span>
                <strong style="color:#94A3B8; font-size:14px; display:block; margin-bottom:4px;">${pLabel} 동안 감지된 [${brandKr}] 실시간 유입자가 없습니다. (0명)</strong>
                <span style="font-size:12px; color:#64748b;">마케팅 봇이 배포한 링크를 통해 실제 사람이 접속하면 1:1로 실시간 기록됩니다.</span>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div style="max-height:360px; overflow-y:auto; display:flex; flex-direction:column; gap:8px;">
            ${targetList.map(v => renderCard(v)).join("")}
        </div>
    `;
}

// 9. 라이브 피드 검색 및 카테고리 필터 이벤트 핸들러
function filterLiveVisitors() {
    renderLiveVisitors();
}

function filterVisitorCategory(cat, btnElement) {
    irVisitorCategory = cat;
    const tabs = document.querySelectorAll("#tab-ir-analytics .filter-tab");
    tabs.forEach(t => t.classList.remove("active"));
    if (btnElement) btnElement.classList.add("active");
    renderLiveVisitors();
}

// 글로벌 바인딩
window.switchPeriod = switchPeriod;
window.switchIRBrand = switchIRBrand;
window.switchChartMode = switchChartMode;
window.loadIRAnalytics = loadIRAnalytics;
window.filterLiveVisitors = filterLiveVisitors;
window.filterVisitorCategory = filterVisitorCategory;
