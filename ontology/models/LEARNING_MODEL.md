# Torah Ontology — Learning Model V1.0
## Chief Torah Ontology Scientist — Research Document

---

## 1. Purpose

The Learning Model defines how NEW Torah texts enter the ontology WITHOUT corrupting existing verified knowledge.

**Core Rule:** Never overwrite verified knowledge automatically.

---

## 2. Input Types

### Type 1: Digital Text (Sefaria, Bar-Ilan, HebrewBooks)
**Reliability:** HIGH
**Validation needed:** LOW (already curated)
**Process:** Direct ingestion with source verification

### Type 2: Academic Book/Article
**Reliability:** MEDIUM-HIGH
**Validation needed:** MEDIUM (check citations)
**Process:** Extract claims → Verify sources → Queue for validation

### Type 3: Chassidic/Kabbalistic Text (first-time digitization)
**Reliability:** HIGH (if authentic)
**Validation needed:** MEDIUM (check authorship)
**Process:** OCR → Authorship verification → Concept extraction → Human validation

### Type 4: Manuscript (rare, handwritten)
**Reliability:** VARIABLE
**Validation needed:** HIGH (paleography, attribution, textual variants)
**Process:** Digital imaging → Paleographic analysis → Textual collation → Scholarly review → Concept extraction → Human validation

### Type 5: Oral Tradition / Minhag Book
**Reliability:** MEDIUM
**Validation needed:** HIGH (trace chain of transmission)
**Process:** Record oral tradition → Trace written sources → Community validation → Concept extraction → Human validation

### Type 6: Internet / Social Media Claim
**Reliability:** LOW
**Validation needed:** VERY HIGH (most are unsourced or fabricated)
**Process:** Reject unless traced to printed source. "Rav X said Y on Facebook" = INVALID without published responsum.

---

## 3. Learning Pipeline

### Stage 1: Ingestion
**Input:** PDF, TXT, DOCX, HTML, OCR scan
**Output:** Raw text with metadata
**Rules:**
- Preserve original Hebrew/Aramaic text exactly
- Record page numbers, section headers, formatting
- Flag OCR errors for manual correction
- Never alter the text during ingestion

### Stage 2: Text Segmentation
**Input:** Raw text
**Output:** Segments (verses, paragraphs, responsa sections)
**Rules:**
- Segment by natural boundaries (paragraphs, responsa sections, chapter breaks)
- Minimum segment: one coherent thought unit
- Maximum segment: one page or one responsum
- Preserve cross-references between segments

### Stage 3: Concept Extraction (AI-Assisted, Human-Validated)
**Input:** Text segments
**Output:** Proposed Concept entities
**Rules:**
- AI suggests concepts based on named entities, key terms, and semantic analysis
- Human validator reviews each proposed concept
- If concept already exists in ontology, flag as CROSS_REFERENCE instead of NEW
- If concept is a variant of existing concept, flag as ALIAS
- If concept is genuinely new, flag as NEW_CONCEPT

### Stage 4: Relationship Extraction (AI-Assisted, Human-Validated)
**Input:** Text segments + Proposed Concepts
**Output:** Proposed Relationship entities
**Rules:**
- AI suggests relationships based on:
  - Explicit statements ("X is derived from Y")
  - Implicit connections (discussed in same context)
  - Cross-references ("as it says in [text]")
  - Structural relationships (commentary on, part of, etc.)
- Human validator reviews each proposed relationship
- If relationship already exists, flag as DUPLICATE
- If relationship contradicts existing relationship, flag as POTENTIAL_DISPUTE
- If relationship is new, flag as NEW_RELATIONSHIP

### Stage 5: Source Extraction
**Input:** Text segments + Proposed Relationships
**Output:** Evidence entities
**Rules:**
- Extract exact quotes with page/line references
- Extract paraphrases with attribution
- Extract references to other texts
- Every proposed relationship MUST have at least one extracted source
- Sources without exact locations are flagged as INCOMPLETE

### Stage 6: Dispute Detection
**Input:** Proposed Relationships + Existing Ontology
**Output:** Proposed Dispute entities
**Rules:**
- Compare proposed opinions against existing opinions
- If a new opinion contradicts an existing opinion, create a POTENTIAL_DISPUTE
- If a new opinion agrees with an existing opinion, strengthen the existing opinion's consensus
- If a new opinion introduces a new perspective, flag as NOVEL
- Disputes are NEVER auto-resolved. They are queued for human validation.

### Stage 7: Human Validation Queue
**Input:** All proposed entities (Concepts, Relationships, Sources, Disputes)
**Output:** Validated or rejected entities
**Rules:**
- Torah scholars review the queue
- Each item can be: APPROVED, REJECTED, MODIFIED, or DEFERRED
- APPROVED items enter the ontology
- REJECTED items are archived with reason
- MODIFIED items are corrected and re-queued
- DEFERRED items wait for additional evidence
- Priority order:
  1. Biblical/Talmudic sources (highest priority)
  2. Rishonic sources
  3. Achronic sources
  4. Modern responsa
  5. Chassidic/Kabbalistic expansions
  6. Internet claims (lowest priority, often rejected)

