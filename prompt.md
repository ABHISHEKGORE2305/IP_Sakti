You are taking over an existing project called `medical-rag`.

IMPORTANT:
Do NOT rebuild the project from scratch.
Do NOT randomly refactor working components.
First inspect the existing repository and understand the current implementation.
Then fix the current legal-aware chunking issue and continue the project systematically.

============================================================
PROJECT PURPOSE
============================================================

This project is a RAG chatbot focused on Indian patent law, Ayurvedic inventions/formulations, Traditional Knowledge (TK), and Indian IP/legal queries.

This is NOT intended to provide medical diagnosis or medical treatment advice.

The chatbot should answer questions such as:

- Can I patent my new Ayurvedic formulation in India?
- Is this Ayurvedic formulation eligible for patent protection?
- Can traditional knowledge be patented?
- What are the requirements for filing a patent in India?
- Does prior art affect my Ayurvedic formulation?
- Can I patent a new process for preparing an Ayurvedic medicine?
- Can an Ayurvedic formulation be patented if its ingredients are already known?
- What makes an Ayurvedic formulation novel for patent purposes?
- What is Section 3(p) of the Patents Act?
- What inventions are not patentable in India?
- What is novelty in patent law?
- What is inventive step?
- What are the requirements for patentability?

The system must answer using retrieved source documents and must minimize hallucination.

============================================================
TARGET ARCHITECTURE
============================================================

The intended architecture is:

Ayurvedic / Indian IP PDFs
        |
        v
PDF extraction using PyMuPDF
        |
        v
Text cleaning
        |
        v
Legal/Ayurvedic-aware chunking
        |
        v
Embedding model: BAAI/bge-m3
        |
        v
Qdrant
        |
        +--------------------------+
        |                          |
        v                          v
Dense semantic search          BM25 sparse search
        |                          |
        +------------+-------------+
                     |
                     v
             RRF hybrid fusion
                     |
                     v
          Cross-Encoder reranking
          BAAI/bge-reranker-v2-m3
                     |
                     v
              Context Builder
                     |
                     v
                    LLM
                     |
                     v
          Answer + source citations

============================================================
CURRENT PROJECT STRUCTURE
============================================================

medical-rag/
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── __init__.py
│   ├── qdrant_setup.py
│   ├── document_loader.py
│   ├── chunker.py
│   ├── embedding_model.py
│   ├── vector_store.py
│   ├── ingest.py
│   ├── reset_collection.py
│   ├── retriever.py
│   ├── bm25_retriever.py
│   ├── hybrid_retriever.py
│   ├── reranker.py
│   ├── final_retriever.py
│   ├── context_builder.py
│   ├── legal_structure.py
│   └── tests/

Inspect the actual repository because the current files may differ from this description.

============================================================
QDRANT
============================================================

Qdrant is running locally.

Typical Docker command:

docker pull qdrant/qdrant

docker run -p 6333:6333 -p 6334:6334 \
  -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
  qdrant/qdrant

Dashboard:

http://localhost:6333/dashboard

Collection:

medical_documents

Vector dimension:

1024

Distance:

Cosine

The vector store uses deterministic UUIDv5 point IDs based on human-readable chunk IDs.

The `chunk_id` is stored in the Qdrant payload.

Do NOT reset/re-ingest Qdrant until the legal-aware chunking validation is complete.

============================================================
CURRENT DOCUMENT CORPUS
============================================================

The current corpus contains:

data/raw/patents_act_1970.pdf
data/raw/patent_rules_2003.pdf
data/raw/pharmaceuticals_guidelines_2014.pdf
data/raw/traditional_knowledge_guidelines_2012.pdf
data/raw/patent_office_manual_2019.pdf
data/raw/tkdl_factsheet.pdf
data/raw/an_overview_of_ayurveda.pdf

Metadata:

1. Patents Act, 1970
   document_type = statute

2. Patents Rules, 2003
   document_type = rules

3. Pharmaceuticals Guidelines
   document_type = patent_guidelines

4. TK/Biological Material Guidelines
   document_type = traditional_knowledge_guidelines

