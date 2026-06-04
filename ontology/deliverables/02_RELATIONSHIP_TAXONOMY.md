# Torah Ontology — Relationship Taxonomy V1.0
## Chief Torah Ontology Scientist — Research Document

---

## 1. Purpose

This document defines the complete taxonomy of relationships in the Torah Ontology. Every relationship type must be formally defined with:
- Meaning
- Directionality
- Domain restrictions (which entity types can participate)
- Evidence requirements
- Confidence rules
- Known failure modes

---

## 2. Relationship Categories

### 2.1 Textual Relationships
Relationships between texts, verses, and commentaries.

#### COMMENTARY_ON
**Meaning:** One text explains, interprets, or comments on another text.
**Direction:** From commentary → commented text.
**Domain:** (Book|Verse|Chapter|Person) → (Book|Verse|Chapter)
**Evidence Requirements:**
- The exact text of the commentary
- The exact text being commented on
- The commentator's name
- The location in the commentary where it appears
**Confidence Rules:**
- If the commentary explicitly says "on [verse X]": confidence=1.0
- If the commentary implicitly discusses the text: confidence=0.8-0.95
- If attribution is uncertain: confidence=0.6-0.8
**Known Failure Modes:**
- Cross-referencing error: commentary attributed to wrong verse
- Anonymous commentary: "some say" without named source
- Multiple commentaries with same name (e.g., "Rashi" could mean different works)

#### QUOTES
**Meaning:** One text directly quotes, paraphrases, or alludes to another text.
**Direction:** From quoting text → quoted text.
**Domain:** (Verse|Book|Commentary) → (Verse|Book)
**Evidence Requirements:**
- The quoted text (exact words if direct)
- The context of the quotation
- Whether it is direct, paraphrase, or allusion
**Confidence Rules:**
- Exact quote with identical words: confidence=1.0
- Close paraphrase: confidence=0.85-0.95
- Allusion or remez: confidence=0.6-0.8
- AI-detected similarity: confidence=0.5-0.7
**Known Failure Modes:**
- Hebrew root-sharing: words share a root but are not quotations
- Common formulaic language: liturgical formulas appear in many texts
- Inverted quotations: Talmud quotes Tanakh, but Tanakh obviously does not quote Talmud

#### MENTIONS
**Meaning:** A text explicitly names or refers to an entity.
**Direction:** From text → entity.
**Domain:** (Verse|Book|Commentary) → (Person|Place|Concept|Mitzvah|Event|DivineName)
**Evidence Requirements:**
- The exact mention in the text
- Surrounding context (3-5 words before and after)
- Disambiguation if the name is ambiguous (e.g., "Moshe" could be Moshe Rabbeinu or another Moshe)
**Confidence Rules:**
- Explicit name with clear context: confidence=1.0
- Pronoun reference with clear antecedent: confidence=0.9
- Implied reference: confidence=0.7-0.85
**Known Failure Modes:**
- Homonymy: "David" could be King David, David Hamelech, or another David
- Metaphorical mentions: "lion of the tribe of Judah" is not a real lion
- Collective mentions: "the elders" refers to a group, not individuals

#### PART_OF
**Meaning:** One entity is a component or subdivision of another.
**Direction:** From part → whole.
**Domain:** (Verse|Chapter|Section|Book) → (Chapter|Book|Corpus)
**Evidence Requirements:**
- Structural evidence (verse numbers, chapter divisions)
- Canonical ordering
**Confidence Rules:**
- Canonical division: confidence=1.0
- Editorial division (added by printers): confidence=0.9
- Disputed division (e.g., chapter breaks in Tanakh): confidence=0.8
**Known Failure Modes:**
- Disputed chapter divisions (Christian chaptering vs. Jewish tradition)
- Verses that belong to multiple chapters in different editions
- Books with uncertain boundaries (e.g., end of Deuteronomy)

