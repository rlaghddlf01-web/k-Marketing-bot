// ==========================================
// [모듈 1] common.js: 공통 상태 관리 및 유틸리티
// ==========================================

let currentBrand = "aura";
let isStockRunning = false;
let isAuraRunning = false;
let isInsuranceRunning = false;
let isKMarketRunning = false;
let isEasyTaxRunning = false;
let logHistory = [];

// 토스트 메시지 표시
function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;
    
    const toast = document.createElement("div");
    toast.className = `toast-message ${type}`;
    toast.style.background = type === "error" ? "#EF4444" : type === "success" ? "#10B981" : "#1E293B";
    toast.style.color = "#FFFFFF";
    toast.style.padding = "10px 16px";
    toast.style.borderRadius = "8px";
    toast.style.marginBottom = "8px";
    toast.style.fontSize = "12.5px";
    toast.style.fontWeight = "700";
    toast.style.boxShadow = "0 4px 14px rgba(0,0,0,0.3)";
    toast.style.animation = "fadeIn 0.3s ease";
    toast.innerText = message;
    
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// 터미널 로그 추가 (URL 자동 하이퍼링크 및 에러/장애 빨간색 강조 박스 직격 표출)
function appendLog(text, type = "info") {
    const logBox = document.getElementById("terminal-log");
    if (!logBox) return;
    
    const timeStr = new Date().toLocaleTimeString();
    const rawText = String(text);
    const isErr = type === "error" || rawText.includes("❌") || rawText.includes("실패") || rawText.includes("세션 만료") || rawText.includes("오류") || rawText.includes("만료");
    const isWarn = type === "warning" || rawText.includes("⚠️") || rawText.includes("경고");
    
    const color = isErr ? "#DC2626" : isWarn ? "#D97706" : type === "success" ? "#059669" : "#475569";
    
    // URL 감지 및 클릭 가능한 <a> 태그로 자동 변환
    let formattedText = rawText;
    const urlRegex = /(https?:\/\/[^\s\)\"\'<>]+)/g;
    formattedText = formattedText.replace(urlRegex, (url) => {
        return `<a href="${url}" target="_blank" rel="noopener noreferrer" style="color:#0284C7;text-decoration:underline;font-weight:700;margin:0 2px;background:rgba(2,132,199,0.1);padding:1px 6px;border-radius:4px;border:1px solid rgba(2,132,199,0.25);">${url} ↗</a>`;
    });

    const line = document.createElement("div");
    line.className = `log-line ${isErr ? 'error' : isWarn ? 'warning' : type}`;
    line.style.fontSize = "12px";
    line.style.fontFamily = "'Pretendard', monospace";
    line.style.margin = isErr ? "6px 0" : "3px 0";
    
    if (isErr) {
        // 🔴 에러/장애 로그: 굵은 빨간 글씨 + 붉은색 강조 박스
        line.style.background = "#FEF2F2";
        line.style.border = "1px solid #FECACA";
        line.style.borderLeft = "4px solid #DC2626";
        line.style.padding = "6px 10px";
        line.style.borderRadius = "6px";
        line.style.fontWeight = "800";
        line.innerHTML = `<span style="color:#991B1B;">[${timeStr}]</span> <span style="color:#DC2626;">${formattedText}</span>`;
    } else if (isWarn) {
        line.style.background = "#FFFBEB";
        line.style.border = "1px solid #FDE68A";
        line.style.borderLeft = "4px solid #F59E0B";
        line.style.padding = "5px 8px";
        line.style.borderRadius = "6px";
        line.style.fontWeight = "700";
        line.innerHTML = `<span style="color:#92400E;">[${timeStr}]</span> <span style="color:#B45309;">${formattedText}</span>`;
    } else {
        line.innerHTML = `<span style="color:#64748b;">[${timeStr}]</span> <span style="color:${color};font-weight:600;">${formattedText}</span>`;
    }
    
    logBox.appendChild(line);

    // 최대 100줄 유지 (오래된 로그 자동 정리)
    while (logBox.children.length > 100) {
        logBox.removeChild(logBox.firstChild);
    }

    logBox.scrollTop = logBox.scrollHeight;
}

// 새로고침 버튼 회전 애니메이션 헬퍼
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

// 탭 초기화 및 전환
function initTabs() {
    const navItems = document.querySelectorAll(".nav-item");
    const tabContents = document.querySelectorAll(".tab-content");

    navItems.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");

            navItems.forEach(i => i.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));

            btn.classList.add("active");
            const targetContent = document.getElementById(`tab-${targetTab}`);
            if (targetContent) targetContent.classList.add("active");

            if (targetTab === "overview" && typeof renderHubGrid === "function") renderHubGrid();
            if (targetTab === "ir-analytics" && typeof loadIRAnalytics === "function") loadIRAnalytics();
            if (targetTab === "platforms" && typeof loadPlatforms === "function") loadPlatforms();
            if (targetTab === "hashtags" && typeof loadHashtags === "function") loadHashtags();
            if (targetTab === "gallery" && typeof loadGallery === "function") loadGallery();
            if (targetTab === "self-learning" && typeof loadGoldenCopies === "function") loadGoldenCopies();
            if (targetTab === "health" && typeof loadHealthStatus === "function") loadHealthStatus();
        });
    });
}

