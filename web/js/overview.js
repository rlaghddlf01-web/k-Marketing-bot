// ==========================================
// [모듈 2] overview.js: 대시보드 & 8대 AI 허브 24시간 무인 관제 전담 모듈
// ==========================================



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

// 0. 각 채널(24개 허브) 고유의 브랜드 다채색(Multicolor) 테마 정의
function getHubColorTheme(key, index) {
    const themes = {
        // 1. 미디어 / 영상 / 숏폼
        shorts: {
            primary: "#EF4444",
            startGradient: "linear-gradient(135deg, #EF4444 0%, #DC2626 100%)",
            actionBg: "#FEF2F2",
            actionBorder: "#FECACA",
            actionColor: "#B91C1C",
            batchGradient: "linear-gradient(135deg, #F43F5E 0%, #E11D48 100%)"
        },
        cardnews: {
            primary: "#EC4899",
            startGradient: "linear-gradient(135deg, #EC4899 0%, #DB2777 100%)",
            actionBg: "#FDF2F8",
            actionBorder: "#FBCFE8",
            actionColor: "#BE185D",
            batchGradient: "linear-gradient(135deg, #D946EF 0%, #C026D3 100%)"
        },
        // 2. 글로벌 SNS
        reddit: {
            primary: "#FF4500",
            startGradient: "linear-gradient(135deg, #FF4500 0%, #EA580C 100%)",
            actionBg: "#FFF7ED",
            actionBorder: "#FED7AA",
            actionColor: "#C2410C"
        },
        fb_groups: {
            primary: "#1877F2",
            startGradient: "linear-gradient(135deg, #1877F2 0%, #0284C7 100%)",
            actionBg: "#EFF6FF",
            actionBorder: "#BFDBFE",
            actionColor: "#1D4ED8"
        },
        blog: {
            primary: "#2563EB",
            startGradient: "linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)",
            actionBg: "#F0F9FF",
            actionBorder: "#BAE6FD",
            actionColor: "#0369A1"
        },
        seo: {
            primary: "#0EA5E9",
            startGradient: "linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%)",
            actionBg: "#F0FDFA",
            actionBorder: "#99F6E4",
            actionColor: "#0F766E"
        },
        threads: {
            primary: "#334155",
            startGradient: "linear-gradient(135deg, #475569 0%, #1E293B 100%)",
            actionBg: "#F8FAFC",
            actionBorder: "#CBD5E1",
            actionColor: "#334155"
        },
        // 3. 네이버 계열 (고유 그린 & 틸 계열 분화)
        naver_clip: {
            primary: "#059669",
            startGradient: "linear-gradient(135deg, #10B981 0%, #059669 100%)",
            actionBg: "#ECFDF5",
            actionBorder: "#A7F3D0",
            actionColor: "#047857"
        },
        naver_blog: {
            primary: "#03C75A",
            startGradient: "linear-gradient(135deg, #03C75A 0%, #029F48 100%)",
            actionBg: "#F0FDF4",
            actionBorder: "#BBF7D0",
            actionColor: "#15803D"
        },
        naver_post: {
            primary: "#0D9488",
            startGradient: "linear-gradient(135deg, #0D9488 0%, #0F766E 100%)",
            actionBg: "#CCFBF1",
            actionBorder: "#99F6E4",
            actionColor: "#115E59"
        },
        search_advisor: {
            primary: "#0284C7",
            startGradient: "linear-gradient(135deg, #0284C7 0%, #0369A1 100%)",
            actionBg: "#F0F9FF",
            actionBorder: "#BAE6FD",
            actionColor: "#075985"
        },
        naver_kin: {
            primary: "#16A34A",
            startGradient: "linear-gradient(135deg, #22C55E 0%, #16A34A 100%)",
            actionBg: "#DCFCE7",
            actionBorder: "#86EFAC",
            actionColor: "#166534"
        },
        naver_cafe: {
            primary: "#15803D",
            startGradient: "linear-gradient(135deg, #16A34A 0%, #15803D 100%)",
            actionBg: "#F0FDF4",
            actionBorder: "#BBF7D0",
            actionColor: "#14532D"
        },
        // 4. 카카오 계열 & 티스토리
        tistory: {
            primary: "#F97316",
            startGradient: "linear-gradient(135deg, #FB923C 0%, #EA580C 100%)",
            actionBg: "#FFF7ED",
            actionBorder: "#FED7AA",
            actionColor: "#C2410C"
        },
        brunch: {
            primary: "#78350F",
            startGradient: "linear-gradient(135deg, #92400E 0%, #78350F 100%)",
            actionBg: "#FEF3C7",
            actionBorder: "#FDE68A",
            actionColor: "#92400E"
        },
        daum_cafe: {
            primary: "#D97706",
            startGradient: "linear-gradient(135deg, #F59E0B 0%, #D97706 100%)",
            actionBg: "#FFFBEB",
            actionBorder: "#FDE68A",
            actionColor: "#B45309"
        },
        kakao_channel: {
            primary: "#EAB308",
            startGradient: "linear-gradient(135deg, #FACC15 0%, #EAB308 100%)",
            actionBg: "#FEFCE8",
            actionBorder: "#FEF08A",
            actionColor: "#854D0E"
        },
        // 5. 대형 커뮤니티 (차별화된 다채로운 색상)
        ppomppu: {
            primary: "#4F46E5",
            startGradient: "linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)",
            actionBg: "#EEF2FF",
            actionBorder: "#C7D2FE",
            actionColor: "#4338CA"
        },
        dcinside: {
            primary: "#2563EB",
            startGradient: "linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)",
            actionBg: "#EFF6FF",
            actionBorder: "#BFDBFE",
            actionColor: "#1E40AF"
        },
        bobaedream: {
            primary: "#7C3AED",
            startGradient: "linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)",
            actionBg: "#F5F3FF",
            actionBorder: "#DDD6FE",
            actionColor: "#6D28D9"
        },
        nate_pann: {
            primary: "#E11D48",
            startGradient: "linear-gradient(135deg, #F43F5E 0%, #E11D48 100%)",
            actionBg: "#FFF1F2",
            actionBorder: "#FECDD3",
            actionColor: "#BE123C"
        },
        fmkorea: {
            primary: "#0284C7",
            startGradient: "linear-gradient(135deg, #38BDF8 0%, #0284C7 100%)",
            actionBg: "#F0F9FF",
            actionBorder: "#BAE6FD",
            actionColor: "#0369A1"
        },
        twitter_x: {
            primary: "#0F172A",
            startGradient: "linear-gradient(135deg, #334155 0%, #0F172A 100%)",
            actionBg: "#F8FAFC",
            actionBorder: "#CBD5E1",
            actionColor: "#0F172A"
        }
    };

    if (themes[key]) return themes[key];

    // Fallback: 다채로운 프리미엄 순환 팔레트
    const palette = [
        { primary: "#2563EB", startGradient: "linear-gradient(135deg, #3B82F6, #1D4ED8)", actionBg: "#EFF6FF", actionBorder: "#BFDBFE", actionColor: "#1E40AF" },
        { primary: "#059669", startGradient: "linear-gradient(135deg, #10B981, #059669)", actionBg: "#ECFDF5", actionBorder: "#A7F3D0", actionColor: "#047857" },
        { primary: "#7C3AED", startGradient: "linear-gradient(135deg, #8B5CF6, #7C3AED)", actionBg: "#F5F3FF", actionBorder: "#DDD6FE", actionColor: "#6D28D9" },
        { primary: "#D97706", startGradient: "linear-gradient(135deg, #F59E0B, #D97706)", actionBg: "#FFFBEB", actionBorder: "#FDE68A", actionColor: "#B45309" },
        { primary: "#E11D48", startGradient: "linear-gradient(135deg, #F43F5E, #E11D48)", actionBg: "#FFF1F2", actionBorder: "#FECDD3", actionColor: "#BE123C" },
        { primary: "#0D9488", startGradient: "linear-gradient(135deg, #14B8A6, #0D9488)", actionBg: "#CCFBF1", actionBorder: "#99F6E4", actionColor: "#115E59" },
        { primary: "#4F46E5", startGradient: "linear-gradient(135deg, #6366F1, #4F46E5)", actionBg: "#EEF2FF", actionBorder: "#C7D2FE", actionColor: "#4338CA" },
        { primary: "#EA580C", startGradient: "linear-gradient(135deg, #FB923C, #EA580C)", actionBg: "#FFF7ED", actionBorder: "#FED7AA", actionColor: "#C2410C" }
    ];
    return palette[(index || 0) % palette.length];
}