5. Patent Office Manual
   document_type = patent_office_manual

6. TKDL Factsheet
   document_type = tkdl_reference

7. Overview of Ayurveda
   document_type = ayurvedic_reference

Likely metadata:

jurisdiction = India
language = en

Previous ingestion:

Patents Act:
69 pages, 148 original chunks

Patent Rules:
66 pages, 162 chunks

Pharma guidelines:
51 pages, 183 chunks

TK/Bio guidelines:
9 pages, 24 chunks

Patent Office Manual:
174 pages, 368 chunks

TKDL:
4 pages, 10 chunks

Ayurveda:
12 pages, 13 chunks

Original total:
908 chunks

BGE-M3 embeddings were generated and 908 vectors were uploaded to Qdrant successfully.

IMPORTANT:
The existing vectors were created before the latest legal-aware chunking fixes. They should eventually be rebuilt after chunking is fully validated.

============================================================
PDF LOADING
============================================================

Current `document_loader.py` is approximately:

from pathlib import Path
import pymupdf
import re

def clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    text = text.strip()
    return text

def load_pdf(
    pdf_path: str,
    metadata: dict | None = None,
):
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    document = pymupdf.open(pdf_path)
    pages = []

    for page_number, page in enumerate(document):
        raw_text = page.get_text()
        text = clean_text(raw_text)

        if not text:
            continue

        page_data = {
            "text": text,
            "page": page_number + 1,
            "source": pdf_path.name,
            "document_id": pdf_path.stem,
        }

        if metadata:
            page_data.update(metadata)

        pages.append(page_data)

    document.close()
    return pages

This part is working.

============================================================
EMBEDDINGS
============================================================

Embedding model:

BAAI/bge-m3

Dimension:

1024

Current implementation uses sentence-transformers.

Example:

from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-m3"

class EmbeddingModel:

    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

    def embed_text(self, text: str):
        vector = self.model.encode(
            text,
            normalize_embeddings=True
        )
        return vector.tolist()

    def embed_documents(self, texts: list[str]):
        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True
        )
        return vectors.tolist()

This is working.

============================================================
RETRIEVAL SYSTEM
============================================================

Current retrieval system contains:

1. Dense Qdrant semantic search
2. BM25 sparse search
3. Reciprocal Rank Fusion (RRF)
4. Cross-encoder reranking

BM25 uses:

rank-bm25

Current tokenization is basic lowercase whitespace splitting.

Cross encoder:

BAAI/bge-reranker-v2-m3

The model has already been downloaded and works.

The final retriever combines hybrid retrieval and reranking.

Use stable `chunk_id` when merging dense and BM25 results.

Do NOT destroy this working retrieval implementation.

============================================================
CURRENT RETRIEVAL RESULTS
============================================================

Previous tests:

Query:
"Can I patent my new Ayurvedic formulation in India?"

Result:
Good enough.
TK guidelines appeared near the top.
TKDL appeared second.

Query:
"Can traditional knowledge be patented?"

Result:
Excellent.

Query:
"What inventions are not patentable in India?"

Result:
Acceptable, but sometimes definitions rank above the actual Section 3.

Query:
"What is Section 3(p) of the Patents Act?"

Result:
Poor legal precision.
Pharmaceutical guidelines and Patent Office Manual sometimes outranked the actual Patents Act.

Query:
"What is novelty in patent law?"

Result:
Good.

Query:
"What is inventive step?"

Result:
Excellent.

Query:
"Can an Ayurvedic formulation made from known ingredients be patented?"

Result:
Very good.
TK guidelines appeared at the top.

Query:
"Can a new process for preparing an Ayurvedic medicine be patented?"

Result:
Retrieval was not ideal.

This is why legal-aware chunking and legal-reference-aware retrieval are important.

============================================================
LEGAL STRUCTURE PROBLEM
============================================================

The original parser searched for explicit strings like:

"Section 3(p)"

But the actual PDF frequently formats legislation like:

3. What are not inventions.—
...
(p) an invention which...

instead of:

Section 3(p)

