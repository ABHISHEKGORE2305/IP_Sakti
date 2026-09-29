# AyurX (IP-SAKTI Sahayak) — Master Demo Video Production Package & Technical Audit

**Project:** AyurX / IP-SAKTI Sahayak  
**Problem Statement ID:** 26045 (Smart India Hackathon 2026)  
**Document Type:** Technical Audit, Demo Architecture, Script, Storyboard & Video Production Master  
**Target Video Duration:** 3 Minutes 15 Seconds (195 Seconds)  
**Resolution / Aspect Ratio:** 1080p Full HD (1920x1080), 16:9, 60fps  
**Audio Style:** Clear, authoritative Indian-English professional narration (145–155 wpm)  

---

## A. PRODUCT UNDERSTANDING

### 1. The Core Problem
India possesses over 5,000 years of documented Ayurvedic wisdom across classical treatises (*Charaka Samhita*, *Sushruta Samhita*, *Ashtanga Hridaya*, *Sharangdhara Samhita*, *Ayurvedic Formulary of India*). Today, thousands of Ayurvedic researchers, startups, MSMEs, and Vaidyas are innovating novel formulations. However, commercializing an Ayurvedic formulation requires navigating four fiercely conflicting, fragmented regulatory and legal regimes:
1. **Indian Patent Law (Patents Act, 1970)**: Section 3(p) bars inventions that are traditional knowledge (TK) or mere duplications of known properties. Section 3(e) bars mere admixtures lacking synergy. Section 3(d) requires proven enhancement of therapeutic efficacy.
2. **Biodiversity & ABS (Biological Diversity Act, 2002 / 2023 Amendment)**: Accessing wild biological resources for commercial utilization mandates prior intimation to State Biodiversity Boards (SBB), Access and Benefit Sharing (ABS) levies (0.1%–0.5% ex-factory sales), and National Biodiversity Authority (NBA) approval (Form III) before patent grant.
3. **Domestic Drug & Food Regulation**: The razor-thin line between a Classical Ayurvedic Medicine (D&C Act 1940 Sec 3(a), Form 24D), a Patent & Proprietary Medicine (D&C Act Sec 3(h)), a Phytopharmaceutical (NDCT Rules 2019), and an Ayurveda-Aahar (FSSAI Regulations 2022).
4. **International Market Access**: Strict divergence across global borders (US FDA DSHEA dietary supplement rules vs Botanical Drug IND; EU Traditional Herbal Medicinal Products Directive 2004/24/EC requiring 30-year evidence).

Generic LLMs (like standard ChatGPT) hallucinate statutory sections, conflate US and Indian patent provisions, miss mandatory NBA filings, and cannot verify whether a citation actually exists in the Gazette.

### 2. The Primary Users
* **Ayurvedic Researchers & Formulators**: Developing modified botanical extracts or novel delivery systems.
* **Ayush Startups & MSMEs**: Seeking patent protection and regulatory licenses without incurring ₹10L+ in exploratory legal advisory fees.
* **Traditional Vaidyas & Healers**: Needing plain-language, regional-language guidance on compliance and rights.
* **IP Attorneys & Patent Agents**: Requiring structured, citation-grounded case briefs to accelerate filing analysis.

### 3. The AyurX Solution
AyurX (IP-SAKTI Sahayak) is an AI-powered legal and regulatory intelligence platform that ingests the authoritative legal corpus, classifies formulations through deterministic statutory trees, routes issues across specialized agents, generates citation-grounded legal verdicts with zero-hallucination verification, builds interactive knowledge graphs, maps IP filing strategies, and outputs formal case briefs ready for IP facilitators.

