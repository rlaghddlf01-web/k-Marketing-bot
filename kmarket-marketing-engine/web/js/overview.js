// ==========================================
// [모듈 2] overview.js: 대시보드 & 8대 AI 허브 24시간 무인 관제 전담 모듈
// ==========================================

// 1. 대시보드 8대 AI 마케팅 허브 그리드 동적 렌더링
function renderHubGrid() {
    const container = document.getElementById("hub-grid-container");
    const panelTitle = document.getElementById("hub-panel-title");
    const panelDesc = document.getElementById("hub-panel-desc");
    if (!container) return;

    if (currentBrand === "kmarket") {
        if (panelTitle) panelTitle.innerText = "🎯 K-Market 8대 AI 마케팅 허브 & 24시간 무인 자율 공장";
        if (panelDesc) panelDesc.innerText = "270개 실물 매물 0원 나눔 숏폼, 카드뉴스, 레딧 1:1, 50만 페북 그룹, 블로그, 구글 색인 핑, 스레드, 텔레그램을 24시간 자율 가동합니다.";

        const hubs = [
            { id: "shorts", name: "0원 나눔 실물 숏폼 팩토리", icon: "🎬", desc: "YouTube Shorts · TikTok · IG Reels · FB Reels (4사 동시 전달)", key: "shorts" },
            { id: "cardnews", name: "실물 매물 4장 카드뉴스", icon: "📸", desc: "Instagram Feed · Facebook Feed · Reddit Gallery (3사 동시 전달)", key: "cardnews" },
            { id: "reddit", name: "Reddit 1:1 리드 헌터", icon: "🤖", desc: "26개 서브레딧 가구/원룸 질문 실시간 감지 & 80:20 솔루션 답변", key: "reddit" },
            { id: "fb_groups", name: "페이스북 50만 그룹 침투기", icon: "👥", desc: "재한 외국인 대형 그룹 정보글 + 첫 댓글 링크 스텔스 침투", key: "fb_groups" },
            { id: "blog", name: "WordPress & Medium SEO 블로그", icon: "🌐", desc: "17개국어 0원 나눔 1,500자 장문 SEO 칼럼 자동 발행", key: "blog" },
            { id: "seo", name: "구글 서치콘솔 & 실시간 색인 핑", icon: "🔍", desc: "Googlebot 실시간 색인 핑(URL_UPDATED) 전송 & sitemap.xml 갱신", key: "seo", isSeo: true },
            { id: "threads", name: "Meta Threads 바이럴 스레드", icon: "🧵", desc: "17개국어 0원 나눔 득템 썰 & 3~4단 구어체 타래 바이럴", key: "threads" },
            { id: "briefing", name: "0원 나눔 텔레그램 브리핑", icon: "📲", desc: "매일 아침 17개 언어 0원 꿀매물 데일리 모닝 푸시 발송", key: "briefing" }
        ];

        container.innerHTML = hubs.map((h, idx) => `
            <div class="action-card" id="card-kmarket-${h.key}" style="background:#13172E;border:1px solid #22294E;border-top:3px solid #10B981;border-radius:12px;padding:16px;display:flex;flex-direction:column;justify-content:space-between;gap:10px;box-shadow:0 4px 14px rgba(0,0,0,0.3);">
                <div>
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                        <span style="font-size:24px;width:38px;height:38px;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.05);border-radius:8px;">${h.icon}</span>
                        <div>
                            <div style="font-size:11px;color:#10B981;font-weight:700;">#${idx+1} K-MARKET 허브</div>
                            <h4 style="margin:0;font-size:14px;font-weight:700;color:#FFFFFF;">${h.name}</h4>
                        </div>
                    </div>
                    <p style="font-size:11.5px;color:#94A3B8;margin:0 0 10px 0;line-height:1.4;">${h.desc}</p>
                    
                    <!-- 실시간 24시간 가동 상태 바 -->
                    <div style="display:flex;justify-content:space-between;align-items:center;background:#090C19;padding:6px 10px;border-radius:8px;border:1px solid #1E2442;margin-bottom:10px;">
                        <span style="font-size:11px;color:#94A3B8;">실시간 상태:</span>
                        <span id="badge-status-kmarket-${h.key}" class="badge-idle" style="font-size:11px;font-weight:700;padding:2px 8px;border-radius:10px;background:rgba(255,255,255,0.08);color:#94A3B8;">
                            ⚪ 대기
                        </span>
                    </div>
                </div>

                <div>
                    <!-- 1:1 무인 가동 및 정지 버튼 그룹 -->
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px;">
                        <button class="btn btn-primary" id="btn-start-kmarket-${h.key}" onclick="startChannelDaemon('kmarket_${h.key}', this)" style="font-size:11.5px;padding:7px 4px;font-weight:700;" title="24시간 무인 자동 배포 데몬 시작">
                            🚀 무인 가동
                        </button>
                        <button class="btn btn-stop" id="btn-stop-kmarket-${h.key}" onclick="stopChannelDaemon('kmarket_${h.key}', this)" style="font-size:11.5px;padding:7px 4px;font-weight:700;" title="무인 데몬 정지">
                            ⏹️ 정지
                        </button>
                    </div>
                    <button class="btn btn-action" onclick="${h.isSeo ? 'triggerGoogleIndex()' : `runModule('kmarket_${h.key}')`}" style="width:100%;font-size:11px;padding:6px 0;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);color:#CBD5E1;">
                        ⚡ 즉시 1회 시험 실행
                    </button>
                </div>
            </div>
        `).join("");

    } else {
        if (panelTitle) panelTitle.innerText = "🎯 EasyTax 8대 AI 세무 허브 & 24시간 무인 자율 공장";
        if (panelDesc) panelDesc.innerText = "조특법 90% 소득세 감면, D-2 환급 숏폼, 세무 카드뉴스, 세무 레딧, 50만 페북 그룹, 세무 블로그, 구글 색인 핑, 스레드, 텔레그램을 24시간 자율 가동합니다.";

        const hubs = [
            { id: "shorts", name: "E-9 90% 감면 세무 숏폼", icon: "🎬", desc: "YouTube Shorts · TikTok · IG Reels · FB Reels (4사 동시 전달)", key: "shorts" },
            { id: "cardnews", name: "Anti-Ban 공인 세무 카드뉴스", icon: "📸", desc: "선입금 0원 & 국세청 공인 대리 4장 카드뉴스 3사 동시 전달", key: "cardnews" },
            { id: "reddit", name: "세금/비자 세무 레딧 헌터", icon: "🤖", desc: "r/korea 세금 질문 감지 & 조특법 팩트 법률 답변", key: "reddit" },
            { id: "fb_groups", name: "외국인 세무 페이스북 그룹 침투", icon: "👥", desc: "재한 50만 그룹 E-9 90% 감면 가이드 + 첫 댓글 링크", key: "fb_groups" },
            { id: "blog", name: "WordPress & Medium 글로벌 세무 블로그", icon: "🌐", desc: "17개국어 5개년 경정청구 전문 칼럼 자동 발행", key: "blog" },
            { id: "seo", name: "구글 서치콘솔 & 세무 색인 핑", icon: "🔍", desc: "전국 325개 거점 세무 랜딩 URL Googlebot 색인 핑 전송", key: "seo", isSeo: true },
            { id: "threads", name: "Meta Threads 세무 스레드", icon: "🧵", desc: "17개국어 조특법 제30조 90% 감면 합법 권리 타래 바이럴", key: "threads" },
            { id: "briefing", name: "17개국 세무 팁 텔레그램 브리핑", icon: "📲", desc: "매일 아침 비자별 절세 팁 17개국 채널 데일리 모닝 푸시", key: "briefing" }
        ];

        container.innerHTML = hubs.map((h, idx) => `
            <div class="action-card" id="card-easytax-${h.key}" style="background:#13172E;border:1px solid #22294E;border-top:3px solid #F59E0B;border-radius:12px;padding:16px;display:flex;flex-direction:column;justify-content:space-between;gap:10px;box-shadow:0 4px 14px rgba(0,0,0,0.3);">
                <div>
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                        <span style="font-size:24px;width:38px;height:38px;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.05);border-radius:8px;">${h.icon}</span>
                        <div>
                            <div style="font-size:11px;color:#F59E0B;font-weight:700;">#${idx+1} EASYTAX 허브</div>
                            <h4 style="margin:0;font-size:14px;font-weight:700;color:#FFFFFF;">${h.name}</h4>
                        </div>
                    </div>
                    <p style="font-size:11.5px;color:#94A3B8;margin:0 0 10px 0;line-height:1.4;">${h.desc}</p>
                    
                    <!-- 실시간 24시간 가동 상태 바 -->
                    <div style="display:flex;justify-content:space-between;align-items:center;background:#090C19;padding:6px 10px;border-radius:8px;border:1px solid #1E2442;margin-bottom:10px;">
                        <span style="font-size:11px;color:#94A3B8;">실시간 상태:</span>
                        <span id="badge-status-easytax-${h.key}" class="badge-idle" style="font-size:11px;font-weight:700;padding:2px 8px;border-radius:10px;background:rgba(255,255,255,0.08);color:#94A3B8;">
                            ⚪ 대기
                        </span>
                    </div>
                </div>

                <div>
                    <!-- 1:1 무인 가동 및 정지 버튼 그룹 -->
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px;">
                        <button class="btn btn-gold" id="btn-start-easytax-${h.key}" onclick="startChannelDaemon('easytax_${h.key}', this)" style="font-size:11.5px;padding:7px 4px;font-weight:700;" title="24시간 무인 세무 배포 데몬 시작">
                            🚀 무인 가동
                        </button>
                        <button class="btn btn-stop" id="btn-stop-easytax-${h.key}" onclick="stopChannelDaemon('easytax_${h.key}', this)" style="font-size:11.5px;padding:7px 4px;font-weight:700;" title="무인 데몬 정지">
                            ⏹️ 정지
                        </button>
                    </div>
                    <button class="btn btn-action" onclick="${h.isSeo ? 'triggerGoogleIndex()' : `runModule('easytax_${h.key}')`}" style="width:100%;font-size:11px;padding:6px 0;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);color:#CBD5E1;">
                        ⚡ 즉시 1회 시험 실행
                    </button>
                </div>
            </div>
        `).join("");
    }
}

