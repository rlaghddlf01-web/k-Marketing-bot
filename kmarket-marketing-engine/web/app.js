// 상태 관리
let currentBrand = "kmarket";
let isKMarketRunning = false;
let isEasyTaxRunning = false;
let logHistory = [];

// 🔄 모든 새로고침 버튼 공통 회전 애니메이션 & 토스트 헬퍼
function animateRefreshBtn(btn, successMsg = "최신 데이터로 새로고침되었습니다! 🔄") {
    if (!btn) return;
    const origHtml = btn.innerHTML;
    btn.innerHTML = `<span class="spin-icon" style="display:inline-block;animation:rotateSpin 0.6s linear infinite;">🔄</span> 갱신 중...`;
    btn.classList.add("btn-spinning");
    setTimeout(() => {
        btn.innerHTML = origHtml;
        btn.classList.remove("btn-spinning");
        if (successMsg) showToast(successMsg);
    }, 600);
}

// 1. 대시보드 오버뷰 새로고침
function refreshOverview(btn) {
    animateRefreshBtn(btn, "대시보드 활동 로그와 상태가 새로고침되었습니다! 📊");
    fetchStatus();
    renderActionGrid();
}

// DOM 요소 로드
document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    renderActionGrid();
    fetchStatus();
    loadPlatforms();
    loadGallery();
    loadGoldenCopies();
    loadSettings();

    // 3초마다 상태 주기적 업데이트
    setInterval(fetchStatus, 3000);
});

// 탭 전환
function initTabs() {
    const navItems = document.querySelectorAll(".nav-item");
    const tabContents = document.querySelectorAll(".tab-content");

    navItems.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");

            navItems.forEach(i => i.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));

            btn.classList.add("active");
            document.getElementById(`tab-${targetTab}`).classList.add("active");

            if (targetTab === "overview") renderActionGrid();
            if (targetTab === "ir-analytics") loadIRAnalytics();
            if (targetTab === "platforms") loadPlatforms();
            if (targetTab === "hashtags") loadHashtags();
            if (targetTab === "gallery") loadGallery();
            if (targetTab === "self-learning") loadGoldenCopies();
            if (targetTab === "health") loadHealthStatus();
        });
    });
}

function switchTabDirect(tabName) {
    const btn = document.querySelector(`.nav-item[data-tab="${tabName}"]`);
    if (btn) btn.click();
}

// 1. 브랜드 전환 스위처 (kmarket ↔ easytax) 100% 완전 분리
function switchBrand(brand) {
    currentBrand = brand;
    const btnKM = document.getElementById("brand-tab-km");
    const btnTax = document.getElementById("brand-tab-tax");
    const pageTitle = document.getElementById("page-title");
    const pageDesc = document.getElementById("page-desc");
    const seasonName = document.getElementById("season-name");

    if (brand === "kmarket") {
        btnKM.style.background = "#7C3AED";
        btnKM.style.borderColor = "transparent";
        btnKM.style.color = "#FFFFFF";
        btnKM.style.boxShadow = "0 4px 14px rgba(124, 58, 237, 0.45)";

        btnTax.style.background = "#13172E";
        btnTax.style.borderColor = "#22294E";
        btnTax.style.color = "#94A3B8";
        btnTax.style.boxShadow = "none";

        pageTitle.innerHTML = "📊 K-Market 100% 라이프 & 0원 나눔 제어 센터";
        pageDesc.innerText = "270개 실물 매물 0원 나눔, 무빙세일, 17개국 양방향 번역 채팅을 100% 전담 제어합니다.";
        seasonName.innerText = "K-MARKET (100% 전력질주)";
        seasonName.style.color = "#FF6B35";
        document.getElementById("google-index-count").innerText = "1,105개 K-Market 대학/공단 URL 가동";
        document.getElementById("stat-seo-count").innerText = "1,105 개 (K-Market)";
    } else {
        btnTax.style.background = "linear-gradient(135deg, #FBBF24, #F59E0B, #D97706)";
        btnTax.style.borderColor = "#FDE68A";
        btnTax.style.color = "#FFFFFF";
        btnTax.style.boxShadow = "0 4px 18px rgba(245, 158, 11, 0.5)";

        btnKM.style.background = "#13172E";
        btnKM.style.borderColor = "#22294E";
        btnKM.style.color = "#94A3B8";
        btnKM.style.boxShadow = "none";

        pageTitle.innerHTML = "💰 EasyTax (KTRS) 100% 세무 환급 제어 센터";
        pageDesc.innerText = "조특법 90% 소득세 감면, D-2 알바 3.3% 환급, 5개년 경정청구를 100% 전담 제어합니다.";
        seasonName.innerText = "EASYTAX (100% 전력질주)";
        seasonName.style.color = "#FACC15";
        document.getElementById("google-index-count").innerText = "5,525개 EasyTax 세무 URL 가동";
        document.getElementById("stat-seo-count").innerText = "5,525 개 (EasyTax)";
    }

    renderActionGrid();
    loadPlatforms();
    loadHashtags();
    loadGallery();
    loadGoldenCopies();
    loadIRAnalytics();
    loadHealthStatus();
}

