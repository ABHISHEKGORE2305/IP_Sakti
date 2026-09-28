// Step 2 — Ayurvedic Classification Wizard.
// Mirrors engines.classifier.classify_product's decision tree exactly:
// Q1 in_first_schedule -> Q2 formulation_modified (if yes) OR
// Q3 intended_use (if no). Optional step — can be skipped.

import { ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';
import { useState } from 'react';
import { INTENDED_USE_OPTIONS } from '../../../lib/wizardConfig';

export default function StepClassification({ onClassify, classifying, result, onNext, onBack }) {
  const [inFirstSchedule, setInFirstSchedule] = useState(null); // true | false | null
  const [formulationModified, setFormulationModified] = useState(null);
  const [intendedUse, setIntendedUse] = useState(null);

  const canSubmit =
    inFirstSchedule === true
      ? formulationModified !== null
      : inFirstSchedule === false
        ? intendedUse !== null
        : false;

  const handleClassify = () => {
    const inputs =
      inFirstSchedule === true
        ? { in_first_schedule: true, formulation_modified: formulationModified }
        : { in_first_schedule: false, intended_use: intendedUse };
    onClassify(inputs);
  };

  const classification = result?.engine_results?.classifier;

  return (
    <div>
      <h2 className="step__heading">Ayurvedic Product Classification</h2>
      <p className="step__subheading">
        Optional — answer these to get the deterministic statutory category (D&amp;C Act /
        FSSAI), or skip straight to your legal question.
      </p>

      <div className="step__field">
        <label className="step__label">
          Q1. Is this formulation documented, unchanged, in a First Schedule authoritative
          Ayurvedic text?
        </label>
        <div className="step__cards" style={{ marginBottom: 0 }}>
          <button
            className={`step__card${inFirstSchedule === true ? ' step__card--active' : ''}`}
            onClick={() => setInFirstSchedule(true)}
          >
            <div className="step__card-title">Yes</div>
          </button>
          <button
            className={`step__card${inFirstSchedule === false ? ' step__card--active' : ''}`}
            onClick={() => setInFirstSchedule(false)}
          >
            <div className="step__card-title">No</div>
          </button>
        </div>
      </div>

      {inFirstSchedule === true && (
        <div className="step__field">
          <label className="step__label">
            Q2. Have the ingredients, extracts, or dosage form been modified from the classical
            text?
          </label>
          <div className="step__cards" style={{ marginBottom: 0 }}>
            <button
              className={`step__card${formulationModified === true ? ' step__card--active' : ''}`}
              onClick={() => setFormulationModified(true)}
            >
              <div className="step__card-title">Modified</div>
            </button>
            <button
              className={`step__card${formulationModified === false ? ' step__card--active' : ''}`}
              onClick={() => setFormulationModified(false)}
            >
              <div className="step__card-title">Unchanged</div>
            </button>
          </div>
        </div>
      )}

      {inFirstSchedule === false && (
        <div className="step__field">
          <label className="step__label">Q3. What are the claims &amp; intended use?</label>
          <div className="step__cards" style={{ marginBottom: 0 }}>
            {INTENDED_USE_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                className={`step__card${intendedUse === opt.value ? ' step__card--active' : ''}`}
                onClick={() => setIntendedUse(opt.value)}
              >
                <div className="step__card-title">{opt.label}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {canSubmit && (
        <button
          className="step__btn step__btn--ghost"
          onClick={handleClassify}
          disabled={classifying}
          style={{ marginBottom: 16 }}
        >
          {classifying ? <Loader2 size={15} className="spin" /> : null}
          {classifying ? 'Classifying…' : 'Run classification'}
        </button>
      )}

      {classification && (
        <div className="classification-result">
          <p className="classification-result__title">{classification.label}</p>
          <p className="classification-result__row">
            <strong>Statutory basis:</strong> {classification.statutory_basis}
          </p>
          <p className="classification-result__row">
            <strong>Regulator:</strong> {classification.primary_regulator}
          </p>
        </div>
      )}

      <div className="step__actions">
        <button className="step__btn step__btn--ghost" onClick={onBack}>
          <ChevronLeft size={16} /> Back
        </button>
        <button className="step__btn step__btn--primary" onClick={onNext}>
          {classification ? 'Continue' : 'Skip this step'} <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
}