### 4. Technical Architecture & RAG Pipeline
* **Corpus & Ingestion**: 28 authoritative legal and pharmacopoeial documents (Patents Act 1970, Patents Amendment Rules 2024, Biological Diversity Act 2002/2023, BD Rules 2024, D&C Act 1940, FSSAI Ayurveda Aahar Regulations 2022, TKDL guidelines, WIPO GRATK Treaty 2024). Ingested via PyMuPDF with legal-aware semantic chunking preserving Act, Chapter, Section, Rule, and Page metadata (1,440+ indexed chunks).
* **Dual Retrieval & Hybrid Fusion**: Dense vector search via `BAAI/bge-m3` embeddings combined with BM25 sparse keyword search in Qdrant vector database (`ayurvedic_ip_corpus`), merged using Reciprocal Rank Fusion (RRF).
* **Reranking & Authority Weighting**: Cross-encoder reranking combined with authority weights (Primary Acts = 1.0, Rules/Regulations = 0.9, Official Guidelines = 0.8, International Treaties = 0.7).
* **Multi-Agent Supervisory Orchestration**: LangGraph-based stateful graph with supervisory intent classification routing queries to specialized agents (`patent_agent`, `abs_agent`, `reg_agent`, `tm_gi_agent`, `intl_agent`).
* **Deterministic Legal Engines**:
  * *Classifier Engine*: Statutory decision tree under D&C Act Sec 3(a)/3(h) and FSSAI 2022.
  * *IP Route Planner Engine*: Evaluates multi-regime viability (Patents, Trademarks, GIs, Trade Secrets, PPV&FR).
  * *Knowledge Graph Engine*: Derives multi-hop relationships (Product → Ingredient → Biological Resource → Classification → Regulatory Authority).
  * *Law Version Comparator*: Retrieval-scoped dual-query engine comparing statutory versions (e.g. Patent Rules 2003 vs 2024).
  * *Citation Verifier*: NLI entailment check validating that every inline claim matches retrieved source chunks.

---

## B. VERIFIED FEATURE INVENTORY