// 2. 대시보드 원클릭 모듈 패널 100% 브랜드별 동적 렌더링
function renderActionGrid() {
    const container = document.getElementById("action-grid-container");
    const panelTitle = document.getElementById("action-panel-title");
    const panelDesc = document.getElementById("action-panel-desc");
    if (!container) return;

    if (currentBrand === "kmarket") {
        panelTitle.innerText = "⚡ K-Market 전담 모듈 원클릭 즉시 실행";
        panelDesc.innerText = "270개 실물 매물 기반 0원 나눔 숏폼, 실물 카드뉴스, 중고 가구 레딧 헌터를 즉시 실행합니다.";

        container.innerHTML = `
            <div class="action-card" style="border-top:3px solid #FF6B35;">
                <div class="action-header">
                    <span class="action-emoji">🎬</span>
                    <div>
                        <h4>0원 나눔 실물 숏폼 팩토리</h4>
                        <p>270개 실매물 사진 + 17개국 음성 TTS 렌더링</p>
                    </div>
                </div>
                <button class="btn btn-action" onclick="runModule('kmarket_shorts')">🛒 숏폼 일괄 렌더링</button>
            </div>

            <div class="action-card" style="border-top:3px solid #FF6B35;">
                <div class="action-header">
                    <span class="action-emoji">📸</span>
                    <div>
                        <h4>실물 매물 4장 카드뉴스</h4>
                        <p>0원 나눔 & 무빙세일 꿀매물 캐러셀 생성</p>
                    </div>
                </div>
                <button class="btn btn-action" onclick="runModule('kmarket_cardnews')">🛒 카드뉴스 생성</button>
            </div>

            <div class="action-card" style="border-top:3px solid #FF6B35;">
                <div class="action-header">
                    <span class="action-emoji">🤖</span>
                    <div>
                        <h4>가구/생활용품 레딧 헌터</h4>
                        <p>r/korea 중고 질문 감지 & 0원 나눔 안내</p>
                    </div>
                </div>
                <button class="btn btn-action" onclick="runModule('kmarket_reddit')">🛒 레딧 스캔 & 답변</button>
            </div>

            <div class="action-card" style="border-top:3px solid #FF6B35;">
                <div class="action-header">
                    <span class="action-emoji">🎁</span>
                    <div>
                        <h4>0원 나눔 데일리 브리핑</h4>
                        <p>매일 아침 17개국 0원 매물 텔레그램 발송</p>
                    </div>
                </div>
                <button class="btn btn-action" onclick="runModule('kmarket_briefing')">🛒 브리핑 발송</button>
            </div>

            <div class="action-card" style="border-top:3px solid #FF6B35;">
                <div class="action-header">
                    <span class="action-emoji">👥</span>
                    <div>
                        <h4>페이스북 50만 그룹 침투기</h4>
                        <p>재한 외국인 대형 그룹 첫 댓글 링크 스텔스</p>
                    </div>
                </div>
                <button class="btn btn-action" onclick="runModule('kmarket_fb_groups')">🛒 페북 그룹 배포</button>
            </div>

            <div class="action-card" style="border-top:3px solid #FF6B35;">
                <div class="action-header">
                    <span class="action-emoji">🌐</span>
                    <div>
                        <h4>WordPress & Medium 글로벌 SEO 블로그</h4>
                        <p>17개국어 0원 나눔 1,500자 장문 SEO 칼럼 자동 발행</p>
                    </div>
                </div>
                <button class="btn btn-action" onclick="runModule('kmarket_blog')">🛒 WordPress / Medium 칼럼 발행</button>
            </div>

            <div class="action-card" style="border-top:3px solid #FF6B35;">
                <div class="action-header">
                    <span class="action-emoji">🌐</span>
                    <div>
                        <h4>대학/공단 K-Market SEO</h4>
                        <p>전국 65개 거점 × 17개 언어 1,105개 캠퍼스 색인</p>
                    </div>
                </div>
                <button class="btn btn-action" onclick="triggerGoogleIndex()">🛒 구글봇 색인 핑 전송</button>
            </div>

            <div class="action-card" style="border-top:3px solid #FF6B35;">
                <div class="action-header">
                    <span class="action-emoji">📄</span>
                    <div>
                        <h4>외국인 생존 가이드북 PDF</h4>
                        <p>중고/0원나눔/원룸 이사 가이드북 렌더링</p>
                    </div>
                </div>
                <button class="btn btn-action" onclick="runModule('kmarket_pdf')">🛒 PDF 가이드 렌더링</button>
            </div>
        `;
    } else {
        panelTitle.innerText = "⚡ EasyTax 전담 세무 모듈 원클릭 즉시 실행";
        panelDesc.innerText = "조특법 90% 소득세 감면, D-2 알바 3.3% 환급, 글로벌 세무 블로그 발행을 즉시 실행합니다.";

        container.innerHTML = `
            <div class="action-card" style="border-top:3px solid #F59E0B;">
                <div class="action-header">
                    <span class="action-emoji">🎬</span>
                    <div>
                        <h4>E-9 90% 감면 세무 숏폼</h4>
                        <p>합법 세무 권리 & Anti-Ban 공인 뱃지 비디오</p>
                    </div>
                </div>
                <button class="btn btn-gold btn-block" onclick="runModule('easytax_shorts')">💰 세무 숏폼 렌더링</button>
            </div>

            <div class="action-card" style="border-top:3px solid #F59E0B;">
                <div class="action-header">
                    <span class="action-emoji">📸</span>
                    <div>
                        <h4>Anti-Ban 공인 세무 카드뉴스</h4>
                        <p>선입금 0원 & 국세청 공인 대리 4장 카드뉴스</p>
                    </div>
                </div>
                <button class="btn btn-gold btn-block" onclick="runModule('easytax_cardnews')">💰 세무 카드뉴스 생성</button>
            </div>

            <div class="action-card" style="border-top:3px solid #F59E0B;">
                <div class="action-header">
                    <span class="action-emoji">🤖</span>
                    <div>
                        <h4>세금/비자 세무 레딧 헌터</h4>
                        <p>r/korea 세금 질문 감지 & 조특법 팩트 법률 답변</p>
                    </div>
                </div>
                <button class="btn btn-gold btn-block" onclick="runModule('easytax_reddit')">💰 세무 레딧 답변</button>
            </div>

            <div class="action-card" style="border-top:3px solid #F59E0B;">
                <div class="action-header">
                    <span class="action-emoji">📜</span>
                    <div>
                        <h4>17개국 세무 팁 브리핑</h4>
                        <p>매일 아침 비자별 절세 팁 텔레그램 발송</p>
                    </div>
                </div>
                <button class="btn btn-gold btn-block" onclick="runModule('easytax_briefing')">💰 세무 브리핑 발송</button>
            </div>

            <div class="action-card" style="border-top:3px solid #F59E0B;">
                <div class="action-header">
                    <span class="action-emoji">👥</span>
                    <div>
                        <h4>외국인 세무 페이스북 그룹 배포</h4>
                        <p>공인 세무 환급 팩트 가이드 스텔스 발행</p>
                    </div>
                </div>
                <button class="btn btn-gold btn-block" onclick="runModule('easytax_fb_groups')">💰 페북 세무 배포</button>
            </div>

            <div class="action-card" style="border-top:3px solid #F59E0B;">
                <div class="action-header">
                    <span class="action-emoji">🌐</span>
                    <div>
                        <h4>WordPress & Medium 글로벌 세무 블로그</h4>
                        <p>17개국어 5개년 경정청구 전문 칼럼 자동 발행</p>
                    </div>
                </div>
                <button class="btn btn-gold btn-block" onclick="runModule('easytax_blog')">💰 세무 블로그 발행</button>
            </div>

            <div class="action-card" style="border-top:3px solid #F59E0B;">
                <div class="action-header">
                    <span class="action-emoji">🌐</span>
                    <div>
                        <h4>산업단지/대학 EasyTax SEO</h4>
                        <p>전국 325개 거점 × 17개 언어 5,525개 세무 URL 색인</p>
                    </div>
                </div>
                <button class="btn btn-gold btn-block" onclick="triggerGoogleIndex()">💰 구글봇 세무 핑 전송</button>
            </div>

            <div class="action-card" style="border-top:3px solid #F59E0B;">
                <div class="action-header">
                    <span class="action-emoji">📄</span>
                    <div>
                        <h4>외국인 종합 절세 가이드북 PDF</h4>
                        <p>5개년 소급 신청 및 비자별 세무 가이드북</p>
                    </div>
                </div>
                <button class="btn btn-gold btn-block" onclick="runModule('easytax_pdf')">💰 세무 가이드북 렌더링</button>
            </div>
            </div>
        `;
    }
}

