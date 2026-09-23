// src/components/TrustSection.jsx
import { motion } from 'framer-motion';
import { Eye, BarChart2, ShieldCheck, Scale } from 'lucide-react';
import { trustPrinciples } from '../data/content';
import './TrustSection.css';

const iconMap = { Eye, BarChart2, ShieldCheck, Scale };

export default function TrustSection() {
  return (
    <section className="section trust-section">
      <div className="container">
        {/* Header */}
        <motion.div
          className="trust-section__header"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        >
          <span className="section-label">Trust & Safety</span>
          <h2 className="section-heading">
            AI should inform —{' '}
            <span className="trust-section__heading-em">
              not replace professional judgment.
            </span>
          </h2>
          <p className="section-subheading">
            AyurX is designed to make information easier to understand while making
            its sources, evidence, uncertainty, and safety considerations visible.
          </p>
        </motion.div>

        {/* Principles grid */}
        <div className="trust-section__grid">
          {trustPrinciples.map((p, i) => {
            const Icon = iconMap[p.icon];
            return (
              <motion.div
                key={p.title}
                className="trust-card"
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-40px' }}
                transition={{ duration: 0.65, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }}
              >
                <div className="trust-card__icon">
                  {Icon && <Icon size={20} strokeWidth={1.5} />}
                </div>
                <h3 className="trust-card__title">{p.title}</h3>
                <p className="trust-card__desc">{p.description}</p>
              </motion.div>
            );
          })}
        </div>

        {/* Disclaimer */}
        <motion.div
          className="trust-section__disclaimer"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <ShieldCheck size={16} strokeWidth={1.5} />
          <p>
            AyurX provides educational and informational support. It does not
            diagnose conditions or replace advice from qualified healthcare
            professionals.
          </p>
        </motion.div>
      </div>
    </section>
  );
}