| Feature / Capability | Implementation Status | Live Evidence in Running App | Demoable? |
| :--- | :--- | :--- | :--- |
| **Multi-Agent RAG Pipeline** | 🟢 **VERIFIED LIVE** | `POST /api/agent` returns structured multi-part legal analysis with statutory citations via Groq/Gemini. | **YES (Hero)** |
| **Conversational RAG Chat** | 🟢 **VERIFIED LIVE** | `POST /api/chat/` powers multi-turn chat with animated word-by-word process indicator and collapsible sources. | **YES** |
| **Deterministic Product Classifier** | 🟢 **VERIFIED LIVE** | `StepClassification.jsx` executes D&C Act Section 3(a)/3(h) decision tree; verified live response. | **YES (Hero)** |
| **Citation Verifier & Inspector** | 🟢 **VERIFIED LIVE** | `StepSources.jsx` renders verified-vs-total badge (`5/5 verified`), authority weights, reranker scores, and page snippets. | **YES (Hero)** |
| **Interactive Knowledge Graph** | 🟢 **VERIFIED LIVE** | `KnowledgeGraphExplorer.jsx` builds and renders dynamic SVG multi-hop entity graphs from `POST /api/knowledge-graph`. | **YES (Hero)** |
| **IP Route Planner** | 🟢 **VERIFIED LIVE** | `IPRoutePlanner.jsx` displays color-coded strategy cards (Available, Conditional, Barred) via `POST /api/ip-route-plan`. | **YES (Hero)** |
| **Law Version Timeline** | 🟢 **VERIFIED LIVE** | `LawVersionTimeline.jsx` runs document-scoped comparative queries (`POST /api/law-version-query`) comparing 2003 vs 2024 rules. | **YES (Differentiator)** |
| **Export Market Navigator** | 🟢 **VERIFIED LIVE** | `ExportMarketCards.jsx` retrieves grounded US FDA (Botanical Drug / DSHEA), EU THMPD, and UK MHRA rules. | **YES** |
| **Multilingual Legal Translation** | 🟢 **VERIFIED LIVE** | `POST /api/translate` translates complex verdicts into Hindi/Tamil while preserving English statutory citations. | **YES (Hero)** |
| **Voice Dictation (Speech-to-Text)** | 🟢 **VERIFIED LIVE** | `StepIssuePicker.jsx` integrates browser `SpeechRecognition` API (`Mic` button) dictating text directly into input. | **YES (Hero)** |
| **Text-to-Speech (Audio Readout)** | 🟢 **VERIFIED LIVE** | `StepAction.jsx` integrates browser `SpeechSynthesisUtterance` (`Listen` button) reading legal answers aloud. | **YES (Hero)** |
| **Multi-Format Case Brief Export** | 🟢 **VERIFIED LIVE** | `lib/caseBrief.js` provides one-click PDF (print CSS), Markdown (.md), and JSON (.json) exports. | **YES (Hero)** |
| **Dedicated ABS Checklist Export** | 🟢 **VERIFIED LIVE** | Separate PDF and Markdown exports for Biological Diversity Act / ABS compliance sheets. | **YES** |
| **Official Resource Links** | 🟢 **VERIFIED LIVE** | `GET /api/references` renders deep links to IP India, WIPO Patentscope, TKDL, and NBA portals. | **YES** |
| **DPDP Privacy & Audit Logging** | 🟢 **VERIFIED LIVE** | `PrivacyDashboard.jsx` fetches live session-scoped SQLite audit log and executes permanent erasure (`/api/privacy/delete`). | **YES** |
| **Golden Benchmark Dashboard** | 🟢 **VERIFIED LIVE** | `EvalDashboard.jsx` reads golden benchmark results showing **98% accuracy (49/50 passed)** across 10 legal categories. | **YES (Credibility)** |
| **Corpus Admin & PDF Staging** | 🟢 **VERIFIED LIVE** | `AdminCorpusPanel.jsx` lists 28 ingested documents (1,440+ chunks) and accepts PDF staging to `data/raw/`. | **YES** |
| **Dark / Light Theme Toggle** | 🟢 **VERIFIED LIVE** | Smooth glassmorphic palette toggle persisted in `localStorage`. | **YES** |
| **Jurisdiction Switcher** | 🟢 **VERIFIED LIVE** | Sidebar toggle between 🇮🇳 India, 🌍 International, and 🌐 Both, scoping retrieval filters. | **YES** |
| **Attorney Case Escalation** | 🟡 **PARTIAL / CONFIG** | `POST /api/escalate` is fully wired to SMTP; requires valid credentials in `.env` to transmit externally. | **Exclude or Mock** |
| **GCC & ASEAN Market Cards** | ⚪ **STATIC PLACEHOLDER** | Labeled explicitly as "Not yet in corpus" to prevent hallucinations. | **Mention as guardrail** |
| **Google OAuth Sign-In** | ⚪ **DISABLED PLACEHOLDER**| Button has `disabled` attribute with "Coming soon" tooltip. | **Exclude from video** |

---

## C. SELECTED DEMO STORY: THE HERO SCENARIO

### Title: "From Kitchen Lab to Global Market: Protecting a Novel Bio-Enhanced Ashwagandha Formulation"

* **User Persona**: **Dr. Aditi Sharma**, R&D Director at an Indian AYUSH Biotech Startup.
* **Her Innovation**: Her team developed a novel liposomal encapsulation of *Withania somnifera* (Ashwagandha) combined with a standardized *Piper longum* (Pippali) bio-enhancer that achieves **300% higher withanolide bioavailability** for osteoarthritis and chronic inflammation.
* **Her Critical Dilemma**:
  1. *Can she patent this in India without triggering Section 3(p) (traditional knowledge) or Section 3(e) (mere admixture)?*
  2. *What are her mandatory obligations under the Biological Diversity Act 2023 for sourcing wild Himalayan Ashwagandha?*
  3. *What regulatory manufacturing license applies under AYUSH / FSSAI?*
  4. *What is her export pathway into the United States?*
