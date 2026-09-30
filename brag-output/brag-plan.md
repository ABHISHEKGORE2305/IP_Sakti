# Brag Plan: IP-Sakti (आयुरX)

## What is this app?
A citation-grounded AI assistant for Ayurvedic IP and regulatory law — it classifies a formulation under Indian statute, routes the question to a specialist agent, and returns an answer where every claim carries the Act, section and page it came from.

## The angle
Most AI confidently invents the section number. This one shows its paperwork.
The whole video is one idea: *the citation is the product*. A question about patenting a classical
formulation goes in; a statute-anchored finding, verified sources and a formal case brief come out.
Nothing here is generic legal-tech — every line on screen is copy from this repo: the real suggestion
chip, the real wizard rail, the real Acts in the corpus, the real "Escalate to IP Facilitator" hand-off.

## Hook (first 2-3 seconds)
Gold serif on deep Ayurvedic green: **"Ask most AI about Section 3(p)."**
Beat. The line below resolves: **"It will invent one."** — the pain, stated flatly, in the product's own
domain vocabulary. Section 3(p) is the actual statutory bar this product exists to reason about.

## Key moments (the middle)
- The six-step rail drawing itself in: Jurisdiction → Classification → Issue Routing → Analysis → Sources → Action Plan.
- The real question typing into the composer: *"Can I patent a formulation I prepared exactly as described in a classical Samhita text?"* with the 🇮🇳 India and Startup / MSME chips lit.
- The answer card resolving with bolded statutory labels, then three source chips arriving one by one — Patents Act 1970 s.3(p), Biological Diversity Act 2002, TKDL Guidelines — each with a page number.
- The case brief PDF sliding up under "Escalate to IP Facilitator".

## Outro / punchline
**"Every answer, with its receipts."** Wordmark आयुरX · IP-Sakti, and the quiet line
*28 statutes indexed. 1,440 provisions. Every answer cites them.*

## User flow worth showing
Entry → key action → result, exactly as the app runs it:
1. **Entry** — pick jurisdiction (India) and persona (Startup / MSME) on Step 1.
2. **Key action** — type the question into the composer; the pipeline reports what it's doing ("Retrieving relevant patent, TK, and ABS provisions…").
3. **Result** — a grounded finding with a confidence band, verified citations, and a one-click case brief PDF sent to an IP facilitator.

## Tone
- Preset: `polished`
- Creative direction: a quiet, authoritative legal-tech product film with Ayurvedic warmth — parchment, gold and deep green, not SaaS blue.
- Interpretation: fewer scenes, longer holds, restrained motion. Confidence comes from the specificity of the statutory text on screen, not from speed. Nothing flashes; things settle.

## Format: landscape — 1920x1080
## Duration: 21s target

## Visual identity (from the project)
- Background: `#0b1510` (`--bg-primary`), elevated surface `#111d14`
- Accent: `#2f9e6e` / `#4cc38f` (emerald, app shell) and `#b8963e` / `#c9a84c` (gold, brand)
- Text: `#f0ebe0` primary, `#c8bfa8` secondary, `#8a7d68` muted
- Display font: Cormorant Garamond (`--font-serif`), with Yatra One for the Devanagari wordmark
- Body font: Inter (`--font-sans`)
- Strongest visual element: the wizard progress rail plus the emerald-bordered answer/source cards on near-black green; the आयुरX wordmark with its gold cursive X.

## Share copy (draft)
Built IP-Sakti: ask it whether your Ayurvedic formulation is patentable and it answers with the Act, the section and the page — then hands you a case brief PDF.