function switchTabDirect(tabName) {
    const btn = document.querySelector(`.nav-item[data-tab="${tabName}"]`);
    if (btn) btn.click();
}

// 브랜드 스위칭 (stock ↔ aura ↔ insurance)
function switchBrand(brand) {
    currentBrand = brand || "aura";
    const btnStock = document.getElementById("brand-tab-stock");
    const btnAura = document.getElementById("brand-tab-aura");
    const btnIns = document.getElementById("brand-tab-insurance");
    const pageTitle = document.getElementById("page-title");
    const pageDesc = document.getElementById("page-desc");
    const seasonName = document.getElementById("season-name");
    const gCount = document.getElementById("google-index-count");
    const seoCount = document.getElementById("stat-seo-count");

    // 기본 탭 스타일 리셋 (화이트 테마)
    [btnStock, btnAura, btnIns].forEach(btn => {
        if (btn) {
            btn.style.background = "#F1F5F9";
            btn.style.border = "1px solid #CBD5E1";
            btn.style.color = "#475569";
            btn.style.boxShadow = "none";
        }
    });

    if (currentBrand === "stock") {
        if (btnStock) {
            btnStock.style.background = "linear-gradient(135deg, #F59E0B, #D97706)";
            btnStock.style.border = "none";
            btnStock.style.color = "#FFFFFF";
            btnStock.style.boxShadow = "0 4px 14px rgba(245,158,11,0.45)";
        }
        if (pageTitle) pageTitle.innerHTML = "📈 Stock Master 주식 AI 마케팅 통합 제어 센터";
        if (pageDesc) pageDesc.innerText = "당일 외인/기관 수급 분석, 장전 08:30 시황, 조건검색식, 24개 증시 채널을 24시간 자율 가동합니다.";
        if (seasonName) {
            seasonName.innerText = "STOCK MASTER AI";
            seasonName.style.color = "#FACC15";
        }
        if (gCount) gCount.innerText = "24개 채널 연결됨";
        if (seoCount) seoCount.innerText = "24개 채널 (Stock AI)";
    } else if (currentBrand === "aura") {
        if (btnAura) {
            btnAura.style.background = "linear-gradient(135deg, #EC4899, #BE185D)";
            btnAura.style.border = "none";
            btnAura.style.color = "#FFFFFF";
            btnAura.style.boxShadow = "0 4px 14px rgba(236,72,153,0.45)";
        }
        if (pageTitle) pageTitle.innerHTML = "💖 Aura AI 데이팅 마케팅 통합 제어 센터";
        if (pageDesc) pageDesc.innerText = "2030 소개팅 팁, 연애 심리 칼럼, 릴스/숏폼, 24개 소셜 채널을 24시간 자율 가동합니다.";
        if (seasonName) {
            seasonName.innerText = "AURA DATING";
            seasonName.style.color = "#EC4899";
        }
        if (gCount) gCount.innerText = "24개 채널 연결됨";
        if (seoCount) seoCount.innerText = "24개 채널 (Aura)";
    } else if (currentBrand === "insurance") {
        if (btnIns) {
            btnIns.style.background = "linear-gradient(135deg, #10B981, #059669)";
            btnIns.style.border = "none";
            btnIns.style.color = "#FFFFFF";
            btnIns.style.boxShadow = "0 4px 14px rgba(16,185,129,0.45)";
        }
        if (pageTitle) pageTitle.innerHTML = "🛡️ InsureBalance 보험비교 마케팅 통합 제어 센터";
        if (pageDesc) pageDesc.innerText = "실손보험 비교, 3대 질병 절약 가이드, 호갱 탈출 팁, 24개 채널을 24시간 자율 가동합니다.";
        if (seasonName) {
            seasonName.innerText = "INSUREBALANCE";
            seasonName.style.color = "#10B981";
        }
        if (gCount) gCount.innerText = "24개 채널 연결됨";
        if (seoCount) seoCount.innerText = "24개 채널 (InsureBalance)";
    }

    if (typeof fetchStatus === "function") fetchStatus();
    if (typeof renderHubGrid === "function") renderHubGrid();
    if (typeof updateGoldenBatchPanel === "function") updateGoldenBatchPanel();
    if (typeof loadPlatforms === "function") loadPlatforms();
    if (typeof loadHashtags === "function") loadHashtags();
    if (typeof loadGallery === "function") loadGallery();
    if (typeof loadGoldenCopies === "function") loadGoldenCopies();
    if (typeof loadIRAnalytics === "function") {
        if (typeof switchIRBrand === "function") {
            switchIRBrand(currentBrand);
        } else {
            loadIRAnalytics();
        }
    }
    if (typeof loadHealthStatus === "function") loadHealthStatus();
    if (typeof loadTelegramCommunityStats === "function") loadTelegramCommunityStats();
    if (typeof renderStockShortsSchedulerPanel === "function") renderStockShortsSchedulerPanel();
    if (typeof filterTimelineBrand === "function") filterTimelineBrand(brand);
    else if (typeof renderMissionTimeline === "function") renderMissionTimeline();
    if (typeof renderEmergencyGuardBanner === "function") renderEmergencyGuardBanner();
}

