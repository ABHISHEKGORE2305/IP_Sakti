// src/components/FinalCTA.jsx
import { motion } from 'framer-motion';
import './FinalCTA.css';

export default function FinalCTA() {
  return (
    <section className="section finalcta-section">
      {/* Background botanical motif */}
      <div className="finalcta-section__bg" aria-hidden="true" />

      <div className="container finalcta-section__inner">
        <motion.div
          className="finalcta-section__content"
          initial={{ opacity: 0, y: 32 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
        >
          <span className="section-label">Get Started</span>

          <h2 className="section-heading finalcta-section__heading">
            Curious about Ayurveda?
            <br />
            <em>Start with a question.</em>
          </h2>

          <p className="section-subheading finalcta-section__sub">
            Explore classical Ayurvedic knowledge, cross-examine evidence, and discover verified botanical sources through one calm interface.
          </p>

          <motion.a
            href="/auth"
            className="btn-primary finalcta-section__cta"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Get Started <span className="btn-arrow">→</span>
          </motion.a>

          {/* Decorative logo echo */}
          <div className="finalcta-section__logo-echo" aria-hidden="true">
            <span className="logo-devanagari">आयुर</span>
            <span className="logo-x">X</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
