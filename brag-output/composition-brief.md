# Hyperframes Composition Brief: IP-Sakti (आयुरX)

## Objective
Create a short launch-style brag video for IP-Sakti — a citation-grounded AI assistant for Ayurvedic IP and regulatory law.

## Output
- Composition directory: `brag-output/composition/`
- Rendered video: `brag-output/brag.mp4`
- Format: landscape — 1920x1080
- Duration: 21s

## Source Material
- Project root: `/Users/aspa/Desktop/abhishek/IP_Sakti`
- Primary files read: `sih_frontend_antigrav/src/index.css` (design tokens), `src/components/Hero.jsx` (wordmark, mantra ring), `src/lib/wizardConfig.js` (rail + persona + jurisdiction copy), `src/lib/suggestions.js` (the real question), `src/lib/caseBrief.js` (case brief letterhead), `src/agents/graph.py` (answer label format), `docs/ayurx_demo_production_master.md` (corpus scale)
- Product name: आयुरX · IP-Sakti
- Tagline / strongest claim: "Citation-grounded Ayurveda IPR intelligence" — every answer carries the Act, section and page.
- Key UI to recreate: the app composer with jurisdiction/persona chips, the six-step wizard rail, the emerald-bordered answer card with source chips, the case brief PDF letterhead.
- Copy that must appear verbatim:
  - "Ask most AI about Section 3(p)."
  - "It will invent one."
  - "Can I patent a formulation I prepared exactly as described in a classical Samhita text?"
  - "Retrieving relevant patent, TK, and ABS provisions…"
  - "Jurisdiction · Classification · Issue Routing · Analysis · Sources · Action Plan"
  - "Patents Act, 1970 — s.3(p), p.12" / "Biological Diversity Act, 2002 — s.6" / "TKDL Guidelines"
  - "Citations verified 3/3"
  - "AYURVEDA IPR CASE BRIEF" / "Escalate to IP Facilitator"
  - "Every answer, with its receipts."
  - "28 statutes indexed. 1,440 provisions."

## Creative Direction
- Tone preset: `polished`
- Creative direction: quiet, authoritative legal-tech product film with Ayurvedic warmth — parchment, gold and deep green, never SaaS blue.
- Interpretation: fewer scenes, longer holds, restrained motion; confidence comes from the specificity of statutory text on screen, not from speed. Things settle, nothing flashes.
- Angle: the citation is the product. A question about patenting a classical formulation goes in; a statute-anchored finding, verified sources and a formal case brief come out. Every line on screen is real copy from this repo.
- Hook: "Ask most AI about Section 3(p)." → "It will invent one."
- Outro: "Every answer, with its receipts."
- Avoid:
  - Generic SaaS language
  - Abstract filler visuals
  - Unrelated visual redesign
  - Any accuracy / "zero hallucination" claim (see Honesty notes in brag-plan.md)

## Visual Identity
- Background: `#0b1510`; elevated surface `#111d14`; card `rgba(15,28,18,0.85)`
- Text: `#f0ebe0` primary, `#c8bfa8` secondary, `#8a7d68` muted
- Accent: emerald `#2f9e6e` / `#4cc38f`; gold `#b8963e` / `#c9a84c`; border `rgba(47,158,110,0.32)` and `rgba(184,150,62,0.25)`
- Display font: Cormorant Garamond (Devanagari wordmark: Yatra One)
- Body font: Inter
- Visual references: the hero's concentric gold mantra rings (faint, background only), the wizard progress rail, emerald-bordered cards, the gold rule under the case brief letterhead.

## Storyboard
Use the storyboard in `brag-output/brag-plan.md` as the creative contract.

Scene summary:
1. The invented citation — 3.5s — two gold/parchment lines, faint gold ring behind.
2. The product + the rail — 4.0s — आयुरX wordmark, "IP-Sakti", tagline, six-step rail drawing in.
3. The real question — 5.0s — composer with India + Startup/MSME chips, question types out, process line replaces send.
4. The grounded answer — 5.5s — answer card with bolded statutory labels, three source chips one by one, "Citations verified 3/3".
5. The brief, and the line — 3.0s — case brief PDF lands under "Escalate to IP Facilitator", resolve to wordmark + "Every answer, with its receipts."

## Audio
- Audio role: warm restrained bed with sparse professional accents.
- Audio arc: enters low under the problem, opens on the product reveal, ducks for the typing, lifts through the citation payoff, fades out under the closing line.
- Music: `assets/music/happy-beats-business-moves-vol-9-by-ende-dot-app.mp3` (114.84 BPM)
- Music treatment: from 0.0s, ~0.4 body volume, duck to ~0.3 during scene 3, fade out across the final 1.2s.
- Music cue guidance: preset at `<skill-dir>/assets/music/cues/happy-beats-business-moves-vol-9-by-ende-dot-app.music-cues.json`. Strong cues to target: 4.23s (product reveal), 10.54s (analysis resolves), 12.65s (first source chip). Beat grid is 0.52s — snap source-chip TEXT to every other beat (~1.05s), not every beat.
- Audio-reactive treatment: subtle — music RMS breathes the emerald glow behind the answer card and the gold rim of the wordmark. No waveform, bars, notes or particles.
- Audio-coupled moments:
  - Scene 3 typing — randomized keypress ticks from the `keyboard/` set; one soft interface click on send.
  - Scene 4 source chips — card sound per chip, fired at the same timestamp as the visual.
  - Scene 5 PDF landing — one dry announcement/impact hit, allowed to ring as music fades.
- SFX selection guidance: sound follows motion. Sparse and dry; nothing rising, nothing whooshing between every scene. This is a legal tool, not a game trailer.
- SFX analysis guidance: read `<skill-dir>/assets/sfx/sfx-analysis.md`; prefer low high-frequency-risk files for the repeated chip sounds.
- Exact SFX choice: Hyperframes chooses filenames, timestamps, density and volume based on the implemented animation.
- Audio files: copy the chosen music and SFX into `brag-output/composition/assets/`.

## Hyperframes Instructions
Load `hyperframes-core`, `hyperframes-animation`, `hyperframes-creative`, `hyperframes-keyframes`, `hyperframes-cli`. This is the /brag workflow — do not enter the `hyperframes` entry-point intent interview or the generic promo / launch-video workflow. Prefer native Hyperframes conventions.

Requirements:
- Show real UI, copy and visual elements from the source project (see the verbatim copy list).
- Keep all text readable: short labels ≥0.8s settled, sentences ≥0.3s/word. The hook lines get the most.
- Total duration 15–25s (target 21s).
- Include the music and SFX layer as described.
- Treat audio notes as guidance; choose SFX after the animation exists.
- Lock 1–3 major reveals to strong cues (±0.15s), mark `// beat-locked`. Snap the source chips to every other beat (±0.10s), mark `// beat-grid`.
- Wire at least one visual to per-frame audio data (subtle), or document why extraction was skipped.
- Use local assets only; no absolute paths.
- Run `hyperframes check` before render — the single gate.