* **Why This Story Dominates**:
  It covers the full SIH problem lifecycle in 3 minutes: **Product Classification → Section 3(p)/3(e) RAG Analysis → Citation Verification → Knowledge Graph → IP Strategy → Voice & Regional Translation → Formal Case Brief Export**.

---

## D. FINAL VIDEO STRUCTURE (Timeline: 00:00 – 03:15)

```
00:00 ─── Hook & Fragmentation Problem (20s)
00:20 ─── Introduction to AyurX & Persona Selection (20s)
00:40 ─── Step 1 & 2: Statutory Product Classification (35s)
01:15 ─── Step 3 & 4: Multi-Regime Issue Routing & Real-Time RAG (35s)
01:50 ─── Step 5: Citation Inspector, Knowledge Graph & IP Planner (35s)
02:25 ─── Step 6: Multilingual Translation, Voice & Case Brief Export (25s)
02:50 ─── Differentiator: Law Version Timeline & Benchmark Evaluation (15s)
03:05 ─── Closing Impact & Vision (10s)
```

---

## E. FINAL VOICEOVER SCRIPT

```text
[00:00 - 00:20 | Hook & Problem]
"India’s Ayurvedic heritage spans over five thousand years. But for today's innovators, turning a traditional formulation into a patented, globally compliant product is a legal maze. Navigating the Patents Act, the Biological Diversity Act, AYUSH drug licensing, and foreign export rules means searching dozens of disconnected portals. Generic AI hallucinates sections. Traditional knowledge gets lost. Innovators get blocked."

[00:20 - 00:40 | Introduction to AyurX]
"Meet AyurX — the IP-SAKTI Sahayak. A source-grounded, multi-agent AI assistant designed specifically for Ayurvedic intellectual property and regulatory compliance. Built on a version-tracked corpus of Indian statutes, pharmacopoeias, and international treaties, AyurX bridges ancient wisdom with rigorous modern patent law."

[00:40 - 01:15 | Classification Engine]
"Let’s follow Dr. Aditi Sharma, an Ayush startup founder. Her team developed a liposomal extract of Ashwagandha and Pippali for joint inflammation. Instead of guessing legal categories, she starts with AyurX’s guided wizard. Selecting her persona as an R&D Startup, the platform initiates a deterministic statutory classification. Because her formulation alters the classical dosage form, AyurX instantly classifies it under Section 3(h) of the Drugs and Cosmetics Act as a Patent & Proprietary Medicine — mapping out her exact State Licensing Authority pathway and Form 24D requirements."

[01:15 - 01:50 | Multi-Regime RAG & Section 3(p)]
"Next, the Multi-Regime Issue Picker. Aditi wants to know: Is this patentable? Using built-in voice dictation, she asks: 'We modified a classical Ashwagandha formulation with a novel liposomal delivery system. Can we patent this in India?' 
AyurX’s supervisory agent immediately routes the query through hybrid dense-sparse retrieval across the Patents Act and TKDL prior art. Within seconds, it delivers a structured legal verdict: While raw Ashwagandha is barred under Section 3(p), her novel liposomal delivery process and synergistic bio-enhancement are eligible under Section 2(1)(j), provided comparative trial data proves enhanced therapeutic efficacy under Section 3(d)."

[01:50 - 02:25 | Trust, Knowledge Graph & IP Strategy]
"Here is where AyurX separates itself from every generic chatbot: Zero-hallucination source grounding. 
Every single claim is verified against retrieved chunks, displaying real authority scores and statutory citations. Below the verdict, the Relational Knowledge Graph automatically maps her formulation: linking Withania somnifera to its regulatory authority, its Section 3(p) TK risk, and her mandatory Form III filing with the National Biodiversity Authority before patent grant. Beside it, the IP Route Planner delivers an instant strategic matrix: Patenting is conditional on synergy, Trademark is available for brand protection in Class 5, and her proprietary liposomal process is secured as a Trade Secret."

[02:25 - 02:50 | Multilingual, Voice & Case Brief]
"AyurX empowers innovators in their native language. With one click, Aditi translates the entire analysis into Hindi — while preserving exact English statutory citations. She clicks 'Listen', and AyurX reads the legal brief aloud. Finally, she exports a comprehensive, print-ready Case Brief and ABS Compliance Checklist in PDF and Markdown — ready to hand directly to her patent attorney."

[02:50 - 03:05 | Differentiators & Live Benchmark]
"Need to compare law changes? AyurX’s Law Version Timeline runs dual retrieval to compare the Patents Rules 2003 against the 2024 Amendments. And transparency is verified live: our built-in Evaluation Dashboard tracks our golden benchmark — achieving a ninety-eight percent pass rate across fifty rigorous legal test cases."

[03:05 - 03:15 | Impact & Closing]
"From raw formulation to verified evidence to actionable legal strategy. AyurX turns fragmented Ayurvedic knowledge into an empowered, global innovation engine. Ancient wisdom. Smarter answers."
```

