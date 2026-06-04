# Torah Knowledge Graph — AI Extraction Design

## 1. Overview

This document specifies the artificial intelligence extraction layer for the Torah Knowledge Graph platform. The system uses large language models (LLMs) to extract structured entities and relationships from Torah texts, validates extraction quality via confidence scoring, tracks provenance for every extraction, and integrates human reviewers for high-stakes decisions.

### 1.1 Design Goals
- **Precision**: Extracted entities and relationships must be factually accurate with respect to the source text.
- **Recall**: Capture as many meaningful entities and relationships as feasible within cost and latency constraints.
- **Verifiability**: Every extraction is traceable to its source text, model, prompt, and generation parameters.
- **Human Oversight**: No extraction enters the canonical graph without passing an automated confidence threshold or human review.
- **Scalability**: Process thousands of text segments in parallel with controlled resource usage.

### 1.2 System Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Text Segments  │────▶│ Entity Extractor │────▶│  Entity Store   │
│   (Qdrant/DB)   │     │   (LLM Agent)    │     │  (Review Queue) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Text Segments  │────▶│ Relation Extract │────▶│ Relation Store  │
│   (Qdrant/DB)   │     │   (LLM Agent)    │     │  (Review Queue) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌──────────────────┐
│  Source Citation  │────▶│ Citation Parser  │
│   Extractor       │     │ (Regex + LLM)    │
└─────────────────┘     └──────────────────┘
```

### 1.3 LLM Selection

| Role | Primary Model | Fallback | Context Window | Cost Driver |
|------|---------------|----------|----------------|-------------|
| Entity Extraction | Claude 4 Sonnet | Claude 4 Haiku | 200K | Input tokens |
| Relationship Extraction | Claude 4 Opus | Claude 4 Sonnet | 200K | Input tokens |
| Citation Parsing | Claude 4 Haiku | Local fine-tuned model | 200K | Batch throughput |
| Explanation Generation | Claude 4 Sonnet | Claude 4 Haiku | 200K | Output tokens |

**Selection Rationale:**
- **Claude 4 Opus** for relationship extraction: Long-context reasoning is critical for connecting entities across multi-paragraph spans, and Opus has the highest reasoning fidelity for Hebrew and Aramaic.
- **Claude 4 Sonnet** for entity extraction: High accuracy at lower cost; entities are typically local to a single sentence or verse.
- **Claude 4 Haiku** for citation parsing and fast filtering: These are pattern-matching tasks that benefit from speed.

---

## 2. Entity Extraction Agent

### 2.1 Entity Types

The extraction system recognizes the following entity types. Each type has a dedicated prompt template and output schema.

| Entity Type | Description | Examples |
|-------------|-------------|----------|
| `Person` | Named individuals, including titles | Moses, Rashi, Rabbi Akiva |
| `Place` | Geographic locations, real or symbolic | Jerusalem, Egypt, Mount Sinai |
| `Concept` | Abstract theological or philosophical ideas | Free will, Divine providence, Teshuvah |
| `Mitzvah` | Commandments (positive or negative) | Shabbat, Kashrut, Tefillin |
| `Event` | Specific historical or narrative occurrences | The Exodus, Giving of the Torah |
| `Text` | Named works or text segments | Torah, Talmud, Zohar, Genesis 1:1 |
| `Object` | Physical items mentioned | Ark of the Covenant, Menorah |
| `TimePeriod` | Named eras or durations | Temple period, 40 years in the desert |

### 2.2 Prompt Templates

#### Base Prompt Structure
Every entity extraction prompt follows this structure:
1. **Role**: Define the extractor's persona (scholarly Torah researcher).
2. **Task**: Describe the extraction task for the specific entity type.
3. **Input**: The text segment (Hebrew, English, or bilingual).
4. **Few-Shot Examples**: 3-5 examples of the target entity type.
5. **Output Schema**: JSON schema description.
6. **Constraints**: Rules about what NOT to extract (e.g., no anachronistic inferences).

#### Person Extraction Prompt

```
You are a scholarly Torah researcher extracting named individuals from Jewish texts.

## Task
Read the provided text and identify all named persons. Include honorifics and titles
(e.g., "Rabbi", "Rav", "HaRambam") as part of the name. Do not infer unnamed
individuals (e.g., "the king" without a name).

## Input Text
{text_segment}

## Few-Shot Examples

