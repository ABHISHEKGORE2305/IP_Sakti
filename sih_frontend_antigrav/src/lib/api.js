// src/lib/api.js
// Thin fetch wrapper around the FastAPI backend (src/api.py).
// Same origin-detection pattern as the legacy frontend/app.js: same-origin
// in production (behind nginx), localhost:8000 fallback for local dev.

const API_BASE = (() => {
  const origin = window.location.origin || '';
  if (origin.startsWith('http')) {
    if (!origin.includes('://localhost') && !origin.includes('://127.0.0.1')) {
      return origin;
    }
  }
  return 'http://127.0.0.1:8000';
})();

// No-login session identity (backend: src/db.py, api.py's _session_id) —
// a UUID generated once and persisted in localStorage, sent as
// X-Session-Id on every request so the audit log / consent / privacy
// endpoints (winning_features.md items 15-17) have something to key on.
const SESSION_ID_KEY = 'ipsakti_session_id';

export function getSessionId() {
  let id = localStorage.getItem(SESSION_ID_KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(SESSION_ID_KEY, id);
  }
  return id;
}

function withSessionHeaders(extra = {}) {
  return { 'X-Session-Id': getSessionId(), ...extra };
}

async function postJson(path, body, { timeoutMs = 60000 } = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: withSessionHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    if (!res.ok) {
      throw new Error(`${path} responded ${res.status}`);
    }

    return await res.json();
  } finally {
    clearTimeout(timeout);
  }
}

async function getJson(path, { timeoutMs = 15000 } = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: withSessionHeaders(),
    signal: AbortSignal.timeout(timeoutMs),
  });
  if (!res.ok) throw new Error(`${path} responded ${res.status}`);
  return res.json();
}

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(4000) });
    if (!res.ok) return { status: 'unreachable' };
    return await res.json();
  } catch {
    return { status: 'unreachable' };
  }
}

/**
 * Run the multi-agent pipeline (agents.graph.run via POST /api/agent).
 *
 * @param {object} payload
 * @param {string} payload.query
 * @param {'India'|'International'|'Both'} [payload.jurisdiction]
 * @param {string} [payload.persona] - "practitioner"|"researcher"|"startup_msme"|"cultivator"
 * @param {string} [payload.forcedAgent] - explicit specialist (issue picker)
 * @param {object} [payload.classificationInputs] - engines.classifier inputs
 * @param {'US'|'EU'|'UK'} [payload.targetMarket]
 * @param {object} [payload.marketInputs] - engines.intl_engine.advise_market inputs
 * @param {object} [payload.gratkInputs]
 * @param {object} [payload.tkInputs] - engines.tk_engine.analyze_tk_patentability inputs
 * @param {object} [payload.iprInputs] - {regime: ...} for engines.ipr_router.advise_regime
 * @param {object} [payload.absInputs] - engines.abs_engine.analyze_abs_compliance inputs
 * @param {object} [payload.regInputs] - engines.reg_engine.analyze_regulatory_pathway inputs
 */
export async function runAgent({
  query,
  jurisdiction = 'India',
  persona,
  forcedAgent,
  classificationInputs,
  targetMarket,
  marketInputs,
  gratkInputs,
  tkInputs,
  iprInputs,
  absInputs,
  regInputs,
} = {}) {
  return postJson('/api/agent', {
    query: query || '',
    jurisdiction,
    persona: persona || null,
    forced_agent: forcedAgent || null,
    classification_inputs: classificationInputs || null,
    target_market: targetMarket || null,
    market_inputs: marketInputs || null,
    gratk_inputs: gratkInputs || null,
    tk_inputs: tkInputs || null,
    ipr_inputs: iprInputs || null,
    abs_inputs: absInputs || null,
    reg_inputs: regInputs || null,
  });
}

