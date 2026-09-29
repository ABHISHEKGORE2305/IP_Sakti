// winning_features.md item 9 — "ask a question under the old law vs the
// current law and show different, correctly cited answers." Each
// version's answer is retrieval-scoped (POST /api/law-version-query ->
// retriever.combined_query_filter's document_id_filter), not just
// prompt-suggested — so the two answers genuinely can't cross-cite.

import { Clock } from 'lucide-react';
import { useEffect, useState } from 'react';
import { getLawFamilies, queryLawVersion } from '../../../lib/api';
import { LAW_QUESTION_SUGGESTIONS } from '../../../lib/suggestions';
import SuggestionChips from '../SuggestionChips';

function VersionAnswer({ version, query, trigger }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!trigger) return;
    setLoading(true);
    setError(null);
    queryLawVersion(query, version.document_id)
      .then(setResult)
      .catch((err) => setError(String(err)))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [trigger]);

  return (
    <div className="analysis-panel">
      <div className="analysis-panel__label">
        {version.label} ({version.year})
      </div>
      {loading && <p className="step__subheading">Querying…</p>}
      {error && <div className="step__error">{error}</div>}
      {result && (
        <>
          <div className="analysis-answer">{result.answer || '—'}</div>
          {result.sources?.length > 0 && (
            <p className="step__subheading" style={{ marginTop: 8, marginBottom: 0 }}>
              {result.sources.length} source(s), all from {version.label}.
            </p>
          )}
        </>
      )}
    </div>
  );
}

export default function LawVersionTimeline() {
  const [families, setFamilies] = useState(null);
  const [familyId, setFamilyId] = useState(null);
  const [query, setQuery] = useState('');
  const [trigger, setTrigger] = useState(0);

  useEffect(() => {
    getLawFamilies().then((data) => {
      setFamilies(data.families || []);
      if (data.families?.length) setFamilyId(data.families[0].family_id);
    });
  }, []);

  const family = families?.find((f) => f.family_id === familyId);

  return (
    <div className="app-panel">
      <h2 className="step__heading">
        <Clock size={18} style={{ verticalAlign: 'middle', marginRight: 8 }} />
        Law Version Timeline
      </h2>
      <p className="step__subheading">
        Ask the same question under two versions of a law, each answer retrieval-scoped to
        exactly that version — not just a prompt instruction.
      </p>

      {families && (
        <div className="step__field">
          <label className="step__label">Law family</label>
          <select className="step__select" value={familyId || ''} onChange={(e) => setFamilyId(e.target.value)}>
            {families.map((f) => (
              <option key={f.family_id} value={f.family_id}>
                {f.label}
              </option>
            ))}
          </select>
          {family?.note && <p className="step__subheading" style={{ marginTop: 8 }}>{family.note}</p>}
        </div>
      )}

      <div className="step__field">
        <label className="step__label">Question</label>
        <div className="action-plan__translate-row">
          <input
            type="text"
            className="step__input"
            placeholder="e.g. What is the fee for filing a patent application?"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{ flex: '1 1 320px' }}
          />
          <button
            className="step__btn step__btn--primary"
            onClick={() => setTrigger((t) => t + 1)}
            disabled={!query.trim() || !family}
          >
            Compare versions
          </button>
        </div>
        <SuggestionChips items={LAW_QUESTION_SUGGESTIONS} value={query} onSelect={setQuery} />
      </div>

      {family && trigger > 0 && (
        <div className="analysis-both-grid">
          {family.versions.map((v) => (
            <VersionAnswer key={v.document_id} version={v} query={query} trigger={trigger} />
          ))}
        </div>
      )}
    </div>
  );
}