// 2. 24시간 무인 자율 채널 데몬 시작
async function startChannelDaemon(moduleKey, btn) {
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spin-icon" style="display:inline-block;animation:rotateSpin 0.6s linear infinite;">🔄</span> 가동 중...`;
    }
    const cleanKey = moduleKey.replace("kmarket_", "").replace("easytax_", "");
    const brandPrefix = moduleKey.startsWith("easytax_") ? "easytax" : "kmarket";
    const badge = document.getElementById(`badge-status-${brandPrefix}-${cleanKey}`);
    if (badge) {
        badge.className = "badge-running";
        badge.style.background = "rgba(16,185,129,0.2)";
        badge.style.color = "#34D399";
        badge.style.border = "1px solid rgba(16,185,129,0.4)";
        badge.innerHTML = "🟢 실행 중 (24h)";
    }

    try {
        const res = await fetch(`/api/channel/start/${moduleKey}`, { method: "POST" });
        const data = await res.json();
        showToast(data.message || `[${moduleKey}] 24시간 무인 가동이 시작되었습니다! 🚀`, "success");
        appendLog(`[Daemon Start] ${data.message || moduleKey}`, "success");
        if (btn) {
            btn.innerHTML = `🔄 무인 가동 중 🟢`;
            btn.style.background = "#059669";
            btn.disabled = false;
        }
        fetchStatus();
    } catch (e) {
        showToast("가동 요청 통신 오류", "error");
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `🚀 무인 가동`;
        }
    }
}

