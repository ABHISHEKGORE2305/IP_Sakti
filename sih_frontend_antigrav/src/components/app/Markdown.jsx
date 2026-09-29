// src/components/app/Markdown.jsx
// Renders Gemini's markdown answers (### headings, **bold**, inline
// citations, checklists) properly instead of dumping the raw markdown
// source as preformatted text. Shared by the wizard's Analysis step and
// the Chat tab so both read identically.

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './Markdown.css';

const BLOCK_START = /^\s{0,3}(#{1,6}\s|>|```|~~~|\||[-*+]\s|\d+[.)]\s)/;
const SETEXT_RULE = /^\s{0,3}(=+|-{2,}|\*{3,}|_{3,})\s*$/;

/**
 * Markdown collapses a single newline into a space, so the engine answers —
 * which are one "**Label**: value" fact per line — render as a run-on
 * paragraph. Turn those single newlines into hard breaks (trailing two
 * spaces), leaving fenced code, tables and lines that already begin a new
 * block untouched.
 */
function preserveLineBreaks(source) {
  const lines = String(source).split('\n');
  let inFence = false;

  return lines
    .map((line, i) => {
      if (/^\s{0,3}(```|~~~)/.test(line)) {
        inFence = !inFence;
        return line;
      }
      if (inFence) return line;

      const next = lines[i + 1];
      if (!line.trim() || !next || !next.trim()) return line;
      if (/\s{2}$/.test(line) || line.endsWith('\\')) return line;
      // The next line already opens its own block, or turns this one into a
      // setext heading / rule — a hard break would be wrong or redundant.
      if (BLOCK_START.test(next) || SETEXT_RULE.test(next)) return line;

      return `${line}  `;
    })
    .join('\n');
}

export default function Markdown({ children, className = '' }) {
  if (!children) return null;
  return (
    <div className={`md-content ${className}`.trim()}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {preserveLineBreaks(children)}
      </ReactMarkdown>
    </div>
  );
}