Example 1:
Text: "וַיֹּאמֶר מֹשֶׁה אֶל־אַהֲרֹן"
Entities: [
  {"name": "Moses", "nameHe": "מֹשֶׁה", "type": "Person", "role": "prophet"},
  {"name": "Aaron", "nameHe": "אַהֲרֹן", "type": "Person", "role": "high priest"}
]

Example 2:
Text: "Rashi comments on this verse..."
Entities: [
  {"name": "Rashi", "nameHe": "רש\"י", "type": "Person", "role": "commentator",
   "fullName": "Shlomo Yitzchaki", "era": "Rishonim"}
]

## Output Schema
Return a JSON object with key "entities" containing an array of objects:
- name (string): Canonical English name
- nameHe (string): Hebrew/Aramaic name as it appears
- type (string): Always "Person"
- role (string, optional): Their role in this context
- fullName (string, optional): Expanded form if known
- era (string, optional): Tannaim / Amoraim / Rishonim / Acharonim / Modern
- aliases (string[], optional): Known aliases

## Constraints
- Only extract explicitly named persons.
- Do not guess at identities of unnamed characters.
- If a person is referred to by title only (e.g., "the prophet"), skip unless the
text explicitly identifies them elsewhere in the same segment.
- Output ONLY the JSON object. No markdown fences, no commentary.
```

#### Place Extraction Prompt

```
You are a scholarly Torah researcher extracting geographic locations from Jewish texts.

## Task
Identify all named places in the text. Include both real historical locations and
places mentioned in prophetic or symbolic contexts. Note if a place is symbolic
rather than literal.

## Input Text
{text_segment}

## Few-Shot Examples

Example 1:
Text: "וַיֹּאמֶר ה' אֶל־אַבְרָם לֶךְ־לְךָ מֵאַרְצְךָ וּמִמּוֹלַדְתְּךָ וּמִבֵּית אָבִיךָ אֶל־הָאָרֶץ אֲשֶׁר אַרְאֶךָּ"
Entities: [
  {"name": "Abram's homeland", "nameHe": "אַרְצְךָ", "type": "Place", "symbolic": false},
  {"name": "The land shown by God", "nameHe": "הָאָרֶץ אֲשֶׁר אַרְאֶךָּ", "type": "Place",
   "canonicalName": "Canaan", "symbolic": false}
]

## Output Schema
Return a JSON object with key "entities" containing an array of objects:
- name (string): Canonical English name
- nameHe (string): Hebrew/Aramaic name as it appears
- type (string): Always "Place"
- canonicalName (string, optional): Modern or widely accepted equivalent
- symbolic (boolean): True if the place is used symbolically
- coordinates (object, optional): {lat, lng} if known and literal

## Constraints
- Distinguish between literal places and metaphorical usage (e.g., "Zion" as Jerusalem vs. "Zion" as a spiritual concept).
- Output ONLY the JSON object.
```

#### Mitzvah Extraction Prompt

```
You are a scholarly Torah researcher identifying commandments (mitzvot) in Jewish texts.

## Task
Extract all explicit commandments — both positive obligations ("thou shalt") and
negative prohibitions ("thou shalt not"). Note the Torah source if stated or
implied by the text context.

## Input Text
{text_segment}

## Few-Shot Examples

Example 1:
Text: "זָכוֹר אֶת־יוֹם הַשַּׁבָּת לְקַדְּשׁוֹ"
Entities: [
  {"name": "Remember the Sabbath day", "nameHe": "זָכוֹר אֶת־יוֹם הַשַּׁבָּת",
   "type": "Mitzvah", "category": "positive", "source": "Exodus 20:8"}
]

Example 2:
Text: "לֹא תִּגְנֹב"
Entities: [
  {"name": "Do not steal", "nameHe": "לֹא תִּגְנֹב",
   "type": "Mitzvah", "category": "negative", "source": "Exodus 20:13"}
]

## Output Schema
Return a JSON object with key "entities" containing an array of objects:
- name (string): Canonical English description
- nameHe (string): Hebrew text of the commandment
- type (string): Always "Mitzvah"
- category (string): "positive" or "negative"
- source (string, optional): Canonical reference if known
- rabbinic (boolean): True if rabbinic rather than Torah commandment

