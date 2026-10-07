// ==========================================
// [모듈] telegram_manager.js: 텔레그램 24시간 자율 성장 통합 사령부 (브랜드별 독립)
// 대형 통합 컨테이너 카드 내 3대 핵심 기능 (AI 매니저/브리핑 | 타 그룹 홍보 | 스텔스 초대) 100% 통합
// 디자인: 클린 모던 화이트 & 소프트 라떼 테마 (앱 전반 톤앤매너 완벽 일체화)
// ==========================================

async function loadTelegramCommunityStats() {
    try {
        const brand = typeof currentBrand !== 'undefined' ? currentBrand : 'stock';
        const [statsResp, outreachResp] = await Promise.all([
            fetch(`/api/telegram/stats?brand=${brand}`).catch(() => ({ json: async () => ({}) })),
            fetch('/api/telegram/outreach/status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ brand })
            }).catch(() => ({ json: async () => ({}) }))
        ]);
        const stats    = await statsResp.json();
        const outreach = await outreachResp.json();
        renderTelegramCommunityPanel(stats, outreach);
    } catch (e) {
        console.error('텔레그램 통계 로드 실패:', e);
    }
}

function renderTelegramCommunityPanel(stats, outreach) {
    const container = document.getElementById('telegram-community-panel-container');
    if (!container) return;

    const brand = (stats && stats.brand) ? stats.brand : (typeof currentBrand !== 'undefined' ? currentBrand : 'stock');
    
    // 브랜드별 기본 메타데이터 세팅
    const pipelineData = (typeof APP_PIPELINES !== 'undefined' && APP_PIPELINES[brand]) ? APP_PIPELINES[brand] : null;
    const tgConfig = (pipelineData && pipelineData.telegram) ? pipelineData.telegram : null;

    let brandTitle = '📈 Stock Master';
    let brandColor = '#F59E0B';
    let brandGradient = 'linear-gradient(135deg, #F59E0B, #D97706)';
    let groupName  = 'Stock Master VIP 시황 (t.me/stockmaster_vip)';
    let brandDesc  = '외인/기관 실시간 수급 분석 · 장전 08:30 브리핑 · 조건검색식 · 하루 2회 정기 증시 브리핑';
    let briefingTitle = '⚡ 장전 08:30 AI 시황 브리핑';
    let pollTitle = '📊 내일 주도섹터 투표 1회 생성';

    if (brand === 'aura') {
        brandTitle = '💖 Aura 데이팅';
        brandColor = '#EC4899';
        brandGradient = 'linear-gradient(135deg, #EC4899, #BE185D)';
        groupName  = 'Aura Dating VIP (t.me/aura_dating_official)';
        brandDesc  = '2030 솔로 미팅 & 소개팅 코칭 · 실시간 Q&A · 주말 매칭 알림 · 하루 2회(12:00/21:00) 정기 브리핑';
        briefingTitle = '⚡ 연애 심리 모닝 브리핑';
        pollTitle = '📊 연애 취향 투표 1회 생성';
    } else if (brand === 'insurance') {
        brandTitle = '🛡️ InsureBalance';
        brandColor = '#10B981';
        brandGradient = 'linear-gradient(135deg, #10B981, #059669)';
        groupName  = 'InsureBalance 케어 (t.me/insurebalance_official)';
        brandDesc  = '실손보험 비교 & 갱신 절약 팁 · 실시간 보험료 상담 · 하루 2회 정기 가계 금융 브리핑';
        briefingTitle = '⚡ 가계 보험료 절약 모닝 브리핑';
        pollTitle = '📊 보험 리모델링 투표 1회 생성';
    } else if (brand === 'easytax') {
        brandTitle = '💰 EasyTax';
        brandColor = '#F59E0B';
        brandGradient = 'linear-gradient(135deg, #F59E0B, #D97706)';
        groupName  = 'EasyTax Korea (t.me/easytax_official)';
        brandDesc  = 'E-9 90% 소득세 감면 & D-2 3.3% 환급 팁 · 17개국어 실시간 세무 상담 · 하루 2회 정기 브리핑';
        briefingTitle = '⚡ 세무 환급 브리핑';
        pollTitle = '📊 투표 1회 생성';
    } else if (brand === 'kmarket') {
        brandTitle = '🛒 K-Market';
        brandColor = '#10B981';
        brandGradient = 'linear-gradient(135deg, #10B981, #059669)';
        groupName  = 'KTRS Market Korea (t.me/kmarket_official)';
        brandDesc  = '270개 0원 무료나눔 매물 헌팅 · 17개국어 AI 실시간 응대 · 하루 2회(08:40/20:00) 정기 브리핑';
        briefingTitle = '⚡ 0원 나눔 모닝 브리핑';
        pollTitle = '📊 투표 1회 생성';
    }

    if (tgConfig) {
        if (tgConfig.title) brandTitle = tgConfig.title.replace(' 텔레그램 24시간 자율 성장 통합 사령부', '');
        if (tgConfig.officialColor) brandColor = tgConfig.officialColor;
        if (tgConfig.groupName) groupName = tgConfig.groupName;
        if (tgConfig.desc) brandDesc = tgConfig.desc;
        if (tgConfig.morningBriefingTitle) briefingTitle = tgConfig.morningBriefingTitle;
        if (tgConfig.pollTitle) pollTitle = tgConfig.pollTitle;
    }

    const ai      = (stats && stats.ai_manager)  || {};
    const scraper = (stats && stats.scraper)     || {};
    const ot      = outreach || {};

    const isRunning    = !!ai.is_running;
    const sessionReady = !!ot.session_ready;

    container.innerHTML = `
        <!-- ━━━ 📱 [메인 사령부] 텔레그램 24시간 자율 성장 통합 센터 (클린 라떼 테마) ━━━ -->
        <div class="card" style="background:#FFFFFF;border:1px solid #E5DDD1;border-top:4px solid ${brandColor};border-radius:16px;padding:20px;margin-bottom:24px;box-shadow:var(--shadow-md);">
            
            <!-- 상단 헤더: 브랜드 공식 그룹 & 전체 상태 요약 -->
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:12px;border-bottom:1px solid #E5DDD1;padding-bottom:14px;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:26px;background:#F6F1EA;border:1px solid #E5DDD1;padding:8px 10px;border-radius:12px;">📱</span>
                    <div>
                        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                            <h2 style="margin:0;font-size:16px;font-weight:800;color:#1E1B18;">${brandTitle} 텔레그램 24시간 자율 성장 통합 사령부</h2>
                            <span style="font-size:11px;color:${brandColor};background:#FAF7F2;border:1px solid #E5DDD1;padding:2px 8px;border-radius:6px;font-weight:700;">공식 본진: ${groupName}</span>
                        </div>
                        <p style="margin:3px 0 0;font-size:11.5px;color:#6E665E;">${brandDesc}</p>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <span class="badge" style="background:${isRunning ? 'rgba(16,185,129,0.15)' : '#F6F1EA'};color:${isRunning ? '#059669' : '#6E665E'};border:1px solid ${isRunning ? 'rgba(16,185,129,0.4)' : '#E5DDD1'};padding:5px 12px;border-radius:20px;font-size:11px;font-weight:700;">
                        ${isRunning ? '🟢 24h AI 사령부 가동 중' : '⏸️ 24h 사령부 대기 중'}
                    </span>
                    <span class="badge" style="background:${sessionReady ? 'rgba(2,132,199,0.12)' : 'rgba(220,38,38,0.12)'};color:${sessionReady ? '#0284C7' : '#DC2626'};border:1px solid ${sessionReady ? 'rgba(2,132,199,0.35)' : 'rgba(220,38,38,0.35)'};padding:5px 12px;border-radius:20px;font-size:11px;font-weight:700;">
                        ${sessionReady ? '🟢 서브폰 세션 연동' : '🔴 서브폰 미연동'}
                    </span>
                </div>
            </div>

            <!-- ━━━ 3열 가로 일체형 서브 카드 그리드 (소프트 라떼 카드) ━━━ -->
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:14px;">
                
                <!-- ━━━ [1열] 24시간 AI 매니저 & 일일 브리핑 ━━━ -->
                <div style="background:#F6F1EA;border:1px solid #E5DDD1;border-top:3.5px solid ${brandColor};border-radius:14px;padding:16px;display:flex;flex-direction:column;justify-content:space-between;box-shadow:var(--shadow-sm);gap:12px;">
                    <div>
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:22px;background:#FFFFFF;border:1px solid #E5DDD1;padding:4px 6px;border-radius:8px;">🤖</span>
                                <div>
                                    <h4 style="margin:0;font-size:14px;font-weight:700;color:#1E1B18;">24시간 AI 지킴이 & 브리핑</h4>
                                    <div style="font-size:10.5px;color:#6E665E;">실시간 Q&A · 웰컴 인사 · 정기 브리핑</div>
                                </div>
                            </div>
                            <span style="font-size:10.5px;padding:3px 8px;border-radius:10px;background:${isRunning ? 'rgba(16,185,129,0.15)' : '#FFFFFF'};color:${isRunning ? '#059669' : '#6E665E'};border:1px solid ${isRunning ? 'rgba(16,185,129,0.35)' : '#E5DDD1'};font-weight:700;">
                                ${isRunning ? '🟢 가동 중' : '⚪ 대기'}
                            </span>
                        </div>

                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:6px;">
                            <div style="background:#FFFFFF;border:1px solid #E5DDD1;padding:8px 10px;border-radius:8px;">
                                <div style="font-size:10px;color:#6E665E;font-weight:600;">🤖 AI 질문 답변</div>
                                <div style="font-size:16px;color:#0284C7;font-weight:800;margin-top:2px;">${ai.auto_answered||0} <span style="font-size:10.5px;color:#6E665E;font-weight:500;">건</span></div>
                            </div>
                            <div style="background:#FFFFFF;border:1px solid #E5DDD1;padding:8px 10px;border-radius:8px;">
                                <div style="font-size:10px;color:#6E665E;font-weight:600;">👋 신규 회원 환영</div>
                                <div style="font-size:16px;color:#059669;font-weight:800;margin-top:2px;">${ai.welcomed_count||0} <span style="font-size:10.5px;color:#6E665E;font-weight:500;">명</span></div>
                            </div>
                        </div>
                    </div>

                    <div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px;">
                            <button class="btn" onclick="startTelegramAIManager()" style="background:${brandGradient};color:#FFFFFF;border:none;padding:8px 4px;border-radius:8px;font-size:11.5px;font-weight:800;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,0.1);">
                                🚀 무인 가동
                            </button>
                            <button class="btn" onclick="stopTelegramAIManager()" style="background:#E2E8F0;color:#475569;border:1px solid #CBD5E1;padding:8px 4px;border-radius:8px;font-size:11.5px;font-weight:700;cursor:pointer;">
                                ⏹️ 정지
                            </button>
                        </div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
                            <button onclick="triggerTelegramBroadcast('morning')" style="background:#FFFFFF;border:1px solid #E5DDD1;color:#1E1B18;padding:7px 4px;border-radius:8px;font-size:10.5px;font-weight:700;cursor:pointer;transition:all 0.2s ease;">
                                ${briefingTitle}
                            </button>
                            <button onclick="triggerTelegramBroadcast('poll')" style="background:#FFFFFF;border:1px solid #E5DDD1;color:#D97706;padding:7px 4px;border-radius:8px;font-size:10.5px;font-weight:700;cursor:pointer;transition:all 0.2s ease;">
                                ${pollTitle}
                            </button>
                        </div>
                    </div>
                </div>

                <!-- ━━━ [2열] 타 그룹 홍보 아웃리치 ━━━ -->
                <div style="background:#F6F1EA;border:1px solid #E5DDD1;border-top:3.5px solid #0284C7;border-radius:14px;padding:16px;display:flex;flex-direction:column;justify-content:space-between;box-shadow:var(--shadow-sm);gap:12px;">
                    <div>
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:22px;background:#FFFFFF;border:1px solid #E5DDD1;padding:4px 6px;border-radius:8px;">📢</span>
                                <div>
                                    <h4 style="margin:0;font-size:14px;font-weight:700;color:#1E1B18;">타 그룹 홍보 아웃리치</h4>
                                    <div style="font-size:10.5px;color:#6E665E;">타깃 그룹 분산 홍보 · 5일 쿨다운 (안전 100%)</div>
                                </div>
                            </div>
                            <span style="font-size:10.5px;padding:3px 8px;border-radius:10px;background:rgba(2,132,199,0.12);color:#0284C7;border:1px solid rgba(2,132,199,0.3);font-weight:700;">
                                🟢 서브폰
                            </span>
                        </div>

                        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-bottom:6px;">
                            <div style="background:#FFFFFF;border:1px solid #E5DDD1;padding:8px 4px;border-radius:8px;text-align:center;">
                                <div style="font-size:9.5px;color:#6E665E;font-weight:600;">📢 총 게시</div>
                                <div style="font-size:15px;color:#0284C7;font-weight:800;margin-top:2px;">${ot.total_posted||0} <span style="font-size:9.5px;color:#6E665E;font-weight:500;">회</span></div>
                            </div>
                            <div style="background:#FFFFFF;border:1px solid #E5DDD1;padding:8px 4px;border-radius:8px;text-align:center;">
                                <div style="font-size:9.5px;color:#6E665E;font-weight:600;">🌐 게시 가능</div>
                                <div style="font-size:15px;color:#059669;font-weight:800;margin-top:2px;">${ot.eligible_groups_now||0} <span style="font-size:9.5px;color:#6E665E;font-weight:500;">/ ${ot.target_groups_total||10}</span></div>
                            </div>
                            <div style="background:#FFFFFF;border:1px solid #E5DDD1;padding:8px 4px;border-radius:8px;text-align:center;">
                                <div style="font-size:9.5px;color:#6E665E;font-weight:600;">⏰ 간격</div>
                                <div style="font-size:15px;color:#7C3AED;font-weight:800;margin-top:2px;">${ot.min_interval_days||5} <span style="font-size:9.5px;color:#6E665E;font-weight:500;">일</span></div>
                            </div>
                        </div>
                    </div>

                    <div>
                        <div style="display:grid;grid-template-columns:2fr 1fr;gap:6px;">
                            <button onclick="runOutreach()" style="background:linear-gradient(135deg, #0284C7, #0369A1);color:#FFFFFF;border:none;padding:8px 4px;border-radius:8px;font-size:11.5px;font-weight:800;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,0.1);">
                                📢 홍보 게시 1회 실행
                            </button>
                            <button onclick="stopOutreach()" style="background:#E2E8F0;color:#475569;border:1px solid #CBD5E1;padding:8px 4px;border-radius:8px;font-size:11.5px;font-weight:700;cursor:pointer;">
                                ⏹️ 정지
                            </button>
                        </div>
                    </div>
                </div>

                <!-- ━━━ [3열] 서브폰 스텔스 초대 부스터 ━━━ -->
                <div style="background:#F6F1EA;border:1px solid #E5DDD1;border-top:3.5px solid #D97706;border-radius:14px;padding:16px;display:flex;flex-direction:column;justify-content:space-between;box-shadow:var(--shadow-sm);gap:12px;">
                    <div>
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:22px;background:#FFFFFF;border:1px solid #E5DDD1;padding:4px 6px;border-radius:8px;">🕵️</span>
                                <div>
                                    <h4 style="margin:0;font-size:14px;font-weight:700;color:#1E1B18;">서브폰 스텔스 초대 부스터</h4>
                                    <div style="font-size:10.5px;color:#6E665E;">1일 5명 캡 · 15~30분 슬립 · 메인 계정 보호</div>
                                </div>
                            </div>
                            <span style="font-size:10.5px;padding:3px 8px;border-radius:10px;background:rgba(217,119,6,0.12);color:#D97706;border:1px solid rgba(217,119,6,0.3);font-weight:700;">
                                🚀 부스터
                            </span>
                        </div>

                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:6px;">
                            <div style="background:#FFFFFF;border:1px solid #E5DDD1;padding:8px 10px;border-radius:8px;">
                                <div style="font-size:10px;color:#6E665E;font-weight:600;">🕵️ 오늘 초대</div>
                                <div style="font-size:16px;color:#D97706;font-weight:800;margin-top:2px;">${scraper.today_invited||0} <span style="font-size:10.5px;color:#6E665E;font-weight:500;">/ 5명</span></div>
                            </div>
                            <div style="background:#FFFFFF;border:1px solid #E5DDD1;padding:8px 10px;border-radius:8px;">
                                <div style="font-size:10px;color:#6E665E;font-weight:600;">🌐 타깃 그룹 풀</div>
                                <div style="font-size:16px;color:#7C3AED;font-weight:800;margin-top:2px;">${scraper.target_groups_count||10} <span style="font-size:10.5px;color:#6E665E;font-weight:500;">개</span></div>
                            </div>
                        </div>
                    </div>

                    <div>
                        <div style="display:grid;grid-template-columns:2fr 1fr;gap:6px;">
                            <button onclick="runStealthInvite()" style="background:linear-gradient(135deg, #F59E0B, #D97706);color:#FFFFFF;border:none;padding:8px 4px;border-radius:8px;font-size:11.5px;font-weight:800;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,0.1);">
                                🕵️ 스텔스 초대 1회 실행
                            </button>
                            <button onclick="stopStealthInvite()" style="background:#E2E8F0;color:#475569;border:1px solid #CBD5E1;padding:8px 4px;border-radius:8px;font-size:11.5px;font-weight:700;cursor:pointer;">
                                ⏹️ 정지
                            </button>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    `;
}