### Stage 8: Ontology Integration
**Input:** Validated entities
**Output:** Updated ontology
**Rules:**
- New concepts are added with domain tags
- New relationships are linked to existing entities
- New disputes are linked to existing opinions
- New sources are linked to existing evidence chains
- Existing entities are NEVER modified — only linked to new entities
- If a new source contradicts an old source, a DISPUTE is created, not a correction

---

## 4. Learning Model Rules

### LR1: No Overwriting
Existing entities CANNOT be modified by the learning pipeline. If new evidence contradicts old evidence, a Dispute entity is created.

### LR2: Provenance Chain
Every new entity MUST trace back to the original text. "AI extracted from [book], validated by [scholar], approved on [date]."

### LR3: Confidence Degradation
AI-extracted entities start with LOW confidence (0.5-0.7). Human validation raises confidence. No AI-extracted entity enters the ontology with confidence > 0.7 without validation.

### LR4: Temporal Stamping
Every entity includes `date_entered`, `date_validated`, and `validator_name`. This allows tracking how the ontology evolves.

### LR5: Reversibility
Any entity added by the learning pipeline CAN be removed without damaging the ontology. Entities are "soft-added" — they can be deactivated if later found incorrect.

### LR6: Community Override
If a validator approves an entity that another validator rejects, the entity is marked as DISPUTED among validators. A third validator breaks the tie.

---

## 5. Learning Model Stress Test

### Scenario: A New Chassidic Book is Discovered
**Book:** "Likutei Avodah" by an obscure 19th-century Rebbe, never published before.

**Learning Pipeline Execution:**
1. Ingestion: OCR scan → raw text
2. Segmentation: 150 segments (paragraphs/sections)
3. Concept Extraction: AI suggests 45 concepts
   - 30 are existing concepts (e.g., "Devekut", "Hitbodedut")
   - 10 are aliases of existing concepts
   - 5 appear genuinely new (e.g., "Avodah BeSimchah Gedolah")
4. Relationship Extraction: AI suggests 120 relationships
   - 80 are existing relationships (e.g., "Devekut → Hitbodedut")
   - 30 are new perspectives on existing relationships
   - 10 are genuinely new relationships
5. Source Extraction: All quotes are extracted with page references
6. Dispute Detection: 3 new opinions contradict existing opinions
   - "This Rebbe says Devekut is accessible to ALL Jews, not just tzaddikim" — contradicts some authorities
   - "This Rebbe says Simchah is MORE important than Hitbodedut" — novel prioritization
   - These become POTENTIAL_DISPUTES
7. Validation Queue: 3 scholars review over 2 weeks
   - 5 new concepts APPROVED
   - 8 relationships APPROVED
   - 2 disputes APPROVED as genuine
   - 2 concepts REJECTED (found to be unsourced folk ideas)
   - 10 items MODIFIED (corrections to AI extraction)
8. Integration: 5 concepts + 8 relationships + 2 disputes added to ontology

**Result:** The ontology grew by 15 entities without any corruption of existing knowledge. 2 items were rejected, preserving ontology integrity.

---

## 6. Learning Model Failure Modes

### Failure 1: The Authorship Problem
**Problem:** Is the "new" book actually by the attributed author? Pseudepigrapha are common in Torah literature.
**Example:** Some "Baal Shem Tov" stories were written by later authors.
**Solution:** Authorship verification is a SEPARATE pipeline before concept extraction. Paleography, linguistic analysis, and historical context are checked first.

### Failure 2: The Sectarian Text
**Problem:** Some texts are from groups outside mainstream Judaism (e.g., Karaite, Sabbatean, Frankist).
**Example:** Sabbatean texts often appear to be standard Kabbalah but contain heretical ideas.
**Solution:** Each new text is tagged with `sectarian_status: mainstream | marginal | heretical | unknown`. Marginal and heretical texts are handled differently — their concepts are noted but flagged.

### Failure 3: The Translation Bias
**Problem:** AI extraction from a translation introduces translator's bias.
**Example:** "Neshamah" translated as "soul" loses the Hebrew nuances.
**Solution:** AI extraction MUST work on Hebrew/Aramaic text. Translations are for human readability only, not for extraction.

### Failure 4: The Novelty Illusion
**Problem:** AI may claim a concept is "new" when it is actually an old concept with a new name.
**Example:** A modern book calls it "Soul Alignment" but it is actually "Devekut."
**Solution:** Semantic similarity check against existing concepts before creating NEW_CONCEPT.

---

## 7. Learning Model V2 Improvements

1. **AuthorshipVerification pipeline:** Pre-extraction verification of text authenticity.
2. **SectarianFlag:** Automatic tagging of texts from marginal groups.
3. **SemanticDeduplication:** Prevents "novelty illusions" by checking against existing concepts.
4. **TemporalEvolution tracker:** Tracks how concepts change across editions of the same book.
5. **CommunityConsensus meter:** Shows how many validators approved/rejected an entity.
