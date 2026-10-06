// ==========================================
// [모듈 9] settings.js: 환경 설정 및 API 키 관리 전담 모듈
// ==========================================

async function loadSettings() {
    try {
        const res = await fetch("/api/settings");
        const data = await res.json();
        if (data && data.settings) {
            const s = data.settings;
            if (document.getElementById("cfg-gemini-key")) {
                document.getElementById("cfg-gemini-key").value = s.GEMINI_API_KEY || s.GEMINI_API_KEY_EASYTAX || "";
            }
            if (document.getElementById("cfg-supabase-url")) {
                document.getElementById("cfg-supabase-url").value = s.SUPABASE_URL || "";
            }
            if (document.getElementById("cfg-supabase-key")) {
                document.getElementById("cfg-supabase-key").value = s.SUPABASE_KEY || "";
            }
            if (document.getElementById("cfg-tg-token")) {
                document.getElementById("cfg-tg-token").value = s.TELEGRAM_BOT_TOKEN || "";
            }
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
        TELEGRAM_BOT_TOKEN: document.getElementById("cfg-tg-token")?.value || "",
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
            showToast("✅ 설정이 성공적으로 저장되었습니다!", "success");
            appendLog("[Settings] 듀얼 채널 환경 설정이 성공적으로 저장되었습니다.", "success");
        }
    } catch (e) {
        showToast("❌ 설정 저장 중 오류가 발생했습니다.", "error");
    }
}

window.loadSettings = loadSettings;
window.saveSettings = saveSettings;
