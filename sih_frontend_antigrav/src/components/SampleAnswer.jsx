// src/components/SampleAnswer.jsx
import { useState } from 'react';
import { motion } from 'framer-motion';
import { BookOpen, ShieldCheck, BarChart2, FileText, ChevronDown } from 'lucide-react';
import './SampleAnswer.css';

const badges = [
  {
    icon: BookOpen,
    label: 'Traditional Use',
    value: 'Ayurvedic sources',
    color: '#4a7c3f',
  },
  {
    icon: BarChart2,
    label: 'Evidence',
    value: 'Varies by outcome',
    color: '#8b6030',
  },
  {
    icon: ShieldCheck,
    label: 'Safety',
    value: 'Precautions may apply',
    color: '#6b3030',
  },
  {
    icon: FileText,
    label: 'Sources',
    value: '4 verified references',
    color: '#2a5070',
  },
];

export default function SampleAnswer() {
  const [sourcesOpen, setSourcesOpen] = useState(false);

  return (
    <section id="sample-answer" className="section sample-section">
      <div className="container">
        {/* Header */}
        <motion.div
          className="sample-section__header"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-80px' }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        >
          <span className="section-label">Sample Interface</span>
          <h2 className="section-heading">See how AyurX answers differently.</h2>
        </motion.div>

        {/* Chat window */}
        <motion.div
          className="sample-window"
          initial={{ opacity: 0, y: 32 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-60px' }}
          transition={{ duration: 0.85, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
        >
          {/* Window chrome */}
          <div className="sample-window__chrome">
            <div className="sample-window__dots">
              <span /><span /><span />
            </div>
            <span className="sample-window__title">AyurX — Knowledge Interface</span>
          </div>

          {/* Body */}
          <div className="sample-window__body">
            {/* User message */}
            <div className="sample-msg sample-msg--user">
              <div className="sample-msg__bubble sample-msg__bubble--user">
                What is Ashwagandha traditionally used for?
              </div>
              <div className="sample-msg__avatar sample-msg__avatar--user">U</div>
            </div>

            {/* AI response */}
            <div className="sample-msg sample-msg--ai">
              <div className="sample-msg__avatar sample-msg__avatar--ai">
                <span className="logo-devanagari" style={{ fontSize: '0.8rem' }}>आयुर</span>
                <span className="logo-x" style={{ fontSize: '1.1rem', top: '2px', position: 'relative' }}>X</span>
              </div>

              <div className="sample-response">
                {/* Herb header */}
                <div className="sample-response__herb">
                  <div>
                    <h3 className="sample-response__herb-name">Ashwagandha</h3>
                    <p className="sample-response__herb-latin">Withania somnifera</p>
                  </div>
                  <div className="sample-response__herb-badge">Adaptogen</div>
                </div>

                {/* Response text */}
                <p className="sample-response__text">
                  Ashwagandha has a long history of use in Ayurveda for several
                  traditional purposes. It is classically described as a{' '}
                  <em>rasayana</em> — a rejuvenating substance — and has been used
                  in contexts relating to vitality, stamina, and general wellness.
                  Modern research has investigated potential effects in areas such
                  as stress and sleep, but the strength of evidence varies
                  depending on the specific outcome and study.
                </p>

                {/* Badges */}
                <div className="sample-response__badges">
                  {badges.map((b) => {
                    const Icon = b.icon;
                    return (
                      <div
                        key={b.label}
                        className="sample-badge"
                        style={{ '--badge-color': b.color }}
                      >
                        <Icon size={13} strokeWidth={1.8} />
                        <div>
                          <span className="sample-badge__label">{b.label}</span>
                          <span className="sample-badge__value">{b.value}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* View sources */}
                <button
                  className="sample-response__sources-btn"
                  onClick={() => setSourcesOpen((v) => !v)}
                  aria-expanded={sourcesOpen}
                >
                  View Sources
                  <ChevronDown
                    size={14}
                    style={{
                      transform: sourcesOpen ? 'rotate(180deg)' : 'none',
                      transition: 'transform 0.3s ease',
                    }}
                  />
                </button>

                {sourcesOpen && (
                  <motion.div
                    className="sample-response__sources"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    {[
                      'Charaka Samhita, Chikitsa Sthana 1.3 — Rasayana formulations',
                      'Ashtanga Hridayam — Dravyaguna Vijnana references',
                      'Chandrasekhar et al. (2012) — Randomised controlled trial on stress',
                      'Pratte et al. (2014) — Systematic review of Ashwagandha research',
                    ].map((src, i) => (
                      <div key={i} className="sample-source-item">
                        <span className="sample-source-item__num">{i + 1}</span>
                        <span>{src}</span>
                      </div>
                    ))}
                  </motion.div>
                )}

                {/* Disclaimer */}
                <p className="sample-response__disclaimer">
                  This response is for educational purposes only. Consult a
                  qualified Ayurvedic practitioner or healthcare professional for
                  personal guidance.
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
