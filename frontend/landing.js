/* Landing page — health badge + a small live demo that calls /api/chat/. */

const API_BASE = (() => {
  const origin = window.location.origin || "";
  if (origin.startsWith("http") && !origin.includes("://localhost") && !origin.includes("://127.0.0.1")) {
    return origin;
  }
  return "http://127.0.0.1:8000";
})();

async function checkHealth() {
  const dot = document.getElementById("statusDot");
  const label = document.getElementById("statusLabel");
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(4000) });
    const data = await res.json();
    if (data.status === "ok") {
      dot.className = "status-dot ok";
      label.textContent = "Backend ready";
    } else {
      dot.className = "status-dot wait";
      label.textContent = "Backend starting…";
    }
  } catch {
    dot.className = "status-dot bad";
    label.textContent = "Backend offline";
  }
}
checkHealth();
setInterval(checkHealth, 20000);

function escapeHtml(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function renderMd(text) {
  try {
    return marked.parse(text);
  } catch {
    return "<p>" + escapeHtml(text).replace(/\n/g, "<br>") + "</p>";
  }
}

async function landingAsk(prefill) {
  const input = document.getElementById("demoInput");
  const btn = document.getElementById("demoSend");
  const out = document.getElementById("demoOutput");

  const query = prefill || (input ? input.value.trim() : "");
  if (!query) return;
  if (input) input.value = "";

  btn.disabled = true;
  out.innerHTML = `<div class="demo-loading"><span class="spinner"></span><span>Searching statutory sources…</span></div>`;

  try {
    const res = await fetch(`${API_BASE}/api/chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, session_id: "landing_demo" }),
    });
    const data = await res.json();

    const retrieved = (data.retrieved && data.retrieved.length ? data.retrieved : data.sources) || [];
    let html = `<div class="demo-answer">${renderMd(data.answer || "No answer was returned.")}</div>`;
    if (retrieved.length) {
      html += `<div class="demo-sources">`;
      retrieved.slice(0, 6).forEach((r) => {
        const label = r.legal_reference || r.section || r.document || "source";
        html += `<span class="demo-source-chip">${escapeHtml(String(label).slice(0, 40))}</span>`;
      });
      html += `</div>`;
    }
    if (data.error) {
      html += `<p class="demo-error">Note: ${escapeHtml(data.error)}</p>`;
    }
    out.innerHTML = html;
  } catch {
    out.innerHTML = `<p class="demo-error">Could not reach the backend. Start it with <code>PYTHONPATH=src python -m uvicorn api:app --port 8000</code>.</p>`;
  } finally {
    btn.disabled = false;
  }
}
window.landingAsk = landingAsk;

document.getElementById("demoInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter") landingAsk();
});
