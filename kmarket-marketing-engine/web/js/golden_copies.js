// ==========================================
// [모듈 7] golden_copies.js: 골든 카피 자가학습 랭킹 전담 모듈
// ==========================================

async function loadGoldenCopies(btn) {
    if (btn) animateRefreshBtn(btn, "골든 카피 랭킹이 새로고침되었습니다! ⭐");
    const tbody = document.getElementById("golden-copies-table-body");
    if (!tbody) return;

    try {
        const res = await fetch(`/api/golden-copies?brand=${currentBrand}`);
        const data = await res.json();
        const copies = data.copies || [];

        if (copies.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:30px;color:#64748b;">등록된 S등급 골든 카피가 없습니다.</td></tr>`;
            return;
        }

        tbody.innerHTML = copies.map((c, idx) => {
            const isKM = c.service_id === "kmarket";
            const brandBadge = isKM
                ? `<span style="background:rgba(16,185,129,0.15);color:#34d399;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:700;">K-Market</span>`
                : `<span style="background:rgba(245,158,11,0.15);color:#fbbf24;padding:2px 6px;border-radius:4px;font-size:10px;font-weight:700;">EasyTax</span>`;
            
            const gradeBadge = c.score >= 85
                ? `<span style="background:rgba(234,179,8,0.2);color:#FACC15;padding:3px 8px;border-radius:6px;font-weight:800;font-size:11px;">🏆 ${c.grade}</span>`
                : `<span style="background:rgba(59,130,246,0.2);color:#60A5FA;padding:3px 8px;border-radius:6px;font-weight:700;font-size:11px;">⭐ ${c.grade}</span>`;

            return `
                <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                    <td style="padding:12px 10px;font-weight:800;color:#94A3B8;">#${idx+1}</td>
                    <td style="padding:12px 10px;">${brandBadge}</td>
                    <td style="padding:12px 10px;font-weight:700;color:#38BDF8;">${c.target_lang || 'en'}</td>
                    <td style="padding:12px 10px;color:#E2E8F0;font-size:12.5px;max-width:380px;line-height:1.4;">${c.content_text}</td>
                    <td style="padding:12px 10px;text-align:center;">${gradeBadge}</td>
                    <td style="padding:12px 10px;text-align:right;font-weight:800;color:#34D399;">${c.clicks || 0} 클릭 / ${c.conversions || 0} 전환</td>
                </tr>
            `;
        }).join("");
    } catch (e) {
        console.error("Golden copies load error:", e);
    }
}

window.loadGoldenCopies = loadGoldenCopies;
