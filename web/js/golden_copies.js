// ==========================================
// [모듈 7] golden_copies.js: AI 시나리오 랩 & 5대 포맷 성과 자가학습 랭킹 전담 모듈
// ==========================================

// 1. 🏆 AI 5대 시나리오 성과 랭킹 로드 (Top-Performing Scenarios)
async function loadScenarioRankings(btn) {
    if (btn) animateRefreshBtn(btn, "AI 시나리오 랭킹이 새로고침되었습니다! 🏆");
    const tbody = document.getElementById("golden-copies-body") || document.getElementById("golden-copies-table-body");
    if (!tbody) return;

    const brand = typeof currentBrand !== "undefined" ? currentBrand : "aura";

    try {
        const res = await fetch(`/api/scenarios?brand=${encodeURIComponent(brand)}`);
        const data = await res.json();
        const rankings = data.rankings || [];

        if (rankings.length === 0) {
            // 백업: golden-copies API로 재시도
            const resCopies = await fetch(`/api/golden-copies?brand=${encodeURIComponent(brand)}`);
            const dataCopies = await resCopies.json();
            const copies = dataCopies.copies || [];

            if (copies.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:30px;color:#64748b;">등록된 S등급 시나리오 성과 데이터가 없습니다.</td></tr>`;
                return;
            }

            tbody.innerHTML = copies.map((c, idx) => {
                const score = c.score || 85.0;
                const gradeBadge = score >= 85
                    ? `<span style="background:rgba(234,179,8,0.2);color:#FACC15;padding:3px 8px;border-radius:6px;font-weight:800;font-size:11px;">🏆 S (골든)</span>`
                    : `<span style="background:rgba(59,130,246,0.2);color:#60A5FA;padding:3px 8px;border-radius:6px;font-weight:700;font-size:11px;">⭐ A (우수)</span>`;

                return `
                    <tr style="border-bottom:1px solid #E5DDD1;">
                        <td style="padding:12px 10px;font-weight:800;color:#1E1B18;">#${idx+1} ${gradeBadge}</td>
                        <td style="padding:12px 10px;font-weight:700;color:#7C3AED;">${c.target_lang || 'KR/EN'}</td>
                        <td style="padding:12px 10px;font-weight:700;color:#1E1B18;">${c.service_id || brand} 핵심 시나리오</td>
                        <td style="padding:12px 10px;color:#475569;font-size:12.5px;max-width:320px;line-height:1.4;">${c.content_text || '-'}</td>
                        <td style="padding:12px 10px;text-align:center;font-weight:800;color:#059669;">${c.clicks || 0} 클릭 / ${c.conversions || 0} 전환</td>
                        <td style="padding:12px 10px;text-align:center;font-weight:800;color:#D97706;">${score}점</td>
                        <td style="padding:12px 10px;font-size:11.5px;color:#64748B;">실제 UTM 유입 1위 후킹 패턴</td>
                    </tr>
                `;
            }).join("");
            return;
        }

        tbody.innerHTML = rankings.map((r, idx) => {
            const gradeBadge = (r.score || 0) >= 90
                ? `<span style="background:rgba(234,179,8,0.2);color:#D97706;padding:3px 8px;border-radius:6px;font-weight:800;font-size:11px;">🏆 ${r.rank || '1위'}</span>`
                : `<span style="background:rgba(59,130,246,0.2);color:#2563EB;padding:3px 8px;border-radius:6px;font-weight:700;font-size:11px;">⭐ ${r.rank || (idx+1)+'위'}</span>`;

            return `
                <tr style="border-bottom:1px solid #E5DDD1;">
                    <td style="padding:12px 10px;font-weight:800;color:#1E1B18;">${gradeBadge}</td>
                    <td style="padding:12px 10px;font-weight:700;color:#7C3AED;">${r.format || 'Shorts'}</td>
                    <td style="padding:12px 10px;font-weight:700;color:#1E1B18;">${r.title || '시나리오'}</td>
                    <td style="padding:12px 10px;color:#475569;font-size:12.5px;max-width:320px;line-height:1.4;">${r.hook_text || r.content_text || '-'}</td>
                    <td style="padding:12px 10px;text-align:center;font-weight:800;color:#059669;">${r.clicks || 0} 클릭 / ${r.conversions || 0} 전환</td>
                    <td style="padding:12px 10px;text-align:center;font-weight:800;color:#D97706;">${r.score || 0}점</td>
                    <td style="padding:12px 10px;font-size:11.5px;color:#64748B;">${r.success_factor || '숫자 강조 + 손실 회피 훅'}</td>
                </tr>
            `;
        }).join("");
    } catch (e) {
        console.error("Scenario rankings load error:", e);
    }
}

