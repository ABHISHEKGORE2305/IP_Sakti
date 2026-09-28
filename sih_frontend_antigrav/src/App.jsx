// src/App.jsx
import { Routes, Route } from 'react-router-dom';
import CustomCursor from './components/CustomCursor';
import LandingPage from './pages/LandingPage';
import AuthPage from './pages/AuthPage';
import AppPage from './pages/AppPage';

export default function App() {
  return (
    <>
      <CustomCursor />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/app" element={<AppPage />} />
      </Routes>
    </>
  );
}