---

## F. FINAL SUBTITLE SCRIPT (.SRT FORMAT)

```srt
1
00:00:00,000 --> 00:00:04,500
India's Ayurvedic heritage spans over five thousand years.

2
00:00:04,500 --> 00:00:09,000
But for today's innovators, turning a traditional formulation into a patented,

3
00:00:09,000 --> 00:00:13,200
globally compliant product is a complex legal maze.

4
00:00:13,200 --> 00:00:16,800
Navigating the Patents Act, the Biological Diversity Act,

5
00:00:16,800 --> 00:00:20,500
AYUSH drug licensing, and foreign export rules means dozens of disconnected portals.

6
00:00:20,500 --> 00:00:24,800
Generic AI hallucinates sections. Traditional knowledge gets lost.

7
00:00:24,800 --> 00:00:29,200
Meet AyurX — the IP-SAKTI Sahayak.

8
00:00:29,200 --> 00:00:34,500
A source-grounded, multi-agent AI assistant for Ayurvedic IP and regulatory compliance.

9
00:00:34,500 --> 00:00:40,000
Built on a version-tracked corpus of Indian statutes, pharmacopoeias, and treaties.

10
00:00:40,000 --> 00:00:44,500
Let’s follow Dr. Aditi Sharma, an Ayush startup founder.

11
00:00:44,500 --> 00:00:49,500
Her team developed a novel liposomal extract of Ashwagandha and Pippali.

12
00:00:49,500 --> 00:00:54,500
Instead of guessing legal categories, she starts with AyurX's guided wizard.

13
00:00:54,500 --> 00:00:59,000
Selecting her persona as an R&D Startup, the platform initiates product classification.

14
00:00:59,000 --> 00:01:04,200
Because her formulation alters the classical dosage form, AyurX instantly classifies it

15
00:01:04,200 --> 00:01:09,500
under Section 3(h) of the Drugs & Cosmetics Act as a Patent & Proprietary Medicine.

16
00:01:09,500 --> 00:01:15,000
Mapping out her State Licensing Authority pathway and Form 24D requirements.

17
00:01:15,000 --> 00:01:19,000
Next: The Multi-Regime Issue Picker. Aditi asks: Is this patentable?

18
00:01:19,000 --> 00:01:24,000
Using built-in voice dictation, she speaks her formulation query directly into AyurX.

19
00:01:24,000 --> 00:01:29,500
Supervisory agents route the query through hybrid dense-sparse retrieval across statutes.

20
00:01:29,500 --> 00:01:34,000
Within seconds, it delivers a structured, grounded legal verdict:

21
00:01:34,000 --> 00:01:38,500
While raw Ashwagandha is barred under Section 3(p),

22
00:01:38,500 --> 00:01:44,000
her novel delivery process and bio-enhancement are eligible under Section 2(1)(j),

23
00:01:44,000 --> 00:01:50,000
provided trial data proves enhanced therapeutic efficacy under Section 3(d).

24
00:01:50,000 --> 00:01:54,800
Here is where AyurX separates itself: Zero-hallucination source grounding.

25
00:01:54,800 --> 00:01:59,500
Every single claim is verified against retrieved chunks with real authority scores.

26
00:01:59,500 --> 00:02:05,000
The Relational Knowledge Graph automatically maps Withania somnifera to its regulator,

27
00:02:05,000 --> 00:02:11,000
its TK risk, and mandatory Form III filing with the National Biodiversity Authority.

28
00:02:11,000 --> 00:02:15,500
Beside it, the IP Route Planner delivers an instant strategic matrix:

29
00:02:15,500 --> 00:02:20,000
Patenting is conditional on synergy, Trademark is available in Class 5,

30
00:02:20,000 --> 00:02:25,000
and her proprietary liposomal process is secured as a Trade Secret.

31
00:02:25,000 --> 00:02:29,200
AyurX empowers innovators in their native language.

32
00:02:29,200 --> 00:02:34,500
With one click, she translates the verdict into Hindi — preserving exact statutory citations.

33
00:02:34,500 --> 00:02:39,000
She clicks 'Listen', and AyurX reads the legal brief aloud.

34
00:02:39,000 --> 00:02:44,500
She exports a print-ready Case Brief and ABS Checklist in PDF and Markdown.

35
00:02:44,500 --> 00:02:50,000
Need to compare rules? The Law Version Timeline compares 2003 Rules against 2024 Amendments.

36
00:02:50,000 --> 00:02:56,000
And our live Evaluation Dashboard proves a ninety-eight percent pass rate across 50 test cases.

37
00:02:56,000 --> 00:03:05,000
From raw formulation to verified evidence to actionable legal strategy.

38
00:03:05,000 --> 00:03:15,000
AyurX: Ancient wisdom. Smarter answers.
```

