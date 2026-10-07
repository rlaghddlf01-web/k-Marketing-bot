// =========================================================================
// 🇰🇷 [신규 독립 모듈] domestic_engines.js: 국내 16대 포털 & 커뮤니티 마케팅 허브
// =========================================================================

const DOMESTIC_HUBS = [
    {
        num: "#8",
        key: "naver_clip",
        name: "네이버 클립",
        icon: "📎",
        tag: "포털 메인",
        tagColor: "#03C75A",
        title: "Aura 데이팅 / 보험 절약 / 주식 시황 숏폼 네이버 메인 노출",
        desc: "네이버 모바일 메인 MY CLIP 피드 상위 노출 타깃 9:16 고화질 클립 자동 송출",
        badge: "네이버 메인 노출"
    },
    {
        num: "#9",
        key: "omni_blog",
        name: "4대 채널 옴니 블로그",
        icon: "🌐",
        tag: "4대 채널 동시 배포",
        tagColor: "#03C75A",
        title: "본진 앱/피드 · 네이버 스마트블록 · 티스토리 구글 SEO · 카카오 브런치",
        desc: "제미나이 1회 작성 + 16:9 감성 사진 1장 생성 ➔ 4대 플랫폼 동시 무인 배포 (API 요금 절감 0원)",
        badge: "4대 채널 옴니"
    },
    {
        num: "#11",
        key: "naver_post",
        name: "네이버 포스트",
        icon: "📮",
        tag: "카드 매거진",
        tagColor: "#03C75A",
        title: "2030 감성 연애 카드뉴스 · 연령별 필수 보장 차트 · 당일 테마주 지도",
        desc: "네이버 모바일 주제판(연애/경제/증권) 메인 노출 고화질 카드형 매거진",
        badge: "주제판 메인"
    },
    {
        num: "#13",
        key: "search_advisor",
        name: "네이버 서치어드바이저",
        icon: "🧭",
        tag: "즉시 색인 핑",
        tagColor: "#0284C7",
        title: "데이팅 · 보험 · 주식 신규 글 네이버 즉각 색인 핑",
        desc: "신규 작성된 칼럼 URL을 Naver Search Advisor에 즉시 전송하여 5분 내 색인 반영",
        badge: "즉시 색인 핑"
    },
    {
        num: "#14",
        key: "google_ping",
        name: "구글 색인 핑",
        icon: "🌐",
        tag: "구글 핑 API",
        tagColor: "#3B82F6",
        title: "Aura 블로그 · 보험료 실시간 계산기 · 급등 검색식 구글 색인 핑",
        desc: "Google Indexing API 직접 호출로 10분 내 구글 스니펫 최상단 노출 유도",
        badge: "구글 즉시 핑"
    },
    {
        num: "#15",
        key: "naver_kin",
        name: "네이버 지식iN",
        icon: "💡",
        tag: "실시간 Q&A 낚아채기",
        tagColor: "#03C75A",
        title: "연애/소개팅 고민 낚아채기 · 보험료 부담 호소글 답변 · 종목 진단",
        desc: "실시간 등록되는 질문 키워드를 실시간 감지하여 전문 답변 및 링크 자동 제공",
        badge: "지식iN 1위"
    },
    {
        num: "#16",
        key: "naver_cafe",
        name: "네이버 카페",
        icon: "☕",
        tag: "5일 로테이션",
        tagColor: "#059669",
        title: "2030 친목/취미 카페 · 맘카페/재테크 카페 · 주식 종목토론 5일 로테이션",
        desc: "회원수 30만 이상 대형 카페 5일 쿨다운 안티밴 준수 자연스러운 정보글 투고",
        badge: "5일 안티밴"
    },
    {
        num: "#17",
        key: "daum_cafe",
        name: "다음(Daum) 카페",
        icon: "🍵",
        tag: "공감/썰 투고",
        tagColor: "#F59E0B",
        title: "여성시대/익명 카페 연애 썰 · 짠돌이 카페 15만원 절약 썰 · 금융 정보글",
        desc: "대형 다음 카페 현실 공감대 높은 생활 밀착형 썰과 실전 후기 바이럴",
        badge: "공감 썰 1위"
    },
    {
        num: "#18",
        key: "ppomppu",
        name: "뽐뿌 포럼",
        icon: "🛒",
        tag: "커뮤니티 팩트",
        tagColor: "#D97706",
        title: "자유게시판 솔로 공감 썰 · 보험/재테크 포럼 후기 · 증권포럼 수급 분석",
        desc: "뽐뿌 자유게시판/보험상담실/증권포럼 맞춤형 팩트 기반 인기글 공략",
        badge: "포럼 추천글"
    },
    {
        num: "#19",
        key: "dcinside",
        name: "디시인사이드",
        icon: "갤",
        tag: "OCR 자동 돌파",
        tagColor: "#1E3A8A",
        title: "연애/솔로 갤러리 · 보험 갤러리 팩트 폭격 · 주식 갤러리 주도주 수급",
        desc: "디시 한글 초성 캡차 ddddocr 자동 돌파 및 갤러리 맞춤형 자연스러운 투고",
        badge: "캡차 자동 돌파"
    },
    {
        num: "#20",
        key: "bobaedream",
        name: "보배드림",
        icon: "🚗",
        tag: "3050 남성 타깃",
        tagColor: "#475569",
        title: "자유게시판 현실 연애 썰 · 교통사고/운전자보험 합의 팁 · 직장인 매매일지",
        desc: "보배드림 베스트글 공략: 3050 직장인/남성 타깃 생활 꿀팁 및 조언 공유",
        badge: "베스트글 공략"
    },
    {
        num: "#21",
        key: "nate_pann",
        name: "네이트판",
        icon: "💬",
        tag: "톡커들의 선택",
        tagColor: "#DC2626",
        title: "톡커들의선택 소개팅 현실 썰 · 2030 가계 재테크 썰 · 주식 탈출기",
        desc: "네이트판 102030 공감 폭발 썰 및 현실적인 조언 바이럴 침투",
        badge: "판 랭킹 진입"
    },
    {
        num: "#22",
        key: "fmkorea",
        name: "에펨코리아(펨코)",
        icon: "⚽",
        tag: "포럼 인기글",
        tagColor: "#2563EB",
        title: "유머/포럼 소개팅 현실 팁 · 재테크/보험 리모델링 후기 · 주식 시황 분석",
        desc: "펨코 2030 남성 커뮤니티 맞춤형 유쾌하고 담백한 정보글 투고",
        badge: "포텐/인기글"
    },
    {
        num: "#23",
        key: "kakao_channel",
        name: "카카오 알림톡/채널",
        icon: "💬",
        tag: "원클릭 DB 푸시",
        tagColor: "#FACC15",
        title: "주말 연애 매칭 푸시 · 1:1 무료 보험 상담 접수 · 장전 08:30 시황 알림톡",
        desc: "카카오 비즈니스 채널 및 알리고 알림톡 공식 연동 실시간 CRM 자동화",
        badge: "알림톡 자동화"
    }
];