// 3. 듀얼 봇 독립 토글
async function toggleKMarketDaemon() {
    const endpoint = isKMarketRunning ? "/api/kmarket/stop" : "/api/kmarket/start";
    try {
        const res = await fetch(endpoint, { method: "POST" });
        const data = await res.json();
        showToast(data.message);
        fetchStatus();
    } catch (e) {
        showToast("K-Market 봇 제어 통신 실패", "error");
    }
}

async function toggleEasyTaxDaemon() {
    const endpoint = isEasyTaxRunning ? "/api/easytax/stop" : "/api/easytax/start";
    try {
        const res = await fetch(endpoint, { method: "POST" });
        const data = await res.json();
        showToast(data.message);
        fetchStatus();
    } catch (e) {
        showToast("EasyTax 봇 제어 통신 실패", "error");
    }
}

// 4. 실시간 상태 조회 (듀얼 봇)
async function fetchStatus() {
    try {
        const res = await fetch("/api/status");
        if (!res.ok) return;
        const data = await res.json();

        // 1. K-Market 봇 상태
        isKMarketRunning = data.kmarket_running;
        const kmIndicator = document.getElementById("km-daemon-indicator");
        const kmStatusText = document.getElementById("km-daemon-status-text");
        const kmToggleBtn = document.getElementById("btn-toggle-km-daemon");
        const kmSub = document.getElementById("km-daemon-sub");

        if (isKMarketRunning) {
            kmIndicator.classList.add("active");
            kmStatusText.innerText = "K-Market 가동 중 🟢";
            kmStatusText.style.color = "#FF6B35";
            kmSub.innerText = `사이클 #${data.kmarket_stats.cycle || 1} • ${data.kmarket_stats.last_run || '실행 중'}`;
            kmToggleBtn.innerText = "⏹️ K-Market 봇 정지";
            kmToggleBtn.className = "btn btn-secondary btn-block";
            kmToggleBtn.style.background = "#1A1F3D";
            kmToggleBtn.style.borderColor = "#2B3466";
        } else {
            kmIndicator.classList.remove("active");
            kmStatusText.innerText = "K-Market 대기 중 ⚪";
            kmStatusText.style.color = "#94A3B8";
            kmSub.innerText = "실물 숏폼/0원나눔/레딧";
            kmToggleBtn.innerText = "🚀 K-Market 봇 가동";
            kmToggleBtn.className = "btn btn-primary btn-block";
            kmToggleBtn.style.background = "";
            kmToggleBtn.style.borderColor = "";
        }

        // 2. EasyTax 봇 상태
        isEasyTaxRunning = data.easytax_running;
        const taxIndicator = document.getElementById("tax-daemon-indicator");
        const taxStatusText = document.getElementById("tax-daemon-status-text");
        const taxToggleBtn = document.getElementById("btn-toggle-tax-daemon");
        const taxSub = document.getElementById("tax-daemon-sub");

        if (isEasyTaxRunning) {
            taxIndicator.classList.add("active");
            taxStatusText.innerText = "EasyTax 가동 중 🟢";
            taxStatusText.style.color = "#FACC15";
            taxSub.innerText = `사이클 #${data.easytax_stats.cycle || 1} • ${data.easytax_stats.last_run || '실행 중'}`;
            taxToggleBtn.innerText = "⏹️ EasyTax 봇 정지";
            taxToggleBtn.className = "btn btn-secondary btn-block";
            taxToggleBtn.style.background = "#1A1F3D";
            taxToggleBtn.style.borderColor = "#2B3466";
        } else {
            taxIndicator.classList.remove("active");
            taxStatusText.innerText = "EasyTax 대기 중 ⚪";
            taxStatusText.style.color = "#94A3B8";
            taxSub.innerText = "E-9 90%감면/환급/Anti-Ban";
            taxToggleBtn.innerText = "💰 EasyTax 봇 가동";
            taxToggleBtn.className = "btn btn-gold btn-block";
            taxToggleBtn.style.background = "";
            taxToggleBtn.style.borderColor = "";
        }

        // 지표 업데이트
        document.getElementById("stat-total-count").innerText = `${data.total_history_count} 건`;
        document.getElementById("stat-top-score").innerText = `${data.top_score} 점`;

        // 최신 로그 추가
        if (data.recent_logs && data.recent_logs.length > 0) {
            data.recent_logs.forEach(msg => appendLog(msg.text, msg.type));
        }
    } catch (e) {
        console.error("Status fetch error:", e);
    }
}

// 5. 기간 탭 전환 (IR 관제)
let currentPeriod = "today";
function switchPeriod(period, btnElement) {
    currentPeriod = period;
    const buttons = document.querySelectorAll(".period-btn");
    buttons.forEach(b => b.classList.remove("active"));
    if (btnElement) btnElement.classList.add("active");
    loadIRAnalytics(period);
}

