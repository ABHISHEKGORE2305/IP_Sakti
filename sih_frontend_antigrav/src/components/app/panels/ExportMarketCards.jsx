// winning_features.md item 12 — Export Market Navigator: country cards
// for key markets, IP filing route, kept strictly in International mode.
// US/EU/UK cards call the real, already-grounded engines.intl_engine
// pathway (advise_market) via POST /api/agent's target_market/market_inputs.
// GCC/ASEAN render as explicit "not yet in corpus" placeholders — engines.
// intl_engine.Market only supports US/EU/UK (confirmed by reading the
// source), so fabricating GCC/ASEAN regulatory claims here would violate
// this platform's citation-grounding guarantee. Flagged, not invented.

import { AlertCircle, Globe2 } from 'lucide-react';
import { useState } from 'react';
import { runAgent } from '../../../lib/api';
import { US_ROUTES, EU_EVIDENCE_BASES } from '../../../lib/wizardConfig';

const MARKETS = [
  { value: 'US', flag: '🇺🇸', label: 'United States' },
  { value: 'EU', flag: '🇪🇺', label: 'European Union' },
  { value: 'UK', flag: '🇬🇧', label: 'United Kingdom' },
];

const NOT_YET_GROUNDED = [
  { flag: '🇸🇦', label: 'GCC (Gulf Cooperation Council)' },
  { flag: '🌏', label: 'ASEAN' },
];

function MarketCard({ market }) {
  const [route, setRoute] = useState(market.value === 'US' ? 'botanical_drug' : 'traditional_use');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const marketInputs = market.value === 'US' ? { route } : market.value === 'EU' ? { evidence_basis: route } : {};

  const fetchPathway = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await runAgent({
        query: `${market.label} market access pathway`,
        jurisdiction: 'International',
        targetMarket: market.value,
        marketInputs,
      });
      setResult(res);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  const pathway = result?.engine_results?.market_pathway;

  return (
    <div className="market-card">
      <div className="market-card__header">
        <span>{market.flag}</span> {market.label}
      </div>

      {market.value === 'US' && (
        <select className="app-sidebar__select" value={route} onChange={(e) => setRoute(e.target.value)}>
          {US_ROUTES.map((r) => (
            <option key={r.value} value={r.value}>
              {r.label}
            </option>
          ))}
        </select>
      )}
      {market.value === 'EU' && (
        <select className="app-sidebar__select" value={route} onChange={(e) => setRoute(e.target.value)}>
          {EU_EVIDENCE_BASES.map((r) => (
            <option key={r.value} value={r.value}>
              {r.label}
            </option>
          ))}
        </select>
      )}

      <button className="step__btn step__btn--ghost" onClick={fetchPathway} disabled={loading} style={{ marginTop: 10 }}>
        {loading ? 'Loading…' : pathway ? 'Refresh' : 'Get pathway'}
      </button>

      {error && <div className="step__error">{error}</div>}

      {pathway && (
        <div className="market-card__body">
          {pathway.route && <p><strong>Route:</strong> {pathway.route}</p>}
          <p><strong>Framework:</strong> {pathway.governing_framework}</p>
          {pathway.requirements?.length > 0 && (
            <ul>
              {pathway.requirements.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          )}
          <p className="market-card__finding">{pathway.finding}</p>
        </div>
      )}
    </div>
  );
}

export default function ExportMarketCards() {
  return (
    <div className="app-panel">
      <h2 className="step__heading">
        <Globe2 size={18} style={{ verticalAlign: 'middle', marginRight: 8 }} />
        Export Market Navigator
      </h2>
      <p className="step__subheading">
        Country cards for key export markets — International mode only. Each card calls the
        real grounded pathway logic (FDA botanical/DSHEA, EU THMPD, UK MHRA THR).
      </p>

      <div className="market-card-grid">
        {MARKETS.map((m) => (
          <MarketCard key={m.value} market={m} />
        ))}
      </div>

      <div className="step__field" style={{ marginTop: 20 }}>
        <label className="step__label">Not yet in corpus</label>
        <div className="market-card-grid">
          {NOT_YET_GROUNDED.map((m) => (
            <div className="market-card market-card--placeholder" key={m.label}>
              <div className="market-card__header">
                <span>{m.flag}</span> {m.label}
              </div>
              <p className="market-card__finding">
                <AlertCircle size={12} style={{ verticalAlign: 'middle', marginRight: 4 }} />
                No grounded regulatory pathway data ingested for this market yet — flagged rather
                than fabricated.
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