// 📱 9:16 모바일 iFrame 실시간 뷰어 브랜드 전환
function switchBrandFrame(brand, btn) {
    const iframe = document.getElementById("liveBrandFrame");
    const openBtn = document.getElementById("btnOpenDedicatedFrame");
    const btnStock = document.getElementById("btnTabStockFrame");
    const btnAura = document.getElementById("btnTabAuraFrame");
    const btnIns = document.getElementById("btnTabInsureFrame");

    const allButtons = [btnStock, btnAura, btnIns];
    allButtons.forEach(b => {
        if (b) {
            b.className = "btn btn-outline";
            b.style.background = "transparent";
            b.style.color = "#475569";
            b.style.borderColor = "#CBD5E1";
            b.style.boxShadow = "none";
        }
    });

    let targetUrl = "https://stockmaster-ai.vercel.app/";
    let dedicatedUrl = "/stock_frame.html";
    let dedicatedTitle = "🔗 주식 AI 단독 뷰어로 열기";

    if (brand === "stock") {
        targetUrl = "https://stockmaster-ai.vercel.app/";
        dedicatedUrl = "/stock_frame.html";
        dedicatedTitle = "🔗 주식 AI 단독 뷰어로 열기";
        if (btnStock) {
            btnStock.className = "btn btn-primary";
            btnStock.style.background = "linear-gradient(135deg, #F59E0B, #D97706)";
            btnStock.style.color = "#FFFFFF";
            btnStock.style.border = "none";
            btnStock.style.boxShadow = "0 4px 12px rgba(245,158,11,0.4)";
        }
    } else if (brand === "aura") {
        targetUrl = "https://aura-ai-dating.vercel.app/";
        dedicatedUrl = "/aura_frame.html";
        dedicatedTitle = "🔗 Aura 데이팅 단독 뷰어로 열기";
        if (btnAura) {
            btnAura.className = "btn btn-primary";
            btnAura.style.background = "linear-gradient(135deg, #EC4899, #BE185D)";
            btnAura.style.color = "#FFFFFF";
            btnAura.style.border = "none";
            btnAura.style.boxShadow = "0 4px 12px rgba(236,72,153,0.4)";
        }
    } else if (brand === "insure" || brand === "insurance") {
        targetUrl = "https://insure-rebalance.vercel.app/";
        dedicatedUrl = "https://insure-rebalance.vercel.app/";
        dedicatedTitle = "🔗 보험 리밸런스 단독 뷰어로 열기";
        if (btnIns) {
            btnIns.className = "btn btn-primary";
            btnIns.style.background = "linear-gradient(135deg, #10B981, #059669)";
            btnIns.style.color = "#FFFFFF";
            btnIns.style.border = "none";
            btnIns.style.boxShadow = "0 4px 12px rgba(16,185,129,0.4)";
        }
    }

    if (iframe) iframe.src = targetUrl;
    if (openBtn) {
        openBtn.href = dedicatedUrl;
        openBtn.innerText = dedicatedTitle;
    }

    showToast(`📱 9:16 모바일 뷰어가 [${brand.toUpperCase()}]로 전환되었습니다!`, "info");
}

window.showToast = showToast;
window.appendLog = appendLog;
window.animateRefreshBtn = animateRefreshBtn;
window.initTabs = initTabs;
window.switchTabDirect = switchTabDirect;
window.switchBrand = switchBrand;
window.switchBrandFrame = switchBrandFrame;