// 6. 실시간 유입 정밀 분석 & KTRS IR 관제 데이터 로드 (브랜드별 분리)
async function loadIRAnalytics(periodOrBtn = currentPeriod, maybeBtn = null) {
    const period = typeof periodOrBtn === 'string' ? periodOrBtn : currentPeriod;
    const btn = typeof periodOrBtn === 'object' && periodOrBtn && periodOrBtn.nodeType ? periodOrBtn : maybeBtn;
    if (btn) animateRefreshBtn(btn, "실시간 유입 및 IR 관제 지표가 새로고침되었습니다! 💎");
    try {
        const res = await fetch(`/api/ir-analytics?period=${period}`);
        const data = await res.json();

        // 1. 상단 4대 핵심 지표
        if (data.kpis) {
            document.getElementById("kpi-today-pv").innerText = `${data.kpis.today_pv.toLocaleString()} 회`;
            document.getElementById("kpi-cumulative-pv").innerText = `${data.kpis.cumulative_pv.toLocaleString()} 회`;
            document.getElementById("kpi-yoy").innerText = data.kpis.yoy_growth;
            document.getElementById("kpi-monthly-visitors").innerText = `${data.kpis.monthly_visitors.toLocaleString()} 명`;
        }

        // 2. 24시간 시간대별 추이 그래프
        const chartContainer = document.getElementById("hourly-bar-chart");
        if (chartContainer && data.hourly_data) {
            const maxVal = Math.max(...data.hourly_data.map(d => d.count), 1);
            chartContainer.innerHTML = data.hourly_data.map(d => {
                const heightPercent = Math.max(8, Math.round((d.count / maxVal) * 100));
                const barColor = currentBrand === "easytax" ? "#f59e0b" : "#10b981";
                return `
                    <div class="bar-column">
                        <span class="bar-badge">${d.count}회</span>
                        <div class="bar-fill" style="height: ${heightPercent}%; background: ${barColor};"></div>
                        <span class="bar-label">${d.hour}</span>
                    </div>
                `;
            }).join("");
        }

        // 3. 글로벌 채널별 유입 현황
        const channelList = document.getElementById("channel-bars-list");
        if (channelList && data.channel_inflows) {
            channelList.innerHTML = data.channel_inflows.map((c, idx) => `
                <div class="channel-bar-row">
                    <div class="channel-info-line">
                        <span><strong>${idx + 1}. ${c.name}</strong> <small style="color:var(--text-secondary);">(${c.status})</small></span>
                        <span><strong style="color:${c.color};">${c.count}회</strong> (${c.share}%)</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill" style="width: ${c.share}%; background: ${c.color};"></div>
                    </div>
                </div>
            `).join("");
        }

        // 4. 각 앱별 최종 산출물 성과 카드 (브랜드별 100% 필터링)
        const appGrid = document.getElementById("ir-app-metrics-grid");
        if (appGrid && data.app_results) {
            const filteredApps = Object.entries(data.app_results).filter(([k, v]) => {
                if (currentBrand === "kmarket") return k === "kmarket";
                if (currentBrand === "easytax") return k === "easytax";
                return true;
            });

            appGrid.innerHTML = filteredApps.map(([key, app]) => {
                const borderCol = key === "kmarket" ? "#10b981" : "#f59e0b";
                return `
                    <div class="platform-card" style="border-top: 4px solid ${borderCol}; grid-column: 1/-1;">
                        <div class="platform-header">
                            <div class="platform-title-area">
                                <span class="platform-icon">${app.icon}</span>
                                <div>
                                    <div class="platform-name" style="font-size:18px;">${app.name}</div>
                                    <div class="platform-api">${app.tagline}</div>
                                </div>
                            </div>
                            <span class="platform-status-badge ready" style="font-size:13px;">${app.status_badge}</span>
                        </div>
                        <div class="platform-body" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:16px; margin-top:16px;">
                            ${Object.entries(app.metrics).map(([mKey, mVal]) => `
                                <div style="background:rgba(255,255,255,0.03); padding:12px; border-radius:8px;">
                                    <div style="font-size:12px; color:var(--text-secondary);">${mKey}</div>
                                    <div style="font-size:18px; font-weight:700; color:#f8fafc; margin-top:4px;">${mVal}</div>
                                </div>
                            `).join("")}
                        </div>
                    </div>
                `;
            }).join("");
        }

    } catch (e) {
        console.error("IR Analytics load error:", e);
    }
}

// 7. 플랫폼 상태 목록 로드 (브랜드별 100% 분리)
async function loadPlatforms(btn) {
    if (btn) animateRefreshBtn(btn, "플랫폼 연동 상태가 새로고침되었습니다! 🚀");
    const container = document.getElementById("platforms-container");
    try {
        const res = await fetch("/api/platforms");
        const data = await res.json();
        let platforms = data.platforms || {};

        let entries = Object.entries(platforms);
        if (currentBrand === "kmarket") {
            entries = entries.filter(([k, p]) => p.brand === "kmarket");
        } else if (currentBrand === "easytax") {
            entries = entries.filter(([k, p]) => p.brand === "easytax");
        }

        container.innerHTML = entries.map(([key, p]) => {
            const badgeClass = p.status === 'ready' ? 'ready' : p.status === 'simulation_mode' ? 'simulation_mode' : 'key_missing';
            const badgeLabel = p.status === 'ready' ? '🟢 가동 준비 완료' : p.status === 'simulation_mode' ? '🔵 시뮬레이션 모드' : '🟡 키 입력 대기';
            
            const isKM = p.brand === 'kmarket';
            const cardBorder = isKM ? 'border-top: 4px solid #10b981;' : 'border-top: 4px solid #f59e0b;';
            const ratioBadgeColor = isKM ? 'background:rgba(16,185,129,0.15);color:#34d399;' : 'background:rgba(245,158,11,0.15);color:#fbbf24;';

            return `
                <div class="platform-card" style="${cardBorder}">
                    <div class="platform-header">
                        <div class="platform-title-area">
                            <span class="platform-icon">${p.icon}</span>
                            <div>
                                <div class="platform-name">${p.name}</div>
                                <div class="platform-api">${p.api_type}</div>
                            </div>
                        </div>
                        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px;">
                            <span class="platform-status-badge ${badgeClass}">${badgeLabel}</span>
                            ${p.ratio ? `<span style="${ratioBadgeColor}padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;">비중: ${p.ratio}</span>` : ''}
                        </div>
                    </div>

                    <div class="platform-body">
                        <div class="platform-desc"><strong>📌 타깃 콘텐츠:</strong> ${p.target_content}</div>
                        <div class="platform-desc"><strong>📊 오늘 처리 실적:</strong> ${p.daily_count}건 • ${p.last_published}</div>
                        <div class="platform-diagnostic">💡 <strong>시스템 진단:</strong> ${p.diagnostic}</div>
                    </div>

                    <button class="btn btn-secondary btn-block" onclick="testPublishPlatform('${key}')">
                        🚀 ${p.name} 직접 자동 발행 테스트
                    </button>
                </div>
            `;
        }).join("");
    } catch (e) {
        console.error("Platforms load error:", e);
    }
}