// 3. 24시간 무인 자율 채널 데몬 정지
async function stopChannelDaemon(moduleKey, btn) {
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `⏹️ 정지 중...`;
    }
    const cleanKey = moduleKey.replace("kmarket_", "").replace("easytax_", "");
    const brandPrefix = moduleKey.startsWith("easytax_") ? "easytax" : "kmarket";
    const badge = document.getElementById(`badge-status-${brandPrefix}-${cleanKey}`);
    if (badge) {
        badge.className = "badge-idle";
        badge.style.background = "rgba(255,255,255,0.08)";
        badge.style.color = "#94A3B8";
        badge.style.border = "none";
        badge.innerHTML = "⚪ 대기";
    }

    try {
        const res = await fetch(`/api/channel/stop/${moduleKey}`, { method: "POST" });
        const data = await res.json();
        showToast(data.message || `[${moduleKey}] 무인 가동이 정지되었습니다.`, "info");
        appendLog(`[Daemon Stop] ${data.message || moduleKey}`, "warning");
        const startBtn = document.getElementById(`btn-start-${brandPrefix}-${cleanKey}`);
        if (startBtn) {
            startBtn.innerHTML = brandPrefix === "easytax" ? "💰 무인 가동" : "🚀 무인 가동";
            startBtn.style.background = "";
        }
        fetchStatus();
    } catch (e) {
        showToast("정지 요청 통신 오류", "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `⏹️ 정지`;
        }
    }
}

