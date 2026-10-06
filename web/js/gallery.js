// ==========================================
// [모듈 6] gallery.js: 미디어 갤러리 전담 모듈
// ==========================================

let cachedGalleryItems = [];
let currentGalleryFilter = "all";

async function loadGallery(btn) {
    if (btn) animateRefreshBtn(btn, "미디어 갤러리가 새로고침되었습니다! 🎬");
    const grid = document.getElementById("gallery-grid");
    try {
        const res = await fetch("/api/outputs?t=" + Date.now());
        const data = await res.json();

        let items = data.items || [];
        cachedGalleryItems = items;

        const imgCount = items.filter(i => i.type === "image").length;
        const audioCount = items.filter(i => i.type === "audio").length;
        const docCount = items.filter(i => i.type === "doc").length;

        if (document.getElementById("gallery-count-img")) document.getElementById("gallery-count-img").innerText = imgCount;
        if (document.getElementById("gallery-count-audio")) document.getElementById("gallery-count-audio").innerText = audioCount;
        if (document.getElementById("gallery-count-doc")) document.getElementById("gallery-count-doc").innerText = docCount;

        renderGalleryItems();
    } catch (e) {
        console.error("Gallery load error:", e);
    }
}

function filterGallery(filterType, btn) {
    currentGalleryFilter = filterType;
    document.querySelectorAll(".gallery-filter-btn").forEach(b => b.classList.remove("active"));
    if (btn) btn.classList.add("active");
    renderGalleryItems();
}

function renderGalleryItems() {
    const grid = document.getElementById("gallery-grid");
    if (!grid) return;

    let items = [...cachedGalleryItems];

    if (currentBrand === "kmarket") {
        const filtered = items.filter(i => i.brand === "kmarket" || i.name.includes("kmarket"));
        if (filtered.length > 0) items = filtered;
    } else if (currentBrand === "easytax") {
        const filtered = items.filter(i => i.brand === "easytax" || i.name.includes("easytax"));
        if (filtered.length > 0) items = filtered;
    }

    if (currentGalleryFilter !== "all") {
        items = items.filter(i => i.type === currentGalleryFilter);
    }

    if (items.length === 0) {
        grid.innerHTML = `<div style="color: var(--text-secondary); grid-column: 1/-1; text-align:center; padding: 40px; background:#13172E; border-radius:12px; border:1px solid #22294E;">
            <span style="font-size:32px; display:block; margin-bottom:8px;">🖼️</span>
            생성된 ${currentGalleryFilter === 'image' ? '카드뉴스 사진' : '미디어'}가 없습니다.
        </div>`;
        return;
    }

    grid.innerHTML = items.map(item => {
        const isKM = item.brand === "kmarket" || item.name.includes("kmarket");
        const brandBadge = isKM
            ? `<span style="background:rgba(16,185,129,0.2);color:#34d399;padding:3px 8px;border-radius:6px;font-size:11px;font-weight:700;">🛒 K-Market</span>`
            : `<span style="background:rgba(245,158,11,0.2);color:#fbbf24;padding:3px 8px;border-radius:6px;font-size:11px;font-weight:700;">💰 EasyTax</span>`;

        let thumbHtml = "";
        if (item.type === "image") {
            thumbHtml = `
                <div class="gallery-thumb-wrapper" style="background:#080A14;height:220px;display:flex;align-items:center;justify-content:center;overflow:hidden;border-radius:10px 10px 0 0;">
                    <img src="${item.url}" class="gallery-thumb" alt="${item.name}" loading="lazy" onclick="window.open('${item.url}', '_blank')" style="width:100%;height:100%;object-fit:cover;cursor:pointer;" title="클릭하여 원본 사진 크게 보기">
                </div>
            `;
        } else if (item.type === "audio") {
            thumbHtml = `
                <div class="gallery-thumb-wrapper" style="background:linear-gradient(135deg,#1E1B4B,#0F172A);height:180px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:16px;">
                    <span style="font-size:36px;margin-bottom:8px;">🎵</span>
                    <audio controls src="${item.url}" style="width:95%;height:32px;"></audio>
                </div>
            `;
        } else {
            thumbHtml = `
                <div class="gallery-thumb-wrapper" style="background:#0D1126;height:160px;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#94A3B8;">
                    <span style="font-size:38px;margin-bottom:6px;">📄</span>
                    <span style="font-size:11px;color:#94A3B8;">텍스트 / PDF 가이드</span>
                </div>
            `;
        }

        return `
            <div class="gallery-card" style="background:#13172E;border:1px solid #22294E;border-radius:12px;overflow:hidden;box-shadow:0 4px 14px rgba(0,0,0,0.3);">
                ${thumbHtml}
                <div style="padding:14px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                        ${brandBadge}
                        <span style="font-size:11px;color:#64748b;">${item.size}</span>
                    </div>
                    <h4 style="margin:4px 0;font-size:13px;font-weight:700;color:#F8FAFC;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${item.name}">${item.name}</h4>
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px;">
                        <span style="font-size:11px;color:#38BDF8;">${item.category}</span>
                        <a href="${item.url}" target="_blank" style="font-size:11.5px;color:#34D399;text-decoration:none;font-weight:700;">열기 / 다운로드 →</a>
                    </div>
                </div>
            </div>
        `;
    }).join("");
}

window.loadGallery = loadGallery;
window.filterGallery = filterGallery;
window.renderGalleryItems = renderGalleryItems;
