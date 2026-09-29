// src/components/app/Markdown.jsx
// Renders Gemini's markdown answers (### headings, **bold**, inline
// citations, checklists) properly instead of dumping the raw markdown
// source as preformatted text. Shared by the wizard's Analysis step and
// the Chat tab so both read identically.

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './Markdown.css';

export default function Markdown({ children, className = '' }) {
  if (!children) return null;
  return (
    <div className={`md-content ${className}`.trim()}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{children}</ReactMarkdown>
    </div>
  );
}