// 8. 17개국 바이럴 해시태그 로드 (브랜드별 100% 분리)
async function loadHashtags(btn) {
    if (btn) animateRefreshBtn(btn, "17개국 타깃 해시태그가 새로고침되었습니다! 📈");
    const container = document.getElementById("hashtags-container");
    const countBadge = document.getElementById("supported-countries-count");
    try {
        const res = await fetch("/api/hashtags");
        const data = await res.json();
        const countries = data.hashtags || {};

        if (countBadge) {
            countBadge.innerText = Object.keys(countries).length;
        }

        container.innerHTML = Object.entries(countries).map(([lang, info]) => {
            const inKoreaTags = (info.in_korea_common || []).map(t => `<span style="background:rgba(59,130,246,0.15);color:#60a5fa;padding:3px 8px;border-radius:12px;font-size:11px;margin:2px;display:inline-block;">${t}</span>`).join("");
            const districtTags = (info.hot_districts || []).map(t => `<span style="background:rgba(168,85,247,0.15);color:#c084fc;padding:2px 6px;border-radius:8px;font-size:10px;margin:2px;display:inline-block;">📍 ${t}</span>`).join("");

            let brandTagsHtml = "";
            let copyTagsList = [...(info.in_korea_common || [])];

            if (currentBrand === "kmarket") {
                const kmTags = (info.kmarket || []).map(t => `<span style="background:rgba(16,185,129,0.15);color:#34d399;padding:3px 8px;border-radius:12px;font-size:11px;margin:2px;display:inline-block;">${t}</span>`).join("");
                copyTagsList.push(...(info.kmarket || []));
                brandTagsHtml = `
                    <div style="margin-top:6px;">
                        <strong style="font-size:11px;color:#34d399;">🛒 K-Market(0원나눔/중고):</strong><br>
                        ${kmTags}
                    </div>
                `;
            } else {
                const taxTags = (info.easytax || []).map(t => `<span style="background:rgba(245,158,11,0.15);color:#fbbf24;padding:3px 8px;border-radius:12px;font-size:11px;margin:2px;display:inline-block;">${t}</span>`).join("");
                copyTagsList.push(...(info.easytax || []));
                brandTagsHtml = `
                    <div style="margin-top:6px;">
                        <strong style="font-size:11px;color:#fbbf24;">💰 EasyTax(90%세금환급):</strong><br>
                        ${taxTags}
                    </div>
                `;
            }

            const copyString = copyTagsList.join(" ");

            return `
                <div class="platform-card" style="display:flex;flex-direction:column;justify-content:space-between;">
                    <div>
                        <div class="platform-header">
                            <div class="platform-title-area">
                                <span class="platform-icon" style="font-size:24px;">${info.flag || "🌐"}</span>
                                <div>
                                    <div class="platform-name">${info.name || lang.toUpperCase()}</div>
                                    <div class="platform-api" style="font-size:11px;color:var(--text-secondary);">${lang.toUpperCase()} 체류자 전용</div>
                                </div>
                            </div>
                            <span class="platform-status-badge ready">🇰🇷 국내 체류 타깃</span>
                        </div>

                        <div class="platform-body">
                            <div style="font-size:11px;color:#94a3b8;margin-bottom:8px;background:rgba(255,255,255,0.03);padding:6px 8px;border-radius:6px;">
                                👥 <strong>타깃:</strong> ${info.target_group || "국내 체류자"}
                            </div>
                            <div>
                                <strong style="font-size:11px;color:#60a5fa;">🇰🇷 국내 체류 모국어 태그:</strong><br>
                                ${inKoreaTags}
                            </div>
                            ${brandTagsHtml}
                            ${districtTags ? `
                            <div style="margin-top:6px;">
                                <strong style="font-size:11px;color:#c084fc;">🏘️ 주요 밀집 거점:</strong><br>
                                ${districtTags}
                            </div>` : ''}
                        </div>
                    </div>

                    <div style="margin-top:12px;padding-top:8px;border-top:1px solid rgba(255,255,255,0.06);">
                        <button class="btn btn-secondary btn-block" style="font-size:12px;padding:6px 10px;" onclick="copyTags('${escape(copyString)}')">
                            📋 [${currentBrand.toUpperCase()}] 태그 일괄 복사
                        </button>
                    </div>
                </div>
            `;
        }).join("");
    } catch (e) {
        console.error("Hashtags load error:", e);
    }
}

// 9. 태그 클립보드 복사
function copyTags(escapedTags) {
    const text = unescape(escapedTags);
    navigator.clipboard.writeText(text).then(() => {
        showToast("해시태그가 클립보드에 복사되었습니다! 📋");
    }).catch(err => {
        showToast("복사 실패", "error");
    });
}

// 10. 바이럴 해시태그 새로고침
async function refreshHashtags(btn) {
    if (btn) animateRefreshBtn(btn, "17개국 실시간 바이럴 트렌드가 갱신되었습니다! 📈");
    appendLog("[Hashtags] 17개국 실시간 바이럴 해시태그 트렌드 갱신 중...", "info");
    showToast("실시간 바이럴 해시태그를 갱신합니다...");
    try {
        const res = await fetch("/api/hashtags/refresh", { method: "POST" });
        const data = await res.json();
        showToast(data.message);
        loadHashtags();
    } catch (e) {
        showToast("해시태그 갱신 실패", "error");
    }
}

// 11. 구글 검색 색인 실시간 트리거 (브랜드별 분리)
async function triggerGoogleIndex() {
    const endpoint = currentBrand === "easytax" ? "/api/easytax/google-index" : "/api/kmarket/google-index";
    const brandName = currentBrand === "easytax" ? "EasyTax" : "K-Market";
    appendLog(`[Google Indexing] Googlebot에게 ${brandName} 전용 1,105개 대학/공단 색인 요청 전송 중...`, "info");
    showToast(`구글 봇에게 [${brandName}] 실시간 색인 핑을 전송합니다...`);

    try {
        const res = await fetch(endpoint, { method: "POST" });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Success] ${data.message}`, "success");
            showToast(data.message);
        } else {
            appendLog(`[Error] ${data.message}`, "error");
        }
    } catch (e) {
        appendLog(`[Error] 구글 색인 요청 통신 실패: ${e}`, "error");
    }
}

// 12. 플랫폼 직접 테스트 발행
async function testPublishPlatform(platformId) {
    appendLog(`[Action] ${platformId.toUpperCase()} 다이렉트 자동 발행 테스트 요청...`, "info");
    showToast(`${platformId} 직접 발행 테스트를 진행합니다...`);

    try {
        const res = await fetch(`/api/platforms/test-publish/${platformId}`, { method: "POST" });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Success] ${data.message}`, "success");
            showToast(data.message);
        } else {
            appendLog(`[Error] ${data.message}`, "error");
        }
    } catch (e) {
        appendLog(`[Error] 플랫폼 테스트 발행 실패: ${e}`, "error");
    }
}