// 2. 📁 최근 생성된 원천 시나리오 산출물 로드
async function loadRecentScenarios(btn) {
    if (btn) animateRefreshBtn(btn, "최근 원천 시나리오 산출물이 새로고침되었습니다! 📁");
    const container = document.getElementById("recent-scenarios-container");
    if (!container) return;

    const brand = typeof currentBrand !== "undefined" ? currentBrand : "aura";

    try {
        const res = await fetch(`/api/scenarios?brand=${encodeURIComponent(brand)}`);
        const data = await res.json();
        const outputs = data.recent_scenarios || [];

        if (outputs.length === 0) {
            container.innerHTML = `
                <div style="grid-column:1/-1;text-align:center;padding:32px;background:#FAF8F5;border:1px solid #E8E3DA;border-radius:12px;color:#64748B;">
                    <span style="font-size:28px;display:block;margin-bottom:6px;">📝</span>
                    최근 생성된 원천 시나리오 대본이 없습니다. AI 시나리오 엔진이 스케줄에 따라 자동 기획합니다.
                </div>
            `;
            return;
        }

        container.innerHTML = outputs.map(sc => {
            return `
                <div class="platform-card" style="background:#FFFFFF;border:1px solid #E5DDD1;border-radius:12px;padding:16px;box-shadow:var(--shadow-sm);">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                        <span style="font-size:11.5px;font-weight:800;color:#7C3AED;background:#F5F3FF;padding:3px 8px;border-radius:6px;border:1px solid #DDD6FE;">
                            ${sc.format ? sc.format.toUpperCase() : 'SCENARIO'} · ${sc.lang || 'KO'}
                        </span>
                        <span style="font-size:11px;color:#64748B;">${sc.created_at || '방금 전'}</span>
                    </div>
                    <h4 style="margin:4px 0 8px 0;font-size:14px;font-weight:700;color:#1E1B18;">${sc.title || '무제 시나리오'}</h4>
                    <div style="font-size:12px;color:#475569;line-height:1.5;background:#F6F1EA;padding:10px;border-radius:8px;max-height:140px;overflow-y:auto;white-space:pre-line;">
                        ${sc.script || sc.body || sc.content || JSON.stringify(sc, null, 2)}
                    </div>
                </div>
            `;
        }).join("");
    } catch (e) {
        console.error("Recent scenarios load error:", e);
    }
}

// 3. 🧬 1위 대본 기반 프롬프트 자가학습 실행
async function triggerEvolvePrompt(btn) {
    const brand = typeof currentBrand !== "undefined" ? currentBrand : "aura";
    const brandName = brand === "stock" ? "📈 StockMaster AI" : brand === "insurance" ? "🛡️ 보험 리밸런스" : "💖 Aura 데이팅";
    
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spin-icon" style="display:inline-block;animation:rotateSpin 0.6s linear infinite;">🔄</span> 자가학습 연산 중...`;
    }

    appendLog(`[Action] ${brandName} 1위 골든 대본 기반 실시간 프롬프트 자가진화(Self-Evolving) 시작...`, "info");
    showToast(`🧬 ${brandName} 1위 대본 자가학습이 시작되었습니다!`, "info");

    try {
        const res = await fetch(`/api/scenarios/evolve`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ brand })
        });
        const data = await res.json();
        
        if (data.success || data.evolved) {
            appendLog(`[Success] 🎉 [자가학습 완료] ${data.message || '1위 대본 후킹 패턴이 Gemini AI 프롬프트에 자동 주입되었습니다.'}`, "success");
            showToast("🎉 1위 대본 자가학습이 완료되었습니다!", "success");
            
            const descEl = document.getElementById("evolved-rule-desc");
            if (descEl && data.evolved_pattern) {
                descEl.innerText = `[학습된 최적 룰] ${data.evolved_pattern}`;
            }
        } else {
            appendLog(`[Info] ℹ️ ${data.message || '자가학습 완료'}`, "info");
            showToast(data.message || "자가학습 완료", "info");
        }
        
        await loadScenarioRankings();
    } catch (e) {
        appendLog(`[Error] ❌ 자가학습 통신 오류: ${e}`, "error");
        showToast("자가학습 요청 실패", "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `🧬 1위 대본 유전자 자가학습 실행`;
        }
    }
}

// 레거시 호환용
async function loadGoldenCopies(btn) {
    return loadScenarioRankings(btn);
}

window.loadScenarioRankings = loadScenarioRankings;
window.loadRecentScenarios = loadRecentScenarios;
window.triggerEvolvePrompt = triggerEvolvePrompt;
window.loadGoldenCopies = loadGoldenCopies;
