// ==========================================
// [모듈 3] platforms.js: 8대 AI 마케팅 허브 실제 발행 내역 & 실시간 라이브 뷰어 전담 모듈 (가로 1열 와이드 뷰)
// ==========================================

async function loadPlatforms(btn) {
    if (btn) animateRefreshBtn(btn, "8대 허브 실제 발행 내역이 새로고침되었습니다! 🚀");
    const container = document.getElementById("platforms-container");
    const headerTitle = document.getElementById("platforms-header-title");
    const headerDesc = document.getElementById("platforms-header-desc");
    if (!container) return;

    const brandName = currentBrand === "kmarket" ? "K-Market" : "EasyTax";
    if (headerTitle) {
        headerTitle.innerText = `🚀 ${brandName} 8대 AI 마케팅 허브 실제 발행 내역 & 실시간 라이브 뷰어`;
    }
    if (headerDesc) {
        headerDesc.innerText = currentBrand === "kmarket"
            ? "숏폼(4사 동시 전달) · 카드뉴스(3사 동시 전달) · 레딧 · 50만 페북 그룹 · 블로그 SEO · 구글 색인 핑 · 스레드 · 텔레그램 실제 발행본을 실시간으로 직접 확인하고 검증합니다."
            : "세무 숏폼(4사 동시 전달) · 세무 카드뉴스(3사) · 레딧 세무 · 50만 페북 그룹 · 세무 블로그 · 구글 색인 핑 · 스레드 · 텔레그램 실제 발행본을 실시간으로 직접 확인하고 검증합니다.";
    }

    try {
        const res = await fetch("/api/platforms");
        const data = await res.json();
        const platforms = data.platforms || {};

        // 현재 브랜드에 해당하는 8개 채널 필터링
        const filteredKeys = Object.keys(platforms).filter(k => {
            const p = platforms[k];
            return p.brand === currentBrand || p.brand === "all";
        });

        if (filteredKeys.length === 0) {
            container.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--text-secondary);background:#13172E;border-radius:16px;">표시할 플랫폼 채널이 없습니다.</div>`;
            return;
        }

        container.innerHTML = filteredKeys.map((k, idx) => {
            const p = platforms[k];
            const prev = p.published_preview || {};
            const isReady = p.status === "ready";
            const borderCol = currentBrand === "kmarket" ? "#10B981" : "#F59E0B";

            return `
                <div class="platform-card" style="width:100%;background:#0E1229;border:1px solid #1E2548;border-left:5px solid ${borderCol};border-radius:14px;padding:20px;display:flex;flex-direction:column;gap:14px;box-shadow:0 4px 20px rgba(0,0,0,0.35);">
                    <!-- 상단 헤더 줄 (좌측: 허브 정보 & 배포 채널 태그 / 우측: 상태 뱃지 & 액션 버튼) -->
                    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:12px;">
                        <div style="display:flex;align-items:center;gap:12px;">
                            <span style="font-size:12px;font-weight:900;background:rgba(255,255,255,0.1);color:#FFFFFF;padding:3px 8px;border-radius:6px;">#${idx+1}</span>
                            <span style="font-size:24px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.05);border-radius:10px;border:1px solid rgba(255,255,255,0.1);">${p.icon}</span>
                            <div>
                                <div style="display:flex;align-items:center;gap:8px;">
                                    <h4 style="margin:0;font-size:16px;font-weight:800;color:#FFFFFF;">${p.name}</h4>
                                    <span class="badge" style="background:rgba(16,185,129,0.15);color:#34D399;border:1px solid rgba(16,185,129,0.3);font-size:11px;padding:3px 8px;border-radius:12px;font-weight:700;">
                                        🟢 실시간 정상 송출
                                    </span>
                                </div>
                                <div style="font-size:12px;color:#94A3B8;margin-top:2px;display:flex;align-items:center;gap:8px;">
                                    <span>🌐 배포 채널: <strong style="color:#38BDF8;">${p.api_type}</strong></span>
                                    <span>·</span>
                                    <span>비중: <strong style="color:#F8FAFC;">${p.ratio}</strong></span>
                                    <span>·</span>
                                    <span>누적 실적: <strong style="color:#10B981;">${p.daily_count}건</strong></span>
                                </div>
                            </div>
                        </div>

                        <div style="display:flex;align-items:center;gap:10px;">
                            <span style="font-size:11.5px;color:#94A3B8;margin-right:4px;">⏱️ ${p.last_published}</span>
                            ${(prev && prev.url) ? `
                                <a href="${prev.url}" target="_blank" class="btn btn-outline" style="font-size:12px;padding:7px 14px;text-decoration:none;display:flex;align-items:center;gap:5px;background:rgba(56,189,248,0.12);color:#38BDF8;border:1px solid rgba(56,189,248,0.35);font-weight:700;border-radius:8px;">
                                    🔗 실제 원본 확인 →
                                </a>
                            ` : ''}
                            <button class="btn btn-secondary" onclick="testPublishPlatform('${k}', this)" style="font-size:12px;padding:7px 14px;font-weight:700;border-radius:8px;">
                                ⚡ 1건 시험 송출
                            </button>
                        </div>
                    </div>

                    <!-- 📋 풀와이드 실제 발행된 콘텐츠 라이브 검증 박스 -->
                    <div style="background:#070A15;border:1px solid #1A213D;border-radius:10px;padding:16px;display:flex;flex-direction:column;gap:10px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span style="font-size:12px;font-weight:800;color:#38BDF8;display:flex;align-items:center;gap:5px;">
                                <span>📄</span> 실제 발행된 콘텐츠 본문 (실시간 검증 뷰어)
                            </span>
                            <span style="font-size:11.5px;color:#A78BFA;font-weight:700;">🏷️ ${prev.media_tag || '✅ 산출물 생성 완료'}</span>
                        </div>

                        ${(p.feed && p.feed.length > 0) ? `
                            <div style="font-size:11.5px; color:#A78BFA; font-weight:700; display:flex; justify-content:space-between; align-items:center;">
                                <span>📜 실시간 질문 감지 & 80:20 솔루션 답변 피드 (${p.feed.length}건)</span>
                                <span style="font-size:11px; color:#64748b;">마우스로 스크롤하여 이전 내역 열람 👇</span>
                            </div>
                            <div style="max-height:240px; overflow-y:auto; display:flex; flex-direction:column; gap:10px; padding-right:6px;">
                                ${p.feed.map((item, fIdx) => `
                                    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.07); border-left:3px solid #FF4500; border-radius:8px; padding:12px; display:flex; flex-direction:column; gap:6px;">
                                        <div style="display:flex; justify-content:space-between; align-items:center;">
                                            <span style="font-size:11.5px; font-weight:800; color:#FF4500;">#${fIdx+1} 💬 Reddit 질문 감지</span>
                                            <span style="font-size:11px; color:#94A3B8;">${item.created_at}</span>
                                        </div>
                                        <div style="font-size:13px; font-weight:800; color:#F8FAFC;">${item.title}</div>
                                        <div style="font-size:12.5px; color:#CBD5E1; line-height:1.55; background:rgba(0,0,0,0.35); padding:10px 12px; border-radius:6px; white-space:pre-line;">${item.content_text}</div>
                                        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px; font-size:11.5px; border-top:1px dashed rgba(255,255,255,0.06); padding-top:6px;">
                                            <a href="${item.reddit_url}" target="_blank" style="color:#38BDF8; text-decoration:none; font-weight:700;">
                                                🔗 레딧 원본 질문/댓글 새창 보기 →
                                            </a>
                                            <a href="${item.target_url}" target="_blank" style="color:#10B981; text-decoration:none; font-weight:600;">
                                                🛒 본문에 포함된 랜딩 URL: ${item.target_url}
                                            </a>
                                        </div>
                                    </div>
                                `).join("")}
                            </div>
                        ` : `
                            <div style="font-size:14px;font-weight:800;color:#F8FAFC;line-height:1.45;">${prev.title || p.target_content}</div>
                            <div style="font-size:13px;color:#CBD5E1;line-height:1.6;white-space:pre-line;background:rgba(0,0,0,0.35);padding:12px 14px;border-radius:8px;border-left:3px solid #38BDF8;">${prev.caption || p.diagnostic}</div>
                        `}
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
