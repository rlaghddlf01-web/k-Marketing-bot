// ==========================================
// [모듈 6] gallery.js: 3대 브랜드 미디어 갤러리 및 실시간 GPU 가동 관제 모듈
// ==========================================

let cachedGalleryItems = [];
let cachedGPUStatus = null;
let currentGalleryFilter = "all";

async function loadGallery(btn) {
    if (btn) animateRefreshBtn(btn, "미디어 갤러리가 새로고침되었습니다! 🎬");
    const grid = document.getElementById("gallery-grid");
    try {
        const res = await fetch("/api/outputs?t=" + Date.now());
        const data = await res.json();

        let items = data.items || [];
        cachedGalleryItems = items;
        cachedGPUStatus = data.gpu_status || null;

        const imgCount = items.filter(i => i.type === "image").length;
        const videoCount = items.filter(i => i.type === "video").length;
        const audioCount = items.filter(i => i.type === "audio").length;
        const docCount = items.filter(i => i.type === "doc").length;

        if (document.getElementById("gallery-count-img")) document.getElementById("gallery-count-img").innerText = imgCount;
        if (document.getElementById("gallery-count-video")) document.getElementById("gallery-count-video").innerText = videoCount;
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

    // 3대 브랜드 필터링
    if (typeof currentBrand !== "undefined" && currentBrand) {
        if (currentBrand === "aura") {
            items = items.filter(i => i.brand === "aura" || i.name.includes("아우라") || i.name.toLowerCase().includes("aura"));
        } else if (currentBrand === "insurance") {
            items = items.filter(i => i.brand === "insurance" || i.name.includes("보험") || i.name.toLowerCase().includes("insure"));
        } else if (currentBrand === "stock") {
            items = items.filter(i => i.brand === "stock" || i.name.includes("주식") || i.name.toLowerCase().includes("stock"));
        }
    }

    if (currentGalleryFilter !== "all") {
        items = items.filter(i => i.type === currentGalleryFilter);
    }

    // 🎮 GPU 실시간 가동 중 라이브 프리뷰 카드 (그래픽카드가 작업 중일 때 최우선 노출)
    let gpuActiveCardHtml = "";
    if (cachedGPUStatus && (cachedGPUStatus.status === "busy" || cachedGPUStatus.status === "running" || (cachedGPUStatus.current_task && cachedGPUStatus.status !== "idle"))) {
        const taskName = cachedGPUStatus.current_task || "미디어 실사 렌더링 중";
        const isCardnews = taskName.includes("카드뉴스") || taskName.includes("T2I") || taskName.includes("사진");
        const isShorts = taskName.includes("숏폼") || taskName.includes("S2V") || taskName.includes("영상");
        const badgeColor = isCardnews ? "#EC4899" : isShorts ? "#8B5CF6" : "#F59E0B";
        const glowColor = isCardnews ? "rgba(236,72,153,0.35)" : "rgba(139,92,246,0.35)";

        gpuActiveCardHtml = `
            <div class="gallery-card gpu-rendering-active-card" style="background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%); border: 2px solid ${badgeColor}; border-radius: 14px; overflow: hidden; box-shadow: 0 10px 30px ${glowColor}; animation: gpuPulseBorder 2s infinite alternate; grid-column: span 1;">
                <div style="height: 220px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: radial-gradient(circle, rgba(236,72,153,0.15) 0%, rgba(15,23,42,0.9) 70%); padding: 20px; text-align: center; position: relative; overflow: hidden;">
                    <div style="position: absolute; top: 12px; left: 12px; display: flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.6); padding: 4px 10px; border-radius: 20px; border: 1px solid ${badgeColor};">
                        <span class="pulse-dot" style="background: #10B981; width: 8px; height: 8px; border-radius: 50%; display: inline-block;"></span>
                        <span style="font-size: 11px; font-weight: 800; color: #FFFFFF;">GPU 실시간 연산 중</span>
                    </div>
                    <div style="font-size: 44px; margin-bottom: 8px; animation: floatIcon 3s ease-in-out infinite;">
                        ${isCardnews ? '🎨' : isShorts ? '🎬' : '⚡'}
                    </div>
                    <div style="font-size: 13.5px; font-weight: 800; color: #F8FAFC; max-width: 90%; line-height: 1.4; text-shadow: 0 2px 8px rgba(0,0,0,0.8);">
                        ${taskName}
                    </div>
                    <div style="margin-top: 10px; font-size: 11px; color: #94A3B8; display: flex; align-items: center; gap: 6px;">
                        <span>🎮 RTX 5060 Ti 100% 가속</span>
                        <span>•</span>
                        <span>실시간 생성 중...</span>
                    </div>
                </div>
                <div style="padding: 14px; background: #0B0F19; border-top: 1px solid rgba(255,255,255,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="background: ${badgeColor}; color: #FFFFFF; font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 6px;">
                            ${isCardnews ? '💖 카드뉴스 실사 제작' : isShorts ? '🎬 22초 숏폼 렌더링' : '⚡ GPU 가동'}
                        </span>
                        <span style="font-size: 11px; color: #34D399; font-weight: 700;">🔄 자동 실시간 반영</span>
                    </div>
                    <p style="margin: 8px 0 0 0; font-size: 11.5px; color: #94A3B8; line-height: 1.35;">
                        그래픽카드가 렌더링을 마치면 완성된 고화질 파일이 이 자리에 즉시 표시됩니다.
                    </p>
                </div>
            </div>
        `;
    }

    if (items.length === 0 && !gpuActiveCardHtml) {
        grid.innerHTML = `<div style="color: var(--text-secondary); grid-column: 1/-1; text-align:center; padding: 40px; background:#FFFFFF; border-radius:12px; border:1px solid #E8E3DA;">
            <span style="font-size:32px; display:block; margin-bottom:8px;">🖼️</span>
            생성된 ${currentGalleryFilter === 'image' ? '카드뉴스 사진' : currentGalleryFilter === 'video' ? '숏폼 영상' : '미디어'}가 없습니다.
        </div>`;
        return;
    }

    const cardsHtml = items.map(item => {
        const isAura = item.brand === "aura" || item.name.includes("아우라") || item.name.toLowerCase().includes("aura");
        const isIns = item.brand === "insurance" || item.name.includes("보험") || item.name.toLowerCase().includes("insure");
        const isStock = item.brand === "stock" || item.name.includes("주식") || item.name.toLowerCase().includes("stock");

        const brandBadge = isAura
            ? `<span style="background:#FCE7F3;color:#BE185D;border:1px solid #FBCFE8;padding:3px 8px;border-radius:6px;font-size:11px;font-weight:700;">💖 Aura 데이팅</span>`
            : isIns
            ? `<span style="background:#ECFDF5;color:#059669;border:1px solid #A7F3D0;padding:3px 8px;border-radius:6px;font-size:11px;font-weight:700;">🛡️ 보험 리밸런스</span>`
            : isStock
            ? `<span style="background:#FFFBEB;color:#D97706;border:1px solid #FDE68A;padding:3px 8px;border-radius:6px;font-size:11px;font-weight:700;">📈 StockMaster AI</span>`
            : `<span style="background:#F1F5F9;color:#475569;border:1px solid #CBD5E1;padding:3px 8px;border-radius:6px;font-size:11px;font-weight:700;">⚡ 공용 미디어</span>`;

        let thumbHtml = "";
        if (item.type === "image") {
            thumbHtml = `
                <div class="gallery-thumb-wrapper" style="background:#FAF8F5;border-bottom:1px solid #E8E3DA;height:220px;display:flex;align-items:center;justify-content:center;overflow:hidden;border-radius:10px 10px 0 0;">
                    <img src="${item.url}" class="gallery-thumb" alt="${item.name}" loading="lazy" onclick="window.open('${item.url}', '_blank')" style="width:100%;height:100%;object-fit:cover;cursor:pointer;" title="클릭하여 원본 카드뉴스 사진 크게 보기">
                </div>
            `;
        } else if (item.type === "video") {
            thumbHtml = `
                <div class="gallery-thumb-wrapper" style="background:#0F172A;border-bottom:1px solid #E8E3DA;height:220px;display:flex;flex-direction:column;align-items:center;justify-content:center;overflow:hidden;border-radius:10px 10px 0 0;position:relative;">
                    <video src="${item.url}" controls preload="metadata" style="width:100%;height:100%;object-fit:cover;" title="22초 완성형 숏폼 재생"></video>
                </div>
            `;
        } else if (item.type === "audio") {
            thumbHtml = `
                <div class="gallery-thumb-wrapper" style="background:linear-gradient(135deg,#F5F3FF,#EDE9FE);border-bottom:1px solid #E8E3DA;height:180px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:16px;">
                    <span style="font-size:36px;margin-bottom:8px;">🎵</span>
                    <audio controls src="${item.url}" style="width:95%;height:32px;"></audio>
                </div>
            `;
        } else {
            thumbHtml = `
                <div class="gallery-thumb-wrapper" style="background:#FAF8F5;border-bottom:1px solid #E8E3DA;height:160px;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#64748B;">
                    <span style="font-size:38px;margin-bottom:6px;">📄</span>
                    <span style="font-size:11px;color:#64748B;">SNS 포스팅 가이드 / 브리핑</span>
                </div>
            `;
        }

        return `
            <div class="gallery-card" style="background:#FFFFFF;border:1px solid #E5DDD1;border-radius:14px;overflow:hidden;box-shadow:var(--shadow-md);transition:transform 0.25s ease, box-shadow 0.25s ease;">
                ${thumbHtml}
                <div style="padding:14px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                        ${brandBadge}
                        <span style="font-size:11px;color:#6E665E;">${item.size}</span>
                    </div>
                    <h4 style="margin:4px 0;font-size:13px;font-weight:700;color:#1E1B18;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${item.name}">${item.name}</h4>
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px;">
                        <span style="font-size:11px;color:#0284C7;font-weight:700;">${item.category}</span>
                        <a href="${item.url}" target="_blank" style="font-size:11.5px;color:#059669;text-decoration:none;font-weight:700;">열기 / 다운로드 →</a>
                    </div>
                </div>
            </div>
        `;
    }).join("");

    grid.innerHTML = gpuActiveCardHtml + cardsHtml;
}

// 전역 등록
window.loadGallery = loadGallery;
window.filterGallery = filterGallery;
window.renderGalleryItems = renderGalleryItems;
