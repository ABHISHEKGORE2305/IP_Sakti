// Step 3 — Multi-Regime Issue Picker.
// Forces a specific specialist agent (bypassing keyword routing — see
// agents.graph.supervisor_router's forced_agent handling) and, for
// intl_agent, exposes the Sprint 4 market/GRATK structured inputs.

import { ChevronLeft, ChevronRight, Mic } from 'lucide-react';
import { useState } from 'react';
import {
  ABS_ACTIVITY_TYPES,
  ABS_ENTITY_TYPES,
  EU_EVIDENCE_BASES,
  IPR_REGIMES,
  ISSUE_REGIMES,
  NICE_PRODUCT_TYPES,
  PPVFR_CATEGORIES,
  REG_PRODUCT_CATEGORIES,
  TARGET_MARKETS,
  US_ROUTES,
} from '../../../lib/wizardConfig';
import { WIZARD_QUERY_SUGGESTIONS } from '../../../lib/suggestions';
import SuggestionChips from '../SuggestionChips';

function useSpeechInput(onResult) {
  const [listening, setListening] = useState(false);
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const supported = Boolean(SpeechRecognition);

  const start = () => {
    if (!supported) return;
    const recognizer = new SpeechRecognition();
    recognizer.lang = 'en-IN';
    recognizer.interimResults = false;
    recognizer.maxAlternatives = 1;
    recognizer.onresult = (e) => onResult(e.results[0][0].transcript);
    recognizer.onend = () => setListening(false);
    recognizer.onerror = () => setListening(false);
    setListening(true);
    recognizer.start();
  };

  return { supported, listening, start };
}

