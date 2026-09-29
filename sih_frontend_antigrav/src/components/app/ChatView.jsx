// src/components/app/ChatView.jsx
// A standalone ChatGPT-style chat tab, separate from the guided wizard.
// Talks to POST /api/chat/ (src/api.py -> rag_pipeline.AyurvedicIPRAG.answer),
// resending recent turns as `history` so follow-ups have context (backend
// itself is stateless per-request).
//
// Unlike the wizard's single-shot Analysis step, the input is never locked
// while a reply is in flight: each sent message gets its own message-id and
// its own pending/done/error state, so the user can keep typing and send
// another question before the previous answer has come back.

import { AlertTriangle, ChevronDown, RotateCcw, Send } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { sendChatMessage } from '../../lib/api';
import Markdown from './Markdown';
import './ChatView.css';

function uid() {
  return crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
}

// Phrases describing what the RAG pipeline is doing while a reply is in
// flight. Words are revealed one at a time (~0.5s apart) so the user sees
// the "thinking" happen instead of a static spinner, then the indicator
// cross-fades into the next phrase and loops until the response lands.
const PROCESS_STEPS = [
  'Reading your question…',
  'Searching the Ayurvedic IP corpus…',
  'Retrieving relevant patent, TK, and ABS provisions…',
  'Cross-checking citations against source statutes…',
  'Drafting a grounded answer…',
];
const WORD_DELAY_MS = 500;
const STEP_PAUSE_MS = 900;

function ProcessAnimation() {
  const [stepIndex, setStepIndex] = useState(0);
  const [wordCount, setWordCount] = useState(0);

  const words = PROCESS_STEPS[stepIndex].split(' ');

  useEffect(() => {
    const timer = setTimeout(
      () => {
        if (wordCount < words.length) {
          setWordCount((c) => c + 1);
        } else {
          setStepIndex((i) => (i + 1) % PROCESS_STEPS.length);
          setWordCount(0);
        }
      },
      wordCount < words.length ? WORD_DELAY_MS : STEP_PAUSE_MS
    );
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [wordCount, stepIndex]);

  return (
    <span className="chat-processing" aria-live="polite" aria-label={PROCESS_STEPS[stepIndex]}>
      <span className="chat-processing__pulse" />
      <span className="chat-processing__text">
        {words.slice(0, wordCount).map((w, i) => (
          <span key={`${stepIndex}-${i}`} className="chat-processing__word">
            {w}
          </span>
        ))}
      </span>
    </span>
  );
}

function SourcesInline({ sources }) {
  const [open, setOpen] = useState(false);
  if (!sources || sources.length === 0) return null;
  return (
    <div className="chat-sources">
      <button className="chat-sources__toggle" onClick={() => setOpen((o) => !o)}>
        <ChevronDown
          size={12}
          style={{ transform: open ? 'rotate(0deg)' : 'rotate(-90deg)', transition: 'transform 0.15s' }}
        />
        {sources.length} source{sources.length > 1 ? 's' : ''}
      </button>
      {open && (
        <ul className="chat-sources__list">
          {sources.map((s) => (
            <li key={s.chunk_id || `${s.document}-${s.page}`}>
              {s.document}
              {s.legal_reference ? `, ${s.legal_reference}` : ''}
              {s.page != null ? `, p.${s.page}` : ''}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function Bubble({ message, onRetry }) {
  const isUser = message.role === 'user';
  return (
    <div className={`chat-row${isUser ? ' chat-row--user' : ''}`}>
      <div className={`chat-bubble${isUser ? ' chat-bubble--user' : ' chat-bubble--assistant'}`}>
        {isUser && <div className="chat-bubble__text">{message.content}</div>}

        {!isUser && message.status === 'pending' && <ProcessAnimation />}

        {!isUser && message.status === 'error' && (
          <div className="chat-bubble__error">
            <AlertTriangle size={13} style={{ marginRight: 6, verticalAlign: 'middle' }} />
            {message.error || 'Something went wrong.'}
            <button className="chat-bubble__retry" onClick={() => onRetry(message.id)}>
              <RotateCcw size={12} /> Retry
            </button>
          </div>
        )}

        {!isUser && message.status === 'done' && (
          <>
            <Markdown>{message.content}</Markdown>
            <SourcesInline sources={message.sources} />
          </>
        )}
      </div>
    </div>
  );
}

export default function ChatView({ jurisdiction }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const listRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    if (!listRef.current) return;
    listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [messages]);

  // Build the {role, content} history the backend expects from every
  // already-*done* turn before `beforeId` (a still-pending or failed turn
  // contributes nothing useful as context).
  const historyBefore = (beforeId) => {
    const out = [];
    for (const m of messages) {
      if (m.id === beforeId) break;
      if (m.role === 'user') out.push({ role: 'user', content: m.content });
      else if (m.status === 'done') out.push({ role: 'assistant', content: m.content });
    }
    return out;
  };

  const runQuery = async (userMsg, assistantId) => {
    const history = historyBefore(userMsg.id);
    try {
      const res = await sendChatMessage({ query: userMsg.content, jurisdiction, history });
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? res.error && !res.answer
              ? { ...m, status: 'error', error: res.error }
              : { ...m, status: 'done', content: res.answer, sources: res.sources || [] }
            : m
        )
      );
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) => (m.id === assistantId ? { ...m, status: 'error', error: String(err) } : m))
      );
    }
  };

  const send = () => {
    const text = input.trim();
    if (!text) return;

    const userMsg = { id: uid(), role: 'user', content: text };
    const assistantMsg = { id: uid(), role: 'assistant', status: 'pending', content: '' };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';

    runQuery(userMsg, assistantMsg.id);
  };

  const retry = (assistantId) => {
    const idx = messages.findIndex((m) => m.id === assistantId);
    if (idx < 1) return;
    const userMsg = messages[idx - 1];
    if (userMsg.role !== 'user') return;

    setMessages((prev) =>
      prev.map((m) => (m.id === assistantId ? { ...m, status: 'pending', error: null } : m))
    );
    runQuery(userMsg, assistantId);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  const autoGrow = (e) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 160)}px`;
  };

  const pendingCount = messages.filter((m) => m.status === 'pending').length;

  return (
    <div className="chat-view">
      <div className="chat-view__header">
        <h2 className="step__heading" style={{ marginBottom: 2 }}>
          Chat
        </h2>
        <p className="step__subheading" style={{ margin: 0 }}>
          Ask follow-up questions freely — no need to wait for a reply before sending the next one.
        </p>
      </div>

      <div className="chat-view__list" ref={listRef}>
        {messages.length === 0 && (
          <div className="chat-view__empty">
            Ask about Indian patent, TK, or ABS law for Ayurvedic inventions. Answers cite the
            underlying statutes and rules retrieved from the corpus.
          </div>
        )}
        {messages.map((m) => (
          <Bubble key={m.id} message={m} onRetry={retry} />
        ))}
      </div>

      <div className="chat-view__composer">
        <textarea
          ref={textareaRef}
          className="chat-view__input"
          placeholder="Ask a question…"
          value={input}
          onChange={autoGrow}
          onKeyDown={handleKeyDown}
          rows={1}
        />
        <button
          className="step__btn step__btn--primary chat-view__send"
          onClick={send}
          disabled={!input.trim()}
          title="Send (Enter)"
        >
          <Send size={15} />
        </button>
      </div>
      {pendingCount > 0 && (
        <div className="chat-view__status">
          {pendingCount} {pendingCount > 1 ? 'replies' : 'reply'} in progress — you can keep chatting.
        </div>
      )}
    </div>
  );
}