---

## G. SHOT-BY-SHOT RECORDING PLAN

| Shot | Time | Screen & Route | Action / Cursor Flow | Visual State & Highlights | Transition |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **01** | `00:00 - 00:15` | Landing Page (`/`) | Slow cinematic scroll down hero; hover over mantra SVG animation. | Rotating Devanagari Sanskrit Mantra wheel; "Ancient wisdom. Modern answers." | Crossfade |
| **02** | `00:15 - 00:25` | Landing Page (`/`) | Click "Get Started →" on Navbar; smooth transition to `/app`. | Navigates into application shell; glassmorphic sidebar appears. | Cut |
| **03** | `00:25 - 00:40` | Wizard Step 1 (`/app`) | Select "🇮🇳 India", select "Startup / MSME" persona card; click "Continue". | Active green border highlight on cards; smooth step transition to Step 2. | Cut |
| **04** | `00:40 - 01:00` | Wizard Step 2 (`/app`) | Click "Yes" for Q1 (First Schedule), click "Modified" for Q2. Click "Run Classification". | Classification card animates in: *"Classical Ayurvedic Medicine (Modified) → P&P Medicine, D&C Act Sec 3(h)"*. | Pan |
| **05** | `01:00 - 01:15` | Wizard Step 2 (`/app`) | Review regulatory route: Form 24D, SLA AYUSH; click "Continue". | Advances progress bar to Step 3 (Issue Picker). | Cut |
| **06** | `01:15 - 01:30` | Wizard Step 3 (`/app`) | Click "Section 3(p) & 3(e) Patentability" card; click Mic icon (dictate query text). | Query pops into textarea: *"Modified liposomal Ashwagandha extract..."* | Cut |
| **07** | `01:30 - 01:50` | Wizard Step 4 (`/app`) | Click "Analyze →"; loading pulses; structured verdict streams in. | Executive Summary, Section 3(p) TK Analysis, Section 3(d) Bioavailability data. | Zoom (1.05x) |
| **08** | `01:50 - 02:10` | Wizard Step 5 (`/app`) | Click "Continue to Sources"; scroll through citation cards; hover on badges. | Citation Badge: *"5 of 5 citations verified"*; source cards show authority weights. | Cut |
| **09** | `02:10 - 02:25` | Wizard Step 5 (`/app`) | Scroll to Knowledge Graph & IP Route Planner; click "Build graph". | Dynamic SVG layered graph connects nodes; IP Route Planner cards highlight. | Cut |
| **10** | `02:25 - 02:40` | Wizard Step 6 (`/app`) | Click "Continue to Action Plan"; switch language to Hindi; click "Translate answer". | Hindi translated answer renders with English statutory citations preserved. Click "Listen". | Cut |
| **11** | `02:40 - 02:50` | Wizard Step 6 (`/app`) | Click "Export PDF" (shows print preview sheet); click "Export Markdown". | Case brief preview with downloaded `.md` file notification. | Cut |
| **12** | `02:50 - 03:05` | Sidebar & Panels (`/app`) | Click "Law Version Timeline" (compare 2003 vs 2024); click "Evaluation" tab. | Side-by-side comparative answers; Eval Dashboard shows **98% Accuracy (49/50 passed)**. | Cut |
| **13** | `03:05 - 03:15` | Closing Screen | Return to Landing Page or Closing Title graphic. | "AyurX: Ancient wisdom. Smarter answers." | Fade to Black |

