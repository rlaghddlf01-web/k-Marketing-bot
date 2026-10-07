// ==========================================
// [모듈 8] hashtags.js: 실시간 바이럴 키워드 & 해시태그 전담 모듈
// ==========================================

async function loadHashtags(btn) {
    const brand = typeof currentBrand !== "undefined" ? currentBrand : "aura";
    if (btn) animateRefreshBtn(btn, `${brand.toUpperCase()} 실시간 네이버/구글 바이럴 키워드가 새로고침되었습니다! ✨`);
    
    const container = document.getElementById("hashtags-container") || document.getElementById("hashtags-grid");
    const liveTrendsBar = document.getElementById("kr-live-trends-bar");

    try {
        const res = await fetch(`/api/hashtags?brand=${encodeURIComponent(brand)}`);
        const data = await res.json();
        
        // 1. 대한민국 실시간 급상승 트렌드 배너 렌더링
        if (liveTrendsBar) {
            const liveTrends = data.kr_live_trends || data.hashtags?.google_kr_live_trends || ["#실시간트렌드", "#급상승", "#네이버1위", "#구글트렌드", "#쇼츠바이럴"];
            liveTrendsBar.innerHTML = liveTrends.map(t => {
                const tagText = t.startsWith("#") ? t : `#${t}`;
                return `
                    <span style="background:linear-gradient(135deg,#EFF6FF,#EEF2FF);color:#1D4ED8;padding:5px 10px;border-radius:20px;font-size:12px;font-weight:700;border:1px solid #BFDBFE;box-shadow:0 1px 2px rgba(0,0,0,0.05);display:inline-flex;align-items:center;gap:4px;">
                        🔥 ${tagText}
                    </span>
                `;
            }).join("");
        }

        if (!container) return;

        // 2. Aura, Insurance, Stock 3대 한국 브랜드 카테고리 매트릭스 렌더링
        if (data.hashtags && data.hashtags.categories) {
            const categories = data.hashtags.categories;
            const brandColor = brand === "aura" ? "#EC4899" : brand === "insurance" ? "#10B981" : "#3B82F6";
            const brandBadge = brand === "aura" ? "💖 2030 실시간" : brand === "insurance" ? "🛡️ 5대 보장 분석" : "📈 퀀트 AI 수급";

            const countEl = document.getElementById("hashtags-country-count");
            if (countEl) countEl.innerText = Object.keys(categories).length;

            container.innerHTML = Object.entries(categories).map(([catKey, catData]) => {
                const naverKeys = catData.naver_top_keywords || [];
                const googleKeys = catData.google_top_keywords || [];
                const hashtags = catData.viral_hashtags || [];

                return `
                    <div class="hashtag-card" style="background:#FFFFFF;border:1px solid #E5DDD1;border-top:3px solid ${brandColor};border-radius:14px;padding:18px;box-shadow:var(--shadow-md);transition:transform 0.25s ease;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:22px;">${catData.icon || '🎯'}</span>
                                <div>
                                    <h4 style="margin:0;font-size:14.5px;font-weight:700;color:#1E1B18;">${catData.name}</h4>
                                    <span style="font-size:11px;color:#64748B;">${catData.aura_feature || catData.feature || catData.description || ''}</span>
                                </div>
                            </div>
                            <span style="font-size:11px;background:#F8FAFC;color:${brandColor};padding:3px 8px;border-radius:6px;font-weight:700;border:1px solid #E2E8F0;">
                                ${brandBadge}
                            </span>
                        </div>
                        <p style="font-size:11.5px;color:#475569;margin:6px 0 10px 0;line-height:1.4;">${catData.description}</p>
                        
                        <!-- 네이버 실시간 키워드 -->
                        <div style="margin-bottom:8px;">
                            <span style="font-size:10.5px;font-weight:700;color:#059669;display:block;margin-bottom:4px;">🔍 네이버 실시간 검색어 (스마트블록 1위)</span>
                            <div style="display:flex;flex-wrap:wrap;gap:4px;">
                                ${naverKeys.length ? naverKeys.map(k => `
                                    <span style="background:#ECFDF5;color:#065F46;padding:3px 7px;border-radius:5px;font-size:11px;border:1px solid #A7F3D0;font-weight:600;">
                                        ${k}
                                    </span>
                                `).join("") : '<span style="font-size:11px;color:#94A3B8;">수집 대기 중</span>'}
                            </div>
                        </div>

                        <!-- 구글 실시간 질문형 키워드 -->
                        <div style="margin-bottom:8px;">
                            <span style="font-size:10.5px;font-weight:700;color:#2563EB;display:block;margin-bottom:4px;">🌐 구글 실시간 Suggest & 질문형 키워드</span>
                            <div style="display:flex;flex-wrap:wrap;gap:4px;">
                                ${googleKeys.length ? googleKeys.map(k => `
                                    <span style="background:#EFF6FF;color:#1E40AF;padding:3px 7px;border-radius:5px;font-size:11px;border:1px solid #BFDBFE;font-weight:600;">
                                        ${k}
                                    </span>
                                `).join("") : '<span style="font-size:11px;color:#94A3B8;">수집 대기 중</span>'}
                            </div>
                        </div>

                        <!-- 바이럴 해시태그 -->
                        <div style="margin-top:10px;padding-top:8px;border-top:1px dashed #E2E8F0;">
                            <span style="font-size:10.5px;font-weight:700;color:${brandColor};display:block;margin-bottom:4px;">#️⃣ 5대 숏폼 & 블로그 자동 결합 바이럴 태그</span>
                            <div style="display:flex;flex-wrap:wrap;gap:4px;">
                                ${hashtags.map(t => `
                                    <span style="background:#F8FAFC;color:#475569;padding:3px 6px;border-radius:4px;font-size:10.5px;border:1px solid #E2E8F0;font-weight:500;">
                                        ${t.startsWith('#') ? t : '#' + t}
                                    </span>
                                `).join("")}
                            </div>
                        </div>
                    </div>
                `;
            }).join("");
            return;
        }

        // 3. 기타 국가/매트릭스 렌더링
        const hashtags = data.hashtags?.countries || data.hashtags || {};
        const countEl = document.getElementById("hashtags-country-count");
        if (countEl) countEl.innerText = Object.keys(hashtags).length;

        container.innerHTML = Object.entries(hashtags).map(([countryCode, countryData]) => {
            const tags = countryData.tags || countryData.in_korea_common || [];
            return `
                <div class="hashtag-card" style="background:#F6F1EA;border:1px solid #E5DDD1;border-top:3px solid #3B82F6;border-radius:14px;padding:16px;box-shadow:var(--shadow-md);">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="font-size:20px;">${countryData.flag || '🌐'}</span>
                            <h4 style="margin:0;font-size:14px;font-weight:700;color:#1E1B18;">${countryData.country_name || countryData.name || countryCode} (${countryCode})</h4>
                        </div>
                        <span style="font-size:11px;color:#0284C7;font-weight:700;">실시간 트렌드</span>
                    </div>
                    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;">
                        ${tags.map(t => `
                            <span style="background:#FFFFFF;color:#334155;padding:4px 8px;border-radius:6px;font-size:11.5px;border:1px solid #E5DDD1;">
                                ${t.startsWith('#') ? t : '#' + t}
                            </span>
                        `).join("")}
                    </div>
                </div>
            `;
        }).join("");
    } catch (e) {
        console.error("Hashtags load error:", e);
    }
}

async function refreshHashtags(btn) {
    const brand = typeof currentBrand !== "undefined" ? currentBrand : "aura";
    try {
        if (btn) btn.disabled = true;
        const res = await fetch(`/api/hashtags/refresh?brand=${encodeURIComponent(brand)}`, { method: "POST" });
        const data = await res.json();
        if (typeof showToast === "function") {
            showToast(data.message || "실시간 트렌드 및 해시태그가 갱신되었습니다!", "success");
        }
        await loadHashtags();
    } catch (e) {
        if (typeof showToast === "function") {
            showToast("해시태그 갱신 실패", "error");
        }
    } finally {
        if (btn) btn.disabled = false;
    }
}

window.loadHashtags = loadHashtags;
window.refreshHashtags = refreshHashtags;