// 13. 원클릭 모듈 실행
async function runModule(moduleName) {
    const brandName = currentBrand === "easytax" ? "EasyTax" : "K-Market";
    appendLog(`[Action] [${brandName}] ${moduleName} 모듈 즉시 실행 요청...`, "info");
    showToast(`[${brandName}] ${moduleName} 모듈이 백그라운드에서 실행됩니다.`);

    try {
        const res = await fetch(`/api/run-module/${moduleName}`, { method: "POST" });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Success] ${data.message}`, "success");
            showToast(data.message);
            fetchStatus();
            loadGallery();
        } else {
            appendLog(`[Error] ${data.message}`, "error");
        }
    } catch (e) {
        appendLog(`[Error] 모듈 실행 통신 실패: ${e}`, "error");
    }
}

// 14. 갤러리 로드 & 카테고리 필터링 (사진 최우선 & 전체 노출)
let cachedGalleryItems = [];
let currentGalleryFilter = "all";

async function loadGallery(btn) {
    if (btn) animateRefreshBtn(btn, "미디어 갤러리가 새로고침되었습니다! 🎬");
    const grid = document.getElementById("gallery-grid");
    try {
        const res = await fetch("/api/outputs?t=" + Date.now());
        const data = await res.json();

        let items = data.items || [];
        cachedGalleryItems = items;

        // 카테고리별 개수 업데이트
        const imgCount = items.filter(i => i.type === "image").length;
        const audioCount = items.filter(i => i.type === "audio").length;
        const docCount = items.filter(i => i.type === "doc").length;

        if (document.getElementById("gallery-count-img")) document.getElementById("gallery-count-img").innerText = imgCount;
        if (document.getElementById("gallery-count-audio")) document.getElementById("gallery-count-audio").innerText = audioCount;
        if (document.getElementById("gallery-count-doc")) document.getElementById("gallery-count-doc").innerText = docCount;

        renderGalleryItems();
    } catch (e) {
        console.error("Gallery load error:", e);
    }
}

function filterGallery(filterType, btn) {
    currentGalleryFilter = filterType;
    document.querySelectorAll(".gallery-filter-btn").forEach(b => b.classList.remove("active"));
    if (btn) btn.classList.add("active");
    renderGalleryItems();
}

function renderGalleryItems() {
    const grid = document.getElementById("gallery-grid");
    if (!grid) return;

    let items = [...cachedGalleryItems];

    // 브랜드 필터링 (선택 시 해당 브랜드 우선, 없으면 전체)
    if (currentBrand === "kmarket") {
        const filtered = items.filter(i => i.brand === "kmarket" || i.name.includes("kmarket"));
        if (filtered.length > 0) items = filtered;
    } else if (currentBrand === "easytax") {
        const filtered = items.filter(i => i.brand === "easytax" || i.name.includes("easytax"));
        if (filtered.length > 0) items = filtered;
    }

    if (currentGalleryFilter !== "all") {
        items = items.filter(i => i.type === currentGalleryFilter);
    }

    if (items.length === 0) {
        grid.innerHTML = `<div style="color: var(--text-secondary); grid-column: 1/-1; text-align:center; padding: 40px; background:#13172E; border-radius:12px; border:1px solid #22294E;">
            <span style="font-size:32px; display:block; margin-bottom:8px;">🖼️</span>
            생성된 ${currentGalleryFilter === 'image' ? '카드뉴스 사진' : '미디어'}가 없습니다.
        </div>`;
        return;
    }

    grid.innerHTML = items.map(item => {
        const isKM = item.brand === "kmarket" || item.name.includes("kmarket");
        const brandBadge = isKM
            ? `<span style="background:rgba(16,185,129,0.2);color:#34d399;padding:3px 8px;border-radius:6px;font-size:11px;font-weight:700;">🛒 K-Market</span>` 
            : `<span style="background:rgba(245,158,11,0.2);color:#fbbf24;padding:3px 8px;border-radius:6px;font-size:11px;font-weight:700;">💰 EasyTax</span>`;

        let thumbHtml = "";
        if (item.type === "image") {
            thumbHtml = `
                <div class="gallery-thumb-wrapper" style="background:#080A14;height:220px;display:flex;align-items:center;justify-content:center;overflow:hidden;border-radius:10px 10px 0 0;">
                    <img src="${item.url}" class="gallery-thumb" alt="${item.name}" loading="lazy" onclick="window.open('${item.url}', '_blank')" style="width:100%;height:100%;object-fit:cover;cursor:pointer;" title="클릭하여 원본 사진 크게 보기">
                </div>
            `;
        } else if (item.type === "audio") {
            thumbHtml = `
                <div class="gallery-thumb-wrapper" style="background:linear-gradient(135deg,#1E1B4B,#0F172A);height:180px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:16px;">
                    <span style="font-size:36px;margin-bottom:8px;">🎵</span>
                    <audio controls src="${item.url}" style="width:95%;height:32px;"></audio>
                </div>
            `;
        } else {
            thumbHtml = `
                <div class="gallery-thumb-wrapper" style="background:#0D1126;height:160px;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#94A3B8;">
                    <span style="font-size:38px;margin-bottom:6px;">📄</span>
                    <span style="font-size:11px;color:#94A3B8;">텍스트 브리핑</span>
                </div>
            `;
        }

        return `
            <div class="gallery-card" style="background:#13172E;border:1px solid #22294E;border-radius:14px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 4px 14px rgba(0,0,0,0.3);">
                ${thumbHtml}
                <div class="gallery-info" style="padding:14px 16px;display:flex;flex-direction:column;flex:1;justify-content:space-between;">
                    <div>
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                            ${brandBadge}
                            <span style="font-size:11px;color:var(--text-secondary);font-weight:600;">${item.size}</span>
                        </div>
                        <div class="gallery-title" title="${item.name}" style="font-size:13px;font-weight:700;color:#FFFFFF;margin-bottom:4px;word-break:break-all;">${item.name}</div>
                        <div class="gallery-meta" style="font-size:11px;color:var(--text-muted);margin-bottom:10px;">${item.category}</div>
                    </div>
                    <a href="${item.url}" target="_blank" class="btn btn-secondary btn-block" style="font-size:12px;padding:8px 12px;text-align:center;text-decoration:none;">
                        ${item.type === 'image' ? '🔍 사진 크게 보기' : '📥 열기 / 다운로드'}
                    </a>
                </div>
            </div>
        `;
    }).join("");
}

// 15. 자가학습 랭킹 로드 (브랜드별 100% 분리)
async function loadGoldenCopies(btn) {
    if (btn) animateRefreshBtn(btn, "골든 카피 랭킹이 새로고침되었습니다! 🧠");
    const tbody = document.getElementById("golden-copies-body");
    try {
        const res = await fetch(`/api/golden-copies?brand=${currentBrand}`);
        const data = await res.json();
        const brandName = currentBrand === "easytax" ? "EasyTax" : "K-Market";

        if (!data.copies || data.copies.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--text-secondary);">[${brandName}] 전용 기록된 S등급 골든 카피가 아직 없습니다. 봇이 가동되면 자동 기록됩니다.</td></tr>`;
            return;
        }

        tbody.innerHTML = data.copies.map(c => {
            const isKM = c.service_id === 'kmarket';
            const badgeStyle = isKM ? 'background:rgba(16,185,129,0.2);color:#34d399;' : 'background:rgba(245,158,11,0.2);color:#fbbf24;';
            const badgeLabel = isKM ? '🛒 K-MARKET' : '💰 EASYTAX';

            return `
                <tr>
                    <td><span style="color:#10b981;font-weight:bold;">${c.score}점</span> (${c.grade})</td>
                    <td><span class="badge" style="${badgeStyle}padding:2px 8px;border-radius:12px;font-size:11px;font-weight:bold;">${badgeLabel}</span></td>
                    <td>${c.target_lang.toUpperCase()}</td>
                    <td style="max-width:350px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="${c.content_text}">${c.content_text}</td>
                    <td>클릭 ${c.clicks}회 / 전환 ${c.conversions}건</td>
                </tr>
            `;
        }).join("");
    } catch (e) {
        console.error("Golden copies load error:", e);
    }
}

