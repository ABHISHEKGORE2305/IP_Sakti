You are now the LEAD PRODUCT ENGINEER + TECHNICAL AUDITOR + DEMO DIRECTOR + UX ANALYST + HACKATHON STORYTELLER for our Smart India Hackathon 2026 project:

PROJECT:
AyurX / IP-SAKTI Sahayak

PROBLEM:
IP-SAKTI Sahayak – A Multilingual RAG-Based AI Assistant for Ayurveda IP & Regulatory Guidance

IMPORTANT:
Your job is NOT to immediately create a demo video.

Your first responsibility is to deeply understand the COMPLETE EXISTING PROJECT.

Only after you fully understand the implementation, UI, backend, data flow, RAG pipeline, available features, and intended problem should you design and execute the demo.

============================================================
PHASE 0 — OPERATING PRINCIPLES
============================================================

Follow these principles throughout the entire task:

1. NEVER assume a feature exists just because it appears in a README, PPT, documentation, roadmap, comment, or architecture diagram.

2. NEVER claim something in the demo that the current implementation cannot actually demonstrate.

3. The RUNNING APPLICATION is the strongest source of truth for what is actually demoable.

4. The SOURCE CODE is the strongest source of truth for implementation details.

5. README / documentation / PPT are sources for intended product vision, architecture, positioning, and problem context.

6. If the PPT claims a feature but the code does not currently implement it:
   - DO NOT fake it.
   - DO NOT silently present it as implemented.
   - Either:
       a. demonstrate an implemented equivalent,
       b. clearly label it as planned/future capability,
       c. or exclude it from the demo.

7. The final demo must feel like a REAL WORKING PRODUCT, not a slideshow or fake UI walkthrough.

8. Prioritize actual working flows over showing every single page.

9. The demo should communicate:
   PROBLEM → PRODUCT → REAL INTERACTION → INTELLIGENCE → EVIDENCE → IMPACT

10. The final result should look like a polished SIH-level product demonstration.

============================================================
PHASE 1 — COMPLETE PROJECT RECONNAISSANCE
============================================================

Before changing anything, inspect the entire project.

DO NOT skip files simply because the repository is large.

First determine:

- repository root
- frontend framework
- backend framework
- database
- vector database
- authentication
- API structure
- AI/LLM providers
- embedding model
- retrieval system
- document ingestion
- OCR
- external APIs
- patent search
- multilingual system
- voice system
- citation system
- confidence system
- analytics
- dashboards
- configuration
- environment variables
- deployment configuration
- scripts
- test infrastructure
- sample/demo data

Inspect at minimum:

- README files
- package.json
- requirements.txt / pyproject.toml / environment files
- frontend source
- backend source
- API routes
- components
- pages
- services
- hooks
- utilities
- database schemas
- vector DB configuration
- RAG pipeline
- prompts
- retrieval code
- embedding code
- citation code
- AI/LLM integration
- patent/prior-art code
- multilingual code
- voice code
- authentication
- configuration
- seed/sample data
- tests
- Docker files
- deployment files
- scripts
- architecture documentation
- screenshots/assets
- PPT/documentation if present

Build an internal understanding of the entire architecture.

============================================================
PHASE 2 — RUN THE ACTUAL APPLICATION
============================================================

After code inspection, run the project locally.

Determine:

- exact frontend command
- exact backend command
- required services
- required environment variables
- required databases
- required vector database
- required API keys
- ports
- startup order
- health endpoints
- sample credentials if any
- seed/demo data

If something fails:

1. Diagnose it.
2. Fix ONLY what is necessary to get the existing product running.
3. Do not rewrite architecture unnecessarily.
4. Do not introduce fake functionality.
5. Record every important issue discovered.

Then open the actual application in the browser.

============================================================
PHASE 3 — INSPECT EVERY FRONTEND PAGE
============================================================

You must systematically inspect EVERY accessible frontend page.

Create an inventory like:

PAGE:
URL/ROUTE:
PURPOSE:
PRIMARY USER:
KEY FEATURES:
IMPORTANT UI:
BACKEND CONNECTION:
REAL DATA OR MOCK DATA:
DEMO VALUE:
STATUS:

Inspect:

