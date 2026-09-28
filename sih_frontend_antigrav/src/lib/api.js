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

async function postJson(path, body, { timeoutMs = 60000 } = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
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
 * @param {'India'|'International'} [payload.jurisdiction]
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

export async function translateText(text, targetLanguage) {
  return postJson(
    '/api/translate',
    { text, target_language: targetLanguage },
    { timeoutMs: 30000 }
  );
}

export { API_BASE };
