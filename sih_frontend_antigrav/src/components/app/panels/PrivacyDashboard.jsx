// winning_features.md items 15-17 — DPDP privacy dashboard, real audit
// log, and the mocked paid-source connector's consent-and-audit flow.
// All session-scoped via src/db.py (no login — see api.js's getSessionId).

import { AlertTriangle, Database, Lock, ShieldCheck, Trash2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { deleteMyData, getAuditLog, getConsent, getPrivacySummary, setConsent } from '../../../lib/api';

const PAID_CONSENT_TYPE = 'paid_source_premium_patent_db';

// Deliberately fabricated, unmissably-labeled sample data — never
// presented as a real database query outcome. See implementation_plan.md's
// Phase 9 note: "even a mocked connector with a real consent-and-audit
// flow earns points" is the doc's own framing for this feature.
const MOCK_RESULTS = [
  { id: 'MOCK-IN-2024-0417291', title: 'Sample record — herbal extraction process', status: 'Granted (mock)' },
  { id: 'MOCK-IN-2023-0298104', title: 'Sample record — Ayurvedic cosmetic formulation', status: 'Pending (mock)' },
  { id: 'MOCK-US-11234567', title: 'Sample record — botanical composition patent', status: 'Granted (mock)' },
];

function PaidConnectorSection({ consent, onConsentChange }) {
  const granted = Boolean(consent?.[PAID_CONSENT_TYPE]);
  const [busy, setBusy] = useState(false);

  const toggle = async () => {
    setBusy(true);
    try {
      await setConsent(PAID_CONSENT_TYPE, !granted);
      onConsentChange();
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="app-panel__section">
      <label className="step__label">
        <Database size={14} style={{ verticalAlign: 'middle', marginRight: 6 }} />
        Paid Source Connector — "Premium Patent Analytics DB"
      </label>
      <p className="step__subheading" style={{ marginTop: -4 }}>
        A mocked paid-database connector, demonstrating the consent-and-audit flow real paid
        sources would need (left_to_do.md item 16). No real query is ever made.
      </p>
      <button className="step__btn step__btn--ghost" onClick={toggle} disabled={busy}>
        {granted ? 'Revoke consent' : 'Grant consent'}
      </button>

      {granted && (
        <div className="mock-connector">
          <div className="mock-connector__banner">
            <AlertTriangle size={13} /> MOCK DATA — not a real database connection
          </div>
          {MOCK_RESULTS.map((r) => (
            <div className="mock-connector__row" key={r.id}>
              <span className="mock-connector__id">{r.id}</span>
              <span>{r.title}</span>
              <span className="mock-connector__status">{r.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function PrivacyDashboard() {
  const [consent, setConsentState] = useState(null);
  const [summary, setSummary] = useState(null);
  const [auditLog, setAuditLog] = useState(null);
  const [deleteStatus, setDeleteStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  const refresh = () => {
    setLoading(true);
    Promise.all([getConsent(), getPrivacySummary(), getAuditLog(50)])
      .then(([c, s, a]) => {
        setConsentState(c.consent || {});
        setSummary(s);
        setAuditLog(a.entries || []);
      })
      .finally(() => setLoading(false));
  };

  useEffect(refresh, []);

  const handleDelete = async () => {
    if (!window.confirm('Delete all locally-logged data for this session? This cannot be undone.')) return;
    const res = await deleteMyData();
    setDeleteStatus(res);
    refresh();
  };

  return (
    <div className="app-panel">
      <h2 className="step__heading">
        <ShieldCheck size={18} style={{ verticalAlign: 'middle', marginRight: 8 }} />
        Privacy & Audit Log
      </h2>
      <p className="step__subheading">
        DPDP-aligned session data — every entry below is scoped to this browser session only
        (no login), never visible to other users.
      </p>

      {loading ? (
        <p className="step__subheading">Loading…</p>
      ) : (
        <>
          <div className="app-panel__section">
            <label className="step__label">
              <Lock size={14} style={{ verticalAlign: 'middle', marginRight: 6 }} /> What's stored
            </label>
            <p className="step__subheading" style={{ marginTop: -4 }}>
              {summary?.audit_log_entries ?? 0} audit-log entries for this session.
            </p>
            <button className="step__btn step__btn--ghost" onClick={handleDelete}>
              <Trash2 size={14} /> Delete my data
            </button>
            {deleteStatus && (
              <div className="step__success">
                Deleted {deleteStatus.audit_log_rows_deleted} audit-log row(s) and{' '}
                {deleteStatus.consent_rows_deleted} consent row(s).
              </div>
            )}
          </div>

          <PaidConnectorSection consent={consent} onConsentChange={refresh} />

          <div className="app-panel__section">
            <label className="step__label">Audit log</label>
            <div className="audit-log">
              {(!auditLog || auditLog.length === 0) && (
                <p className="step__subheading">No activity logged yet this session.</p>
              )}
              {auditLog?.map((e, i) => (
                <div className="audit-log__row" key={i}>
                  <span className="audit-log__time">{new Date(e.timestamp * 1000).toLocaleString()}</span>
                  <span className="audit-log__type">{e.event_type}</span>
                  <span className="audit-log__payload">{JSON.stringify(e.payload)}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