// 1. 대시보드 24대 AI 마케팅 허브 그리드 동적 렌더링 (APP_PIPELINES 모듈 연동)
function renderHubGrid(btn) {
    if (btn) animateRefreshBtn(btn, "허브 그리드가 새로고침되었습니다! 🔄");
    const container = document.getElementById("hub-grid-container");
    const panelTitle = document.getElementById("hub-panel-title");
    const panelDesc = document.getElementById("hub-panel-desc");
    if (!container) return;

    const brand = currentBrand || "aura";
    const app = (typeof APP_PIPELINES !== "undefined" && APP_PIPELINES[brand]) ? APP_PIPELINES[brand] : APP_PIPELINES["aura"];

    if (panelTitle) panelTitle.innerText = `🎯 24대 AI 마케팅 허브 & 24시간 무인 자율 공장`;
    if (panelDesc) panelDesc.innerText = `숏폼, 카드뉴스, 레딧, 페이스북, 블로그, 구글 색인 핑, 스레드 및 국내 16대 포털/커뮤니티 채널을 24시간 자율 가동합니다. (텔레그램은 상단 전용 사령부에서 통합 관제)`;

    container.innerHTML = app.hubs.map((h, idx) => {
        const theme = getHubColorTheme(h.key, idx);
        const isShorts = h.key === "shorts";
        const isCardnews = h.key === "cardnews";
        const isOmniBlog = h.key === "omni_blog";
        const isThreads = h.key === "threads";
        const isSeo = h.key === "seo";
        const isKin = h.key === "naver_kin" || h.isKin;
        const isReddit = h.key === "reddit";
        const runActionText = isShorts 
            ? "🎬 완성 숏폼 원클릭 제작" 
            : isCardnews 
            ? "📸 카드뉴스 원클릭 제작" 
            : isOmniBlog 
            ? "🚀 옴니블로그 즉시 1회 발행" 
            : isThreads
            ? "📜 스토리 타래 1회 발행"
            : isSeo
            ? "🌐 구글·네이버 동시 색인 핑"
            : isKin
            ? "💡 지식iN 실시간 1회 낚아채기"
            : isReddit
            ? "🤖 레딧 1회 스텔스 침투"
            : "⚡ 즉시 1회 시험 실행";
        const runActionOnClick = isOmniBlog 
            ? `publishOmniBlog('${brand}')`
            : isSeo
            ? `triggerSeoPing('${brand}', this)`
            : isKin
            ? `triggerKinCatch('${brand}', this)`
            : `runModule('${brand}_${h.key}')`;

        // 🌐 SEO 전용 서치콘솔 바로가기 링크 그룹
        const seoConsoleLinks = isSeo ? `
            <div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:8px;padding-top:8px;border-top:1px dashed #E5DDD1;">
                <a href="${h.googleConsoleUrl || 'https://search.google.com/search-console'}" target="_blank" rel="noopener noreferrer" style="font-size:10.5px;font-weight:700;color:#2563EB;background:#EFF6FF;border:1px solid #BFDBFE;padding:3px 6px;border-radius:6px;text-decoration:none;display:inline-flex;align-items:center;gap:3px;" title="구글 서치콘솔 관리자 페이지 열기">
                    <span>🔍 구글 콘솔 ↗</span>
                </a>
                <a href="${h.naverAdvisorUrl || 'https://searchadvisor.naver.com/console/board'}" target="_blank" rel="noopener noreferrer" style="font-size:10.5px;font-weight:700;color:#059669;background:#ECFDF5;border:1px solid #A7F3D0;padding:3px 6px;border-radius:6px;text-decoration:none;display:inline-flex;align-items:center;gap:3px;" title="네이버 서치어드바이저 관리자 페이지 열기">
                    <span>🧭 네이버 콘솔 ↗</span>
                </a>
                <a href="${h.sitemapUrl || '#'}" target="_blank" rel="noopener noreferrer" style="font-size:10.5px;font-weight:700;color:#7C3AED;background:#F5F3FF;border:1px solid #DDD6FE;padding:3px 6px;border-radius:6px;text-decoration:none;display:inline-flex;align-items:center;gap:3px;" title="등록된 XML 사이트맵 보기">
                    <span>📄 사이트맵 ↗</span>
                </a>
            </div>
        ` : '';

        // 🤖 레딧 전용 2단계 족집게 스텔스 위젯
        const redditWidget = isReddit ? `
            <div style="margin-top:8px;padding-top:8px;border-top:1px dashed #E5DDD1;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                    <span style="font-size:11px;font-weight:700;color:#EA580C;">🛡️ 스텔스 쿼터:</span>
                    <span style="font-size:11px;font-weight:800;color:#1E1B18;background:#FFF7ED;border:1px solid #FED7AA;padding:2px 8px;border-radius:10px;">
                        홍보 4회 + 비홍보 4회
                    </span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                    <span style="font-size:11px;color:#6E665E;">침투 원칙:</span>
                    <span style="font-size:10.5px;font-weight:700;color:#059669;">Zero URL + 구글 검색 유도</span>
                </div>
                <div style="display:flex;gap:4px;">
                    <a href="${h.redditUrl || 'https://www.reddit.com/r/stocks/'}" target="_blank" rel="noopener noreferrer" style="font-size:10.5px;font-weight:700;color:#EA580C;background:#FFF7ED;border:1px solid #FED7AA;padding:3px 6px;border-radius:6px;text-decoration:none;display:inline-flex;align-items:center;gap:3px;" title="레딧 타겟 서브레딧 열기">
                        <span>🤖 타겟 서브레딧 ↗</span>
                    </a>
                </div>
            </div>
        ` : '';

        // 🌐 옴니블로그 전용 24시간 무인 정시 스케줄러 배지 위젯 (15분 시차 분산)
        const blogScheduleText = brand === "aura" ? "하루 3회 (09:45 / 14:45 / 19:45)"
                               : brand === "stock" ? "하루 3회 (10:15 / 15:15 / 20:15)"
                               : "하루 3회 (10:00 / 15:00 / 20:00)";

        const blogWidget = isOmniBlog ? `
            <div style="margin-top:8px;padding-top:8px;border-top:1px dashed #E5DDD1;">
                <div style="display:flex;justify-content:space-between;align-items:center;background:#EFF6FF;border:1px solid #BFDBFE;padding:5px 8px;border-radius:6px;font-size:11px;font-weight:700;color:#1D4ED8;">
                    <span>⏰ 15분 시차 정시 스케줄:</span>
                    <span style="color:#2563EB;">${blogScheduleText}</span>
                </div>
            </div>
        ` : '';

        // 💡 지식iN 전용 실시간 쿼터 & 바로가기 위젯
        const kinWidget = isKin ? `
            <div style="margin-top:8px;padding-top:8px;border-top:1px dashed #E5DDD1;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                    <span style="font-size:11px;font-weight:700;color:#059669;">🎯 일일 선발 쿼터:</span>
                    <span id="kin-quota-${brand}" style="font-size:11px;font-weight:800;color:#1E1B18;background:#ECFDF5;border:1px solid #A7F3D0;padding:2px 8px;border-radius:10px;">
                        <span id="kin-count-${brand}">0</span> / 10개 (엄선 26:1)
                    </span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                    <span style="font-size:11px;color:#6E665E;">무인 레이더 감시:</span>
                    <span id="kin-slot-${brand}" style="font-size:10.5px;font-weight:700;color:#2563EB;">🌙 24시간 실시간 감지</span>
                </div>
                <div id="kin-recent-${brand}" style="font-size:11px;color:#4A443D;background:#FFFFFF;padding:6px 8px;border-radius:6px;border:1px solid #E5DDD1;margin-bottom:6px;max-height:45px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                    최근 낚아챈 질문: 대기 중
                </div>
                <div style="display:flex;gap:4px;">
                    <a href="https://kin.naver.com" target="_blank" rel="noopener noreferrer" style="font-size:10.5px;font-weight:700;color:#059669;background:#ECFDF5;border:1px solid #A7F3D0;padding:3px 6px;border-radius:6px;text-decoration:none;display:inline-flex;align-items:center;gap:3px;" title="네이버 지식iN 바로가기">
                        <span>💡 네이버 지식iN ↗</span>
                    </a>
                </div>
            </div>
        ` : '';

        return `
        <div class="action-card" id="card-${brand}-${h.key}" style="background:#F6F1EA;border:1px solid #E5DDD1;border-top:3.5px solid ${theme.primary};border-radius:14px;padding:16px;display:flex;flex-direction:column;justify-content:space-between;gap:12px;box-shadow:var(--shadow-md);transition:transform 0.25s ease, box-shadow 0.25s ease;">
            <div>
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                    <span style="font-size:24px;width:38px;height:38px;display:flex;align-items:center;justify-content:center;background:#FFFFFF;border:1px solid #E5DDD1;border-radius:8px;">${h.icon}</span>
                    <div>
                        <div style="font-size:11px;color:${theme.primary};font-weight:800;">#${idx+1} 마케팅 허브</div>
                        <h4 style="margin:0;font-size:14px;font-weight:700;color:#1E1B18;">${h.name}</h4>
                    </div>
                </div>
                <p style="font-size:11.5px;color:#6E665E;margin:0 0 10px 0;line-height:1.45;">${h.desc}</p>
                ${seoConsoleLinks}
                ${redditWidget}
                ${blogWidget}
                ${kinWidget}

                <!-- 실시간 24시간 가동 상태 바 -->
                <div style="display:flex;justify-content:space-between;align-items:center;background:#FFFFFF;padding:6px 10px;border-radius:8px;border:1px solid #E5DDD1;margin-top:8px;">
                    <span style="font-size:11px;color:#6E665E;">실시간 상태:</span>
                    <span id="badge-status-${brand}-${h.key}" class="badge-idle" style="font-size:11px;font-weight:700;padding:2px 8px;border-radius:10px;background:#F6F1EA;color:#6E665E;border:1px solid #E5DDD1;">
                        ⚪ 대기
                    </span>
                </div>
            </div>

            <div>
                <!-- 1:1 무인 가동 및 정지 버튼 그룹 -->
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px;">
                    <button class="btn" id="btn-start-${brand}-${h.key}" data-original-bg="${theme.startGradient}" onclick="startChannelDaemon('${brand}_${h.key}', this)" style="font-size:11.5px;padding:7px 4px;font-weight:800;background:${theme.startGradient};color:#FFFFFF;border:none;border-radius:8px;box-shadow:0 3px 8px rgba(0,0,0,0.12);cursor:pointer;" title="24시간 무인 자동 배포 데몬 시작">
                        🚀 무인 가동
                    </button>
                    <button class="btn btn-stop" id="btn-stop-${brand}-${h.key}" onclick="stopChannelDaemon('${brand}_${h.key}', this)" style="font-size:11.5px;padding:7px 4px;font-weight:700;border-radius:8px;cursor:pointer;" title="무인 데몬 정지">
                        ⏹️ 정지
                    </button>
                </div>
                ${isShorts ? `
                <div style="display:grid;grid-template-columns:1.2fr 1fr;gap:6px;">
                    <button class="btn btn-action" id="btn-run-${brand}-${h.key}" onclick="runModule('${brand}_shorts')" style="font-size:11px;padding:7px 2px;background:${theme.actionBg};border:1.5px solid ${theme.actionBorder};color:${theme.actionColor};font-weight:800;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.05);cursor:pointer;" title="1번 탈출전화부터 8번 안심레이더까지 8대 주제 숏폼을 순차적으로 100% 무인 자동 렌더링">
                        🎬 8대 숏폼 순차 제작
                    </button>
                    <button class="btn btn-action" onclick="runModule('${brand}_master_photo')" style="font-size:11px;padding:7px 2px;background:#FFFFFF;border:1px solid #CBD5E1;color:#475569;font-weight:700;border-radius:8px;cursor:pointer;" title="텍스트 프롬프트로 28세 여성 실사 인물 사진만 단독 생성">
                        📸 인물 사진 생성
                    </button>
                </div>
                ` : `
                <button class="btn btn-action" id="${isOmniBlog ? `btn-omni-${brand}` : isSeo ? `btn-seo-${brand}` : isKin ? `btn-kin-${brand}` : `btn-run-${brand}-${h.key}`}" onclick="${runActionOnClick}" style="width:100%;font-size:11.5px;padding:7px 0;background:${theme.actionBg};border:1px solid ${theme.actionBorder};color:${theme.actionColor};font-weight:700;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.04);cursor:pointer;">
                    ${runActionText}
                </button>
                `}
            </div>
        </div>
    `}).join("");

    setTimeout(() => {
        loadMediaEngineSettings();
        loadKinStats(brand);
    }, 50);
}

// 🌐 3대 슈퍼앱 전용 구글 & 네이버 실시간 색인 핑 전송 트리거
async function triggerSeoPing(brand, btn) {
    const nameMap = { "aura": "💖 Aura", "insurance": "🛡️ 보험비교", "stock": "📈 주식AI", "kmarket": "🛒 K-Market", "easytax": "💰 EasyTax" };
    const brandName = nameMap[brand] || brand.toUpperCase();
    
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spin-icon" style="display:inline-block;animation:rotateSpin 0.6s linear infinite;">🔄</span> 2대 포털 핑 전송 중...`;
    }
    appendLog(`[SEO Ping] 🌐 ${brandName} 구글 서치콘솔 + 네이버 서치어드바이저 동시 색인 핑 전송 시작...`, "info");
    showToast(`🌐 ${brandName} 구글·네이버 검색엔진 동시 색인 핑을 전송합니다!`, "info");

    try {
        const res = await fetch(`/api/seo/ping/${brand}`, { method: "POST" });
        const data = await res.json();
        showToast(data.message || `🌐 ${brandName} 2대 검색엔진 색인 핑 완료!`, "success");
        appendLog(`[SEO Ping Success] 🎉 ${data.message || '색인 핑 전송 완료'}`, "success");
        if (typeof fetchStatus === "function") fetchStatus();
    } catch (e) {
        showToast(`❌ 색인 핑 요청 실패: ${e}`, "error");
        appendLog(`[SEO Ping Error] ❌ ${e}`, "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `🌐 구글·네이버 동시 색인 핑`;
        }
    }
}

// 💡 Aura 및 브랜드 전용 네이버 지식iN 100대 키워드 실시간 낚아채기 트리거
async function triggerKinCatch(brand, btn) {
    const nameMap = { "aura": "💖 Aura 데이팅", "insurance": "🛡️ 보험비교", "stock": "📈 주식AI" };
    const brandName = nameMap[brand] || brand.toUpperCase();

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spin-icon" style="display:inline-block;animation:rotateSpin 0.6s linear infinite;">🔄</span> 100대 키워드 낚아채는 중...`;
    }
    appendLog(`[지식iN 레이더] 💡 ${brandName} 100대 황금 키워드 실시간 질문 스캔 & 85점 심사 시작...`, "info");
    showToast(`💡 ${brandName} 네이버 지식iN 실시간 낚아채기를 실행합니다!`, "info");

    try {
        const res = await fetch(`/api/kin/${brand}/run`, { method: "POST" });
        const data = await res.json();
        showToast(data.message || `💡 ${brandName} 지식iN 낚아채기 가동 완료!`, "success");
        appendLog(`[지식iN 가동] 🎉 ${data.message || '완료'}`, "success");
        setTimeout(() => loadKinStats(brand), 3000);
    } catch (e) {
        showToast(`❌ 지식iN 실행 실패: ${e}`, "error");
        appendLog(`[지식iN Error] ❌ ${e}`, "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `💡 지식iN 실시간 1회 낚아채기`;
        }
    }
}