Therefore a stateful legal parser was created.

It tracks:

section
clause
subsection
legal_reference

============================================================
IMPORTANT RAW PDF DISCOVERY
============================================================

The Patents Act PDF structure was inspected directly.

Pages 1–6:
TABLE OF CONTENTS / ARRANGEMENT OF SECTIONS

Page 7 onward:
ACTUAL STATUTE

Page 7 begins:

THE PATENTS ACT, 1970

ACT NO. 39 OF 1970

An Act to amend and consolidate the law relating to patents.

CHAPTER I
PRELIMINARY

1. Short title, extent and commencement.—...

Page 9 contains the actual:

3. What are not inventions.—...

Page 10 continues Section 3.

Section 3(p) contains:

(p) an invention which, in effect, is traditional knowledge or which is an aggregation or duplication of known properties of traditionally known component or components.

This is an extremely important provision for this project.

============================================================
LEGAL PARSER BUG #1: TABLE OF CONTENTS
============================================================

Originally the parser incorrectly interpreted this TOC line:

3. What are not inventions.

on page 1 as:

Section 3

That was wrong.

Pages 1–6 are the Table of Contents.

The actual statute begins on page 7.

Therefore legal parsing should only start at page 7 for this PDF.

============================================================
LEGAL PARSER BUG #2: THE SCHEDULE
============================================================

The Table of Contents itself contains:

THE SCHEDULE

The chunker originally detected this and set:

in_schedule = True

Then the actual Act pages were treated as if they were already inside the Schedule.

This prevented actual section parsing.

The fix is:

ONLY detect the Schedule after legal parsing has started.

Correct logic:

if (
    legal_parsing_enabled
    and re.search(
        r"\bTHE\s+SCHEDULE\b",
        line,
        flags=re.IGNORECASE,
    )
):
    in_schedule = True
    current_section = None
    current_clause = None
    current_text.append(line)
    continue

============================================================
LEGAL PARSER BUG #3: AMENDMENT FOOTNOTES
============================================================

The PDF contains lines such as:

3. Sub-clause (B) omitted by Act 33 of 2021, s. 13 (w.e.f. 4-4-2021).

The generic section regex interpreted that as:

Section 3

That incorrectly reset the current legal section.

The parser was changed so amendment/footnote prefixes such as:

Ins.
Subs.
Sub-clause
Omitted
The words
Clause

are rejected as actual section headings.

============================================================
LEGAL PARSER BUG #4: UPPERCASE NESTED SUBCLAUSES
============================================================

The PDF contains:

(u) “prescribed” means,—
(A) in relation to proceedings before a High Court...

The old clause regex used case-insensitive matching and incorrectly treated:

(A)

as:

Clause a

This was fixed.

Top-level clauses should only recognize lowercase:

(a)
(b)
(c)
...
(p)

The regex is:

r"^\(([a-z])\)\s+"

with NO `re.IGNORECASE`.

Therefore:

(p) ...
=> clause p

(A) ...
=> other

============================================================
CURRENT legal_structure.py
============================================================

The intended implementation is:

import re


def detect_section_heading(line: str):

    line = line.strip()

    match = re.match(
        r"^(\d+[A-Za-z]?)\.\s+(.+)$",
        line
    )

    if not match:
        return None

    section_number = match.group(1)
    title = match.group(2).strip()

    if not title:
        return None

    if re.match(
        r"^(Ins\.|Subs\.|Sub-clause|Omitted|"
        r"The words|Clause)",
        title,
        re.IGNORECASE
    ):
        return None

    if len(title) < 5:
        return None

    return section_number


def detect_clause(line: str):

    line = line.strip()

    match = re.match(
        r"^\(([a-z])\)\s+",
        line
    )

    if match:
        return match.group(1)

    return None


def detect_subsection(line: str):

    line = line.strip()

    match = re.match(
        r"^\((\d+[A-Za-z]?)\)\s+",
        line
    )

    if match:
        return match.group(1)

    return None


def build_legal_reference(
    section=None,
    clause=None
):

    if section is None:
        return None

    if clause:
        return f"Section {section}({clause})"

    return f"Section {section}"


