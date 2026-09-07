// ==========================================
// [모듈 2] overview.js: 대시보드 & 8대 AI 허브 24시간 무인 관제 전담 모듈
// ==========================================

// 🎯 듀얼 트랙 전략 배지 렌더링 헬퍼 (유료 채널 8대 황금국가 선불 최적화 vs 무료 채널 17개국 전세계 그물망)
function renderDualTrackBadge(h, brand) {
    const isMedia = (h.key === "shorts" || h.key === "cardnews");
    if (isMedia) {
        return `
            <!-- 🎯 8대 황금 타깃 모드 (선불 최적화) -->
            <div style="background:rgba(245, 158, 11, 0.08);border:1px solid rgba(245, 158, 11, 0.28);border-radius:8px;padding:8px 10px;margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                    <span style="font-size:11px;font-weight:800;color:#FBBF24;display:flex;align-items:center;gap:4px;">
                        🎯 8대 황금 타깃 모드 <span style="font-size:9.5px;color:#FDE68A;background:rgba(245,158,11,0.22);padding:1px 5px;border-radius:4px;border:1px solid rgba(245,158,11,0.35);">선불 최적화</span>
                    </span>
                    <span style="font-size:9.5px;color:#A3E635;font-weight:700;">환급 타깃 90% 집중</span>
                </div>
                <div style="font-size:9.5px;color:#CBD5E1;display:flex;flex-wrap:wrap;gap:3px;margin:5px 0;">
                    <span style="background:#1E2442;padding:2px 5px;border-radius:3px;">🇻🇳 베트남</span>
                    <span style="background:#1E2442;padding:2px 5px;border-radius:3px;">🇺🇿 우즈벡</span>
                    <span style="background:#1E2442;padding:2px 5px;border-radius:3px;">🇰🇭 캄보디아</span>
                    <span style="background:#1E2442;padding:2px 5px;border-radius:3px;">🇳🇵 네팔</span>
                    <span style="background:#1E2442;padding:2px 5px;border-radius:3px;">🇹🇭 태국</span>
                    <span style="background:#1E2442;padding:2px 5px;border-radius:3px;">🇮🇩 인도네시아</span>
                    <span style="background:#1E2442;padding:2px 5px;border-radius:3px;">🇲🇳 몽골</span>
                    <span style="background:#1E2442;padding:2px 5px;border-radius:3px;">🇲🇲 미얀마</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;font-size:10px;color:#94A3B8;border-top:1px dashed rgba(255,255,255,0.12);padding-top:6px;margin-top:4px;">
                    <span style="font-weight:700;color:#FDE68A;">⏰ 1일 2슬롯 (11:30 / 18:30)</span>
                    <span id="golden-counter-${brand}-${h.key}" style="color:#10B981;font-weight:800;font-size:11px;">오늘 실적: 0 / 16${h.key === 'shorts' ? '편' : '세트'}</span>
                </div>
            </div>
        `;
    } else {
        return `
            <!-- 🌐 비용 0원 무료 채널: 17개국 전체 그물망 -->
            <div style="background:rgba(56, 189, 248, 0.05);border:1px solid rgba(56, 189, 248, 0.2);border-radius:8px;padding:6px 10px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:10.5px;font-weight:700;color:#38BDF8;display:flex;align-items:center;gap:4px;">
                    🌐 17개국 전 세계 그물망
                </span>
                <span style="font-size:9.5px;color:#34D399;font-weight:800;background:rgba(52,211,153,0.12);padding:1px 6px;border-radius:4px;border:1px solid rgba(52,211,153,0.25);">
                    비용 0원 무료 독점
                </span>
            </div>
        `;
    }
}

async function fetchGoldenTargets() {
    try {
        const res = await fetch("/api/golden-targets");
        if (!res.ok) return;
        const data = await res.json();
        if (data.channels) {
            updateGoldenTargetIndicators(data.channels);
        }
    } catch (e) {}
}

function updateGoldenTargetIndicators(goldenTargets) {
    if (!goldenTargets) return;
    Object.keys(goldenTargets).forEach(chKey => {
        const info = goldenTargets[chKey];
        if (!info) return;
        const brand = chKey.startsWith("easytax_") ? "easytax" : "kmarket";
        const moduleName = chKey.replace("kmarket_", "").replace("easytax_", "");
        const indicator = document.getElementById(`golden-target-indicator-${brand}-${moduleName}`);
        if (indicator && info.detail) {
            indicator.innerText = `다음 순번: ${info.detail.flag || ''} ${info.detail.native || info.current_lang} (${info.current_lang})`;
        }
    });
}