// 16. 환경 설정 로드 및 저장
async function loadSettings(btn) {
    if (btn) animateRefreshBtn(btn, "환경 설정값이 성공적으로 다시 로드되었습니다! ⚙️");
    try {
        const res = await fetch("/api/settings");
        const data = await res.json();
        if (data.settings) {
            document.getElementById("cfg-gemini-key").value = data.settings.GEMINI_API_KEY || "";
            document.getElementById("cfg-supabase-url").value = data.settings.SUPABASE_URL || "";
            document.getElementById("cfg-supabase-key").value = data.settings.SUPABASE_KEY || "";
            
            document.getElementById("cfg-km-youtube").value = data.settings.KMARKET_YOUTUBE_KEY || data.settings.YOUTUBE_API_KEY || "";
            document.getElementById("cfg-km-meta").value = data.settings.KMARKET_META_TOKEN || data.settings.META_ACCESS_TOKEN || "";
            document.getElementById("cfg-km-tiktok").value = data.settings.KMARKET_TIKTOK_TOKEN || data.settings.TIKTOK_ACCESS_TOKEN || "";
            
            document.getElementById("cfg-tax-youtube").value = data.settings.EASYTAX_YOUTUBE_KEY || "";
            document.getElementById("cfg-tax-meta").value = data.settings.EASYTAX_META_TOKEN || "";
            document.getElementById("cfg-tax-tiktok").value = data.settings.EASYTAX_TIKTOK_TOKEN || "";
            
            document.getElementById("cfg-tg-token").value = data.settings.TELEGRAM_BOT_TOKEN || "";
            document.getElementById("cfg-delay-min").value = data.settings.REPLY_DELAY_MIN_SEC || "180";
            document.getElementById("cfg-delay-max").value = data.settings.REPLY_DELAY_MAX_SEC || "420";
        }
    } catch (e) {
        console.error("Settings load error:", e);
    }
}

async function saveSettings(e) {
    e.preventDefault();
    const payload = {
        GEMINI_API_KEY: document.getElementById("cfg-gemini-key").value,
        SUPABASE_URL: document.getElementById("cfg-supabase-url").value,
        SUPABASE_KEY: document.getElementById("cfg-supabase-key").value,
        
        KMARKET_YOUTUBE_KEY: document.getElementById("cfg-km-youtube").value,
        KMARKET_META_TOKEN: document.getElementById("cfg-km-meta").value,
        KMARKET_TIKTOK_TOKEN: document.getElementById("cfg-km-tiktok").value,
        
        EASYTAX_YOUTUBE_KEY: document.getElementById("cfg-tax-youtube").value,
        EASYTAX_META_TOKEN: document.getElementById("cfg-tax-meta").value,
        EASYTAX_TIKTOK_TOKEN: document.getElementById("cfg-tax-tiktok").value,
        
        TELEGRAM_BOT_TOKEN: document.getElementById("cfg-tg-token").value,
        REPLY_DELAY_MIN_SEC: document.getElementById("cfg-delay-min").value,
        REPLY_DELAY_MAX_SEC: document.getElementById("cfg-delay-max").value
    };

    try {
        const res = await fetch("/api/settings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        showToast(data.message || "듀얼 채널 설정이 성공적으로 저장되었습니다!");
        loadPlatforms();
    } catch (e) {
        showToast("설정 저장 실패", "error");
    }
}

// 17. 터미널 로그 및 토스트
function appendLog(text, type = "info") {
    const box = document.getElementById("terminal-log");
    if (!box) return;
    const line = document.createElement("div");
    line.className = `log-line ${type}`;
    const time = new Date().toLocaleTimeString();
    line.innerText = `[${time}] ${text}`;
    box.appendChild(line);
    box.scrollTop = box.scrollHeight;
}

function clearLogs() {
    document.getElementById("terminal-log").innerHTML = "";
}

function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;
    const toast = document.createElement("div");
    toast.className = "toast";
    if (type === "error") toast.style.borderColor = "#ef4444";
    toast.innerText = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
}