def classify_legal_line(line: str):

    section = detect_section_heading(line)

    if section:
        return {
            "type": "section",
            "section": section
        }

    clause = detect_clause(line)

    if clause:
        return {
            "type": "clause",
            "clause": clause
        }

    subsection = detect_subsection(line)

    if subsection:
        return {
            "type": "subsection",
            "subsection": subsection
        }

    return {
        "type": "other"
    }

============================================================
PARSER TEST STATUS
============================================================

The isolated parser tests currently PASS.

Test:

from legal_structure import classify_legal_line

tests = [
    '3. What are not inventions.—The following are not inventions within the meaning of this Act,—',
    '3. Sub-clause (B) omitted by Act 33 of 2021, s. 13 (w.e.f. 4-4-2021).',
    '(p) an invention which, in effect, is traditional knowledge',
    '(A) in relation to proceedings before a High Court',
]

Expected and actual behavior:

Real Section 3:
{'type': 'section', 'section': '3'}

Amendment footnote:
{'type': 'other'}

Clause p:
{'type': 'clause', 'clause': 'p'}

Uppercase nested A:
{'type': 'other'}

Therefore `legal_structure.py` itself is currently behaving correctly.

============================================================
CURRENT CHUNKER BUG
============================================================

The current chunker test:

from document_loader import load_pdf
from chunker import create_chunks

pages = load_pdf('data/raw/patents_act_1970.pdf')
chunks = create_chunks(pages)

produces:

TOTAL CHUNKS: 357

But:

for chunk in chunks:
    if chunk.get('section') == '3':
        ...

returns NOTHING.

This means:

classify_legal_line()

correctly recognizes Section 3,

but:

create_chunks()

is not carrying Section 3 into generated chunks.

The most recent suspected cause is the Schedule detection issue.

The chunker must ensure that:

1. pages 1–6 are not legally parsed
2. page 7 activates legal parsing
3. TOC "THE SCHEDULE" does not activate schedule mode
4. actual Schedule detection still works later
5. Section 3 is stored in current_section
6. Section 3 remains active across page 9 → page 10
7. Section 3(p) is generated correctly
8. amendment footnotes do not reset current_section

============================================================
CURRENT CHUNKER DESIGN
============================================================

The chunker tracks:

current_section
current_clause
in_schedule
legal_parsing_enabled
chunk_counter

Conceptually:

for each page:

    if page_number >= 7:
        legal_parsing_enabled = True

    if legal parsing disabled:
        append raw text
        continue

    if THE SCHEDULE:
        enter schedule mode

    classification = classify_legal_line(line)

    if section:
        flush previous chunk
        current_section = new section
        current_clause = None

    if clause:
        flush previous chunk
        current_clause = clause

    otherwise:
        append line

Each generated chunk should contain:

chunk_id
text
page
source
document_id
document
section
clause
legal_reference

============================================================
IMPORTANT CHUNKING CONSIDERATIONS
============================================================

The current legal-aware chunker creates chunks around sections/clauses.

For example:

Section 3
Section 3(a)
Section 3(b)
...
Section 3(p)

This is desirable for legal retrieval.

However, the current `chunk_size` and `chunk_overlap` arguments may not yet be meaningfully used for every chunk type.

Do not blindly redesign this right now.

First make legal section/clause tracking correct.

After that, consider improving chunk size and page-continuation handling.

============================================================
CONTEXT BUILDER
============================================================

The context builder has already been updated.

DO NOT unnecessarily rewrite it.

It includes:

SOURCE N
Document: ...
Page: ...
Legal Reference: ...
Section: ...
Rule: ...
Chunk ID: ...

Source metadata includes:

source_number
chunk_id
document
document_id
source
page
section
rule
legal_reference
reranker_score

This is already wired for legal references.

============================================================
LEGAL CONTENT THAT MATTERS
============================================================

Important Patents Act provisions include:

Section 2(1)(j):
Definition of invention.

Section 2(1)(ja):
Inventive step.

Section 2(1)(l):
New invention.