#### SOURCE_FOR
**Meaning:** A text is the primary source for a concept, law, or idea.
**Direction:** From source text → derived concept.
**Domain:** (Verse|Book|Commentary) → (Concept|Mitzvah|HalachicTopic|Opinion)
**Evidence Requirements:**
- The exact text that serves as the source
- The concept derived from it
- The derivation method (direct, inference, analogy)
**Confidence Rules:**
- Explicit "derived from [verse]": confidence=1.0
- Standard rabbinic derivation (e.g., kal v'chomer): confidence=0.95
- AI-inferred derivation: confidence=0.6-0.8
**Known Failure Modes:**
- Retrospective attribution: later authorities attribute ideas to earlier texts
- Multiple sources: a concept may have multiple independent sources
- Lost sources: Talmud refers to lost texts as sources

#### EXPANDS
**Meaning:** One text elaborates, extends, or adds detail to another text.
**Direction:** From expanding text → expanded text.
**Domain:** (Book|Commentary) → (Book|Commentary)
**Evidence Requirements:**
- Evidence that the second text existed before the first
- The specific additions made
**Confidence Rules:**
- Explicit "as it says in [earlier text]": confidence=0.95
- Clear thematic continuation: confidence=0.8-0.9
**Known Failure Modes:**
- Parallel development: two texts may expand on a common source independently
- Pseudepigraphic texts: texts falsely attributed to earlier authors

#### CONTRADICTS
**Meaning:** Two texts make assertions that cannot both be true in the same context.
**Direction:** Undirected (symmetric).
**Domain:** (Verse|Book|Commentary|Opinion) ↔ (Verse|Book|Commentary|Opinion)
**Evidence Requirements:**
- Both contradictory assertions quoted exactly
- The context of each assertion
- Evidence that they are addressing the same question
**Confidence Rules:**
- Direct logical contradiction in same context: confidence=0.95
- Apparent contradiction (different contexts): confidence=0.7
- AI-detected contradiction: confidence=0.5-0.7
**Known Failure Modes:**
- Contextual resolution: apparent contradictions resolved by different contexts
- Dialectical method: Talmud intentionally juxtaposes contradictions to generate discussion
- Translation artifacts: contradictions introduced by translation

---

### 2.2 Conceptual Relationships
Relationships between ideas, concepts, and principles.

#### RELATED_TO
**Meaning:** Two concepts are connected in thought, practice, or meaning.
**Direction:** Undirected (symmetric).
**Domain:** Concept ↔ Concept
**Evidence Requirements:**
- Explanation of the connection
- At least one textual source linking them
**Confidence Rules:**
- Explicitly linked in Torah literature: confidence=0.9
- Thematically connected by scholars: confidence=0.7-0.8
- AI-detected semantic similarity: confidence=0.5-0.7
**Known Failure Modes:**
- Over-association: concepts mentioned in same text but unrelated
- Domain leakage: concepts related in one domain but not another

#### DERIVED_FROM
**Meaning:** One concept is logically or textually derived from another.
**Direction:** From derived concept → source concept.
**Domain:** (Concept|HalachicTopic|Mitzvah|Opinion) → (Concept|Verse|HalachicTopic)
**Evidence Requirements:**
- The derivation method (e.g., "kal v'chomer", "gezeirah shavah", "binyan av")
- The source text or concept
- The reasoning chain
**Confidence Rules:**
- Explicit derivation in Talmudic hermeneutics: confidence=0.95
- Philosophical derivation: confidence=0.8
- AI-inferred derivation: confidence=0.5-0.7
**Known Failure Modes:**
- Circular derivation: A derived from B, B derived from A
- Over-derivation: concept stretched beyond its original meaning
- Lost intermediate steps: derivation requires missing steps

#### CAUSES
**Meaning:** One concept or event causes or leads to another.
**Direction:** From cause → effect.
**Domain:** (Concept|Event|Mitzvah|HistoricalEvent) → (Concept|Event|Mitzvah)
**Evidence Requirements:**
- Causal mechanism (divine decree, natural law, spiritual law)
- Conditions under which causation occurs
- Counter-evidence if causation is conditional
**Confidence Rules:**
- Explicit causal statement in Torah: confidence=0.9
- Rabbinic causal principle: confidence=0.8
- Chassidic/Kabbalistic spiritual causation: confidence=0.7
**Known Failure Modes:**
- Correlation vs. causation: two concepts often co-occur but one does not cause the other
- Divine inscrutability: God's reasons are not always knowable
- Multiple causes: an effect may have many contributing causes

#### REPAIRS
**Meaning:** One practice, prayer, or concept repairs or corrects a spiritual damage or sin.
**Direction:** From repair method → damage/sin.
**Domain:** (Mitzvah|Prayer|Tikkun|Segulah) → (Concept|Sin|Mitzvah)
**Evidence Requirements:**
- The damage being repaired
- The repair method
- Source claiming the repair is effective
- Conditions for efficacy
**Confidence Rules:**
- Explicit repair instruction in Kabbalah/Chassidut: confidence=0.85
- Talmudic statement of repair: confidence=0.9
- Folk segulah without named source: confidence=0.3 (flagged as unverified)
**Known Failure Modes:**
- Unverified segulot: popular practices without Torah source
- Conflicting repair methods: different sources prescribe different repairs for same damage
- Placebo effect: repair attributed to practice when correlation is coincidental

#### ASSOCIATED_WITH
**Meaning:** Two concepts are frequently mentioned together, practiced together, or belong to the same category.
**Direction:** Undirected.
**Domain:** (Concept|Mitzvah|Sefirah|DivineName) ↔ (Concept|Mitzvah|Sefirah|DivineName)
**Evidence Requirements:**
- Evidence of co-occurrence or co-practice
- The nature of the association
**Confidence Rules:**
- Explicitly paired in Torah: confidence=0.9
- Frequently co-mentioned by commentators: confidence=0.8
- Thematic association by scholars: confidence=0.6
**Known Failure Modes:**
- Co-occurrence bias: concepts mentioned in same chapter but not truly associated
- Historical contingency: concepts associated in one era but not another

---

### 2.3 Social Relationships
Relationships between people and institutions.

#### TEACHER_OF
**Meaning:** A person taught another person.
**Direction:** From teacher → student.
**Domain:** Person → Person
**Evidence Requirements:**
- Explicit statement "[A] learned from [B]"
- Contextual evidence (student quotes teacher)
**Confidence Rules:**
- Explicit "my teacher": confidence=1.0
- Quoted as authority: confidence=0.9
- Same yeshiva/academy: confidence=0.7
**Known Failure Modes:**
- Indirect transmission: "from Moshe to Yehoshua" spans many intermediaries
- Multiple teachers: a student may have many teachers
- Unknown teachers: some sages have unknown teachers

#### STUDENT_OF
**Meaning:** Inverse of TEACHER_OF.
**Direction:** From student → teacher.

#### DISCIPLE_OF
**Meaning:** A close, dedicated student in Chassidic context.
**Direction:** From disciple → master.
**Domain:** Person → Person
**Evidence Requirements:**
- Explicit designation as disciple
- Stories of close relationship
**Confidence Rules:**
- Explicit "my disciple": confidence=1.0
- Stories indicating close relationship: confidence=0.8
**Known Failure Modes:**
- Formal vs. informal: some "disciples" were casual students
- Posthumous attribution: disciples claimed by later traditions

#### CONTEMPORARY_OF
**Meaning:** Two people lived in the same era and could have known each other.
**Direction:** Undirected.
**Domain:** Person ↔ Person
**Evidence Requirements:**
- Overlapping lifespans
- Shared geographical region
**Confidence Rules:**
- Explicitly mentioned together: confidence=0.9
- Lifespan overlap with shared region: confidence=0.7
**Known Failure Modes:**
- No interaction: contemporaries who never met
- Regional separation: same era but different countries

#### IN_DYNASTY
**Meaning:** A person belongs to a Chassidic dynasty.
**Direction:** From person → dynasty.
**Domain:** Person → (string dynasty name)
**Evidence Requirements:**
- Explicit identification with dynasty
- Lineage tracing
**Confidence Rules:**
- Explicit: confidence=1.0
- Lineage-based: confidence=0.9

---

### 2.4 Promissory Relationships
Relationships involving divine promises and spiritual remedies.

#### PROMISES
**Meaning:** A promise is made to or about an entity.
**Direction:** From promise → beneficiary/entity.
**Domain:** Promise → (Concept|Mitzvah|Person|Segulah|Event)
**Evidence Requirements:**
- Exact promise text
- Conditions
- Beneficiaries
- Source
**Confidence Rules:**
- Explicit promise in Tanakh: confidence=1.0
- Talmudic promise: confidence=0.95
- Kabbalistic/Chassidic promise: confidence=0.85
**Known Failure Modes:**
- Conditional vs. unconditional promises: confusion about whether conditions apply
- Corporate vs. individual: promises to Israel vs. to individuals
- Temporal limitation: promises for specific eras

#### SEGULAH_FOR
**Meaning:** A segulah is prescribed for a purpose.
**Direction:** From segulah → purpose/concept.
**Domain:** Segulah → (Concept|Mitzvah|Person|Promise|Event)
**Evidence Requirements:**
- Purpose
- Requirements
- Source
- Authority level
**Confidence Rules:**
- Named source with explicit segulah: confidence=0.85
- Minhag without named source: confidence=0.5
- Folk practice without Torah source: confidence=0.2 (flagged)
**Known Failure Modes:**
- Unsourced segulot: practices without any Torah authority
- Conflicting segulot: different sources give different segulot for same purpose
- Placebo effect: benefits attributed to segulah without causal link

#### TIKKUN_FOR
**Meaning:** A tikkun repairs a specific sin or spiritual damage.
**Direction:** From tikkun → sin/damage.
**Domain:** Tikkun → (Concept|Sin|Mitzvah|Event)
**Evidence Requirements:**
- Sin being repaired
- Repair method
- Source
**Confidence Rules:**
- Explicit tikkun in Kabbalistic source: confidence=0.85
- Talmudic source: confidence=0.9
- Chassidic source: confidence=0.85
**Known Failure Modes:**
- Missing context: tikkun may only apply in specific circumstances
- Over-generalization: tikkun prescribed for sin A applied to sin B

---

### 2.5 Dispute Relationships
Relationships involving disagreements between authorities.

#### DISPUTES
**Meaning:** Two opinions are in conflict.
**Direction:** From opinion → opinion (or via Dispute entity).
**Domain:** Opinion ↔ Opinion
**Evidence Requirements:**
- Both opinions stated exactly
- The point of disagreement
- The sources for each opinion
**Confidence Rules:**
- Explicitly recorded as dispute: confidence=1.0
- Scholars identify as dispute: confidence=0.9
**Known Failure Modes:**
- Apparent dispute (different cases): opinions address different situations
- Semantic dispute (same conclusion, different reasoning)
- Unrecorded agreement: authorities actually agree but texts present them as disagreeing

#### AGREES_WITH
**Meaning:** Two opinions support or align with each other.
**Direction:** Undirected.
**Domain:** Opinion ↔ Opinion
**Evidence Requirements:**
- Evidence of agreement
- Source where agreement is stated
**Confidence Rules:**
- Explicit agreement: confidence=1.0
- Parallel reasoning: confidence=0.8
- Same conclusion: confidence=0.7
**Known Failure Modes:**
- Independent agreement: two authorities reach same conclusion without knowing each other
- Coincidental agreement: same conclusion for different reasons

#### RESPONDS_TO
**Meaning:** One authority explicitly responds to another's opinion.
**Direction:** From responding opinion → target opinion.
**Domain:** Opinion → Opinion
**Evidence Requirements:**
- Explicit "Rabbi X says... but I say..."
- The response text
**Confidence Rules:**
- Explicit response: confidence=1.0
- Implied response (same topic, opposite conclusion): confidence=0.8
**Known Failure Modes:**
- Misattribution: responding to opinion actually held by someone else
- Straw man: responding to weakened version of opponent's argument

---

### 2.6 Hierarchical Relationships
Relationships of classification and subsumption.

#### SUBSUMES
**Meaning:** One concept encompasses or is a broader category of another.
**Direction:** From broader → narrower.
**Domain:** Concept → Concept
**Evidence Requirements:**
- Evidence that the narrower concept is a type/instance of the broader
**Confidence Rules:**
- Explicit classification: confidence=0.95
- Thematic inclusion: confidence=0.8
**Known Failure Modes:**
- Overlapping categories: concept belongs to multiple broader categories
- Fuzzy boundaries: unclear whether concept is subsumed

#### INSTANCE_OF
**Meaning:** One entity is a specific instance of a general type.
**Direction:** From instance → type.
**Domain:** (Mitzvah|Event|Person|Place) → Concept
**Evidence Requirements:**
- Evidence that the instance belongs to the type
**Confidence Rules:**
- Explicit designation: confidence=1.0
- Clear classification: confidence=0.9
**Known Failure Modes:**
- Borderline cases: unclear whether entity is an instance
- Prototype effects: some instances are more central than others

---

### 2.7 Kabbalistic Relationships
Relationships specific to Kabbalistic concepts.

#### COMPOSES
**Meaning:** One sefirah or partzuf is composed of others.
**Direction:** From whole → component.
**Domain:** (Partzuf|Sefirah) → (Sefirah|Partzuf)
**Evidence Requirements:**
- Kabbalistic source describing composition
**Confidence Rules:**
- Explicit in Lurianic Kabbalah: confidence=0.95
- Zoharic source: confidence=0.9
**Known Failure Modes:**
- Different Lurianic schools: composition may vary by school
- Symbolic vs. literal: some compositions are metaphorical

#### EMANATES_FROM
**Meaning:** One sefirah emanates from or flows from another.
**Direction:** From emanated → source.
**Domain:** Sefirah → Sefirah
**Evidence Requirements:**
- Kabbalistic source describing emanation
- Directionality (which flows into which)
**Confidence Rules:**
- Standard Tree of Life structure: confidence=0.95
- Variant structures: confidence=0.8
**Known Failure Modes:**
- Bidirectional flow: some sefirot influence each other mutually
- Different kabbalistic systems: Cordovero vs. Luria vs. Ashlag

#### CORRESPONDS_TO
**Meaning:** One concept in one domain corresponds to another in a different domain (e.g., sefirah to body part, letter, or world).
**Direction:** Undirected.
**Domain:** (Sefirah|DivineName|Letter) ↔ (BodyPart|World|Color|Day)
**Evidence Requirements:**
- Kabbalistic source stating correspondence
**Confidence Rules:**
- Explicit correspondence: confidence=0.9
- Inferred correspondence: confidence=0.7
**Known Failure Modes:**
- Multiple correspondences: one sefirah may correspond to multiple things
- System-dependent: correspondences vary by kabbalistic system

#### BALANCES
**Meaning:** Two sefirot or middot balance each other.
**Direction:** Undirected.
**Domain:** (Sefirah|Middah) ↔ (Sefirah|Middah)
**Evidence Requirements:**
- Source describing balance
- The mechanism of balance
**Confidence Rules:**
- Explicit balance (e.g., Chesed-Gevurah): confidence=0.95
- Thematic balance: confidence=0.8
**Known Failure Modes:**
- Asymmetric balance: one side may dominate
- Context-dependent: balance depends on situation

---

## 3. Relationship Metadata

Every relationship instance MUST include:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| source | source_ref | yes | Where this relationship is asserted |
| confidence | float | yes | 0.0-1.0 confidence score |
| extraction_method | enum | yes | Manual \| Imported \| AI_Extracted \| Derived |
| created_by | string | yes | Person or system that created it |
| created_at | datetime | yes | Timestamp |
| explanation | text | no | Why this relationship exists |
| is_disputed | boolean | yes | Whether the relationship itself is disputed |
| dispute_ref | dispute_ref | no | If disputed, link to Dispute entity |
| context | text | no | Contextual conditions for this relationship |

---

## 4. Confidence Calibration

### Confidence Scale
| Range | Meaning | Human Review Required? |
|-------|---------|----------------------|
| 1.0 | Canonical, explicit, undisputed | No |
| 0.95-0.99 | Explicit but complex | Optional |
| 0.85-0.94 | Well-supported inference | Optional |
| 0.70-0.84 | Reasonable inference | Yes (validator review) |
| 0.50-0.69 | Weak inference | Yes (expert review) |
| <0.50 | Speculative | Reject or flag strongly |

### Confidence by Relationship Type
| Relationship | Canonical | AI-Extracted |
|-------------|-----------|--------------|
| COMMENTARY_ON | 1.0 | 0.6-0.8 |
| QUOTES | 1.0 | 0.5-0.7 |
| MENTIONS | 1.0 | 0.7-0.9 |
| PART_OF | 1.0 | 0.9 |
| SOURCE_FOR | 0.95 | 0.5-0.7 |
| RELATED_TO | 0.9 | 0.5-0.7 |
| DERIVED_FROM | 0.95 | 0.5-0.7 |
| CAUSES | 0.9 | 0.5-0.6 |
| REPAIRS | 0.85 | 0.4-0.6 |
| PROMISES | 1.0 | 0.6-0.8 |
| SEGULAH_FOR | 0.85 | 0.3-0.5 |
| TIKKUN_FOR | 0.85 | 0.4-0.6 |
| DISPUTES | 1.0 | 0.6-0.8 |
| AGREES_WITH | 0.9 | 0.5-0.7 |
| SUBSUMES | 0.95 | 0.6-0.8 |
| EMANATES_FROM | 0.95 | 0.5-0.7 |

---

## 5. Relationship Validation Rules

### RV1: Source Requirement
Every relationship MUST have a source. No relationship exists without provenance.

### RV2: Domain Compatibility
The relationship type must be compatible with the entity types it connects. For example, COMMENTARY_ON cannot link a Place to a Person.

### RV3: Confidence Consistency
If confidence < 0.7, the relationship MUST be flagged for human review.

### RV4: Dispute Linkage
If is_disputed=true, the relationship MUST link to a Dispute entity.

### RV5: Context Preservation
If the relationship only holds in certain contexts (e.g., "according to Rambam"), that context MUST be recorded.

### RV6: Direction Preservation
Directional relationships must not be reversed. COMMENTARY_ON goes from commentary to source, never the reverse.

### RV7: Anti-Cyclicity for Hierarchies
Hierarchical relationships (SUBSUMES, PART_OF, INSTANCE_OF) must not form cycles.

### RV8: Cross-Domain Explicitness
Cross-domain relationships (e.g., a Kabbalistic concept linked to a Halachic concept) MUST include an explanation of how they connect.

---

## 6. Known Relationship Taxonomy Failures

### Failure 1: The Omnidirectional Relationship
Some Torah relationships are fundamentally bidirectional in a way that cannot be captured by directed edges. Example: "Chesed balances Gevurah" — both are simultaneously in tension and harmony. A directed edge loses this symmetry.

**Analysis:** The ontology can represent this as two directed edges (BALANCES in both directions) or as an undirected edge with a note. However, the fundamental tension-harmony duality is not fully captured.

### Failure 2: The Context-Dependent Relationship
"Teshuvah" is RELATED_TO "Kapparah" in some contexts (Yom Kippur) but not in others (daily repentance). A single edge cannot capture this context-sensitivity.

**Analysis:** The ontology requires context annotations on every relationship, but this creates combinatorial explosion. A relationship with 5 valid contexts and 3 invalid contexts requires 8 annotations.

### Failure 3: The Degree of Relationship
Some relationships have degrees: "strongly agrees with" vs. "weakly agrees with". Binary edges cannot capture gradation.

**Analysis:** The ontology uses confidence scores and strength properties, but these are post-hoc quantifications of what Torah literature expresses qualitatively.

### Failure 4: The Evolving Relationship
Rambam and Ramban disagreed on some topics but Ramban's commentary often defends Rambam against critics. Their relationship is simultaneously DISPUTES and AGREES_WITH depending on the topic and era.

**Analysis:** The ontology must create topic-specific relationship instances, not global relationship instances between persons. This requires very fine-grained relationship creation.

### Failure 5: The Meta-Relationship
Some Torah texts discuss relationships themselves (e.g., Zohar discusses how sefirot relate to each other). The ontology needs relationships ABOUT relationships.

**Analysis:** This requires a meta-level in the ontology where the ontology itself becomes a subject of study. This is philosophically complex and may require a separate meta-ontology layer.
