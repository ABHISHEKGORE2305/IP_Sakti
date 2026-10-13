// src/components/AvailabilityNotice.jsx
import { useEffect, useRef, useState } from 'react';
import { Clock, X } from 'lucide-react';
import './AvailabilityNotice.css';

export default function AvailabilityNotice() {
  const [isOpen, setIsOpen] = useState(true);
  const closeButtonRef = useRef(null);

  // Focus the close button on mount for keyboard users,
  // lock background scroll, and support Escape to dismiss.
  useEffect(() => {
    if (!isOpen) return;
    closeButtonRef.current?.focus({ preventScroll: true });

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    const onKeyDown = (e) => {
      if (e.key === 'Escape') setIsOpen(false);
    };
    window.addEventListener('keydown', onKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener('keydown', onKeyDown);
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const close = () => setIsOpen(false);

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) close();
  };

  return (
    <div
      className="avail-overlay"
      onClick={handleBackdropClick}
      data-testid="availability-notice-overlay"
    >
      <div
        className="avail-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="avail-notice-title"
        aria-describedby="avail-notice-desc"
      >
        <button
          ref={closeButtonRef}
          type="button"
          className="avail-close"
          aria-label="Dismiss availability notice"
          onClick={close}
        >
          <X size={18} aria-hidden="true" />
        </button>

        <p className="avail-eyebrow">Availability</p>
        <h2 id="avail-notice-title" className="avail-title">
          A Quick Note on Availability
        </h2>

        <div id="avail-notice-desc" className="avail-body">
          <p>
            We&rsquo;re a student team building and maintaining this project with
            limited deployment resources. Since our AI agent requires significant
            computational resources, our backend is available daily from{' '}
            <strong>12:00 PM to 9:00 PM IST</strong>.
          </p>
          <p>
            If you&rsquo;re visiting outside these hours, some features may be
            temporarily unavailable. We appreciate your patience and support as we
            continue improving the platform.
          </p>
        </div>

        <div className="avail-schedule" aria-label="Backend availability schedule">
          <Clock size={16} aria-hidden="true" className="avail-schedule__icon" />
          <span>
            Daily, <strong>12:00 PM &ndash; 9:00 PM IST</strong>
          </span>
        </div>

        <div className="avail-footer">
          <span className="avail-thanks">Thank you for your understanding!</span>
          <button type="button" className="btn-primary avail-cta" onClick={close}>
            Got it
          </button>
        </div>
      </div>
    </div>
  );
}
