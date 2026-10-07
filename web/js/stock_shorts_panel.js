// ==============================================================================
// 📈 [독립 레고 블록] stock_shorts_panel.js: StockMaster AI 30초 퀀트 숏폼 자율 스케줄러 UI
// ==============================================================================

let stockShortsState = null;
let isStockShortsGenerating = false;

async function fetchStockShortsStatus() {
    try {
        const res = await fetch("/api/stock/shorts/status");
        if (!res.ok) return;
        const data = await res.json();
        stockShortsState = data;
        renderStockShortsSchedulerPanel();
    } catch (e) {
        console.error("숏폼 스케줄러 상태 로드 오류:", e);
    }
}

function renderStockShortsSchedulerPanel() {
    const container = document.getElementById("stock-shorts-scheduler-container");
    if (!container) return;

    // 현재 브랜드가 stock이 아니면 숨김 (stock일 때만 표시)
    if (typeof currentBrand !== "undefined" && currentBrand !== "stock") {
        container.style.display = "none";
        return;
    }
    container.style.display = "block";

    if (!stockShortsState) {
        container.innerHTML = `
            <div class="section-card" style="border-top: 4px solid #F59E0B; padding: 20px; text-align: center;">
                <span class="spin-icon" style="display:inline-block;animation:rotateSpin 0.8s linear infinite;font-size:20px;">🔄</span>
                <p style="margin-top:8px;font-size:13px;color:#64748b;">StockMaster AI 30초 숏폼 스케줄러 상태 불러오는 중...</p>
            </div>
        `;
        return;
    }

    const state = stockShortsState;
    const isWeekday = state.mode_type === "weekday";
    const modeBadgeColor = isWeekday ? "#10B981" : "#3B82F6";
    const modeBgColor = isWeekday ? "#ECFDF5" : "#EFF6FF";
    const modeBorderColor = isWeekday ? "#A7F3D0" : "#BFDBFE";

    const nextInfo = state.next_slot 
        ? `<strong style="color:#D97706;">${state.next_slot.time}</strong> [주제 #${state.next_slot.expected_topic} ${state.next_slot.label}]`
        : "오늘 예정된 슬롯 완료";

    const weekdaySlots = state.weekday_slots || {};
    const weekendSlots = state.weekend_slots || {};

    const historyRows = (state.history || []).slice(-5).reverse().map(h => `
        <tr style="border-bottom: 1px solid #F1F5F9; font-size: 12px;">
            <td style="padding: 8px 6px; color:#64748B;">${h.timestamp ? h.timestamp.split(' ')[1] : '-'}</td>
            <td style="padding: 8px 6px; font-weight:700; color:#1E293B;">주제 #${h.topic_id}</td>
            <td style="padding: 8px 6px; color:#059669; font-weight:600;">${h.duration}s</td>
            <td style="padding: 8px 6px; color:#475569;">${h.file_size_mb} MB</td>
            <td style="padding: 8px 6px;"><span style="background:#ECFDF5; color:#059669; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:700;">🟢 ${h.status || '완료'}</span></td>
        </tr>
    `).join("");

    container.innerHTML = `
        <div class="section-card" style="border-top: 4px solid #F59E0B; margin-bottom: 24px; background: #FFFFFF; box-shadow: 0 4px 20px rgba(245, 158, 11, 0.08);">
            <!-- 상단 헤더 -->
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px; margin-bottom: 16px;">
                <div>
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom: 4px;">
                        <h3 class="section-title" style="margin:0; color:#B45309; font-size:16px; display:flex; align-items:center; gap:6px;">
                            <span>📈</span> StockMaster AI 30초 퀀트 숏폼 자율 스케줄러 센터
                        </h3>
                        <span style="background:${modeBgColor}; border:1px solid ${modeBorderColor}; color:${modeBadgeColor}; padding:3px 8px; border-radius:6px; font-size:11.5px; font-weight:700;">
                            ${state.mode_label}
                        </span>
                    </div>
                    <p class="section-subtitle" style="margin:0; font-size:12.5px; color:#64748b;">
                        365일 24시간 무인 자율 구동 ✕ 평일 3회 순차 롤링 & 주말 2회 리스크 특화 브랜딩
                    </p>
                </div>
                <div style="display:flex; gap:8px; align-items:center;">
                    <div style="background:#FEF3C7; border:1px solid #FDE68A; padding:6px 12px; border-radius:8px; font-size:12px; color:#92400E;">
                        ⏰ 다음 예정: ${nextInfo}
                    </div>
                    <button class="btn btn-secondary" onclick="fetchStockShortsStatus()" style="font-size:12px; padding:6px 10px;">
                        🔄 새로고침
                    </button>
                </div>
            </div>

            <!-- 2열 그리드: 좌측 스케줄 슬롯 제어 / 우측 수동 즉시 생성 & 히스토리 -->
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px;">
                
                <!-- 1. 스케줄 슬롯 제어판 -->
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:14px;">
                    <div style="font-weight:700; font-size:13px; color:#1E293B; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
                        <span>⚙️ 정시 무인 자동 송출 슬롯</span>
                        <span style="font-size:11px; color:#64748B;">한국표준시 (KST)</span>
                    </div>

                    <!-- 평일 3대 슬롯 -->
                    <div style="margin-bottom:12px;">
                        <div style="font-size:11.5px; font-weight:700; color:#059669; margin-bottom:6px;">🔥 평일 정규장 슬롯 (1일 3회 순차 롤링)</div>
                        <div style="display:flex; flex-direction:column; gap:6px;">
                            <label style="display:flex; align-items:center; justify-content:space-between; background:#FFFFFF; padding:8px 10px; border-radius:8px; border:1px solid #E2E8F0; font-size:12px;">
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <input type="checkbox" id="stock-slot-0930-chk" ${weekdaySlots.slot_0930?.enabled ? 'checked' : ''} onchange="saveStockShortsConfig()">
                                    <strong style="color:#0284C7;">1차 09:30</strong> (장 초반 수급·주도주)
                                </div>
                                <span style="font-size:11px; color:#64748B;">주제 1~6 롤링</span>
                            </label>
                            <label style="display:flex; align-items:center; justify-content:space-between; background:#FFFFFF; padding:8px 10px; border-radius:8px; border:1px solid #E2E8F0; font-size:12px;">
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <input type="checkbox" id="stock-slot-1200-chk" ${weekdaySlots.slot_1200?.enabled ? 'checked' : ''} onchange="saveStockShortsConfig()">
                                    <strong style="color:#0284C7;">2차 12:00</strong> (점심 시황·리스크)
                                </div>
                                <span style="font-size:11px; color:#64748B;">주제 1~6 롤링</span>
                            </label>
                            <label style="display:flex; align-items:center; justify-content:space-between; background:#FFFFFF; padding:8px 10px; border-radius:8px; border:1px solid #E2E8F0; font-size:12px;">
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <input type="checkbox" id="stock-slot-1500-chk" ${weekdaySlots.slot_1500?.enabled ? 'checked' : ''} onchange="saveStockShortsConfig()">
                                    <strong style="color:#0284C7;">3차 15:00</strong> (장 마감 결산·총괄)
                                </div>
                                <span style="font-size:11px; color:#64748B;">주제 1~6 롤링</span>
                            </label>
                        </div>
                    </div>

                    <!-- 주말/공휴일 2대 슬롯 -->
                    <div>
                        <div style="font-size:11.5px; font-weight:700; color:#2563EB; margin-bottom:6px;">🌿 주말·공휴일 슬롯 (1일 2회 특화 브랜딩)</div>
                        <div style="display:flex; flex-direction:column; gap:6px;">
                            <label style="display:flex; align-items:center; justify-content:space-between; background:#FFFFFF; padding:8px 10px; border-radius:8px; border:1px solid #E2E8F0; font-size:12px;">
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <input type="checkbox" id="stock-slot-1100-chk" ${weekendSlots.slot_1100?.enabled ? 'checked' : ''} onchange="saveStockShortsConfig()">
                                    <strong style="color:#2563EB;">1차 11:00</strong> (주말 브런치 계좌점검)
                                </div>
                                <span style="font-size:11px; font-weight:700; color:#D97706;">[주제 03 리스크가드]</span>
                            </label>
                            <label style="display:flex; align-items:center; justify-content:space-between; background:#FFFFFF; padding:8px 10px; border-radius:8px; border:1px solid #E2E8F0; font-size:12px;">
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <input type="checkbox" id="stock-slot-1800-chk" ${weekendSlots.slot_1800?.enabled ? 'checked' : ''} onchange="saveStockShortsConfig()">
                                    <strong style="color:#2563EB;">2차 18:00</strong> (월요일 개장 대비 총괄)
                                </div>
                                <span style="font-size:11px; font-weight:700; color:#D97706;">[주제 06 총괄소개]</span>
                            </label>
                        </div>
                    </div>
                </div>

                <!-- 2. 수동 즉시 생성 & 최근 히스토리 -->
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:14px; display:flex; flex-direction:column; justify-content:space-between;">
                    <div>
                        <div style="font-weight:700; font-size:13px; color:#1E293B; margin-bottom:10px;">⚡ 원클릭 즉시 생성 및 지정 렌더링</div>
                        <div style="display:flex; gap:8px; margin-bottom:12px;">
                            <select id="stock-manual-topic-select" style="flex:1; padding:8px 10px; border-radius:8px; border:1px solid #CBD5E1; font-size:12px; font-weight:600; background:#FFFFFF;">
                                <option value="auto">🔄 자동 순차 롤링 (다음: #${state.current_topic_index})</option>
                                <option value="1">[주제 01] 삼성전자 4대모달 퀀트수급 (30s)</option>
                                <option value="2">[주제 02] SK하이닉스 HBM독주 수급 (28s)</option>
                                <option value="3">[주제 03] AI 리스크 가드 (완주스크롤 30s)</option>
                                <option value="4">[주제 04] 10분 전광판 당일 1위 주도주 (24s)</option>
                                <option value="5">[주제 05] 코스피 시장스트레스 & 속보 (25s)</option>
                                <option value="6">[주제 06] 스톡마스터AI 총괄 소개 (35s)</option>
                            </select>
                            <button class="btn" id="btn-stock-shorts-run-now" onclick="triggerManualStockShortsRun()" style="background:linear-gradient(135deg, #F59E0B, #D97706); color:#FFFFFF; font-weight:800; font-size:12px; padding:8px 16px; border-radius:8px; border:none; cursor:pointer; white-space:nowrap; box-shadow:0 2px 8px rgba(245,158,11,0.3);">
                                🎬 즉시 생성 (Run Now)
                            </button>
                        </div>
                    </div>

                    <!-- 최근 생성 히스토리 -->
                    <div>
                        <div style="font-size:11.5px; font-weight:700; color:#475569; margin-bottom:6px;">📊 최근 완성 숏폼 목록 (최근 5건)</div>
                        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; overflow:hidden;">
                            <table style="width:100%; border-collapse:collapse; text-align:left;">
                                <thead>
                                    <tr style="background:#F1F5F9; font-size:11px; color:#64748B;">
                                        <th style="padding:6px;">시간</th>
                                        <th style="padding:6px;">주제</th>
                                        <th style="padding:6px;">길이</th>
                                        <th style="padding:6px;">용량</th>
                                        <th style="padding:6px;">상태</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${historyRows || '<tr><td colspan="5" style="text-align:center;padding:12px;font-size:11.5px;color:#94A3B8;">최근 생성된 숏폼이 없습니다.</td></tr>'}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    `;
}

