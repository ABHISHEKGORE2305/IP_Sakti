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
import { uid } from '../lib/uid';
import './AppPage.css';

const THEME_KEY = 'ipsakti_theme';

export default function AppPage() {
  const [theme, setTheme] = useState(() => localStorage.getItem(THEME_KEY) || 'dark');
  const [jurisdiction, setJurisdiction] = useState('India');
  const [language, setLanguage] = useState('en');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [wizardResetKey, setWizardResetKey] = useState(0);
  const [view, setView] = useState('wizard');
  // The chat transcript lives here, not inside ChatView, so it survives
  // switching tabs and can be seeded from the wizard's analysis.
  const [chatMessages, setChatMessages] = useState([]);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_KEY, theme);
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === 'dark' ? 'light' : 'dark'));

  const startNewSession = () => {
    setWizardResetKey((k) => k + 1);
    setChatMessages([]);
    setView('wizard');
    setSidebarOpen(false);
  };

  // "Continue in chat" from the wizard's action step: carry the analysed
  // question and its answer into the chat transcript as a completed turn, so
  // follow-ups are sent with that context as `history` instead of starting
  // from a blank slate.
  const continueInChat = ({ query, answer, sources }) => {
    setChatMessages((prev) => {
      const alreadySeeded = prev.some((m) => m.seededFrom === 'wizard' && m.content === answer);
      if (alreadySeeded) return prev;
      return [
        ...prev,
        { id: uid(), role: 'user', content: query, seededFrom: 'wizard' },
        {
          id: uid(),
          role: 'assistant',
          status: 'done',
          content: answer,
          sources: sources || [],
          seededFrom: 'wizard',
        },
      ];
    });
    setView('chat');
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
            onContinueInChat={continueInChat}
          />
        )}
        {view === 'chat' && (
          <ChatView
            jurisdiction={jurisdiction}
            messages={chatMessages}
            onMessagesChange={setChatMessages}
          />
        )}
        {view === 'export-markets' && <ExportMarketCards />}
        {view === 'law-versions' && <LawVersionTimeline />}
        {view === 'privacy' && <PrivacyDashboard />}
        {view === 'admin-corpus' && <AdminCorpusPanel />}
        {view === 'eval-dashboard' && <EvalDashboard />}
      </main>
    </div>
  );
}