// 1. 대시보드 8대 AI 마케팅 허브 그리드 동적 렌더링
function renderHubGrid() {
    const container = document.getElementById("hub-grid-container");
    const panelTitle = document.getElementById("hub-panel-title");
    const panelDesc = document.getElementById("hub-panel-desc");
    if (!container) return;

    if (currentBrand === "kmarket") {
        if (panelTitle) panelTitle.innerText = "🎯 K-Market 7대 AI 마케팅 허브 & 24시간 무인 자율 공장";
        if (panelDesc) panelDesc.innerText = "270개 실물 매물 0원 나눔 숏폼, 카드뉴스, 레딧 1:1, 50만 페북 그룹, 블로그, 구글 색인 핑, 스레드를 24시간 자율 가동합니다. (텔레그램은 상단 전용 사령부에서 통합 관제)";

        const hubs = [
            { id: "shorts", name: "0원 나눔 실물 숏폼 팩토리", icon: "🎬", desc: "4개 플랫폼 숏폼 (하루 3회 정시: 12:00 / 20:30 / 23:30 KST)", key: "shorts" },
            { id: "cardnews", name: "실물 매물 4장 카드뉴스", icon: "📸", desc: "4장 캐러셀 카드뉴스 (하루 3회 정시: 08:00 / 15:30 / 22:30 KST)", key: "cardnews" },
            { id: "reddit", name: "Reddit 1:1 리드 헌터", icon: "🤖", desc: "26개 서브레딧 실시간 감지 (1시간 간격 정기 자율 헌팅)", key: "reddit" },
            { id: "fb_groups", name: "페이스북 50만 그룹 침투기", icon: "👥", desc: "4장 카드뉴스 + 첫댓글 (하루 3회 정시: 09:30 / 13:30 / 19:30 KST)", key: "fb_groups" },
            { id: "blog", name: "17개국어 SEO 블로그 칼럼", icon: "🌐", desc: "17개국어 칼럼 (하루 3회 정시: 09:00 / 13:00 / 19:00 KST)", key: "blog" },
            { id: "seo", name: "구글 서치콘솔 & 실시간 색인 핑", icon: "🔍", desc: "Googlebot 색인 핑 & 사이트맵 갱신 (하루 1회 정시: 01:00 KST)", key: "seo", isSeo: true },
            { id: "threads", name: "Meta Threads 바이럴 스레드", icon: "🧵", desc: "3~4단 타래 바이럴 (하루 3회 정시: 11:00 / 16:30 / 21:30 KST)", key: "threads" }
        ];

        container.innerHTML = hubs.map((h, idx) => {
            const isMediaHub = (h.key === "shorts" || h.key === "cardnews");
            const engineSwitchHtml = isMediaHub ? `
                <!-- ⚡ 100% 통합 단일 표준: Google Gemini 3.1 Flash-Lite Image -->
                <div style="background:#090C19;padding:9px 12px;border-radius:8px;border:1px solid #1E2442;margin-bottom:8px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:11px;color:#38BDF8;font-weight:700;">⚡ 비주얼 엔진:</span>
                        <span style="font-size:10.5px;color:#10B981;font-weight:800;background:rgba(16,185,129,0.12);padding:2px 7px;border-radius:4px;border:1px solid rgba(16,185,129,0.3);">
                            🏆 Gemini 3.1 Flash-Lite
                        </span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px;font-size:9.5px;color:#94A3B8;">
                        <span>초고속 렌더링 (3.5초)</span>
                        <span style="color:#334155;">│</span>
                        <span style="color:#38BDF8;font-weight:600;">장당 ~7원 · 무결점 실사</span>
                    </div>
                </div>
            ` : "";

            return `
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
                    
                    ${engineSwitchHtml}
                    ${renderDualTrackBadge(h, 'kmarket')}

                    <!-- 실시간 24시간 가동 상태 바 -->
                    <div style="display:flex;justify-content:space-between;align-items:center;background:#090C19;padding:6px 10px;border-radius:8px;border:1px solid #1E2442;margin-bottom:10px;">
                        <span style="font-size:11px;color:#94A3B8;">실시간 상태:</span>
                        <span id="badge-status-kmarket-${h.key}" class="badge-idle" style="font-size:11px;font-weight:700;padding:2px 8px;border-radius:10px;background:rgba(255,255,255,0.08);color:#94A3B8;">
                            ⚪ 대기
                        </span>
                    </div>
                </div>

                <div>
                    ${isMediaHub ? `
                    <!-- 🌟 8대 황금 타깃 1일 2슬롯 24시간 무인 가동 및 정지 -->
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px;">
                        <button class="btn btn-primary" id="btn-daemon-gb-kmarket-${h.key}" onclick="startGoldenBatchDaemon()" style="font-size:11.5px;padding:7px 4px;font-weight:800;background:linear-gradient(135deg, #10B981, #059669);color:#FFFFFF;" title="오전 11:30 & 저녁 18:30 8대 국가 자동 대량 생산 무인 가동">
                            🚀 8개국 무인 가동
                        </button>
                        <button class="btn btn-stop" id="btn-stop-gb-kmarket-${h.key}" onclick="stopGoldenBatchDaemon()" style="font-size:11.5px;padding:7px 4px;font-weight:700;" title="8개국 무인 데몬 정지">
                            ⏹️ 정지
                        </button>
                    </div>
                    <!-- 🔥 8대 국가 즉시 일괄 렌더링 버튼 (원클릭 완성!) -->
                    <button class="btn" id="btn-run-gb-kmarket-${h.key}" onclick="triggerGoldenBatchRun('${h.key}', this)" style="width:100%;font-size:12.5px;padding:9px 0;background:linear-gradient(135deg, #F59E0B 0%, #D97706 100%);border:none;color:#000000;font-weight:900;border-radius:8px;box-shadow:0 4px 12px rgba(245,158,11,0.35);cursor:pointer;" title="8대 황금 타깃 국가 일괄 렌더링">
                        ⚡ 8대 국가 즉시 일괄 렌더링 (${h.key === 'shorts' ? '8편' : '8세트'})
                    </button>
                    ` : `
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
                    `}
                </div>
            </div>
        `}).join("");

    } else {
        if (panelTitle) panelTitle.innerText = "🎯 EasyTax 7대 AI 세무 허브 & 24시간 무인 자율 공장";
        if (panelDesc) panelDesc.innerText = "조특법 90% 소득세 감면, D-2 환급 숏폼, 세무 카드뉴스, 세무 레딧, 50만 페북 그룹, 세무 블로그, 구글 색인 핑, 스레드를 24시간 자율 가동합니다. (텔레그램은 상단 전용 사령부에서 통합 관제)";

        const hubs = [
            { id: "shorts", name: "E-9 90% 감면 세무 숏폼", icon: "🎬", desc: "4개 플랫폼 세무 숏폼 (하루 3회 정시: 12:00 / 20:30 / 23:30 KST)", key: "shorts" },
            { id: "cardnews", name: "Anti-Ban 공인 세무 카드뉴스", icon: "📸", desc: "4장 캐러셀 세무 카드뉴스 (하루 3회 정시: 08:00 / 15:30 / 22:30 KST)", key: "cardnews" },
            { id: "reddit", name: "세금/비자 세무 레딧 헌터", icon: "🤖", desc: "r/korea 세무 질문 감지 (1시간 간격 정기 자율 헌팅)", key: "reddit" },
            { id: "fb_groups", name: "외국인 세무 페이스북 그룹 침투", icon: "👥", desc: "4장 카드뉴스 + 첫댓글 (하루 3회 정시: 09:30 / 13:30 / 19:30 KST)", key: "fb_groups" },
            { id: "blog", name: "15개국어 글로벌 세무 블로그", icon: "🌐", desc: "15개국어 세무 칼럼 (하루 3회 정시: 09:00 / 13:00 / 19:00 KST)", key: "blog" },
            { id: "seo", name: "구글 서치콘솔 & 세무 색인 핑", icon: "🔍", desc: "Googlebot 색인 핑 & 사이트맵 갱신 (하루 1회 정시: 01:00 KST)", key: "seo", isSeo: true },
            { id: "threads", name: "Meta Threads 세무 스레드", icon: "🧵", desc: "조특법 90% 감면 타래 (하루 3회 정시: 11:00 / 16:30 / 21:30 KST)", key: "threads" }
        ];

        container.innerHTML = hubs.map((h, idx) => {
            const isMediaHub = (h.key === "shorts" || h.key === "cardnews");
            const engineSwitchHtml = isMediaHub ? `
                <!-- ⚡ 100% 통합 단일 표준: Google Gemini 3.1 Flash-Lite Image -->
                <div style="background:#090C19;padding:9px 12px;border-radius:8px;border:1px solid #1E2442;margin-bottom:8px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:11px;color:#38BDF8;font-weight:700;">⚡ 비주얼 엔진:</span>
                        <span style="font-size:10.5px;color:#F59E0B;font-weight:800;background:rgba(245,158,11,0.12);padding:2px 7px;border-radius:4px;border:1px solid rgba(245,158,11,0.3);">
                            🏆 Gemini 3.1 Flash-Lite
                        </span>
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px;font-size:9.5px;color:#94A3B8;">
                        <span>초고속 렌더링 (3.5초)</span>
                        <span style="color:#334155;">│</span>
                        <span style="color:#F59E0B;font-weight:600;">장당 ~7원 · 무결점 실사</span>
                    </div>
                </div>
            ` : "";

            return `
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
                    
                    ${engineSwitchHtml}
                    ${renderDualTrackBadge(h, 'easytax')}

                    <!-- 실시간 24시간 가동 상태 바 -->
                    <div style="display:flex;justify-content:space-between;align-items:center;background:#090C19;padding:6px 10px;border-radius:8px;border:1px solid #1E2442;margin-bottom:10px;">
                        <span style="font-size:11px;color:#94A3B8;">실시간 상태:</span>
                        <span id="badge-status-easytax-${h.key}" class="badge-idle" style="font-size:11px;font-weight:700;padding:2px 8px;border-radius:10px;background:rgba(255,255,255,0.08);color:#94A3B8;">
                            ⚪ 대기
                        </span>
                    </div>
                </div>

                <div>
                    ${isMediaHub ? `
                    <!-- 🌟 8대 황금 타깃 1일 2슬롯 24시간 무인 가동 및 정지 -->
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px;">
                        <button class="btn btn-gold" id="btn-daemon-gb-easytax-${h.key}" onclick="startGoldenBatchDaemon()" style="font-size:11.5px;padding:7px 4px;font-weight:800;background:linear-gradient(135deg, #10B981, #059669);color:#FFFFFF;" title="오전 11:30 & 저녁 18:30 8대 국가 세무 자동 대량 생산 무인 가동">
                            🚀 8개국 무인 가동
                        </button>
                        <button class="btn btn-stop" id="btn-stop-gb-easytax-${h.key}" onclick="stopGoldenBatchDaemon()" style="font-size:11.5px;padding:7px 4px;font-weight:700;" title="8개국 무인 데몬 정지">
                            ⏹️ 정지
                        </button>
                    </div>
                    <!-- 🔥 8대 국가 즉시 일괄 렌더링 버튼 (원클릭 완성!) -->
                    <button class="btn" id="btn-run-gb-easytax-${h.key}" onclick="triggerGoldenBatchRun('${h.key}', this)" style="width:100%;font-size:12.5px;padding:9px 0;background:linear-gradient(135deg, #F59E0B 0%, #D97706 100%);border:none;color:#000000;font-weight:900;border-radius:8px;box-shadow:0 4px 12px rgba(245,158,11,0.35);cursor:pointer;" title="8대 황금 타깃 국가 세무 일괄 렌더링">
                        ⚡ 8대 국가 즉시 일괄 렌더링 (${h.key === 'shorts' ? '8편' : '8세트'})
                    </button>
                    ` : `
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
                    `}
                </div>
            </div>
        `}).join("");
    }
    // 스위치 UI 상태 동기화 및 8대 황금 타깃 순환 상태 갱신
    setTimeout(loadMediaEngineSettings, 50);
    setTimeout(fetchGoldenTargets, 100);
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
        if (typeof loadTelegramCommunityStats === "function") loadTelegramCommunityStats();
        renderHubGrid();
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
        if (typeof loadTelegramCommunityStats === "function") loadTelegramCommunityStats();
        renderHubGrid();
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
        if (typeof loadTelegramCommunityStats === "function") loadTelegramCommunityStats();
        renderHubGrid();
    } catch (e) {
        showToast("EasyTax 정지 통신 오류", "error");
    }
}

