// Step 4 — Dynamic AI Analysis Feed.
// The backend call is a single request/response (no SSE/websocket infra),
// so the stage list below is a UI-only progression timed against typical
// latency, replaced the instant the real result comes back — it never
// fabricates the answer itself, only the "what's happening" narration.

import { AlertTriangle, ChevronLeft, ChevronRight, RotateCcw } from 'lucide-react';
import { useEffect, useState } from 'react';
import { ANALYSIS_STAGES } from '../../../lib/wizardConfig';

function ConfidenceBadge({ band }) {
  if (!band) return null;
  return <span className={`step__badge step__badge--${band}`}>{band} confidence</span>;
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

      {result && !loading && (
        <>
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
          <div className="analysis-answer">{result.final_answer || '—'}</div>
        </>
      )}

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