/**
 * ChatGPT-style multi-turn chat (POST /api/chat/). Stateless on the
 * backend per-request — `history` (oldest first, {role, content} pairs)
 * is resent on every call so follow-ups have context.
 *
 * @param {object} payload
 * @param {string} payload.query
 * @param {'India'|'International'|'Both'} [payload.jurisdiction]
 * @param {{role: 'user'|'assistant', content: string}[]} [payload.history]
 */
export async function sendChatMessage({ query, jurisdiction = 'India', history = [] } = {}) {
  return postJson(
    '/api/chat/',
    { query: query || '', jurisdiction, history },
    { timeoutMs: 90000 }
  );
}

export async function translateText(text, targetLanguage) {
  return postJson(
    '/api/translate',
    { text, target_language: targetLanguage },
    { timeoutMs: 30000 }
  );
}

export async function escalateCase({ caseBriefMarkdown, query, replyTo }) {
  return postJson(
    '/api/escalate',
    { case_brief_markdown: caseBriefMarkdown, query: query || null, reply_to: replyTo || null },
    { timeoutMs: 20000 }
  );
}

export async function fetchKnowledgeGraph({
  jurisdiction = 'India',
  ingredient,
  biologicalResource,
  classificationInputs,
  tkInputs,
  absInputs,
} = {}) {
  return postJson(
    '/api/knowledge-graph',
    {
      jurisdiction,
      ingredient: ingredient || null,
      biological_resource: biologicalResource || null,
      classification_inputs: classificationInputs || null,
      tk_inputs: tkInputs || null,
      abs_inputs: absInputs || null,
    },
    { timeoutMs: 15000 }
  );
}

export async function fetchReferences() {
  return getJson('/api/references', { timeoutMs: 8000 });
}

/**
 * IP Route Planner (winning_features.md item 6).
 * @param {object} params
 * @param {object} params.ipRegimes - the `ip_regimes` field from a classification result
 * @param {string} [params.tkRisk] - overall_risk from an analyze_tk_patentability() result
 * @param {boolean} [params.isRegionLinked]
 */
export async function fetchIpRoutePlan({ ipRegimes, tkRisk, isRegionLinked = false } = {}) {
  return postJson('/api/ip-route-plan', {
    ip_regimes: ipRegimes || {},
    tk_risk: tkRisk || null,
    is_region_linked: isRegionLinked,
  });
}

// ---- Consent, audit log, privacy (winning_features.md items 15-17) ----

export async function setConsent(consentType, granted) {
  return postJson('/api/consent', { consent_type: consentType, granted });
}

export async function getConsent() {
  return getJson('/api/consent');
}

export async function getAuditLog(limit = 200) {
  return getJson(`/api/audit-log?limit=${limit}`);
}

export async function getPrivacySummary() {
  return getJson('/api/privacy/summary');
}

export async function deleteMyData() {
  return postJson('/api/privacy/delete', {});
}

// ---- Corpus admin panel (winning_features.md item 20) ----

export async function getAdminCorpus() {
  return getJson('/api/admin/corpus', { timeoutMs: 15000 });
}

export async function uploadCorpusDocument(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/api/admin/corpus/upload`, {
    method: 'POST',
    headers: withSessionHeaders(),
    body: formData,
    signal: AbortSignal.timeout(60000),
  });
  if (!res.ok) throw new Error(`upload responded ${res.status}`);
  return res.json();
}

// ---- Evaluation dashboard (winning_features.md item 19) ----

export async function getEvalResults() {
  return getJson('/api/eval-results');
}

// ---- Law Version Timeline (winning_features.md item 9) ----

export async function getLawFamilies() {
  return getJson('/api/law-versions');
}

export async function queryLawVersion(query, documentId) {
  return postJson('/api/law-version-query', { query, document_id: documentId }, { timeoutMs: 45000 });
}

// ---- Bhashini (winning_features.md item 13) ----

export async function getBhashiniStatus() {
  return getJson('/api/bhashini/status');
}

export { API_BASE };