Section 3:
What are not inventions.

Section 3(d):
Known substance / efficacy-related exclusion.

Section 3(e):
Mere admixture.

Section 3(i):
Certain treatment methods.

Section 3(p):
Traditional knowledge exclusion.

Section 4:
Atomic energy.

Section 6:
Persons entitled to apply.

Section 10:
Contents of specifications.

Section 25:
Opposition.

Section 64:
Revocation.

Section 83:
General principles.

Section 84:
Compulsory licences.

Also relevant:
Rules and official guidelines.

DO NOT hardcode legal answers.
Use source documents as the authority.

============================================================
LEGAL RETRIEVAL PROBLEM
============================================================

One major retrieval problem:

Query:

"What is Section 3(p) of the Patents Act?"

Sometimes the system ranks:

Pharmaceutical Guidelines
Patent Office Manual

above:

Patents Act Section 3(p)

This is undesirable.

For explicit legal-reference queries, the authoritative source containing the exact provision should be heavily preferred.

Potential strategy:

1. Detect explicit legal references in the query.
2. Search exact legal_reference metadata.
3. Combine with dense and BM25 retrieval.
4. Apply source authority weighting.
5. Cross-encoder rerank.
6. Return authoritative statutory source when appropriate.

Do NOT implement this blindly.

First inspect the existing retrieval implementation.

============================================================
SOURCE AUTHORITY
============================================================

Eventually introduce source authority metadata.

Potential hierarchy:

1. statute
2. rules
3. official government guidelines
4. patent office manual
5. official reference/factsheet
6. general Ayurveda reference

However, authority must be context-aware.

Example:

"What is Section 3(p)?"

Prefer:

Patents Act

over:

Patent Office Manual

But:

"How are Ayurvedic inventions examined?"

could legitimately prioritize:

official AYUSH/IP guidelines

Do not apply a blanket source boost to every query.

============================================================
QUERY LEGAL REFERENCE DETECTION
============================================================

Eventually detect references such as:

Section 3
Section 3(p)
Section 2(1)(j)
Section 2(1)(ja)
Rule 24B

Example:

query:
"What is Section 3(p) of the Patents Act?"

Extract:

query_legal_reference = "Section 3(p)"

Use this as an additional retrieval signal.

Exact legal-reference matches should have high importance.

============================================================
RETRIEVAL IMPROVEMENT PLAN
============================================================

After legal chunking is fixed:

1. Validate legal metadata.
2. Rebuild Qdrant.
3. Re-ingest documents.
4. Re-run retrieval tests.
5. Implement explicit legal reference detection.
6. Add exact legal-reference retrieval/boosting.
7. Add source authority weighting.
8. Re-evaluate hybrid retrieval.
9. Re-evaluate reranking.
10. Test legal questions again.

============================================================
REQUIRED LEGAL CHUNKING TESTS
============================================================

Create/update automated tests for:

A. TOC Section 3:

"3. What are not inventions."

on page 1

must NOT become:

Section 3

B. Actual Section 3:

"3. What are not inventions.—..."

on page 9

must become:

section = "3"

C. Clause p:

"(p) an invention which, in effect, is traditional knowledge..."

must become:

clause = "p"

legal_reference = "Section 3(p)"

D. Uppercase nested clause:

"(A) in relation to proceedings before a High Court"

must NOT become clause a.

E. Amendment footnote:

"3. Sub-clause (B) omitted by Act 33 of 2021..."

must NOT become Section 3.

F. Page continuation:

Section 3 begins on page 9 and continues on page 10.

Section state must survive the page boundary.

G. Section transition:

Section 4 must become Section 4.

H. Section 6 must become Section 6.

I. Section 7 must become Section 7.

============================================================
EXPECTED SECTION 3 OUTPUT
============================================================

After fixing the chunker, this command:

PYTHONPATH=src python -c "
from document_loader import load_pdf
from chunker import create_chunks

pages = load_pdf('data/raw/patents_act_1970.pdf')
chunks = create_chunks(pages)

print('TOTAL CHUNKS:', len(chunks))

