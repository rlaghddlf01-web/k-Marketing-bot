// ==========================================
// [모듈 8] hashtags.js: 17개국 바이럴 해시태그 전담 모듈
// ==========================================

async function loadHashtags(btn) {
    if (btn) animateRefreshBtn(btn, "17개국 바이럴 해시태그가 새로고침되었습니다! 📈");
    const grid = document.getElementById("hashtags-grid");
    if (!grid) return;

    try {
        const res = await fetch("/api/hashtags");
        const data = await res.json();
        const hashtags = data.hashtags || {};

        grid.innerHTML = Object.entries(hashtags).map(([countryCode, countryData]) => {
            const tags = countryData.tags || [];
            const isKM = currentBrand === "kmarket";
            const badgeColor = isKM ? "#10B981" : "#F59E0B";

            return `
                <div class="hashtag-card" style="background:#13172E;border:1px solid #22294E;border-top:3px solid ${badgeColor};border-radius:12px;padding:16px;box-shadow:0 4px 14px rgba(0,0,0,0.3);">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="font-size:20px;">${countryData.flag || '🌐'}</span>
                            <h4 style="margin:0;font-size:14px;font-weight:700;color:#FFFFFF;">${countryData.country_name} (${countryCode})</h4>
                        </div>
                        <span style="font-size:11px;color:#38BDF8;font-weight:700;">실시간 트렌드</span>
                    </div>
                    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;">
                        ${tags.map(t => `
                            <span style="background:rgba(255,255,255,0.05);color:#CBD5E1;padding:4px 8px;border-radius:6px;font-size:11.5px;border:1px solid rgba(255,255,255,0.08);">
                                #${t}
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

async function refreshHashtags() {
    try {
        const res = await fetch("/api/hashtags/refresh", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "해시태그 트렌드가 갱신되었습니다!", "success");
        loadHashtags();
    } catch (e) {
        showToast("해시태그 갱신 실패", "error");
    }
}

window.loadHashtags = loadHashtags;
window.refreshHashtags = refreshHashtags;
