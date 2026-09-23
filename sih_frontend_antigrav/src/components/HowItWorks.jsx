import { useState } from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, Search, ShieldCheck, FileCheck } from 'lucide-react';
import { steps } from '../data/content';
import ayurved1Img from '../assets/ayurved1.png';
import './HowItWorks.css';

const iconMap = { MessageSquare, Search, ShieldCheck, FileCheck };

export default function HowItWorks() {
  const [activeStep, setActiveStep] = useState(0);

  return (
    <section id="how-it-works" className="section how-section">
      <div className="container">
        {/* Header */}
        <motion.div
          className="how-section__header"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        >
          <span className="section-label">Process</span>
          <h2 className="section-heading">From question to responsible answer.</h2>
          <p className="section-subheading">
            A structured approach that combines Ayurvedic knowledge, retrieval,
            evidence awareness, and safety.
          </p>
        </motion.div>

        {/* Step flow */}
        <div className="how-section__flow">
          {/* Animated connecting line */}
          <div className="how-section__track" aria-hidden="true">
            <motion.div
              className="how-section__track-fill"
              initial={{ scaleX: 0 }}
              whileInView={{ scaleX: 1 }}
              viewport={{ once: true, margin: '-80px' }}
              transition={{ duration: 1.2, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
              style={{ originX: 0 }}
            />
          </div>

          {steps.map((step, i) => {
            const Icon = iconMap[step.icon];
            const isActive = i === activeStep;
            return (
              <motion.div
                key={step.number}
                className={`how-step${isActive ? ' how-step--active' : ''}`}
                initial={{ opacity: 0, y: 32 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-40px' }}
                transition={{ duration: 0.65, delay: 0.15 + i * 0.12, ease: [0.16, 1, 0.3, 1] }}
                onClick={() => setActiveStep(i)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && setActiveStep(i)}
                aria-pressed={isActive}
              >
                {/* Icon circle */}
                <div className="how-step__icon-wrap">
                  <div className="how-step__icon">
                    {Icon && <Icon size={20} strokeWidth={1.6} />}
                  </div>
                  <span className="how-step__number">{step.number}</span>
                </div>

                <h3 className="how-step__title">{step.title}</h3>
                <p className="how-step__desc">{step.description}</p>

                {/* Connector arrow (not on last) */}
                {i < steps.length - 1 && (
                  <span className="how-step__arrow" aria-hidden="true">→</span>
                )}
              </motion.div>
            );
          })}
        </div>

        {/* Step showcase with active detail and ayurved1 visual */}
        <div className="how-section__showcase">
          <motion.div
            className="how-section__detail"
            key={activeStep}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
            aria-live="polite"
          >
            <div className="how-section__detail-header">
              <span className="how-section__detail-num">{steps[activeStep].number}</span>
              <span className="how-section__detail-title">{steps[activeStep].title}</span>
            </div>
            <p className="how-section__detail-desc">{steps[activeStep].description}</p>
            <div className="how-section__detail-tags">
              <span className="how-tag">Classical Verification</span>
              <span className="how-tag">Trusted Herbology</span>
            </div>
          </motion.div>

          <motion.div
            className="how-section__visual-card"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="how-section__visual-media">
              <img
                src={ayurved1Img}
                alt="Ayurvedic herbs and formulations knowledge illustration"
                className="how-section__visual-img"
              />
            </div>
            <div className="how-section__visual-info">
              <span className="how-section__visual-badge">AyurX Knowledge Index</span>
              <h4 className="how-section__visual-title">Classical Ayurvedic Herb & Compound Corpus</h4>
              <p className="how-section__visual-desc">
                Every query cross-references authoritative classical Ayurvedic treatises and modern botanical pharmacopoeias for accurate botanical identification and preparation standards.
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
