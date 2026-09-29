// Step 4 — Dynamic AI Analysis Feed.
// The backend call is a single request/response (no SSE/websocket infra),
// so the stage list below is a UI-only progression timed against typical
// latency, replaced the instant the real result comes back — it never
// fabricates the answer itself, only the "what's happening" narration.
//
// jurisdiction="Both" (winning_features.md item 2) returns
// {india: <result>, international: <result>} instead of a flat result —
// rendered as two side-by-side panels below, never merged into one.

import { AlertTriangle, ChevronDown, ChevronLeft, ChevronRight, RotateCcw } from 'lucide-react';
import { useEffect, useState } from 'react';
import { ANALYSIS_STAGES } from '../../../lib/wizardConfig';
import Markdown from '../Markdown';

function ConfidenceBadge({ band }) {
  if (!band) return null;
  return <span className={`step__badge step__badge--${band}`}>{band} confidence</span>;
}

// winning_features.md item 11 — the REAL per-node agent step trace
// (agents/state.py's `trace`, accumulated by every node in agents/graph.py),
// not the simulated progress bar above. Collapsed by default since it's
// a transparency/debugging aid, not primary reading content.
function StepTracePanel({ trace }) {
  const [open, setOpen] = useState(false);
  if (!trace || trace.length === 0) return null;

  return (
    <div className="step-trace">
      <button className="step-trace__toggle" onClick={() => setOpen((o) => !o)}>
        <ChevronDown size={13} style={{ transform: open ? 'rotate(0deg)' : 'rotate(-90deg)', transition: 'transform 0.15s' }} />
        Agent step trace ({trace.length} steps) — the real backend record
      </button>
      {open && (
        <ol className="step-trace__list">
          {trace.map((t, i) => (
            <li key={i} className="step-trace__item">
              <span className="step-trace__node">{t.node}</span>
              <span className="step-trace__summary">{t.summary}</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

function AnalysisPanel({ label, result }) {
  return (
    <div className="analysis-panel">
      {label && <div className="analysis-panel__label">{label}</div>}
      <div className="analysis-meta">
        <ConfidenceBadge band={result.confidence?.band} />
        {result.selected_agents?.length > 0 && (
          <span className="step__badge" style={{ background: 'var(--app-bg-elevated)', color: 'var(--app-text-secondary)' }}>
            {result.selected_agents.join(', ')}
          </span>
        )}
        {result.citations && (
          <span className="step__badge" style={{ background: 'var(--app-bg-elevated)', color: 'var(--app-text-secondary)' }}>
            {result.citations.verified_citations}/{result.citations.total_citations} citations verified
          </span>
        )}
      </div>
      <div className="analysis-answer">
        {result.final_answer ? <Markdown>{result.final_answer}</Markdown> : '—'}
      </div>
      <StepTracePanel trace={result.trace} />
    </div>
  );
}

export default function StepAnalysis({ loading, result, error, onBack, onNext, onRetry }) {
  const [activeStage, setActiveStage] = useState(0);

  useEffect(() => {
    if (!loading) return undefined;
    // Reset the stage progression every time a new run starts.
    setActiveStage(0);
    const interval = setInterval(() => {
      setActiveStage((s) => (s < ANALYSIS_STAGES.length - 1 ? s + 1 : s));
    }, 1100);
    return () => clearInterval(interval);
  }, [loading]);

  const isBoth = Boolean(result?.india || result?.international);

  return (
    <div>
      <h2 className="step__heading">Dynamic AI Analysis</h2>
      <p className="step__subheading">
        {loading
          ? 'Running the multi-agent pipeline against the legal corpus…'
          : 'Analysis complete.'}
      </p>

      {(loading || !result) && (
        <div className="analysis-stages">
          {ANALYSIS_STAGES.map((label, i) => (
            <div
              key={label}
              className={`analysis-stage${
                i < activeStage ? ' analysis-stage--done' : i === activeStage ? ' analysis-stage--active' : ''
              }`}
            >
              <span className="analysis-stage__dot" />
              {label}
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="step__error">
          <AlertTriangle size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
          {error}
        </div>
      )}

      {result && !loading && isBoth && (
        <div className="analysis-both-grid">
          <AnalysisPanel label="🇮🇳 India" result={result.india} />
          <AnalysisPanel label="🌍 International" result={result.international} />
        </div>
      )}

      {result && !loading && !isBoth && <AnalysisPanel result={result} />}

      <div className="step__actions">
        <button className="step__btn step__btn--ghost" onClick={onBack} disabled={loading}>
          <ChevronLeft size={16} /> Back
        </button>
        <div style={{ display: 'flex', gap: 10 }}>
          {!loading && (error || result?.error) && (
            <button className="step__btn step__btn--ghost" onClick={onRetry}>
              <RotateCcw size={14} /> Retry
            </button>
          )}
          <button className="step__btn step__btn--primary" onClick={onNext} disabled={loading || !result}>
            View Sources <ChevronRight size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