// 18. 실시간 시스템 헬스케어 & 맥박 관제 (100% 브랜드별 완전 분리)
async function loadHealthStatus(btn) {
    if (btn) animateRefreshBtn(btn, "시스템 맥박 및 헬스케어 상태가 새로고침되었습니다! 🩺");
    try {
        const res = await fetch("/api/health");
        const data = await res.json();

        // 1. 패널 제목 및 설명 동적 변경
        const panelTitle = document.getElementById("health-panel-title");
        const panelDesc = document.getElementById("health-panel-desc");
        const brainTitle = document.getElementById("health-brain-title");
        const channelsTitle = document.getElementById("health-channels-title");

        const isKM = currentBrand === "kmarket";

        if (panelTitle) {
            panelTitle.innerText = isKM 
                ? "🩺 [K-Market 전담] 실시간 헬스케어 & 맥박 관제 센터"
                : "🩺 [EasyTax 전담] 국세청 세무 헬스케어 & 맥박 관제 센터";
        }
        if (panelDesc) {
            panelDesc.innerText = isKM
                ? "270개 실물 매물 0원 나눔 숏폼, 17개국 텔레그램, 페이스북 50만 그룹 등 K-Market 7대 전용 채널의 맥박을 실시간 감시합니다."
                : "조특법 90% 소득세 감면, D-2 알바 3.3% 환급, Anti-Ban 공인 세무 등 EasyTax 7대 전용 채널의 맥박을 실시간 감시합니다.";
        }
        if (brainTitle) {
            brainTitle.innerText = isKM
                ? "🧠 K-Market 전담 AI 생성 엔진 & 0원 나눔 자가학습 DB"
                : "🧠 EasyTax 전담 세무 법률 엔진 & 공인 세무 자가학습 DB";
            brainTitle.style.color = isKM ? "#10b981" : "#f59e0b";
        }
        if (channelsTitle) {
            channelsTitle.innerText = isKM
                ? "🛒 K-Market 7대 소셜 & 커뮤니티 전담 맥박"
                : "💰 EasyTax 7대 국세청 세무 전담 맥박";
            channelsTitle.style.color = isKM ? "#10b981" : "#f59e0b";
        }

        // 2. 헤더 건강도 뱃지 갱신
        const headerBadge = document.getElementById("header-health-score");
        if (headerBadge) {
            headerBadge.innerText = `${data.health_score}% ${data.overall_status === 'healthy' ? '정상 🟢' : '주의 🟡'}`;
        }

        // 3. 🧠 현재 브랜드 전용 핵심 3대 두뇌 카드 렌더링
        const brainGrid = document.getElementById("health-brain-grid");
        if (brainGrid && data.brain) {
            const brainItems = [
                {
                    name: isKM ? "K-Market Gemini 생성 엔진" : "EasyTax 조특법 법률 AI 엔진",
                    icon: "🧠",
                    status: data.brain.gemini_ai.status,
                    message: isKM ? "0원 나눔 실물 매물 카피 생성 엔진 가동" : "국세청 팩트 법률 & 세무 카피 엔진 가동",
                    ping: data.brain.gemini_ai.ping_ms
                },
                {
                    name: isKM ? "K-Market 무인 자율주행 봇" : "EasyTax 세금환급 무인 전담 봇",
                    icon: "🐍",
                    status: isKM ? (isKMarketRunning ? "ok" : "idle") : (isEasyTaxRunning ? "ok" : "idle"),
                    message: isKM 
                        ? (isKMarketRunning ? "24시간 0원 나눔 봇 회전 중 🟢" : "K-Market 봇 대기 중 (원클릭 가동)")
                        : (isEasyTaxRunning ? "24시간 세무 환급 봇 회전 중 🟢" : "EasyTax 봇 대기 중 (원클릭 가동)")
                },
                {
                    name: isKM ? "Supabase (kmarket_golden_copies)" : "Supabase (easytax_golden_copies)",
                    icon: "🗄️",
                    status: data.brain.supabase_db.status,
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

        // 4. 📡 현재 브랜드 전용 7대 채널 실시간 맥박 (100% 필터링)
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

// 1초 정밀 자가진단 실행
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
        } else {
            appendLog(`[Error] ${data.message}`, "error");
        }
    } catch (e) {
        appendLog(`[Error] 자가진단 요청 통신 실패: ${e}`, "error");
    }
}

// 환경 설정 불러오기
async function loadSettings() {
    try {
        const res = await fetch("/api/settings");
        const data = await res.json();
        if (data && data.settings) {
            const s = data.settings;
            if (document.getElementById("cfg-gemini-key")) {
                document.getElementById("cfg-gemini-key").value = s.GEMINI_API_KEY || s.GEMINI_API_KEY_EASYTAX || "";
            }
            if (document.getElementById("cfg-supabase-url")) {
                document.getElementById("cfg-supabase-url").value = s.SUPABASE_URL || "";
            }
            if (document.getElementById("cfg-supabase-key")) {
                document.getElementById("cfg-supabase-key").value = s.SUPABASE_KEY || "";
            }
            if (document.getElementById("cfg-tg-token")) {
                document.getElementById("cfg-tg-token").value = s.TELEGRAM_BOT_TOKEN || "";
            }
            if (document.getElementById("cfg-delay-min")) {
                document.getElementById("cfg-delay-min").value = s.REPLY_DELAY_MIN_SEC || 180;
            }
            if (document.getElementById("cfg-delay-max")) {
                document.getElementById("cfg-delay-max").value = s.REPLY_DELAY_MAX_SEC || 420;
            }
        }
    } catch (e) {
        console.error("Settings load error:", e);
    }
}

// 환경 설정 저장하기
async function saveSettings(event) {
    if (event) event.preventDefault();
    const payload = {
        GEMINI_API_KEY: document.getElementById("cfg-gemini-key")?.value || "",
        GEMINI_API_KEY_EASYTAX: document.getElementById("cfg-gemini-key")?.value || "",
        SUPABASE_URL: document.getElementById("cfg-supabase-url")?.value || "",
        SUPABASE_KEY: document.getElementById("cfg-supabase-key")?.value || "",
        TELEGRAM_BOT_TOKEN: document.getElementById("cfg-tg-token")?.value || "",
        REPLY_DELAY_MIN_SEC: document.getElementById("cfg-delay-min")?.value || "180",
        REPLY_DELAY_MAX_SEC: document.getElementById("cfg-delay-max")?.value || "420"
    };

    try {
        const res = await fetch("/api/settings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: json.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            showToast("✅ 설정이 성공적으로 저장되었습니다!");
            appendLog("[Settings] 듀얼 채널 환경 설정이 성공적으로 저장되었습니다.", "success");
        }
    } catch (e) {
        showToast("❌ 설정 저장 중 오류가 발생했습니다.");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadSettings();
});