## Constraints
- Only extract explicit commandments, not general ethical advice.
- Distinguish Torah-level from rabbinic-level when the text makes this clear.
- Output ONLY the JSON object.
```

### 2.3 Few-Shot Examples with Hebrew Context

All prompt templates include 3-5 few-shot examples per entity type. The examples:
- **Always include Hebrew text** alongside English extraction to anchor the model in the source language.
- **Cover edge cases**: ambiguous names, titles vs. names, symbolic vs. literal places, Torah vs. rabbinic mitzvot.
- **Use real verses and commentaries** (e.g., Rashi on Genesis, Rambam's Mishneh Torah) rather than synthetic text.

**Example Pool Maintenance:**
- Examples are stored in `ai-extraction/prompts/few_shot_examples/` as YAML files, one per entity type.
- A quarterly review process evaluates example effectiveness via A/B testing against a human-annotated validation set.
- Low-performing examples (those that lead to model errors) are replaced.

### 2.4 Output Schema

**Unified Entity Output Schema:**
```json
{
  "entities": [
    {
      "name": "Moses",
      "nameHe": "מֹשֶׁה",
      "type": "Person",
      "role": "prophet",
      "fullName": "Moshe Rabbeinu",
      "era": "Biblical",
      "aliases": ["Moshe"],
      "span": {"start": 12, "end": 17},
      "confidence": 0.97
    }
  ],
  "metadata": {
    "model": "claude-sonnet-4-6-20251001",
    "promptVersion": "v2.1.0",
    "temperature": 0.1,
    "inputTokens": 1240,
    "outputTokens": 340
  }
}
```

**Field Descriptions:**
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Canonical English name |
| `nameHe` | string | Name as it appears in Hebrew/Aramaic |
| `type` | string | Entity type from the taxonomy |
| `span` | object | Character offsets in the input text |
| `confidence` | float | Model's self-reported confidence (0.0–1.0) |
| `metadata.model` | string | Model identifier |
| `metadata.promptVersion` | string | Prompt template version |

---

## 3. Relationship Extraction Agent

### 3.1 Relationship Types

| Relationship | Direction | Description | Example |
|--------------|-----------|-------------|---------|
| `AUTHORED_BY` | Text → Person | Text was written by this person | "Mishneh Torah" AUTHORED_BY "Rambam" |
| `COMMENTARY_ON` | Text → Text | Commentary explains base text | "Rashi on Genesis" COMMENTARY_ON "Genesis" |
| `CITES` | Text → Text | Text quotes or references another | "Talmud Shabbat 2a" CITES "Mishnah Shabbat 1:1" |
| `MENTIONS` | Text → Entity | Text mentions person/place/concept | "Genesis 1:1" MENTIONS "God" |
| `TEACHES` | Person → Person | Teacher-student relationship | "Rabbi Yochanan" TEACHES "Resh Lakish" |
| `RELATED_TO` | Concept → Concept | Theological or thematic connection | "Free will" RELATED_TO "Divine providence" |
| `OCCURRED_AT` | Event → Place | Event took place at location | "Giving of the Torah" OCCURRED_AT "Mount Sinai" |
| `PARTICIPATED_IN` | Person → Event | Person took part in event | "Moses" PARTICIPATED_IN "Exodus" |
| `PROHIBITS` | Mitzvah → Concept | Prohibition targets an action/concept | "Lashon hara" PROHIBITS "Gossip" |
| `REQUIRES` | Mitzvah → Object | Commandment requires a physical object | "Tefillin" REQUIRES "Tefillin straps" |
| `FOLLOWS_FROM` | Concept → Concept | Logical or textual derivation | "Teshuvah" FOLLOWS_FROM "Free will" |
| `OPPOSES` | Concept → Concept | Contradictory or opposing ideas | "Determinism" OPPOSES "Free will" |

### 3.2 Prompt Templates

#### Relationship Extraction Prompt

```
You are a scholarly Torah researcher identifying relationships between entities in Jewish texts.

## Task
Given a text segment and a list of entities already extracted from it, identify all
meaningful relationships between those entities. Relationships can be explicit
(stated in the text) or implicit (strongly implied by the context). For each
relationship, provide a confidence score and a brief explanation.

## Supported Relationship Types
{relationship_types_json}

## Input
Text: {text_segment}

Entities in this text:
{entities_json}

## Few-Shot Examples

Example 1:
Text: "וַיֹּאמֶר ה' אֶל־מֹשֶׁה..."
Entities: [{"name": "God", "type": "Person"}, {"name": "Moses", "type": "Person"}]
Relationships: [
  {
    "source": "God",
    "target": "Moses",
    "type": "SPEAKS_TO",
    "confidence": 0.99,
    "explanation": "The text explicitly states 'the Lord said to Moses'.",
    "evidence": "וַיֹּאמֶר ה' אֶל־מֹשֶׁה"
  }
]