---

## H. ON-SCREEN TEXT & CALLOUT OVERLAYS

* **00:05** — Callout: `The Problem: 5,000 Years of Traditional Knowledge vs Complex Modern IP Law`
* **00:22** — Title Banner: `AyurX (IP-SAKTI Sahayak) | SIH 2026 Problem ID 26045`
* **00:45** — Badge Overlay: `Deterministic Statutory Classification | D&C Act 1940 & FSSAI 2022`
* **01:10** — Pill: `Regulatory Pathway: AYUSH SLA · Form 24D`
* **01:25** — Callout: `Voice Dictation & Multi-Regime Supervisory Routing`
* **01:42** — Box: `Patents Act Section 3(p) TK Bar vs Section 2(1)(j) Novel Delivery Mechanism`
* **01:58** — Green Stamp: `100% Zero-Hallucination Citation Verification`
* **02:12** — Overlay: `Multi-Hop Relational Knowledge Graph (SVG Layered Layout)`
* **02:20** — Strategic Matrix: `IP Route Planner: Patent (Conditional) · Trademark (Class 5) · Trade Secret (Active)`
* **02:32** — Callout: `Regional Language Delivery | Preserving Statutory Precision`
* **02:45** — Callout: `One-Click Attorney-Ready Case Brief Export (PDF & Markdown)`
* **02:55** — Graphic: `Law Version Timeline: Document-Scoped Retrieval (2003 vs 2024 Rules)`
* **03:02** — Metric Tile: `Golden Benchmark: 98% Accuracy (49/50 Questions Passed)`
* **03:10** — Final Wordmark: `आयुरX — Ancient Wisdom. Smarter Answers.`

---

## I. EDITING & POST-PRODUCTION INSTRUCTIONS

1. **Resolution & Canvas**: 1920x1080 at 60 fps. Use a clean browser window at 100% scaling (1470x836 or 1920x1080 native).
2. **Pacing & Trimming**: Cut all network loading waits longer than 1.5 seconds. Use smooth L-cuts and J-cuts between narration and UI actions.
3. **Cursor Movement**: Enable cursor smoothing (e.g. ScreenFlow, Camtasia, or After Effects). Avoid erratic mouse wiggling; move with deliberate trajectory.
4. **Zooms & Focal Points**:
   * Zoom 1.15x into the **Classification Result** card at `00:55`.
   * Zoom 1.2x into the **Citation Verification Badge** (`5 of 5 verified`) at `01:55`.
   * Zoom 1.1x into the **Knowledge Graph** at `02:15`.
   * Zoom 1.15x into the **Eval Dashboard Accuracy Tile** (`98%`) at `03:02`.
