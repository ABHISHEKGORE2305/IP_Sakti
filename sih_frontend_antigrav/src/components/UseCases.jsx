// src/components/UseCases.jsx
import { motion } from 'framer-motion';
import { Leaf, FlaskConical, Heart, Layers, ShieldAlert, BookOpen } from 'lucide-react';
import { useCases } from '../data/content';
import './UseCases.css';

const iconMap = { Leaf, FlaskConical, Heart, Layers, ShieldAlert, BookOpen };

export default function UseCases() {
  return (
    <section id="use-cases" className="section usecases-section">
      <div className="container">
        <motion.div
          className="usecases-section__header"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        >
          <span className="section-label">Use Cases</span>
          <h2 className="section-heading">Explore Ayurveda with context.</h2>
        </motion.div>

        <div className="usecases-grid">
          {useCases.map((uc, i) => {
            const Icon = iconMap[uc.icon];
            return (
              <motion.div
                key={uc.number}
                className="usecase-card"
                initial={{ opacity: 0, y: 28 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-40px' }}
                transition={{ duration: 0.6, delay: (i % 3) * 0.1, ease: [0.16, 1, 0.3, 1] }}
                whileHover={{ y: -4 }}
              >
                <div className="usecase-card__icon">
                  {Icon && <Icon size={22} strokeWidth={1.5} />}
                </div>
                <div className="usecase-card__content">
                  <div className="usecase-card__meta">
                    <h3 className="usecase-card__title">{uc.title}</h3>
                    <span className="usecase-card__number">{uc.number}</span>
                  </div>
                  <p className="usecase-card__desc">{uc.description}</p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