Example 2:
Text: "Rashi explains that Abraham left Haran because God commanded him to go to Canaan."
Entities: [{"name": "Rashi", "type": "Person"}, {"name": "Abraham", "type": "Person"},
           {"name": "Haran", "type": "Place"}, {"name": "Canaan", "type": "Place"}]
Relationships: [
  {
    "source": "Rashi",
    "target": "Genesis",
    "type": "COMMENTARY_ON",
    "confidence": 0.98,
    "explanation": "Rashi is commenting on the Torah passage about Abraham.",
    "evidence": "Rashi explains that Abraham..."
  },
  {
    "source": "Abraham",
    "target": "Haran",
    "type": "DEPARTED_FROM",
    "confidence": 0.92,
    "explanation": "Abraham left Haran per Rashi's commentary.",
    "evidence": "Abraham left Haran"
  }
]

## Output Schema
Return a JSON object with key "relationships" containing an array of objects:
- source (string): Name of the source entity
- sourceType (string): Type of source entity
- target (string): Name of the target entity
- targetType (string): Type of target entity
- type (string): Relationship type from the supported list
- confidence (float): 0.0 to 1.0
- explanation (string): Brief justification
- evidence (string): Verbatim quote from the text supporting the relationship

## Constraints
- Only create relationships between entities present in the provided list.
- If a relationship is highly speculative (confidence < 0.6), omit it.
- Distinguish between text-level relationships (what the text says) and
  commentary-level relationships (what a commentator says about the text).
