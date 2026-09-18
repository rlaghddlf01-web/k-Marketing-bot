// ==============================================================================
// [모듈 8] hashtags.js: 17개국 바이럴 해시태그 & 대한민국 실시간 트렌드 전담 모듈
// ==============================================================================

async function loadHashtags(btn) {
    if (btn && typeof animateRefreshBtn === "function") {
        animateRefreshBtn(btn, "17개국 바이럴 해시태그가 새로고침되었습니다! 📈");
    }
    const container = document.getElementById("hashtags-container") || document.getElementById("hashtags-grid");
    if (!container) return;

    try {
        const res = await fetch("/api/hashtags");
        const data = await res.json();
        const hashtagDb = data.hashtags || {};
        
        // 1. 🇰🇷 대한민국 영토 내 실시간 급상승 트렌드 바 렌더링
        const krBar = document.getElementById("kr-live-trends-bar");
        const krTrends = hashtagDb.korea_live_trends || ["#한국트렌드", "#실시간급상승", "#서울핫플", "#쇼츠인기", "#koreatrend", "#fyp"];
        if (krBar) {
            krBar.innerHTML = krTrends.map(tag => `
                <span onclick="copyHashtagText('${tag}')" title="클릭하여 복사" style="cursor:pointer;background:rgba(239,68,68,0.15);color:#FCA5A5;border:1px solid rgba(239,68,68,0.35);padding:4px 10px;border-radius:20px;font-size:12px;font-weight:600;display:inline-flex;align-items:center;gap:4px;transition:all 0.2s ease;">
                    ${tag}
                </span>
            `).join("");
        }

        // 2. 17개국 국가별 타깃 매트릭스 렌더링
        const countries = hashtagDb.countries || {};
        const countryEntries = Object.entries(countries);
        
        const countEl = document.getElementById("hashtags-country-count");
        if (countEl) countEl.innerText = countryEntries.length;

        const isKM = (typeof currentBrand !== "undefined" ? currentBrand : "kmarket") === "kmarket";
        const brandColor = isKM ? "#10B981" : "#F59E0B";
        const brandLabel = isKM ? "KTRS 마켓 (0원나눔)" : "EasyTax (세금환급)";

        container.innerHTML = countryEntries.map(([countryCode, countryData]) => {
            const flag = countryData.flag || '🌐';
            const countryName = countryData.name || countryCode.toUpperCase();
            const targetGroup = countryData.target_group || "체류 외국인 유학생 및 근로자";
            
            // 태그 조합
            const inKoreaTags = countryData.in_korea_common || [];
            const serviceTags = (isKM ? countryData.kmarket : countryData.easytax) || [];
            const districtTags = countryData.hot_districts || [];
            const workerTags = isKM ? ["#0원나눔", "#외국인근로자", "#E9비자"] : ["#E9비자", "#외국인근로자", "#세금환급"];

            // 전체 복사용 태그 문자열 (중복 제거)
            const allTags = Array.from(new Set([...workerTags, ...inKoreaTags, ...serviceTags, ...districtTags]));
            const allTagsStr = allTags.join(" ");

            return `
                <div class="hashtag-card" style="background:#13172E;border:1px solid #22294E;border-top:3px solid ${brandColor};border-radius:12px;padding:16px;box-shadow:0 4px 14px rgba(0,0,0,0.3);display:flex;flex-direction:column;justify-content:space-between;">
                    <div>
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:22px;">${flag}</span>
                                <div>
                                    <h4 style="margin:0;font-size:14.5px;font-weight:700;color:#FFFFFF;">${countryName}</h4>
                                    <span style="font-size:11px;color:#94A3B8;">${countryCode.toUpperCase()} • ${brandLabel}</span>
                                </div>
                            </div>
                            <button class="btn btn-secondary" onclick="copyHashtagText('${encodeURIComponent(allTagsStr)}', true)" style="padding:4px 9px;font-size:11px;border-radius:6px;background:rgba(56,189,248,0.1);color:#38BDF8;border:1px solid rgba(56,189,248,0.25);cursor:pointer;">
                                📋 전체복사
                            </button>
                        </div>
                        <p style="font-size:11.5px;color:#94A3B8;margin:6px 0 10px 0;line-height:1.4;">
                            🎯 <strong>타깃:</strong> ${targetGroup}
                        </p>
                    </div>
                    <div style="display:flex;flex-wrap:wrap;gap:5px;margin-top:6px;">
                        ${allTags.map(t => `
                            <span onclick="copyHashtagText('${t}')" title="클릭하여 단일 태그 복사" style="cursor:pointer;background:rgba(255,255,255,0.05);color:#CBD5E1;padding:3px 7px;border-radius:6px;font-size:11px;border:1px solid rgba(255,255,255,0.08);transition:all 0.15s ease;">
                                ${t}
                            </span>
                        `).join("")}
                    </div>
                </div>
            `;
        }).join("");
    } catch (e) {
        console.error("Hashtags load error:", e);
        const container = document.getElementById("hashtags-container") || document.getElementById("hashtags-grid");
        if (container) {
            container.innerHTML = `<div style="grid-column:1/-1;padding:24px;text-align:center;color:#EF4444;">해시태그 데이터를 불러오지 못했습니다: ${e.message}</div>`;
        }
    }
}

function copyHashtagText(text, isEncoded = false) {
    const rawText = isEncoded ? decodeURIComponent(text) : text;
    navigator.clipboard.writeText(rawText).then(() => {
        if (typeof showToast === "function") {
            showToast(isEncoded ? "12개 바이럴 해시태그 전체가 복사되었습니다! 📋" : `${rawText} 복사 완료!`, "success");
        } else {
            alert("복사되었습니다:\n" + rawText);
        }
    }).catch(err => {
        console.error("복사 실패:", err);
    });
}

async function refreshHashtags(btn) {
    if (btn && typeof animateRefreshBtn === "function") {
        animateRefreshBtn(btn, "구글 트렌드 KR 실시간 수집 중...");
    }
    try {
        const res = await fetch("/api/hashtags/refresh", { method: "POST" });
        const data = await res.json();
        if (typeof showToast === "function") {
            showToast(data.message || "17개국 실시간 해시태그 트렌드가 새로고침되었습니다! 🚀", "success");
        }
        await loadHashtags();
    } catch (e) {
        if (typeof showToast === "function") {
            showToast("해시태그 갱신 중 통신 오류", "error");
        }
    }
}

window.loadHashtags = loadHashtags;
window.refreshHashtags = refreshHashtags;
window.copyHashtagText = copyHashtagText;
