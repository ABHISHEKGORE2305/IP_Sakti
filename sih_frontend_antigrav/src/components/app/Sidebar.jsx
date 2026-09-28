// src/components/app/Sidebar.jsx
// Responsive glassmorphic sidebar: logo, new-session action, theme toggle,
// jurisdiction toggle, and the multilingual language selector.

import { Globe2, Languages, Moon, PlusCircle, Sun, X } from 'lucide-react';
import { JURISDICTIONS, LANGUAGES } from '../../lib/wizardConfig';
import './Sidebar.css';

export default function Sidebar({
  theme,
  onToggleTheme,
  jurisdiction,
  onJurisdictionChange,
  language,
  onLanguageChange,
  onNewSession,
  open,
  onClose,
}) {
  return (
    <>
      {open && <div className="sidebar__scrim" onClick={onClose} />}

      <aside className={`app-sidebar${open ? ' app-sidebar--open' : ''}`} aria-label="IP-Sakti navigation">
        <div className="app-sidebar__header">
          <a href="/" className="app-sidebar__logo" aria-label="IP-Sakti home">
            <span className="app-sidebar__logo-dev">आयुर</span>
            <span className="app-sidebar__logo-x">X</span>
          </a>
          <button className="app-sidebar__close" aria-label="Close menu" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <button className="app-sidebar__new" onClick={onNewSession}>
          <PlusCircle size={16} />
          New Analysis
        </button>

        <section className="app-sidebar__section">
          <p className="app-sidebar__label">
            <Globe2 size={13} /> Jurisdiction
          </p>
          <div className="app-sidebar__pills">
            {JURISDICTIONS.map((j) => (
              <button
                key={j.value}
                className={`app-sidebar__pill${jurisdiction === j.value ? ' app-sidebar__pill--active' : ''}`}
                onClick={() => onJurisdictionChange(j.value)}
                title={j.desc}
              >
                <span>{j.flag}</span> {j.label}
              </button>
            ))}
          </div>
        </section>

        <section className="app-sidebar__section">
          <p className="app-sidebar__label">
            <Languages size={13} /> Language
          </p>
          <select
            className="app-sidebar__select"
            value={language}
            onChange={(e) => onLanguageChange(e.target.value)}
          >
            {LANGUAGES.map((l) => (
              <option key={l.code} value={l.code}>
                {l.label}
              </option>
            ))}
          </select>
          <p className="app-sidebar__hint">Statutory references stay in English when translated.</p>
        </section>

        <div className="app-sidebar__spacer" />

        <button className="app-sidebar__theme" onClick={onToggleTheme}>
          {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
          {theme === 'dark' ? 'Light mode' : 'Dark mode'}
        </button>

        <p className="app-sidebar__disclaimer">
          Informational only — not a substitute for advice from a registered IP professional.
        </p>
      </aside>
    </>
  );
}
