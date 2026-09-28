// src/pages/AuthPage.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Lock, Eye, EyeOff, User, ArrowRight, Leaf, BookOpen, ShieldCheck } from 'lucide-react';
import authBgImg from '../assets/ayurvedic-reference.jpg';
import './AuthPage.css';

// After mock auth success, go to the Sprint 5 guided-wizard app
const APP_ROUTE = '/app';

const FEATURES = [
  {
    Icon: Leaf,
    title: 'Authentic Sources',
    desc: 'Drawn from classical texts',
  },
  {
    Icon: BookOpen,
    title: 'Evidence-Aware',
    desc: 'Citations with every answer',
  },
  {
    Icon: ShieldCheck,
    title: 'Safe & Responsible',
    desc: 'Health information, not a substitute for professional care',
  },
];

export default function AuthPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState('signin'); // 'signin' | 'signup'
  const [showPwd, setShowPwd] = useState(false);
  const [showConfirmPwd, setShowConfirmPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [forgotMsg, setForgotMsg] = useState('');
  const [errors, setErrors] = useState({});

  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    rememberMe: false,
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: '' }));
  };

  const validate = () => {
    const errs = {};
    if (mode === 'signup' && !form.name.trim()) errs.name = 'Full name is required.';
    if (!form.email.trim()) errs.email = 'Email address is required.';
    if (!form.password.trim()) errs.password = 'Password is required.';
    if (mode === 'signup') {
      if (!form.confirmPassword.trim())
        errs.confirmPassword = 'Please confirm your password.';
      else if (form.password && form.password !== form.confirmPassword)
        errs.confirmPassword = 'Passwords do not match.';
    }
    return errs;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length > 0) {
      setErrors(errs);
      return;
    }
    setLoading(true);
    // Mock auth — accept any non-empty credentials, redirect after brief delay
    setTimeout(() => {
      navigate(APP_ROUTE);
    }, 800);
  };

  const handleForgotPassword = (e) => {
    e.preventDefault();
    setForgotMsg('Password recovery will be available soon.');
    setTimeout(() => setForgotMsg(''), 3500);
  };

  const switchMode = (newMode) => {
    setMode(newMode);
    setErrors({});
    setForgotMsg('');
    setShowPwd(false);
    setShowConfirmPwd(false);
    setForm({ name: '', email: '', password: '', confirmPassword: '', rememberMe: false });
  };

  const isSignIn = mode === 'signin';

  return (
    <div className="auth-page">
      {/* ── Background layers ── */}
      <div
        className="auth-page__bg"
        style={{ backgroundImage: `url(${authBgImg})` }}
        aria-hidden="true"
      />
      <div className="auth-page__overlay" aria-hidden="true" />

      {/* ── Two-column layout ── */}
      <div className="auth-page__layout">

        {/* ════════════ LEFT: Branding ════════════ */}
        <motion.section
          className="auth-left"
          aria-label="AyurX branding"
          initial={{ opacity: 0, x: -28 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
        >
          {/* Logo */}
          <a href="/" className="auth-left__logo" aria-label="Back to AyurX home">
            <span className="auth-left__logo-dev">आयुर</span>
            <span className="auth-left__logo-x">X</span>
          </a>

          {/* Main headline */}
          <div className="auth-left__body">
            <h1 className="auth-left__heading">
              Ancient<br />
              Wisdom.<br />
              <em>Modern Answers.</em>
            </h1>

            <p className="auth-left__sub">
              Evidence-based Ayurveda,<br />
              powered by AI.
            </p>

            {/* Feature highlights */}
            <ul className="auth-features" aria-label="Key features">
              {FEATURES.map(({ Icon, title, desc }) => (
                <li key={title} className="auth-feature">
                  <div className="auth-feature__icon-wrap" aria-hidden="true">
                    <Icon size={16} strokeWidth={1.8} />
                  </div>
                  <div className="auth-feature__text">
                    <span className="auth-feature__title">{title}</span>
                    <span className="auth-feature__desc">{desc}</span>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          {/* Bottom shloka */}
          <div className="auth-left__shloka-block">
            <p className="auth-left__shloka">"सर्वे सन्तु निरामयाः"</p>
            <p className="auth-left__motto">— Towards a healthier tomorrow</p>
          </div>
        </motion.section>

        {/* ════════════ RIGHT: Auth card ════════════ */}
        <div className="auth-right" aria-label="Authentication">
          <AnimatePresence mode="wait">
            <motion.div
              key={mode}
              className="auth-card"
              role="main"
              initial={{ opacity: 0, y: 22 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -14 }}
              transition={{ duration: 0.42, ease: [0.16, 1, 0.3, 1] }}
            >
              {/* Card heading */}
              <header className="auth-card__header">
                <h2 className="auth-card__heading">
                  {isSignIn ? 'Welcome Back' : 'Create Your Account'}
                </h2>
                <p className="auth-card__sub">
                  {isSignIn
                    ? 'Sign in to continue your Ayurvedic journey'
                    : 'Begin your Ayurvedic journey'}
                </p>
              </header>

              {/* Form */}
              <form
                className="auth-form"
                onSubmit={handleSubmit}
                noValidate
                aria-label={isSignIn ? 'Sign in form' : 'Sign up form'}
              >
                {/* Full name (sign-up only) */}
                {!isSignIn && (
                  <div className="auth-field">
                    <div className={`auth-input-wrap${errors.name ? ' --error' : ''}`}>
                      <User size={15} className="auth-input-icon" aria-hidden="true" />
                      <input
                        type="text"
                        name="name"
                        id="auth-name"
                        className="auth-input"
                        placeholder="Full name"
                        value={form.name}
                        onChange={handleChange}
                        autoComplete="name"
                        aria-required="true"
                        aria-invalid={!!errors.name}
                        aria-describedby={errors.name ? 'auth-name-err' : undefined}
                      />
                    </div>
                    {errors.name && (
                      <p id="auth-name-err" className="auth-error" role="alert">
                        {errors.name}
                      </p>
                    )}
                  </div>
                )}

                {/* Email */}
                <div className="auth-field">
                  <div className={`auth-input-wrap${errors.email ? ' --error' : ''}`}>
                    <Mail size={15} className="auth-input-icon" aria-hidden="true" />
                    <input
                      type="email"
                      name="email"
                      id="auth-email"
                      className="auth-input"
                      placeholder="Email address"
                      value={form.email}
                      onChange={handleChange}
                      autoComplete="email"
                      aria-required="true"
                      aria-invalid={!!errors.email}
                      aria-describedby={errors.email ? 'auth-email-err' : undefined}
                    />
                  </div>
                  {errors.email && (
                    <p id="auth-email-err" className="auth-error" role="alert">
                      {errors.email}
                    </p>
                  )}
                </div>

                {/* Password */}
                <div className="auth-field">
                  <div className={`auth-input-wrap${errors.password ? ' --error' : ''}`}>
                    <Lock size={15} className="auth-input-icon" aria-hidden="true" />
                    <input
                      type={showPwd ? 'text' : 'password'}
                      name="password"
                      id="auth-password"
                      className="auth-input"
                      placeholder="Password"
                      value={form.password}
                      onChange={handleChange}
                      autoComplete={isSignIn ? 'current-password' : 'new-password'}
                      aria-required="true"
                      aria-invalid={!!errors.password}
                      aria-describedby={errors.password ? 'auth-pwd-err' : undefined}
                    />
                    <button
                      type="button"
                      className="auth-eye"
                      aria-label={showPwd ? 'Hide password' : 'Show password'}
                      onClick={() => setShowPwd((v) => !v)}
                    >
                      {showPwd ? <EyeOff size={15} /> : <Eye size={15} />}
                    </button>
                  </div>
                  {errors.password && (
                    <p id="auth-pwd-err" className="auth-error" role="alert">
                      {errors.password}
                    </p>
                  )}
                </div>

                {/* Confirm password (sign-up only) */}
                {!isSignIn && (
                  <div className="auth-field">
                    <div
                      className={`auth-input-wrap${
                        errors.confirmPassword ? ' --error' : ''
                      }`}
                    >
                      <Lock size={15} className="auth-input-icon" aria-hidden="true" />
                      <input
                        type={showConfirmPwd ? 'text' : 'password'}
                        name="confirmPassword"
                        id="auth-confirm-password"
                        className="auth-input"
                        placeholder="Confirm password"
                        value={form.confirmPassword}
                        onChange={handleChange}
                        autoComplete="new-password"
                        aria-required="true"
                        aria-invalid={!!errors.confirmPassword}
                        aria-describedby={
                          errors.confirmPassword ? 'auth-cpwd-err' : undefined
                        }
                      />
                      <button
                        type="button"
                        className="auth-eye"
                        aria-label={showConfirmPwd ? 'Hide password' : 'Show password'}
                        onClick={() => setShowConfirmPwd((v) => !v)}
                      >
                        {showConfirmPwd ? <EyeOff size={15} /> : <Eye size={15} />}
                      </button>
                    </div>
                    {errors.confirmPassword && (
                      <p id="auth-cpwd-err" className="auth-error" role="alert">
                        {errors.confirmPassword}
                      </p>
                    )}
                  </div>
                )}

                {/* Remember me + Forgot password (sign-in only) */}
                {isSignIn && (
                  <div className="auth-row">
                    <label className="auth-remember" htmlFor="auth-remember-me">
                      <input
                        type="checkbox"
                        id="auth-remember-me"
                        name="rememberMe"
                        className="auth-checkbox-native"
                        checked={form.rememberMe}
                        onChange={handleChange}
                      />
                      <span className="auth-checkbox-box" aria-hidden="true" />
                      <span className="auth-remember-label">Remember me</span>
                    </label>
                    <button
                      type="button"
                      className="auth-forgot"
                      id="auth-forgot-btn"
                      onClick={handleForgotPassword}
                    >
                      Forgot password?
                    </button>
                  </div>
                )}

                {/* Forgot password message */}
                <AnimatePresence>
                  {forgotMsg && (
                    <motion.p
                      className="auth-forgot-msg"
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      role="status"
                    >
                      {forgotMsg}
                    </motion.p>
                  )}
                </AnimatePresence>

                {/* Submit */}
                <button
                  type="submit"
                  id="auth-submit-btn"
                  className="auth-submit"
                  disabled={loading}
                  aria-label={isSignIn ? 'Sign in to AyurX' : 'Create your AyurX account'}
                >
                  {loading ? (
                    <span className="auth-spinner" aria-label="Authenticating…" />
                  ) : (
                    <>
                      {isSignIn ? 'Sign In' : 'Create Account'}
                      <ArrowRight size={16} aria-hidden="true" />
                    </>
                  )}
                </button>
              </form>

              {/* Divider */}
              <div className="auth-divider" aria-hidden="true">
                <span />
                <span className="auth-divider__text">or</span>
                <span />
              </div>

              {/* Google button — visual only, no OAuth */}
              <button
                type="button"
                id="auth-google-btn"
                className="auth-google"
                disabled
                aria-label="Continue with Google — coming soon"
                title="Google sign-in coming soon"
              >
                {/* Official Google logo SVG */}
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 18 18"
                  fill="none"
                  aria-hidden="true"
                >
                  <path
                    d="M17.64 9.2045c0-.638-.0573-1.252-.1636-1.8418H9v3.4814h4.8436c-.2086 1.125-.8427 2.0782-1.7959 2.717v2.2587h2.9087c1.7018-1.5668 2.6836-3.874 2.6836-6.6153z"
                    fill="#4285F4"
                  />
                  <path
                    d="M9 18c2.43 0 4.4673-.8059 5.9564-2.1818l-2.9087-2.2587c-.8059.54-1.8368.8591-3.0477.8591-2.3441 0-4.3282-1.5836-5.036-3.7105H.9574v2.3318C2.4382 15.9832 5.4818 18 9 18z"
                    fill="#34A853"
                  />
                  <path
                    d="M3.964 10.71c-.18-.54-.2823-1.1177-.2823-1.71s.1023-1.17.2823-1.71V4.9582H.9574C.3477 6.1732 0 7.5477 0 9s.3477 2.8268.9574 4.0418L3.964 10.71z"
                    fill="#FBBC05"
                  />
                  <path
                    d="M9 3.5795c1.3214 0 2.5077.4541 3.4405 1.346l2.5813-2.5814C13.4627.8918 11.4255 0 9 0 5.4818 0 2.4382 2.0168.9574 4.9582L3.964 7.29C4.6718 5.1632 6.6559 3.5795 9 3.5795z"
                    fill="#EA4335"
                  />
                </svg>
                Continue with Google
              </button>

              {/* Switch mode */}
              <p className="auth-switch">
                {isSignIn ? (
                  <>
                    Don&apos;t have an account?{' '}
                    <button
                      type="button"
                      id="auth-switch-signup"
                      className="auth-switch-btn"
                      onClick={() => switchMode('signup')}
                    >
                      Sign up
                    </button>
                  </>
                ) : (
                  <>
                    Already have an account?{' '}
                    <button
                      type="button"
                      id="auth-switch-signin"
                      className="auth-switch-btn"
                      onClick={() => switchMode('signin')}
                    >
                      Sign in
                    </button>
                  </>
                )}
              </p>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
