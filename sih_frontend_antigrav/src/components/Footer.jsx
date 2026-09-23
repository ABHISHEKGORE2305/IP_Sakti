// src/components/Footer.jsx
import { footerColumns } from '../data/content';
import './Footer.css';

export default function Footer() {
  return (
    <footer id="footer" className="footer" role="contentinfo">
      <div className="container">
        <div className="footer__top">
          {/* Brand */}
          <div className="footer__brand">
            <div className="footer__logo">
              <span className="logo-devanagari">आयुर</span>
              <span className="logo-x">X</span>
            </div>
            <p className="footer__tagline">Ancient wisdom. Smarter answers.</p>
            <p className="footer__disclaimer">
              AyurX provides informational support and does not replace diagnosis,
              treatment, or advice from a qualified healthcare professional.
            </p>
          </div>

          {/* Columns */}
          <nav className="footer__columns" aria-label="Footer navigation">
            {footerColumns.map((col) => (
              <div key={col.heading} className="footer__col">
                <h3 className="footer__col-heading">{col.heading}</h3>
                <ul className="footer__col-links">
                  {col.links.map((link) => (
                    <li key={link}>
                      <a href="#" className="footer__link">{link}</a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </nav>
        </div>

        {/* Bottom bar */}
        <div className="footer__bottom">
          <p className="footer__copy">© 2026 AyurX. All rights reserved.</p>
          <div className="footer__bottom-links">
            <a href="#" className="footer__link">Privacy</a>
            <a href="#" className="footer__link">Terms</a>
            <a href="#" className="footer__link">Contact</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
