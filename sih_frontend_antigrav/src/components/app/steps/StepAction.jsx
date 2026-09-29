// Step 6 — Interactive Compliance Checklist & Case Escalation.
// Renders the Phase 5.4 case brief, exports it (PDF/Markdown/JSON), and
// offers on-demand translation (POST /api/translate) + text-to-speech.

import { ChevronLeft, FileDown, FileJson, FileText, Languages, Leaf, Send, Volume2 } from 'lucide-react';
import { useState } from 'react';
import { escalateCase, translateText } from '../../../lib/api';
import {
  buildCaseBriefMarkdown,
  downloadAbsChecklist,
  downloadJson,
  downloadMarkdown,
  printAbsChecklist,
  printCaseBrief,
} from '../../../lib/caseBrief';
import { LANGUAGES } from '../../../lib/wizardConfig';
import Markdown from '../Markdown';

export default function StepAction({ wizardState, result, language, onBack }) {
  const [translated, setTranslated] = useState(null);
  const [translating, setTranslating] = useState(false);
  const [translateError, setTranslateError] = useState(null);
  const [replyTo, setReplyTo] = useState('');
  const [escalating, setEscalating] = useState(false);
  const [escalateStatus, setEscalateStatus] = useState(null); // { ok: bool, message: string }

  const brief = buildCaseBriefMarkdown(wizardState, result);
  const languageLabel = LANGUAGES.find((l) => l.code === language)?.label || 'English';

  const handleEscalate = async () => {
    setEscalating(true);
    setEscalateStatus(null);
    try {
      const res = await escalateCase({
        caseBriefMarkdown: brief,
        query: wizardState?.query,
        replyTo: replyTo || undefined,
      });
      if (res.sent) {
        setEscalateStatus({ ok: true, message: 'Sent to your IP facilitator.' });
      } else {
        setEscalateStatus({ ok: false, message: res.error || 'Escalation failed.' });
      }
    } catch (err) {
      setEscalateStatus({ ok: false, message: String(err) });
    } finally {
      setEscalating(false);
    }
  };

  const handleTranslate = async () => {
    if (!result?.final_answer) return;
    setTranslating(true);
    setTranslateError(null);
    try {
      const res = await translateText(result.final_answer, language);
      if (res.error) {
        setTranslateError(res.error);
      } else {
        setTranslated(res.translated_text);
      }
    } catch (err) {
      setTranslateError(String(err));
    } finally {
      setTranslating(false);
    }
  };

  const speak = (text) => {
    if (!window.speechSynthesis || !text) return;
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  };

  const checklistItems =
    wizardState?.classificationResult?.classifier?.licensing_route ||
    (result?.engine_results?.classifier?.licensing_route ?? []);

  return (
    <div>
      <h2 className="step__heading">Action Plan & Case Brief</h2>
      <p className="step__subheading">
        Export this analysis as a formal case brief, or hand it to an IP facilitator.
      </p>

      {checklistItems.length > 0 && (
        <div className="step__field">
          <label className="step__label">Licensing checklist</label>
          <div className="classification-result">
            {checklistItems.map((item, i) => (
              <p key={i} className="classification-result__row">
                ☐ {item}
              </p>
            ))}
          </div>
        </div>
      )}

      <div className="action-plan__translate-row">
        <Languages size={15} color="var(--app-text-muted)" />
        <span style={{ fontSize: '0.82rem', color: 'var(--app-text-secondary)' }}>
          Translate to {languageLabel}
          {language === 'en' ? ' (already English)' : ''}
        </span>
        {language !== 'en' && (
          <button className="step__btn step__btn--ghost" onClick={handleTranslate} disabled={translating}>
            {translating ? 'Translating…' : 'Translate answer'}
          </button>
        )}
        {window.speechSynthesis && (
          <button
            className="step__btn step__btn--ghost"
            onClick={() => speak(translated || result?.final_answer)}
          >
            <Volume2 size={14} /> Listen
          </button>
        )}
      </div>
      {translateError && <div className="step__error">{translateError}</div>}
      {translated && (
        <div className="analysis-answer" style={{ marginBottom: 20 }}>
          <Markdown>{translated}</Markdown>
        </div>
      )}

      <label className="step__label">Case brief preview</label>
      <div className="action-plan__brief">{brief}</div>

      <div className="action-plan__export-row">
        <button className="step__btn step__btn--ghost" onClick={() => printCaseBrief(wizardState, result)}>
          <FileDown size={14} /> Export PDF
        </button>
        <button className="step__btn step__btn--ghost" onClick={() => downloadMarkdown(wizardState, result)}>
          <FileText size={14} /> Export Markdown
        </button>
        <button className="step__btn step__btn--ghost" onClick={() => downloadJson(wizardState, result)}>
          <FileJson size={14} /> Export JSON
        </button>
      </div>

      {result?.engine_results?.abs_compliance && (
        <>
          <label className="step__label">ABS compliance checklist</label>
          <p className="step__subheading" style={{ marginTop: -4 }}>
            A dedicated export of just the biodiversity/ABS obligations and their citations
            (winning_features.md item 7) — separate from the general case brief above.
          </p>
          <div className="action-plan__export-row">
            <button className="step__btn step__btn--ghost" onClick={() => printAbsChecklist(result)}>
              <Leaf size={14} /> Export ABS Checklist PDF
            </button>
            <button className="step__btn step__btn--ghost" onClick={() => downloadAbsChecklist(result)}>
              <FileText size={14} /> Export ABS Checklist Markdown
            </button>
          </div>
        </>
      )}

      <label className="step__label">Escalate to IP Facilitator</label>
      <p className="step__subheading" style={{ marginTop: -4 }}>
        Emails this case brief to the IP facilitator for human review.
      </p>
      <div className="action-plan__translate-row">
        <input
          type="email"
          className="step__input"
          placeholder="Your email (optional, for facilitator to reply to)"
          value={replyTo}
          onChange={(e) => setReplyTo(e.target.value)}
          style={{ flex: '1 1 260px', minWidth: 200 }}
        />
        <button className="step__btn step__btn--primary" onClick={handleEscalate} disabled={escalating}>
          <Send size={14} /> {escalating ? 'Sending…' : 'Escalate'}
        </button>
      </div>
      {escalateStatus && (
        <div className={escalateStatus.ok ? 'step__success' : 'step__error'}>{escalateStatus.message}</div>
      )}

      <div className="step__actions">
        <button className="step__btn step__btn--ghost" onClick={onBack}>
          <ChevronLeft size={16} /> Back
        </button>
        <span />
      </div>
    </div>
  );
}
