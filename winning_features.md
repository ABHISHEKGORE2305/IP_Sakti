Here's a curated feature list, tiered by how much each one matters to the judges. The problem statement ends by saying the solution "should be evaluable on answer accuracy, citation correctness, safe abstention, and multilingual quality," so those four criteria anchor everything below.

## Tier 1: Must-haves (you'll be judged directly on these)

**1. Citation-grounded RAG engine**
- Every claim is linked to a specific source: section, rule, or treaty article, such as "Patents Act 1970, S. 3(p)" or "Nagoya Protocol, Art. 6". Clicking a citation opens the exact passage, highlighted, not just the document.
- Chunk statutes at the section and sub-section level, with metadata for act, section, jurisdiction, effective date, and amendment source. Generic fixed-size chunking will produce wrong citations.
- Use hybrid retrieval (BM25 plus dense embeddings) with a reranker. Legal text is keyword-heavy, and "Section 3(p)" has to match exactly.

**2. Jurisdiction toggle with visibly separate answers**
- An 🇮🇳 India / 🌐 International switch, plus a "Both" mode that renders two side-by-side panels and never mixes them in one paragraph.
- Enforce the separation at retrieval time with a metadata filter, not just in the prompt. You can then tell judges the separation is architectural.

**3. Formulation Classification Wizard**
- A guided flow that asks 3–6 minimal questions: Is the formula from a First-Schedule text? Is it modified? Is it a new indication? Is it a standardized plant extract? Is it for food or topical use?
- Output: the regulatory category (Classical, P&P, New ASU drug, Phytopharmaceutical, Ayurveda Aahar, Cosmetic), plus a category card showing licensing requirements, evidence needed, patentability outlook, ABS obligations, and advertising restrictions.
- This is the heart of the problem statement. Build it well and show it in the first minute of your demo.

**4. Safe abstention and confidence indicator**
- Show a High / Medium / Low confidence badge based on retrieval score, source agreement, and coverage.
- If retrieval is weak or the question is out of scope (for example, "Should I sue X?"), the assistant declines, explains why, and offers escalation. Judges will deliberately try to trip it, so demo a refusal on purpose.

**5. Standing disclaimer and escalation to a human IP facilitator**
- A persistent "Information, not legal advice" banner.
- A "Talk to an expert" button that packages the conversation, the classification result, and the cited sources into a handoff ticket (a mock facilitator dashboard is enough).

## Tier 2: Differentiators (these win it)

**6. IP Route Planner**
- The user describes a product and gets a personalized IP strategy map. For example: "Patent: likely barred under S. 3(p) as TK; consider a trademark for the brand, a design for the packaging, and a trade secret for the process; a GI if the product is region-linked."
- Present it as a visual decision tree, not a paragraph.

**7. ABS Compliance Helper**
- Asks whether you are an Indian entity, whether the resource is codified or cultivated, and what your commercial intent is. It then outputs the likely obligations under the Biological Diversity Act (as amended in 2023) and the 2024 Rules: whether prior approval or intimation is needed, which form applies, whom to approach (NBA or SBB), and when benefit-sharing applies.
- Add a downloadable ABS checklist PDF with citations.

**8. TKDL / Prior-Art Pointer**
- Maps a formulation to its classical text references and to the relevant TKDL categories, with deep links to TKDL and IP India public search.
- Adds a "Misappropriation risk" flag, which surfaces the TK-protection angle the problem statement emphasizes.

**9. Version-tracked corpus with a "Law changed" timeline**
- Every source carries an effective-from/effective-to date. Answers show a line like "As of [date], per Patents (Amendment) Rules 2024."
- A "What changed?" view compares old and new provisions, such as the Patent Rules before and after 2024, or the Biological Diversity Act before and after the 2023 amendment.
- A strong demo moment: ask a question under the old law versus the current law and show different, correctly cited answers. The Ayurveda advertisement-rule developments are a good live example of a fast-moving area, but verify their current status before you use them.

**10. Knowledge graph layer**
- Model entities and relations such as Plant → Formulation → Classical Text → Regulatory Category → Applicable Law → Form/Authority.
- Use it for multi-hop questions like "I'm exporting an Ashwagandha extract to the EU; what do I need?" The graph combines the Indian ABS requirements, the export route, and the international regime.
- Include a visual graph explorer. Judges love seeing the reasoning path.

