// winning_features.md item 20 — Corpus admin panel: shows every known
// document (PDF + web-sourced) with real chunk counts, and lets you
// upload a new PDF. Upload only stages the file + registers it as
// "pending_reindex" — it deliberately does NOT synchronously re-embed
// (see api.py's POST /api/admin/corpus/upload docstring for why).

import { Database } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { getAdminCorpus, uploadCorpusDocument } from '../../../lib/api';

const STATUS_COLOR = {
  indexed: 'var(--risk-low)',
  not_ingested: 'var(--risk-medium)',
  pending_reindex: 'var(--risk-medium)',
};

export default function AdminCorpusPanel() {
  const [documents, setDocuments] = useState(null);
  const [error, setError] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploading, setUploading] = useState(false);
  const fileInput = useRef(null);

  const refresh = () => {
    getAdminCorpus()
      .then((data) => setDocuments(data.documents || []))
      .catch((err) => setError(String(err)));
  };

  useEffect(refresh, []);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadStatus(null);
    try {
      const res = await uploadCorpusDocument(file);
      setUploadStatus(res);
      refresh();
    } catch (err) {
      setUploadStatus({ saved: false, error: String(err) });
    } finally {
      setUploading(false);
      if (fileInput.current) fileInput.current.value = '';
    }
  };

  const totalChunks = documents?.reduce((sum, d) => sum + (d.chunk_count || 0), 0) || 0;

  return (
    <div className="app-panel">
      <h2 className="step__heading">
        <Database size={18} style={{ verticalAlign: 'middle', marginRight: 8 }} />
        Corpus Admin
      </h2>
      <p className="step__subheading">
        Every document known to the system — PDF, periodic web-fetch, and uploaded-pending —
        with real chunk counts from the actual ingested data.
      </p>

      <div className="app-panel__section">
        <label className="step__label">Upload a new PDF</label>
        <p className="step__subheading" style={{ marginTop: -4 }}>
          Saves to data/raw/ and marks it pending re-index — you still run
          `PYTHONPATH=src python3 src/ingest.py` after adding it to document_config.DOCUMENTS to
          actually embed it (deliberately not automatic — see the backend endpoint's docstring).
        </p>
        <input ref={fileInput} type="file" accept="application/pdf" onChange={handleUpload} disabled={uploading} />
        {uploading && <p className="step__subheading">Uploading…</p>}
        {uploadStatus?.saved && (
          <div className="step__success">
            Saved as {uploadStatus.document_id}, status: {uploadStatus.status}.
            <br />
            {uploadStatus.next_step}
          </div>
        )}
        {uploadStatus && !uploadStatus.saved && <div className="step__error">{uploadStatus.error}</div>}
      </div>

      {error && <div className="step__error">{error}</div>}

      {documents && (
        <div className="app-panel__section">
          <label className="step__label">
            {documents.length} documents, {totalChunks} total chunks indexed
          </label>
          <div className="admin-corpus-table">
            <div className="admin-corpus-table__header">
              <span>Document</span>
              <span>Type</span>
              <span>Jurisdiction</span>
              <span>Source</span>
              <span>Chunks</span>
              <span>Status</span>
            </div>
            {documents.map((d) => (
              <div className="admin-corpus-table__row" key={d.document_id}>
                <span title={d.filename}>{d.document || d.document_id}</span>
                <span>{d.document_type || '—'}</span>
                <span>{d.jurisdiction || '—'}</span>
                <span>{d.source}</span>
                <span>{d.chunk_count}</span>
                <span style={{ color: STATUS_COLOR[d.status] || 'var(--app-text-secondary)' }}>{d.status}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
