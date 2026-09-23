// src/components/Hero.jsx
import { motion } from 'framer-motion';
import { ShieldCheck, BarChart2, FileCheck } from 'lucide-react';
import ayurveda2Img from '../assets/ayurveda2.png';
import './Hero.css';

export default function Hero() {
  const handleScrollClick = (e) => {
    e.preventDefault();
    window.location.href = '/auth';
  };

  return (
    <section id="home" className="hero" aria-label="AyurX Hero">
      <div className="hero__split">
        {/* ── LEFT HALF: Dark green with rotating Sanskrit Mantra animation ── */}
        <div className="hero__left">
          {/* Animated Sanskrit Mantra Circle in transparent red */}
          <div className="hero__mantra-container" aria-hidden="true">
            <svg
              viewBox="0 0 600 600"
              className="hero__mantra-svg"
              xmlns="http://www.w3.org/2000/svg"
            >
              <defs>
                {/* Outer mantra path */}
                <path
                  id="mantraPathOuter"
                  d="M 300, 300 m -240, 0 a 240,240 0 1,1 480,0 a 240,240 0 1,1 -480,0"
                  fill="none"
                />
                {/* Middle shloka path */}
                <path
                  id="mantraPathMid"
                  d="M 300, 300 m -185, 0 a 185,185 0 1,1 370,0 a 185,185 0 1,1 -370,0"
                  fill="none"
                />
                {/* Inner aphorism path */}
                <path
                  id="mantraPathInner"
                  d="M 300, 300 m -132, 0 a 132,132 0 1,1 264,0 a 132,132 0 1,1 -264,0"
                  fill="none"
                />
              </defs>

              {/* Concentric gold guideline rings - subtle and calm */}
              <circle
                cx="300"
                cy="300"
                r="254"
                stroke="rgba(199, 164, 90, 0.15)"
                strokeWidth="0.8"
                strokeDasharray="4 6"
                fill="none"
              />
              <circle
                cx="300"
                cy="300"
                r="238"
                stroke="rgba(199, 164, 90, 0.22)"
                strokeWidth="1"
                fill="none"
              />
              <circle
                cx="300"
                cy="300"
                r="185"
                stroke="rgba(199, 164, 90, 0.18)"
                strokeWidth="0.8"
                fill="none"
              />
              <circle
                cx="300"
                cy="300"
                r="132"
                stroke="rgba(199, 164, 90, 0.15)"
                strokeWidth="0.8"
                strokeDasharray="3 5"
                fill="none"
              />
              <circle
                cx="300"
                cy="300"
                r="78"
                stroke="rgba(199, 164, 90, 0.12)"
                strokeWidth="0.8"
                fill="none"
              />
              {/* Center: subtle Om symbol */}
              <text
                x="300"
                y="314"
                textAnchor="middle"
                fontFamily="'Rozha One', serif"
                fontSize="28"
                fill="rgba(199, 164, 90, 0.2)"
                style={{ userSelect: 'none' }}
              >
                ॐ
              </text>


              {/* Complete Outer Sanskrit Devanagari Mantra Ring (Full 360° Loop) */}
              <text className="hero__mantra-text-outer" fill="rgba(199, 164, 90, 0.35)">
                <textPath href="#mantraPathOuter" startOffset="0%" textLength="1507" lengthAdjust="spacing">
                  ॐ भूर्भुवः स्वः तत्सवितुर्वरेण्यं भर्गो देवस्य धीमहि धियो यो नः प्रचोदयात् ॥ ॐ त्र्यम्बकं यजामहे सुगन्धिं पुष्टिवर्धनम् उर्वारुकमिव बन्धनान् मृत्योर्मुक्षीय मामृतात् ॥ ॐ भूर्भुवः स्वः तत्सवितुर्वरेण्यं भर्गो देवस्य धीमहि धियो यो नः प्रचोदयात् ॥
                </textPath>
              </text>

              {/* Complete Middle Sanskrit Shloka Ring (Full 360° Loop) */}
              <text className="hero__mantra-text-mid" fill="rgba(199, 164, 90, 0.3)">
                <textPath href="#mantraPathMid" startOffset="0%" textLength="1162" lengthAdjust="spacing">
                  शरीरेन्द्रियसत्त्वात्मसंयोगो धारि जीवितम् । नित्यगश्चानुबन्धश्च पर्यायैरायुरुच्यते ॥ ॐ सर्वे भवन्तु सुखिनः सर्वे सन्तु निरामयाः । ॐ शान्तिः ॥ शरीरेन्द्रियसत्त्वात्मसंयोगो धारि जीवितम् ॥
                </textPath>
              </text>

              {/* Complete Inner Aphorism Ring (Full 360° Loop) */}
              <text className="hero__mantra-text-inner" fill="rgba(199, 164, 90, 0.25)">
                <textPath href="#mantraPathInner" startOffset="0%" textLength="829" lengthAdjust="spacing">
                  touch of the earth • ancient wisdom for healthy life • harmony of nature & body • ayurveda • touch of the earth • ancient wisdom •
                </textPath>
              </text>
            </svg>
          </div>

          {/* Centered Brand Content */}
          <div className="hero__left-content">
            <motion.div
              className="hero__technical-label"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            >
              AI-POWERED AYURVEDIC KNOWLEDGE
            </motion.div>

            {/* Logo: "आयुरX" with enlarged, attractive typography and flowy cursive X */}
            <motion.div
              className="hero__brand-wordmark"
              initial={{ opacity: 0, scale: 0.94 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.85, ease: [0.16, 1, 0.3, 1] }}
              aria-label="आयुरX"
            >
              <span className="hero__brand-devanagari">आयुर</span>
              <span className="hero__brand-x">X</span>
            </motion.div>

            {/* Tagline */}
            <motion.p
              className="hero__tagline"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            >
              “Evidence-based Ayurveda, powered by AI.”
            </motion.p>

            {/* CTA Button */}
            <motion.div
              className="hero__cta-wrapper"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.35, ease: [0.16, 1, 0.3, 1] }}
            >
              <a
                href="/auth"
                className="hero__cta-btn"
                onClick={handleScrollClick}
              >
                GET STARTED <span className="hero__cta-arrow">→</span>
              </a>
            </motion.div>

            {/* Trust Indicators */}
            <motion.div
              className="hero__trust-indicators"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.45, ease: [0.16, 1, 0.3, 1] }}
            >
              <span className="hero__trust-item"><ShieldCheck size={14} /> Source-backed</span>
              <span className="hero__trust-item"><BarChart2 size={14} /> Evidence-aware</span>
              <span className="hero__trust-item"><FileCheck size={14} /> Safety-first</span>
            </motion.div>
          </div>
        </div>

        {/* ── RIGHT HALF: ayurveda2.png image (moved 20% right, 15% transparent) ── */}
        <div className="hero__right">
          <img
            src={ayurveda2Img}
            alt="Ayurvedic ancient manuscripts, mortar, singing bowl and herbs"
            className="hero__right-img"
          />
          <div className="hero__right-edge-fade" aria-hidden="true" />
        </div>
      </div>
    </section>
  );
}
