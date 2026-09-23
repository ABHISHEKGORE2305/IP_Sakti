// src/components/Navbar.jsx
import { useState, useEffect } from 'react';
import { Menu, X } from 'lucide-react';
import { navLinks } from '../data/content';
import './Navbar.css';

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [activeLink, setActiveLink] = useState('#home');

  useEffect(() => {
    const onScroll = () => {
      setScrolled(window.scrollY > 40);

      // Simple active section detection
      const sections = ['#home', '#problems', '#how-it-works', '#use-cases', '#testimonials'];
      for (const sectionId of sections) {
        const el = document.querySelector(sectionId);
        if (el) {
          const rect = el.getBoundingClientRect();
          if (rect.top <= 160 && rect.bottom >= 160) {
            setActiveLink(sectionId);
            break;
          }
        }
      }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleNav = (href) => {
    setActiveLink(href);
    setMenuOpen(false);
    const el = document.querySelector(href);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <header className={`navbar${scrolled ? ' navbar--scrolled' : ''}`} role="banner">
      <div className="navbar__inner container">
        {/* Logo */}
        <a
          href="#home"
          className="navbar__logo"
          onClick={(e) => { e.preventDefault(); handleNav('#home'); }}
          aria-label="AyurX Home"
        >
          <span className="navbar__logo-devanagari">आयुर</span>
          <span className="navbar__logo-x">X</span>
        </a>

        {/* Desktop Nav */}
        <nav className="navbar__links" aria-label="Main navigation">
          {navLinks.map((link) => {
            const isActive = activeLink === link.href;
            return (
              <a
                key={link.href}
                href={link.href}
                className={`navbar__link${isActive ? ' navbar__link--active' : ''}`}
                onClick={(e) => { e.preventDefault(); handleNav(link.href); }}
              >
                {link.label}
              </a>
            );
          })}
        </nav>

        {/* Desktop CTA */}
        <a
          href="/auth"
          className="navbar__cta"
        >
          <span>Get Started</span>
          <span className="navbar__cta-arrow">→</span>
        </a>

        {/* Mobile toggle */}
        <button
          className="navbar__toggle"
          aria-label={menuOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen((v) => !v)}
        >
          {menuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className="navbar__mobile" role="navigation" aria-label="Mobile navigation">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="navbar__mobile-link"
              onClick={(e) => { e.preventDefault(); handleNav(link.href); }}
            >
              {link.label}
            </a>
          ))}
          <a
            href="/auth"
            className="btn-primary navbar__mobile-cta"
          >
            Get Started <span className="btn-arrow">→</span>
          </a>
        </div>
      )}
    </header>
  );
}