- Output ONLY the JSON object.
```

### 3.3 Context Window Management (Chunking Strategy)

Relationship extraction requires sufficient context to identify non-local relationships (e.g., a commentary linking a verse to a distant Talmud passage). However, LLM context windows are finite and attention degrades over long inputs.

**Chunking Strategy:**
1. **Primary Chunk**: The text segment being analyzed (typically one verse, Mishnah, or Talmud paragraph). Size: ~200–500 tokens.
2. **Surrounding Context**: ±2 segments before and after the primary chunk. Size: ~400–1000 additional tokens.
3. **Metadata Context**: Fixed-size context containing relevant metadata (text title, author, category, date). Size: ~100–200 tokens.
4. **Entity Registry**: All entities extracted from the entire chapter/section, not just the current chunk, to enable cross-chunk relationships. Size: variable, capped at 500 tokens.

**Total Context Budget per Call:**
| Model | Max Context | Reserved for Output | Available for Input | Typical Chunk |
|-------|-------------|---------------------|---------------------|---------------|
| Claude 4 Opus | 200K | 8K | 192K | 4K–8K |
| Claude 4 Sonnet | 200K | 4K | 196K | 2K–4K |

**Hierarchical Chunking for Long Texts:**
- For texts longer than the context budget (e.g., a full Talmud daf), use a two-pass approach:
  1. **Pass 1**: Extract intra-chunk relationships with local context only.
  2. **Pass 2**: Aggregate all entities from Pass 1, then run a "global linking" pass that identifies cross-chunk relationships using the entity registry.

### 3.4 Output Schema

**Relationship Output Schema:**
```json
{
  "relationships": [
    {
      "source": "Rashi",
      "sourceType": "Person",
      "target": "Genesis",
      "targetType": "Text",
      "type": "COMMENTARY_ON",
      "confidence": 0.98,
      "explanation": "Rashi is the author of a well-known commentary on the Torah.",
      "evidence": "Rashi comments on this verse...",
      "directional": true,
      "temporalScope": "medieval"
    }
  ],
  "metadata": {
    "model": "claude-opus-4-8-20251001",
    "promptVersion": "v3.0.0",
    "temperature": 0.2,
    "inputTokens": 8500,
    "outputTokens": 1200
  }
}
```

---

## 4. Confidence Scoring

### 4.1 Score Range
Every extracted entity and relationship receives a confidence score on a continuous scale from **0.0 to 1.0**.

**Score Interpretation:**
| Range | Interpretation | Action |
|-------|----------------|--------|
| 0.90 – 1.00 | Near-certain | Auto-accept into canonical graph |
| 0.70 – 0.89 | Probable | Queue for human review ( expedited queue) |
| 0.50 – 0.69 | Uncertain | Queue for human review (standard queue) |
| 0.00 – 0.49 | Unlikely | Auto-reject; log for analysis |

### 4.2 Thresholds and Actions

**Auto-Accept (≥ 0.90):**
- Entity/relationship is inserted into the canonical graph immediately.
- A `provenance` edge links it to the extraction job.
- Flagged for spot-check in monthly quality audits.

**Human Review (0.70 – 0.89):**
- Placed in the `review_queue` with `priority: high`.
- Reviewer sees: source text, extracted entity/relationship, model explanation, and a one-click accept/reject/edit interface.
- Target review SLA: 48 hours.

**Standard Review (0.50 – 0.69):**
- Placed in `review_queue` with `priority: normal`.
- Reviewer sees the same interface plus a "suggest alternative" button.
- Target review SLA: 7 days.

**Auto-Reject (< 0.50):**
- Stored in `rejected_extractions` table for model improvement analysis.
- Never enters the canonical graph.
- Monthly report on rejection patterns fed back to prompt engineering.

### 4.3 Calibration Method

Raw LLM confidence scores are often poorly calibrated (overconfident). We apply post-hoc calibration using a human-validated subset.

**Calibration Process:**
1. **Collect Validation Set**: 2,000 extractions (entities + relationships) from a representative sample of texts across all categories (Tanakh, Talmud, Halakhah, Kabbalah).
2. **Human Annotation**: Three domain experts (rabbinic scholars) independently label each extraction as correct, partially correct, or incorrect. Majority vote determines ground truth.
3. **Score Binning**: Divide raw scores into 10 bins (0.0–0.1, 0.1–0.2, ..., 0.9–1.0).
4. **Calibration Curve**: Compute empirical accuracy per bin. If the 0.8–0.9 bin has 75% accuracy, we learn that raw scores in that range need to be adjusted down.
5. **Platt Scaling**: Fit a logistic regression `calibrated_score = 1 / (1 + exp(A * raw_score + B))` to map raw scores to empirical probabilities.
6. **Temperature Tuning**: Adjust the LLM sampling temperature (typically 0.1–0.3 for extraction) based on calibration results.

**Recalibration Schedule:**
- Initial calibration before production deployment.
- Recalibration quarterly or whenever the model version or prompt template changes.
- Triggered automatically if the weekly accuracy audit deviates >5% from the calibration curve.

---

## 5. Source Citation Extraction

### 5.1 Regex Patterns for Common Citation Formats

A regex-based pre-filter extracts obvious citations before calling the LLM, reducing cost and latency.

**Pattern Catalog:**

| Format | Regex | Example |
|--------|-------|---------|
| Biblical (English) | `([1-3]?\s*[A-Za-z]+)\s+(\d+):(\d+)` | `Genesis 1:1` |
| Biblical (Hebrew) | `([א-ת\"'\s]+)\s+([א-ת\"']+)\s+(\d+)` | `בראשית א א` |
| Talmud Daf | `([A-Za-z\s]+)\s+(\d+)([ab])` | `Shabbat 2a` |
| Mishnah | `Mishnah\s+([A-Za-z\s]+)\s+(\d+):(\d+)` | `Mishnah Shabbat 1:1` |
| Rambam (Halakhah) | `Mishneh\s+Torah,?\s+(.*?),?\s+(\d+):(\d+)` | `Mishneh Torah, Hilchot Shabbat 1:1` |
| Shulchan Aruch | `Shulchan\s+Aruch,?\s+(.*?),?\s+(\d+)` | `Shulchan Aruch, Orach Chaim 1` |
| Zohar | `Zohar\s+(.*?),?\s+(\d+)([ab])` | `Zohar Bereshit 2a` |

**Regex Engine:**
- Uses the `regex` crate (Rust/ Python `regex` module) for Unicode-aware matching.
- Patterns are loaded from `ai-extraction/citation_patterns.json` and can be updated without redeployment.
- Each pattern includes a `target_schema` field mapping capture groups to canonical reference fields.

### 5.2 LLM-Based Parsing for Non-Standard Citations

Many Torah texts use non-standard or abbreviated citation forms that regex cannot capture.

**Examples Requiring LLM Parsing:**
- `"In the first perek of Bava Metzia"` → `Bava Metzia 1` ("perek" = chapter, but no verse given)
- `"As the Rambam writes in Hilchot Teshuvah"` → `Mishneh Torah, Hilchot Teshuvah` (work inferred from author)
- `"The gemara in the first chapter of Berakhot"` → `Berakhot 2a–13b` ("gemara" implies Talmud Bavli)
- `"Rashi's comment on the verse"` → requires context from the surrounding text to identify which verse

**LLM Citation Parser Prompt:**
```
You are a Torah citation parser. Given a text snippet containing a reference to a Jewish
text, identify the canonical source.

## Input
Text: "{text_snippet}"
Available context: The current text is {current_text_title}, section {current_section}.

## Task
Extract the citation and return it in canonical form. If the citation is ambiguous
(e.g., "the Talmud" without specifying tractate), return the most likely specific
reference and a confidence score.

## Output Schema
{
  "citations": [
    {
      "rawText": "the first perek of Bava Metzia",
      "canonicalRef": "Bava Metzia 1",
      "work": "Bava Metzia",
      "category": "Talmud",
      "confidence": 0.88,
      "explanation": "'Perek' means chapter; Bava Metzia is explicit."
    }
  ]
}
```

### 5.3 Validation Against Known Source Database

All extracted citations are validated against the `canonical_books` and `canonical_refs` tables.

**Validation Rules:**
1. **Book exists**: The cited work must exist in `canonical_books`.
2. **Chapter/verse in range**: The chapter and verse numbers must be within the known length of the work (from Sefaria index metadata).
3. **Amud exists**: For Talmud, `a`/`b` must be valid; daf number must be within range.
4. **Cross-reference check**: If a commentary cites a base text, the base text must exist.

**Validation Results:**
- `VALID`: Citation passes all checks.
- `OUT_OF_RANGE`: Chapter/verse is beyond known bounds (e.g., `Genesis 100:1`). Flagged for review — may indicate a textual variant or error.
- `UNKNOWN_WORK`: Cited work not in database. Queued for catalog addition.
- `AMBIGUOUS`: Multiple possible resolutions (e.g., `Shabbat` could be tractate or weekly observance). Human review required.

---

## 6. Explanation Generation

### 6.1 Prompt Template for Relationship Justification

For every relationship entering the review queue or canonical graph, the system generates a human-readable explanation justifying the extraction.

```
You are a Torah scholar writing a brief explanation of why two entities are related.

## Task
Given a source text, two entities, and their relationship type, write a concise
explanation (1–3 sentences) of why this relationship exists in the text. The
explanation should be understandable to a literate reader with basic Torah knowledge.

## Input
Source text: {text_segment}
Entity 1: {entity1_name} ({entity1_type})
Entity 2: {entity2_name} ({entity2_type})
Relationship: {relationship_type}
Evidence quote: {evidence_quote}

## Output Schema
{
  "reasoning": "A clear, concise explanation of the relationship.",
  "evidenceQuote": "The verbatim quote from the text that supports the relationship.",
  "authority": "The textual or traditional authority for this claim (e.g., 'Rashi', 'Talmud Bavli', 'Midrash Rabbah').",
  "confidence": 0.92
}

## Constraints
- The reasoning must be grounded in the provided evidence quote.
- Do not introduce information not present in the source text.
- If the relationship is inferred rather than explicit, clearly state the inference.
```

### 6.2 Required Fields

Every explanation record must contain:

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `reasoning` | string | Human-readable justification | Yes |
| `evidenceQuote` | string | Verbatim text supporting the relationship | Yes |
| `authority` | string | Traditional or textual authority | Yes |
| `confidence` | float | Extraction confidence | Yes |
| `language` | string | Language of the explanation (`en` or `he`) | Yes |

---

## 7. Provenance Tracking

Every extraction is traceable to its origin. Provenance is stored as a property on the extracted node/edge and in the `extraction_provenance` table.

### 7.1 Tracked Fields

| Field | Description | Example |
|-------|-------------|---------|
| `extractionId` | UUID of the extraction job | `018f...` |
| `modelName` | LLM model used | `claude-opus-4-8-20251001` |
| `modelVersion` | API version or model checkpoint | `20251001` |
| `promptHash` | SHA-256 of the full prompt template | `a3f7...` |
| `promptVersion` | Semantic version of the prompt | `v2.1.0` |
| `temperature` | Sampling temperature | `0.1` |
| `maxTokens` | Max output tokens requested | `4096` |
| `topP` | Nucleus sampling parameter | `0.9` |
| `inputTokens` | Number of input tokens | `1240` |
| `outputTokens` | Number of output tokens | `340` |
| `timestamp` | ISO 8601 timestamp of extraction | `2026-06-04T12:00:00Z` |
| `jobId` | Parent ETL/AI job identifier | `job-2026-06-04-001` |
| `sourceRef` | Canonical reference of the source text | `Genesis.1.1` |
| `sourceDataset` | Dataset the text came from | `sefaria_api` |
| `chunkIndex` | Index of the chunk within the parent text | `0` |
| `totalChunks` | Total chunks for this text | `5` |

### 7.2 Prompt Hash (SHA-256)
The prompt hash ensures reproducibility. When a prompt template is updated, the hash changes, allowing downstream systems to detect which extractions were produced with which prompt version.

**Hash Computation:**
```python
import hashlib

def hash_prompt(prompt_text: str) -> str:
    return hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()[:16]
```

---

## 8. Human-in-the-Loop Workflow

### 8.1 Review Queue UI Design

The review queue is a web interface (part of the Torah Knowledge Graph frontend) where domain experts review, validate, or reject AI extractions.

**Queue Layout:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Torah KG Review Queue                              [Filters ▼] │
├──────────────────┬──────────────────────────────────────────────┤
│ Queue            │  Item #1,847 of 12,301                      │
│ ├─ High Priority │                                               │
│ ├─ Standard      │  Source: Genesis 1:1                          │
│ ├─ Citation      │  Text: "בְּרֵאשִׁית בָּרָא אֱלֹהִים..."         │
│ └─ Resolved      │                                               │
│                  │  Extracted Entity:                            │
│                  │  Name: God (אֱלֹהִים)                          │
│                  │  Type: Person                                 │
│                  │  Confidence: 0.82 (Human Review Required)     │
│                  │                                               │
│                  │  [✓ Accept]  [✗ Reject]  [✎ Edit]  [? Skip]  │
│                  │                                               │
│                  │  Explanation:                                 │
│                  │  "The text explicitly names God as the      │
│                  │   creator in Genesis 1:1."                  │
│                  │                                               │
│                  │  Evidence: "בָּרָא אֱלֹהִים"                   │
│                  │                                               │
│                  │  Model: claude-sonnet-4-6                     │
│                  │  Prompt: v2.1.0                               │
└──────────────────┴──────────────────────────────────────────────┘
```

**Queue Filters:**
- By entity type (Person, Place, Mitzvah, etc.)
- By confidence range (0.70–0.79, 0.80–0.89)
- By source text category (Tanakh, Talmud, Halakhah)
- By model/prompt version (to validate new prompt releases)
- By reviewer assignment

**Keyboard Shortcuts:**
- `A` = Accept
- `R` = Reject
- `E` = Edit
- `S` = Skip
- `J` = Next
- `K` = Previous

### 8.2 Bulk Validation Interface
For high-volume review (e.g., validating a new model release), reviewers can process items in bulk.

**Bulk Mode Features:**
- **Grid view**: 10–50 items per page, each showing source text, extracted entity, and confidence.
- **Bulk actions**: Select multiple items, then Accept All, Reject All, or Reject Selected.
- **Auto-accept rules**: Reviewers can define rules (e.g., "auto-accept all Person extractions with confidence > 0.85 from Tanakh") that apply to the current queue page.
- **Conflict detection**: If two reviewers disagree on the same item, it is escalated to a senior reviewer.

**Review Statistics Dashboard:**
- Personal stats: items reviewed, accuracy rate (vs. consensus), average time per item.
- Team stats: queue depth, throughput, backlog ETA.
- Model stats: precision/recall by model version, calibrated vs. raw confidence correlation.

### 8.3 Dispute Mechanism
If a reviewer believes an extraction is correct but the system flagged it incorrectly, or vice versa, they can open a dispute.

**Dispute Workflow:**
1. **Flag**: Reviewer clicks "Dispute" and selects a reason: `incorrect_extraction`, `wrong_confidence`, `missing_context`, `other`.
2. **Annotate**: Reviewer writes a brief note (min 20 characters) explaining the dispute.
3. **Escalate**: Item is moved to the `disputed_items` queue and assigned to a senior reviewer (rabbinic scholar or domain lead).
4. **Adjudicate**: Senior reviewer reviews the dispute, the original extraction, and the primary reviewer's note. They make a final ruling: `uphold` (original decision stands), `overturn` (reverse the decision), or `defer` (requires further research).
5. **Feedback Loop**: Disputes that result in `overturn` are logged in `model_feedback` and fed into the next prompt calibration cycle.

---

## 9. Batch Processing

### 9.1 Chunk Size Optimization
Text segments are chunked before extraction to maximize throughput while preserving context.

**Chunk Size by Text Category:**
| Category | Chunk Size (verses/paragraphs) | Rationale |
|----------|-------------------------------|-----------|
| Tanakh | 1 verse | Entities are typically verse-local |
| Mishnah | 1–2 mishnayot | Short, self-contained units |
| Talmud | 1 paragraph (~50–100 words) | Complex cross-references need local context |
| Halakhah (Rambam, Shulchan Aruch) | 1 halakhah/seif | Logical self-contained units |
| Kabbalah (Zohar) | 1 paragraph | Dense symbolism requires tight context |
| Commentary | 1 comment | Each comment is an independent unit |

**Dynamic Chunking:**
- If a chunk exceeds 2,000 tokens after encoding, it is split at the nearest paragraph boundary.
- If a chunk is smaller than 100 tokens, it is merged with the next chunk to reduce per-call overhead.

### 9.2 Parallel Processing Limits

**Concurrency Controls:**
| Resource | Max Parallel | Throttle |
|----------|--------------|----------|
| LLM API calls | 50 | Token bucket (10K TPM burst, 5K TPM sustained) |
| Qdrant embedding | 4 | GPU memory (batch size 100) |
| Neo4j writes | 8 | Connection pool (max 20) |
| PostgreSQL writes | 16 | Connection pool (max 50) |

**Backpressure:**
- If LLM API rate limit is hit (429), workers sleep for `Retry-After` seconds and requeue remaining chunks.
- If Qdrant GPU queue exceeds 10 batches, pause embedding workers until the queue drains.

### 9.3 Retry and Dead-Letter Queue

**Retry Policy:**
| Failure Type | Max Retries | Backoff | Action After Exhaustion |
|--------------|-------------|---------|------------------------|
| LLM API timeout | 3 | Exponential: 2s, 4s, 8s | Move to DLQ |
| LLM API 429 | 5 | As header + 1s buffer | Move to DLQ |
| LLM API 500 | 3 | 5s fixed | Move to DLQ |
| Invalid JSON output | 2 | 0s (immediate retry with stricter prompt) | Move to DLQ |
| Neo4j connection lost | 5 | Exponential: 1s, 2s, 4s, 8s, 16s | Move to DLQ |

**Dead-Letter Queue (`ai_extraction_dlq`):**
```json
{
  "jobId": "job-001",
  "chunkRef": "Genesis.1.1",
  "stage": "entity_extraction",
  "error": "LLM returned malformed JSON",
  "rawResponse": "...",
  "retryCount": 3,
  "lastAttempt": "2026-06-04T12:00:00Z",
  "originalPromptHash": "a3f7..."
}
```

**DLQ Processing:**
- DLQ consumer runs every 6 hours.
- Items are retried once with an extended timeout and a fallback model (Haiku for Sonnet tasks, Sonnet for Opus tasks).
- If still failing, items are archived to S3 and a Jira ticket is created for manual investigation.

---

## 10. Integration with ETL and Graph

### 10.1 Pipeline Stage Order

```
ETL Raw Texts → Qdrant Embedding → AI Extraction → Review Queue → Canonical Graph
```

**Stage Details:**
1. **ETL** loads raw texts into PostgreSQL and Neo4j (as `Text` nodes).
2. **Embedding** generates vector representations for all text segments; stored in Qdrant.
3. **AI Extraction** reads text segments from PostgreSQL, generates entities and relationships.
4. **Review Queue** holds extractions pending validation.
5. **Canonical Graph** receives validated extractions as new nodes and edges.

### 10.2 Idempotency
Every extraction job is idempotent. Re-running the same job with the same parameters produces the same results (or supersedes them with a new version).

- Neo4j nodes use `(ref, contentHash)` unique constraint; re-extraction with the same hash updates properties rather than creating duplicates.
- If an extraction changes (new model version, new prompt), the old extraction is marked `replaced_by` the new one, preserving history.

---

## 11. Security and Ethics

### 11.1 Model Usage Policy
- All LLM usage complies with Anthropic's Acceptable Use Policy.
- No user personal data is sent to the LLM API.
- Source texts sent for extraction are public domain or CC-licensed religious texts.

### 11.2 Bias Mitigation
- Prompts include explicit instructions to respect all Jewish denominational perspectives when extracting theological concepts.
- Reviewers are drawn from multiple backgrounds (Orthodox, Conservative, Reform, secular academic) to prevent single-perspective bias.
- Disproportionate extraction errors by text category (e.g., under-extraction of female figures) are monitored and reported monthly.

### 11.3 Data Retention
- Raw LLM responses are retained for 90 days for debugging and calibration.
- After 90 days, only the final extracted entities, provenance metadata, and aggregated statistics are retained.
- No LLM prompts or responses containing Hebrew/Aramaic text are used for model training by the LLM provider (per API terms).

---

*Document Version: 1.0*
*Last Updated: 2026-06-04*
*Maintainer: Torah Knowledge Graph AI Team*