// 4. 채널 뱃지 동기화
function updateChannelBadges(runningChannels) {
    if (!runningChannels) return;
    const modules = ["shorts", "cardnews", "reddit", "fb_groups", "blog", "seo", "threads", "briefing"];
    const brands = ["kmarket", "easytax"];

    brands.forEach(b => {
        modules.forEach(m => {
            const key = `${b}_${m}`;
            const isRunning = !!runningChannels[key];
            const badge = document.getElementById(`badge-status-${b}-${m}`);
            const startBtn = document.getElementById(`btn-start-${b}-${m}`);

            if (badge) {
                if (isRunning) {
                    badge.className = "badge-running";
                    badge.style.background = "rgba(16,185,129,0.2)";
                    badge.style.color = "#34D399";
                    badge.style.border = "1px solid rgba(16,185,129,0.4)";
                    badge.innerHTML = "🟢 실행 중 (24h)";
                } else {
                    badge.className = "badge-idle";
                    badge.style.background = "rgba(255,255,255,0.08)";
                    badge.style.color = "#94A3B8";
                    badge.style.border = "none";
                    badge.innerHTML = "⚪ 대기";
                }
            }

            if (startBtn) {
                if (isRunning) {
                    startBtn.innerHTML = `🔄 무인 가동 중 🟢`;
                    startBtn.style.background = "#059669";
                } else {
                    startBtn.innerHTML = b === "easytax" ? "💰 무인 가동" : "🚀 무인 가동";
                    startBtn.style.background = "";
                }
            }
        });
    });
}

// 5. 사이드바 데몬 시작/정지 & 마스터 제어
async function startKMarketDaemon() {
    try {
        const res = await fetch("/api/kmarket/start", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "K-Market 무인 성장봇 사이클이 가동되었습니다! 🚀", "success");
        fetchStatus();
    } catch (e) {
        showToast("K-Market 가동 통신 오류", "error");
    }
}

async function stopKMarketDaemon() {
    try {
        const res = await fetch("/api/kmarket/stop", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "K-Market 봇이 정지되었습니다.", "info");
        fetchStatus();
    } catch (e) {
        showToast("K-Market 정지 통신 오류", "error");
    }
}

async function startEasyTaxDaemon() {
    try {
        const res = await fetch("/api/easytax/start", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "EasyTax 세금환급 봇 사이클이 가동되었습니다! 💰", "success");
        fetchStatus();
    } catch (e) {
        showToast("EasyTax 가동 통신 오류", "error");
    }
}

async function stopEasyTaxDaemon() {
    try {
        const res = await fetch("/api/easytax/stop", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "EasyTax 봇이 정지되었습니다.", "info");
        fetchStatus();
    } catch (e) {
        showToast("EasyTax 정지 통신 오류", "error");
    }
}

async function startAllBots() {
    showToast("⚡ K-Market & EasyTax 전체 봇을 동시 가동합니다! 🚀", "success");
    await startKMarketDaemon();
    await startEasyTaxDaemon();
}

async function stopAllBots() {
    showToast("🛑 모든 무인 봇을 정지합니다.", "warning");
    await stopKMarketDaemon();
    await stopEasyTaxDaemon();
}

// 6. 실시간 서버 상태 폴링 (3초 주기)
let lastSeenLogKeys = new Set();