export default function StepIssuePicker({
  jurisdiction,
  query,
  onQueryChange,
  forcedAgent,
  onForcedAgentChange,
  targetMarket,
  onTargetMarketChange,
  marketInputs,
  onMarketInputsChange,
  gratkInputs,
  onGratkInputsChange,
  iprInputs,
  onIprInputsChange,
  absInputs,
  onAbsInputsChange,
  regInputs,
  onRegInputsChange,
  onBack,
  onNext,
}) {
  const speech = useSpeechInput((text) => onQueryChange(`${query ? query + ' ' : ''}${text}`));

  const canSubmit = query.trim().length > 0 && (forcedAgent !== 'intl_agent' || targetMarket);

  return (
    <div>
      <h2 className="step__heading">Multi-Regime Issue Picker</h2>
      <p className="step__subheading">
        Pick the legal regime this question is about, then describe your situation.
      </p>

      <div className="step__cards">
        {ISSUE_REGIMES.filter(
          (r) => jurisdiction === 'India' || r.agent === 'intl_agent' || r.agent === 'patent_agent'
        ).map((regime) => (
          <button
            key={regime.agent}
            className={`step__card${forcedAgent === regime.agent ? ' step__card--active' : ''}`}
            onClick={() => onForcedAgentChange(regime.agent)}
          >
            <div className="step__card-title">{regime.label}</div>
            <div className="step__card-desc">{regime.desc}</div>
          </button>
        ))}
      </div>

      {forcedAgent === 'intl_agent' && (
        <div className="market-subform">
          <div className="step__field">
            <label className="step__label">Target market</label>
            <div className="step__cards" style={{ marginBottom: 0 }}>
              {TARGET_MARKETS.map((m) => (
                <button
                  key={m.value}
                  className={`step__card${targetMarket === m.value ? ' step__card--active' : ''}`}
                  onClick={() => {
                    onTargetMarketChange(m.value);
                    onMarketInputsChange(null);
                  }}
                >
                  <div className="step__card-title">{m.label}</div>
                  <div className="step__card-desc">{m.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {targetMarket === 'US' && (
            <div className="step__field">
              <label className="step__label">US route</label>
              <select
                className="step__select"
                value={marketInputs?.route || ''}
                onChange={(e) => onMarketInputsChange({ route: e.target.value })}
              >
                <option value="" disabled>
                  Select a route…
                </option>
                {US_ROUTES.map((r) => (
                  <option key={r.value} value={r.value}>
                    {r.label}
                  </option>
                ))}
              </select>
            </div>
          )}

          {targetMarket === 'EU' && (
            <div className="step__field">
              <label className="step__label">EU evidence basis</label>
              <select
                className="step__select"
                style={{ marginBottom: 10 }}
                value={marketInputs?.evidence_basis || ''}
                onChange={(e) =>
                  onMarketInputsChange({ ...marketInputs, evidence_basis: e.target.value })
                }
              >
                <option value="" disabled>
                  Select an evidence basis…
                </option>
                {EU_EVIDENCE_BASES.map((r) => (
                  <option key={r.value} value={r.value}>
                    {r.label}
                  </option>
                ))}
              </select>

              {marketInputs?.evidence_basis === 'traditional_use' && (
                <div style={{ display: 'flex', gap: 10 }}>
                  <input
                    className="step__input"
                    type="number"
                    placeholder="Years of traditional use"
                    value={marketInputs?.years_traditional_use || ''}
                    onChange={(e) =>
                      onMarketInputsChange({
                        ...marketInputs,
                        years_traditional_use: Number(e.target.value) || 0,
                      })
                    }
                  />
                  <input
                    className="step__input"
                    type="number"
                    placeholder="Years in the EU"
                    value={marketInputs?.years_eu_use || ''}
                    onChange={(e) =>
                      onMarketInputsChange({
                        ...marketInputs,
                        years_eu_use: Number(e.target.value) || 0,
                      })
                    }
                  />
                </div>
              )}

              {marketInputs?.evidence_basis === 'well_established_use' && (
                <input
                  className="step__input"
                  type="number"
                  placeholder="Years of EU bibliographic evidence"
                  value={marketInputs?.years_bibliographic_evidence || ''}
                  onChange={(e) =>
                    onMarketInputsChange({
                      ...marketInputs,
                      years_bibliographic_evidence: Number(e.target.value) || 0,
                    })
                  }
                />
              )}
            </div>
          )}

          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={Boolean(gratkInputs?.uses_genetic_resource_or_traditional_knowledge)}
              onChange={(e) =>
                onGratkInputsChange({
                  uses_genetic_resource_or_traditional_knowledge: e.target.checked,
                })
              }
            />
            This invention is based on genetic resources / traditional knowledge (checks GRATK
            disclosure obligation)
          </label>
        </div>
      )}

      {forcedAgent === 'abs_agent' && (
        <div className="market-subform">
          <div className="step__field">
            <label className="step__label">Entity type</label>
            <select
              className="step__select"
              value={absInputs?.entity_type || ''}
              onChange={(e) => onAbsInputsChange({ ...absInputs, entity_type: e.target.value })}
            >
              <option value="" disabled>Select…</option>
              {ABS_ENTITY_TYPES.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>
          <div className="step__field">
            <label className="step__label">Activity type</label>
            <select
              className="step__select"
              value={absInputs?.activity_type || ''}
              onChange={(e) => onAbsInputsChange({ ...absInputs, activity_type: e.target.value })}
            >
              <option value="" disabled>Select…</option>
              {ABS_ACTIVITY_TYPES.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>
          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={Boolean(absInputs?.seeking_ipr_on_biological_invention)}
              onChange={(e) =>
                onAbsInputsChange({ ...absInputs, seeking_ipr_on_biological_invention: e.target.checked })
              }
            />
            Seeking a patent/IPR on an invention based on this biological resource
          </label>
        </div>
      )}

      {forcedAgent === 'reg_agent' && (
        <div className="market-subform">
          <div className="step__field">
            <label className="step__label">Product category</label>
            <select
              className="step__select"
              value={regInputs?.product_category || ''}
              onChange={(e) => onRegInputsChange({ ...regInputs, product_category: e.target.value })}
            >
              <option value="" disabled>Select…</option>
              {REG_PRODUCT_CATEGORIES.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>
          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={Boolean(regInputs?.makes_disease_cure_claim)}
              onChange={(e) =>
                onRegInputsChange({ ...regInputs, makes_disease_cure_claim: e.target.checked })
              }
            />
            Advertising/labelling makes a disease-cure or prevention claim
          </label>
        </div>
      )}

      {forcedAgent === 'tm_gi_agent' && (
        <div className="market-subform">
          <div className="step__field">
            <label className="step__label">IP regime</label>
            <select
              className="step__select"
              value={iprInputs?.regime || ''}
              onChange={(e) => onIprInputsChange({ regime: e.target.value })}
            >
              <option value="" disabled>Select…</option>
              {IPR_REGIMES.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>

          {iprInputs?.regime === 'trademark' && (
            <>
              <div className="step__field">
                <label className="step__label">Product/service type (NICE class)</label>
                <select
                  className="step__select"
                  value={iprInputs?.product_type || ''}
                  onChange={(e) => onIprInputsChange({ ...iprInputs, product_type: e.target.value })}
                >
                  <option value="" disabled>Select…</option>
                  {NICE_PRODUCT_TYPES.map((o) => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </select>
              </div>
              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={Boolean(iprInputs?.is_generic_or_descriptive_ayurvedic_term)}
                  onChange={(e) =>
                    onIprInputsChange({
                      ...iprInputs,
                      is_generic_or_descriptive_ayurvedic_term: e.target.checked,
                    })
                  }
                />
                This is a generic/descriptive Ayurvedic term (e.g. a classical formulation name)
              </label>
            </>
          )}

          {iprInputs?.regime === 'ppv_fr' && (
            <div className="step__field">
              <label className="step__label">Plant variety category</label>
              <select
                className="step__select"
                value={iprInputs?.variety_category || ''}
                onChange={(e) => onIprInputsChange({ ...iprInputs, variety_category: e.target.value })}
              >
                <option value="" disabled>Select…</option>
                {PPVFR_CATEGORIES.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
          )}
        </div>
      )}

      <div className="step__field">
        <label className="step__label">Describe your situation or question</label>
        <textarea
          className="step__textarea"
          rows={4}
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          placeholder="e.g. We modified a classical Ashwagandha formulation with a novel liposomal extraction process — is it patentable?"
        />
        <SuggestionChips
          items={WIZARD_QUERY_SUGGESTIONS}
          value={query}
          onSelect={onQueryChange}
        />
        {speech.supported && (
          <button
            className="step__btn step__btn--ghost"
            style={{ marginTop: 8 }}
            onClick={speech.start}
            disabled={speech.listening}
          >
            <Mic size={14} /> {speech.listening ? 'Listening…' : 'Voice input'}
          </button>
        )}
      </div>

      <div className="step__actions">
        <button className="step__btn step__btn--ghost" onClick={onBack}>
          <ChevronLeft size={16} /> Back
        </button>
        <button className="step__btn step__btn--primary" onClick={onNext} disabled={!canSubmit}>
          Analyze <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
}
