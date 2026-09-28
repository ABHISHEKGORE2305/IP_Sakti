// src/pages/AppPage.jsx
// Main product shell: sidebar (theme/jurisdiction/language toggle) + the
// 6-step guided wizard. This is the "/app" experience Sprint 5 adds —
// distinct from the marketing LandingPage.

import { useEffect, useState } from 'react';
import Sidebar from '../components/app/Sidebar';
import Wizard from '../components/app/Wizard';
import './AppPage.css';

const THEME_KEY = 'ipsakti_theme';

export default function AppPage() {
  const [theme, setTheme] = useState(() => localStorage.getItem(THEME_KEY) || 'dark');
  const [jurisdiction, setJurisdiction] = useState('India');
  const [language, setLanguage] = useState('en');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [wizardResetKey, setWizardResetKey] = useState(0);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === 'dark' ? 'light' : 'dark'));

  const startNewSession = () => {
    setWizardResetKey((k) => k + 1);
    setSidebarOpen(false);
  };

  return (
    <div className={`app-shell${sidebarOpen ? ' app-shell--sidebar-open' : ''}`}>
      <Sidebar
        theme={theme}
        onToggleTheme={toggleTheme}
        jurisdiction={jurisdiction}
        onJurisdictionChange={setJurisdiction}
        language={language}
        onLanguageChange={setLanguage}
        onNewSession={startNewSession}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <button
        className="app-shell__menu-btn"
        aria-label="Open menu"
        onClick={() => setSidebarOpen(true)}
      >
        ☰
      </button>

      <main className="app-shell__main">
        <Wizard
          key={wizardResetKey}
          jurisdiction={jurisdiction}
          onJurisdictionChange={setJurisdiction}
          language={language}
        />
      </main>
    </div>
  );
}
