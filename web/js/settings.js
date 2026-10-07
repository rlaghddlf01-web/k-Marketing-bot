// ==========================================
// [모듈 9] settings.js: 환경 설정 및 API 키 관리 전담 모듈 (3대 슈퍼앱 전담)
// ==========================================

async function loadSettings(btn) {
    if (btn) animateRefreshBtn(btn, "환경 설정값이 다시 로드되었습니다! ⚙️");
    try {
        const res = await fetch("/api/settings");
        const data = await res.json();
        if (data && data.settings) {
            const s = data.settings;
            // 🤖 AI 및 공용 DB
            if (document.getElementById("cfg-gemini-key")) {
                document.getElementById("cfg-gemini-key").value = s.GEMINI_API_KEY || s.GEMINI_API_KEY_EASYTAX || "";
            }
            if (document.getElementById("cfg-supabase-url")) {
                document.getElementById("cfg-supabase-url").value = s.SUPABASE_URL || "";
            }
            if (document.getElementById("cfg-supabase-key")) {
                document.getElementById("cfg-supabase-key").value = s.SUPABASE_KEY || "";
            }

            // 💖 1. Aura 데이팅
            if (document.getElementById("cfg-aura-youtube")) {
                document.getElementById("cfg-aura-youtube").value = s.AURA_YOUTUBE_API_KEY || s.YOUTUBE_API_KEY_AURA || "";
            }
            if (document.getElementById("cfg-aura-meta")) {
                document.getElementById("cfg-aura-meta").value = s.AURA_META_TOKEN || s.META_GRAPH_TOKEN_AURA || "";
            }

            // 🛡️ 2. Insurance 보험비교
            if (document.getElementById("cfg-ins-youtube")) {
                document.getElementById("cfg-ins-youtube").value = s.INSURANCE_YOUTUBE_API_KEY || s.YOUTUBE_API_KEY_INSURANCE || "";
            }
            if (document.getElementById("cfg-ins-meta")) {
                document.getElementById("cfg-ins-meta").value = s.INSURANCE_META_TOKEN || s.META_GRAPH_TOKEN_INSURANCE || "";
            }

            // 📈 3. Stock Master 주식 AI
            if (document.getElementById("cfg-stock-youtube")) {
                document.getElementById("cfg-stock-youtube").value = s.STOCK_YOUTUBE_API_KEY || s.YOUTUBE_API_KEY_STOCK || "";
            }
            if (document.getElementById("cfg-stock-meta")) {
                document.getElementById("cfg-stock-meta").value = s.STOCK_META_TOKEN || s.META_GRAPH_TOKEN_STOCK || "";
            }

            // 🛡️ Anti-Ban 지터 딜레이
            if (document.getElementById("cfg-delay-min")) {
                document.getElementById("cfg-delay-min").value = s.REPLY_DELAY_MIN_SEC || 180;
            }
            if (document.getElementById("cfg-delay-max")) {
                document.getElementById("cfg-delay-max").value = s.REPLY_DELAY_MAX_SEC || 420;
            }
        }
    } catch (e) {
        console.error("Settings load error:", e);
    }
}

async function saveSettings(event) {
    if (event) event.preventDefault();
    const payload = {
        GEMINI_API_KEY: document.getElementById("cfg-gemini-key")?.value || "",
        GEMINI_API_KEY_EASYTAX: document.getElementById("cfg-gemini-key")?.value || "",
        SUPABASE_URL: document.getElementById("cfg-supabase-url")?.value || "",
        SUPABASE_KEY: document.getElementById("cfg-supabase-key")?.value || "",
        
        AURA_YOUTUBE_API_KEY: document.getElementById("cfg-aura-youtube")?.value || "",
        AURA_META_TOKEN: document.getElementById("cfg-aura-meta")?.value || "",

        INSURANCE_YOUTUBE_API_KEY: document.getElementById("cfg-ins-youtube")?.value || "",
        INSURANCE_META_TOKEN: document.getElementById("cfg-ins-meta")?.value || "",

        STOCK_YOUTUBE_API_KEY: document.getElementById("cfg-stock-youtube")?.value || "",
        STOCK_META_TOKEN: document.getElementById("cfg-stock-meta")?.value || "",

        REPLY_DELAY_MIN_SEC: document.getElementById("cfg-delay-min")?.value || "180",
        REPLY_DELAY_MAX_SEC: document.getElementById("cfg-delay-max")?.value || "420"
    };

    try {
        const res = await fetch("/api/settings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            showToast("💾 모든 계정 및 설정이 성공적으로 저장되었습니다!", "success");
            appendLog("[Settings] 3대 슈퍼앱 환경 설정이 성공적으로 저장되었습니다.", "success");
        }
    } catch (e) {
        showToast("❌ 설정 저장 중 오류가 발생했습니다.", "error");
    }
}

window.loadSettings = loadSettings;
window.saveSettings = saveSettings;
