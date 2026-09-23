// src/components/Testimonials.jsx
import { motion } from 'framer-motion';
import { testimonials } from '../data/content';
import ayurvedicRefImg from '../assets/ayurvedic-reference.jpg';
import './Testimonials.css';

export default function Testimonials() {
  return (
    <section id="testimonials" className="section testimonials-section">
      <div className="container">
        <motion.div
          className="testimonials-section__header"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        >
          <span className="section-label">Feedback</span>
          <h2 className="section-heading">
            Built to make Ayurvedic knowledge easier to understand.
          </h2>
        </motion.div>

        {/* Featured Ayurvedic Environment Banner */}
        <motion.div
          className="testimonials-feature"
          initial={{ opacity: 0, y: 28 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-40px' }}
          transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="testimonials-feature__img-wrap">
            <img
              src={ayurvedicRefImg}
              alt="Traditional Ayurvedic medicine bottles, herbal poultices and incense"
              className="testimonials-feature__img"
            />
          </div>
          <div className="testimonials-feature__content">
            <span className="testimonials-feature__badge">Clinical & Classical Feedback</span>
            <h3 className="testimonials-feature__title">
              Designed in conversation with traditional vaidyas & modern wellness seekers
            </h3>
            <p className="testimonials-feature__desc">
              From individual herbs like Ashwagandha and Brahmi to complex classical formulations, our feedback loop ensures that ancient wisdom is respected while answering contemporary health queries clearly.
            </p>
          </div>
        </motion.div>

        {/* Testimonial Cards Grid */}
        <div className="testimonials-grid">
          {testimonials.map((t, i) => (
            <motion.div
              key={i}
              className="testimonial-card"
              initial={{ opacity: 0, y: 32 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-40px' }}
              transition={{ duration: 0.7, delay: i * 0.12, ease: [0.16, 1, 0.3, 1] }}
              whileHover={{ y: -4 }}
            >
              {/* Quote mark */}
              <span className="testimonial-card__quote-mark" aria-hidden="true">"</span>

              <p className="testimonial-card__quote">{t.quote}</p>

              <div className="testimonial-card__footer">
                <div className="testimonial-card__avatar" aria-hidden="true">
                  {t.label.charAt(0)}
                </div>
                <div>
                  <span className="testimonial-card__name">{t.label}</span>
                  <span className="testimonial-card__role">{t.role}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Prototype note */}
        <motion.p
          className="testimonials-section__note"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.5 }}
        >
          * These are prototype demonstration responses, not verified user testimonials.
        </motion.p>
      </div>
    </section>
  );
}