// 2. 국내 16대 마케팅 허브 그리드 동적 렌더링
function renderDomesticEngines() {
    const container = document.getElementById("domestic-grid-container");
    if (!container) return;

    container.innerHTML = DOMESTIC_HUBS.map(h => {
        const accent = h.tagColor || "#10B981";

        return `
        <div class="action-card" id="card-domestic-${h.key}" style="background:#F6F1EA;border:1px solid #E5DDD1;border-top:3px solid ${accent};border-radius:14px;padding:16px;display:flex;flex-direction:column;justify-content:space-between;gap:12px;box-shadow:var(--shadow-md);transition:transform 0.25s ease, box-shadow 0.25s ease;">
            <div>
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <span style="font-size:24px;width:38px;height:38px;display:flex;align-items:center;justify-content:center;background:#FFFFFF;border-radius:8px;border:1px solid #E5DDD1;">${h.icon}</span>
                        <div>
                            <div style="font-size:11px;color:${accent};font-weight:700;">${h.num} ${h.name}</div>
                            <h4 style="margin:2px 0 0 0;font-size:13.5px;font-weight:800;color:#1E1B18;line-height:1.3;">${h.title}</h4>
                        </div>
                    </div>
                    <span style="font-size:10px;font-weight:700;color:${accent};background:#FFFFFF;border:1px solid #E5DDD1;padding:2px 6px;border-radius:4px;white-space:nowrap;">
                        ${h.badge}
                    </span>
                </div>
                <p style="font-size:11.5px;color:#6E665E;margin:0 0 10px 0;line-height:1.45;">${h.desc}</p>

                <!-- 실시간 상태 바 -->
                <div style="display:flex;justify-content:space-between;align-items:center;background:#FFFFFF;padding:6px 10px;border-radius:8px;border:1px solid #E5DDD1;margin-bottom:6px;">
                    <span style="font-size:10.5px;color:#6E665E;">실시간 상태:</span>
                    <span id="badge-status-domestic-${h.key}" class="badge-idle" style="font-size:10.5px;font-weight:700;padding:2px 8px;border-radius:10px;background:#F6F1EA;color:#6E665E;border:1px solid #E5DDD1;">
                        ⚪ 가동 대기
                    </span>
                </div>
            </div>

            <div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px;">
                    <button class="btn" id="btn-start-domestic-${h.key}" onclick="startDomesticDaemon('${h.key}', this)" style="font-size:11.5px;padding:7px 4px;font-weight:800;background:linear-gradient(135deg, ${accent} 0%, #1E293B 100%);color:#FFFFFF;border:none;border-radius:8px;box-shadow:0 3px 8px rgba(0,0,0,0.12);cursor:pointer;" title="24시간 무인 자동 배포 데몬 시작">
                        🚀 무인 가동
                    </button>
                    <button class="btn btn-stop" id="btn-stop-domestic-${h.key}" onclick="stopDomesticDaemon('${h.key}', this)" style="font-size:11.5px;padding:7px 4px;font-weight:700;border-radius:8px;cursor:pointer;" title="무인 데몬 정지">
                        ⏹️ 정지
                    </button>
                </div>
                <button class="btn btn-action" id="btn-run-domestic-${h.key}" onclick="triggerDomesticRun('${h.key}', this)" style="width:100%;font-size:11.5px;padding:7.5px 0;background:#FFFFFF;border:1px solid ${accent};color:${accent};font-weight:800;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.04);cursor:pointer;" title="채널 원클릭 즉시 실행">
                    ⚡ 원클릭 즉시 발행
                </button>
            </div>
        </div>
        `;
    }).join("");
}

