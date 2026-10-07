// ==========================================
// [모듈 3] platforms.js: 3대 슈퍼앱 8대 AI 마케팅 허브 실제 발행 내역 & 실시간 라이브 뷰어 전담 모듈 (가로 1열 와이드 뷰)
// ==========================================

async function loadPlatforms(btn) {
    if (btn) animateRefreshBtn(btn, "8대 허브 실제 발행 내역이 새로고침되었습니다! 🚀");
    const container = document.getElementById("platforms-container");
    const headerTitle = document.getElementById("platforms-header-title");
    const headerDesc = document.getElementById("platforms-header-desc");
    if (!container) return;

    const brandName = currentBrand === "stock" ? "📈 Stock Master 주식 AI" : currentBrand === "aura" ? "💖 Aura 데이팅" : currentBrand === "insurance" ? "🛡️ InsureBalance 보험비교" : "3대 슈퍼앱";
    if (headerTitle) {
        headerTitle.innerText = `🚀 ${brandName} 24대 AI 마케팅 허브 실제 발행 내역 & 실시간 라이브 뷰어`;
    }
    if (headerDesc) {
        headerDesc.innerText = currentBrand === "stock"
            ? "외인/기관 수급 숏폼(유튜브/인스타/틱톡/페북/클립) · 4장 퀀트 카드뉴스 · 옴니 블로그 · 구글/네이버 색인 핑 · 실시간 수급 스레드 · VIP 시황 텔레그램 실제 발행본을 실시간으로 직접 확인하고 검증합니다."
            : currentBrand === "aura"
            ? "소개팅 첫인상 숏폼 · 연애 센스 카드뉴스 · 2030 연애 심리 블로그 · 구글/네이버 색인 핑 · 2030 공감 스레드 · 텔레그램 커뮤니티 실제 발행본을 실시간으로 직접 확인합니다."
            : "보험료 다이어트 숏폼 · 호갱 탈출 카드뉴스 · 4대 옴니 블로그 · 구글/네이버 색인 핑 · 절약 스레드 · 텔레그램 상담실 실제 발행본을 실시간으로 직접 확인합니다.";
    }

    try {
        const res = await fetch("/api/platforms");
        const data = await res.json();
        const platforms = data.platforms || {};

        // 현재 브랜드에 해당하는 채널 필터링 (없으면 전체 채널 표시)
        let filteredKeys = Object.keys(platforms).filter(k => {
            const p = platforms[k];
            return p.brand === currentBrand || p.brand === "all";
        });

        if (filteredKeys.length === 0) {
            filteredKeys = Object.keys(platforms);
        }

        if (filteredKeys.length === 0) {
            container.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--text-secondary);background:#FFFFFF;border:1px solid #E8E3DA;border-radius:16px;">24대 플랫폼 채널이 준비 중입니다.</div>`;
            return;
        }

        const borderCol = currentBrand === "aura" ? "#EC4899" : currentBrand === "insurance" ? "#10B981" : currentBrand === "kmarket" ? "#10B981" : currentBrand === "easytax" ? "#F59E0B" : "#F59E0B";

        container.innerHTML = filteredKeys.map((k, idx) => {
            const p = platforms[k];
            const prev = p.published_preview || {};
            const isReady = p.status === "ready";

            return `
                <div class="platform-card" style="width:100%;background:#F6F1EA;border:1px solid #E5DDD1;border-left:5px solid ${borderCol};border-radius:14px;padding:20px;display:flex;flex-direction:column;gap:14px;box-shadow:var(--shadow-md);transition:transform 0.25s ease, box-shadow 0.25s ease;">
                    <!-- 상단 헤더 줄 (좌측: 허브 정보 & 배포 채널 태그 / 우측: 상태 뱃지 & 액션 버튼) -->
                    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;border-bottom:1px solid #E5DDD1;padding-bottom:12px;">
                        <div style="display:flex;align-items:center;gap:12px;">
                            <span style="font-size:12px;font-weight:900;background:#FFFFFF;color:#7C3AED;padding:3px 8px;border-radius:6px;border:1px solid #E5DDD1;">#${idx+1}</span>
                            <span style="font-size:24px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;background:#FFFFFF;border-radius:10px;border:1px solid #E5DDD1;">${p.icon}</span>
                            <div>
                                <div style="display:flex;align-items:center;gap:8px;">
                                    <h4 style="margin:0;font-size:16px;font-weight:800;color:#1E1B18;">${p.name}</h4>
                                    <span class="badge" style="background:#ECFDF5;color:#059669;border:1px solid #A7F3D0;font-size:11px;padding:3px 8px;border-radius:12px;font-weight:700;">
                                        🟢 실시간 정상 송출
                                    </span>
                                </div>
                                <div style="font-size:12px;color:#6E665E;margin-top:2px;display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                                    <span>🌐 배포 채널: <strong style="color:#0284C7;">${p.api_type}</strong></span>
                                    <span>·</span>
                                    <span>비중: <strong style="color:#1E1B18;">${p.ratio}</strong></span>
                                    <span>·</span>
                                    <span>누적 실적: <strong style="color:#059669;">${p.daily_count}건</strong></span>
                                </div>
                            </div>
                        </div>

                        <div style="display:flex;align-items:center;gap:10px;">
                            <span style="font-size:11.5px;color:#6E665E;margin-right:4px;">⏱️ ${p.last_published}</span>
                            ${(prev && prev.url) ? `
                                <a href="${prev.url}" target="_blank" class="btn btn-outline" style="font-size:12px;padding:7px 14px;text-decoration:none;display:flex;align-items:center;gap:5px;background:#F0F9FF;color:#0284C7;border:1px solid #BAE6FD;font-weight:700;border-radius:8px;">
                                    🔗 실제 원본 확인 →
                                </a>
                            ` : ''}
                            <button class="btn btn-secondary" onclick="testPublishPlatform('${k}', this)" style="font-size:12px;padding:7px 14px;font-weight:700;border-radius:8px;">
                                ⚡ 1건 시험 송출
                            </button>
                        </div>
                    </div>

                    <!-- 📋 풀와이드 실제 발행된 콘텐츠 라이브 검증 박스 -->
                    <div style="background:#FFFFFF;border:1px solid #E5DDD1;border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:10px;box-shadow:var(--shadow-sm);">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span style="font-size:12px;font-weight:800;color:#0284C7;display:flex;align-items:center;gap:5px;">
                                <span>📄</span> 실제 발행된 콘텐츠 본문 & SNS 업로드 가이드 (실시간 검증 뷰어)
                            </span>
                            <span style="font-size:11.5px;color:#7C3AED;font-weight:700;">🏷️ ${prev.media_tag || '✅ 산출물 생성 완료'}</span>
                        </div>

                        <div style="font-size:14px;font-weight:800;color:#0F172A;line-height:1.45;">${prev.title || p.target_content}</div>
                        <div style="font-size:12.5px;color:#334155;line-height:1.65;white-space:pre-line;background:#F5F1E8;padding:12px 14px;border-radius:8px;border-left:3px solid #0284C7;">${prev.caption || p.diagnostic}</div>
                        
                        ${prev.local_path ? `
                            <div style="font-size:11px;color:#64748B;background:#F8FAFC;padding:6px 10px;border-radius:6px;border:1px dashed #CBD5E1;display:flex;align-items:center;gap:6px;">
                                <span>📁 파일 저장 경로:</span>
                                <code style="font-family:'JetBrains Mono',monospace;color:#0F172A;">${prev.local_path}</code>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }).join("");
    } catch (e) {
        console.error("Platforms load error:", e);
    }
}

// 플랫폼 1건 직접 송출 테스트
async function testPublishPlatform(platformId, btn) {
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spin-icon" style="display:inline-block;animation:rotateSpin 0.6s linear infinite;">🔄</span> 송출 중...`;
    }
    try {
        const res = await fetch(`/api/platforms/test-publish/${platformId}`, { method: "POST" });
        const data = await res.json();
        showToast(data.message || "송출 테스트 완료! 피드를 새로고침합니다.", "success");
        appendLog(`[Publish Test] ${data.message}`, "success");
        loadPlatforms();
    } catch (e) {
        showToast("송출 테스트 통신 오류", "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `⚡ 1건 시험 송출`;
        }
    }
}

window.loadPlatforms = loadPlatforms;
window.testPublishPlatform = testPublishPlatform;
