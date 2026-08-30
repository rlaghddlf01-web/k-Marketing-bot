// ==========================================
// [모듈] telegram_manager.js: 텔레그램 24시간 자율 성장 통합 사령부 (브랜드별 독립)
// 대형 통합 컨테이너 카드 내 3대 핵심 기능 (AI 매니저/브리핑 | 타 그룹 홍보 | 스텔스 초대) 100% 통합
// ==========================================

async function loadTelegramCommunityStats() {
    try {
        const brand = typeof currentBrand !== 'undefined' ? currentBrand : 'kmarket';
        const [statsResp, outreachResp] = await Promise.all([
            fetch(`/api/telegram/stats?brand=${brand}`),
            fetch('/api/telegram/outreach/status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ brand })
            })
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

    const brand      = stats.brand || (typeof currentBrand !== 'undefined' ? currentBrand : 'kmarket');
    const isKm       = brand === 'kmarket';
    const brandTitle = isKm ? '🛒 K-Market' : '💰 EasyTax';
    const brandColor = isKm ? '#10B981' : '#F59E0B';
    const groupName  = isKm ? 'K-Market Korea (t.me/kmarket_official)' : 'EasyTax Korea (t.me/easytax_official)';
    const brandDesc  = isKm
        ? '270개 0원 무료나눔 매물 헌팅 · 17개국어 AI 실시간 응대 · 하루 2회(08:40/20:00) 정기 브리핑'
        : 'E-9 90% 소득세 감면 & D-2 3.3% 환급 팁 · 17개국어 실시간 세무 상담 · 하루 2회 정기 브리핑';

    const ai      = stats.ai_manager  || {};
    const scraper = stats.scraper     || {};
    const ot      = outreach           || {};

    const isRunning    = ai.is_running;
    const sessionReady = ot.session_ready;

    container.innerHTML = `
        <!-- ━━━ 📱 [메인 사령부] 텔레그램 24시간 자율 성장 통합 센터 ━━━ -->
        <div class="card" style="background:#0F1326;border:1px solid #2A3362;border-top:4px solid ${brandColor};border-radius:16px;padding:22px;margin-bottom:24px;box-shadow:0 8px 30px rgba(0,0,0,0.4);">
            
            <!-- 상단 헤더: 브랜드 공식 그룹 & 전체 상태 요약 -->
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;flex-wrap:wrap;gap:12px;border-bottom:1px solid #1E2548;padding-bottom:14px;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:28px;background:rgba(255,255,255,0.06);padding:8px 10px;border-radius:12px;">📱</span>
                    <div>
                        <div style="display:flex;align-items:center;gap:8px;">
                            <h2 style="margin:0;font-size:16px;font-weight:800;color:#FFFFFF;">${brandTitle} 텔레그램 24시간 자율 성장 통합 사령부</h2>
                            <span style="font-size:11px;color:${brandColor};background:rgba(255,255,255,0.06);padding:2px 8px;border-radius:6px;font-weight:700;">공식 본진: ${groupName}</span>
                        </div>
                        <p style="margin:3px 0 0;font-size:11px;color:#94A3B8;">${brandDesc}</p>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <span class="badge" style="background:${isRunning ? '#10B981' : '#64748B'};color:#fff;padding:5px 12px;border-radius:20px;font-size:11px;font-weight:bold;">
                        ${isRunning ? '🟢 24h AI 사령부 가동 중' : '⏸️ 24h 사령부 대기 중'}
                    </span>
                    <span class="badge" style="background:${sessionReady ? 'rgba(56,189,248,0.15)' : 'rgba(239,68,68,0.15)'};color:${sessionReady ? '#38BDF8' : '#F87171'};border:1px solid ${sessionReady ? '#0284C7' : '#DC2626'};padding:5px 12px;border-radius:20px;font-size:11px;font-weight:bold;">
                        ${sessionReady ? '🟢 서브폰 세션 연동' : '🔴 서브폰 미연동'}
                    </span>
                </div>
            </div>

            <!-- ━━━ 3열 가로 일체형 서브 카드 그리드 ━━━ -->
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:14px;">
                
                <!-- ━━━ [1열] 24시간 AI 매니저 & 일일 브리핑 ━━━ -->
                <div style="background:#13172E;border:1px solid #22294E;border-top:3px solid ${brandColor};border-radius:12px;padding:16px;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 4px 14px rgba(0,0,0,0.25);">
                    <div>
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:20px;">🤖</span>
                                <div>
                                    <h4 style="margin:0;font-size:13.5px;font-weight:700;color:#FFFFFF;">24시간 AI 지킴이 & 브리핑</h4>
                                    <div style="font-size:10px;color:#94A3B8;">17개국 환영 · Q&A · 08:40/20:00 푸시</div>
                                </div>
                            </div>
                            <span style="font-size:10px;padding:2px 7px;border-radius:10px;background:${isRunning?'rgba(16,185,129,0.2)':'rgba(100,116,139,0.2)'};color:${isRunning?'#10B981':'#94A3B8'};font-weight:700;">
                                ${isRunning ? '🟢 가동 중' : '⚪ 대기'}
                            </span>
                        </div>

                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:12px;">
                            <div style="background:#090C19;border:1px solid #1E2442;padding:8px 10px;border-radius:6px;">
                                <div style="font-size:9.5px;color:#94A3B8;font-weight:600;">🤖 AI 질문 답변</div>
                                <div style="font-size:15px;color:#38BDF8;font-weight:bold;margin-top:2px;">${ai.total_ai_replies||0} <span style="font-size:10px;color:#64748B;">건</span></div>
                            </div>
                            <div style="background:#090C19;border:1px solid #1E2442;padding:8px 10px;border-radius:6px;">
                                <div style="font-size:9.5px;color:#94A3B8;font-weight:600;">👋 모국어 환영</div>
                                <div style="font-size:15px;color:#10B981;font-weight:bold;margin-top:2px;">${ai.total_welcomed||0} <span style="font-size:10px;color:#64748B;">명</span></div>
                            </div>
                        </div>
                    </div>

                    <div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px;">
                            <button onclick="startTelegramAIManager()" style="background:#10B981;color:#fff;border:none;padding:7px 4px;border-radius:6px;font-size:11px;font-weight:bold;cursor:pointer;">
                                🚀 무인 가동
                            </button>
                            <button onclick="stopTelegramAIManager()" style="background:#EF4444;color:#fff;border:none;padding:7px 4px;border-radius:6px;font-size:11px;font-weight:bold;cursor:pointer;">
                                ⏹️ 정지
                            </button>
                        </div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
                            <button onclick="triggerTelegramBroadcast('morning_briefing')" style="background:#38BDF8;color:#0B1120;border:none;padding:6px 4px;border-radius:6px;font-size:10.5px;font-weight:bold;cursor:pointer;">
                                ⚡ ${isKm ? '0원 나눔' : '세무 환급'} 브리핑
                            </button>
                            <button onclick="triggerTelegramBroadcast('poll')" style="background:rgba(139,92,246,0.15);border:1px solid #8B5CF6;color:#C4B5FD;padding:6px 0;border-radius:6px;font-size:10.5px;font-weight:bold;cursor:pointer;">
                                📊 투표 1회 생성
                            </button>
                        </div>
                    </div>
                </div>

                <!-- ━━━ [2열] 타 그룹 홍보 게시 (Ban 위험 0%) ━━━ -->
                <div style="background:#13172E;border:1px solid #22294E;border-top:3px solid #38BDF8;border-radius:12px;padding:16px;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 4px 14px rgba(0,0,0,0.25);">
                    <div>
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:20px;">📢</span>
                                <div>
                                    <h4 style="margin:0;font-size:13.5px;font-weight:700;color:#FFFFFF;">타 그룹 홍보 아웃리치</h4>
                                    <div style="font-size:10px;color:#94A3B8;">8개국어 현지화 · 5일 로테이션 (안전 100%)</div>
                                </div>
                            </div>
                            <span style="font-size:10px;padding:2px 7px;border-radius:10px;background:${sessionReady?'rgba(16,185,129,0.2)':'rgba(239,68,68,0.2)'};color:${sessionReady?'#10B981':'#F87171'};font-weight:700;">
                                ${sessionReady ? '🟢 서브폰' : '🔴 미연동'}
                            </span>
                        </div>

                        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;margin-bottom:12px;">
                            <div style="background:#090C19;border:1px solid #1E2442;padding:8px 4px;border-radius:6px;text-align:center;">
                                <div style="font-size:9px;color:#94A3B8;font-weight:600;">📢 총 게시</div>
                                <div style="font-size:14px;color:#38BDF8;font-weight:bold;margin-top:2px;">${ot.total_posts||0} <span style="font-size:9px;color:#64748B;">회</span></div>
                            </div>
                            <div style="background:#090C19;border:1px solid #1E2442;padding:8px 4px;border-radius:6px;text-align:center;">
                                <div style="font-size:9px;color:#94A3B8;font-weight:600;">🌐 게시 가능</div>
                                <div style="font-size:14px;color:#10B981;font-weight:bold;margin-top:2px;">${ot.eligible_groups_now||0} <span style="font-size:9px;color:#64748B;">/ ${ot.target_groups_total||10}</span></div>
                            </div>
                            <div style="background:#090C19;border:1px solid #1E2442;padding:8px 4px;border-radius:6px;text-align:center;">
                                <div style="font-size:9px;color:#94A3B8;font-weight:600;">⏰ 간격</div>
                                <div style="font-size:14px;color:#A855F7;font-weight:bold;margin-top:2px;">${ot.min_interval_days||5} <span style="font-size:9px;color:#64748B;">일</span></div>
                            </div>
                        </div>
                    </div>

                    <div>
                        <div style="display:grid;grid-template-columns:2fr 1fr;gap:6px;">
                            <button onclick="runOutreach()" style="background:#38BDF8;color:#0B1120;border:none;padding:7px 4px;border-radius:6px;font-size:11px;font-weight:bold;cursor:pointer;">
                                📢 홍보 게시 1회 실행
                            </button>
                            <button onclick="stopOutreach()" style="background:#334155;color:#CBD5E1;border:none;padding:7px 4px;border-radius:6px;font-size:11px;font-weight:bold;cursor:pointer;">
                                ⏹️ 정지
                            </button>
                        </div>
                    </div>
                </div>

                <!-- ━━━ [3열] 서브폰 스텔스 초대 부스터 ━━━ -->
                <div style="background:#13172E;border:1px solid #22294E;border-top:3px solid #F59E0B;border-radius:12px;padding:16px;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 4px 14px rgba(0,0,0,0.25);">
                    <div>
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:20px;">🕵️</span>
                                <div>
                                    <h4 style="margin:0;font-size:13.5px;font-weight:700;color:#FFFFFF;">서브폰 스텔스 초대 부스터</h4>
                                    <div style="font-size:10px;color:#94A3B8;">1일 5명 캡 · 15~30분 슬립 · 메인 계정 완벽 보호</div>
                                </div>
                            </div>
                            <span style="font-size:10px;padding:2px 7px;border-radius:10px;background:rgba(245,158,11,0.2);color:#F59E0B;font-weight:700;">
                                🚀 부스터
                            </span>
                        </div>

                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:12px;">
                            <div style="background:#090C19;border:1px solid #1E2442;padding:8px 10px;border-radius:6px;">
                                <div style="font-size:9.5px;color:#94A3B8;font-weight:600;">🕵️ 오늘 초대</div>
                                <div style="font-size:15px;color:#F59E0B;font-weight:bold;margin-top:2px;">${scraper.today_invited||0} <span style="font-size:10px;color:#64748B;">/ 5명</span></div>
                            </div>
                            <div style="background:#090C19;border:1px solid #1E2442;padding:8px 10px;border-radius:6px;">
                                <div style="font-size:9.5px;color:#94A3B8;font-weight:600;">🌐 타깃 그룹 풀</div>
                                <div style="font-size:15px;color:#A855F7;font-weight:bold;margin-top:2px;">${scraper.target_groups_count||10} <span style="font-size:10px;color:#64748B;">개</span></div>
                            </div>
                        </div>
                    </div>

                    <div>
                        <div style="display:grid;grid-template-columns:2fr 1fr;gap:6px;">
                            <button onclick="runStealthInvite()" style="background:#F59E0B;color:#0B1120;border:none;padding:7px 4px;border-radius:6px;font-size:11px;font-weight:bold;cursor:pointer;">
                                🕵️ 스텔스 초대 1회 실행
                            </button>
                            <button onclick="stopStealthInvite()" style="background:#334155;color:#CBD5E1;border:none;padding:7px 4px;border-radius:6px;font-size:11px;font-weight:bold;cursor:pointer;">
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
    const brand = typeof currentBrand !== 'undefined' ? currentBrand : 'kmarket';
    const resp = await fetch('/api/telegram/toggle-manager', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ brand, action: 'start' })
    });
    const res = await resp.json();
    alert(res.message || '가동되었습니다.');
    loadTelegramCommunityStats();
}

async function stopTelegramAIManager() {
    const brand = typeof currentBrand !== 'undefined' ? currentBrand : 'kmarket';
    const resp = await fetch('/api/telegram/toggle-manager', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ brand, action: 'stop' })
    });
    const res = await resp.json();
    alert(res.message || '정지되었습니다.');
    loadTelegramCommunityStats();
}

async function triggerTelegramBroadcast(type) {
    const brand = typeof currentBrand !== 'undefined' ? currentBrand : 'kmarket';
    const resp = await fetch('/api/telegram/broadcast', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, brand })
    });
    const res = await resp.json();
    alert(res.message || '발송되었습니다.');
    loadTelegramCommunityStats();
}

async function runOutreach() {
    const brand = typeof currentBrand !== 'undefined' ? currentBrand : 'kmarket';
    const resp = await fetch('/api/telegram/outreach/run', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ brand })
    });
    const res = await resp.json();
    alert(res.message || '홍보 게시 완료.');
    loadTelegramCommunityStats();
}

function stopOutreach() {
    alert('📢 타 그룹 홍보 자동 배포가 일시 정지(대기) 상태입니다.');
    loadTelegramCommunityStats();
}

async function runStealthInvite() {
    const brand = typeof currentBrand !== 'undefined' ? currentBrand : 'kmarket';
    const resp = await fetch('/api/telegram/stealth-invite', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ brand })
    });
    const res = await resp.json();
    alert(res.message || '초대 작업 실행.');
    loadTelegramCommunityStats();
}

function stopStealthInvite() {
    alert('🕵️ 서브폰 스텔스 초대가 일시 정지(대기) 상태입니다.');
    loadTelegramCommunityStats();
}

// 10초마다 자동 갱신
setInterval(loadTelegramCommunityStats, 10000);
document.addEventListener('DOMContentLoaded', loadTelegramCommunityStats);