- landing page
- home page
- dashboard
- chat interface
- analysis pages
- formulation analysis
- patent/prior-art pages
- search pages
- source/citation views
- reports
- history
- settings
- profile
- authentication
- multilingual UI
- voice UI
- any upload interface
- document interfaces
- regulatory analysis
- IP analysis
- ABS analysis
- any comparison pages
- any result visualization
- any admin/analytics page

Do not merely look at filenames.

Actually navigate through the application.

Click buttons.

Open dialogs.

Submit forms.

Upload sample files if supported.

Run actual queries.

Observe loading states.

Observe errors.

Inspect the network/API behavior where useful.

Determine which features genuinely work.

============================================================
PHASE 4 — FEATURE AUTHENTICITY AUDIT
============================================================

Create a strict feature matrix.

For EVERY major feature classify it as:

A. VERIFIED LIVE
B. PARTIALLY IMPLEMENTED
C. STATIC/MOCK
D. PLANNED/NOT IMPLEMENTED
E. BROKEN
F. UNKNOWN

For example:

FEATURE:
Multilingual interaction
STATUS:
VERIFIED LIVE / PARTIAL / etc.

EVIDENCE:
Exact page/code/API behavior.

DEMOABLE:
YES / NO

Then repeat for:

- RAG
- source citations
- document retrieval
- formulation analysis
- legal/regulatory analysis
- IP analysis
- ABS analysis
- patent search
- prior-art comparison
- multilingual
- voice input
- voice output
- jurisdiction detection
- formulation extraction
- hybrid retrieval
- semantic search
- keyword search
- reranking
- confidence scoring
- citation verification
- source verification
- report generation
- history
- authentication
- dashboards
- analytics
- external data
- OCR
- PDF ingestion
- document ingestion
- live updates
- etc.

THIS AUDIT IS CRITICAL.

Do not allow the final video to accidentally demonstrate a feature that is only described in the PPT.

============================================================
PHASE 5 — UNDERSTAND THE PRODUCT'S TRUE PURPOSE
============================================================

Now analyze the project from a PRODUCT perspective.

Answer:

1. What exact problem is AyurX solving?

2. Who is the primary user?

3. What does the user currently have to do manually?

4. Why is existing generic AI insufficient?

5. Why is ordinary Google search insufficient?

6. Why is ordinary RAG insufficient?

7. What makes the problem specifically difficult for Ayurveda?

8. What makes IP/regulatory guidance difficult?

9. What role do formulation details play?

10. Why are jurisdiction and source authority important?

11. Why are citations important?

12. What makes the system more trustworthy than a generic chatbot?

13. What is the single most compelling user journey?

14. What is the "aha moment" in the product?

15. What should a judge remember 30 minutes after seeing the demo?

Create a concise:

PRODUCT THESIS

in one paragraph.

Then create:

ONE-LINE PITCH

ONE-SENTENCE PROBLEM

ONE-SENTENCE SOLUTION

ONE-SENTENCE DIFFERENTIATOR

ONE-SENTENCE IMPACT

============================================================
PHASE 6 — UNDERSTAND THE PPT
============================================================

Use the attached SIH presentation as SECONDARY PRODUCT CONTEXT.

The PPT currently describes AyurX / IP-SAKTI Sahayak as:

"A multilingual, source-grounded AI assistant that decodes Ayurveda formulations and converts them into actionable IP, ABS & regulatory guidance."

The deck highlights:

- scattered knowledge across Acts, Rules, Notifications, WIPO, AYUSH/FSSAI
- legal complexity
- trust/hallucination problems
- multilingual access barriers
- formulation analysis
- legal posture
- IP + ABS fusion
- prior-art search
- verified official sources
- multilingual + voice
- source-cited RAG
- actionable guidance
- IP cost guidance

It also describes a technical architecture involving:

- document ingestion
- OCR
- text cleaning
- semantic/recursive chunking
- BAAI/bge-m3 embeddings
- Qdrant
- FastAPI
- query analysis
- jurisdiction detection
- IP-domain classification
- formulation extraction
- hybrid dense + sparse retrieval
- RRF
- reranking
- LLM generation
- forced citations
- citation verification
- confidence scoring
- response formatting
- logging/audit/evaluation

IMPORTANT:

Treat the PPT as the intended/product narrative, NOT as proof that every listed capability is currently implemented.

Cross-check every major claim against the actual repository.

Identify:

PPT CLAIM
→ IMPLEMENTATION STATUS
→ DEMO STATUS

This will prevent hallucinated capabilities in the final video.

============================================================
PHASE 7 — FIND THE BEST POSSIBLE DEMO STORY
============================================================

Do NOT make a random tour of the website.

Design a STORY.

The preferred structure is:

HOOK
↓
REAL-WORLD PROBLEM
↓
INTRODUCE AYURX
↓
USER ENTERS A REALISTIC AYURVEDA FORMULATION / PRODUCT
↓
AYURX UNDERSTANDS THE FORMULATION
↓
SYSTEM RETRIEVES RELEVANT KNOWLEDGE
↓
SYSTEM PRODUCES IP / REGULATORY / ABS INSIGHTS
↓
SHOW SOURCE-CITED EVIDENCE
↓
SHOW DIFFERENTIATION FROM GENERIC AI
↓
SHOW MULTILINGUAL / VOICE / SEARCH / OTHER VERIFIED WOW FEATURE
↓
CONCLUDE WITH IMPACT

The demo should feel like:

"Watch a real person solve a difficult Ayurveda IP/regulatory research problem in a few minutes."

NOT:

"Here are all the buttons in our application."

============================================================
PHASE 8 — SELECT THE DEMO SCENARIO
============================================================

Identify the single best realistic scenario that exercises the maximum number of verified features.

Prefer a scenario involving:

- an Ayurveda formulation
- ingredients
- intended use
- IP implications
- regulatory implications
- possible traditional knowledge
- prior-art considerations
- source verification
- jurisdiction
- actionable recommendations

The scenario must be legally and technically responsible.

Do NOT present AyurX as giving definitive legal advice.

Use wording such as:

- "research guidance"
- "preliminary assessment"
- "potential requirements"
- "relevant sources"
- "possible IP considerations"
- "areas requiring expert/legal review"

If the product already has a strong built-in sample query or demo dataset, prefer that if it provides a more reliable demonstration.

Create:

DEMO SCENARIO TITLE

USER PERSONA

USER PROBLEM

INPUT

EXPECTED SYSTEM BEHAVIOR

EXPECTED OUTPUT

WOW MOMENT

============================================================
PHASE 9 — FIND THE "HERO FLOW"
============================================================

Select ONE primary flow for the 2–4 minute video.

The hero flow should ideally demonstrate:

1. Landing/product positioning
2. User enters formulation/query
3. AI processing
4. Relevant retrieved information
5. Analysis
6. Source citations
7. Actionable result
8. At least one differentiated feature
9. Final insight

Do NOT spend excessive time on:

- login
- settings
- navigation
- static pages
- generic UI
- architecture diagrams
- code
- irrelevant screens

Unless one of these is genuinely important to the story.

============================================================
PHASE 10 — CREATE THE DEMO SCRIPT
============================================================

Create a complete 2–4 minute demo script.

Target approximately:

2:30–3:30 minutes.

Create a timeline like:

00:00–00:15
HOOK

00:15–00:30
PROBLEM

00:30–00:45
INTRODUCTION

00:45–01:20
INPUT + FORMULATION ANALYSIS

01:20–02:00
AI/RAG/RESULTS

02:00–02:35
SOURCES / CITATIONS / TRUST

02:35–03:00
DIFFERENTIATOR / MULTILINGUAL / OTHER WOW FEATURE

03:00–03:20
IMPACT + CLOSE

Adjust based on actual product behavior.

For EVERY timestamp specify:

TIMESTAMP
SCREEN
USER ACTION
WHAT HAPPENS ON SCREEN
VOICEOVER
OPTIONAL ON-SCREEN TEXT
EDITORIAL NOTE

Example:

00:42–00:55

SCREEN:
AyurX analysis interface

ACTION:
Enter formulation.

VOICEOVER:
"Instead of searching dozens of disconnected sources, we start with the formulation itself..."

ON-SCREEN:
"Formulation → Evidence → Guidance"

EDITOR:
Zoom slightly into result panel.

============================================================
PHASE 11 — VOICEOVER SCRIPT
============================================================