// ━━━ API 호출 함수 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async function startTelegramAIManager() {
    const brand = typeof currentBrand !== 'undefined' ? currentBrand : 'stock';
    try {
        const resp = await fetch('/api/telegram/toggle-manager', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ brand, action: 'start' })
        });
        const res = await resp.json();
        if (typeof showToast === 'function') showToast(res.message || '가동되었습니다.', 'success');
        else alert(res.message || '가동되었습니다.');
    } catch (e) {
        if (typeof showToast === 'function') showToast('API 호출 오류: ' + e, 'error');
        else alert('API 호출 중 오류: ' + e);
    }
    loadTelegramCommunityStats();
}

async function stopTelegramAIManager() {
    const brand = typeof currentBrand !== 'undefined' ? currentBrand : 'stock';
    try {
        const resp = await fetch('/api/telegram/toggle-manager', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ brand, action: 'stop' })
        });
        const res = await resp.json();
        if (typeof showToast === 'function') showToast(res.message || '정지되었습니다.', 'warning');
        else alert(res.message || '정지되었습니다.');
    } catch (e) {
        if (typeof showToast === 'function') showToast('API 호출 오류: ' + e, 'error');
        else alert('API 호출 중 오류: ' + e);
    }
    loadTelegramCommunityStats();
}

