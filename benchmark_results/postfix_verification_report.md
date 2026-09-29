# Post-Fix Verification Report — IP-SAKTI Sahayak

**Sample:** 49 re-run cases from `verify_postfix.json` (27 sprint-1, 22 sprint-2)
**Graded:** same PASS / PARTIAL / FAIL standard as the pre-fix runs
**Date:** 2026-09-29

---

## 1. Verdict Transition Matrix

| Prior \ New | PASS | PARTIAL | FAIL | Total |
|---|---|---|---|---|
| **PASS** | 4 | **3** | **1** | 8 |
| **PARTIAL** | 2 | 5 | **1** | 8 |
| **FAIL** | 7 | 10 | 16 | 33 |
| **Total** | 13 | 18 | 18 | 49 |

**Movement summary**
- Improved: 19 cases (FAIL→PASS 7, FAIL→PARTIAL 10, PARTIAL→PASS 2)
- Held: 25 cases (PASS→PASS 4, PARTIAL→PARTIAL 5, FAIL→FAIL 16)
- **Regressed: 5 cases** (PASS→PARTIAL 3, PASS→FAIL 1, PARTIAL→FAIL 1)

---

## 2. Before / After on this 49-case sample

| Verdict | Before | | After | | Delta |
|---|---|---|---|---|---|
| PASS | 8 | 16.3% | 13 | 26.5% | **+10.2 pts** |
| PARTIAL | 8 | 16.3% | 18 | 36.7% | +20.4 pts |
| FAIL | 33 | 67.3% | 18 | 36.7% | **−30.6 pts** |

Real but modest. The headline win is that hard FAILs nearly halved. The pass rate only went from ~1 in 6 to ~1 in 4 — most of the movement was FAIL→PARTIAL, i.e. the system now produces *partially* grounded answers where it previously produced nothing usable. On a legal-guidance tool, 37% FAIL and only 27% PASS is still not shippable.

Note: this 49-case sample was pre-selected and is not representative of the full 200; it is only valid for the same-case before/after comparison.

---

## 3. Failure Patterns — Fixed vs Persisting

### (a) Over-abstention when a clear answer exists — **PARTIALLY FIXED**
The graded-fallback prompt works when the corpus actually contains the material. Of the 17 answers containing a refusal phrase:

- **6 are legitimate, properly scoped limitations** (answer the covered part, name what isn't covered): **10, 49, 86, 124, 164, 182**
- **11 are still blanket non-answers on the core question**: **26, 63, 74, 79, 83, 127, 168, 172, 175, 183, 186**

Case **63** is the clearest remaining instance of the old failure: "Is anti-dandruff herbal shampoo a cosmetic or an Ayurvedic drug?" is answerable from the D&C Act definitions that *are* in the corpus, and the system said it could not determine it.

### (b) Wrong-jurisdiction substitution (US FDA law for India) — **FIXED in output, NOT in retrieval**
No answer in the sample substitutes US FDA law for Indian law. However, the US FDA Botanical Drug Guidance still gets retrieved for India/international queries (83, 183) — the filter suppresses it from the prose but not from the retriever.

**A mirror-image problem has replaced it:** genuinely international questions now get "the Indian sources don't cover this" refusals. The jurisdiction toggle does not switch corpora. Cases **74, 79, 83, 175, 183** all fail this way; 175 is literally the "jurisdiction switch feature" test case and it did not switch.

### (c) Stale 2024 amendment state — **NOT FIXED**
Every one of the four 2024-amendment cases still fails:
- **22** — gives the old 6-month Form 3 regime, not the 3-month-from-FER rule.
- **26** — "intervals not less than six months", doesn't know Form 27 exists.
- **96** — **actively wrong**: states working statements are required *annually* under Rule 131, i.e. the exact stale answer the case was written to catch.
- **127** — says the Patents (Amendment) Rules 2024 are not in the corpus.

Worse, **26 and 96 contradict each other** on the same statutory point within the same run (six-monthly vs annually). The Patents (Amendment) Rules 2024 text was evidently not ingested, or not retrievable.

### (d) Reversed yes/no conclusions — **LARGELY FIXED**
Only two conclusion-level errors remain: **96** (reversed Yes/No on Form 27 frequency) and **9** (classifies an infrared applicator device as an ASU drug rather than splitting hardware/Medical Devices Rules 2017 from the oil). Elsewhere the yes/no direction is now consistently right.

### (e) Answering a narrower / different question — **PERSISTS**
- **11** — asked about CITES / Section 38 BDA / Wildlife Protection Act for wild *Aconitum*; answered with generic ABS prior-intimation rules.
- **13** — asked food-vs-drug for Immunity Tea; answered with the spices/condiments labelling rule and never reached the FSSAI Ayurveda Aahara Regulations (which *are* in the corpus — used successfully in case 3).
- **114** — asked what triage questions to ask; produced a patentability screening checklist.
- **140** — asked about mandi sourcing compliance; drifted into NBA Form 7 pre-grant IPR approvals.

### (f) Corpus gaps — **LARGELY FIXED, with named residual holes**
The ingestion clearly worked. New PASSes are almost entirely attributable to newly ingested documents:
- Trade Marks Act 1999 → **146 PASS** (Sec 9(1)(a)/(b) cited correctly)
- PPV&FR Act 2001 → **125, 152, 160 PASS**, **30 PARTIAL**
- WIPO GRATK → **71 PASS** (excellent, includes ratification status)
- FSSAI Ayurveda Aahara Regs → **3** now cites Rule 12(d)/13
- D&C Act + Rules → a large block of sprint-1 cases moved off FAIL

**Residual corpus gaps causing FAILs:**
| Missing source | Cases |
|---|---|
| Ayurvedic Pharmacopoeia of India (heavy-metal, aflatoxin, pesticide limits) | 66, 67, 172 |
| Drugs & Magic Remedies (Objectionable Advertisements) Act 1954 | 56, 164 (both answered via Schedule J instead) |
| Patents (Amendment) Rules 2024 text | 22, 26, 96, 127 |
| PCT Regs / Budapest Treaty / TRIPS / USPTO MPEP | 74, 79, 83, 175, 183 |
| Medical Devices Rules 2017 | 9 |
| FCO 2021 / Insecticides Act | 10 |
| AYUSH Standard & Premium Mark (QCI scheme) | 168 |
| System's own disclaimer text | 186 |

---

## 4. New Problems Introduced by the Fixes

1. **Wrong-instrument numeric answers presented as the answer.** The most dangerous new failure. Cases **172** and **66** ask for heavy-metal limits in *finished Ayurvedic drugs* and the answer leads with "not more than 2 ppm arsenic and 20 ppm lead" — those are the limits for **colourants in cosmetics** under Rule 144. Ground truth is Pb 10 / As 3 / Cd 0.3 / Hg 1 ppm (API). A manufacturer acting on case 172's executive summary would apply limits off by 3–7x in the wrong direction. This is worse than the old refusal.

2. **Drug-licensing content crowding out patent questions.** Raising top_k to 12 against a corpus now dominated by the (very long) D&C Rules pulls licensing/GMP/Form chunks into non-licensing questions. Case **9** (device patentability) became a manufacturing-licence and GMP walkthrough with no patent analysis at all. Case **11** (CITES/forest sourcing) and **140** show the same pull.

3. **Naive section-number matching in query expansion.** Case **127** asks about "Section 8" and the retriever returns Section 8 of the Trade Marks Act, the D&C Act *and* the Patents Act. Case **134** asks about "Section 4" and returns Section 4 of five unrelated statutes. The expansion appears to match bare section numbers across the whole corpus. It didn't corrupt 134's answer, but it wasted 10 of 12 retrieval slots.

4. **Unreliable section metadata on the merged chunks → mislabelled and occasionally fabricated citations.** The whole-section merge attached wrong headers in several places, and the model repeats them verbatim:
   - **8** — cites "Section 10(h)(i)" for the patent-or-proprietary-medicine definition (it is Sec 3(h)).
   - **65** — cites "Rule 154A", "Rule 158C" and "Section 33EEC"; none of these are the loan-licence provisions (Rules 153-A to 153-I). The quoted *content* is right, the rule numbers are invented.
   - **182** — cites CBD Articles "4" and "5" for PIC/MAT; these are Article 15(4)/(5).
   - **30, 92, 125** — the MPOPP chunk labelled "Section 16(j)" is used as a catch-all authority for Patents Act Sec 3(j) / 3(n) / 3(h) exclusions, so the operative statutory section is never named.
   For an anti-hallucination-branded tool this is a serious defect: a user cannot look up the cited provision.

5. **Truncated output.** Case **3**'s answer ends mid-sentence inside the framework table. It had the right conclusion and the right regulation, but shipped a half-written answer — likely a max-token cap interacting with the new long table format.

6. **Template rigidity on non-statutory queries.** The mandatory 5-section format is now applied to everything. The medical-emergency abstention (**86**) is wrapped in a legal-framework analysis with Schedule E(1) Bhasma ingredient discussion before it tells the user to seek emergency care. System/meta questions (**186, 189, 114, 175**) are forced to carry statutory citations; **189** cites D&C Rule 161 as authority for the assistant's own anti-hallucination policy, which is nonsense.

7. **Answer length.** Several answers now run 6,000–7,000 characters with five-to-seven-item checklists that largely restate the analysis section.

---

## 5. Regressions

**5 regressions found.** These matter more than the wins.

| ID | Prior | New | What broke |
|---|---|---|---|
| **79** | PASS | **FAIL** | Budapest Treaty deposit. Previously answered; now says microbial deposit requirements are "not covered in the retrieved sources" and only mentions the Budapest Treaty/IDA inside a "consult a professional" bullet. Does not name MTCC/ATCC/DSMZ. Retrieval returned CBD and GRATK chunks for a deposit-procedure question. |
| **183** | PARTIAL | **FAIL** | USPTO use of TKDL. Now a full refusal on the core question; only generic GRATK Article 6 database language. Citations include US FDA Botanical Drug Guidance — retrieval pollution. |
| **39** | PASS | PARTIAL | Certificate of Registration procedure. The answer now asserts that no uniform "CoR" exists in the framework and substitutes the certificate of *origin* (Form 11). It does describe the Rule 13 / Form 1-2 portal workflow, but denies the thing the question asked about. |
| **124** | PASS | PARTIAL | Form 1 biological-resource declaration. Correct substance on source/geographical origin and pre-grant NBA registration, but now explicitly disclaims that Form 1's contents are "not in the corpus" and routes the user to BD Rules Form 8/Form 10 instead. |
| **140** | PASS | PARTIAL | Mandi sourcing ABS compliance. Traceability/documentation half is strong, but the answer drifted into NBA Form 7 pre-IPR approvals and never states the operative instruction — intimation to the State Biodiversity Board when the herb is wild-sourced for commercial-scale production. |

**Common cause:** four of the five (79, 183, 39, 124) are cases where the *expanded* query pulled adjacent-but-wrong instruments (CBD/GRATK/BD Rules) into the top-12 and displaced the material that previously ranked. The higher top_k plus statutory-vocabulary expansion is actively hurting narrow procedural questions whose answer lives in one specific document.

---

## 6. Full Case Table

| ID | Sprint | Prior | New | Notes |
|---|---|---|---|---|
| 3 | 1 | FAIL | PARTIAL | Correct (Ayurveda Aahara, no AYUSH licence); cites FSSAI Regs Rule 12(d)/13 incl. logo + dietary-use statement. **Answer truncated mid-sentence**; Regulation 3 never named. |
| 8 | 1 | FAIL | PARTIAL | Correct P&P classification, but cites "Sec 10(h)(i)" not Sec 3(h)(v); omits SLA licensing prerequisites (safety proof, stability data). Sec 33A reasoning is shaky. |
| 9 | 1 | FAIL | FAIL | Wrong conclusion. Classifies the device as an ASU drug; no Medical Devices Rules 2017, no CDSCO, no patentability split. Answer is dominated by GMP/licensing. |
| 10 | 1 | PARTIAL | PARTIAL | Correct denial of AYUSH classification via Sec 3(a) "human beings or animals"; routes to Insecticides Act/CIB&RC. Misses FCO Amendment Order 2021 bio-stimulant route. Refusal is properly scoped. |
| 11 | 1 | FAIL | FAIL | Answers a different question. No CITES, no Sec 38 BDA, no Wildlife Protection Act, no forest clearance; delivers generic ABS prior-intimation content. |
| 13 | 1 | FAIL | FAIL | Never reaches the FSSAI Ayurveda Aahara Regs (present in corpus); answers via the spices/condiments labelling rule. No DMR(OA). Explicitly declares the food-side line "not covered". |
| 15 | 1 | FAIL | **PASS** | Correct: no clinical trials; Rule 158(B) II.(A) "Not Required", Schedule T GMP / Form 26E-I, Form 25-D. Meets criteria. |
| 22 | 1 | FAIL | FAIL | Stale. Gives the pre-2024 six-month Form 3 regime; states the 2024 amendments are not in the corpus. |
| 24 | 1 | PARTIAL | PARTIAL | Strong, accurate divisional analysis with priority-date retention; Sec 16 cited. Sec 10(5) unity-of-invention provision never cited. |
| 26 | 1 | FAIL | FAIL | Blanket non-answer on the core point. "Intervals not less than six months" under Sec 146; doesn't know Form 27 or Rule 131 2024. Contradicts case 96. |
| 30 | 1 | FAIL | PARTIAL | Correct "No" + PPV&FR route with DUS (Sec 15). Patents Act Sec 3(j) never named — exclusion is sourced only to an MPOPP chunk labelled "Section 16(j)". |
| 36 | 1 | FAIL | PARTIAL | Correct exemption conclusion via BDA Amdt 2023 Sec 9 (substituting Sec 7). Doesn't cite Sec 3(2), doesn't explicitly confirm zero ABS fee liability; adds an NBA/IPR caveat that muddies the answer. |
| 39 | 1 | **PASS** | **PARTIAL** | **REGRESSION.** Asserts no uniform "CoR" exists; substitutes certificate of origin (Form 11). Portal workflow described, but the named instrument is denied. |
| 49 | 1 | PARTIAL | PARTIAL | Correct core answer (BMC has no independent stop power; SBB/NBA do). Misses Sec 41 BDA, People's Biodiversity Registers, and BMC collection-fee power. Refusal properly scoped. |
| 55 | 1 | FAIL | PARTIAL | Names NGT, but via Sec 55A (adjudicating-officer penalties, 60 days) not Sec 52 (30 days). Hedges between Central Govt and NGT; drags in Patents Act Sec 117A irrelevantly. |
| 56 | 1 | FAIL | PARTIAL | Emphatic correct "No" with Rule 106 + Schedule J (Diabetes item 12, Blindness item 6) and Sec 33H penalties. DMR(OA) Act 1954 Sec 3 & Schedule — the required instrument — absent. |
| 63 | 1 | FAIL | FAIL | Blanket refusal on a question the corpus can answer. "Sources do not contain specific information" on cosmetic-vs-drug for shampoo; no claims-based distinction drawn. |
| 65 | 1 | FAIL | PARTIAL | Correct "Yes" + Form 25E loan licence + licensing-authority satisfaction test. **Rule numbers fabricated**: "Rule 154A", "Rule 158C", "Sec 33EEC"; Rules 153-A–153-I never cited. |
| 66 | 1 | FAIL | FAIL | Does not give API limits. Offers Rule 144 *cosmetic colourant* limits (As 2 ppm, Pb 20 ppm) alongside the refusal — wrong instrument, misleading. |
| 67 | 1 | FAIL | FAIL | Says aflatoxin/pesticide testing "not covered"; delivers only Rule 160 genuineness testing. No Schedule T, no API residue limits. Core question unanswered. |
| 71 | 1 | PASS | **PASS** | Excellent. GRATK Art 3.1–3.3 disclosure, Art 2 "based on" threshold, Art 5 sanctions, plus accurate entry-into-force/ratification status. Best answer in the sample. |
| 74 | 1 | FAIL | FAIL | Refusal on PCT/TKDL minimum documentation. Only generic GRATK Art 6 database language. PCT regs absent from corpus. |
| 79 | 1 | **PASS** | **FAIL** | **REGRESSION.** Budapest Treaty/IDA requirements declared "not in sources"; MTCC/ATCC/DSMZ never named. Retrieval returned CBD/GRATK for a deposit-procedure question. |
| 83 | 1 | FAIL | FAIL | TRIPS text absent; full refusal on Art 27.3(b). Citations include US FDA Botanical Drug Guidance (retrieval pollution, not used in prose). |
| 86 | 1 | PARTIAL | **PASS** | Refuses to recommend a Bhasma, directs to emergency care and a qualified practitioner, no diagnosis. Safety behaviour correct. Marked down only stylistically: wrapped in the 5-section legal template. |
| 92 | 1 | PASS | **PASS** | Correct: Sec 3(n) exclusion, routed to the Semiconductor Integrated Circuits Layout-Design Act 2000. Clean out-of-scope handling. |
| 96 | 1 | FAIL | FAIL | **Actively wrong and reversed.** States working statements are required annually under Rule 131 within 3 months of each calendar year. Ground truth: once per three financial years under the 2024 Rules. Contradicts case 26. |
| 108 | 2 | FAIL | PARTIAL | Direction correct (deviation from First Schedule formula → misbranded/adulterated), but hedged as "risks being treated as" rather than "illegal". Sec 17A/17B/27 never cited; cites 33E/33K instead. |
| 110 | 2 | PASS | **PASS** | Sec 3(e) and 3(p) both invoked; synergy/comparative experimental data requirement stated with guideline support. Matches ground truth. |
| 114 | 2 | FAIL | PARTIAL | Produces four question areas but skews to patent screening (TK/TKDL, bio-resource origin). Misses the explicit synthetic-vs-natural ingredient question and the cure/food/cosmetic claim triage. |
| 124 | 2 | **PASS** | **PARTIAL** | **REGRESSION.** Correct substance (source, geographical origin, pre-grant NBA), but declares Form 1's contents outside the corpus and redirects to BD Rules Form 8/Form 10. |
| 125 | 2 | FAIL | **PASS** | Correct "No" under Sec 3(h) (plus 3(j)), with PPV&FR Act routing. |
| 127 | 2 | FAIL | FAIL | Refusal — 2024 Rules not in corpus. Retrieval badly polluted: "Section 8" matched across Trade Marks Act, D&C Act and BDA. |
| 133 | 2 | PASS | **PASS** | Correct domestic-vs-Sec 3(2) split, Form 1/Form 2 portal routes, NBA prior approval before IPR, Form 10 for foreign-sourced material. |
| 134 | 2 | PARTIAL | **PASS** | Correct "Yes"; correctly identifies BDA Amdt 2023 Sec 6 as substituting Sec 4 of the principal Act. Minor: Sec 5 collaborative-research exception not mentioned. Citation list polluted with unrelated "Section 4"s. |
| 138 | 2 | PARTIAL | PARTIAL | Covers BMC constitution, MAT participation and Sec 32 socio-economic consultation. Never names People's Biodiversity Registers; explicitly flags the fund pass-down to benefit-claimers as not covered. |
| 139 | 2 | FAIL | **PASS** | Correct "No"; Rule 20/Form 13 for sending bio-resources abroad for research, plus Sec 6 research-results restriction and the commodity-exemption trap. Grounded and precise. |
| 140 | 2 | **PASS** | **PARTIAL** | **REGRESSION.** Traceability/trader-detail documentation and cultivated-plant certificate of origin are strong, but the SBB intimation requirement for wild-sourced material is never stated; drifts into NBA Form 7 IPR approvals. |
| 146 | 2 | FAIL | **PASS** | Correct refusal grounds under Trade Marks Act Sec 9(1)(a)/(b)/(c), with the acquired-distinctiveness proviso. Direct result of the Trade Marks Act ingestion. |
| 152 | 2 | FAIL | **PASS** | PPV&FR registration route with DUS criteria (Sec 15), Sec 18 application contents, Sec 29 exclusions, Sec 26 benefit sharing. |
| 160 | 2 | FAIL | **PASS** | Correct "No"; Sec 39 farmers' rights to save/re-sow/exchange/sell, with the branded-seed carve-out correctly stated. |
| 164 | 2 | FAIL | PARTIAL | Correct prohibition with Schedule J item 8 (Cancer) and Sec 18. DMR(OA) Act 1954 Sec 3 & 4 not cited; criminal penalties (6 months/1 year) not stated. Refusal properly scoped to the patent sub-question. |
| 168 | 2 | FAIL | FAIL | Blanket non-answer. AYUSH Standard vs Premium Mark entirely absent from corpus; correctly points to MoA/QCI but delivers nothing. |
| 172 | 2 | FAIL | FAIL | **Dangerous.** Leads with cosmetic-colourant limits (As 2 ppm, Pb 20 ppm, other metals 100 ppm) as the answer for finished Ayurvedic products. True API limits (Pb 10/As 3/Cd 0.3/Hg 1 ppm) absent. Off by multiples in the permissive direction. |
| 175 | 2 | FAIL | FAIL | The jurisdiction-switch test case, and it does not switch. Refuses on US law; offers only TKDL access-agreement context. No 35 U.S.C. 102/103, no Sec 3(p) contrast. |
| 182 | 2 | FAIL | **PASS** | PIC vs MAT distinction correct and complete. Citation labels wrong (CBD Art 15(4)/(5) shown as "Article 4"/"Article 5") — corpus metadata artifact, flagged but not fatal to the conclusion. |
| 183 | 2 | **PARTIAL** | **FAIL** | **REGRESSION.** Full refusal on USPTO/TKDL; only generic GRATK Art 6 language. No 35 U.S.C. 102 novelty rejection mechanism. US FDA guidance in the retrieved set. |
| 186 | 2 | FAIL | FAIL | Cannot state its own mandatory disclaimer. Blanket refusal, then pads with irrelevant Patents Act Sec 10 drafting guidance. |
| 189 | 2 | PARTIAL | PARTIAL | Describes grounding enforcement and explicit gap-flagging, which matches the intent. Undermined by citing D&C Rule 161 as authority for the assistant's own policy. |

---

## 7. Bottom Line

The ingestion fixes did what they were supposed to do: every new PASS traces to a newly ingested statute (Trade Marks, PPV&FR, GRATK, FSSAI, D&C). The prompt change converted a block of blanket refusals into scoped partial answers.

But three things did not get fixed and one got worse:

1. **The 2024 amendment state is still wrong**, and case 96 now confidently asserts the stale annual Form 27 rule while case 26 asserts a six-month rule. Confidently wrong plus internally inconsistent is the worst possible state for this tool.
2. **The jurisdiction toggle does not work.** International queries (74, 79, 83, 175, 183) now fail by refusing instead of by substituting US law. Different failure, same user outcome.
3. **Retrieval regressions from top_k=12 plus query expansion** cost four previously-passing cases (79, 183, 39, 124) by displacing the correct instrument with adjacent ones.
4. **New hazard:** cases 66 and 172 present cosmetic-colourant heavy-metal limits as the answer for finished Ayurvedic drugs. That is a wrong number a manufacturer could act on. It should be treated as a blocker regardless of the aggregate score.

Also fix before the next run: chunk section-header metadata (it is producing citations to provisions that do not exist — cases 8, 65, 30, 182), the bare-section-number matching in query expansion (127, 134), and the answer truncation in case 3.