// 💡 네이버 지식iN 실시간 일일 쿼터 및 최근 등록 내역 조회
async function loadKinStats(brand = "aura") {
    try {
        const res = await fetch(`/api/kin/${brand}/history`);
        const data = await res.json();
        if (data.success) {
            const countEl = document.getElementById(`kin-count-${brand}`);
            if (countEl) countEl.innerText = data.daily_total || 0;
            const slotEl = document.getElementById(`kin-slot-${brand}`);
            if (slotEl && data.current_slot) slotEl.innerText = data.current_slot.name || "24시간 실시간 감지";
            const recentEl = document.getElementById(`kin-recent-${brand}`);
            if (recentEl && data.history && data.history.length > 0) {
                const latest = data.history[0];
                const liveUrl = latest.published_url || latest.url || "#";
                recentEl.innerHTML = `<span style="color:#64748B;font-size:10.5px;">[${latest.created_at || '-'}]</span> <a href="${liveUrl}" target="_blank" style="color:#0284C7;text-decoration:underline;font-weight:700;" title="${latest.title}">${latest.title}</a>`;
            }
        }
    } catch (e) {
        console.debug("지식iN 통계 로드 예외:", e);
    }
}

// 2. 24시간 무인 자율 채널 데몬 시작
async function startChannelDaemon(moduleKey, btn) {
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spin-icon" style="display:inline-block;animation:rotateSpin 0.6s linear infinite;">🔄</span> 가동 중...`;
    }
    const cleanKey = moduleKey.replace("kmarket_", "").replace("easytax_", "").replace("stock_", "").replace("aura_", "").replace("insurance_", "");
    const brandPrefix = moduleKey.startsWith("aura_") ? "aura" : moduleKey.startsWith("insurance_") ? "insurance" : moduleKey.startsWith("stock_") ? "stock" : moduleKey.startsWith("easytax_") ? "easytax" : "kmarket";
    const badge = document.getElementById(`badge-status-${brandPrefix}-${cleanKey}`);
    if (badge) {
        badge.className = "badge-running";
        badge.style.background = "#DCFCE7";
        badge.style.color = "#15803D";
        badge.style.border = "1px solid #86EFAC";
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
            btn.style.background = btn.getAttribute("data-original-bg") || "";
        }
    }
}

