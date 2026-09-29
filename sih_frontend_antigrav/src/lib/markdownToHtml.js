// src/lib/markdownToHtml.js
// A small, dependency-free Markdown -> HTML renderer used for the printable
// (Save-as-PDF) case brief. The on-screen preview uses react-markdown; the
// print window is a detached document, so it needs plain HTML it can inline.
//
// Supports exactly the subset buildCaseBriefMarkdown / buildAbsChecklistMarkdown
// emit: h1/h2/h3, bullet lists, ordered lists, GFM task-list items, bold,
// italics, inline code and links.

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function inline(text) {
  return escapeHtml(text)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2">$1</a>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[\s(])\*([^*\n]+)\*(?=[\s).,;:]|$)/g, '$1<em>$2</em>')
    .replace(/(^|[\s(])_([^_\n]+)_(?=[\s).,;:]|$)/g, '$1<em>$2</em>');
}

export function markdownToHtml(markdown) {
  const out = [];
  let listType = null; // 'ul' | 'ol' | null
  let listKey = null; // type + variant, so a checklist starts a fresh list

  const closeList = () => {
    if (listType) {
      out.push(`</${listType}>`);
      listType = null;
      listKey = null;
    }
  };

  const openList = (type, className) => {
    const key = `${type}:${className || ''}`;
    if (listKey !== key) {
      closeList();
      out.push(`<${type}${className ? ` class="${className}"` : ''}>`);
      listType = type;
      listKey = key;
    }
  };

  for (const rawLine of String(markdown || '').split('\n')) {
    const lineText = rawLine.trimEnd();

    if (!lineText.trim()) {
      closeList();
      continue;
    }

    const heading = /^(#{1,4})\s+(.*)$/.exec(lineText);
    if (heading) {
      closeList();
      const level = heading[1].length;
      out.push(`<h${level}>${inline(heading[2])}</h${level}>`);
      continue;
    }

    const task = /^[-*]\s+\[( |x|X)\]\s+(.*)$/.exec(lineText);
    if (task) {
      openList('ul', 'checklist');
      const box = task[1].trim() ? '☑' : '☐';
      out.push(`<li><span class="box">${box}</span>${inline(task[2])}</li>`);
      continue;
    }

    const bullet = /^[-*]\s+(.*)$/.exec(lineText);
    if (bullet) {
      openList('ul', null);
      out.push(`<li>${inline(bullet[1])}</li>`);
      continue;
    }

    const ordered = /^(\d+)\.\s+(.*)$/.exec(lineText);
    if (ordered) {
      openList('ol', null);
      out.push(`<li>${inline(ordered[2])}</li>`);
      continue;
    }

    closeList();
    out.push(`<p>${inline(lineText)}</p>`);
  }

  closeList();
  return out.join('\n');
}