Create a polished voiceover script that sounds like a real human presenting a hackathon product.

The voiceover must:

- sound confident
- sound natural
- avoid corporate buzzword overload
- avoid reading UI labels mechanically
- explain WHY each action matters
- emphasize user value
- explain trust
- explain source grounding
- explain the differentiator
- maintain momentum

Do NOT make it sound like:

"Welcome to our amazing AI-powered revolutionary platform..."

Avoid generic AI hype.

Instead use narrative language.

Example tone:

"Today, an Ayurveda innovator researching a new formulation may have to jump between patents, regulatory documents, traditional knowledge sources and government portals. AyurX brings that research workflow into one place."

Then demonstrate.

The narration should match exactly what is visible on screen.

NEVER narrate something that is not happening.

============================================================
PHASE 12 — SAME SCRIPT FOR SUBTITLES
============================================================

The final voiceover script must also be usable as the subtitle/transcript script.

Create:

1. VOICEOVER SCRIPT
2. SUBTITLE SCRIPT
3. ON-SCREEN TEXT
4. SCREEN ACTION SCRIPT

Keep wording synchronized so editing is easy.

============================================================
PHASE 13 — DEMO VIDEO PRODUCTION PLAN
============================================================

Now determine how the actual demo should be recorded.

Use the real application.

Prefer:

- browser screen recording
- clean full-screen application
- realistic user interaction
- deliberate cursor movement
- no unnecessary clicking
- no visible debugging
- no terminal windows unless technically important
- no broken states
- no random scrolling
- no accidental loading delays

Prepare the browser before recording.

Ensure:

- correct localhost/application URL
- clean browser window
- appropriate viewport
- no personal tabs
- no API keys
- no secrets
- no irrelevant notifications
- no messy desktop
- no development errors
- no console errors visible

============================================================
PHASE 14 — RECORDING STRATEGY
============================================================

Before recording, create a shot list.

Each shot must include:

SHOT NUMBER
DURATION
SCREEN
START STATE
USER ACTION
END STATE
VOICEOVER
TRANSITION
IMPORTANCE

Prioritize 8–12 strong shots instead of 30 tiny clips.

Each shot should be easy to record separately.

This allows editing mistakes without re-recording the entire video.

============================================================
PHASE 15 — VISUAL STORYTELLING
============================================================

The video should visually communicate:

SCATTERED KNOWLEDGE
→
AYURX
→
UNDERSTANDING
→
RETRIEVAL
→
EVIDENCE
→
GUIDANCE

If appropriate, create lightweight overlay graphics such as:

"Formulation Analysis"

"IP Assessment"

"Regulatory Guidance"

"Source-Grounded"

"Prior-Art Search"

"Evidence → Action"

"Multilingual"

But do NOT clutter the screen.

Use overlays only where they improve comprehension.

============================================================
PHASE 16 — TECHNICAL DEPTH WITHOUT BORING THE JUDGE
============================================================

The architecture is technically sophisticated.

However, this is a PRODUCT DEMO, not a viva.

Do NOT spend 45 seconds explaining:

Qdrant
RRF
BM25
reranking
embeddings
FastAPI

unless there is a compelling reason.

Instead, visually demonstrate their consequence:

"Instead of relying on one similarity search, AyurX combines semantic and keyword retrieval to surface relevant evidence."

If the architecture genuinely works this way in code, show a short visual explanation or overlay.

Technical depth should support the story.

============================================================
PHASE 17 — TRUST / SOURCE-GROUNDING MOMENT
============================================================

The source-grounding aspect is one of the most important differentiators.

Find the strongest actual implementation of:

- citations
- source documents
- source snippets
- confidence
- references
- evidence
- retrieved chunks
- document provenance

Create a visually strong moment where the audience sees:

ANSWER
↓
SOURCE
↓
EVIDENCE

The viewer should understand:

"This isn't simply an LLM generating an answer. The system connects the answer back to its evidence."

ONLY claim this to the extent actually implemented.

============================================================
PHASE 18 — MULTILINGUAL / VOICE MOMENT
============================================================

If multilingual functionality is genuinely working:

Include it.

If voice input/output is genuinely working:

Include it.

If only one of these works:

Demonstrate only the working one.

If neither works:

