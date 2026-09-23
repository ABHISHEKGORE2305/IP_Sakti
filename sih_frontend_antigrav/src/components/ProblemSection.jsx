// src/components/ProblemSection.jsx
import { motion } from 'framer-motion';
import * as LucideIcons from 'lucide-react';
import { problems } from '../data/content';
import './ProblemSection.css';

const cardVariants = {
  hidden: { opacity: 0, y: 36, rotateX: 6 },
  visible: (i) => ({
    opacity: 1,
    y: 0,
    rotateX: 0,
    transition: { duration: 0.7, delay: i * 0.15, ease: [0.16, 1, 0.3, 1] },
  }),
};

export default function ProblemSection() {
  return (
    <section id="problems" className="section problem-section">
      <div className="container">
        {/* Header */}
        <motion.div
          className="problem-section__header"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        >
          <span className="section-label">The Challenge</span>
          <h2 className="section-heading">
            Ayurvedic knowledge is everywhere.
            <br />
            <em>Reliable guidance isn't.</em>
          </h2>
        </motion.div>

        {/* Cards */}
        <div className="problem-section__cards">
          {problems.map((p, i) => {
            const Icon = LucideIcons[p.icon] || LucideIcons.HelpCircle;
            return (
              <motion.div
                key={p.number}
                className="problem-card"
                custom={i}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: '-60px' }}
                variants={cardVariants}
                whileHover={{ y: -4 }}
              >
                <div className="problem-card__header">
                  <span className="problem-card__number">{p.number}</span>
                  <div className="problem-card__icon"><Icon size={20} /></div>
                </div>
                <h3 className="problem-card__title">{p.title}</h3>
                <p className="problem-card__desc">{p.description}</p>
                <div className="problem-card__meta">{p.meta}</div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