// 3. 24시간 무인 자율 채널 데몬 정지
async function stopChannelDaemon(moduleKey, btn) {
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `⏹️ 정지 중...`;
    }
    const cleanKey = moduleKey.replace("kmarket_", "").replace("easytax_", "").replace("stock_", "").replace("aura_", "").replace("insurance_", "");
    const brandPrefix = moduleKey.startsWith("aura_") ? "aura" : moduleKey.startsWith("insurance_") ? "insurance" : moduleKey.startsWith("stock_") ? "stock" : moduleKey.startsWith("easytax_") ? "easytax" : "kmarket";
    const badge = document.getElementById(`badge-status-${brandPrefix}-${cleanKey}`);
    if (badge) {
        badge.className = "badge-idle";
        badge.style.background = "#F6F1EA";
        badge.style.color = "#6E665E";
        badge.style.border = "1px solid #E5DDD1";
        badge.innerHTML = "⚪ 대기";
    }

    try {
        const res = await fetch(`/api/channel/stop/${moduleKey}`, { method: "POST" });
        const data = await res.json();
        showToast(data.message || `[${moduleKey}] 무인 가동이 정지되었습니다.`, "info");
        appendLog(`[Daemon Stop] ${data.message || moduleKey}`, "warning");
        const startBtn = document.getElementById(`btn-start-${brandPrefix}-${cleanKey}`);
        if (startBtn) {
            startBtn.innerHTML = "🚀 무인 가동";
            startBtn.style.background = startBtn.getAttribute("data-original-bg") || "";
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

// 4. 채널 뱃지 동기화는 하단의 실시간 세션/장애 감지 통합 updateChannelBadges()를 단일 사용합니다.


// 5. 사이드바 데몬 시작/정지 & 3대 슈퍼앱 마스터 제어
async function startStockDaemon() {
    try {
        const res = await fetch("/api/stock/start", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "📈 Stock Master 주식 AI 무인 봇 사이클이 가동되었습니다! 🚀", "success");
        fetchStatus();
    } catch (e) {
        showToast("주식 AI 가동 통신 오류", "error");
    }
}

async function stopStockDaemon() {
    try {
        const res = await fetch("/api/stock/stop", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "📈 Stock Master 주식 AI 봇이 정지되었습니다.", "info");
        fetchStatus();
    } catch (e) {
        showToast("주식 AI 정지 통신 오류", "error");
    }
}

async function startAuraDaemon() {
    try {
        const res = await fetch("/api/aura/start", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "💖 Aura 데이팅 무인 봇 사이클이 가동되었습니다! 🚀", "success");
        fetchStatus();
    } catch (e) {
        showToast("Aura 가동 통신 오류", "error");
    }
}

async function stopAuraDaemon() {
    try {
        const res = await fetch("/api/aura/stop", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "💖 Aura 데이팅 봇이 정지되었습니다.", "info");
        fetchStatus();
    } catch (e) {
        showToast("Aura 정지 통신 오류", "error");
    }
}

async function startInsuranceDaemon() {
    try {
        const res = await fetch("/api/insurance/start", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "🛡️ InsureBalance 보험비교 무인 봇 사이클이 가동되었습니다! 🚀", "success");
        fetchStatus();
    } catch (e) {
        showToast("보험비교 가동 통신 오류", "error");
    }
}

async function stopInsuranceDaemon() {
    try {
        const res = await fetch("/api/insurance/stop", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "🛡️ InsureBalance 보험비교 봇이 정지되었습니다.", "info");
        fetchStatus();
    } catch (e) {
        showToast("보험비교 정지 통신 오류", "error");
    }
}

async function startKMarketDaemon() {
    try {
        const res = await fetch("/api/kmarket/start", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "KTRS 마켓 무인 성장봇 사이클이 가동되었습니다! 🚀", "success");
        fetchStatus();
    } catch (e) {
        showToast("KTRS 마켓 가동 통신 오류", "error");
    }
}

async function stopKMarketDaemon() {
    try {
        const res = await fetch("/api/kmarket/stop", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "KTRS 마켓 봇이 정지되었습니다.", "info");
        fetchStatus();
    } catch (e) {
        showToast("KTRS 마켓 정지 통신 오류", "error");
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
    showToast("⚡ 3대 슈퍼앱 전체 봇을 동시 가동합니다! 🚀", "success");
    await startStockDaemon();
    await startAuraDaemon();
    await startInsuranceDaemon();
    if (typeof loadTelegramCommunityStats === "function") loadTelegramCommunityStats();
}

async function stopAllBots() {
    showToast("🛑 모든 무인 봇을 정지합니다.", "warning");
    await stopStockDaemon();
    await stopAuraDaemon();
    await stopInsuranceDaemon();
    if (typeof loadTelegramCommunityStats === "function") loadTelegramCommunityStats();
}

// 🚨 6-1. 실시간 비상관제 & ALL CLEAR 가드 배너 렌더링
let lastEmergencyStatus = null;
let lastSummary = null;

function renderEmergencyGuardBanner(emergencyStatus, summary) {
    const container = document.getElementById("emergency-guard-banner-container");
    if (!container) return;

    const activeBrand = (typeof currentBrand !== 'undefined') ? currentBrand : 'all';
    const liveFeed = (typeof window.__lastLiveFeed !== "undefined") ? window.__lastLiveFeed : {};
    const brands = liveFeed.brands || {};

    const realAlerts = [];
    Object.keys(brands).forEach(bKey => {
        if (activeBrand !== "all" && bKey !== activeBrand) return;
        const bData = brands[bKey];
        const chs = bData.blog?.channels || {};
        const bName = bData.brand_name || bKey;

        // 티스토리 세션 만료 실시간 감지
        if (chs.tistory?.is_session_expired) {
            const batName = bKey === "aura" ? "[1회연동]_아우라_티스토리_영구로그인.bat"
                          : bKey === "insurance" ? "[1회연동]_보험비교_티스토리_영구로그인.bat"
                          : "[1회연동]_주식AI_티스토리_영구로그인.bat";
            realAlerts.push({
                brand: bName,
                title: `🔴 [${bName}] 티스토리 카카오 로그인 세션 만료`,
                message: "카카오 세션 쿠키가 만료되어 티스토리 자동 포스팅이 차단되었습니다.",
                action_guide: `바탕화면의 [${batName}] 배치 파일을 1회 실행하여 로그인해 주세요.`
            });
        }

        // 네이버 블로그 에러 실시간 감지
        if (chs.naver_blog?.status === "error") {
            realAlerts.push({
                brand: bName,
                title: `🔴 [${bName}] 네이버 블로그 포스팅 오류`,
                message: chs.naver_blog.message || "네이버 블로그 로그인 및 세션 확인이 필요합니다.",
                action_guide: `바탕화면의 [1회연동]_..._네이버_영구로그인.bat 실행 필요`
            });
        }
    });

    if (realAlerts.length > 0) {
        // 🔴 긴급 장애 경보 배너 (RED) - 세션 만료 및 에러 직격 표출
        container.innerHTML = `
            <div class="emergency-alert-box" style="background:#FEF2F2;border:2.5px solid #EF4444;border-radius:14px;padding:16px 20px;box-shadow:0 8px 25px rgba(239,68,68,0.25);">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:12px;">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <span style="font-size:26px;">🚨</span>
                        <div>
                            <h3 style="margin:0;font-size:16px;font-weight:900;color:#991B1B;">[긴급 조치 필요] 실시간 채널 장애 ${realAlerts.length}건 감지</h3>
                            <span style="font-size:12px;color:#B91C1C;font-weight:700;">아래 표시된 항목의 조치 방법을 확인하고 1회 로그인을 완료해 주세요.</span>
                        </div>
                    </div>
                    <span class="badge" style="background:#DC2626;color:#FFFFFF;font-weight:800;padding:6px 12px;border-radius:8px;font-size:12px;">
                        🔴 ACTION REQUIRED
                    </span>
                </div>
                <div style="display:flex;flex-direction:column;gap:8px;">
                    ${realAlerts.map(a => `
                        <div style="background:#FFFFFF;border:1.5px solid #FECACA;border-left:5px solid #DC2626;border-radius:8px;padding:12px 16px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
                            <div>
                                <div style="font-size:13.5px;font-weight:800;color:#991B1B;">${a.title}</div>
                                <div style="font-size:12px;color:#4B5563;margin-top:2px;">${a.message}</div>
                            </div>
                            <div style="font-size:12px;font-weight:800;color:#991B1B;background:#FEE2E2;padding:6px 12px;border-radius:6px;border:1px solid #FCA5A5;">
                                👉 ${a.action_guide}
                            </div>
                        </div>
                    `).join("")}
                </div>
            </div>
        `;
    } else {
        container.innerHTML = `
            <div class="all-clear-box" style="background:#F0FDF4;border:1.5px solid #86EFAC;border-radius:12px;padding:12px 18px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="font-size:20px;">🟢</span>
                    <div>
                        <strong style="color:#166534;font-size:14px;">현재 감지된 시스템 장애 0건 (모든 채널 정상)</strong>
                    </div>
                </div>
            </div>
        `;
    }
}

// 🚀 [신규 전광판] 3대 브랜드 실시간 마케팅 무인 발행 라이브 전광판 렌더러
function renderTodayLiveFeedBoard(liveFeed, gpuStatus) {
    const container = document.getElementById("today-live-feed-container");
    if (!container || !liveFeed || !liveFeed.brands) return;

    const summary = liveFeed.summary || {};
    const brands = liveFeed.brands || {};
    const timestamp = liveFeed.timestamp || "";
    const today = liveFeed.today || "";

    // 🎮 GPU 실시간 렌더링 가동 전광판 배너
    let gpuBannerHtml = "";
    if (gpuStatus && (gpuStatus.status === "busy" || gpuStatus.status === "running" || (gpuStatus.current_task && gpuStatus.status !== "idle"))) {
        const taskName = gpuStatus.current_task || "미디어 실사 렌더링 중";
        const isCardnews = taskName.includes("카드뉴스") || taskName.includes("T2I") || taskName.includes("사진");
        const isShorts = taskName.includes("숏폼") || taskName.includes("S2V") || taskName.includes("영상");
        const badgeColor = isCardnews ? "#EC4899" : isShorts ? "#8B5CF6" : "#F59E0B";
        const bgGrad = isCardnews
            ? "linear-gradient(135deg, #FFF1F2 0%, #FDF2F8 50%, #FAF5FF 100%)"
            : "linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 50%, #F0F9FF 100%)";
        const borderCol = isCardnews ? "#F472B6" : "#A78BFA";

        gpuBannerHtml = `
            <div class="gpu-live-status-banner" style="background:${bgGrad};border:2px solid ${borderCol};border-radius:14px;padding:14px 18px;margin-bottom:16px;box-shadow:0 8px 25px rgba(236,72,153,0.18);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;animation:gpuPulseBorder 2s infinite alternate;">
                <div style="display:flex;align-items:center;gap:14px;">
                    <div style="width:44px;height:44px;border-radius:12px;background:#0F172A;display:flex;align-items:center;justify-content:center;font-size:22px;box-shadow:0 4px 12px rgba(0,0,0,0.15);">
                        ${isCardnews ? '🎨' : isShorts ? '🎬' : '⚡'}
                    </div>
                    <div>
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="background:${badgeColor};color:#FFFFFF;font-size:11px;font-weight:800;padding:2px 8px;border-radius:12px;display:inline-flex;align-items:center;gap:5px;">
                                <span class="pulse-dot" style="background:#FFFFFF;width:6px;height:6px;border-radius:50%;display:inline-block;"></span>
                                GPU 실시간 연산 가동 중
                            </span>
                            <span style="font-size:11.5px;color:#64748B;font-weight:600;">🎮 NVIDIA GeForce RTX 5060 Ti (100% 자율 생산)</span>
                        </div>
                        <div style="font-size:14.5px;font-weight:800;color:#0F172A;margin-top:4px;">
                            ${taskName}
                        </div>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <span class="badge" style="background:#ECFDF5;color:#059669;border:1px solid #A7F3D0;font-weight:700;font-size:11.5px;">
                        🟢 렌더링 완료 시 자동 동기화
                    </span>
                    <button class="btn btn-secondary" onclick="switchTabDirect('gallery')" style="font-size:11.5px;padding:6px 12px;">
                        📸 갤러리/사진 확인 →
                    </button>
                </div>
            </div>
        `;
    }

    const brandConfigs = {
        aura: {
            title: "💖 Aura AI 데이팅",
            sub: "2030 소개팅 · 데이팅 앱",
            color: "#EC4899",
            bgGradient: "linear-gradient(135deg, #FFF1F2 0%, #FDF2F8 100%)",
            border: "#FBCFE8",
            badgeBg: "#FCE7F3",
            badgeColor: "#BE185D",
            landing: "https://aura-ai-dating.vercel.app/"
        },
        insurance: {
            title: "🛡️ 보험 리밸런스",
            sub: "실손 · 3대질병 · 보험비교",
            color: "#10B981",
            bgGradient: "linear-gradient(135deg, #ECFDF5 0%, #F0FDF4 100%)",
            border: "#A7F3D0",
            badgeBg: "#D1FAE5",
            badgeColor: "#065F46",
            landing: "https://insure-rebalance.vercel.app/"
        },
        stock: {
            title: "📈 StockMaster AI",
            sub: "국내주식 · 10분 계량 전광판",
            color: "#F59E0B",
            bgGradient: "linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%)",
            border: "#FDE68A",
            badgeBg: "#FEF3C7",
            badgeColor: "#92400E",
            landing: "https://stockmaster-ai.vercel.app/"
        }
    };

    let brandCardsHtml = Object.keys(brandConfigs).map(bKey => {
        const cfg = brandConfigs[bKey];
        const bData = brands[bKey] || {};
        const blog = bData.blog || {};
        const kin = bData.kin || {};
        const shorts = bData.shorts || {};
        const channels = blog.channels || {};
        const shortsPlatforms = shorts.platforms || {};

        // 0. 자체 홈페이지 블로그 (Supabase / 라운지)
        const supa = channels.supabase_research || channels.app_lounge || {};
        let supaHtml = "";
        if (bKey === "stock" && supa.title) {
            supaHtml = `
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:8px 10px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">
                    <div>
                        <div style="display:flex;align-items:center;gap:6px;">
                            <span style="background:#FEF3C7;color:#92400E;font-size:10.5px;font-weight:800;padding:2px 6px;border-radius:4px;">🌐 자체 홈페이지 퀀트 블로그</span>
                            <span style="font-size:10.5px;color:#64748B;">🕒 ${supa.published_at || blog.last_run_time || '-'}</span>
                        </div>
                        <div style="font-size:12px;font-weight:700;color:#0F172A;margin-top:2px;">${supa.title}</div>
                    </div>
                    <a href="${cfg.landing}" target="_blank" style="display:inline-flex;align-items:center;gap:4px;padding:4px 9px;background:#F59E0B;color:#FFFFFF;border-radius:5px;font-size:11px;font-weight:800;text-decoration:none;">
                        <span>🔗 홈페이지 글 열기</span><span>↗</span>
                    </a>
                </div>
            `;
        } else if (bKey === "aura") {
            supaHtml = `
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:8px 10px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">
                    <div>
                        <div style="display:flex;align-items:center;gap:6px;">
                            <span style="background:#FCE7F3;color:#BE185D;font-size:10.5px;font-weight:800;padding:2px 6px;border-radius:4px;">💖 Aura 자체 VIP 라운지</span>
                            <span style="font-size:10.5px;color:#059669;font-weight:700;">🟢 실시간 연동 중</span>
                        </div>
                    </div>
                    <a href="${cfg.landing}" target="_blank" style="display:inline-flex;align-items:center;gap:4px;padding:4px 9px;background:#EC4899;color:#FFFFFF;border-radius:5px;font-size:11px;font-weight:800;text-decoration:none;">
                        <span>🔗 라운지 열기</span><span>↗</span>
                    </a>
                </div>
            `;
        }

        // 1. 네이버 블로그
        const nb = channels.naver_blog || {};
        let naverHtml = "";
        if (nb.is_success && nb.url) {
            naverHtml = `
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:8px 10px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">
                    <div>
                        <div style="display:flex;align-items:center;gap:6px;">
                            <span style="background:#ECFDF5;color:#059669;font-size:10.5px;font-weight:800;padding:2px 6px;border-radius:4px;">🟢 네이버 블로그 (${nb.is_today ? '오늘 발행' : '이전 발행'})</span>
                            <span style="font-size:10.5px;color:#64748B;">🕒 ${nb.published_at || blog.last_run_time || '-'}</span>
                        </div>
                        <div style="font-size:12px;font-weight:700;color:#0F172A;margin-top:2px;">${blog.last_title_naver || blog.last_title || '네이버 글'}</div>
                    </div>
                    <a href="${nb.url}" target="_blank" style="display:inline-flex;align-items:center;gap:4px;padding:4px 9px;background:#03C75A;color:#FFFFFF;border-radius:5px;font-size:11px;font-weight:800;text-decoration:none;">
                        <span>🔗 네이버 글 열기</span><span>↗</span>
                    </a>
                </div>
            `;
        } else {
            const isErr = nb.status === "error";
            naverHtml = `
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:8px 10px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">
                    <div>
                        <div style="display:flex;align-items:center;gap:6px;">
                            <span style="background:${isErr ? '#FEE2E2' : '#FEF3C7'};color:${isErr ? '#DC2626' : '#92400E'};font-size:10.5px;font-weight:700;padding:2px 6px;border-radius:4px;">${isErr ? '🔴 네이버 블로그 에러' : '⚪ 네이버 블로그 미발행'}</span>
                            <span style="font-size:11px;color:${isErr ? '#991B1B' : '#64748B'};font-weight:600;">${nb.message || '오늘자 정기 스케줄 대기 중'}</span>
                        </div>
                    </div>
                    <span style="font-size:10.5px;color:#92400E;background:#FEF3C7;padding:2px 6px;border-radius:4px;font-weight:700;">👉 오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거</span>
                </div>
            `;
        }

        // 2. 티스토리 블로그
        const tb = channels.tistory || {};
        let tistoryHtml = "";
        const batFile = bKey === "aura" ? "[1회연동]_Aura_티스토리_영구로그인.bat" 
                      : bKey === "insurance" ? "[1회연동]_보험비교_티스토리_영구로그인.bat" 
                      : "[1회연동]_주식AI_티스토리_영구로그인.bat";

        if (tb.is_success && tb.url) {
            tistoryHtml = `
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:8px 10px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">
                    <div>
                        <div style="display:flex;align-items:center;gap:6px;">
                            <span style="background:#FFF7ED;color:#C2410C;font-size:10.5px;font-weight:800;padding:2px 6px;border-radius:4px;">🟠 티스토리</span>
                            <span style="font-size:10.5px;color:#64748B;">🕒 ${tb.published_at || '-'}</span>
                        </div>
                    </div>
                    <a href="${tb.url}" target="_blank" style="display:inline-flex;align-items:center;gap:4px;padding:4px 9px;background:#FF5722;color:#FFFFFF;border-radius:5px;font-size:11px;font-weight:800;text-decoration:none;">
                        <span>🔗 티스토리 열기</span><span>↗</span>
                    </a>
                </div>
            `;
        } else if (tb.is_session_expired) {
            tistoryHtml = `
                <div style="background:#FEF2F2;border:1.5px solid #FECACA;border-radius:8px;padding:8px 10px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="background:#FEE2E2;color:#DC2626;font-size:10.5px;font-weight:800;padding:2px 6px;border-radius:4px;">🔴 티스토리 세션 만료</span>
                        <span style="font-size:11px;color:#991B1B;font-weight:700;">⚠️ 조치 필요</span>
                    </div>
                    <div style="font-size:11px;color:#7F1D1D;margin-top:4px;line-height:1.4;">
                        👉 바탕화면의 <strong>${batFile}</strong> 을 실행하여 1회 로그인해 주세요.
                    </div>
                </div>
            `;
        } else {
            const isFail = tb.status === "error" || (tb.message && !tb.message.includes("대기"));
            tistoryHtml = `
                <div style="background:${isFail ? '#FFF1F2' : '#FFFFFF'};border:${isFail ? '1.5px solid #FECDD3' : '1px solid #E2E8F0'};border-radius:8px;padding:8px 10px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="background:${isFail ? '#FFE4E6' : '#F1F5F9'};color:${isFail ? '#E11D48' : '#64748B'};font-size:10.5px;font-weight:800;padding:2px 6px;border-radius:4px;">${isFail ? '❌ 티스토리 미발행 / 오류' : '⚪ 티스토리'}</span>
                        <span style="font-size:11px;color:${isFail ? '#BE123C' : '#64748B'};font-weight:700;">${tb.status || '대기'}</span>
                    </div>
                    <div style="font-size:11px;color:${isFail ? '#9F1239' : '#64748B'};margin-top:4px;line-height:1.4;">
                        ${tb.message ? `💬 사유: ${tb.message}` : '오늘 발행 대기 중'}
                    </div>
                </div>
            `;
        }

        // 3. 4대 숏폼 플랫폼 분리 렌더링
        const yt = shortsPlatforms.youtube || {};
        const insta = shortsPlatforms.instagram || {};
        const fb = shortsPlatforms.facebook || {};
        const clip = shortsPlatforms.naver_clip || {};

        let shortsListHtml = `
            <div style="display:flex;flex-direction:column;gap:6px;">
                <!-- 🔴 YouTube Shorts -->
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:6px;padding:6px 8px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:4px;">
                    <div style="display:flex;align-items:center;gap:6px;overflow:hidden;text-overflow:ellipsis;">
                        <span style="font-size:13px;">🔴</span>
                        <span style="font-size:11px;font-weight:800;color:#0F172A;">유튜브 쇼츠</span>
                        <span style="font-size:10px;color:#64748B;">🕒 ${yt.published_at || '-'}</span>
                    </div>
                    ${yt.url ? `<a href="${yt.url}" target="_blank" style="font-size:10.5px;font-weight:700;color:#DC2626;text-decoration:underline;">🎬 영상 보기 ↗</a>` : `<span style="font-size:10px;color:#94A3B8;">대기</span>`}
                </div>
                <!-- 📸 Instagram Reels -->
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:6px;padding:6px 8px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:4px;">
                    <div style="display:flex;align-items:center;gap:6px;overflow:hidden;text-overflow:ellipsis;">
                        <span style="font-size:13px;">📸</span>
                        <span style="font-size:11px;font-weight:800;color:#0F172A;">인스타 릴스</span>
                        <span style="font-size:10px;color:#64748B;">🕒 ${insta.published_at || '-'}</span>
                    </div>
                    ${(insta.is_success && insta.url) ? `<a href="${insta.url}" target="_blank" style="font-size:10.5px;font-weight:700;color:#E1306C;text-decoration:underline;">🎬 릴스 열기 ↗</a>` : `<span style="font-size:10px;color:#94A3B8;">대기</span>`}
                </div>
                <!-- 🔵 Facebook Reels -->
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:6px;padding:6px 8px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:4px;">
                    <div style="display:flex;align-items:center;gap:6px;overflow:hidden;text-overflow:ellipsis;">
                        <span style="font-size:13px;">🔵</span>
                        <span style="font-size:11px;font-weight:800;color:#0F172A;">페이스북 릴스</span>
                        <span style="font-size:10px;color:#64748B;">🕒 ${fb.published_at || '-'}</span>
                    </div>
                    ${(fb.is_success && fb.url) ? `<a href="${fb.url}" target="_blank" style="font-size:10.5px;font-weight:700;color:#1877F2;text-decoration:underline;">🎬 릴스 열기 ↗</a>` : `<span style="font-size:10px;color:#94A3B8;">대기</span>`}
                </div>
                <!-- 🟢 Naver Clip -->
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:6px;padding:6px 8px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:4px;">
                    <div style="display:flex;align-items:center;gap:6px;overflow:hidden;text-overflow:ellipsis;">
                        <span style="font-size:13px;">🟢</span>
                        <span style="font-size:11px;font-weight:800;color:#0F172A;">네이버 클립</span>
                        <span style="font-size:10px;color:#64748B;">🕒 ${clip.published_at || '-'}</span>
                    </div>
                    ${clip.url ? `<a href="${clip.url}" target="_blank" style="font-size:10.5px;font-weight:700;color:#03C75A;text-decoration:underline;">🟢 클립 열기 ↗</a>` : `<span style="font-size:10px;color:#94A3B8;">대기</span>`}
                </div>
            </div>
        `;

        // 4. 📸 4대 옴니 카드뉴스 섹션
        const cardnews = bData.cardnews || {};
        const cardPlatforms = cardnews.platforms || {};
        const cardIg = cardPlatforms.instagram || {};
        const cardFb = cardPlatforms.facebook || {};
        const cardLocal = cardPlatforms.local_slides || {};

        let cardnewsListHtml = `
            <div style="display:flex;flex-direction:column;gap:6px;">
                <!-- 📸 Instagram Carousel (5장 캐러셀) -->
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:6px;padding:6px 8px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:4px;">
                    <div style="display:flex;align-items:center;gap:6px;overflow:hidden;text-overflow:ellipsis;">
                        <span style="font-size:13px;">📸</span>
                        <span style="font-size:11px;font-weight:800;color:#0F172A;">인스타 캐러셀 (5장)</span>
                        <span style="font-size:10px;color:#64748B;">🕒 ${cardIg.published_at || '-'}</span>
                    </div>
                    ${(cardIg.is_success && cardIg.url) ? `<a href="${cardIg.url}" target="_blank" style="font-size:10.5px;font-weight:700;color:#E1306C;text-decoration:underline;">📸 캐러셀 열기 ↗</a>` : `<span style="font-size:10px;color:#94A3B8;">대기</span>`}
                </div>
                <!-- 📘 Facebook Album (5장 앨범) -->
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:6px;padding:6px 8px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:4px;">
                    <div style="display:flex;align-items:center;gap:6px;overflow:hidden;text-overflow:ellipsis;">
                        <span style="font-size:13px;">📘</span>
                        <span style="font-size:11px;font-weight:800;color:#0F172A;">페이스북 앨범 (5장)</span>
                        <span style="font-size:10px;color:#64748B;">🕒 ${cardFb.published_at || '-'}</span>
                    </div>
                    ${(cardFb.is_success && cardFb.url) ? `<a href="${cardFb.url}" target="_blank" style="font-size:10.5px;font-weight:700;color:#1877F2;text-decoration:underline;">📘 앨범 열기 ↗</a>` : `<span style="font-size:10px;color:#94A3B8;">대기</span>`}
                </div>
                <!-- 📁 1080x1350 카드뉴스 5장 완제품 -->
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:6px;padding:6px 8px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:4px;">
                    <div style="display:flex;align-items:center;gap:6px;overflow:hidden;text-overflow:ellipsis;">
                        <span style="font-size:13px;">📁</span>
                        <span style="font-size:11px;font-weight:800;color:#0F172A;">1080x1350 완제품</span>
                        <span style="font-size:10px;color:#64748B;">🕒 ${cardLocal.time || '-'}</span>
                    </div>
                    ${cardLocal.is_success ? `<span style="font-size:10px;font-weight:700;color:#059669;background:#ECFDF5;padding:2px 6px;border-radius:4px;" title="${cardLocal.folder}">✅ ${cardLocal.slide_count}장 완성</span>` : `<span style="font-size:10px;color:#94A3B8;">제작 대기</span>`}
                </div>
            </div>
        `;

        // 5. 지식iN 목록
        const kinAnswers = kin.recent_answers || [];
        let kinListHtml = "";
        if (kinAnswers.length > 0) {
            kinListHtml = `
                <div style="display:flex;flex-direction:column;gap:5px;margin-top:6px;">
                    ${kinAnswers.map((ka, kIdx) => `
                        <div style="display:flex;justify-content:space-between;align-items:center;font-size:11.5px;gap:6px;background:#FFFFFF;padding:5px 8px;border-radius:5px;border:1px solid #E2E8F0;">
                            <div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:210px;">
                                <strong style="color:#0284C7;">#${kIdx+1}</strong> <span title="${ka.title}">${ka.title}</span>
                            </div>
                            <div style="display:flex;align-items:center;gap:6px;white-space:nowrap;">
                                <span style="font-size:10px;color:#64748B;">🕒 ${ka.created_at || '-'}</span>
                                ${ka.url ? `<a href="${ka.url}" target="_blank" style="color:#0284C7;font-weight:800;text-decoration:underline;font-size:10.5px;">열기↗</a>` : ''}
                            </div>
                        </div>
                    `).join("")}
                </div>
            `;
        } else {
            kinListHtml = `<div style="font-size:11px;color:#94A3B8;margin-top:4px;">오늘 등록된 답변 대기 중</div>`;
        }

        // 6. ☕ 네이버 카페 침투 (5일 로테이션 스텔스)
        const cafe = bData.cafe || {};
        const cafePosts = cafe.recent_posts || [];
        let cafeListHtml = "";
        if (cafePosts.length > 0) {
            cafeListHtml = `
                <div style="display:flex;flex-direction:column;gap:5px;margin-top:6px;">
                    ${cafePosts.map((cp, cIdx) => `
                        <div style="background:#FFFFFF;padding:6px 8px;border-radius:6px;border:1px solid #E2E8F0;display:flex;flex-direction:column;gap:4px;">
                            <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;gap:6px;">
                                <div style="display:flex;align-items:center;gap:5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:210px;">
                                    <span style="background:#FEF3C7;color:#D97706;font-size:9.5px;font-weight:800;padding:1px 5px;border-radius:3px;white-space:nowrap;">${cp.cafe_name || '정예카페'}</span>
                                    <strong style="color:#0F172A;" title="${cp.title}">${cp.title}</strong>
                                </div>
                                <div style="display:flex;align-items:center;gap:5px;white-space:nowrap;">
                                    <span style="font-size:10px;color:#64748B;">🕒 ${cp.datetime || cp.date || '-'}</span>
                                    ${cp.url ? `<a href="${cp.url}" target="_blank" style="color:#D97706;font-weight:800;text-decoration:underline;font-size:10.5px;">열기↗</a>` : ''}
                                </div>
                            </div>
                            ${cp.reply_text ? `
                                <div style="font-size:10.5px;color:#475569;background:#FDF8F3;border-left:2px solid #F59E0B;padding:4px 6px;border-radius:3px;line-height:1.35;word-break:break-all;" title="${cp.reply_text}">
                                    💬 <em>"${cp.reply_text.length > 70 ? cp.reply_text.substring(0, 70) + '...' : cp.reply_text}"</em>
                                </div>
                            ` : ''}
                        </div>
                    `).join("")}
                </div>
            `;
        } else {
            cafeListHtml = `
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:6px;padding:6px 8px;font-size:11px;color:#64748B;display:flex;justify-content:space-between;align-items:center;margin-top:4px;">
                    <span>⚪ 오늘 정시 침투 대기 중 (순번: <strong>${cafe.current_slot || '1번 슬롯'}</strong>)</span>
                    <span style="font-size:10px;color:#D97706;font-weight:700;">1일 1건 엄수</span>
                </div>
            `;
        }

        return `
            <div style="background:${cfg.bgGradient};border:1.5px solid ${cfg.border};border-radius:14px;padding:16px;display:flex;flex-direction:column;gap:12px;box-shadow:0 4px 12px rgba(0,0,0,0.03);">
                <!-- 브랜드 헤더 -->
                <div style="display:flex;justify-content:space-between;align-items:flex-start;border-bottom:1px dashed ${cfg.border};padding-bottom:10px;">
                    <div>
                        <div style="display:flex;align-items:center;gap:6px;">
                            <h4 style="margin:0;font-size:15px;font-weight:800;color:#0F172A;">${cfg.title}</h4>
                            <span style="font-size:10.5px;font-weight:700;color:${cfg.badgeColor};background:${cfg.badgeBg};padding:2px 6px;border-radius:4px;">${cfg.sub}</span>
                        </div>
                        <div style="font-size:11px;color:#64748B;margin-top:3px;">
                            랜딩: <a href="${cfg.landing}" target="_blank" style="color:#64748B;text-decoration:underline;">${cfg.landing}</a>
                        </div>
                    </div>
                    <button class="btn" onclick="publishOmniBlog('${bKey}', this)" style="font-size:11px;font-weight:700;padding:5px 10px;background:#FFFFFF;border:1px solid ${cfg.border};color:${cfg.color};border-radius:6px;cursor:pointer;" title="오늘의 블로그 즉시 1회 발행">
                        ✍️ 즉시발행
                    </button>
                </div>

                <!-- 1. 📰 4대 블로그 섹션 -->
                <div style="display:flex;flex-direction:column;gap:6px;">
                    <div style="font-size:12px;font-weight:800;color:#334155;">📰 블로그 채널 발행 상태 (초 단위 시간 검증)</div>
                    ${supaHtml}
                    ${naverHtml}
                    ${tistoryHtml}
                </div>

                <!-- 2. 🎬 4대 숏폼 & 릴스 섹션 -->
                <div style="display:flex;flex-direction:column;gap:6px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:12px;font-weight:800;color:#DC2626;">🎬 4대 숏폼 & 릴스 (플랫폼별 발행 URL & 시간)</span>
                        <span style="font-size:10.5px;font-weight:700;color:#DC2626;background:#FEE2E2;padding:2px 6px;border-radius:4px;">오늘 ${shorts.today_count || 0}건</span>
                    </div>
                    ${shortsListHtml}
                </div>

                <!-- 3. 📸 4대 옴니 카드뉴스 섹션 -->
                <div style="display:flex;flex-direction:column;gap:6px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:12px;font-weight:800;color:#7C3AED;">📸 4대 옴니 카드뉴스 (1080x1350 & 배포 URL)</span>
                        <span style="font-size:10.5px;font-weight:700;color:#7C3AED;background:#F3E8FF;padding:2px 6px;border-radius:4px;">오늘 ${cardnews.today_count || 0}건</span>
                    </div>
                    ${cardnewsListHtml}
                </div>

                <!-- 4. 💬 네이버 지식iN 1:1 낚아채기 섹션 -->
                <div style="display:flex;flex-direction:column;gap:4px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:12px;font-weight:800;color:#0284C7;">💬 네이버 지식iN (오늘 ${kin.today_count || 0} / ${kin.target_count || 10}건)</span>
                        <button onclick="triggerKinCatch('${bKey}', this)" style="font-size:10px;font-weight:700;padding:2px 6px;background:#E0F2FE;color:#0284C7;border:1px solid #BAE6FD;border-radius:4px;cursor:pointer;">⚡ 1회 낚아채기</button>
                    </div>
                    ${kinListHtml}
                </div>

                <!-- 5. ☕ 네이버 카페 8대 정예 침투 섹션 -->
                <div style="display:flex;flex-direction:column;gap:4px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:12px;font-weight:800;color:#D97706;">☕ 네이버 카페 침투 (오늘 ${cafe.today_count || 0} / 1건 | 슬롯: ${cafe.current_slot || '-'})</span>
                        <button onclick="triggerCafeInfiltration('${bKey}', this)" style="font-size:10px;font-weight:700;padding:2px 6px;background:#FEF3C7;color:#D97706;border:1px solid #FDE68A;border-radius:4px;cursor:pointer;">⚡ 1회 즉시 침투</button>
                    </div>
                    ${cafeListHtml}
                </div>
            </div>
        `;
    }).join("");

    container.innerHTML = `
        ${gpuBannerHtml}
        <div class="section-card" style="border-top: 4px solid #3B82F6; background:#FFFFFF; box-shadow:0 6px 20px rgba(0,0,0,0.06); margin-bottom: 24px;">
            <!-- 전광판 상단 바 -->
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:10px;">
                <div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <h3 class="section-title" style="margin:0;font-size:17px;font-weight:800;color:#1E293B;">
                            🚀 3대 브랜드 실시간 마케팅 무인 발행 라이브 전광판 (100% 투명 시간/URL 표출)
                        </h3>
                        <span class="badge-live-pulse" style="font-size:11px;"><span class="pulse-dot"></span> 실시간 동기화</span>
                    </div>
                    <p class="section-subtitle" style="margin-top:4px;font-size:12px;color:#64748B;">
                        모든 블로그, 숏폼(유튜브/인스타/페북/클립), 카드뉴스, 지식iN, 네이버 카페의 <strong>실제 발행 URL과 초 단위 시각(YYYY-MM-DD HH:MM:SS)</strong>을 투명하게 직격 표출합니다.
                    </p>
                </div>
                <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                    <div style="font-size:11.5px;color:#475569;background:#F1F5F9;padding:6px 12px;border-radius:8px;font-weight:700;">
                        📅 오늘(${today}) 실적: 블로그 <strong style="color:#2563EB;">${summary.total_blog_today || 0}</strong>건 | 숏폼 <strong style="color:#DC2626;">${summary.total_shorts_today || 0}</strong>건 | 카드뉴스 <strong style="color:#7C3AED;">${summary.total_cardnews_today || 0}</strong>세트 | 지식iN <strong style="color:#0284C7;">${summary.total_kin_today || 0}</strong>건 | 카페 <strong style="color:#D97706;">${summary.total_cafe_today || 0}</strong>건
                    </div>
                    <button class="btn btn-secondary" onclick="fetchStatus()" style="font-size:12px;padding:6px 12px;">
                        🔄 실시간 갱신
                    </button>
                    <button class="btn" onclick="publishOmniBlog('all', this)" style="background:linear-gradient(135deg, #3B82F6, #1D4ED8);color:#FFFFFF;font-weight:800;font-size:12px;padding:6px 14px;border-radius:8px;border:none;cursor:pointer;">
                        ⚡ 3대 앱 1회 일괄 발행
                    </button>
                </div>
            </div>

            <!-- 3대 브랜드 카드 그리드 (3열) -->
            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(320px, 1fr));gap:16px;">
                ${brandCardsHtml}
            </div>
        </div>
    `;
}

function updateChannelBadges(runningChannels = {}, liveFeed = {}, channelErrors = {}) {
    const brand = currentBrand || "aura";
    const bFeed = (liveFeed && liveFeed.brands && liveFeed.brands[brand]) || {};
    const blog = bFeed.blog || {};
    const kin = bFeed.kin || {};
    const shorts = bFeed.shorts || {};
    const channels = blog.channels || {};
    const shortsPlatforms = shorts.platforms || {};

    // 1. 옴니 블로그 카드 (#card-${brand}-omni_blog)
    const blogBadge = document.getElementById(`badge-status-${brand}-omni_blog`);
    const blogCard = document.getElementById(`card-${brand}-omni_blog`);
    const tb = channels.tistory || {};
    const nb = channels.naver_blog || {};
    const supa = channels.supabase_research || {};
    const blogErr = channelErrors && (channelErrors[`${brand}_omni_blog`] || channelErrors[`${brand}_blog`]);

    if (blogBadge && blogCard) {
        if (blogErr) {
            blogBadge.innerHTML = "🚨 오류 발생";
            blogBadge.style.background = "#FEF2F2";
            blogBadge.style.color = "#DC2626";
            blogBadge.style.border = "1.5px solid #F87171";
            blogCard.style.border = "2px solid #EF4444";
            blogCard.style.boxShadow = "0 4px 14px rgba(239, 68, 68, 0.25)";

            let errBox = document.getElementById(`err-box-${brand}-omni_blog`);
            if (!errBox) {
                errBox = document.createElement("div");
                errBox.id = `err-box-${brand}-omni_blog`;
                errBox.style.cssText = "background:#FEF2F2;border:1px solid #FECACA;color:#991B1B;padding:8px 10px;border-radius:8px;font-size:11.5px;margin-top:8px;line-height:1.4;";
                blogBadge.parentElement.after(errBox);
            }
            errBox.innerHTML = `🚨 <strong>오류 원인:</strong> ${blogErr.error || '블로그 발행 오류'}<br><span style="color:#6B7280;font-size:10.5px;">발생시각: ${blogErr.occurred_at || ''}</span>`;
        } else if (tb.is_session_expired) {
            blogBadge.innerHTML = "🔴 티스토리 세션 만료";
            blogBadge.style.background = "#FEF2F2";
            blogBadge.style.color = "#DC2626";
            blogBadge.style.border = "1.5px solid #F87171";
            blogCard.style.border = "2px solid #EF4444";
            blogCard.style.boxShadow = "0 4px 14px rgba(239, 68, 68, 0.2)";

            let errBox = document.getElementById(`err-box-${brand}-omni_blog`);
            if (!errBox) {
                errBox = document.createElement("div");
                errBox.id = `err-box-${brand}-omni_blog`;
                errBox.style.cssText = "background:#FEF2F2;border:1px solid #FECACA;color:#991B1B;padding:8px 10px;border-radius:8px;font-size:11.5px;margin-top:8px;line-height:1.4;";
                blogBadge.parentElement.after(errBox);
            }
            const batFile = brand === "aura" ? "[1회연동]_아우라_티스토리_영구로그인.bat" 
                          : brand === "insurance" ? "[1회연동]_보험비교_티스토리_영구로그인.bat" 
                          : "[1회연동]_주식AI_티스토리_영구로그인.bat";
            errBox.innerHTML = `⚠️ <strong>장애 원인:</strong> 카카오 로그인 세션 만료<br>👉 <strong>해결 조치:</strong> 바탕화면의 <code>${batFile}</code> 을 실행해 주세요.`;
        } else if (nb.is_success && nb.is_today) {
            blogBadge.innerHTML = "🟢 네이버 오늘 발행 완료";
            blogBadge.style.background = "#ECFDF5";
            blogBadge.style.color = "#059669";
            blogBadge.style.border = "1px solid #A7F3D0";
            blogCard.style.border = "1px solid #E5DDD1";
            const errBox = document.getElementById(`err-box-${brand}-omni_blog`);
            if (errBox) errBox.remove();
        } else if (tb.is_success && tb.url) {
            blogBadge.innerHTML = "🟢 티스토리 정상 연동 (발행 완료)";
            blogBadge.style.background = "#ECFDF5";
            blogBadge.style.color = "#059669";
            blogBadge.style.border = "1px solid #A7F3D0";
            blogCard.style.border = "1px solid #E5DDD1";
            blogCard.style.boxShadow = "var(--shadow-md)";

            const errBox = document.getElementById(`err-box-${brand}-omni_blog`);
            if (errBox) errBox.remove();
        } else if (supa.is_success) {
            blogBadge.innerHTML = "🟢 본진 블로그 발행 완료";
            blogBadge.style.background = "#ECFDF5";
            blogBadge.style.color = "#059669";
            blogBadge.style.border = "1px solid #A7F3D0";
            blogCard.style.border = "1px solid #E5DDD1";
            blogCard.style.boxShadow = "var(--shadow-md)";

            const errBox = document.getElementById(`err-box-${brand}-omni_blog`);
            if (errBox) errBox.remove();
        } else {
            blogBadge.innerHTML = "⚪ 정시 스케줄 대기";
            blogBadge.style.background = "#F6F1EA";
            blogBadge.style.color = "#6E665E";
            blogBadge.style.border = "1px solid #E5DDD1";
            blogCard.style.border = "1px solid #E5DDD1";
            blogCard.style.boxShadow = "var(--shadow-md)";

            const errBox = document.getElementById(`err-box-${brand}-omni_blog`);
            if (errBox) errBox.remove();
        }
    }

    // 2. 지식iN 허브 카드
    const kinBadge = document.getElementById(`badge-status-${brand}-naver_kin`);
    const kinCard = document.getElementById(`card-${brand}-naver_kin`);
    const kinCountEl = document.getElementById(`kin-count-${brand}`);
    const kinRecentEl = document.getElementById(`kin-recent-${brand}`);
    const kinErr = channelErrors && (channelErrors[`${brand}_naver_kin`] || channelErrors[`${brand}_kin`]);

    if (kinCountEl) kinCountEl.innerText = `${kin.today_count || 0}`;
    if (kinRecentEl && kin.recent_answers && kin.recent_answers.length > 0) {
        const ka = kin.recent_answers[0];
        const liveUrl = ka.published_url || ka.url || "#";
        kinRecentEl.innerHTML = `<span style="color:#64748B;font-size:10.5px;">[${ka.created_at || '-'}]</span> <a href="${liveUrl}" target="_blank" style="color:#0284C7;text-decoration:underline;font-weight:700;" title="${ka.title}">${ka.title}</a>`;
    }
    if (kinBadge) {
        if (kinErr) {
            kinBadge.innerHTML = "🚨 오류 발생";
            kinBadge.style.background = "#FEF2F2";
            kinBadge.style.color = "#DC2626";
            kinBadge.style.border = "1.5px solid #F87171";
            if (kinCard) kinCard.style.border = "2px solid #EF4444";
        } else {
            kinBadge.innerHTML = `🟢 감시 중 (오늘 ${kin.today_count || 0}/10건)`;
            kinBadge.style.background = "#ECFDF5";
            kinBadge.style.color = "#059669";
            kinBadge.style.border = "1px solid #A7F3D0";
            if (kinCard) kinCard.style.border = "1px solid #E5DDD1";
        }
    }

    // 3. 숏폼 허브 카드
    const shortsBadge = document.getElementById(`badge-status-${brand}-shorts`);
    const shortsCard = document.getElementById(`card-${brand}-shorts`);
    const shortsErr = channelErrors && (channelErrors[`${brand}_shorts`] || channelErrors[`${brand}_omni_shorts`]);

    if (shortsBadge) {
        if (shortsErr) {
            shortsBadge.innerHTML = "🚨 오류 발생";
            shortsBadge.style.background = "#FEF2F2";
            shortsBadge.style.color = "#DC2626";
            shortsBadge.style.border = "1.5px solid #F87171";
            if (shortsCard) shortsCard.style.border = "2px solid #EF4444";
        } else {
            const isDaemonOn = runningChannels[`${brand}_shorts`];
            const yt = shortsPlatforms.youtube || {};
            shortsBadge.innerHTML = yt.published_at ? `🟢 최신: ${yt.published_at}` : isDaemonOn ? "🟢 24시간 무인 가동 중" : "⚪ 정시 스케줄 대기";
            shortsBadge.style.background = isDaemonOn ? "#ECFDF5" : "#F6F1EA";
            shortsBadge.style.color = isDaemonOn ? "#059669" : "#6E665E";
            shortsBadge.style.border = isDaemonOn ? "1px solid #A7F3D0" : "1px solid #E5DDD1";
            if (shortsCard) shortsCard.style.border = "1px solid #E5DDD1";
        }
    }

    // 4. 나머지 20대 허브 채널 뱃지 & 실시간 에러 동기화
    const allHubKeys = ["omni_cardnews", "threads", "omni_threads", "reddit", "naver_cafe", "cafe", "seo", "google_ping", "search_advisor", "dcinside", "ppomppu", "nate_pann", "kakao_channel", "briefing", "tiktok", "youtube"];
    
    // running_channels 및 등록된 모든 허브 카드 순회
    allHubKeys.forEach(pureKey => {
        const fullKey = `${brand}_${pureKey}`;
        const badge = document.getElementById(`badge-status-${brand}-${pureKey}`) || document.getElementById(`badge-status-${brand}-${pureKey.replace('omni_', '')}`);
        const card = document.getElementById(`card-${brand}-${pureKey}`) || document.getElementById(`card-${brand}-${pureKey.replace('omni_', '')}`);
        const chErr = channelErrors && (channelErrors[fullKey] || channelErrors[pureKey] || channelErrors[`${brand}_${pureKey.replace('omni_', '')}`]);

        if (badge) {
            let errBox = document.getElementById(`err-box-${brand}-${pureKey}`);
            if (chErr) {
                badge.innerHTML = "🚨 오류 발생";
                badge.style.background = "#FEF2F2";
                badge.style.color = "#DC2626";
                badge.style.border = "1.5px solid #F87171";
                if (card) {
                    card.style.border = "2px solid #EF4444";
                    card.style.boxShadow = "0 4px 14px rgba(239, 68, 68, 0.25)";
                }
                if (!errBox && card) {
                    errBox = document.createElement("div");
                    errBox.id = `err-box-${brand}-${pureKey}`;
                    errBox.style.cssText = "background:#FEF2F2;border:1px solid #FECACA;color:#991B1B;padding:8px 10px;border-radius:8px;font-size:11.5px;margin-top:8px;line-height:1.4;";
                    badge.parentElement.after(errBox);
                }
                if (errBox) {
                    errBox.innerHTML = `🚨 <strong>오류 원인:</strong> ${chErr.error || '실행 실패'}<br><span style="color:#6B7280;font-size:10.5px;">발생시각: ${chErr.occurred_at || ''}</span>`;
                }
            } else {
                if (errBox) errBox.remove();
                if (card) {
                    card.style.border = "1px solid #E5DDD1";
                    card.style.boxShadow = "var(--shadow-md)";
                }
                const isRunning = runningChannels[fullKey] || runningChannels[pureKey] || runningChannels[`${brand}_${pureKey.replace('omni_', '')}`];
                badge.innerHTML = isRunning ? "🟢 24시간 무인 가동 중" : "⚪ 대기 중";
                badge.style.background = isRunning ? "#ECFDF5" : "#F6F1EA";
                badge.style.color = isRunning ? "#059669" : "#6E665E";
                badge.style.border = isRunning ? "1px solid #A7F3D0" : "1px solid #E5DDD1";
            }
        }
    });
}


// 6. 실시간 서버 상태 폴링 (3초 주기)
let lastSeenLogKeys = new Set();

async function fetchStatus() {
    try {
        const res = await fetch("/api/status");
        if (!res.ok) return;
        const data = await res.json();

        // 🚀 실시간 무인 발행 라이브 전광판 렌더링 (GPU 상태 포함)
        if (data.today_live_feed) {
            renderTodayLiveFeedBoard(data.today_live_feed, data.gpu_status);
        }

        // 갤러리 탭 실시간 GPU 상태 동기화
        if (typeof cachedGPUStatus !== "undefined") {
            cachedGPUStatus = data.gpu_status || null;
            const galleryTab = document.getElementById("tab-gallery");
            if (galleryTab && galleryTab.classList.contains("active") && typeof renderGalleryItems === "function") {
                renderGalleryItems();
            }
        }

        // 🚨 실시간 비상관제 배너 렌더링
        if (data.emergency_status) {
            renderEmergencyGuardBanner(data.emergency_status, data.emergency_status.summary);
        }

        isStockRunning = data.stock_running || false;
        isAuraRunning = data.aura_running || false;
        isInsuranceRunning = data.insurance_running || false;
        isKMarketRunning = data.kmarket_running || false;
        isEasyTaxRunning = data.easytax_running || false;

        // 📈 Stock Master 사이드바 상태
        const stockStatusText = document.getElementById("stock-daemon-status-text");
        const stockSub = document.getElementById("stock-daemon-sub");
        if (stockStatusText) {
            stockStatusText.innerText = isStockRunning ? "📈 주식 AI 가동 중 🟢" : "📈 주식 AI 대기 중 ⚪";
            stockStatusText.style.color = isStockRunning ? "#34D399" : "#FACC15";
        }
        if (stockSub) {
            stockSub.innerText = isStockRunning ? "24시간 자동 분석/발행 중" : "실시간수급/장전브리핑/조건검색";
        }

        // 💖 Aura 사이드바 상태
        const auraStatusText = document.getElementById("aura-daemon-status-text");
        const auraSub = document.getElementById("aura-daemon-sub");
        if (auraStatusText) {
            auraStatusText.innerText = isAuraRunning ? "💖 Aura 데이팅 가동 중 🟢" : "💖 Aura 데이팅 대기 중 ⚪";
            auraStatusText.style.color = isAuraRunning ? "#34D399" : "#EC4899";
        }
        if (auraSub) {
            auraSub.innerText = isAuraRunning ? "24시간 자동 매칭/바이럴 중" : "소개팅첫만남/2030연애/클립";
        }

        // 🛡️ InsureBalance 사이드바 상태
        const insStatusText = document.getElementById("insurance-daemon-status-text");
        const insSub = document.getElementById("insurance-daemon-sub");
        if (insStatusText) {
            insStatusText.innerText = isInsuranceRunning ? "🛡️ 보험비교 가동 중 🟢" : "🛡️ 보험비교 대기 중 ⚪";
            insStatusText.style.color = isInsuranceRunning ? "#34D399" : "#10B981";
        }
        if (insSub) {
            insSub.innerText = isInsuranceRunning ? "24시간 보장 분석/리모델링 중" : "실손/3대질병/호갱탈출";
        }

        // 🛸 3대 슈퍼앱 24시간 무인 오토파일럿 마스터 관제 바 업데이트
        const auraKinCount = data.kin_quotas?.aura?.today_total || 0;
        const insKinCount = data.kin_quotas?.insurance?.today_total || 0;
        const stockKinCount = data.kin_quotas?.stock?.today_total || 0;

        const barAura = document.getElementById("bar-aura-status");
        if (barAura) {
            barAura.innerHTML = isAuraRunning 
                ? `<span style="color:#34D399;font-weight:700;">🟢 가동 중 (지식iN ${auraKinCount}/10건)</span>`
                : `<span style="color:#CBD5E1;">⚪ 대기 중 (지식iN ${auraKinCount}/10건)</span>`;
        }

        const barIns = document.getElementById("bar-insurance-status");
        if (barIns) {
            barIns.innerHTML = isInsuranceRunning 
                ? `<span style="color:#34D399;font-weight:700;">🟢 가동 중 (지식iN ${insKinCount}/10건)</span>`
                : `<span style="color:#CBD5E1;">⚪ 대기 중 (지식iN ${insKinCount}/10건)</span>`;
        }

        const barStock = document.getElementById("bar-stock-status");
        if (barStock) {
            barStock.innerHTML = isStockRunning 
                ? `<span style="color:#34D399;font-weight:700;">🟢 가동 중 (지식iN ${stockKinCount}/10건)</span>`
                : `<span style="color:#CBD5E1;">⚪ 대기 중 (지식iN ${stockKinCount}/10건)</span>`;
        }

        const masterBadge = document.getElementById("master-autopilot-badge");
        if (masterBadge) {
            const anyRunning = isAuraRunning || isInsuranceRunning || isStockRunning;
            masterBadge.innerHTML = anyRunning ? "🟢 24시간 자율 가동 중" : "⚪ 대기 중";
            masterBadge.style.background = anyRunning ? "#10B981" : "#64748B";
        }

        // 22대 허브 실시간 뱃지 & 실시간 장애(빨간불) 동기화
        updateChannelBadges(data.running_channels, data.today_live_feed, data.channel_errors);
        if (data.golden_targets) {
            updateGoldenTargetIndicators(data.golden_targets);
        }
        if (data.golden_batch_summary) {
            updateGoldenBatchPanel(data.golden_batch_summary);
        }

        // 상단 지표 (현재 브랜드 전용 1:1 완벽 분리)
        const brand = currentBrand || "stock";
        const totalEl = document.getElementById("stat-total-count");
        const topScoreEl = document.getElementById("stat-top-score");
        const seoCountEl = document.getElementById("stat-seo-count");
        const googleCountEl = document.getElementById("google-index-count");

        if (totalEl) {
            if (brand === "stock") totalEl.innerText = `${data.stock_history_count || 0} 건`;
            else if (brand === "aura") totalEl.innerText = `${data.aura_history_count || 0} 건`;
            else if (brand === "insurance") totalEl.innerText = `${data.insurance_history_count || 0} 건`;
            else if (brand === "kmarket") totalEl.innerText = `${data.kmarket_history_count || 0} 건`;
            else if (brand === "easytax") totalEl.innerText = `${data.easytax_history_count || 0} 건`;
            else totalEl.innerText = `${data.total_history_count || 0} 건`;
        }
        if (topScoreEl) {
            if (brand === "stock") topScoreEl.innerText = `${data.stock_top_score || 0.0} 점`;
            else if (brand === "aura") topScoreEl.innerText = `${data.aura_top_score || 0.0} 점`;
            else if (brand === "insurance") topScoreEl.innerText = `${data.insurance_top_score || 0.0} 점`;
            else if (brand === "kmarket") topScoreEl.innerText = `${data.kmarket_top_score || 0.0} 점`;
            else if (brand === "easytax") topScoreEl.innerText = `${data.easytax_top_score || 0.0} 점`;
            else topScoreEl.innerText = `${data.top_score || 0.0} 점`;
        }
        if (seoCountEl) {
            const bLabel = brand === "stock" ? "Stock AI" : brand === "aura" ? "Aura" : "InsureBalance";
            seoCountEl.innerText = `22개 채널 (${bLabel})`;
        }
        if (googleCountEl) {
            googleCountEl.innerText = `22개 채널 연결됨`;
        }
        const antibanEl = document.getElementById("stat-antiban-status");
        if (antibanEl && data.human_routines && data.human_routines[brand]) {
            const hr = data.human_routines[brand];
            antibanEl.innerText = `${hr.total_minutes || 0}분 스텔스 (${hr.total_likes || 0}❤️)`;
        }

        // 최신 로그 콘솔 (중복 방지: 새 로그만 딱 1번 출력)
        if (data.recent_logs && data.recent_logs.length > 0) {
            data.recent_logs.forEach(msg => {
                const logKey = `${msg.id || msg.timestamp || msg.time || ''}_${msg.text}`;
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
    const brandName = currentBrand === "easytax" ? "EasyTax" : "KTRS 마켓";
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

// 9. 비주얼 미디어 엔진 관리
async function setMediaEngine(channelKey, engineMode = "wan") {
    appendLog(`[Engine] ${channelKey} 비주얼 엔진 준비 완료`, "info");
}

async function loadMediaEngineSettings() {
}

function updateMediaEngineUI(settings = {}, stats = {}) {
}

function refreshOverview(btn) {
    animateRefreshBtn(btn, "대시보드 활동 로그와 상태가 새로고침되었습니다! 📊");
    fetchStatus();
    renderHubGrid();
    loadMediaEngineSettings();
}

// 🌟 10. 8대 황금 타깃 국가 1일 2슬롯 풀가동 제어 모듈
let lastGoldenBatchSummary = null;

// 🚀 [원클릭 즉시 제작] 대시보드 버튼 하나로 즉시 카드뉴스/숏폼 생산 및 바탕화면 출력
async function triggerOneClickProduce(brand, mode, btnElement = null) {
    const brandNames = {
        stock: "Stock Master (주식 AI)",
        aura: "Aura (AI 데이팅)",
        insurance: "InsureBalance (보험비교)",
        easytax: "EasyTax (세금 환급)",
        kmarket: "K-Market (생활 커뮤니티)"
    };
    const brandName = brandNames[brand] || brand;
    const modeName = mode === "shorts" ? "완성 숏폼" : "4장 카드뉴스";
    const langSelect = document.getElementById(`select-lang-${brand}-${mode}`);
    const lang = langSelect ? langSelect.value : "ko";
    const amountSelect = document.getElementById(`select-amount-${brand}-${mode}`);
    const amount = amountSelect ? amountSelect.value : "random";
    
    appendLog(`[Action] 🚀 [${brandName}] ${modeName} 원클릭 즉시 제작 요청...`, "info");
    showToast(`🚀 [${brandName}] ${modeName} 제작을 시작합니다!`, "info");

    const originalText = btnElement ? btnElement.innerHTML : "";
    if (btnElement) {
        btnElement.disabled = true;
        btnElement.style.opacity = "0.7";
        btnElement.innerHTML = `<span>⏳</span> 제작 진행 중...`;
    }

    try {
        const res = await fetch("/api/factory/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                brand: brand,
                mode: mode,
                lang: lang,
                amount: amount
            })
        });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Success] 🎉 ${data.message}`, "success");
            showToast(`🎉 제작이 시작되었습니다. 완성 후 바탕화면에 저장됩니다.`, "success");
        } else {
            appendLog(`[Error] ⚠️ ${data.message}`, "error");
            showToast(data.message, "error");
        }
    } catch (e) {
        appendLog(`[Error] ❌ 팩토리 통신 오류: ${e}`, "error");
        showToast("팩토리 통신 오류", "error");
    } finally {
        setTimeout(() => {
            if (btnElement) {
                btnElement.disabled = false;
                btnElement.style.opacity = "1";
                btnElement.innerHTML = originalText;
            }
            fetchStatus();
        }, 3000);
    }
}

async function triggerGoldenBatchRun(contentType = 'all', btnElement = null) {
    const brand = currentBrand || 'kmarket';
    const brandName = brand === 'easytax' ? 'EasyTax (세무)' : 'KTRS 마켓 (쇼핑)';
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
    const brandName = brand === 'easytax' ? 'EasyTax (세무)' : 'KTRS 마켓 (쇼핑)';
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
    const brandName = brand === 'easytax' ? 'EasyTax (세무)' : 'KTRS 마켓 (쇼핑)';
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
                btnDaemonShorts.innerHTML = "🚀 무인 가동";
                btnDaemonShorts.style.background = "linear-gradient(135deg, #10B981, #059669)";
            }
            if (btnDaemonCardnews) {
                btnDaemonCardnews.innerHTML = "🚀 무인 가동";
                btnDaemonCardnews.style.background = "linear-gradient(135deg, #10B981, #059669)";
            }
        }
    }
}

window.renderHubGrid = renderHubGrid;
// 🚀 4대 옴니블로그 원클릭 즉시 발행 함수 (BAT 파일 대체)
async function publishOmniBlog(brand) {
    const btnId = `btn-omni-${brand}`;
    const btn = document.getElementById(btnId);
    const originalHtml = btn ? btn.innerHTML : "";

    const nameMap = {
        aura: "💖 Aura 데이팅",
        insurance: "🛡️ InsureBalance 보험비교",
        stock: "📈 Stock Master 주식AI",
        all: "⚡ 3대 슈퍼앱 전체"
    };
    const brandName = nameMap[brand] || brand;

    if (btn) {
        btn.disabled = true;
        btn.style.opacity = "0.7";
        btn.innerHTML = `<span>⏳ ${brandName} 발행 중...</span>`;
    }

    appendLog(`[Action] ${brandName} 4대 옴니블로그 1회 즉시 발행 시작... (Gemini 2,000자 + 16:9 사진 생성)`, "info");
    showToast(`🚀 ${brandName} 옴니블로그 1회 즉시 발행이 시작되었습니다!`, "info");

    try {
        if (brand === "all") {
            // 3대 브랜드 순차 백그라운드 트리거
            const resA = await fetch("/api/omni-blog/publish/aura", { method: "POST" });
            const resI = await fetch("/api/omni-blog/publish/insurance", { method: "POST" });
            const resS = await fetch("/api/omni-blog/publish/stock", { method: "POST" });
            const data = await resA.json();
            appendLog(`[Success] 3대 슈퍼앱 전체 옴니블로그 1회 발행 작업이 가동되었습니다.`, "success");
            showToast("🎉 3대 앱 옴니블로그 발행이 백그라운드에서 진행 중입니다!", "success");
        } else {
            const res = await fetch(`/api/omni-blog/publish/${brand}`, { method: "POST" });
            const data = await res.json();
            if (data.success) {
                appendLog(`[Success] ${data.message}`, "success");
                showToast(data.message, "success");
            } else {
                appendLog(`[Error] 발행 실패: ${data.message}`, "error");
                showToast(`발행 실패: ${data.message}`, "error");
            }
        }
        if (typeof fetchStatus === "function") fetchStatus();
    } catch (e) {
        appendLog(`[Error] 옴니블로그 통신 실패: ${e}`, "error");
        showToast("서버 통신 실패", "error");
    } finally {
        setTimeout(() => {
            if (btn) {
                btn.disabled = false;
                btn.style.opacity = "1";
                btn.innerHTML = originalHtml;
            }
        }, 3000);
    }
}

// 💬 네이버 지식iN 실시간 1회 낚아채기 트리거
async function triggerKinCatch(brand, btn) {
    const nameMap = { aura: "💖 Aura 데이팅", insurance: "🛡️ 보험 리밸런스", stock: "📈 StockMaster AI" };
    const bName = nameMap[brand] || brand;
    const originalText = btn ? btn.innerText : "";
    if (btn) {
        btn.disabled = true;
        btn.innerText = "⏳ 낚아채는 중...";
        btn.style.opacity = "0.7";
    }
    appendLog(`[Action] ${bName} 지식iN 실시간 1회 낚아채기 시작... (적합도 심사 & 제미나이 1:1 답변)`, "info");
    showToast(`🎯 ${bName} 지식iN 1회 낚아채기가 시작되었습니다!`, "info");
    try {
        const res = await fetch(`/api/kin/${brand}/run`, { method: "POST" });
        const data = await res.json();
        if (data.success) {
            const rec = data.record || {};
            appendLog(`[Success] 🎉 [${bName} 지식iN 등록 완료] '${rec.title || ''}'`, "success");
            showToast(`🎉 ${bName} 지식iN 답변이 성공적으로 등록되었습니다!`, "success");
        } else {
            appendLog(`[Info] ℹ️ [${bName} 지식iN] ${data.message || '새 질문 탐색 완료'}`, "info");
            showToast(data.message || "새 질문 탐색 완료", "info");
        }
        if (typeof fetchStatus === "function") fetchStatus();
    } catch (e) {
        appendLog(`[Error] ❌ 지식iN 통신 오류: ${e}`, "error");
        showToast("지식iN 서버 통신 실패", "error");
    } finally {
        setTimeout(() => {
            if (btn) {
                btn.disabled = false;
                btn.innerText = originalText;
                btn.style.opacity = "1";
            }
        }, 2000);
    }
}

// ☕ 네이버 카페 5일 로테이션 1회 즉시 침투 트리거
async function triggerCafeInfiltration(brand, btn) {
    const nameMap = { aura: "💖 Aura 데이팅", insurance: "🛡️ 보험 리밸런스", stock: "📈 StockMaster AI" };
    const bName = nameMap[brand] || brand;
    const originalText = btn ? btn.innerText : "";
    if (btn) {
        btn.disabled = true;
        btn.innerText = "⏳ 침투 중...";
        btn.style.opacity = "0.7";
    }
    appendLog(`[Action] ${bName} 네이버 카페 5일 로테이션 1회 침투 시작... (파이썬 100% 심사 & 게이트키퍼)`, "info");
    showToast(`☕ ${bName} 네이버 카페 1회 즉시 침투가 시작되었습니다!`, "info");
    try {
        const res = await fetch(`/api/cafe/${brand}/run`, { method: "POST" });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Success] 🎉 [${bName} 카페 침투 가동] ${data.message}`, "success");
            showToast(data.message || "카페 침투가 백그라운드에서 가동되었습니다.", "success");
        } else {
            appendLog(`[Error] ❌ [${bName} 카페] ${data.message || '침투 요청 실패'}`, "error");
            showToast(data.message || "카페 침투 요청 실패", "error");
        }
        if (typeof fetchStatus === "function") fetchStatus();
    } catch (e) {
        appendLog(`[Error] ❌ 카페 침투 통신 오류: ${e}`, "error");
        showToast("카페 침투 통신 실패", "error");
    } finally {
        setTimeout(() => {
            if (btn) {
                btn.disabled = false;
                btn.innerText = originalText;
                btn.style.opacity = "1";
            }
        }, 2000);
    }
}

window.publishOmniBlog = publishOmniBlog;
window.triggerKinCatch = triggerKinCatch;
window.triggerCafeInfiltration = triggerCafeInfiltration;
window.renderHubGrid = renderHubGrid;
window.renderActionGrid = renderHubGrid;
window.startChannelDaemon = startChannelDaemon;
window.stopChannelDaemon = stopChannelDaemon;
window.startStockDaemon = startStockDaemon;
window.stopStockDaemon = stopStockDaemon;
window.startAuraDaemon = startAuraDaemon;
window.stopAuraDaemon = stopAuraDaemon;
window.startInsuranceDaemon = startInsuranceDaemon;
window.stopInsuranceDaemon = stopInsuranceDaemon;
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
window.renderEmergencyGuardBanner = renderEmergencyGuardBanner;
window.renderTodayLiveFeedBoard = renderTodayLiveFeedBoard;
window.updateChannelBadges = updateChannelBadges;

// 초기화 시 엔진 상태 로드
document.addEventListener("DOMContentLoaded", () => {
    setTimeout(loadMediaEngineSettings, 200);
    setTimeout(() => {
        if (typeof updateGoldenBatchPanel === "function") updateGoldenBatchPanel();
    }, 250);
});