for chunk in chunks:
    if chunk.get('section') == '3':
        print(
            chunk['page'],
            chunk['legal_reference'],
            chunk['text'][:120]
        )
"

must show Section 3 chunks.

Most importantly, there must be a:

Section 3(p)

chunk containing the traditional knowledge provision.

============================================================
RE-INGESTION PLAN
============================================================

Do NOT re-ingest until legal chunking passes.

Once chunking is correct:

1. Validate legal metadata.
2. Reset the Qdrant collection.
3. Run ingestion.
4. Generate BGE-M3 embeddings.
5. Upload the new vectors.
6. Verify Qdrant payloads.
7. Run retrieval tests.

============================================================
RETRIEVAL TEST SUITE
============================================================

After re-ingestion test:

1. "What is Section 3(p) of the Patents Act?"
2. "Can traditional knowledge be patented?"
3. "What inventions are not patentable in India?"
4. "Can I patent my new Ayurvedic formulation in India?"
5. "Can an Ayurvedic formulation made from known ingredients be patented?"
6. "Can I patent a new process for preparing an Ayurvedic medicine?"
7. "What is novelty in patent law?"
8. "What is inventive step?"
9. "What are the requirements for patentability?"
10. "What does Section 2(1)(j) mean?"

For explicit statutory questions, actual Patents Act chunks should rank above secondary manuals/guidelines whenever the requested provision exists there.

============================================================
LLM LAYER
============================================================

After retrieval is reliable, implement:

src/llm.py

Use Gemini through `google-genai`.

Environment variable:

GEMINI_API_KEY

Target model:

gemini-2.5-flash

The LLM must answer ONLY from retrieved context.

Requirements:

- Do not hallucinate legal provisions.
- Clearly distinguish statute, rules, guidelines, manuals and reference material.
- If context is insufficient, say so.
- Do not present general reference material as statutory law.
- Include source citations such as [Source 1], [Source 2].
- Prefer authoritative provisions for explicit legal questions.
- Provide informational answers rather than pretending to be a lawyer.
- For actual filing/legal decisions, recommend consulting a qualified patent professional.

============================================================
RAG PIPELINE
============================================================

Eventually create:

src/rag_pipeline.py

Flow:

user query
    ↓
query/legal-reference analysis
    ↓
dense retrieval
    +
BM25 retrieval
    ↓
RRF
    ↓
legal-reference boost if applicable
    ↓
source authority weighting
    ↓
cross-encoder reranking
    ↓
context builder
    ↓
LLM
    ↓
answer + sources

Expected output:

{
    "answer": "...",
    "sources": [...]
}

============================================================
FUTURE CORPUS IMPROVEMENT
============================================================

The current corpus does NOT yet contain the official:

"Guidelines for Examination of Ayush Related Inventions-2025"

This is highly relevant and should be added later.

Also consider adding current official versions of:

- Patents Act
- Patents Rules
- relevant IP India guidelines
- relevant Biological Diversity Act / access-and-benefit-sharing provisions
- other official traditional knowledge/IP sources

IMPORTANT:
Do not silently treat the current old PDFs as the complete current law.

The Patent Office Manual 2019 is a practical manual and not the statute.

============================================================
IMPORTANT ENGINEERING RULES
============================================================

1. Inspect before editing.
2. Preserve working components.
3. Make small, testable changes.
4. Do not randomly refactor.
5. Do not re-ingest until chunking passes.
6. Do not delete Qdrant data unnecessarily.
7. Use stable chunk IDs.
8. Keep metadata structured.
9. Do not hardcode legal answers.
10. Do not hardcode answers into the LLM.
11. Source documents must drive answers.
12. Avoid hallucinated legal citations.
13. Add automated tests for every parser bug discovered.
14. Keep code understandable.
15. This is an educational/portfolio project, so prefer clean, explainable architecture.
16. Avoid unnecessary frameworks.
17. Preserve the existing dense/BM25/RRF/reranker architecture.
18. Legal authority must be considered when ranking legal sources.
19. Explicit legal-reference queries need special handling.
20. Do not claim a source is current unless the corpus actually contains the current version.