async function triggerManualStockShortsRun() {
    if (isStockShortsGenerating) return;
    const select = document.getElementById("stock-manual-topic-select");
    const val = select ? select.value : "auto";
    const topicId = val === "auto" ? null : parseInt(val, 10);

    const btn = document.getElementById("btn-stock-shorts-run-now");
    const origHtml = btn ? btn.innerHTML : "";
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spin-icon" style="display:inline-block;animation:rotateSpin 0.8s linear infinite;">⏳</span> 렌더링 중...`;
    }
    isStockShortsGenerating = true;

    if (typeof appendLog === "function") {
        appendLog(`[StockMaster] 주제 #${topicId ? topicId : '자동 롤링'} 30초 퀀트 숏폼 백그라운드 렌더링 시작...`, "info");
    }
    if (typeof showToast === "function") {
        showToast("🎬 StockMaster 30초 숏폼 생성이 시작되었습니다!", "info");
    }

    try {
        const res = await fetch("/api/stock/shorts/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ topic_id: topicId })
        });
        const data = await res.json();
        if (data.success) {
            if (typeof showToast === "function") showToast("🚀 숏폼 제작 작업이 백그라운드에서 진행 중입니다!", "success");
        }
    } catch (e) {
        if (typeof showToast === "function") showToast(`오류 발생: ${e}`, "error");
    } finally {
        setTimeout(() => {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = origHtml;
            }
            isStockShortsGenerating = false;
            fetchStockShortsStatus();
        }, 3000);
    }
}

