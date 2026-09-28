// Step 5 — Interactive Source & Citation Inspector.
// Full-text snippets, reranker/authority score badges, and per-citation
// verified/unverified status from agents.citation_agent.verify_citations.

import { CheckCircle2, ChevronLeft, ChevronRight, XCircle } from 'lucide-react';

export default function StepSources({ result, onBack, onNext }) {
  const sources = result?.sources || [];
  const citations = result?.citations;

  return (
    <div>
      <h2 className="step__heading">Sources & Citation Inspector</h2>
      <p className="step__subheading">
        Every source actually retrieved for this answer, with its authority weight and the
        zero-hallucination citation check.
      </p>

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
          </div>
        ))}
      </div>

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