// 실행 트리거 함수
async function triggerDomesticRun(hubKey, btn) {
    if (typeof appendLog === "function") appendLog(`[Domestic Hub] #${hubKey} 국내 채널 즉시 1회 발행 시작...`, "info");
    if (typeof showToast === "function") showToast(`#${hubKey} 국내 채널 즉시 발행이 시작되었습니다!`, "success");
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = "⏳ 발행 중...";
    }
    try {
        const brand = (typeof currentBrand !== "undefined") ? currentBrand : "aura";
        const res = await fetch(`/api/run-hub/${brand}/${hubKey}`, { method: "POST" });
        const data = await res.json();
        if (typeof appendLog === "function") appendLog(`[Success] 🎉 ${data.message || '발행 요청 완료'}`, "success");
    } catch (e) {
        if (typeof appendLog === "function") appendLog(`[Error] ❌ 발행 통신 오류: ${e}`, "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = "⚡ 원클릭 즉시 발행";
        }
    }
}

function startDomesticDaemon(hubKey, btn) {
    const badge = document.getElementById(`badge-status-domestic-${hubKey}`);
    if (badge) {
        badge.innerText = "🟢 24h 무인 가동 중";
        badge.style.color = "#34D399";
        badge.style.background = "rgba(16,185,129,0.15)";
    }
    if (typeof showToast === "function") showToast(`#${hubKey} 24시간 무인 데몬이 활성화되었습니다!`, "success");
}

function stopDomesticDaemon(hubKey, btn) {
    const badge = document.getElementById(`badge-status-domestic-${hubKey}`);
    if (badge) {
        badge.innerText = "⚪ 가동 대기";
        badge.style.color = "#94A3B8";
        badge.style.background = "rgba(255,255,255,0.08)";
    }
    if (typeof showToast === "function") showToast(`#${hubKey} 무인 데몬이 정지되었습니다.`, "info");
}

window.renderDomesticEngines = renderDomesticEngines;
window.triggerDomesticRun = triggerDomesticRun;
window.startDomesticDaemon = startDomesticDaemon;
window.stopDomesticDaemon = stopDomesticDaemon;

// DOM 로드 시 자동 렌더링
document.addEventListener("DOMContentLoaded", () => {
    setTimeout(renderDomesticEngines, 150);
});