async function saveStockShortsConfig() {
    const s0930 = document.getElementById("stock-slot-0930-chk")?.checked ?? true;
    const s1200 = document.getElementById("stock-slot-1200-chk")?.checked ?? true;
    const s1500 = document.getElementById("stock-slot-1500-chk")?.checked ?? true;
    const s1100 = document.getElementById("stock-slot-1100-chk")?.checked ?? true;
    const s1800 = document.getElementById("stock-slot-1800-chk")?.checked ?? true;

    const payload = {
        weekday_slots: {
            slot_0930: { time: "09:30", enabled: s0930, label: "장 초반 수급·주도주" },
            slot_1200: { time: "12:00", enabled: s1200, label: "점심 시황·리스크" },
            slot_1500: { time: "15:00", enabled: s1500, label: "장 마감 결산·총괄" }
        },
        weekend_slots: {
            slot_1100: { time: "11:00", enabled: s1100, topic_id: 3, label: "주말 계좌 리스크 점검" },
            slot_1800: { time: "18:00", enabled: s1800, topic_id: 6, label: "월요일 개장 대비 총괄 소개" }
        }
    };

    try {
        const res = await fetch("/api/stock/shorts/config", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            stockShortsState = data;
            if (typeof showToast === "function") showToast("⚙️ 숏폼 스케줄 설정이 저장되었습니다!", "success");
        }
    } catch (e) {
        console.error("스케줄 저장 실패:", e);
    }
}

window.fetchStockShortsStatus = fetchStockShortsStatus;
window.renderStockShortsSchedulerPanel = renderStockShortsSchedulerPanel;
window.triggerManualStockShortsRun = triggerManualStockShortsRun;
window.saveStockShortsConfig = saveStockShortsConfig;

// DOM 로드 시 자동 초기화
document.addEventListener("DOMContentLoaded", () => {
    setTimeout(fetchStockShortsStatus, 300);
});