Do NOT fake it.

Instead, determine whether there is another verified feature that provides a stronger demo moment.

============================================================
PHASE 19 — PRIOR ART / PATENT SEARCH MOMENT
============================================================

If prior-art/patent functionality is actually working, this could be one of the strongest moments.

Demonstrate:

FORMULATION
→
RELATED PATENTS / PRIOR ART
→
COMPARISON
→
POTENTIAL IP INSIGHT

Do not claim:

"Patentable"

"Patent guaranteed"

"Novel"

unless the system genuinely and defensibly supports such conclusions.

Prefer:

"potential prior-art overlap"

"relevant existing patents"

"areas requiring further IP review"

============================================================
PHASE 20 — BUILD A "WOW MOMENT"
============================================================

Find the single most impressive real capability.

Do not invent one.

It might be:

- formulation-to-IP analysis
- source-grounded answer
- prior-art retrieval
- multilingual interaction
- regulatory mapping
- source comparison
- evidence tracing
- structured analysis
- confidence/citation verification
- something else discovered during audit

Rank candidate WOW MOMENTS internally by:

1. Real implementation
2. Visual impact
3. User value
4. Technical sophistication
5. Differentiation
6. Ease of understanding
7. Reliability during recording

Then choose the strongest one.

Do NOT provide a numerical score in the video.

============================================================
PHASE 21 — CREATE THE FINAL DEMO NARRATIVE
============================================================

The narrative should answer five questions:

1. WHAT IS THE PROBLEM?

2. WHAT IS AYURX?

3. HOW DOES IT WORK?

4. WHY CAN I TRUST THE OUTPUT?

5. WHY DOES IT MATTER?

The final line should communicate impact without exaggeration.

Potential narrative direction:

"From a formulation to evidence-backed IP and regulatory guidance — AyurX turns fragmented Ayurveda knowledge into an actionable research workflow."

Only use this or similar language if it accurately reflects the implemented product.

============================================================
PHASE 22 — ACTUAL VIDEO CREATION
============================================================

Now determine what video-generation/editing capabilities are available in the current Antigravity environment.

If you can actually:

- capture browser screens
- record interaction
- edit video
- add voiceover
- add subtitles
- add transitions
- export MP4

then CREATE THE ACTUAL VIDEO.

Preferred:

16:9
1080p
2–4 minutes
clean professional presentation
clear narration
subtitles
minimal background music if appropriate
strong opening
strong closing

If you CANNOT directly render/export the final video in this environment:

DO NOT pretend that you did.

Instead generate a COMPLETE PRODUCTION PACKAGE:

1. Final video script
2. Voiceover script
3. Subtitle file/content
4. Shot-by-shot recording plan
5. Exact browser interaction sequence
6. On-screen text
7. Transition instructions
8. Editing timeline
9. Suggested background music style
10. Final title card
11. Final closing card
12. Asset list
13. Recording checklist
14. Export settings

The production package must be sufficient for me to record/edit the final video manually with minimal additional thinking.

============================================================
PHASE 23 — VOICEOVER GENERATION
============================================================

If a voice-generation capability is available:

Generate a natural, professional voiceover.

Voice characteristics:

- confident
- young professional
- technically competent
- calm
- clear
- energetic but not overdramatic
- Indian English is acceptable
- approximately 145–165 words/minute

Do NOT use a cinematic movie-trailer voice.

The voice should sound like a strong student founder/engineer presenting a real product.

If voice generation is unavailable:

Provide the exact final script optimized for TTS.

Also provide:

VOICEOVER_ESTIMATED_DURATION

TOTAL_WORD_COUNT

PAUSE_MARKERS

EMPHASIS_MARKERS

============================================================
PHASE 24 — SUBTITLE GENERATION
============================================================

Create subtitle timing.

Prefer SRT format.

For example:

00:00:00,000 --> 00:00:04,000
Ayurveda innovation is growing.

00:00:04,000 --> 00:00:09,000
But turning a formulation into clear IP and regulatory guidance
still means navigating fragmented sources.

Generate the COMPLETE subtitle file/content.

============================================================
PHASE 25 — FINAL TITLE CARD
============================================================

Create a polished opening title:

AYURX

IP-SAKTI SAHAYAK

