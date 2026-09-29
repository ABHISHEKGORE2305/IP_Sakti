// winning_features.md item 6 — IP Route Planner: "present it as a visual
// decision tree, not a paragraph." Renders POST /api/ip-route-plan's
// per-regime outlook list (engines/ipr_router.plan_ip_route — a
// composition of the classification's own ip_regimes blurbs + Section
// 3(p) risk, not new legal facts) as colored flow boxes.

import { GitBranch } from 'lucide-react';
import { useEffect, useState } from 'react';
import { fetchIpRoutePlan } from '../../../lib/api';

const OUTLOOK_STYLE = {
  available: { color: 'var(--risk-low)', label: 'Available' },
  conditional: { color: 'var(--risk-medium)', label: 'Conditional' },
  caution: { color: 'var(--risk-medium)', label: 'Caution' },
  barred: { color: 'var(--risk-high)', label: 'Barred' },
};

const REGIME_LABEL = {
  patent: 'Patent',
  trademark: 'Trademark',
  geographical_indication: 'Geographical Indication',
  industrial_design: 'Industrial Design',
  trade_secret: 'Trade Secret',
  copyright: 'Copyright',
  ppv_fr: 'Plant Variety (PPV&FR)',
};

export default function IPRoutePlanner({ ipRegimes, tkRisk, isRegionLinked }) {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!ipRegimes) {
      setPlan(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchIpRoutePlan({ ipRegimes, tkRisk, isRegionLinked })
      .then((data) => {
        if (!cancelled) setPlan(data.plan || []);
      })
      .catch((err) => {
        if (!cancelled) setError(String(err));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(ipRegimes), tkRisk, isRegionLinked]);

  if (!ipRegimes) return null;

  return (
    <div className="step__field" style={{ marginTop: 24 }}>
      <label className="step__label">
        <GitBranch size={14} style={{ verticalAlign: 'middle', marginRight: 6 }} />
        IP Route Planner
      </label>
      <p className="step__subheading" style={{ marginTop: -4 }}>
        Your personalized IP strategy map, from the classification's own regime notes
        {tkRisk ? ' and the Section 3(p)/3(e) risk analysis' : ''}.
      </p>
      {loading && <p className="step__subheading">Building…</p>}
      {error && <div className="step__error">{error}</div>}
      {plan && (
        <div className="ip-route-plan">
          {plan.map((p) => {
            const style = OUTLOOK_STYLE[p.outlook] || OUTLOOK_STYLE.available;
            return (
              <div className="ip-route-plan__box" key={p.regime} style={{ borderColor: style.color }}>
                <div className="ip-route-plan__header">
                  <span className="ip-route-plan__regime">{REGIME_LABEL[p.regime] || p.regime}</span>
                  <span className="ip-route-plan__outlook" style={{ color: style.color, borderColor: style.color }}>
                    {style.label}
                  </span>
                </div>
                <div className="ip-route-plan__note">{p.note}</div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