**11. Agentic multi-source orchestration**
- A planner agent splits a complex query into sub-queries (IP, regulatory, ABS, international), runs each with the right retriever or tool, and a synthesizer merges the results with citations kept intact.
- Show the agent's step trace in a collapsible panel for transparency.

**12. Export Market Navigator**
- Country cards for key markets (EU, US, UK, GCC, ASEAN) covering how herbal and Ayurvedic products are classified, the registration pathway, and the relevant IP filing route (PCT, Madrid, Hague).
- Keep this strictly in International mode.

## Tier 3: Multilingual and access (explicitly required)

**13. Bhashini integration**
- Text translation for at least 4–5 languages (Hindi, Marathi, Tamil, Bengali, and so on), plus Bhashini ASR/TTS for voice input and output.
- Keep legal terms in the original with a gloss, e.g., "पेटेंट (Patent)". Citations stay canonical in English, but the explanation is in the user's language.
- Target cultivators and vaidyas with a voice-first mode. A demo of a farmer asking in Hindi about selling medicinal plants and getting ABS guidance is powerful.

**14. Persona modes**
- Four personas: Practitioner, Researcher, Startup/MSME, and Cultivator. Each adjusts vocabulary, depth, and which tools surface first. It's cheap to build and makes the product feel purpose-built.

**15. Source Gateway**
- One-click deep links to free official databases (India Code, IP India, TKDL, the GI Registry, NBA).
- Paid-source connectors only with explicit, logged consent: a consent modal, a per-source permission, and a revocation option. Even a mocked connector with a real consent-and-audit flow earns points.

## Tier 4: Trust, safety, and compliance

**16. DPDP-aligned privacy**
- Consent at onboarding, data minimization, a "delete my data" option, and PII redaction before queries reach the LLM.
- A privacy dashboard showing what's stored.

**17. Audit log**
- Every query, retrieved source, answer, and permission grant is logged immutably. Build an admin view for this.

**18. Guardrails**
- Prompt-injection filtering, an anti-hallucination check (a post-generation verifier that confirms each cited section exists and supports the claim), and topic scope limits.
- Map the design to recognized standards such as the OWASP Top 10 for LLM applications in your presentation.

## Tier 5: Proof that it works

**19. Evaluation dashboard**
- Build a gold Q&A set of 100–200 questions across IP types, classifications, jurisdictions, out-of-scope traps, and multilingual variants.
- Report answer accuracy, citation precision and recall, abstention correctness, and translation quality (such as BLEU/chrF or human rating), using RAGAS-style metrics like faithfulness and context precision.
- Put it live in the app. Very few teams show measured results, and this directly answers the evaluation criteria in the problem statement.

**20. Corpus admin panel**
- Upload new notifications, auto-chunk and tag them, mark superseded provisions, and re-index. This shows the "keep the corpus current" requirement is real.

## Recommended build order (it mirrors the problem statement's staging)

1. **MVP (days 1–2):** corpus ingestion with section-level chunking, the RAG engine with citations, the jurisdiction toggle, the disclaimer, and abstention.
2. **Core differentiators:** the Classification Wizard, the IP Route Planner, the ABS Helper, and the TKDL pointer.
3. **Depth:** the knowledge graph, the agentic orchestration, and version tracking.
4. **Polish:** Bhashini voice and text, persona modes, the evaluation dashboard, the consent and audit flows, and mock paid connectors.

## Tips for winning the demo

- Tell a story with one user journey: an AYUSH startup founder has a modified Triphala-based formulation. Walk through classification, then the IP routes (with the S. 3(p) warning), then ABS obligations, then the export plan. End with the same question asked in Hindi by voice.
- Show three failure-safety moments: a refusal on legal advice, a low-confidence escalation, and a law-version comparison.
- Keep your evaluation scores on a slide. Numbers beat claims.
- Curate a smaller, high-quality corpus. Twenty perfectly chunked and tagged key instruments beat 500 badly parsed PDFs.
- Frame the architecture diagram around the problem statement's own wording (RAG, then the knowledge graph, then agents, then connectors) so judges can tick boxes easily.