async function startAllBots() {
    showToast("⚡ K-Market & EasyTax 전체 봇을 동시 가동합니다! 🚀", "success");
    await startKMarketDaemon();
    await startEasyTaxDaemon();
    if (typeof loadTelegramCommunityStats === "function") loadTelegramCommunityStats();
}

async function stopAllBots() {
    showToast("🛑 모든 무인 봇을 정지합니다.", "warning");
    await stopKMarketDaemon();
    await stopEasyTaxDaemon();
    if (typeof loadTelegramCommunityStats === "function") loadTelegramCommunityStats();
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
        if (data.golden_targets) {
            updateGoldenTargetIndicators(data.golden_targets);
        }
        if (data.golden_batch_summary) {
            updateGoldenBatchPanel(data.golden_batch_summary);
        }

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

// 9. 이미지 생성 엔진 단일 표준 (Google Gemini 3.1 Flash-Lite Image)
async function setMediaEngine(channelKey, engineMode = "gemini") {
    appendLog(`[Engine] ${channelKey} 비주얼 엔진: 🏆 Gemini 3.1 Flash-Lite Image 가동 중`, "info");
    showToast(`[${channelKey}] 비주얼 엔진이 Gemini 3.1 Flash-Lite Image로 확정되었습니다.`);
}

async function loadMediaEngineSettings() {
    // 100% Gemini 3.1 Flash-Lite Image 단일 표준 가동
}

function updateMediaEngineUI(settings = {}, stats = {}) {
    // 단일 표준 엔진 UI
}

function refreshOverview(btn) {
    animateRefreshBtn(btn, "대시보드 활동 로그와 상태가 새로고침되었습니다! 📊");
    fetchStatus();
    renderHubGrid();
    loadMediaEngineSettings();
}

// 🌟 10. 8대 황금 타깃 국가 1일 2슬롯 풀가동 제어 모듈
let lastGoldenBatchSummary = null;

async function triggerGoldenBatchRun(contentType = 'all', btnElement = null) {
    const brand = currentBrand || 'kmarket';
    const brandName = brand === 'easytax' ? 'EasyTax (세무)' : 'K-Market (쇼핑)';
    const typeLabel = contentType === 'shorts' ? '숏폼 8편' : contentType === 'cardnews' ? '5장 카드뉴스 8세트' : '숏폼 8편 + 카드뉴스 8세트 (총 16건)';
    
    appendLog(`[Action] 🌟 [${brandName}] 8대 황금 타깃 국가 ${typeLabel} 일괄 즉시 생산 가동...`, "info");
    showToast(`🌟 [${brandName}] 8대 황금 타깃 ${typeLabel} 대량 생산을 시작합니다!`, "success");

    const btn = btnElement || document.getElementById(`btn-run-gb-${brand}-${contentType}`);
    const originalText = btn ? btn.innerHTML : "";
    if (btn) {
        btn.disabled = true;
        btn.style.opacity = "0.7";
        btn.innerHTML = `<span>⏳</span> 8대 국가 대량 생산 중... (바탕화면 실시간 저장)`;
    }

    try {
        const res = await fetch("/api/golden-batch/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ brand: brand, type: contentType, slot_name: "manual" })
        });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Success] 🎉 ${data.message}`, "success");
            showToast(data.message, "success");
        } else {
            appendLog(`[Error] ⚠️ ${data.message}`, "error");
        }
    } catch (e) {
        appendLog(`[Error] ❌ 골든 배치 통신 오류: ${e}`, "error");
        showToast("골든 배치 통신 오류", "error");
    } finally {
        setTimeout(() => {
            if (btn) {
                btn.disabled = false;
                btn.style.opacity = "1";
                btn.innerHTML = originalText;
                updateGoldenBatchPanel();
            }
            fetchStatus();
        }, 3000);
    }
}

async function startGoldenBatchDaemon() {
    const brand = currentBrand || 'kmarket';
    const brandName = brand === 'easytax' ? 'EasyTax (세무)' : 'K-Market (쇼핑)';
    appendLog(`[Daemon] ⏰ [${brandName}] 8대 황금 타깃 24시간 무인 데몬 시작 요청 (11:30 & 18:30)...`, "info");
    showToast(`⏰ [${brandName}] 24시간 무인 예약 데몬이 가동됩니다!`, "success");

    try {
        const res = await fetch("/api/golden-batch/daemon/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ brand: brand })
        });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Success] 🟢 ${data.message}`, "success");
            showToast(data.message, "success");
            fetchStatus();
        }
    } catch (e) {
        appendLog(`[Error] ❌ 데몬 시작 통신 오류: ${e}`, "error");
    }
}

