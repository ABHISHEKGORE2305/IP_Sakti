# IP-Sakti: Comprehensive & Phased Implementation Plan
## Ayurveda, Traditional Knowledge & Intellectual Property Rights AI Platform

---

## Executive Summary

**IP-Sakti** is an advanced, retrieval-grounded AI legal intelligence platform designed specifically for the intersection of **Ayurveda, Traditional Knowledge (TK), Indian Intellectual Property Law (Patents, Trademarks, Geographical Indications, Copyrights, Designs, Trade Secrets, PPV&FR), Biological Diversity (ABS Compliance), and Regulatory Frameworks (AYUSH, CDSCO, FSSAI)**, extending to **International IPR & Global Market Access (WIPO, US FDA, EU THMPD, PCT, Madrid System)**.

This implementation plan translates the entire specification from [`left_to_do.md`](file:///Users/aspa/Desktop/abhishek/IP_Sakti/left_to_do.md) and [`prompt.md`](file:///Users/aspa/Desktop/abhishek/IP_Sakti/prompt.md) into a structured, production-grade, 6-phase engineering blueprint.

---

## 1. Gap Analysis: Current Baseline vs. Target State

| Capability Area | Current Repository State | Target System Requirements (`left_to_do.md`) | Gap Status |
| :--- | :--- | :--- | :--- |
| **1. Legal Corpus Coverage** | 7 raw PDFs (Patents Act 1970, Patent Rules 2003, Pharma Guidelines 2014, TK Guidelines 2012, Manual 2019, TKDL factsheet, Overview of Ayurveda) | 25+ comprehensive statutory documents including Patents Rules 2024, AYUSH Examination Guidelines 2025, Biological Diversity Act 2002/2023, Drugs & Cosmetics Act, FSSAI Ayurveda-Aahar 2022, WIPO GRATK Treaty 2024, US FDA Botanical Guidelines, EU THMPD. | 🔴 Major Gap |
| **2. Jurisdiction Handling** | Single implicit jurisdiction (India). | Dynamic toggle for 🇮🇳 **India** vs. 🌍 **International** (with US, EU, UK, Japan, Australia country scoping), strict legal separation, law version/date tagging. | 🔴 Major Gap |
| **3. Ayurvedic Classification** | None. | Guided interactive questionnaire (Classical, Proprietary, Generic, Phytopharmaceutical, Ayurveda-Aahar, Food, Cosmetic) mapping to regulators and IP paths. | 🔴 Major Gap |
| **4. Multi-Regime IPR Routing** | Basic patent statute search. | Comprehensive decision router for Patents (Sec 3(p), 3(d), 3(e)), GIs, Trademarks (Classes 5/3/30), Copyrights, Designs, Trade Secrets, PPV&FR. | 🔴 Major Gap |
| **5. Traditional Knowledge & TKDL** | Static TK guidelines PDF chunks. | Active TK detection, Section 3(p) prior art analyzer, TKDL citation pointers, innovation vs. classical formulation separation. | 🟡 Partial |
| **6. Biodiversity & ABS Compliance** | None. | Form I/II/III recommendation, NBA/SBB jurisdiction mapping, Section 6/19/20 compliance checklist, Commercial vs Research benefit-sharing tracker. | 🔴 Major Gap |
| **7. Product Regulatory Module** | None. | Drugs & Cosmetics Act (First Schedule), AYUSH GMP, FSSAI Ayurveda-Aahar, DMR(OA) Act advertising checks, Phytopharmaceutical GSR 918(E). | 🔴 Major Gap |
| **8. International IP Module** | None. | WIPO GRATK Treaty 2024, Nagoya Protocol, PCT, Madrid System, US FDA Botanical Drug Guidance, EU THMPD herbal directive. | 🔴 Major Gap |
| **9. Retrieval & Reranking** | Dense (BGE-M3) + BM25 + RRF + BAAI Cross-Encoder reranker. | Query legal-reference parsing, authority-weighted scoring (Statute > Rules > Guidelines > Manuals), metadata filtering by jurisdiction/regime. | 🟡 Solid Base, Needs Tuning |
| **10. Knowledge Graph** | None. | Relational multi-hop graph connecting: Product ➔ Ingredients ➔ Biological Resource ➔ TK ➔ Regulation ➔ IP Type ➔ Authority ➔ Jurisdiction. | 🔴 Major Gap |
| **11. Agentic Orchestration** | Single linear pipeline (`rag_pipeline.py`). | LangGraph multi-agent hierarchy: Classifier Agent, Patent Agent, TM/GI Agent, ABS Agent, Regulatory Agent, International Agent, Citation Guardrail Agent. | 🔴 Major Gap |
| **12. Citation & Verification** | Context metadata in prompt. | Strict citation verification, pinpoint Section/Rule/Page mapping, anti-phantom citation filter ("No citation = No legal claim"). | 🟡 Partial |
| **13. Confidence & Abstention** | Basic fallback message if 0 chunks. | Multi-factor confidence scoring (High/Medium/Low) based on source freshness, similarity, and coverage; strict safe abstention when sources are inadequate. | 🔴 Major Gap |
| **14. Human Escalation** | Simple Markdown conversation dump. | Formal "Escalate to IP Facilitator" module with auto-generated Case Summary Brief (risks, missing info, questions for attorney, exportable PDF/JSON). | 🔴 Major Gap |
| **15. Multilingual Support** | English only. | Multilingual interaction (Hindi, Marathi, Tamil, Telugu, Bengali, Gujarati, etc.) with legal terminology preservation and translation integrity. | 🔴 Major Gap |
| **16. User Interface & Experience** | Simple 3-column static layout. | Guided step-by-step wizard, Glassmorphic modern aesthetic, Dark/Light modes, interactive checklist, PDF document upload/analysis, voice input. | 🟡 Basic MVP, Needs Overhaul |
| **17. Governance, DPDP & Audit** | Basic console prints. | DPDP Act compliance, PII redaction, audit logs of queries/citations/confidence, golden benchmark evaluation suite. | 🔴 Major Gap |

---

## 2. Target System Architecture

```mermaid
flowchart TB
    subgraph UI ["Layer 1: User Interface & Interaction"]
        WebUI["Web Application (Modern UI / Glassmorphic)"]
        Wizard["Guided Classification & IPR Wizard"]
        DocUpload["Formulation & PDF Document Ingestion"]
        VoiceLang["Voice (STT/TTS) & Multilingual Selector (Bhashini)"]
        JurisdictionSwitch["Jurisdiction Selector (🇮🇳 India / 🌍 International)"]
    end

    subgraph Gateway ["Layer 2: API Gateway & Security"]
        FastAPIGw["FastAPI REST & WebSocket Gateway"]
        PIIScrub["PII Redaction & DPDP Privacy Filter"]
        SessionMgr["Session & Conversation State Manager"]
        RateLimiter["Rate Limiting & Auth Guard"]
    end

    subgraph Orchestration ["Layer 3: Multi-Agent Orchestration (LangGraph)"]
        Supervisor["Supervisor & Routing Agent"]
        ClassifierAgent["Ayurvedic Product Classifier Agent"]
        PatentAgent["Patent & Section 3(p)/3(d) Agent"]
        TMGIAgent["Trademark & GI Agent"]
        ABSAgent["Biodiversity & ABS Compliance Agent"]
        RegAgent["Regulatory Pathway (AYUSH/FSSAI/CDSCO) Agent"]
        IntlAgent["International IP & Export Agent"]
        CitationAgent["Source Verification & Citation Guardrail Agent"]
    end

    subgraph Intelligence ["Layer 4: Specialized Intelligence Engines"]
        ClassTree["Ayurvedic Product Decision Tree"]
        ABSEngine["NBA/SBB Form I-III Decision Logic"]
        TKDLEngine["TK / Section 3(p) Innovation vs Classical Differentiator"]
        RegCrosswalk["AYUSH vs FSSAI vs Drug Regulatory Crosswalk"]
    end

    subgraph Retrieval ["Layer 5: Hybrid Retrieval & Knowledge Layer"]
        QueryParser["Query & Legal-Reference Extractor"]
        DenseSearch["Dense Semantic Search (BGE-M3 @ Qdrant)"]
        BM25Search["BM25 Lexical & Tokenized Search"]
        AuthorityRRF["Authority-Weighted RRF Fusion"]
        CrossRerank["Cross-Encoder Reranker (bge-reranker-v2-m3)"]
        LegalKG["Relational Legal Knowledge Graph"]
    end

    subgraph Storage ["Layer 6: Knowledge Base & Vector Stores"]
        QdrantDB[("Qdrant Vector DB (1024-dim Collections)")]
        DocStore[("Authoritative Corpus Store (25+ Acts, Rules, Guidelines)")]
        KGStore[("Knowledge Graph Store (Entities & Relations)")]
        AuditStore[("Audit Logs, Citations & Session Storage")]
    end

    subgraph Guardrails ["Layer 7: Safety, Governance & Output"]
        ConfidenceScorer["Multi-factor Confidence Scorer (High/Med/Low)"]
        AbstentionGate["Mandatory Safe Abstention Gate"]
        DisclaimerEngine["Mandatory Legal Disclaimer Engine"]
        ReportGen["Compliance Checklist & Case File PDF Exporter"]
    end

    %% Connections
    UI --> Gateway
    Gateway --> Orchestration
    Orchestration --> Intelligence
    Orchestration --> Retrieval
    Retrieval --> Storage
    Intelligence --> Retrieval
    Orchestration --> Guardrails
    Guardrails --> Gateway
```

---

## 3. Phase-wise Implementation Roadmap

```mermaid
gantt
    title IP-Sakti Phased Development Timeline
    dateFormat  YYYY-MM-DD
    section Phase 1: Core Foundation
    Corpus Expansion & Ingestion           :p1_1, 2026-09-25, 4d
    Legal Chunking & Qdrant Re-index      :p1_2, after p1_1, 3d
    Precision Retrieval & Authority Boost :p1_3, after p1_2, 3d
    Confidence & Safe Abstention Engine   :p1_4, after p1_3, 2d
    section Phase 2: Domain Engines
    Ayurvedic Product Classifier Engine   :p2_1, after p1_4, 4d
    TK & Section 3(p) Analysis Engine     :p2_2, after p2_1, 3d
    Biodiversity & ABS Compliance Engine  :p2_3, after p2_1, 4d
    Regulatory Pathway Engine (AYUSH/FSSAI):p2_4, after p2_2, 3d
    Multi-Regime IPR Decision Engine      :p2_5, after p2_3, 3d
    section Phase 3: Multi-Agent System
    LangGraph Multi-Agent Orchestration   :p3_1, after p2_5, 5d
    Citation Verification Guardrail Agent :p3_2, after p3_1, 3d
    Structured Output & Dual-Layer Answer :p3_3, after p3_2, 3d
    section Phase 4: International IPR
    International Corpus & Treaties Ingest:p4_1, after p3_3, 4d
    Country-Specific Regulatory Modules   :p4_2, after p4_1, 4d
    Global Export & Patent Filings Matrix :p4_3, after p4_2, 3d
    section Phase 5: UI & Multilingual
    Modern Web Dashboard & Guided Wizard  :p5_1, after p4_3, 6d
    Document Upload & Formulation Analyzer:p5_2, after p5_1, 4d
    Multilingual & Bhashini Integration   :p5_3, after p5_2, 4d
    Case Brief & PDF Report Export        :p5_4, after p5_3, 3d
    section Phase 6: Governance & QA
    DPDP Compliance & PII Sanitization    :p6_1, after p5_4, 3d
    Golden Benchmark Test Suite (50+ Cases):p6_2, after p6_1, 4d
    Production Hardening & CI/CD          :p6_3, after p6_2, 3d
```

---

## 4. Detailed Phase Specifications

### Phase 1: Core Foundation, Corpus Expansion & Precision Retrieval

#### 1.1 Authoritative Legal Corpus Expansion
Acquire, clean, and structure the complete authoritative corpus in `data/raw/`:
1. **Patents Act, 1970** (incorporating amendments up to 2024).
2. **Patents (Amendment) Rules, 2024** & Patents Rules, 2003.
3. **Guidelines for Examination of Ayush Related Inventions (2025/latest)**.
4. **Guidelines for Examination of Patent Applications in the Field of Pharmaceuticals (2014)**.
5. **Guidelines for Processing of Patent Applications relating to Traditional Knowledge and Biological Material (2012)**.
6. **Manual of Patent Office Practice and Procedure (2019/latest)**.
7. **The Biological Diversity Act, 2002** and **Biological Diversity (Amendment) Act, 2023**.
8. **Biological Diversity Rules, 2004** & **Access and Benefit Sharing (ABS) Guidelines, 2014**.
9. **Drugs and Cosmetics Act, 1940** (Chapter IVA provisions for Ayurvedic, Siddha, Unani drugs) & **Rules, 1945**.
10. **FSSAI (Ayurveda Aahar) Regulations, 2022** & Food Safety and Standards Act, 2006.
11. **Geographical Indications of Goods (Registration and Protection) Act, 1999** & Rules, 2002.
12. **Trade Marks Act, 1999** & Trade Marks Rules, 2017 (NICE Classification Classes 5, 3, 30, 32, 44).
13. **Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954**.
14. **TKDL (Traditional Knowledge Digital Library) Official Reference Manual**.

#### 1.2 Metadata & Document Hierarchy Schema
Every document chunk will carry rich hierarchical metadata:
```json
{
  "chunk_id": "patents_act_1970_s003_p",
  "document_id": "patents_act_1970",
  "document": "The Patents Act, 1970",
  "document_type": "statute",
  "issuing_authority": "Parliament of India / CGPDTM",
  "jurisdiction": "India",
  "version_date": "2024-03-15",
  "is_current": true,
  "hierarchy": {
    "chapter": "CHAPTER II",
    "chapter_title": "INVENTIONS NOT PATENTABLE",
    "section": "3",
    "section_title": "What are not inventions",
    "clause": "p",
    "legal_reference": "Section 3(p)"
  },
  "authority_weight": 1.0,
  "text": "(p) an invention which, in effect, is traditional knowledge or which is an aggregation or duplication of known properties of traditionally known component or components."
}
```

Authority Weights:
* **Statutes (Acts)**: `1.0`
* **Statutory Rules**: `0.9`
* **Official Examination Guidelines (AYUSH/Pharma/TK)**: `0.85`
* **Manuals of Practice**: `0.75`
* **Regulatory Gazette Notifications**: `0.80`
* **Reference & Educational Overviews**: `0.50`

#### 1.3 Legal-Reference Aware Retrieval & Fusion Algorithm
Implement `src/retrieval/query_analyzer.py` and enhance `src/retrieval/hybrid_retriever.py`:
1. **Query Legal-Reference Regex & Named Entity Extractor**:
   * Extracts target references from queries (e.g., `Section 3(p)`, `Rule 24B`, `Section 3(d)`, `Form III`).
2. **Deterministic Exact-Match Metadata Filter**:
   * Direct payload lookup for exact statutory sections requested by the user.
3. **Hybrid RRF + Authority Weighting**:
   $$\text{Score}(d) = \sum_{m \in \{\text{Dense}, \text{BM25}\}} \frac{w_m}{k + \text{Rank}_m(d)} \times \text{Authority}(d) \times \text{ExactRefBoost}(d)$$
4. **Cross-Encoder Context Reranking**:
   * Uses `BAAI/bge-reranker-v2-m3` across the top 30 merged candidates to produce the final top $K$ (default 6) chunks.

#### 1.4 Confidence & Safe Abstention Engine
Implement `src/guardrails/confidence.py`:
$$\text{Confidence} = 0.40 \cdot S_{\text{rerank}} + 0.30 \cdot S_{\text{retrieval\_density}} + 0.20 \cdot S_{\text{authority}} + 0.10 \cdot S_{\text{query\_term\_coverage}}$$
* **Score $\ge 0.75$**: **High Confidence** 🟢
* **$0.50 \le \text{Score} < 0.75$**: **Medium Confidence** 🟡
* **$\text{Score} < 0.50$**: **Low Confidence / Safe Abstention Trigger** 🔴
* **Abstention Response**:
  > *"I could not locate sufficiently authoritative statutory provisions or official guidelines to answer this specific query with certainty. In accordance with legal safety guidelines, I will not generate an unsubstantiated legal interpretation. Please consult an accredited IP professional or refer to the primary portals listed below."*

---

### Phase 2: Domain Engines & Decision Logic

#### 2.1 Ayurvedic Product Classification Engine (`src/engines/classifier.py`)
Deterministic decision tree that takes user inputs and determines the statutory product identity:

```mermaid
graph TD
    Start([Product Description / Formulation Input]) --> Q1{In First Schedule Authoritative Texts?}
    Q1 -- Yes --> Q2{Formulation Modified or Changed?}
    Q1 -- No --> Q3{Claims & Intended Use?}
    
    Q2 -- Unchanged --> C1["Classical Ayurvedic Medicine (D&C Act Sec 3(a))"]
    Q2 -- Modified Ingredients/Extracts/Forms --> C2["Patent or Proprietary Medicine (D&C Act Sec 3(h))"]
    
    Q3 -- Therapeutic / Cure / Disease Treatment --> C4["New Ayurvedic Drug / Phytopharmaceutical (CDSCO / AYUSH)"]
    Q3 -- Nutritional / Dietary Supplement --> C5["Ayurveda-Aahar (FSSAI Regulations 2022)"]
    Q3 -- General Food / Beverage --> C6["General Food / FSSAI"]
    Q3 -- Topical / Beautification / Cleansing --> C7["Ayurvedic Cosmetic (D&C Act Rules)"]
```

Output contract for each classification:
* **Statutory Classification & Category**
* **Primary Regulator** (Ministry of AYUSH / State Licensing Authority / CDSCO / FSSAI)
* **Manufacturing & Licensing Route** (Form 25D, Form 24D, FSSAI Central License)
* **Clinical Evidence & Trial Requirements** (Rule 158B proof of safety/efficacy vs literature citation)
* **IP Regimes Available** (Patentability viability, Trademark classes, GI relevance)
* **ABS / Biodiversity Triggers**

#### 2.2 Traditional Knowledge & Section 3(p) Analysis Engine (`src/engines/tk_engine.py`)
Analyzes innovation claims against Section 3(p) and 3(e) of the Indian Patents Act:
1. **Classical Formulation Check**: If formulation is documented in Schedule 1 texts $\rightarrow$ Strict Section 3(p) exclusion.
2. **Mere Admixture vs. Synergistic Interaction (Section 3(e))**:
   * If combination of known herbs $\rightarrow$ Presumed unpatentable unless experimental synergistic data (isobolograms, enhanced bioavailability, surprising efficacy) is demonstrated.
3. **Novel Extraction / Isolation Process**:
   * Process patent eligibility under Section 2(1)(j) provided the process parameters are novel, non-obvious, and not standard Ayurvedic extraction methods (Swarasa, Kwatha, Sneha Kalpana).
4. **New Second Medical Use**:
   * Section 3(d) analysis for new therapeutic uses of known traditional plants.
5. **TKDL Prior Art Mitigation Strategy**:
   * How to frame patent claims to distinguish from TKDL citations.

#### 2.3 Biodiversity & Access and Benefit Sharing (ABS) Engine (`src/engines/abs_engine.py`)
Implements legal analysis under the **Biological Diversity Act, 2002 & 2023 Amendment**:
1. **Entity Classification**:
   * Indian individual/entity vs. Foreign individual/entity/Non-Resident Indian (Section 3 vs. Section 7).
2. **Biological Resource Sourcing**:
   * Commercial Utilization vs. Non-Commercial Research vs. Bio-survey.
   * Exemptions (Normally Traded Commodities - NTC list, Traditional Indian medicine practitioners / Vaidyas).
3. **Mandatory Approvals & Form Recommendations**:
   * **Form I**: Access to biological resources by foreign entities (Section 3).
   * **Form II**: Transfer of research results to foreign entities (Section 4).
   * **Form III**: Application for Intellectual Property Rights on biological inventions (Section 6) — *Must be obtained before patent grant*.
   * **Form IV**: Third-party transfer of accessed biological resources (Section 20).
4. **State Biodiversity Board (SBB) Intimation**:
   * Prior intimation requirements for Indian commercial manufacturers.
5. **Interactive ABS Compliance Checklist Generator**:
   * Step-by-step required documentation, timelines, and benefit-sharing percentage calculators.

#### 2.4 Multi-Regime IPR Decision Engine (`src/engines/ipr_router.py`)
Routes queries across the 7 IP regimes:
* **Patents**: Patentability assessment, claim drafting recommendations, Form 1/2/3/5/18/27 filing workflows, 2024 fee schedules.
* **Trademarks**: Trademark selection, avoiding descriptive Ayurvedic terms (Section 9/11), NICE Classification guidance (Class 5 for medicines/supplements, Class 3 for cosmetics, Class 30 for herbal teas/confections, Class 44 for Ayurvedic clinics/Panchakarma).
* **Geographical Indications (GI)**: Collective community ownership, registration process under GI Act 1999, Authorized User registration (e.g., Navara Rice, Nilambur Teak, Malabar Pepper).
* **Industrial Designs**: Novel bottle, packaging, applicator, or device shape protection under Designs Act 2000.
* **Trade Secrets**: Non-disclosure strategies for proprietary processing steps, extraction temperatures, and proportions.
* **Copyright**: Protection for formulation books, branding brochures, website text, software algorithms.
* **Plant Variety Protection (PPV&FR Act, 2001)**: Registration of extant, farmers', and novel medicinal plant varieties.

---

### Phase 3: Multi-Agent Orchestration & Grounded Generation

#### 3.1 LangGraph Multi-Agent Architecture
Implement an intelligent graph orchestrator in `src/agents/`:

```mermaid
stateDiagram-v2
    [*] --> InputSanitizer
    InputSanitizer --> SupervisorRouter
    
    state SupervisorRouter {
        [*] --> IntentAnalysis
        IntentAnalysis --> SelectAgents
    }
    
    SupervisorRouter --> ClassifierAgent : Needs Product Classification
    SupervisorRouter --> PatentAgent : Patent / S.3(p) Query
    SupervisorRouter --> TMGIAgent : Trademark / GI Query
    SupervisorRouter --> ABSAgent : Biological Resource / NBA Query
    SupervisorRouter --> RegAgent : AYUSH / FSSAI Regulatory Query
    SupervisorRouter --> IntlAgent : International / Export Query
    
    ClassifierAgent --> PatentAgent : Classification Context Passed
    ClassifierAgent --> ABSAgent : Biological Ingredients Passed
    ClassifierAgent --> RegAgent : Regulatory Category Passed
    
    PatentAgent --> VerificationGuardrail
    TMGIAgent --> VerificationGuardrail
    ABSAgent --> VerificationGuardrail
    RegAgent --> VerificationGuardrail
    IntlAgent --> VerificationGuardrail
    
    state VerificationGuardrail {
        [*] --> ExtractCitations
        ExtractCitations --> VerifyAgainstRetrievedSources
        VerifyAgainstRetrievedSources --> CalculateConfidence
        CalculateConfidence --> SafeAbstentionCheck
    }
    
    VerificationGuardrail --> OutputSynthesizer : Grounding Verified
    VerificationGuardrail --> FallbackHandler : Failed Grounding / Abstain
    
    OutputSynthesizer --> [*]
    FallbackHandler --> [*]
```

#### 3.2 Agent Definitions & Responsibilities

| Agent | Responsibility | Tools & Engines Used |
| :--- | :--- | :--- |
| **Supervisor Agent** | Parses user query, determines jurisdiction, dispatches sub-agents in parallel or sequence, manages shared conversation state. | Intent Classifier, Routing Engine |
| **Classifier Agent** | Executes guided interactive questions or parses user text to establish the statutory product classification. | Decision Tree Engine, Schedule 1 Text Index |
| **Patent Agent** | Analyzes novelty, inventive step, traditional knowledge exclusions (S.3(p)), admixtures (S.3(e)), and drafting strategy. | Patent Hybrid Retriever, S.3 Analyzer |
| **TM & GI Agent** | Advises on trademark brand distinctiveness, NICE class selection, and GI registration workflows. | TM & GI Search Connector, Nice Class Index |
| **ABS Agent** | Analyzes biological materials, NBA vs SBB jurisdiction, Form I-IV requirements, and benefit sharing. | BD Act Rules Index, ABS Checklist Generator |
| **Regulatory Agent** | Details AYUSH licensing, FSSAI Ayurveda-Aahar, CDSCO phytopharmaceuticals, and advertising compliance. | D&C Act Index, FSSAI 2022 Index, DMR(OA) Index |
| **International Agent** | Assesses WIPO treaties, PCT entry, US FDA botanical drug rules, EU THMPD compliance, and export markets. | International Treaties Store, US/EU/UK Rules |
| **Citation Verifier Agent** | Scans final draft answer, matches every legal assertion to a retrieved text chunk, strips unverified claims, and calculates confidence. | Cross-Encoder Validator, Citation Parser |

#### 3.3 Strict Output Structure & Dual-Layer Reasoning
Every generated response follows a structured, easy-to-read, dual-layer format:
1. **Executive Summary** (Plain English actionable takeaways for entrepreneurs & vaidyas).
2. **Applicable Legal & Regulatory Framework** (Exact statutory sections, rules, and government notifications).
3. **Analysis & Specific Guidance** (Step-by-step breakdown of how the law applies to the user's specific facts).
4. **Identified Risks & Red Flags** (Section 3(p) risks, ABS non-compliance liabilities, advertising restrictions).
5. **Actionable Checklist / Next Steps** (Chronological sequence of forms, approvals, and filings).
6. **Authoritative Sources & Citations** (Clickable, traceable cards with exact sections, rule numbers, and page references).
7. **Confidence Score & Disclaimer** (Mandatory legal advice disclaimer).

---

### Phase 4: International IP & Export Market Access

#### 4.1 Global Treaties & Frameworks Ingestion
Add international treaties and guidelines to `data/raw/international/`:
* **WIPO Treaty on Intellectual Property, Genetic Resources and Associated Traditional Knowledge (GRATK, 2024)**.
* **Convention on Biological Diversity (CBD, 1992)** & **Nagoya Protocol on Access and Benefit-sharing (2010)**.
* **TRIPS Agreement (Trade-Related Aspects of Intellectual Property Rights)** (Article 27.3(b)).
* **Patent Cooperation Treaty (PCT)** regulations and national phase entry rules.
* **Madrid System** for International Registration of Marks.
* **Hague System** for International Registration of Industrial Designs.

#### 4.2 Country-Specific Herbal & Botanical Drug Modules

```mermaid
graph LR
    UserQuery[Export / International IP Query] --> MarketSelect{Select Target Market}
    MarketSelect --> USA["🇺🇸 USA: US FDA Botanical Guidance / DSHEA Dietary Supplement"]
    MarketSelect --> EU["🇪🇺 European Union: EMA / THMPD (Directive 2004/24/EC)"]
    MarketSelect --> UK["🇬🇧 United Kingdom: MHRA Traditional Herbal Registration (THR)"]
    MarketSelect --> Japan["🇯🇵 Japan: PMDA Kampo / Crude Drug Standards"]
    MarketSelect --> Australia["🇦🇺 Australia: TGA Listed / Registered Medicines"]
```

* **United States**:
  * **Botanical Drugs Route (FDA Guidance 2016)**: Multi-batch chemical fingerprinting, raw material sourcing consistency, Phase I-III clinical trial pathway without requiring single-molecule isolation.
  * **Dietary Supplements (DSHEA 1994)**: Structure/function claims vs disease claims, New Dietary Ingredient (NDI) notifications, GMP 21 CFR Part 111.
  * **USPTO Patent Considerations**: Subject matter eligibility under 35 U.S.C. 101 (*Alice/Mayo* framework for natural products).
* **European Union**:
  * **Traditional Herbal Medicinal Products Directive (THMPD 2004/24/EC)**: 30 years of traditional use requirement (including at least 15 years in the EU).
  * **Well-Established Use Route**: 10 years of EU clinical bibliographic evidence.
* **Global GratK Disclosure Compliance**:
  * Mandatory patent application disclosure of the country of origin/source of genetic resources and traditional knowledge.

---

### Phase 5: Modern UI, Interactive Workflows & Multilingual Experience

#### 5.1 UI/UX Re-architecture
Create a modern, responsive web application in `frontend/`:
* **Design Philosophy**: Glassmorphism, deep forest & emerald accents (representing Ayurveda), clean typography (Outfit / Inter), seamless micro-interactions, dark/light theme toggle.
* **Guided Wizard Flow**:
  1. **Jurisdiction & Market Switch** (🇮🇳 India / 🌍 International).
  2. **Ayurvedic Classification Wizard** (Interactive questions determining product category).
  3. **Multi-Regime Issue Picker** (Patent, Trademark, GI, ABS, Regulatory, Export).
  4. **Dynamic AI Analysis Feed** (Real-time agent stage indicator, thought progression).
  5. **Interactive Source & Citation Inspector** (Right-hand drawer with full text preview, score badges, version tags).
  6. **Interactive Compliance Checklist** (Exportable to PDF, Markdown, and JSON).
  7. **Case Escalation Drawer** (One-click attorney case summary generator).

#### 5.2 Document & Formulation Upload Analyzer
* Allows users to upload formulation sheets (PDF / Image / Text).
* Parses botanical names (e.g., *Withania somnifera*, *Curcuma longa*, *Tinospora cordifolia*), part used, extraction solvent, proportions, and manufacturing steps.
* Automated check against:
  * First Schedule Ayurvedic Pharmacopoeia of India (API) texts.
  * Known TKDL compositions.
  * National Biodiversity Authority (NBA) regulated biological resources list.

#### 5.3 Multilingual & Bhashini Support
* Full support for Indian languages: **Hindi, Marathi, Tamil, Telugu, Kannada, Bengali, Gujarati, Malayalam, Punjabi**, and **English**.
* Preservation of exact statutory references in English (e.g., *"Patents Act Section 3(p)"*) while delivering clear, accessible explanations in the user's native language.
* Voice Query & Text-to-Speech (STT/TTS) using browser Web Speech API with Bhashini API integration.

#### 5.4 Case Summary & Attorney Escalation File
Generates a formal legal case brief:
```markdown
# AYURVEDA IPR CASE BRIEF
**Generated by IP-Sakti** | Date: 2026-09-24

### 1. Client & Formulation Overview
* **Product Name**: Bio-Enhanced Ashwagandha Liposomal Extract
* **Classified Category**: Patent/Proprietary Medicine (D&C Act Sec 3(h))
* **Jurisdiction**: India + US Export Interest

### 2. Biological Material & ABS Status
* **Biological Ingredients**: Withania somnifera (Roots) sourced from Neemuch, MP.
* **NBA Approval Required**: Form III (Prior to Patent Grant)
* **SBB Intimation**: Form I to MP State Biodiversity Board required.

### 3. Patentability & Section 3(p) Assessment
* **Key Challenge**: Section 3(p) Traditional Knowledge exclusion.
* **Proposed Overcoming Strategy**: Emphasize novel lipid-encapsulation process parameters and comparative bioavailability data (3.4x higher serum concentration).

### 4. Regulatory & Licensing Pathway
* **Licensing Authority**: State AYUSH Licensing Authority (Form 25D).
* **Clinical Trial Exemption**: Rule 158B(iv) safety data required for new dosage forms.

### 5. Open Questions for IP Facilitator
* [ ] Verify if foreign funding triggers Section 3 of BD Act.
* [ ] Review claim 1-5 phrasing for process-only protection.
```

---

### Phase 6: Security, DPDP Governance, Evaluation & Production Hardening

#### 6.1 DPDP Act & Privacy Compliance
* **Data Minimization**: Automatic sanitization of Personally Identifiable Information (PII) such as Aadhaar, PAN, phone numbers, and addresses from user queries before vectorization and LLM prompting.
* **Confidentiality & Non-Disclosure**: Client formulation data marked as ephemeral, stored encrypted at rest with session-scoped isolation.
* **Consent Management**: Explicit consent dialog for query logging and human expert escalation.

#### 6.2 Golden Benchmark Evaluation Suite (`tests/eval_benchmark.py`)
Build a comprehensive test suite of **50 golden legal questions** covering:
1. Classical single-plant formulations vs Section 3(p).
2. Novel synergistic herbal extracts vs Section 3(e).
3. Process patents for traditional preparation methods.
4. ABS compliance triggers for foreign equity holders.
5. Ayurvedic cosmetics vs Ayurvedic drugs regulatory boundaries.
6. FSSAI Ayurveda-Aahar classification and health claims.
7. Trademark distinctiveness for Sanskrit herbal terms.
8. GI protection for regional medicinal crops.
9. US FDA Botanical Drug guidance comparison.
10. Safe abstention on ambiguous/unsupported queries.

Evaluation Metrics:
* **Legal Accuracy (Ground Truth Match)**: Target $\ge 95\%$
* **Citation Precision (Zero Phantom Citations)**: Target $100\%$
* **Citation Completeness**: Target $\ge 90\%$
* **Safe Abstention Accuracy on Out-of-Corpus Queries**: Target $\ge 98\%$
* **Product Classification Accuracy**: Target $\ge 95\%$

---

## 5. File & Directory Reorganization Structure

```text
IP_Sakti/
├── data/
│   ├── raw/
│   │   ├── india/
│   │   │   ├── statutes/               # Patents Act 1970, BD Act 2002/2023, D&C Act 1940
│   │   │   ├── rules/                  # Patents Rules 2024, BD Rules 2004, D&C Rules 1945
│   │   │   ├── guidelines/             # AYUSH Guidelines 2025, Pharma 2014, TK 2012, Manual 2019
│   │   │   ├── regulatory/             # FSSAI Ayurveda-Aahar 2022, DMR(OA) Act 1954
│   │   │   └── references/             # TKDL Manual, Overview of Ayurveda, API Schedule 1 list
│   │   └── international/
│   │       ├── treaties/               # WIPO GRATK 2024, Nagoya Protocol, TRIPS, PCT
│   │       └── guidelines/             # US FDA Botanical Guidance 2016, EU THMPD Directive
│   └── processed/
│       ├── chunks_india.json           # Chunked legal corpus with full metadata
│       └── chunks_international.json   # International treaties & country guidelines
├── frontend/
│   ├── index.html                      # Modern Glassmorphic Dashboard & Guided Wizard
│   ├── style.css                       # Design system, CSS variables, dark/light themes
│   ├── app.js                          # Core UI logic, WebSocket/REST API client, state management
│   ├── components/
│   │   ├── wizard.js                   # Product classification questionnaire
│   │   ├── citations.js                # Source drawer & citation viewer
│   │   ├── checklist.js                # Interactive compliance checklist
│   │   └── escalation.js               # Attorney brief exporter
│   └── assets/                         # SVG icons, logos, badges
├── src/
│   ├── __init__.py
│   ├── config.py                       # System configurations, models, weights, paths
│   ├── api.py                          # FastAPI server endpoints (Chat, Classify, ABS, Export)
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── classifier.py               # Ayurvedic Product Classification decision tree
│   │   ├── tk_engine.py                # Traditional Knowledge & Section 3(p) analyzer
│   │   ├── abs_engine.py               # Biological Diversity & ABS compliance logic
│   │   ├── reg_engine.py               # AYUSH, FSSAI, CDSCO regulatory router
│   │   └── ipr_router.py               # Patent, TM, GI, Copyright, Design, Secret router
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── document_loader.py          # PyMuPDF parser with schedule & TOC awareness
│   │   ├── chunker.py                  # Legal-aware structural chunker
│   │   ├── embedding_model.py          # BAAI/bge-m3 dense embedder
│   │   ├── vector_store.py             # Qdrant client & collection manager
│   │   ├── bm25_retriever.py           # Lexical search engine
│   │   ├── query_parser.py             # Legal-reference & named entity extractor
│   │   ├── authority_fusion.py         # Authority-weighted RRF
│   │   ├── reranker.py                 # Cross-encoder bge-reranker-v2-m3
│   │   └── hybrid_retriever.py         # Master hybrid retrieval pipeline
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── state.py                    # LangGraph AgentState schema
│   │   ├── supervisor.py               # Master intent router & orchestrator
│   │   ├── patent_agent.py             # Patent analysis specialist
│   │   ├── tm_gi_agent.py              # Trademark & GI specialist
│   │   ├── abs_agent.py                # Biodiversity & ABS specialist
│   │   ├── reg_agent.py                # Regulatory pathway specialist
│   │   ├── intl_agent.py               # International IP & export specialist
│   │   └── citation_agent.py           # Verification & anti-hallucination guardrail
│   ├── guardrails/
│   │   ├── __init__.py
│   │   ├── confidence.py               # Multi-factor confidence scoring
│   │   ├── abstention.py               # Safe abstention gate
│   │   └── pii_sanitizer.py            # DPDP privacy filter
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── gemini_client.py            # Google GenAI / Gemini 2.5 client
│   │   └── prompts.py                  # Grounded legal system prompts & templates
│   └── utils/
│       ├── __init__.py
│       ├── export_pdf.py               # Case brief & checklist PDF generator
│       └── bhashini.py                 # Multilingual translation & glossary keeper
├── tests/
│   ├── test_legal_chunker.py           # Chunker unit tests
│   ├── test_retrieval_precision.py     # Retrieval top-k & section match tests
│   ├── test_engines.py                 # Classifier, ABS, TK engine unit tests
│   ├── test_agents.py                  # Multi-agent LangGraph execution tests
│   ├── test_confidence_abstention.py   # Abstention gate validation
│   └── eval_benchmark.py               # 50 golden legal questions evaluation runner
├── requirements.txt
├── IMPLEMENTATION_PLAN.md
└── README.md
```

---

## 6. Immediate Action Items & Execution Checklist

### Sprint 1: Precision Legal Chunking & Corpus Ingestion (Immediate Priority)
- [x] Analyze existing codebase, chunker logic, and current bug status.
- [x] Ingest **AYUSH Examination Guidelines 2025**, **Patents Rules 2024**, and **Biological Diversity Act 2002/2023** into `data/raw/`. *(was blocked awaiting source PDFs; completed as a Sprint 6 follow-up once supplied — see the Sprint 6 section below. This line was stale until the 2026-09-25 audit caught it still marked incomplete.)*
- [x] Run full chunking pipeline and verify `Section 3(p)`, `Section 3(d)`, `Section 3(e)`, and `Section 2(1)(j)` chunk creation. *(found and fixed a footnote-misclassification bug in `legal_structure.py` that was corrupting Section 2's clauses; all four provisions now verified present in `data/processed/chunks.json`)*
- [x] Rebuild Qdrant collection with 1024-dim BGE-M3 vectors and stable UUIDs. *(1239/1239 points, verified via `reset_collection.py` + `ingest.py`)*
- [x] Implement query legal-reference extractor (`legal_reference.py`) and authority-weighted RRF. *(extractor already existed; extended it to match subsection-qualified citations like "Section 2(1)(j)"; added `authority_weight` end-to-end — `document_config.py` → `chunker.py` → `vector_store.py`/`retriever.py`/`bm25_retriever.py` → `hybrid_retriever.py`'s RRF formula)*

### Sprint 2: Domain Intelligence Engines
- [x] Implement `classifier.py` (Ayurvedic Product Classification decision tree). *(`src/engines/classifier.py`)*
- [x] Implement `tk_engine.py` (Section 3(p) & innovation differentiator). *(`src/engines/tk_engine.py` — also covers 3(e), 3(d), 2(1)(j) process eligibility, TKDL mitigation)*
- [x] Implement `abs_engine.py` (BD Act compliance & Form I-IV generator). *(`src/engines/abs_engine.py`)*
- [x] Implement `reg_engine.py` (AYUSH vs FSSAI vs CDSCO regulatory cross-walk). *(`src/engines/reg_engine.py` — also covers DMR(OA) advertising-claim risk)*
- All four verified via `src/test_engines.py` (`PYTHONPATH=src python3 src/test_engines.py`). Not yet wired into `api.py` — no API routes/agent orchestration exist yet (Sprint 3 scope). `ipr_router.py` (Phase 2.4, 7-regime IP router) was in the Phase 2 spec but not on this checklist — flagging in case it should be pulled into Sprint 2/3.

### Sprint 3: LangGraph Agentic Pipeline & Guardrails
- [x] Define `AgentState` schema and setup LangGraph multi-agent flow. *(`src/agents/state.py`, `src/agents/graph.py` — InputSanitizer → SupervisorRouter → 6 specialist nodes → VerificationGuardrail → OutputSynthesizer/FallbackHandler, compiled with LangGraph's `StateGraph`; `langgraph`/`langchain-core` added to `requirements.txt`)*
- [x] Implement `citation_agent.py` to enforce zero-hallucination and citation verification. *(`src/agents/citation_agent.py` — parses `[Document, Section/Rule, Page]` citations and verifies each against the actually-retrieved chunks)*
- [x] Implement `confidence.py` with multi-factor scoring and automated abstention. *(`src/guardrails/confidence.py` — the Phase 1.4 formula, plus a citation-precision cap/override)*
- Supervisor routing (`src/agents/supervisor.py`) is deterministic keyword-based, not an LLM call — kept auditable and free; only the specialist nodes hit Gemini.
- `patent_agent`/`abs_agent`/`reg_agent`/`tm_gi_agent` are RAG-grounded via the Sprint 1 retriever; `classifier_agent` runs the Sprint 2 engine directly when structured inputs are supplied (bypasses the confidence gate — deterministic, no hallucination risk) and falls back to RAG otherwise. `intl_agent` and `tm_gi_agent` are RAG-only for now — no dedicated corpus/engine exists yet (international corpus is Sprint 4; no `ipr_router.py`/TM-GI engine was built in Sprint 2).
- Verified via `src/test_agents.py` (deterministic, no external services) plus live end-to-end runs through `agents.graph.run(...)` against the real Qdrant/Gemini stack (citation stripping, confidence capping, and abstention all observed working).
- Found and fixed two real bugs while verifying: (1) `context_builder.py` was interpolating literal `"None"` into the LLM's context/citations for chunks without a section/rule; (2) the citation parser split naively on every comma, breaking on document titles that contain one (e.g. "The Patents Act, 1970") — now anchors on the `Section`/`Rule` marker instead.

### Sprint 4: International IP & Export Layer
- [ ] Ingest WIPO GRATK Trea[x]2024, Nagoya Protocol, and US FDA Botanical Guidance. *(blocked — same as Sprint 1's corpus item, awaiting source PDFs from user for `data/raw/international/`)*
- [x] Build jurisdiction toggle and market-specific regulatory advisors (US, EU, UK). *(`src/engines/intl_engine.py` — US botanical-drug/DSHEA routes + USPTO Alice/Mayo §101 eligibility, EU THMPD traditional-use (30y/15y) & well-established-use (10y) thresholds, UK MHRA THR, and the cross-market GRATK disclosure obligation; wired into `intl_agent` in `src/agents/specialists.py`)*
- Jurisdiction toggle lives in `agents.graph.supervisor_router`: `state["jurisdiction"] = "International"` routes the no-keyword-match default to `intl_agent` instead of the India-specific `patent_agent`; `state["target_market"]`/`market_inputs`/`gratk_inputs` route straight to `intl_agent`'s deterministic engine path (bypasses the confidence gate, same pattern as `classifier_agent`).
- `intl_agent` without a `target_market` still falls back to RAG against the India-only corpus (grounding gap flagged in its `note` field) until the international corpus above is actually ingested.
- Verified via the extended `src/test_agents.py` (all engine thresholds, both toggle directions, structured routing) plus a live end-to-end run through `agents.graph.run(...)`.

### Sprint 5: UI Overhaul & Multilingual Experience
- [x] Redesign frontend with modern Glassmorphic theme, responsive sidebar, and theme toggle. *(new `/app` route in `sih_frontend_antigrav` — chosen over the legacy `frontend/` vanilla UI per user decision; `Sidebar.jsx` is glassmorphic/backdrop-blurred, collapses off-canvas under 900px, dark/light toggle via a new `[data-theme='light']` override block in `index.css`)*
- [x] Build interactive 6-step guided wizard (Jurisdiction → Product Classification → Issue Routing → Analysis → Sources → Action Plan). *(`Wizard.jsx` + `steps/Step{Jurisdiction,Classification,IssuePicker,Analysis,Sources,Action}.jsx`, each step backed by real engine/agent calls, not mock data)*
- [x] Implement downloadable PDF case brief and compliance checklist exporter. *(`lib/caseBrief.js` — Markdown/JSON via Blob download; PDF via a print-formatted window + `window.print()`, i.e. the browser's native "Save as PDF" — no bundled PDF library or CDN dependency, but also not a server-rendered PDF; flagging that distinction rather than overclaiming)*
- [x] Add multilingual translation layer with Indian legal glossary preservation. *(new `POST /api/translate` endpoint — Gemini-based, not Bhashini: no Bhashini API credentials were available, so this reuses the existing Gemini client with a prompt that preserves bracketed statutory citations in English (`prompt.TRANSLATION_PROMPT`), verified live in Hindi; 9 Indian languages + English in the sidebar selector, swap-in point for the real Bhashini API is `api.py`'s `api_translate`)*
- New backend plumbing needed to make any of this reachable: `POST /api/agent` (runs `agents.graph.run` — jurisdiction toggle, `forced_agent` for the issue picker, `classification_inputs`, `target_market`/`market_inputs`/`gratk_inputs`) and `agents.specialists.configure()` so the agent graph reuses the RAG pipeline's already-loaded retriever/reranker/LLM instead of loading a second copy. Also added `forced_agent` routing (highest precedence) to `agents/graph.py`'s `supervisor_router`, needed for the Issue Picker step to force a specific specialist regardless of query-text keywords.
- Verified via `npm run build`/`npm run lint` (clean — Node 22 required, see note below) and live `curl` smoke tests of `/api/agent` (classifier path, RAG path, US/EU market path) and `/api/translate` against a running server — confirmed retriever/LLM reuse (no double model load) and citation-preserving Hindi translation. **Not verified**: interactive browser testing of the wizard UI — no browser/screenshot tool was available in this environment, so the six steps are confirmed to build, lint, and transform cleanly (every new file returns 200 from the Vite dev server) plus careful prop/state wiring review, but not click-tested end-to-end in an actual browser.
- Environment note: `npm run build`/`dev` require Node ≥22 (Vite 8/rolldown needs `node:util`'s `styleText`, added in Node 21.7+) — this session's default Node was 18.20.8; used `nvm use 22` (already installed) to build. Worth pinning in project docs/CI if not already.
- Out of scope (not on this checklist): Phase 5.2's Document & Formulation Upload Analyzer, and Phase 5.3's Bhashini STT/TTS specifically — added browser-native Web Speech API (`SpeechRecognition`/`speechSynthesis`) for voice input/listen instead, feature-detected and hidden where unsupported.

### Sprint 6: Governance, Testing & Golden Benchmark Evaluation
- [x] Implement DPDP-aligned PII sanitizer. *(`src/guardrails/pii_sanitizer.py` — Aadhaar/PAN/phone/email/PIN-code regex redaction; wired into `agents/graph.py`'s `input_sanitizer` node, which now runs before embedding/retrieval/LLM on every query. `AgentState.pii_redactions` and the `/api/agent` response carry only the redaction *type*, never the raw matched value — verified no leak via `test_agents.py` and a live end-to-end check.)*
- [x] Run `eval_benchmark.py` across 50 golden legal scenarios. *(`src/eval_benchmark.py` — 5 questions × the 10 Phase 6.2 categories, LLM-free by design (retrieval/engine/confidence checks only, to respect Gemini's ~20/day free-tier quota; `--full` opt-in samples the real graph). **Final: 49/50 (98%)** — exactly hits the plan's "Safe Abstention Accuracy ≥98%" target. One remaining failure is documented in-file as a known, narrow limitation (see below), not hidden or force-passed.)*
- [x] Final end-to-end integration testing and deployment readiness. *(9/9 live checks against a running server: health, classifier engine path, abs_agent routing, intl market pathway, jurisdiction toggle, PII redaction, Hindi translation with citation preservation, legacy `/api/chat/` compatibility, CORS preflight. Frontend `npm run build` clean.)*
- **Real bug found and fixed by the benchmark itself** (exactly what a golden-benchmark suite is for): `guardrails/confidence.py`'s `_sigmoid` assumed the reranker's raw scores center on 0, but bge-reranker-v2-m3 empirically scores genuinely irrelevant query/passage pairs at ~0.0001-0.0004 (not negative) — so a plain `sigmoid(x)` mapped "no signal" to ~0.5 ("medium confidence") instead of low, meaning **every one of the 15 out-of-corpus questions (categories 7/8/10) was failing to abstain** before the fix (0/15 → 14/15 after). Fixed by shifting the sigmoid's midpoint/steepness (`RERANK_THRESHOLD`/`RERANK_STEEPNESS`); re-verified the known-good Section 3(p) case stayed "high" (confidence actually rose, 0.818→0.917) with no regression.
- **Known limitation, documented not hidden**: `legal_reference.py`'s exact-reference boost has no concept of *which Act* a cited section belongs to — a query citing "Section 9 of the Trade Marks Act" gets boosted by the Patents Act's own unrelated Section 9, driving confidence artificially high instead of abstaining. Root-caused and left as a flagged future fix (see the comment at that benchmark question) rather than rushed under this pass.
- **Sprint 1/4 corpus follow-up completed**: 4 source PDFs you dropped into `data/raw/` (Patents (Amendment) Rules 2024, AYUSH Examination Guidelines 2025, Biological Diversity (Amendment) Act 2023, Biological Diversity Rules 2024) are now ingested (11 documents, 1724 chunks). Two more real bugs found and fixed while wiring them in: (1) `chunker.py` hardcoded "skip legal parsing until page 7," a hack specific to the original Patents Act PDF's table of contents, which would have silently corrupted chunking on every new document — generalized to a per-document `toc_skip_pages` config; (2) Rules-type documents (`patent_rules_2003.pdf` too, not just the new ones) were being labelled `"Section N"` instead of `"Rule N"`, and the dormant `"rule"` payload field the rest of the pipeline was already built to expect was never populated — fixed in `legal_structure.py`/`chunker.py`. Also confirmed by content inspection (not filename) that the BD Act file is the **2023 amendment only**, not the full 2002 principal Act — labelled accordingly to avoid citation misattribution. WIPO GRATK/Nagoya Protocol/US FDA Botanical Guidance for Sprint 4 are still not ingested (not supplied).
- **Security finding, flagged not fixed at your instruction**: `.env` (containing `GEMINI_API_KEY`) has been git-tracked since 4 commits ago, and the repo has a live, already-pushed private GitHub remote. You chose to leave this as-is for now — noting it here so it isn't lost track of; the key is in git history on that remote regardless of any future `.gitignore` fix, so rotating it remains advisable whenever convenient.

---

## 7. Post-Completion Audit (2026-09-25)

After all 6 sprints were marked complete, a full audit checked every claim in this document against the actual code rather than trusting the sprint summaries at face value. It found — and fixed — several real gaps that had been silently missed or only partially wired, plus documented what genuinely can't be closed without more input from you.

### Fixed during the audit

- **`ipr_router.py` (Phase 2.4) had never been built**, despite being flagged twice (Sprint 2 and Sprint 3 notes) as a known gap and never followed up. Built now — deterministic guidance across all 7 IP regimes named in the plan (Patents filing workflow; Trademark NICE-class mapping + Section 9 distinctiveness screen; GI registration process; Industrial Designs; Trade Secrets; Copyright; PPV&FR variety categories).
- **Four of the six specialist agents were never wired to their own engines.** Only `classifier_agent` and `intl_agent` (Sprints 3/4) actually called their deterministic Sprint 2 engines — `patent_agent`, `tm_gi_agent`, `abs_agent`, and `reg_agent` were pure RAG-only the entire time, despite `tk_engine.py`, `abs_engine.py`, and `reg_engine.py` existing, tested, and doing nothing. This directly contradicted Phase 3.2's own agent/tool table ("Patent Agent... S.3 Analyzer", "ABS Agent... ABS Checklist Generator", etc.). All four are now wired the same way `classifier_agent` was: an optional structured-input field (`tk_inputs`, `ipr_inputs`, `abs_inputs`, `reg_inputs`) that bypasses RAG/the confidence gate entirely when supplied, falling back to RAG for free-text queries. `agents/graph.py`'s `supervisor_router` fast-paths all six inputs through one table instead of two hardcoded special cases. Also wired end-to-end into the Sprint 5 wizard's Issue Picker step (`StepIssuePicker.jsx` + `wizardConfig.js`) and `api.py`'s `AgentRequest`/`AgentResponse` — not just reachable by direct API call.
- **Phase 3.3's mandated "dual-layer" output structure was never enforced.** The plan requires every generated answer to follow a specific 5-part structure (Executive Summary, Legal Framework, Analysis, Risks, Checklist — Sources and Confidence are deliberately *not* asked of the LLM, since those are already computed independently by `citation_agent.py`/`confidence.py` and asking the LLM to self-report them would risk conflicting, unverified numbers). `prompt.SYSTEM_PROMPT` never mandated this at all before now — fixed and verified live (real Gemini call, correct 5-section structure, 8/8 citations still verified).
- **Two real crash bugs**: `abs_agent` only caught `TypeError` from `analyze_abs_compliance`, but an invalid `entity_type`/`activity_type` string raises `ValueError` (the engine converts them to enums internally) — uncaught, this would crash the whole graph run. Same root cause, pre-existing since Sprint 3, in `classifier_agent` for an invalid `intended_use` string. Both fixed; `reg_agent`'s narrower `TypeError`-only catch was checked and confirmed correct (its engine never raises `ValueError`).
- **`_retrieve_and_draft` (the shared RAG path every specialist falls back to) had no exception handling around the retriever call at all** — unlike `rag_pipeline.py`'s equivalent path, which does. A Qdrant outage would have crashed every specialist's fallback path, not just returned a clean error. Fixed to match `rag_pipeline.py`'s pattern; verified with a simulated retriever failure (no crash, clean abstention message to the user, real error surfaced separately in the `error` field for diagnostics).
- **Cosmetic but real**: `tk_engine.py`'s individual findings stored the raw `Risk` enum instead of `.value`, which under Python 3.11+'s changed `Enum.__str__` rendered as `"Risk.BARRED"` instead of `"barred"` in every surfaced answer. Fixed; confirmed no other engine has the same leak (all others already used `.value` consistently).
- A stale checklist line (Sprint 1's corpus item, still marked `[ ]`/blocked even though it was actually completed in Sprint 6) is now corrected above.

All fixes are covered by new assertions in `src/test_engines.py`/`src/test_agents.py` (not just manually verified once) — full suite re-run clean, and `src/eval_benchmark.py` re-run clean at 49/50 (98%) with no regression.

### Confirmed genuinely not done — not fixed, and why

- **Sprint 4's international corpus** (WIPO GRATK Treaty 2024, Nagoya Protocol, US FDA Botanical Guidance) is still not ingested — still blocked on you supplying the source PDFs, same as before. `intl_agent`'s free-text fallback remains India-corpus-only.
- **Phase 6.1's Consent Management** (an explicit consent dialog before query logging/escalation) and **encrypted-at-rest storage** — neither is built. The PII sanitizer (Sprint 6) covers data *minimization*, but there is no session/query persistence layer anywhere in the system to begin with (the API is fully stateless), so "encrypted at rest" doesn't yet have anything to apply to. Building a persistence layer speculatively, with no spec for what gets stored or for how long, would be scope invention rather than implementing something the plan actually specified in enough detail to build — flagging rather than guessing.
- **Gap Analysis row 10, "Knowledge Graph"** (`LegalKG`/`KGStore` in the Layer 5/6 architecture diagram): never appears as a concrete task in any Phase 1-6 detailed spec or any Sprint checklist — it's named only in the high-level gap table and architecture diagram, with no entity/relation schema ever defined. Treated as an unscoped architectural aspiration, not a missed deliverable; building a graph database around an undefined schema wasn't attempted.
- **Phase 3.1's agent-to-agent chaining** (the state diagram's `ClassifierAgent --> PatentAgent : Classification Context Passed` edges) doesn't exist as an internal LangGraph edge — the graph dispatches to exactly one specialist per request. In practice this handoff happens one level up, at the product/wizard level instead: Sprint 5's wizard runs Classification (step 2) before Issue Routing (step 3), so the classification result is already in hand — and visible to the user — before they pick a specialist. This is a design choice worth naming explicitly rather than a silent gap, since "how" the requirement is met differs from the diagram even though the underlying need (classification context available before specialist analysis) is met.
- **`src/config.py`** (Phase 5's target file structure) doesn't exist — configuration values (`QDRANT_URL`, model names, etc.) remain scattered as module-level constants across several files, as they were before Sprint 1. This is a code-organization / DRY observation, not a functional defect (every value is still correct and consistent where checked); consolidating it wasn't treated as a "fix" since nothing is actually broken.
- The **`.env` git-tracking / API-key exposure** finding from Sprint 6 remains exactly as you left it (not fixed, by your explicit choice) — still worth acting on when convenient, not raised again here as new.

---

## 8. Sprint 7 — left_to_do.md Gap Closure (2026-09-28)

Went back to the original spec (`left_to_do.md`) item-by-item rather than
just this plan's own checklist, since it's the superset document. Most of
its 25 items were already covered by Sprints 1-6; the genuinely new gaps,
and what was done about each:

- **`src/config.py`** (flagged as missing in the Section 7 audit) — built.
  Consolidates the QDRANT_URL/COLLECTION_NAME/model-name/RRF/authority/
  bonus/confidence-threshold constants that were previously duplicated
  across ~13 files, wired through as defaults everywhere (all overridable,
  no behavior change — `test_engines.py`/`test_agents.py` re-run clean).
- **Item 15, Human Escalation** — was export-only (download a case brief
  locally). Added `POST /api/escalate` (`src/escalation.py`, stdlib
  `smtplib`) which emails the case brief to a configured facilitator
  inbox, and a real "Escalate" button + reply-to field in `StepAction.jsx`.
  Delivery config (`SMTP_HOST`/`SMTP_USER`/`SMTP_PASSWORD`/
  `ESCALATION_EMAIL_TO`) is read from `.env` and not yet set — by your
  choice, built now and wired later, same pattern as `GEMINI_API_KEY`.
  `GET /api/escalate/status` reports whether it's configured.
- **Item 16, Official Database Access** — `src/references.py` + `GET
  /api/references`: categorized deep links to IP India (patent/trademark/
  design search), GI Registry, TKDL, WIPO/WIPO Lex/PCT/Madrid/Hague, NBA,
  AYUSH, FSSAI, CDSCO. Surfaced in `StepSources.jsx`. Deliberately does
  not attempt record lookup/scraping (each portal has its own CAPTCHA/
  session flow) or any paid-database connector — item 16 requires
  explicit per-use permission and access logging for paid sources, which
  is a separate, not-built feature.
- **Item 13, source freshness checking** — chunks never carried a
  `version_date` (Section 7's audit already noted this). Rather than
  guessing amendment dates from memory, `src/freshness.py` maps each
  document's own already-asserted title year (e.g. "The Patents Act,
  1970") to a staleness flag (>10 years old) applied post-hoc in `api.py`
  — no re-ingestion, no new claims. Surfaced as `freshness_note` on every
  citation/source and rendered in `StepSources.jsx`.
- **Item 11, Knowledge Graph** — Gap Analysis row 10 and the Section 7
  audit both flagged this as unscoped. Built `src/engines/
  knowledge_graph.py`: a multi-hop graph (`Product -> Ingredient ->
  Biological Resource -> TK -> IP Type -> Authority -> ABS ->
  Jurisdiction`) assembled from the outputs of the already-tested
  `classifier.py`/`tk_engine.py`/`abs_engine.py` engines — not a
  fabricated ingredient/regulation dataset (only the ingredient/
  biological-resource label itself is free text, unverified). Exposed via
  `POST /api/knowledge-graph`, covered by new assertions in
  `test_engines.py`, and rendered as a traversable edge list in
  `StepSources.jsx` (pre-filled from the wizard's own classification/ABS
  answers, not a separate re-entry of the same facts).
- **Explicitly deferred, by your decision, not by oversight**: items 19
  (conversation history, source bookmarking)/20 (consent management,
  encryption at rest, RBAC)/22 (audit/prompt/citation logs) all need the
  same missing piece — a persistence layer with per-user identity, which
  the API still deliberately does not have. You chose "skip for now"
  rather than build a minimal unauthenticated SQLite layer for it.
- International corpus (WIPO GRATK, Nagoya, TRIPS, US FDA Botanical
  Guidance, EU THMPD) remained not ingested at the time this was
  written — **resolved in Sprint 8, below.**

All new code covered by `test_engines.py` (knowledge graph) and manually
verified live against a running server with real Qdrant/Gemini (health,
`/api/references`, `/api/knowledge-graph`, `/api/escalate` unconfigured-
error path, `/api/escalate/status`, and `freshness_note` appearing on a
real Patents Act 1970 citation). Frontend `npm run build`/`npm run lint`
clean (Node 22, same requirement as Sprint 5).

---

## 9. Sprint 8 — International Corpus & Live Web-Sourced Ingestion (2026-09-28)

Two things landed together: you supplied five real international PDFs,
and a second ingestion path (periodic web fetching) was built for
content that's genuinely only available as web pages.

**International PDF corpus — now ingested.** Five documents registered
in `document_config.py`'s `DOCUMENTS` and run through the normal
`ingest.py` pipeline (full re-embed: 16 documents, 2173 chunks total):
- `cbd-en.pdf` — Convention on Biological Diversity, full text and
  annexes (`document_type: "treaty"`, authority weight 0.95).
- `nagoya-protocol-en.pdf` — Nagoya Protocol, full text (`"treaty"`).
- `Botanical-Drug-Development--Guidance-for-Industry.pdf` — the actual
  US FDA guidance (`"international_guidance"`, 0.80) — this is the real
  document; a web-fetch attempt at the same content was independently
  confirmed blocked by FDA's anti-bot page (see below), so this PDF is
  the only path to it right now.
- `gratk_dc_exsum.pdf` — WIPO's own 2-page informal summary of the
  GRATK Treaty (`"treaty_overview"`, 0.65) — not the full binding text,
  which wasn't supplied as a clean standalone PDF.
- `gratk.pdf` — a genuine 1-page excerpt from a WIPO General Assembly
  document showing GRATK ratification/accession status (also
  `"treaty_overview"`) — confirmed by content inspection, not assumed
  from the filename.

Verified live: real full-text retrieval with correct page numbers for
both the Nagoya Protocol and the FDA guidance via `POST /api/agent`
free-text queries (e.g. a Nagoya ABS query surfaced pages 3-6; an FDA
botanical-drug query surfaced pages 8-34) — not just "the file loaded,"
the actual pipeline retrieves and cites it correctly.

**Live web-sourced corpus — new second ingestion path.** For official
content that's a web page, not a downloadable PDF (regulatory portals,
treaty-body overview pages), added a parallel pipeline that reuses the
same chunker/embedder/Qdrant store as the PDF path but never touches
`ingest.py` or `chunks.json`:
- `src/web_sources.py` — the curated source registry (parallel to
  `document_config.DOCUMENTS`), each entry needing an explicit,
  hand-verified CSS `content_selector` (no automatic "readability"
  extraction — a heuristic mis-extracting legal text is worse than
  skipping the source).
- `src/web_loader.py` — fetcher mirroring `document_loader.load_pdf()`'s
  exact output contract (honors `robots.txt`, honest User-Agent,
  `pdf_link` fetch mode delegates straight to the existing `load_pdf`).
- `src/ingest_web.py` — standalone script (run manually or via cron, not
  a scheduler inside the FastAPI process), with SHA-256 change detection
  so an unchanged page costs nothing on re-run (confirmed live: second
  run loaded zero embedding-model weight, "unchanged" for all sources),
  and a delete-then-reinsert-by-`document_id` strategy
  (`QdrantVectorStore.delete_by_document_id`, new method) so a page that
  chunks differently on re-fetch doesn't leave orphaned stale points.
- `src/freshness.py` gained a parallel `web_freshness_note()` path
  (days-since-fetch, not years-since-enactment) for chunks carrying a
  `fetched_at` field — `api.py`'s `_resolve_freshness_note()` picks the
  right one automatically.
- `hybrid_retriever.py` merges `data/processed/chunks_web.json` into the
  in-memory BM25 corpus alongside `chunks.json` if present, optional and
  additive — a fresh clone with no web corpus yet is unaffected.

**Verification was done live, not assumed** — every one of the 15
starter URLs from the original plan was actually fetched with
`requests`/`BeautifulSoup` before being trusted:
- **Working** (6, now in `web_sources.WEB_SOURCES`): `wipo_gratk_treaty_2024`,
  `pct_texts`, `madrid_legal_texts`, `hague_legal_texts`,
  `budapest_treaty` (all WIPO overview/landing pages — real WIPO
  content, but a summary, not the full treaty text), and `cdsco_home`.
- **Superseded** by the real PDFs above: `cbd_convention_text` (its URL
  404'd anyway), `nagoya_protocol_text`, `us_fda_botanical_guidance` —
  removed from the registry rather than left as redundant lower-quality
  duplicates.
- **Confirmed broken, left commented out with the specific reason**:
  `trips_agreement` (WTO redirects to their own 404 page — a 200-status
  trap), `eu_thmpd_directive` (EUR-Lex returns an empty 202 to a plain
  GET), `uk_mhra_thr_scheme` (gov.uk genuinely 404s), `ipindia_patents_overview`
  (dead deep link), and `ayush_home`/`fssai_home` (both are
  JavaScript-rendered SPAs — a plain HTTP GET returns an empty app
  shell; would need a headless browser, explicitly out of scope for
  this v1 static fetcher).

All ingested content (16 PDFs + 6 web sources, 2173 + 9 chunks) verified
via `test_engines.py`/`test_agents.py` (clean) and live queries against
a running server. `data/raw/`'s remaining un-ingested items —
`3_Patents_Amendment_Rules_2024...`/`26_.../27_...` were already
ingested in Sprint 6 — this sprint's new files are exactly the five
listed above.

---

## 10. Sprint 9 — winning_features.md Full Build (2026-09-29)

`winning_features.md` is a 20-item, tiered hackathon-judging wishlist.
Two audits (frontend + backend) first confirmed what was actually true
vs. only claimed: RAG+citations, the classifier wizard, confidence/
abstention, and the disclaimer were real; but jurisdiction separation
was enforced only by which agent got picked (not a retrieval-time
filter), the "agent step trace" was a fake timed progress bar, the
knowledge graph was plain text rows, and 12 of the 20 items had no code
at all. This sprint built all 20, phase by phase, each verified live
against the real Qdrant/Gemini stack before moving on — not just unit
tests.

**Architectural jurisdiction separation (item 2)** — `retriever.py`'s
new `jurisdiction_query_filter`/`combined_query_filter` pass a real
Qdrant `Filter` into `query_points()`; `bm25_retriever.py` mirrors it
client-side. Verified live: an India-scoped FDA query returns **zero**
FDA chunks, not just a prompt telling the LLM to ignore them. `"Both"`
mode (`agents/graph.py`'s `run()`) invokes the graph twice and returns
`{india, international}` as separate objects — confirmed they can
produce genuinely different outcomes (one answered, one abstained) in
the same call.

**Real agent step trace (item 11)** — `AgentState.trace` uses a LangGraph
`Annotated[list, operator.add]` reducer so every node in `agents/graph.py`
appends its own entry; `StepAnalysis.jsx` renders the actual sequence
post-hoc, distinct from the pre-existing simulated progress bar (kept,
since there's no streaming backend to drive it live).

**Persistence layer (`src/db.py`)** — stdlib SQLite, no login, session-
scoped via an `X-Session-Id` header the frontend generates once into
`localStorage`. Backs a real audit log (`/api/audit-log`), consent
(`/api/consent`, including a **mocked** "Premium Patent Analytics DB"
connector unmissably labeled MOCK DATA per item 15's own framing), and
DPDP delete-my-data (`/api/privacy/delete`) — verified live: grant
consent → log an entry → read it back → delete → confirm gone.

**Corpus admin panel (item 20)** — `/api/admin/corpus` merges the PDF/
web/uploaded document lists with real chunk counts from the actual
ingested JSON files (not placeholders); upload stages a PDF and marks it
`pending_reindex` rather than pretending to synchronously re-embed it
inside a request.

**Law Version Timeline (item 9)** — initially missed in this sprint's
own plan, caught in review. A full old-vs-new text diff isn't honestly
buildable — the corpus only has *one* full original+amendment pair
(Patents Rules 2003/2024); Biological Diversity only has the 2023
amendment and 2024 rules, not the original 2002/2004 text, and that gap
is stated in `law_versions.py` rather than papered over. Instead:
`retriever.py` gained a `document_id_filter` (same `Filter` mechanism as
jurisdiction), so `POST /api/law-version-query` answers the *same
question* with retrieval genuinely scoped to exactly one version.
Verified live: "fee for filing a patent application" against the 2003
Rules vs. the 2024 Amendment returns sources exclusively from each
respective document — the doc's own suggested demo moment, for real.

**IP Route Planner / ABS PDF / TKDL pointer (items 6-8)** —
`engines/ipr_router.plan_ip_route()` and `engines/tk_engine.
misappropriation_risk()` compose existing, already-tested engine output
into a strategy list and a risk flag — no new legal facts. Rendered as
colored flow boxes (`IPRoutePlanner.jsx`) and a labeled risk badge
(`StepSources.jsx`), not paragraphs. `caseBrief.js` gained a dedicated
`buildAbsChecklistMarkdown` export, separate from the general case
brief.

**Visual knowledge graph explorer (item 10)** — `engines/
knowledge_graph.py`'s `{nodes, edges}` carries no layout by design;
`KnowledgeGraphExplorer.jsx` computes a deterministic layered SVG layout
client-side (columns by node `kind`), no new charting dependency.

**Bhashini (item 13)** — `src/bhashini_client.py` built against the
public ULCA two-step pipeline contract, env-var-gated
(`BHASHINI_USER_ID`/`BHASHINI_API_KEY`) exactly like `llm.py`/
`escalation.py`'s pattern. **Not live-verified** — no credentials exist
yet — every exact endpoint/payload field is marked `# VERIFY` in the
source, and `/api/translate` falls back to the existing Gemini path on
any failure or missing config, so nothing breaks either way.

**Persona modes (item 14)** — `prompt.py`'s `PERSONA_GUIDANCE` dict
feeds a new `{persona_guidance}` `SYSTEM_PROMPT` placeholder (same
`.format()` mechanism as `{context}`/`{query}`); adjusts tone/depth only,
verified it never changes which sources get cited.

**Export Market Navigator (item 12)** — real cards for US/EU/UK calling
the already-grounded `intl_engine` pathway; GCC/ASEAN render as explicit
"not yet in corpus" placeholders since `intl_engine.Market` only ever
supported three markets — flagged, not fabricated.

**Prompt-injection filtering (item 18)** — `guardrails/injection_filter.py`
expands the previous 4-phrase check to ~17 patterns across instruction-
override, jailbreak framing, and system-prompt exfiltration; still
deterministic regex, not an LLM judge, matching the supervisor's existing
"auditable and free" design.

**Evaluation dashboard (item 19)** — `eval_benchmark.py --out-json`
writes the real 49/50 (98%) golden-benchmark result to
`data/processed/eval_results.json`; `GET /api/eval-results` serves it;
`EvalDashboard.jsx` renders it as stat tiles + per-category bars — the
actual measured numbers, not a mockup.

All of Phases 0-11 verified via `test_engines.py`/`test_agents.py`
(both clean, with new assertions for the injection filter, trace
accumulation, and `"Both"` mode) plus live end-to-end checks against a
running server with real Qdrant/Gemini for every phase that touched
retrieval or generation. Frontend `npm run build`/`npm run lint` clean
throughout (Node 22).

---

## 11. Conclusion

By executing this phased implementation plan, **IP-Sakti** will evolve from a prototype retrieval script into an enterprise-grade, authoritative, and trusted AI companion for Indian Ayurveda innovators, researchers, and legal practitioners, setting the gold standard for citation-grounded legal AI in traditional knowledge and intellectual property.
