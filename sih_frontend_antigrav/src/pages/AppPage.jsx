// src/pages/AppPage.jsx
// Main product shell: sidebar (theme/jurisdiction/language toggle) + the
// 6-step guided wizard. This is the "/app" experience Sprint 5 adds —
// distinct from the marketing LandingPage.

import { useEffect, useState } from 'react';
import ChatView from '../components/app/ChatView';
import AdminCorpusPanel from '../components/app/panels/AdminCorpusPanel';
import EvalDashboard from '../components/app/panels/EvalDashboard';
import ExportMarketCards from '../components/app/panels/ExportMarketCards';
import LawVersionTimeline from '../components/app/panels/LawVersionTimeline';
import PrivacyDashboard from '../components/app/panels/PrivacyDashboard';
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
  const [view, setView] = useState('wizard');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === 'dark' ? 'light' : 'dark'));

  const startNewSession = () => {
    setWizardResetKey((k) => k + 1);
    setView('wizard');
    setSidebarOpen(false);
  };

  const handleViewChange = (v) => {
    setView(v);
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
        view={view}
        onViewChange={handleViewChange}
      />

      <button
        className="app-shell__menu-btn"
        aria-label="Open menu"
        onClick={() => setSidebarOpen(true)}
      >
        ☰
      </button>

      <main className="app-shell__main">
        {view === 'wizard' && (
          <Wizard
            key={wizardResetKey}
            jurisdiction={jurisdiction}
            onJurisdictionChange={setJurisdiction}
            language={language}
          />
        )}
        {view === 'chat' && <ChatView jurisdiction={jurisdiction} />}
        {view === 'export-markets' && <ExportMarketCards />}
        {view === 'law-versions' && <LawVersionTimeline />}
        {view === 'privacy' && <PrivacyDashboard />}
        {view === 'admin-corpus' && <AdminCorpusPanel />}
        {view === 'eval-dashboard' && <EvalDashboard />}
      </main>
    </div>
  );
}
