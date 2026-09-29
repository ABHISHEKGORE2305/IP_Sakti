// winning_features.md item 19 — evaluation dashboard, live in the app.
// Reads GET /api/eval-results (written by
// `PYTHONPATH=src python3 src/eval_benchmark.py --out-json ...`), the
// actual 50-question golden benchmark — not fabricated numbers.

import { BarChart3 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { getEvalResults } from '../../../lib/api';

function bandColor(ratio) {
  if (ratio >= 0.9) return 'var(--risk-low)';
  if (ratio >= 0.7) return 'var(--risk-medium)';
  return 'var(--risk-high)';
}

export default function EvalDashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getEvalResults()
      .then(setData)
      .catch((err) => setError(String(err)));
  }, []);

  return (
    <div className="app-panel">
      <h2 className="step__heading">
        <BarChart3 size={18} style={{ verticalAlign: 'middle', marginRight: 8 }} />
        Evaluation Dashboard
      </h2>
      <p className="step__subheading">
        Results from the golden benchmark (src/eval_benchmark.py) — answer accuracy, citation
        correctness, and safe abstention across 10 question categories.
      </p>

      {error && <div className="step__error">{error}</div>}

      {data && !data.available && (
        <p className="step__subheading">
          Not yet run. From the project root: `PYTHONPATH=src python3 src/eval_benchmark.py
          --out-json data/processed/eval_results.json`
        </p>
      )}

      {data?.available && (
        <>
          <div className="eval-stat-row">
            <div className="eval-stat-tile" style={{ borderColor: bandColor(data.accuracy) }}>
              <div className="eval-stat-tile__value" style={{ color: bandColor(data.accuracy) }}>
                {(data.accuracy * 100).toFixed(0)}%
              </div>
              <div className="eval-stat-tile__label">Overall accuracy</div>
            </div>
            <div className="eval-stat-tile">
              <div className="eval-stat-tile__value">{data.total_passed}/{data.total}</div>
              <div className="eval-stat-tile__label">Questions passed</div>
            </div>
            <div className="eval-stat-tile">
              <div className="eval-stat-tile__value">{new Date(data.run_at).toLocaleDateString()}</div>
              <div className="eval-stat-tile__label">Last run</div>
            </div>
          </div>

          <div className="app-panel__section">
            <label className="step__label">By category</label>
            <div className="eval-category-list">
              {data.categories.map((c) => {
                const ratio = c.total ? c.passed / c.total : 0;
                return (
                  <div className="eval-category-row" key={c.category}>
                    <span className="eval-category-row__name">{c.name}</span>
                    <span className="eval-category-row__bar">
                      <span
                        className="eval-category-row__fill"
                        style={{ width: `${ratio * 100}%`, background: bandColor(ratio) }}
                      />
                    </span>
                    <span className="eval-category-row__score">{c.passed}/{c.total}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