============================================================
CURRENT STATUS
============================================================

PDF extraction                  DONE
Text cleaning                   DONE
Initial chunking                DONE
BGE-M3 embeddings               DONE
Qdrant                          DONE
Dense retrieval                 DONE
BM25                            DONE
Hybrid RRF                      DONE
Cross encoder                   DONE
Context builder                 DONE
Legal parser                    FIXED
Legal-aware chunker             CURRENTLY DEBUGGING
Legal reference retrieval       TODO
Source authority weighting      TODO
LLM                             TODO
Full RAG pipeline               TODO
Citation handling               TODO
2025 AYUSH corpus               TODO
Current-law corpus update       TODO
Final evaluation                TODO

============================================================
IMMEDIATE TASK — DO THIS FIRST
============================================================

Do NOT jump directly to the LLM.

First inspect the actual repository.

Inspect:

src/legal_structure.py
src/chunker.py
src/context_builder.py
src/retriever.py
src/bm25_retriever.py
src/hybrid_retriever.py
src/reranker.py
src/final_retriever.py
src/vector_store.py
src/ingest.py

Then reproduce the current bug:

create_chunks(pages)

currently produces approximately:

TOTAL CHUNKS: 357

but no chunks where:

chunk.get("section") == "3"

The isolated parser DOES recognize Section 3 correctly.

Therefore determine exactly why `create_chunks()` is failing to preserve Section 3 metadata.

The likely current issue is that Schedule detection is triggered by the Table of Contents before legal parsing starts.

Fix that.

The correct conceptual order is:

1. Determine whether actual legal parsing has started.
2. Pages 1–6 of this Patents Act PDF are TOC.
3. Page 7 starts the actual Act.
4. Only after legal parsing is enabled should Schedule detection happen.
5. Then classify sections and clauses.

After fixing, verify:

- TOC Section 3 is ignored.
- Actual Section 3 is detected.
- Section 3(p) exists.
- Section 3(p) contains the traditional knowledge provision.
- Amendment footnotes do not create fake sections.
- Uppercase `(A)` is not treated as a clause.
- Section 3 survives page 9 → page 10.
- Section 4 starts correctly.
- Section 6 starts correctly.
- Section 7 starts correctly.

Do not reset Qdrant yet.

============================================================
AFTER IMMEDIATE FIX
============================================================

Once the chunker passes:

1. Build automated legal parser tests.
2. Validate Sections 2, 3, 4, 6, 7, 10, 25, etc.
3. Validate Section 2(1)(j), 2(1)(ja), 2(1)(l).
4. Validate Section 3(d), 3(e), 3(i), 3(p).
5. Validate Rule references.
6. Validate Schedule handling.
7. Validate amendment footnotes.
8. Validate page-boundary continuity.
9. Reset/rebuild Qdrant.
10. Re-ingest all documents.
11. Re-run dense/BM25/hybrid/reranker tests.
12. Implement explicit legal-reference detection.
13. Implement legal-reference-aware retrieval.
14. Implement source authority weighting.
15. Implement LLM.
16. Implement final RAG pipeline.
17. Add source citations.
18. Add evaluation tests.
19. Add current official AYUSH 2025 guidelines.
20. Improve corpus freshness.

============================================================
HOW TO WORK
============================================================

For every change:

1. Explain what you found.
2. Explain the root cause.
3. Make the smallest appropriate code change.
4. Run a focused test.
5. Show the test result.
6. Only then move to the next task.

Do not make five unrelated changes at once.

If something is already working, leave it alone.

If a design decision is uncertain, inspect the existing code and test behavior before changing it.

The immediate goal is NOT to build the entire chatbot today.

The immediate goal is:

MAKE LEGAL-AWARE CHUNKING CORRECT AND VERIFIED.

The first concrete success condition is:

Section 3(p)

must appear as a generated chunk with:

section = "3"
clause = "p"
legal_reference = "Section 3(p)"

and the chunk text must contain the traditional-knowledge exclusion from the Patents Act.

Only after that is proven should the project move forward.