async function stopGoldenBatchDaemon() {
    const brand = currentBrand || 'kmarket';
    const brandName = brand === 'easytax' ? 'EasyTax (세무)' : 'K-Market (쇼핑)';
    appendLog(`[Daemon] ⏹️ [${brandName}] 8대 황금 타깃 무인 데몬 정지 요청...`, "info");
    showToast(`⏹️ [${brandName}] 무인 데몬이 정지되었습니다.`, "info");

    try {
        const res = await fetch("/api/golden-batch/daemon/stop", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ brand: brand })
        });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Info] ⚪ ${data.message}`, "info");
            showToast(data.message, "info");
            fetchStatus();
        }
    } catch (e) {
        appendLog(`[Error] ❌ 데몬 정지 통신 오류: ${e}`, "error");
    }
}

function updateGoldenBatchPanel(summary) {
    if (summary) lastGoldenBatchSummary = summary;
    const currentSummary = summary || lastGoldenBatchSummary;
    const brand = currentBrand || 'kmarket';

    if (currentSummary) {
        const totalS = currentSummary.total_shorts || 0;
        const totalC = currentSummary.total_cardnews || 0;
        
        const counterShorts = document.getElementById(`golden-counter-${brand}-shorts`);
        const counterCardnews = document.getElementById(`golden-counter-${brand}-cardnews`);
        if (counterShorts) counterShorts.innerText = `오늘 실적: ${totalS} / 16편`;
        if (counterCardnews) counterCardnews.innerText = `오늘 실적: ${totalC} / 16세트 (${totalC * 5}장)`;

        const daemonRunning = currentSummary.daemon_running ? (currentSummary.daemon_running[brand] || currentSummary.daemon_running['all']) : false;
        const badgeShorts = document.getElementById(`badge-status-${brand}-shorts`);
        const badgeCardnews = document.getElementById(`badge-status-${brand}-cardnews`);
        const btnDaemonShorts = document.getElementById(`btn-daemon-gb-${brand}-shorts`);
        const btnDaemonCardnews = document.getElementById(`btn-daemon-gb-${brand}-cardnews`);
        
        if (daemonRunning) {
            if (badgeShorts) {
                badgeShorts.innerHTML = "🟢 1일 2슬롯 무인 가동 중";
                badgeShorts.style.color = "#34D399";
                badgeShorts.style.background = "rgba(16,185,129,0.15)";
            }
            if (badgeCardnews) {
                badgeCardnews.innerHTML = "🟢 1일 2슬롯 무인 가동 중";
                badgeCardnews.style.color = "#34D399";
                badgeCardnews.style.background = "rgba(16,185,129,0.15)";
            }
            if (btnDaemonShorts) {
                btnDaemonShorts.innerHTML = "🔄 24h 가동 중 🟢";
                btnDaemonShorts.style.background = "#059669";
            }
            if (btnDaemonCardnews) {
                btnDaemonCardnews.innerHTML = "🔄 24h 가동 중 🟢";
                btnDaemonCardnews.style.background = "#059669";
            }
        } else {
            if (btnDaemonShorts) {
                btnDaemonShorts.innerHTML = "🚀 8개국 무인 가동";
                btnDaemonShorts.style.background = "linear-gradient(135deg, #10B981, #059669)";
            }
            if (btnDaemonCardnews) {
                btnDaemonCardnews.innerHTML = "🚀 8개국 무인 가동";
                btnDaemonCardnews.style.background = "linear-gradient(135deg, #10B981, #059669)";
            }
        }
    }
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
window.setMediaEngine = setMediaEngine;
window.loadMediaEngineSettings = loadMediaEngineSettings;
window.triggerGoldenBatchRun = triggerGoldenBatchRun;
window.startGoldenBatchDaemon = startGoldenBatchDaemon;
window.stopGoldenBatchDaemon = stopGoldenBatchDaemon;
window.updateGoldenBatchPanel = updateGoldenBatchPanel;

// 초기화 시 엔진 상태 로드
document.addEventListener("DOMContentLoaded", () => {
    setTimeout(loadMediaEngineSettings, 200);
    setTimeout(() => {
        if (typeof updateGoldenBatchPanel === "function") updateGoldenBatchPanel();
    }, 250);
});