## Audio direction
- Role: warm, restrained bed with sparse professional accents.
- Music: `happy-beats-business-moves-vol-9-by-ende-dot-app.mp3` (114.84 BPM) — warm and forward without being upbeat-startup.
- Music treatment: start at 0.0s, hold around 0.4 through the body, duck slightly under the typing scene, fade out over the final 1.2s so the last accent rings.
- Music cue guidance: preset read from `assets/music/cues/happy-beats-business-moves-vol-9-by-ende-dot-app.music-cues.json`. Target strong cues at **4.23s** (product reveal), **10.54s** (analysis resolves) and **12.65s**/**14.22s** region (source chips). Beat grid 0.52s apart — too fast for sequential *text*, so source chips snap to every other beat (~1.05s apart).
- Audio-reactive treatment: subtle; let music RMS breathe the emerald glow behind the answer card and the gold rim of the wordmark. No waveform, bars or particles.
- SFX posture: sparse. Key ticks under the typed question, a soft card sound per source chip, one dry announcement hit on the case brief landing.
- Audio-coupled moments: the typed question (keypress set), the three source chips (card sounds on the beat grid), the final PDF/wordmark landing (single impact).
- Restraint rule: no whooshes on every transition, no riser into the outro, nothing that makes a legal tool sound like a game trailer.

## Storyboard

### Scene 1 — The invented citation — 3.5s
Near-black green field. Gold serif line 1 settles: "Ask most AI about Section 3(p)." (holds ~1.3s). Line 2 resolves beneath in parchment: "It will invent one." (holds ~1.2s). No chrome, no UI. A single faint gold ring arc (the hero's mantra circle motif) breathes at low opacity behind the type.
Sequential/interaction: yes — two lines, one after the other, each held to its reading floor.
Audio intent: music enters low and warm; the second line lands with the bed already moving.
Audio-coupled idea: none — let the type be silent and confident.
Music: warm bed, entering.
Transition mood: soft crossfade → Scene 2

### Scene 2 — The product + the rail — 4.0s
आयुरX wordmark (Devanagari + cursive gold X) settles centre-left with "IP-Sakti" beneath it and the line "Citation-grounded Ayurveda IPR intelligence." To its right, the six-step rail draws in: Jurisdiction · Classification · Issue Routing · Analysis · Sources · Action Plan — pips connecting left to right, emerald.
Sequential/interaction: yes — six rail pips arrive along the beat grid (non-text-critical, so they may hit consecutive beats); labels are already present, only the pips animate.
Audio intent: arrival — the bed opens up on the reveal.
Audio-coupled idea: reveal beat-locked to the 4.23s strong cue.
Music: bed, full.
Transition mood: clean wipe → Scene 3

### Scene 3 — The real question — 5.0s
The app composer, recreated: the 🇮🇳 India chip and the Startup / MSME persona chip lit emerald at the top. The question types into the field character by character: "Can I patent a formulation I prepared exactly as described in a classical Samhita text?" On completion the send button pulses once and the process line replaces it: "Retrieving relevant patent, TK, and ABS provisions…"
Sequential/interaction: yes — simulated typing, then a simulated send, then the process line.
Audio intent: intimate, working; music ducks a touch so the keys read.
Audio-coupled idea: randomized keypress ticks under the typing; one soft interface click on send.
Music: bed, ducked ~0.3.
Transition mood: soft crossfade → Scene 4

### Scene 4 — The grounded answer — 5.5s
The answer card resolves on emerald-bordered dark surface, with the product's real bolded-label format:
**Regime**: Patent & Traditional Knowledge · **Finding**: Section 3(p) bars inventions that are, in effect, traditional knowledge. Below it, three source chips arrive one by one, every other beat: "Patents Act, 1970 — s.3(p), p.12" · "Biological Diversity Act, 2002 — s.6" · "TKDL Guidelines". A small emerald pill reads "Citations verified 3/3" and the confidence band sits beside it.
Sequential/interaction: yes — three source chips, beat-grid snapped at ~1.05s spacing so each is readable.
Audio intent: the payoff; the bed lifts, each chip gets a soft card sound.
Audio-coupled idea: chips on the beat grid from the 12.65s strong cue; subtle RMS-driven glow on the card border.
Music: bed, full.
Transition mood: soft slide → Scene 5

### Scene 5 — The brief, and the line — 3.0s
The case brief PDF page slides up — letterhead "AYURVEDA IPR CASE BRIEF", the gold rule, section headings ghosted beneath — under the label "Escalate to IP Facilitator". It settles, then the frame resolves to the wordmark and the closing line: "Every answer, with its receipts." with "28 statutes indexed. 1,440 provisions." small beneath.
Sequential/interaction: yes — document lands, then the closing line.
Audio intent: resolution; one dry impact on the document landing, then the bed fades out under the final line.
Audio-coupled idea: single announcement/impact hit on the PDF landing; music fade across the last 1.2s.
Music: bed → fade out.
Transition mood: hold to end.

**Music mood for this video:** warm, professional, restrained — forward motion without startup-hype energy.
**Audio summary:** A low warm bed enters under the problem, opens on the product reveal, ducks for the typing, lifts through the citation payoff, and fades out under the closing line so the final document hit rings alone.

**Duration check:** 3.5 + 4.0 + 5.0 + 5.5 + 3.0 = **21.0s** ✓ (15–25s)

## Honesty notes
- No accuracy or "zero hallucination" claim appears on screen. The repo's own benchmark (`benchmark_results/postfix_verification_report.md`) reports 26.5% PASS on a 49-case sample, so the video claims only what the system demonstrably does: it cites, and it verifies citations against the retrieved source.
- "28 statutes indexed. 1,440 provisions." comes from `docs/ayurx_demo_production_master.md` (28 authoritative documents, 1,440+ indexed chunks).
- All names, questions and citations on screen are real product copy or real statutes. No user data, no credentials, no internal hostnames.