async function triggerTelegramBroadcast(type) {
    const brand = typeof currentBrand !== 'undefined' ? currentBrand : 'stock';
    try {
        const resp = await fetch('/api/telegram/broadcast', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type, brand })
        });
        const res = await resp.json();
        if (typeof showToast === 'function') showToast(res.message || '발송되었습니다.', 'success');
        else alert(res.message || '발송되었습니다.');
    } catch (e) {
        if (typeof showToast === 'function') showToast('API 호출 오류: ' + e, 'error');
        else alert('API 호출 중 오류: ' + e);
    }
    loadTelegramCommunityStats();
}

async function runOutreach() {
    const brand = typeof currentBrand !== 'undefined' ? currentBrand : 'stock';
    try {
        const resp = await fetch('/api/telegram/outreach/run', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ brand })
        });
        const res = await resp.json();
        if (typeof showToast === 'function') showToast(res.message || '홍보 게시 완료.', 'success');
        else alert(res.message || '홍보 게시 완료.');
    } catch (e) {
        if (typeof showToast === 'function') showToast('API 호출 오류: ' + e, 'error');
        else alert('API 호출 중 오류: ' + e);
    }
    loadTelegramCommunityStats();
}

function stopOutreach() {
    if (typeof showToast === 'function') showToast('📢 타 그룹 홍보 자동 배포가 일시 정지(대기) 상태입니다.', 'info');
    else alert('📢 타 그룹 홍보 자동 배포가 일시 정지(대기) 상태입니다.');
    loadTelegramCommunityStats();
}