async function fetchStatus() {
    try {
        const res = await fetch("/api/status");
        if (!res.ok) return;
        const data = await res.json();

        isKMarketRunning = data.kmarket_running;
        isEasyTaxRunning = data.easytax_running;

        // K-Market 사이드바 상태
        const kmIndicator = document.getElementById("km-daemon-indicator");
        const kmStatusText = document.getElementById("km-daemon-status-text");
        const kmSub = document.getElementById("km-daemon-sub");
        if (kmStatusText) {
            kmStatusText.innerText = isKMarketRunning ? "🛒 K-Market 가동 중 🟢" : "🛒 K-Market 대기 ⚪";
            kmStatusText.style.color = isKMarketRunning ? "#34D399" : "#94A3B8";
        }
        if (kmSub) {
            kmSub.innerText = isKMarketRunning ? `사이클 #${data.kmarket_stats?.cycle || 1} • 가동 중` : "실물 숏폼/0원나눔/레딧";
        }

        // EasyTax 사이드바 상태
        const taxIndicator = document.getElementById("tax-daemon-indicator");
        const taxStatusText = document.getElementById("tax-daemon-status-text");
        const taxSub = document.getElementById("tax-daemon-sub");
        if (taxStatusText) {
            taxStatusText.innerText = isEasyTaxRunning ? "💰 EasyTax 가동 중 🟢" : "💰 EasyTax 대기 ⚪";
            taxStatusText.style.color = isEasyTaxRunning ? "#FACC15" : "#94A3B8";
        }
        if (taxSub) {
            taxSub.innerText = isEasyTaxRunning ? `사이클 #${data.easytax_stats?.cycle || 1} • 가동 중` : "E-9 90%감면/환급/Anti-Ban";
        }

        // 8대 허브 실시간 뱃지 동기화
        updateChannelBadges(data.running_channels);

        // 상단 지표 (현재 브랜드 전용 1:1 완벽 분리)
        if (currentBrand === "kmarket") {
            if (document.getElementById("stat-total-count")) {
                document.getElementById("stat-total-count").innerText = `${data.kmarket_history_count || 0} 건`;
            }
            if (document.getElementById("stat-top-score")) {
                document.getElementById("stat-top-score").innerText = `${data.kmarket_top_score || 0} 점`;
            }
            if (document.getElementById("stat-seo-count")) {
                document.getElementById("stat-seo-count").innerText = `1,105 개 (K-Market)`;
            }
            if (document.getElementById("google-index-count")) {
                document.getElementById("google-index-count").innerText = `1,105개 K-Market 대학/공단 URL`;
            }
        } else {
            if (document.getElementById("stat-total-count")) {
                document.getElementById("stat-total-count").innerText = `${data.easytax_history_count || 0} 건`;
            }
            if (document.getElementById("stat-top-score")) {
                document.getElementById("stat-top-score").innerText = `${data.easytax_top_score || 0} 점`;
            }
            if (document.getElementById("stat-seo-count")) {
                document.getElementById("stat-seo-count").innerText = `5,525 개 (EasyTax)`;
            }
            if (document.getElementById("google-index-count")) {
                document.getElementById("google-index-count").innerText = `5,525개 EasyTax 전국 세무 URL`;
            }
        }

        // 최신 로그 콘솔 (중복 방지: 새 로그만 딱 1번 출력)
        if (data.recent_logs && data.recent_logs.length > 0) {
            data.recent_logs.forEach(msg => {
                const logKey = `${msg.timestamp || ''}_${msg.text}`;
                if (!lastSeenLogKeys.has(logKey)) {
                    lastSeenLogKeys.add(logKey);
                    appendLog(msg.text, msg.type);
                }
            });
            if (lastSeenLogKeys.size > 150) {
                lastSeenLogKeys = new Set(Array.from(lastSeenLogKeys).slice(-50));
            }
        }
    } catch (e) {
        console.error("Status fetch error:", e);
    }
}

// 7. 모듈 1회성 실행
async function runModule(moduleName) {
    appendLog(`[Action] ${moduleName} 모듈 즉시 실행 요청...`, "info");
    showToast(`${moduleName} 모듈이 백그라운드에서 실행됩니다.`);
    try {
        const res = await fetch(`/api/run-module/${moduleName}`, { method: "POST" });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Success] ${data.message}`, "success");
            showToast(data.message);
            fetchStatus();
        } else {
            appendLog(`[Error] ${data.message}`, "error");
        }
    } catch (e) {
        appendLog(`[Error] 모듈 실행 통신 실패: ${e}`, "error");
    }
}

// 8. 구글 실시간 색인 핑
async function triggerGoogleIndex() {
    const endpoint = currentBrand === "easytax" ? "/api/easytax/google-index" : "/api/kmarket/google-index";
    const brandName = currentBrand === "easytax" ? "EasyTax" : "K-Market";
    appendLog(`[Google Indexing] Googlebot에게 ${brandName} 6,630개 URL 색인 핑 전송 중...`, "info");
    showToast(`구글 봇에게 [${brandName}] 실시간 색인 핑을 전송합니다...`);

    try {
        const res = await fetch(endpoint, { method: "POST" });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Success] ${data.message}`, "success");
            showToast(data.message, "success");
        } else {
            appendLog(`[Error] ${data.message}`, "error");
        }
    } catch (e) {
        appendLog(`[Error] 구글 색인 요청 통신 실패: ${e}`, "error");
    }
}

function refreshOverview(btn) {
    animateRefreshBtn(btn, "대시보드 활동 로그와 상태가 새로고침되었습니다! 📊");
    fetchStatus();
    renderHubGrid();
}

window.renderHubGrid = renderHubGrid;
window.renderActionGrid = renderHubGrid;
window.startChannelDaemon = startChannelDaemon;
window.stopChannelDaemon = stopChannelDaemon;
window.startKMarketDaemon = startKMarketDaemon;
window.stopKMarketDaemon = stopKMarketDaemon;
window.startEasyTaxDaemon = startEasyTaxDaemon;
window.stopEasyTaxDaemon = stopEasyTaxDaemon;
window.startAllBots = startAllBots;
window.stopAllBots = stopAllBots;
window.fetchStatus = fetchStatus;
window.runModule = runModule;
window.triggerGoogleIndex = triggerGoogleIndex;
window.refreshOverview = refreshOverview;
