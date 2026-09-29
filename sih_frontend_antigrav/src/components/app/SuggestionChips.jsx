// Tappable starter suggestions shown under a free-text input.
//
// Rendered only while the field is empty: once there is text in the box, a
// tap would overwrite what the user wrote, so the chips get out of the way
// instead. Clearing the field brings them back.

import './SuggestionChips.css';

export default function SuggestionChips({ items, value, onSelect, label = 'Try one of these' }) {
  if (!items || items.length === 0) return null;
  if ((value || '').trim()) return null;

  return (
    <div className="suggestion-chips">
      <span className="suggestion-chips__label">{label}</span>
      <div className="suggestion-chips__row">
        {items.map((item) => {
          const text = typeof item === 'string' ? item : item.value;
          const chipLabel = typeof item === 'string' ? item : item.label;
          return (
            <button
              type="button"
              key={text}
              className="suggestion-chips__chip"
              onClick={() => onSelect(text)}
              title={text}
            >
              {chipLabel}
            </button>
          );
        })}
      </div>
    </div>
  );
}
