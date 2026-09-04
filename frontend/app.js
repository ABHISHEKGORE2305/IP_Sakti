/* ============================================================
   Ayurveda & Indian Patent Law — RAG Assistant (frontend)
   Talks to the FastAPI backend in medical-rag/src/api.py
   ============================================================ */

const API_BASE = (() => {
  const origin = window.location.origin || "";
  if (origin.startsWith("http")) {
    // Served behind nginx / same origin as the API -> use relative calls.
    if (!origin.includes("://localhost") && !origin.includes("://127.0.0.1")) {
      return origin;
    }
  }
  return "http://127.0.0.1:8000";
})();

const sessionId = "session_" + Math.random().toString(36).slice(2, 9);

const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const sourcesEmpty = document.getElementById("sourcesEmpty");
const sourcesList = document.getElementById("sourcesList");
const srcCount = document.getElementById("srcCount");

/* ---------------- backend health ---------------- */

async function pollHealth() {
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
pollHealth();
setInterval(pollHealth, 15000);

/* ---------------- helpers ---------------- */

function escapeHtml(str) {
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function renderMarkdown(text) {
  try {
    return marked.parse(text);
  } catch {
    return escapeHtml(text).replace(/\n/g, "<br>");
  }
}

function scrollChat() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

/* ---------------- messages ---------------- */

function addUserMessage(text) {
  const el = document.createElement("div");
  el.className = "msg msg-user";
  el.textContent = text;
  chatMessages.appendChild(el);
  scrollChat();
}

function showLoader() {
  const stages = [
    "Embedding query with BAAI/bge-m3",
    "Searching dense vectors in Qdrant",
    "Running BM25 sparse retrieval",
    "Fusing candidates with reciprocal rank fusion",
    "Re-ranking with cross-encoder bge-reranker-v2-m3",
    "Applying statutory-reference boosts",
    "Assembling grounded context window",
    "Generating answer with citations",
  ];
  const STEP_MS = 3000; // 7 transitions -> ~21s before settling on the last stage

  const el = document.createElement("div");
  el.className = "msg-loader";
  el.id = "activeLoader";
  el.innerHTML = `<span class="spinner"></span><span class="loader-stage">${stages[0]}<span class="loader-dots"></span></span>`;
  chatMessages.appendChild(el);
  scrollChat();

  const stageEl = el.querySelector(".loader-stage");
  let i = 0;
  const timer = setInterval(() => {
    i = Math.min(i + 1, stages.length - 1);
    if (stageEl) stageEl.innerHTML = `${stages[i]}<span class="loader-dots"></span>`;
    if (i === stages.length - 1) clearInterval(timer);
  }, STEP_MS);

  return {
    remove: () => {
      clearInterval(timer);
      el.remove();
    },
  };
}

let responseSeq = 0;
const responses = {};        // respId -> { retrieved: [...] }
let selectedRespId = null;

function addBotMessage(answer, retrieved, errorNote) {
  const respId = "resp_" + ++responseSeq;
  responses[respId] = { retrieved: retrieved || [] };

  const el = document.createElement("div");
  el.className = "msg msg-bot";
  el.dataset.respId = respId;

  let html = `<div class="msg-body">${renderMarkdown(answer)}</div>`;

  if (retrieved && retrieved.length) {
    html += `<div class="cite-row">`;
    retrieved.forEach((r, i) => {
      const label = r.legal_reference || r.document || `Source ${i + 1}`;
      html += `<span class="cite-chip" data-idx="${i}">${escapeHtml(String(label).slice(0, 32))}</span>`;
    });
    html += `</div>`;
    html += `<div class="cite-hint">${retrieved.length} source${retrieved.length === 1 ? "" : "s"} — click this answer to view them all on the right.</div>`;
    el.classList.add("clickable");
  } else if (errorNote) {
    html += `<div class="cite-hint">${escapeHtml(errorNote)}</div>`;
  }

  el.innerHTML = html;

  el.addEventListener("click", (e) => {
    const chip = e.target.closest(".cite-chip");
    selectResponse(respId, chip ? Number(chip.dataset.idx) : null);
  });

  chatMessages.appendChild(el);
  scrollChat();
  return respId;
}

/* ---------------- right sidebar ---------------- */

function selectResponse(respId, highlightIdx) {
  const store = responses[respId];
  if (!store) return;
  selectedRespId = respId;

  document.querySelectorAll(".msg-bot").forEach((b) => {
    b.classList.toggle("selected", b.dataset.respId === respId);
  });

  renderSources(store.retrieved, highlightIdx);
}

function renderSources(retrieved, highlightIdx) {
  if (!retrieved || !retrieved.length) {
    sourcesEmpty.classList.remove("hidden");
    sourcesEmpty.textContent = "No statutory sources were retrieved for this answer.";
    sourcesList.classList.add("hidden");
    srcCount.textContent = "";
    return;
  }

  sourcesEmpty.classList.add("hidden");
  sourcesList.classList.remove("hidden");
  srcCount.textContent = retrieved.length;

  sourcesList.innerHTML = retrieved
    .map((r, i) => {
      const rank = r.rank || i + 1;
      const ref = r.legal_reference || "";
      const page = r.page != null ? `p. ${r.page}` : "";
      const score = typeof r.reranker_score === "number"
        ? `${r.reranker_score >= 0 ? "+" : ""}${r.reranker_score.toFixed(2)}`
        : "";
      const snippet = r.snippet || r.text || "";
      return `
        <div class="source-card" data-idx="${i}">
          <div class="source-card-head">
            <span class="source-rank">#${rank}</span>
            <span class="source-doc">${escapeHtml(r.document || "Source")}</span>
          </div>
          <div class="source-meta">
            ${ref ? `<span class="source-badge">${escapeHtml(ref)}</span>` : ""}
            ${page ? `<span class="source-badge muted">${page}</span>` : ""}
            ${score ? `<span class="source-badge muted">score ${score}</span>` : ""}
          </div>
          ${snippet ? `<div class="source-snippet">${escapeHtml(snippet)}</div><div class="source-toggle">Show more</div>` : ""}
        </div>`;
    })
    .join("");

  sourcesList.querySelectorAll(".source-card").forEach((card) => {
    card.addEventListener("click", () => {
      card.classList.toggle("expanded");
      const t = card.querySelector(".source-toggle");
      if (t) t.textContent = card.classList.contains("expanded") ? "Show less" : "Show more";
    });
  });

  if (highlightIdx != null) {
    const card = sourcesList.querySelector(`.source-card[data-idx="${highlightIdx}"]`);
    if (card) {
      sourcesList.querySelectorAll(".source-card").forEach((c) => c.classList.remove("highlight"));
      card.classList.add("highlight");
      card.scrollIntoView({ block: "nearest", behavior: "smooth" });
    }
  }
}

/* ---------------- submit ---------------- */

function sendQuickPrompt(text) {
  chatInput.value = text;
  chatForm.requestSubmit();
}

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;

  addUserMessage(text);
  chatInput.value = "";
  sendBtn.disabled = true;

  const loader = showLoader();

  try {
    const res = await fetch(`${API_BASE}/api/chat/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: text, session_id: sessionId }),
    });
    const data = await res.json();
    loader.remove();

    const retrieved = data.retrieved && data.retrieved.length ? data.retrieved : (data.sources || []);
    const respId = addBotMessage(data.answer || "No answer was returned.", retrieved, data.error || "");

    // Auto-show this answer's sources; user can click older answers to switch.
    selectResponse(respId, null);
  } catch (err) {
    loader.remove();
    addBotMessage(
      "Could not reach the backend. Start it with `PYTHONPATH=src python -m uvicorn api:app --port 8000` and try again.",
      [],
      "network error"
    );
  } finally {
    sendBtn.disabled = false;
    chatInput.focus();
  }
});

/* ---------------- export ---------------- */

document.getElementById("exportBtn").addEventListener("click", () => {
  const bubbles = [...chatMessages.children].filter(
    (n) => n.classList.contains("msg-user") || n.classList.contains("msg-bot")
  );
  if (bubbles.length <= 1) {
    alert("Ask at least one question first.");
    return;
  }

  const lines = [
    "# Ayurveda & Indian Patent Law — conversation",
    "",
    `_Exported ${new Date().toISOString()}_`,
    "",
    "> Informational only, grounded in retrieved statutory sources. Not legal advice.",
    "",
  ];

  bubbles.forEach((node) => {
    if (node.classList.contains("msg-user")) {
      lines.push(`## Q: ${node.textContent.trim()}`, "");
      return;
    }
    const body = node.querySelector(".msg-body");
    if (body) lines.push(body.innerText.trim(), "");
    const respId = node.dataset.respId;
    const retrieved = respId && responses[respId] ? responses[respId].retrieved : [];
    if (retrieved.length) {
      lines.push("**Sources:**");
      retrieved.forEach((r) => {
        const bits = [r.document, r.legal_reference, r.page != null ? `p. ${r.page}` : ""].filter(Boolean);
        lines.push(`- ${bits.join(", ")}`);
      });
      lines.push("");
    }
  });

  const blob = new Blob([lines.join("\n")], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `patent-rag-chat-${Date.now()}.md`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
});