async function runStealthInvite() {
    const brand = typeof currentBrand !== 'undefined' ? currentBrand : 'stock';
    try {
        const resp = await fetch('/api/telegram/stealth-invite', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ brand })
        });
        const res = await resp.json();
        if (typeof showToast === 'function') showToast(res.message || '초대 작업 실행.', 'success');
        else alert(res.message || '초대 작업 실행.');
    } catch (e) {
        if (typeof showToast === 'function') showToast('API 호출 오류: ' + e, 'error');
        else alert('API 호출 중 오류: ' + e);
    }
    loadTelegramCommunityStats();
}

function stopStealthInvite() {
    if (typeof showToast === 'function') showToast('🕵️ 서브폰 스텔스 초대가 일시 정지(대기) 상태입니다.', 'info');
    else alert('🕵️ 서브폰 스텔스 초대가 일시 정지(대기) 상태입니다.');
    loadTelegramCommunityStats();
}

// 10초마다 자동 갱신
setInterval(loadTelegramCommunityStats, 10000);
document.addEventListener('DOMContentLoaded', loadTelegramCommunityStats);

window.loadTelegramCommunityStats = loadTelegramCommunityStats;
window.renderTelegramCommunityPanel = renderTelegramCommunityPanel;
window.startTelegramAIManager = startTelegramAIManager;
window.stopTelegramAIManager = stopTelegramAIManager;
window.triggerTelegramBroadcast = triggerTelegramBroadcast;
window.runOutreach = runOutreach;
window.stopOutreach = stopOutreach;
window.runStealthInvite = runStealthInvite;
window.stopStealthInvite = stopStealthInvite;