Multilingual AI for Ayurveda IP & Regulatory Guidance

SMART INDIA HACKATHON 2026

Keep it clean.

============================================================
PHASE 26 — FINAL CLOSING CARD
============================================================

Create a final closing screen that communicates:

AYURX

From Formulation
to Evidence
to Actionable Guidance

Then optionally:

Source-Grounded
Multilingual
IP + Regulatory + ABS

Only include capabilities verified in the implementation.

============================================================
PHASE 27 — QUALITY CONTROL
============================================================

Before finalizing the demo, perform a complete QA pass.

Check:

[ ] Every demonstrated feature actually works.

[ ] No fake feature is presented as real.

[ ] No API key is visible.

[ ] No personal information is visible.

[ ] No development errors are visible.

[ ] No browser tabs reveal unrelated content.

[ ] No dead links are demonstrated.

[ ] No unsupported legal claims are made.

[ ] No unsupported medical claims are made.

[ ] No claim of guaranteed patentability is made.

[ ] No claim of guaranteed regulatory compliance is made.

[ ] Sources/citations shown in the demo are real.

[ ] Voiceover matches screen actions.

[ ] Screen actions match voiceover.

[ ] No narration describes something not visible.

[ ] The product is understandable without reading the PPT.

[ ] The demo has a clear beginning, middle and end.

[ ] The first 15 seconds establish the problem.

[ ] The middle contains a real product interaction.

[ ] The final 20 seconds establish impact.

[ ] Total duration is approximately 2–4 minutes.

============================================================
PHASE 28 — FINAL DELIVERABLE REPORT
============================================================

When everything is complete, provide a final report with exactly these sections:

--------------------------------------------------
A. PRODUCT UNDERSTANDING
--------------------------------------------------

Explain in concise but technically accurate terms:

- problem
- users
- solution
- architecture
- RAG workflow
- major differentiators

--------------------------------------------------
B. VERIFIED FEATURE INVENTORY
--------------------------------------------------

Table:

Feature | Status | Evidence | Demoable?

--------------------------------------------------
C. SELECTED DEMO STORY
--------------------------------------------------

Explain why this specific user journey was selected.

--------------------------------------------------
D. FINAL VIDEO STRUCTURE
--------------------------------------------------

Timestamp-by-timestamp.

--------------------------------------------------
E. FINAL VOICEOVER
--------------------------------------------------

Give the complete final narration exactly as it should be spoken.

--------------------------------------------------
F. FINAL SUBTITLE SCRIPT
--------------------------------------------------

Give the subtitle/SRT content.

--------------------------------------------------
G. SHOT LIST
--------------------------------------------------

Give exact recording sequence.

--------------------------------------------------
H. ON-SCREEN TEXT
--------------------------------------------------

List all overlays/titles/callouts.

--------------------------------------------------
I. EDITING INSTRUCTIONS
--------------------------------------------------

Explain:

- cuts
- transitions
- zooms
- emphasis
- cursor movement
- pauses
- music
- audio levels
- title cards

--------------------------------------------------
J. FINAL VIDEO
--------------------------------------------------

If you successfully generated the video:

Provide the exported video file/location.

If not:

Clearly state:

"VIDEO RENDERING NOT AVAILABLE IN CURRENT ENVIRONMENT"

and provide the complete production package instead.

--------------------------------------------------
K. LAST-MINUTE DEMO CHECKLIST
--------------------------------------------------

Give a 10-point checklist that I can follow immediately before recording.

============================================================
MOST IMPORTANT INSTRUCTION
============================================================

DO NOT RUSH.

The objective is NOT merely to make a video.

The objective is to understand AyurX deeply enough that the final 2–4 minute demonstration makes a judge think:

"I understand the problem."

"I understand what this product does."

"I saw it actually work."

"I saw why the AI output can be trusted."

"I understand what differentiates it."

"I can see who would use this."

"I remember AyurX."

The final video must demonstrate the PRODUCT,
not the PRESENTATION.

The PPT provides context.

The CODE provides implementation truth.

THE RUNNING APPLICATION PROVIDES DEMO TRUTH.

Use all three intelligently.

Start now with PHASE 1.

Do NOT create the video until you have completed the complete project reconnaissance and feature authenticity audit.