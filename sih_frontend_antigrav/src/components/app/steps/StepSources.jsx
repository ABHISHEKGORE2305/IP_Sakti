// Step 5 — Interactive Source & Citation Inspector.
// Full-text snippets, reranker/authority score badges, and per-citation
// verified/unverified status from agents.citation_agent.verify_citations.
//
// jurisdiction="Both" (winning_features.md item 2) returns
// {india: <result>, international: <result>} — rendered as two
// side-by-side source lists below, never merged.

import { AlertTriangle, CheckCircle2, ChevronLeft, ChevronRight, ExternalLink, GitBranch, XCircle } from 'lucide-react';
import { useEffect, useState } from 'react';
import { fetchKnowledgeGraph, fetchReferences } from '../../../lib/api';
import { BIOLOGICAL_RESOURCE_SUGGESTIONS, INGREDIENT_SUGGESTIONS } from '../../../lib/suggestions';
import SuggestionChips from '../SuggestionChips';
import IPRoutePlanner from './IPRoutePlanner';
import KnowledgeGraphExplorer from './KnowledgeGraphExplorer';

// left_to_do.md item 16 — deep links to free official portals (IP India,
// WIPO, GI Registry, TKDL, AYUSH, FSSAI, NBA...), served from
// GET /api/references (src/references.py). Loaded lazily so a slow/failed
// fetch never blocks the citation inspector above it.
function OfficialResources() {
  const [categories, setCategories] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    fetchReferences()
      .then((data) => {
        if (!cancelled) setCategories(data.categories || []);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error || (categories && categories.length === 0)) return null;

  return (
    <div className="step__field" style={{ marginTop: 24 }}>
      <label className="step__label">Official resources</label>
      <p className="step__subheading" style={{ marginTop: -4 }}>
        Free government/WIPO portals for record lookup — patent, trademark, and GI status are not
        tracked in this corpus, so verify directly at the source.
      </p>
      {!categories ? (
        <p className="step__subheading">Loading…</p>
      ) : (
        <div className="reference-grid">
          {categories.map((cat) => (
            <div className="reference-grid__category" key={cat.category}>
              <div className="reference-grid__title">{cat.category}</div>
              {cat.links.map((link) => (
                <a
                  key={link.url}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="reference-grid__link"
                  title={link.description}
                >
                  <ExternalLink size={12} /> {link.title}
                </a>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// left_to_do.md item 11 / winning_features.md item 10 — relational
// knowledge graph, rendered via KnowledgeGraphExplorer's SVG layered
// layout. Built from POST /api/knowledge-graph (engines/knowledge_graph.py),
// which derives every hop from the classification/ABS facts the wizard
// already collected — only the ingredient/biological resource name is
// free text, since no such reference dataset exists yet.
function KnowledgeGraphPanel({ jurisdiction, classificationInputs, absInputs }) {
  const [ingredient, setIngredient] = useState('');
  const [biologicalResource, setBiologicalResource] = useState('');
  const [graph, setGraph] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const hasFacts = classificationInputs || absInputs || ingredient.trim();

  const build = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchKnowledgeGraph({
        jurisdiction,
        ingredient: ingredient.trim() || undefined,
        biologicalResource: biologicalResource.trim() || undefined,
        classificationInputs: classificationInputs || undefined,
        absInputs: absInputs || undefined,
      });
      setGraph(data);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="step__field" style={{ marginTop: 24 }}>
      <label className="step__label">Knowledge graph explorer</label>
      <p className="step__subheading" style={{ marginTop: -4 }}>
        Multi-hop view connecting this product to its regulation, IP options, and ABS obligations.
        {classificationInputs || absInputs
          ? ' Pre-filled from your classification and ABS answers.'
          : ' Add an ingredient name to build a minimal graph, or complete Step 2/3 first for the full picture.'}
      </p>
      <div className="action-plan__translate-row">
        <input
          type="text"
          className="step__input"
          placeholder="Ingredient (e.g. Withania somnifera)"
          value={ingredient}
          onChange={(e) => setIngredient(e.target.value)}
          style={{ flex: '1 1 220px', minWidth: 180 }}
        />
        <input
          type="text"
          className="step__input"
          placeholder="Biological resource / source (optional)"
          value={biologicalResource}
          onChange={(e) => setBiologicalResource(e.target.value)}
          style={{ flex: '1 1 220px', minWidth: 180 }}
        />
        <button className="step__btn step__btn--ghost" onClick={build} disabled={loading || !hasFacts}>
          <GitBranch size={14} /> {loading ? 'Building…' : 'Build graph'}
        </button>
      </div>
      <SuggestionChips
        items={INGREDIENT_SUGGESTIONS}
        value={ingredient}
        onSelect={setIngredient}
        label="Common ingredients"
      />
      <SuggestionChips
        items={BIOLOGICAL_RESOURCE_SUGGESTIONS}
        value={biologicalResource}
        onSelect={setBiologicalResource}
        label="Common sources"
      />
      {error && <div className="step__error">{error}</div>}
      <KnowledgeGraphExplorer graph={graph} />
    </div>
  );
}

// winning_features.md item 8 — TKDL / Prior-Art Pointer's "Misappropriation
// risk" flag, surfaced from engines.tk_engine's tkdl_mitigation/
// misappropriation_risk (only present when tk_inputs drove a deterministic
// analysis — absent, not fabricated, for free-text/RAG answers).
function TkdlRiskBadge({ engineResults }) {
  const analysis = engineResults?.tk_patentability;
  if (!analysis) return null;

  const risk = analysis.misappropriation_risk;
  const tkdl = analysis.tkdl_mitigation;
  const levelColor = { high: 'var(--risk-high)', moderate: 'var(--risk-medium)', low: 'var(--risk-low)' };

  return (
    <div className="step__field" style={{ marginTop: 24 }}>
      <label className="step__label">TKDL / Prior-Art Pointer</label>
      {risk && (
        <div className="citation-summary" style={{ borderColor: levelColor[risk.level] }}>
          <AlertTriangle size={16} color={levelColor[risk.level]} />
          <span>
            <strong style={{ color: levelColor[risk.level] }}>Misappropriation risk: {risk.level}</strong>
            {' — '}
            {risk.finding}
          </span>
        </div>
      )}
      {tkdl && (
        <p className="step__subheading" style={{ marginTop: 8 }}>
          {tkdl.finding} {tkdl.recommendation}
        </p>
      )}
    </div>
  );
}

function SourcesPanel({ label, result }) {
  const sources = result?.sources || [];
  const citations = result?.citations;

  return (
    <div>
      {label && <div className="analysis-panel__label">{label}</div>}
      {citations && (
        <div className="citation-summary">
          {citations.verified_citations === citations.total_citations ? (
            <CheckCircle2 size={16} color="var(--risk-low)" />
          ) : (
            <XCircle size={16} color="var(--risk-high)" />
          )}
          {citations.total_citations === 0
            ? 'This answer made no inline citations.'
            : `${citations.verified_citations} of ${citations.total_citations} inline citations verified against the retrieved sources.`}
        </div>
      )}

      {sources.length === 0 && (
        <p className="step__subheading">No sources were retrieved for this query.</p>
      )}

      <div className="source-list">
        {sources.map((s, i) => (
          <div className="source-card" key={s.chunk_id || i}>
            <div className="source-card__header">
              <div>
                <div className="source-card__doc">{s.document || 'Unknown source'}</div>
                {(s.legal_reference || s.page != null) && (
                  <div className="source-card__ref">
                    {s.legal_reference}
                    {s.page != null ? ` · p.${s.page}` : ''}
                  </div>
                )}
              </div>
              <div className="source-card__scores">
                {s.authority_weight != null && (
                  <span className="source-card__score">authority {s.authority_weight.toFixed(2)}</span>
                )}
                {s.reranker_score != null && (
                  <span className="source-card__score">score {s.reranker_score.toFixed(2)}</span>
                )}
              </div>
            </div>
            {s.snippet && <div className="source-card__snippet">{s.snippet}</div>}
            {s.freshness_note && <div className="source-card__freshness">⚠ {s.freshness_note}</div>}
          </div>
        ))}
      </div>

      <TkdlRiskBadge engineResults={result?.engine_results} />
    </div>
  );
}

export default function StepSources({
  result,
  onBack,
  onNext,
  jurisdiction,
  classificationInputs,
  classificationResult,
  absInputs,
}) {
  const isBoth = Boolean(result?.india || result?.international);
  const ipRegimes = classificationResult?.engine_results?.classifier?.ip_regimes;

  return (
    <div>
      <h2 className="step__heading">Sources & Citation Inspector</h2>
      <p className="step__subheading">
        Every source actually retrieved for this answer, with its authority weight and the
        zero-hallucination citation check.
      </p>

      {isBoth ? (
        <div className="analysis-both-grid">
          <SourcesPanel label="🇮🇳 India" result={result.india} />
          <SourcesPanel label="🌍 International" result={result.international} />
        </div>
      ) : (
        <SourcesPanel result={result} />
      )}

      <IPRoutePlanner ipRegimes={ipRegimes} isRegionLinked={false} />

      <KnowledgeGraphPanel
        jurisdiction={jurisdiction}
        classificationInputs={classificationInputs}
        absInputs={absInputs}
      />

      <OfficialResources />

      <div className="step__actions">
        <button className="step__btn step__btn--ghost" onClick={onBack}>
          <ChevronLeft size={16} /> Back
        </button>
        <button className="step__btn step__btn--primary" onClick={onNext}>
          Continue to Action Plan <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
}
