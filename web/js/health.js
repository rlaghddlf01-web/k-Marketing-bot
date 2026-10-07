// ==========================================
// [모듈 5] health.js: 3대 슈퍼앱 실시간 장애 감지 & 정직한 실시간 관제 모듈
// ==========================================

async function loadHealthStatus(btn) {
    if (btn) animateRefreshBtn(btn, "실시간 상태가 새로고침되었습니다! 🩺");
    try {
        // 실시간 라이브 피드와 헬스 데이터를 동시 조회
        const [healthRes, feedRes] = await Promise.all([
            fetch("/api/health"),
            fetch("/api/today-live-feed")
        ]);

        const data = await healthRes.json();
        const liveFeed = await feedRes.json();

        const b = currentBrand || "stock";
        const brandName = b === "stock" ? "📈 Stock Master 주식 AI" : b === "aura" ? "💖 Aura AI 데이팅" : b === "insurance" ? "🛡️ InsureBalance 보험비교" : b.toUpperCase();
        const panelTitle = document.getElementById("health-panel-title");
        const panelDesc = document.getElementById("health-panel-desc");
        
        if (panelTitle) {
            panelTitle.innerText = `🩺 [${brandName} 전담] 실시간 채널 무결성 & 장애 관제 센터`;
        }
        if (panelDesc) {
            panelDesc.innerText = "가짜 정상 문구를 전면 배제하고, 실제 발행 글 링크와 세션 만료 장애 및 해결 조치법을 100% 투명하게 실시간 표출합니다.";
        }

        const bFeed = (liveFeed.brands && liveFeed.brands[b]) || {};
        const blog = bFeed.blog || {};
        const kin = bFeed.kin || {};
        const shorts = bFeed.shorts || {};
        const cardnews = bFeed.cardnews || {};
        const channels = blog.channels || {};
        const shortsPlatforms = shorts.platforms || {};
        const cardPlatforms = cardnews.platforms || {};

        // 🚨 1. [장애 및 미발행 감지 분석]
        // - criticalIssues: 카카오/네이버 세션 만료 등 사용자의 즉시 조치(배치 실행)가 필요한 치명적 장애
        // - scheduledPending: 오늘 아직 정기 스케줄 시간이 되지 않은 정상 대기(미발행) 채널
        const criticalIssues = [];
        const scheduledPending = [];

        Object.keys(liveFeed.brands || {}).forEach(bKey => {
            // 현재 선택된 브랜드 전담 필터링
            if (b && b !== "all" && bKey !== b) return;

            const bf = liveFeed.brands[bKey];
            const chs = bf.blog?.channels || {};
            const shs = bf.shorts?.platforms || {};
            const crds = bf.cardnews?.platforms || {};
            const bTitle = bf.brand_name || bKey;

            // 1. 티스토리 블로그
            const batName = bKey === "aura" ? "[1회연동]_Aura_티스토리_영구로그인.bat" 
                          : bKey === "insurance" ? "[1회연동]_보험비교_티스토리_영구로그인.bat" 
                          : "[1회연동]_주식AI_티스토리_영구로그인.bat";

            if (chs.tistory?.is_session_expired) {
                criticalIssues.push({
                    brand: bTitle,
                    type: "세션 만료",
                    channel: "티스토리 (Tistory)",
                    cause: "카카오 로그인 세션 쿠키 수명 만료",
                    action: `바탕화면의 [${batName}] 배치 파일을 1회 실행하여 로그인해 주세요.`
                });
            } else if (chs.tistory?.status === "error") {
                criticalIssues.push({
                    brand: bTitle,
                    type: "발행 오류",
                    channel: "티스토리 (Tistory)",
                    cause: chs.tistory.message || "티스토리 자동 발행 실패",
                    action: `블로그 ID 확인 및 필요 시 바탕화면의 [${batName}] 실행`
                });
            } else if (!chs.tistory?.is_today && !chs.tistory?.is_success) {
                scheduledPending.push({
                    brand: bTitle,
                    type: "미발행",
                    channel: "티스토리 블로그",
                    cause: `오늘자 미발행 (최근 실제 발행: ${chs.tistory?.published_at || '-'})`,
                    action: "오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거"
                });
            }

            // 2. 네이버 블로그
            const naverBat = bKey === "aura" ? "[1회연동]_Aura_네이버_영구로그인.bat"
                           : bKey === "insurance" ? "[1회연동]_보험비교_네이버_영구로그인.bat"
                           : "[1회연동]_주식AI_네이버_영구로그인.bat";

            if (chs.naver_blog?.status === "error") {
                criticalIssues.push({
                    brand: bTitle,
                    type: "발행 에러",
                    channel: "네이버 블로그",
                    cause: chs.naver_blog.message || "네이버 글쓰기 세션 확인 필요",
                    action: `바탕화면의 [${naverBat}] 실행 필요`
                });
            } else if (!chs.naver_blog?.is_today) {
                scheduledPending.push({
                    brand: bTitle,
                    type: "미발행",
                    channel: "네이버 블로그",
                    cause: chs.naver_blog?.message || `오늘자 미발행 (최근 실제 발행: ${chs.naver_blog?.published_at || bf.blog?.last_run_time || '-'})`,
                    action: "오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거"
                });
            }

            // 3. 4대 숏폼 플랫폼
            const spCheckList = [
                { name: "유튜브 쇼츠", data: shs.youtube || {} },
                { name: "인스타그램 릴스", data: shs.instagram || {} },
                { name: "페이스북 릴스", data: shs.facebook || {} },
                { name: "네이버 클립", data: shs.naver_clip || {} }
            ];
            spCheckList.forEach(sp => {
                if (!sp.data.is_today && !sp.data.url) {
                    scheduledPending.push({
                        brand: bTitle,
                        type: "미발행",
                        channel: `숏폼 (${sp.name})`,
                        cause: `오늘자 미발행 (최근 실제 발행: ${sp.data.published_at || '-'})`,
                        action: "오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거"
                    });
                }
            });

            // 4. 5장 카드뉴스 플랫폼
            const cardCheckList = [
                { name: "인스타 캐러셀 (5장)", data: crds.instagram || {} },
                { name: "페이스북 앨범 (5장)", data: crds.facebook || {} },
                { name: "1080x1350 카드뉴스 완제품", data: crds.local_slides || {} }
            ];
            cardCheckList.forEach(cp => {
                if (!cp.data.is_today && !cp.data.url && !cp.data.is_success) {
                    scheduledPending.push({
                        brand: bTitle,
                        type: "미발행",
                        channel: `카드뉴스 (${cp.name})`,
                        cause: `오늘자 미발행 (최근 실제 발행: ${cp.data.published_at || cp.data.time || '-'})`,
                        action: "오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거"
                    });
                }
            });
        });

        // 🧠 2. 최상단: 실시간 장애 & 정기 스케줄 대기 관제 센터 렌더링
        const brainGrid = document.getElementById("health-brain-grid");
        if (brainGrid) {
            if (criticalIssues.length > 0) {
                brainGrid.innerHTML = `
                    <div style="grid-column: 1 / -1; background:#FEF2F2; border:2px solid #F87171; border-radius:12px; padding:16px 20px; box-shadow:0 4px 14px rgba(239,68,68,0.15);">
                        <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
                            <span style="font-size:20px;">🚨</span>
                            <h4 style="margin:0; font-size:16px; font-weight:800; color:#991B1B;">
                                실시간 장애 감지 (${criticalIssues.length}건) — 즉시 조치 필요
                            </h4>
                        </div>
                        <div style="display:flex; flex-direction:column; gap:10px;">
                            ${criticalIssues.map(iss => `
                                <div style="background:#FFFFFF; border:1px solid #FECACA; border-radius:8px; padding:12px 14px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                                    <div>
                                        <div style="display:flex; align-items:center; gap:8px;">
                                            <span style="background:#DC2626; color:#FFFFFF; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px;">${iss.brand}</span>
                                            <strong style="color:#0F172A; font-size:13.5px;">${iss.channel} - ${iss.type}</strong>
                                        </div>
                                        <div style="color:#64748B; font-size:12px; margin-top:4px;">
                                            원인: <span style="color:#DC2626; font-weight:600;">${iss.cause}</span>
                                        </div>
                                    </div>
                                    <div style="background:#FFFBEB; border:1px solid #FDE68A; padding:6px 12px; border-radius:6px; font-size:12px; color:#92400E; font-weight:700;">
                                        👉 ${iss.action}
                                    </div>
                                </div>
                            `).join("")}
                        </div>
                    </div>
                `;
            } else if (scheduledPending.length > 0) {
                brainGrid.innerHTML = `
                    <div style="grid-column: 1 / -1; background:#FFFBEB; border:2px solid #FCD34D; border-radius:12px; padding:16px 20px; box-shadow:0 4px 14px rgba(245,158,11,0.12);">
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:12px;">
                            <div style="display:flex; align-items:center; gap:8px;">
                                <span style="font-size:20px;">⏳</span>
                                <div>
                                    <h4 style="margin:0; font-size:16px; font-weight:800; color:#92400E;">
                                        오늘자 정기 스케줄 대기 & 미발행 관제 (${scheduledPending.length}개 채널 대기 중)
                                    </h4>
                                    <span style="font-size:11.5px; color:#B45309;">치명적 장애 0건 — 정해진 시각에 24시간 무인 자동 발행되거나 수동 1회 즉시 실행 가능합니다.</span>
                                </div>
                            </div>
                            <span style="background:#F59E0B; color:#FFFFFF; font-size:11px; font-weight:800; padding:4px 10px; border-radius:6px;">⚪ STANDBY</span>
                        </div>
                        <div style="display:flex; flex-direction:column; gap:8px; max-height:280px; overflow-y:auto; padding-right:4px;">
                            ${scheduledPending.map(iss => `
                                <div style="background:#FFFFFF; border:1px solid #FDE68A; border-radius:8px; padding:10px 14px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                                    <div>
                                        <div style="display:flex; align-items:center; gap:8px;">
                                            <span style="background:#F59E0B; color:#FFFFFF; font-size:10.5px; font-weight:800; padding:2px 6px; border-radius:4px;">${iss.brand}</span>
                                            <strong style="color:#0F172A; font-size:13px;">${iss.channel} - <span style="color:#B45309;">${iss.type}</span></strong>
                                        </div>
                                        <div style="color:#64748B; font-size:11.5px; margin-top:3px;">
                                            원인: <span style="color:#B45309; font-weight:600;">${iss.cause}</span>
                                        </div>
                                    </div>
                                    <div style="background:#FEF3C7; border:1px solid #FDE68A; padding:5px 10px; border-radius:6px; font-size:11.5px; color:#92400E; font-weight:700;">
                                        👉 ${iss.action}
                                    </div>
                                </div>
                            `).join("")}
                        </div>
                    </div>
                `;
            } else {
                brainGrid.innerHTML = `
                    <div style="grid-column: 1 / -1; background:#F0FDF4; border:2px solid #86EFAC; border-radius:12px; padding:16px 20px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:20px;">✅</span>
                            <h4 style="margin:0; font-size:15px; font-weight:800; color:#166534;">
                                현재 감지된 장애 0건 — 3대 브랜드 모든 채널 100% 정상 작동 중
                            </h4>
                        </div>
                    </div>
                `;
            }
        }

        // 🔐 2.5 6대 플랫폼 영구 로그인 실시간 관제 센터 렌더링 (Threads, Naver, Instagram, Facebook, YouTube, TikTok, Tistory, Brunch)
        const authGrid = document.getElementById("health-auth-sentinel-grid");
        const authSentinelData = data.auth_sentinel || {};
        const brandAuth = (authSentinelData.brands && authSentinelData.brands[b]) || {};
        const platformAuthList = Array.isArray(brandAuth.platforms) 
            ? brandAuth.platforms 
            : Object.values(brandAuth.platforms || {});

        if (authGrid) {
            if (platformAuthList.length === 0) {
                authGrid.innerHTML = `
                    <div style="grid-column: 1 / -1; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:14px; text-align:center; color:#64748B; font-size:12.5px;">
                        선택된 브랜드(${brandName})의 영구 로그인 진단 데이터를 불러오는 중입니다...
                    </div>
                `;
            } else {
                authGrid.innerHTML = platformAuthList.map(p => {
                    const isOk = p.status === "active";
                    const isWarn = p.status === "expiring_soon" || p.status === "missing";
                    const isErr = p.status === "expired" || p.status === "locked";
                    
                    const borderColor = isOk ? "#86EFAC" : isWarn ? "#FCD34D" : "#FCA5A5";
                    const topBorderColor = isOk ? "#22C55E" : isWarn ? "#F59E0B" : "#EF4444";
                    const badgeBg = isOk ? "#ECFDF5" : isWarn ? "#FFFBEB" : "#FEF2F2";
                    const badgeColor = isOk ? "#059669" : isWarn ? "#92400E" : "#DC2626";
                    const badgeBorder = isOk ? "#A7F3D0" : isWarn ? "#FDE68A" : "#FECACA";

                    return `
                        <div style="background:#FFFFFF; border:1.5px solid ${borderColor}; border-top:4px solid ${topBorderColor}; border-radius:12px; padding:14px 16px; box-shadow:0 2px 8px rgba(0,0,0,0.04); display:flex; flex-direction:column; justify-content:space-between; gap:10px;">
                            <div>
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                    <div style="display:flex; align-items:center; gap:8px;">
                                        <span style="font-size:20px;">${p.icon || '🔐'}</span>
                                        <strong style="font-size:14px; color:#0F172A;">${p.platform_name || p.platform}</strong>
                                    </div>
                                    <span style="background:${badgeBg}; color:${badgeColor}; border:1px solid ${badgeBorder}; font-size:11px; font-weight:800; padding:2px 7px; border-radius:5px;">
                                        ${p.status_label || (isOk ? '🟢 정상' : '🔴 점검 필요')}
                                    </span>
                                </div>
                                
                                <div style="display:flex; flex-direction:column; gap:4px; font-size:12px; color:#475569; background:#F8FAFC; padding:8px 10px; border-radius:6px; border:1px solid #F1F5F9;">
                                    <div style="display:flex; justify-content:space-between;">
                                        <span style="color:#64748B;">인증 계정:</span>
                                        <strong style="color:#0F172A;">${p.account || '-'}</strong>
                                    </div>
                                    <div style="display:flex; justify-content:space-between;">
                                        <span style="color:#64748B;">세션 수명:</span>
                                        <span style="color:${isOk ? '#059669' : '#DC2626'}; font-weight:700;">${p.expires_at || '확인 대기'}</span>
                                    </div>
                                </div>
                            </div>

                            ${!isOk ? `
                                <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:8px; padding:10px 12px; font-size:11.5px; line-height:1.45;">
                                    <div style="color:#991B1B; margin-bottom:4px;">
                                        ⚠️ <strong>장애 원인:</strong> <span style="font-weight:600;">${p.cause || '세션 만료 또는 로그인 필요'}</span>
                                    </div>
                                    <div style="color:#1E40AF; background:#EFF6FF; border:1px solid #BFDBFE; padding:6px 8px; border-radius:6px; margin-top:6px; font-weight:700;">
                                        👉 <strong>해결 조치:</strong> ${p.action || '배치 파일 실행으로 1회 로그인'}
                                    </div>
                                </div>
                            ` : `
                                <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:6px; padding:6px 10px; font-size:11.5px; color:#166534; font-weight:600; display:flex; align-items:center; gap:6px;">
                                    <span>✨</span> <span>영구 로그인 활성 상태 — 무인 자동 발행 준비 완료</span>
                                </div>
                            `}
                        </div>
                    `;
                }).join("");
            }
        }

        // 📡 3. 채널별 실제 발행 상태 및 바로가기 링크 렌더링
        const channelsGrid = document.getElementById("health-channels-grid");
        if (channelsGrid) {
            const nb = channels.naver_blog || {};
            const tb = channels.tistory || {};
            const supa = channels.supabase_research || {};
            const kinAnswers = kin.recent_answers || [];

            // 4대 숏폼 플랫폼 목록 생성
            const spList = [
                { key: "youtube", name: "유튜브 쇼츠", icon: "🔴", data: shortsPlatforms.youtube || {} },
                { key: "instagram", name: "인스타그램 릴스", icon: "📸", data: shortsPlatforms.instagram || {} },
                { key: "facebook", name: "페이스북 릴스", icon: "👥", data: shortsPlatforms.facebook || {} },
                { key: "naver_clip", name: "네이버 클립", icon: "🟢", data: shortsPlatforms.naver_clip || {} }
            ];

            const shortsHtml = spList.map(sp => {
                const isPub = sp.data.is_today && sp.data.url;
                const hasPast = Boolean(sp.data.url);
                return `
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:10px 12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span>${sp.icon}</span>
                            <strong style="font-size:13px; color:#0F172A;">${sp.name}</strong>
                            <span style="font-size:11px; color:#64748B;">⏱️ ${sp.data.published_at || '-'}</span>
                            ${isPub 
                                ? `<span style="background:#ECFDF5; color:#059669; font-size:10.5px; font-weight:800; padding:2px 6px; border-radius:4px;">🟢 오늘 발행 완료</span>`
                                : `<span style="background:#FEF3C7; color:#92400E; font-size:10.5px; font-weight:700; padding:2px 6px; border-radius:4px;">⚪ 오늘자 미발행 (정시 대기)</span>`}
                        </div>
                        <div style="display:flex; align-items:center; gap:6px;">
                            ${isPub 
                                ? `<a href="${sp.data.url}" target="_blank" style="font-size:11px; font-weight:700; color:#DC2626; background:#FEE2E2; border:1px solid #FECACA; padding:3px 8px; border-radius:6px; text-decoration:none; display:inline-flex; align-items:center; gap:3px;">
                                    <span>🔗 바로가기</span> <span>↗</span>
                                   </a>`
                                : hasPast
                                ? `<a href="${sp.data.url}" target="_blank" style="font-size:11px; font-weight:700; color:#475569; background:#F1F5F9; border:1px solid #E2E8F0; padding:3px 8px; border-radius:6px; text-decoration:none; display:inline-flex; align-items:center; gap:3px;">
                                    <span>🎬 최근 영상 ↗</span>
                                   </a>`
                                : `<span style="font-size:11px; font-weight:700; color:#92400E; background:#FEF3C7; padding:3px 8px; border-radius:6px;">👉 오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거</span>`}
                        </div>
                    </div>
                `;
            }).join("");

            // 5장 카드뉴스 플랫폼 목록 생성
            const cpList = [
                { key: "instagram", name: "인스타 캐러셀 (5장)", icon: "📸", data: cardPlatforms.instagram || {} },
                { key: "facebook", name: "페이스북 앨범 (5장)", icon: "📘", data: cardPlatforms.facebook || {} },
                { key: "local_slides", name: "1080x1350 카드뉴스 5장 완제품", icon: "📁", data: cardPlatforms.local_slides || {} }
            ];

            const cardnewsHtml = cpList.map(cp => {
                const isPub = cp.data.is_today && (cp.data.url || cp.data.is_success);
                const hasPast = Boolean(cp.data.url || cp.data.is_success);
                return `
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:10px 12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span>${cp.icon}</span>
                            <strong style="font-size:13px; color:#0F172A;">${cp.name}</strong>
                            <span style="font-size:11px; color:#64748B;">⏱️ ${cp.data.published_at || cp.data.time || '-'}</span>
                            ${isPub 
                                ? `<span style="background:#ECFDF5; color:#059669; font-size:10.5px; font-weight:800; padding:2px 6px; border-radius:4px;">🟢 오늘 발행 완료</span>`
                                : `<span style="background:#FEF3C7; color:#92400E; font-size:10.5px; font-weight:700; padding:2px 6px; border-radius:4px;">⚪ 오늘자 미발행 (정시 대기)</span>`}
                        </div>
                        <div style="display:flex; align-items:center; gap:6px;">
                            ${isPub && cp.data.url
                                ? `<a href="${cp.data.url}" target="_blank" style="font-size:11px; font-weight:700; color:#E1306C; background:#FCE7F3; border:1px solid #FBCFE8; padding:3px 8px; border-radius:6px; text-decoration:none; display:inline-flex; align-items:center; gap:3px;">
                                    <span>📸 카드뉴스 열기</span> <span>↗</span>
                                   </a>`
                                : hasPast && cp.data.url
                                ? `<a href="${cp.data.url}" target="_blank" style="font-size:11px; font-weight:700; color:#475569; background:#F1F5F9; border:1px solid #E2E8F0; padding:3px 8px; border-radius:6px; text-decoration:none; display:inline-flex; align-items:center; gap:3px;">
                                    <span>📸 최근 카드뉴스 ↗</span>
                                   </a>`
                                : cp.data.is_success
                                ? `<span style="font-size:11px; font-weight:700; color:#059669; background:#ECFDF5; padding:3px 8px; border-radius:6px;">✅ ${cp.data.slide_count || 5}장 완제품 보관 중</span>`
                                : `<span style="font-size:11px; font-weight:700; color:#92400E; background:#FEF3C7; padding:3px 8px; border-radius:6px;">👉 오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거</span>`}
                        </div>
                    </div>
                `;
            }).join("");

            channelsGrid.innerHTML = `
                ${supa.is_success ? `
                <!-- 0. 🌐 자체 홈페이지 퀀트 리서치 블로그 -->
                <div class="action-card" style="border:1.5px solid #E2E8F0; border-top:4px solid #2563EB; background:#FFFFFF; padding:16px; border-radius:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:18px;">🌐</span>
                            <h4 style="margin:0; font-size:15px; font-weight:800; color:#0F172A;">자체 홈페이지 블로그 (Supabase 본진)</h4>
                        </div>
                        <span style="background:#EFF6FF; color:#1D4ED8; font-size:11px; font-weight:800; padding:3px 8px; border-radius:6px; border:1px solid #BFDBFE;">🟢 1순위 등록 완료</span>
                    </div>
                    <div style="font-size:13px; font-weight:700; color:#1E293B; margin-bottom:8px; line-height:1.4;">
                        ${supa.title || 'StockMaster 자체 퀀트 리서치 칼럼'}
                    </div>
                    <div style="font-size:11.5px; color:#64748B; margin-bottom:12px;">
                        발행 시각: <strong>${supa.published_at || '-'}</strong>
                    </div>
                    <a href="${supa.url || 'https://stockmaster-ai.vercel.app/'}" target="_blank" style="display:inline-flex; align-items:center; gap:6px; padding:7px 12px; background:#2563EB; color:#FFFFFF; border-radius:6px; font-size:12px; font-weight:800; text-decoration:none;">
                        <span>🔗 자체 홈페이지 블로그 열기</span>
                        <span>↗</span>
                    </a>
                </div>
                ` : ''}

                <!-- 1. 네이버 블로그 실시간 상태 -->
                <div class="action-card" style="border:1.5px solid #E2E8F0; border-top:4px solid #03C75A; background:#FFFFFF; padding:16px; border-radius:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:18px;">🟢</span>
                            <h4 style="margin:0; font-size:15px; font-weight:800; color:#0F172A;">네이버 블로그</h4>
                        </div>
                        ${nb.is_success && nb.is_today
                            ? `<span style="background:#ECFDF5; color:#059669; font-size:11px; font-weight:800; padding:3px 8px; border-radius:6px; border:1px solid #A7F3D0;">🟢 오늘 발행 완료</span>` 
                            : `<span style="background:#FEF3C7; color:#92400E; font-size:11px; font-weight:800; padding:3px 8px; border-radius:6px; border:1px solid #FDE68A;">⚪ 오늘자 미발행 (정시 대기)</span>`}
                    </div>
                    <div style="font-size:13px; font-weight:700; color:#1E293B; margin-bottom:8px; line-height:1.4;">
                        ${nb.title || blog.last_title_naver || blog.last_title || '오늘 발행 대기 중'}
                    </div>
                    <div style="font-size:11.5px; color:#64748B; margin-bottom:8px;">
                        발행 시각: <strong>${nb.published_at || blog.last_run_time || '-'}</strong>
                    </div>
                    ${(!nb.is_today) ? `
                        <div style="background:#FFFBEB; border:1px solid #FDE68A; padding:8px 10px; border-radius:6px; font-size:11.5px; color:#92400E; margin-bottom:10px; line-height:1.4;">
                            ⚠️ <strong>원인:</strong> 오늘자 미발행 (최근 실제 발행: ${nb.published_at || blog.last_run_time || '-' })<br>
                            👉 <strong>조치:</strong> 오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거
                        </div>
                    ` : ''}
                    ${nb.url && nb.is_success 
                        ? `<a href="${nb.url}" target="_blank" style="display:inline-flex; align-items:center; gap:6px; padding:7px 12px; background:#03C75A; color:#FFFFFF; border-radius:6px; font-size:12px; font-weight:800; text-decoration:none;">
                            <span>🔗 발행된 네이버 글 열기</span>
                            <span>↗</span>
                           </a>` 
                        : `<span style="font-size:11.5px; color:#94A3B8;">오늘 발행된 네이버 상세 URL이 없습니다.</span>`}
                </div>

                <!-- 2. 티스토리 블로그 실시간 상태 -->
                <div class="action-card" style="border:1.5px solid #E2E8F0; border-top:4px solid #FF5722; background:#FFFFFF; padding:16px; border-radius:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:18px;">🟠</span>
                            <h4 style="margin:0; font-size:15px; font-weight:800; color:#0F172A;">티스토리 (Tistory)</h4>
                        </div>
                        ${tb.is_success
                            ? (tb.is_today 
                                ? `<span style="background:#ECFDF5; color:#059669; font-size:11px; font-weight:800; padding:3px 8px; border-radius:6px;">🟢 오늘 발행 완료</span>`
                                : `<span style="background:#ECFDF5; color:#059669; font-size:11px; font-weight:800; padding:3px 8px; border-radius:6px;">🟢 정상 연동됨 (최신 글 연결)</span>`)
                            : tb.is_session_expired 
                            ? `<span style="background:#FEE2E2; color:#DC2626; font-size:11px; font-weight:800; padding:3px 8px; border-radius:6px; border:1px solid #FECACA;">🔴 세션 만료</span>`
                            : `<span style="background:#FEF3C7; color:#92400E; font-size:11px; font-weight:800; padding:3px 8px; border-radius:6px; border:1px solid #FDE68A;">⚪ 오늘자 미발행 (정시 대기)</span>`}
                    </div>
                    <div style="font-size:13px; font-weight:700; color:#1E293B; margin-bottom:8px; line-height:1.4;">
                        ${tb.title || blog.last_title_tistory || blog.last_title || '오늘 발행 대기 중'}
                    </div>
                    <div style="font-size:11.5px; color:#64748B; margin-bottom:8px;">
                        발행 시각: <strong>${tb.published_at || '-'}</strong>
                    </div>
                    ${tb.is_session_expired 
                        ? `<div style="background:#FEF2F2; border:1px solid #FECACA; padding:8px 10px; border-radius:6px; font-size:11.5px; color:#991B1B; margin-bottom:10px;">
                            ⚠️ <strong>원인:</strong> 카카오 세션 만료<br>
                            👉 <strong>조치:</strong> [1회연동] 티스토리 배치 파일 실행 필요
                           </div>` 
                        : (!tb.is_today && !tb.is_success) ? `
                        <div style="background:#FFFBEB; border:1px solid #FDE68A; padding:8px 10px; border-radius:6px; font-size:11.5px; color:#92400E; margin-bottom:10px; line-height:1.4;">
                            ⚠️ <strong>원인:</strong> 오늘자 미발행 (최근 실제 발행: ${tb.published_at || '-'})<br>
                            👉 <strong>조치:</strong> 오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거
                        </div>
                    ` : ''}
                    ${tb.url && tb.is_success 
                        ? `<a href="${tb.url}" target="_blank" style="display:inline-flex; align-items:center; gap:6px; padding:7px 12px; background:#FF5722; color:#FFFFFF; border-radius:6px; font-size:12px; font-weight:800; text-decoration:none;">
                            <span>🔗 발행된 티스토리 글 열기</span>
                            <span>↗</span>
                           </a>` 
                        : ''}
                </div>

                <!-- 3. 네이버 지식iN 실시간 상태 -->
                <div class="action-card" style="border:1.5px solid #E2E8F0; border-top:4px solid #0284C7; background:#FFFFFF; padding:16px; border-radius:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:18px;">💬</span>
                            <h4 style="margin:0; font-size:15px; font-weight:800; color:#0F172A;">네이버 지식iN</h4>
                        </div>
                        <span style="background:#E0F2FE; color:#0284C7; font-size:11.5px; font-weight:800; padding:3px 8px; border-radius:6px;">
                            오늘 ${kin.today_count || 0} / ${kin.target_count || 10}건 답변
                        </span>
                    </div>
                    ${kinAnswers.length > 0
                        ? `<div style="margin-top:6px; display:flex; flex-direction:column; gap:6px;">
                            ${kinAnswers.slice(0, 3).map((ka, kIdx) => `
                                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:8px 10px; display:flex; justify-content:space-between; align-items:center; gap:8px;">
                                    <div style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex:1;">
                                        <span style="font-size:11px; color:#64748B;">[${ka.created_at || '-'}]</span>
                                        <strong style="font-size:12px; color:#0F172A; margin-left:4px;">${ka.title}</strong>
                                    </div>
                                    <a href="${ka.url}" target="_blank" style="font-size:11px; font-weight:700; color:#0284C7; background:#E0F2FE; padding:3px 8px; border-radius:4px; text-decoration:none; white-space:nowrap;">
                                        열기 ↗
                                    </a>
                                </div>
                            `).join("")}
                           </div>` 
                        : `<div style="font-size:12px; color:#92400E; background:#FFFBEB; border:1px solid #FDE68A; padding:8px 10px; border-radius:6px; margin-top:8px;">
                            ⚠️ <strong>원인:</strong> 오늘자 미발행 (실시간 질문 낚아채기 대기 중)<br>
                            👉 <strong>조치:</strong> 오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거
                           </div>`}
                </div>

                <!-- 4. 4대 숏폼 & 릴스 플랫폼별 실시간 상태 -->
                <div class="action-card" style="border:1.5px solid #E2E8F0; border-top:4px solid #DC2626; background:#FFFFFF; padding:16px; border-radius:12px; grid-column: 1 / -1;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:18px;">🎬</span>
                            <h4 style="margin:0; font-size:15px; font-weight:800; color:#0F172A;">4대 숏폼 플랫폼 개별 송출 현황 (유튜브 · 인스타 · 페이스북 · 네이버 클립)</h4>
                        </div>
                        <span style="background:${shorts.today_count > 0 ? '#ECFDF5' : '#FEF3C7'}; color:${shorts.today_count > 0 ? '#059669' : '#92400E'}; font-size:11.5px; font-weight:800; padding:3px 8px; border-radius:6px;">
                            오늘 ${shorts.today_count || 0}건 송출 완료
                        </span>
                    </div>
                    ${shortsHtml}
                </div>

                <!-- 5. 5장 카드뉴스 플랫폼별 실시간 상태 -->
                <div class="action-card" style="border:1.5px solid #E2E8F0; border-top:4px solid #E1306C; background:#FFFFFF; padding:16px; border-radius:12px; grid-column: 1 / -1;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:18px;">📸</span>
                            <h4 style="margin:0; font-size:15px; font-weight:800; color:#0F172A;">5장 카드뉴스 플랫폼 개별 송출 현황 (인스타 · 페이스북 · 완제품 파일)</h4>
                        </div>
                        <span style="background:${cardnews.today_count > 0 ? '#ECFDF5' : '#FEF3C7'}; color:${cardnews.today_count > 0 ? '#059669' : '#92400E'}; font-size:11.5px; font-weight:800; padding:3px 8px; border-radius:6px;">
                            오늘 ${cardnews.today_count || 0}건 발행 완료
                        </span>
                    </div>
                    ${cardnewsHtml}
                </div>
            `;
        }

        // 헤더 뱃지 업데이트 (치명적 장애 vs 정시 대기 분리)
        const headerBadge = document.getElementById("header-health-score");
        if (headerBadge) {
            if (criticalIssues.length > 0) {
                headerBadge.innerText = `장애 ${criticalIssues.length}건 감지 🔴`;
                headerBadge.style.background = "#FEF2F2";
                headerBadge.style.color = "#DC2626";
                headerBadge.style.borderColor = "#F87171";
            } else if (scheduledPending.length > 0) {
                headerBadge.innerText = `정시 대기 중 (${scheduledPending.length}채널) 🟢`;
                headerBadge.style.background = "#ECFDF5";
                headerBadge.style.color = "#059669";
                headerBadge.style.borderColor = "#A7F3D0";
            } else {
                headerBadge.innerText = "100% 정상 🟢";
                headerBadge.style.background = "#ECFDF5";
                headerBadge.style.color = "#059669";
                headerBadge.style.borderColor = "#A7F3D0";
            }
        }
    } catch (e) {
        console.error("Health status load error:", e);
    }
}

async function runFullHealthDiagnostic(btn) {
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spin-icon" style="display:inline-block;animation:rotateSpin 0.6s linear infinite;">🔄</span> 자가진단 중...`;
    }
    appendLog("[Diagnosis] 전체 시스템 정밀 자가진단 실행 중...", "info");
    showToast("🔍 시스템 전체 자가진단을 시작합니다...", "info");
    try {
        const res = await fetch("/api/health/run-diagnostic", { method: "POST" });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Success] ${data.message}`, "success");
            showToast(data.message, "success");
            await loadHealthStatus();
        }
    } catch (e) {
        appendLog(`[Error] 자가진단 요청 통신 실패: ${e}`, "error");
        showToast("자가진단 통신 오류", "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `🔍 1초 정밀 자가진단`;
        }
    }
}

window.loadHealthStatus = loadHealthStatus;
window.runFullHealthDiagnostic = runFullHealthDiagnostic;
