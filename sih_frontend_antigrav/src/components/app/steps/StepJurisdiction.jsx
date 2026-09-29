// Step 1 — Jurisdiction & Market Switch, plus persona selection.
import { ChevronRight } from 'lucide-react';
import { JURISDICTIONS, PERSONAS } from '../../../lib/wizardConfig';

export default function StepJurisdiction({ jurisdiction, onChange, onNext, persona, onPersonaChange }) {
  return (
    <div>
      <h2 className="step__heading">Jurisdiction & Market Switch</h2>
      <p className="step__subheading">
        Choose the legal scope for this analysis. India routes through the Patents Act, D&amp;C
        Act, Biological Diversity Act, and AYUSH/FSSAI/CDSCO. International routes through WIPO,
        US FDA, EU THMPD, and export-market pathways. This choice also filters retrieval itself —
        an India-scoped answer cannot cite International sources, and vice versa.
      </p>

      <div className="step__cards">
        {JURISDICTIONS.map((j) => (
          <button
            key={j.value}
            className={`step__card${jurisdiction === j.value ? ' step__card--active' : ''}`}
            onClick={() => onChange(j.value)}
          >
            <div className="step__card-title">
              <span>{j.flag}</span> {j.label}
            </div>
            <div className="step__card-desc">{j.desc}</div>
          </button>
        ))}
      </div>

      <label className="step__label" style={{ marginTop: 24, display: 'block' }}>
        Who's asking? (optional)
      </label>
      <p className="step__subheading" style={{ marginTop: -4 }}>
        Adjusts tone and depth only — never changes which legal facts get cited.
      </p>
      <div className="step__cards">
        {PERSONAS.map((p) => (
          <button
            key={p.value}
            className={`step__card${persona === p.value ? ' step__card--active' : ''}`}
            onClick={() => onPersonaChange(persona === p.value ? null : p.value)}
          >
            <div className="step__card-title">{p.label}</div>
            <div className="step__card-desc">{p.desc}</div>
          </button>
        ))}
      </div>

      <div className="step__actions">
        <span />
        <button className="step__btn step__btn--primary" onClick={onNext}>
          Continue <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
}