5. **Color Grading**: Keep clean dark-mode contrast (`#0f172a` slate background, `#c7a45a` muted Ayurvedic gold accents, and `#10b981` emerald green verified badges).
6. **Audio Mix**:
   * Voiceover: Normalized to -14 LUFS, crisp high-mid EQ boost for dialogue clarity, light compression.
   * Background Music: Subtle, calm ambient acoustic/sitar-pad instrumental at -26 dB. Duck audio to -32 dB during technical explanations.

---

## J. FINAL VIDEO STATUS & PRODUCTION PACKAGE

```
================================================================================
[PRODUCTION STATUS]
VIDEO RENDERING NOT DIRECTLY AVAILABLE IN CURRENT HEADLESS TERMINAL ENVIRONMENT
================================================================================
```
*Because the headless Mac shell lacks `ffmpeg` and hardware GUI screen recording daemons, direct binary `.mp4` rendering is unavailable. However, the complete production package above provides 100% of the assets, exact timestamps, audio narration, subtitles, and click sequences required to record or composite the final demo immediately.*

### Asset Index for Recording:
* **Frontend Web URL**: `http://localhost:5173`
* **Backend API Base**: `http://127.0.0.1:8000`
* **Sample Input Query**:
  `"We developed a novel liposomal encapsulation of Withania somnifera (Ashwagandha) extract combined with Piper longum to enhance withanolide bioavailability by 300% for osteoarthritis. Can we patent this in India without triggering Section 3(p) or Section 3(e)?"`
* **Classification Inputs**:
  * Q1: In First Schedule text? → **Yes**
  * Q2: Formulation modified? → **Modified**
* **Jurisdiction**: India (`🇮🇳 India`)
* **Persona**: Startup / MSME (`Startup / MSME`)

---

## K. 10-POINT LAST-MINUTE DEMO RECORDING CHECKLIST

Follow this exact 10-point checklist before hitting record:

1. **Verify Services Running**:
   * Terminal 1: `PYTHONPATH=src ./venv/bin/python -m uvicorn api:app --reload --port 8000` (FastAPI backend active).
   * Terminal 2: `npm run dev` in `sih_frontend_antigrav` (Vite active on `http://localhost:5173`).
2. **Clean Browser Window**: Open Chrome in an incognito or dedicated profile. Hide bookmark bar (`Cmd + Shift + B`), close unrelated tabs, and maximize to 1080p.
3. **Verify API Connectivity**: Click `/app` → check that Knowledge Graph, Classification, and Chat respond without red connection errors.
4. **Theme Setting**: Set theme to **Dark Mode** via sidebar toggle (displays gold typography and green badges with highest contrast).
5. **Pre-populate Query**: Have the Ashwagandha liposomal query copied to clipboard for instant pasting or clean voice dictation.
6. **Microphone Permissions**: Ensure Google Chrome has microphone access enabled in macOS System Settings so the `Mic` voice input button works instantly.
7. **Volume Settings**: If demonstrating Text-to-Speech (`Listen` button), set system output volume to 60% so the browser speech is captured clearly by your recording software.
8. **Test PDF Print Preview**: Click "Export PDF" once beforehand to ensure the browser print preview dialog opens without delay.
9. **Display Zoom**: Set browser zoom to 100% (`Cmd + 0`) for crisp 1:1 pixel rendering.
10. **Zero-Glitch Reset**: Click "New Analysis" in the sidebar immediately prior to recording to ensure all state counters start fresh at Step 1.
