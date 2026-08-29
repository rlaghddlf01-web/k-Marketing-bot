// ==========================================
// [모듈 1] common.js: 공통 상태 관리 및 유틸리티
// ==========================================

let currentBrand = "kmarket";
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

// 터미널 로그 추가
function appendLog(text, type = "info") {
    const logBox = document.getElementById("terminal-log");
    if (!logBox) return;
    
    const timeStr = new Date().toLocaleTimeString();
    const color = type === "error" ? "#EF4444" : type === "success" ? "#34D399" : type === "warning" ? "#F59E0B" : "#94A3B8";
    
    const line = document.createElement("div");
    line.className = `log-line ${type}`;
    line.style.fontSize = "12px";
    line.style.fontFamily = "monospace";
    line.style.margin = "3px 0";
    line.innerHTML = `<span style="color:#64748b;">[${timeStr}]</span> <span style="color:${color};">${text}</span>`;
    
    logBox.appendChild(line);

    // 최대 100줄 유지 (오래된 로그 자동 정리로 메모리 및 스크롤 최적화)
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

// 브랜드 스위칭 (kmarket ↔ easytax)
function switchBrand(brand) {
    currentBrand = brand;
    const btnKM = document.getElementById("brand-tab-km");
    const btnTax = document.getElementById("brand-tab-tax");
    const pageTitle = document.getElementById("page-title");
    const pageDesc = document.getElementById("page-desc");
    const seasonName = document.getElementById("season-name");

    if (brand === "kmarket") {
        if (btnKM) {
            btnKM.style.background = "#7C3AED";
            btnKM.style.borderColor = "transparent";
            btnKM.style.color = "#FFFFFF";
            btnKM.style.boxShadow = "0 4px 14px rgba(124, 58, 237, 0.45)";
        }
        if (btnTax) {
            btnTax.style.background = "#13172E";
            btnTax.style.borderColor = "#22294E";
            btnTax.style.color = "#94A3B8";
            btnTax.style.boxShadow = "none";
        }
        if (pageTitle) pageTitle.innerHTML = "📊 K-Market 마케팅 통합 제어 센터";
        if (pageDesc) pageDesc.innerText = "270개 실물 매물 0원 나눔, 무빙세일, 17개국 양방향 번역 채팅을 실시간 제어합니다.";
        if (seasonName) {
            seasonName.innerText = "K-MARKET";
            seasonName.style.color = "#FF6B35";
        }
        const gCount = document.getElementById("google-index-count");
        if (gCount) gCount.innerText = "1,105개 K-Market 대학/공단 URL";
        const seoCount = document.getElementById("stat-seo-count");
        if (seoCount) seoCount.innerText = "1,105 개 (K-Market)";
    } else {
        if (btnTax) {
            btnTax.style.background = "linear-gradient(135deg, #FBBF24, #F59E0B, #D97706)";
            btnTax.style.borderColor = "#FDE68A";
            btnTax.style.color = "#FFFFFF";
            btnTax.style.boxShadow = "0 4px 18px rgba(245, 158, 11, 0.5)";
        }
        if (btnKM) {
            btnKM.style.background = "#13172E";
            btnKM.style.borderColor = "#22294E";
            btnKM.style.color = "#94A3B8";
            btnKM.style.boxShadow = "none";
        }
        if (pageTitle) pageTitle.innerHTML = "💰 EasyTax (KTRS) 100% 세무 환급 제어 센터";
        if (pageDesc) pageDesc.innerText = "조특법 90% 소득세 감면, D-2 알바 3.3% 환급, 5개년 경정청구를 실시간 제어합니다.";
        if (seasonName) {
            seasonName.innerText = "EASYTAX";
            seasonName.style.color = "#FACC15";
        }
        const gCount = document.getElementById("google-index-count");
        if (gCount) gCount.innerText = "5,525개 EasyTax 전국 세무 URL";
        const seoCount = document.getElementById("stat-seo-count");
        if (seoCount) seoCount.innerText = "5,525 개 (EasyTax)";
    }

    if (typeof fetchStatus === "function") fetchStatus();
    if (typeof renderHubGrid === "function") renderHubGrid();
    if (typeof loadPlatforms === "function") loadPlatforms();
    if (typeof loadHashtags === "function") loadHashtags();
    if (typeof loadGallery === "function") loadGallery();
    if (typeof loadGoldenCopies === "function") loadGoldenCopies();
    if (typeof loadIRAnalytics === "function") loadIRAnalytics();
    if (typeof loadHealthStatus === "function") loadHealthStatus();
}

window.showToast = showToast;
window.appendLog = appendLog;
window.animateRefreshBtn = animateRefreshBtn;
window.initTabs = initTabs;
window.switchTabDirect = switchTabDirect;
window.switchBrand = switchBrand;
