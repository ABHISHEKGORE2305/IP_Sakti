// src/components/app/Wizard.jsx
// The 6-step guided wizard: Jurisdiction -> Classification -> Issue
// Routing -> Analysis -> Sources -> Action Plan. Owns all wizard state
// and the two backend calls (classification + main analysis); each step
// is a presentational component driven by props.

import { useState } from 'react';
import { runAgent } from '../../lib/api';
import { WIZARD_STEPS } from '../../lib/wizardConfig';
import StepAction from './steps/StepAction';
import StepAnalysis from './steps/StepAnalysis';
import StepClassification from './steps/StepClassification';
import StepIssuePicker from './steps/StepIssuePicker';
import StepJurisdiction from './steps/StepJurisdiction';
import StepSources from './steps/StepSources';
import './Wizard.css';

export default function Wizard({ jurisdiction, onJurisdictionChange, language, onContinueInChat }) {
  const [stepIndex, setStepIndex] = useState(0);

  const [classificationResult, setClassificationResult] = useState(null);
  const [classificationInputs, setClassificationInputs] = useState(null);
  const [classifying, setClassifying] = useState(false);
  const [persona, setPersona] = useState(null);

  const [query, setQuery] = useState('');
  const [forcedAgent, setForcedAgent] = useState(null);
  const [targetMarket, setTargetMarket] = useState(null);
  const [marketInputs, setMarketInputs] = useState(null);
  const [gratkInputs, setGratkInputs] = useState(null);
  const [iprInputs, setIprInputs] = useState(null);
  const [absInputs, setAbsInputs] = useState(null);
  const [regInputs, setRegInputs] = useState(null);

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [runError, setRunError] = useState(null);

  const goTo = (i) => setStepIndex(Math.max(0, Math.min(WIZARD_STEPS.length - 1, i)));
  const next = () => goTo(stepIndex + 1);
  const back = () => goTo(stepIndex - 1);

  const runClassification = async (inputs) => {
    setClassifying(true);
    setClassificationInputs(inputs);
    try {
      const res = await runAgent({
        query: 'Classify this product',
        jurisdiction,
        persona,
        classificationInputs: inputs,
      });
      setClassificationResult(res);
    } catch (err) {
      setClassificationResult({ error: String(err), final_answer: '', sources: [] });
    } finally {
      setClassifying(false);
    }
  };

  const runAnalysis = async () => {
    setLoading(true);
    setRunError(null);
    setResult(null);
    try {
      const res = await runAgent({
        query,
        jurisdiction,
        persona,
        forcedAgent,
        targetMarket,
        marketInputs,
        gratkInputs,
        iprInputs,
        absInputs,
        regInputs,
      });
      setResult(res);
    } catch (err) {
      setRunError(String(err));
    } finally {
      setLoading(false);
    }
  };

  const wizardStateForExport = {
    jurisdiction,
    targetMarket,
    query,
    classificationResult,
  };

  const steps = [
    <StepJurisdiction
      key="jurisdiction"
      jurisdiction={jurisdiction}
      onChange={onJurisdictionChange}
      onNext={next}
      persona={persona}
      onPersonaChange={setPersona}
    />,
    <StepClassification
      key="classification"
      onClassify={runClassification}
      classifying={classifying}
      result={classificationResult}
      onNext={next}
      onBack={back}
    />,
    <StepIssuePicker
      key="issue"
      jurisdiction={jurisdiction}
      query={query}
      onQueryChange={setQuery}
      forcedAgent={forcedAgent}
      onForcedAgentChange={setForcedAgent}
      targetMarket={targetMarket}
      onTargetMarketChange={setTargetMarket}
      marketInputs={marketInputs}
      onMarketInputsChange={setMarketInputs}
      gratkInputs={gratkInputs}
      onGratkInputsChange={setGratkInputs}
      iprInputs={iprInputs}
      onIprInputsChange={setIprInputs}
      absInputs={absInputs}
      onAbsInputsChange={setAbsInputs}
      regInputs={regInputs}
      onRegInputsChange={setRegInputs}
      onBack={back}
      onNext={() => {
        next();
        runAnalysis();
      }}
    />,
    <StepAnalysis
      key="analysis"
      loading={loading}
      result={result}
      error={runError}
      onBack={back}
      onNext={next}
      onRetry={runAnalysis}
    />,
    <StepSources
      key="sources"
      result={result}
      onBack={back}
      onNext={next}
      jurisdiction={jurisdiction}
      classificationInputs={classificationInputs}
      classificationResult={classificationResult}
      absInputs={absInputs}
    />,
    <StepAction
      key="action"
      wizardState={wizardStateForExport}
      result={result}
      language={language}
      onBack={back}
      onContinueInChat={
        onContinueInChat && result?.final_answer
          ? () =>
              onContinueInChat({
                query,
                answer: result.final_answer,
                sources: result.sources || [],
              })
          : null
      }
    />,
  ];

  return (
    <div className="wizard">
      <ol className="wizard__progress" aria-label="Wizard progress">
        {WIZARD_STEPS.map((s, i) => (
          <li
            key={s.key}
            className={`wizard__progress-item${i === stepIndex ? ' wizard__progress-item--active' : ''}${
              i < stepIndex ? ' wizard__progress-item--done' : ''
            }`}
          >
            <button
              className="wizard__progress-btn"
              onClick={() => i <= stepIndex && goTo(i)}
              disabled={i > stepIndex}
            >
              <span className="wizard__progress-index">{i + 1}</span>
              <span className="wizard__progress-label">{s.label}</span>
            </button>
          </li>
        ))}
      </ol>

      <div className="wizard__panel">{steps[stepIndex]}</div>
    </div>
  );
}
