# Torah Ontology Blueprint V1.0
## Chief Torah Ontology Scientist — Research Document

---

## 1. Purpose

This document defines the formal ontology for representing Torah knowledge across all domains: Tanakh, Halacha, Kabbalah, Chassidut, and Musar. It is a conceptual model ONLY. No code. No databases. No APIs.

The purpose is to discover whether Torah knowledge can be formally represented before any implementation begins.

---

## 2. Design Principles

### P1: Authenticity-First
Every concept must correspond to a real term used in authentic Torah literature. No invented terms. No modern neologisms unless they are well-established in Torah scholarship.

### P2: Multi-Perspectival
The same concept can exist simultaneously in multiple domains with different meanings. The ontology must represent this without forcing a single definition.

### P3: Dispute-Preservation
When authorities disagree, the ontology must represent ALL opinions as first-class objects. No opinion is "correct" in the ontology.

### P4: Source-Binding
Every assertion in the ontology must be bound to a specific textual source. Unsourced assertions are not allowed.

### P5: Context-Sensitivity
The meaning of a concept depends on its textual context (book, chapter, section, commentator). The ontology must track context.

### P6: Hierarchical Flexibility
Concepts may have multiple parents, multiple children, and non-hierarchical relationships. The ontology is a graph, not a tree.

---

## 3. Entity Types

### Core Entities

#### Concept
A fundamental idea, principle, or notion in Torah thought.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| canonical_name | string | yes | Primary English name |
| hebrew_name | string | yes | Hebrew name in original spelling |
| domain | enum | yes | Torah \| Halacha \| Kabbalah \| Chassidut \| Musar |
| sub_domain | string | no | e.g., "Sefirot", "Middot", "Korbanot" |
| definition | text | yes | Core meaning |
| hebrew_definition | text | no | Definition in Hebrew |
| aliases | [string] | no | Alternative names |
| etymology | text | no | Linguistic origin |
| first_appearance | source_ref | no | Where concept first appears |
| authority_level | enum | yes | Biblical \| Talmudic \| Geonic \| Rishonic \| Achronic \| Modern |
| is_disputed | boolean | yes | Whether authorities disagree on its meaning |
| has_multiple_domains | boolean | yes | Whether it appears in multiple domains with different meanings |
| parent_concepts | [concept_ref] | no | Broader concepts it falls under |
| child_concepts | [concept_ref] | no | Narrower concepts it encompasses |
| related_concepts | [concept_ref] | no | Concepts it is connected to |
| source_requirements | [source_spec] | yes | Minimum sources needed to define it |
| dispute_rules | [dispute_rule] | no | How disputes about this concept are modeled |
| context_rules | [context_rule] | no | Rules for interpreting meaning in different contexts |

#### Person
A human being mentioned in Torah literature.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| canonical_name | string | yes | Primary name |
| hebrew_name | string | yes | Hebrew name |
| aliases | [string] | no | Alternative names |
| lifespan | string | no | Birth-death dates (Hebrew/Gregorian) |
| era | enum | yes | Biblical \| Tannaitic \| Amoraic \| Geonic \| Rishonic \| Achronic \| Modern |
| primary_role | enum | yes | Prophet \| King \| Sage \| Commentator \| Kabbalist \| Tzaddik \| Posek \| etc. |
| secondary_roles | [enum] | no | Additional roles |
| teacher_of | [person_ref] | no | Known students |
| student_of | [person_ref] | no | Known teachers |
| authored_books | [book_ref] | no | Books written by this person |
| lineage | string | no | Family connections |
| burial_place | place_ref | no | Burial location |
| generation | integer | no | For Chassidic rebbes: generation |
| dynasty | string | no | Chassidic dynasty |
| authority_level | enum | yes | How authoritative this person is in their domain |
| is_disputed | boolean | yes | Whether their identity or status is disputed |

#### Book
A written work in Torah literature.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| canonical_title | string | yes | Primary title |
| hebrew_title | string | yes | Hebrew title |
| aliases | [string] | no | Alternative titles |
| author | person_ref | yes | Primary author |
| co_authors | [person_ref] | no | Additional authors |
| domain | enum | yes | Torah \| Halacha \| Kabbalah \| Chassidut \| Musar |
| category | enum | yes | Tanakh \| Mishnah \| Talmud \| Midrash \| Commentaries \| etc. |
| corpus | enum | yes | Specific corpus |
| era | enum | yes | When it was written |
| language | enum | yes | Hebrew \| Aramaic \| Bilingual |
| is_canonical | boolean | yes | Whether it is considered canonical |
| is_commentary | boolean | yes | Whether it is a commentary on another work |
| commented_on | [book_ref] | no | What works it comments on |
| total_chapters | integer | no | Structural info |
| total_verses | integer | no | For verse-based works |
| authority_level | enum | yes | How authoritative in its domain |
| is_disputed | boolean | yes | Whether authorship or authenticity is disputed |

#### Source
A specific textual location where information appears.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| book | book_ref | yes | Book this source is in |
| chapter | string | no | Chapter/section |
| verse | string | no | Verse/paragraph |
| page | string | no | Page number (for printed works) |
| daf | string | no | Daf for Talmud |
| amud | string | no | Amud for Talmud |
| siman | string | no | Siman for Shulchan Aruch |
| seif | string | no | Seif for Shulchan Aruch |
| halacha | string | no | Halacha number for Rambam |
| chapter_in_book | string | no | Chapter in structured works |
| paragraph | string | no | Paragraph in prose works |
| url | string | no | URL if available online |
| exact_text | text | no | Exact quoted text |
| hebrew_text | text | no | Hebrew text |
| translation | text | no | Translation if original is Hebrew/Aramaic |
| context | text | no | Surrounding context |
| authority_level | enum | yes | Biblical \| Talmudic \| Geonic \| Rishonic \| Achronic \| Modern |

#### Verse
A specific verse in Tanakh or other verse-based literature.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| book | book_ref | yes | Book |
| chapter | integer | yes | Chapter number |
| verse_number | integer | yes | Verse number |
| ref | string | yes | Canonical reference ("Genesis 1:1") |
| text_hebrew | text | yes | Hebrew text with cantillation |
| text_english | text | no | Primary translation |
| text_aramaic | text | no | Aramaic version if applicable |
| language | enum | yes | Hebrew \| Aramaic \| Bilingual |
| category | enum | yes | Tanakh \| Mishnah \| Talmud \| etc. |
| corpus | enum | yes | Specific corpus |

#### Mitzvah
A divine commandment.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| canonical_name | string | yes | Name |
| hebrew_name | string | yes | Hebrew name |
| number | integer | no | Rambam's enumeration |
| category | enum | yes | Positive \| Negative \| Rabbinic |
| source_verse | verse_ref | yes | Primary biblical source |
| description | text | yes | What it requires |
| applicable_to | enum | yes | All \| Kohen \| Levi \| Israel \| Women \| Men |
| time_bound | boolean | yes | Whether it is time-bound |
| rabbinic | boolean | yes | Whether it is d'rabbanan |
| is_disputed | boolean | yes | Whether it is counted differently by authorities |
| dispute_rules | [dispute_rule] | no | How counting disputes are modeled |

#### HalachicTopic
A topic in Jewish law.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| canonical_name | string | yes | Name |
| hebrew_name | string | yes | Hebrew name |
| shulchan_aruch_section | string | no | OC \| YD \| EH \| CM |
| rambam_hilchot | string | no | Hilchot reference |
| primary_sources | [source_ref] | yes | Key Talmudic sources |
| is_disputed | boolean | yes | Whether ruling varies by authority |
| dispute_rules | [dispute_rule] | no | How disputes are modeled |

#### Middah
A character trait.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| canonical_name | string | yes | Name |
| hebrew_name | string | yes | Hebrew name |
| domain | enum | yes | Torah \| Halacha \| Kabbalah \| Chassidut \| Musar |
| is_positive | boolean | yes | Whether it is a positive trait |
| is_negative | boolean | yes | Whether it is a negative trait (can be both) |
| opposing_trait | middah_ref | no | The trait that balances/opposes it |
| source_in_mishnah | string | no | Pirkei Avot or other |
| is_disputed | boolean | yes | Whether authorities disagree on its importance |

#### Prayer
A prayer or liturgical text.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| canonical_name | string | yes | Name |
| hebrew_name | string | yes | Hebrew name |
| text_hebrew | text | yes | Hebrew text |
| text_english | text | no | Translation |
| occasion | enum | yes | Daily \| Shabbat \| Holiday \| Lifecycle |
| specific_time | enum | no | Morning \| Evening \| etc. |
| source | source_ref | yes | Talmudic or Zohar source |
| has_kavvanot | boolean | yes | Whether it has kabbalistic intentions |
| is_biblical | boolean | yes | Whether text is from Tanakh |

#### DivineName
A name of God.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| canonical_name | string | yes | Name |
| hebrew_name | string | yes | Hebrew name |
| pronunciation | string | no | How it is pronounced |
| meaning | text | no | Etymological meaning |
| gematria | integer | no | Numerical value |
| first_appearance | verse_ref | no | Where it first appears |
| is_explicit | boolean | yes | One of the 7 explicit names |
| sefirot_associations | [sefirah_ref] | no | Associated sefirot |

#### Sefirah
A divine emanation in Kabbalah.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| canonical_name | string | yes | Name |
| hebrew_name | string | yes | Hebrew name |
| attribute | text | yes | Primary attribute |
| corresponding_day | string | no | Omer day |
| color | string | no | Visual color |
| partzuf | string | no | e.g., Abba, Imma |
| world | enum | no | Atzilut \| Beriah \| Yetzirah \| Asiyah |
| body_correspondence | string | no | Body part correspondence |
| letter | string | no | Hebrew letter correspondence |
| number | integer | yes | Position in Tree of Life (1-10) |

#### Partzuf
A divine countenance/face in Lurianic Kabbalah.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| canonical_name | string | yes | Name |
| hebrew_name | string | yes | Hebrew name |
| sefirot_composition | [sefirah_ref] | yes | Which sefirot compose it |
| world | enum | yes | Atzilut \| Beriah \| Yetzirah \| Asiyah |
| associated_with | enum | no | Abba \| Imma \| Zeir Anpin \| Nukvah \| Arich Anpin \| Atik |
| is_disputed | boolean | yes | Whether its composition is disputed |

#### Segulah
A spiritual remedy or protective practice.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| canonical_name | string | yes | Name |
| hebrew_name | string | yes | Hebrew name |
| purpose | text | yes | What it protects against or brings |
| requirements | [text] | yes | What must be done |
| source | source_ref | yes | Primary source |
| source_type | enum | yes | Talmud \| Zohar \| Shulchan Aruch \| Chassidic |
| authority_level | enum | yes | Biblical \| Talmudic \| Kabbalistic \| Minhag |
| conditions | [text] | no | Prerequisites |
| timing | string | no | When it applies |
| is_disputed | boolean | yes | Whether its efficacy is disputed |

#### Promise
A divine promise in Torah literature.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| canonical_name | string | yes | Name or description |
| promise_text | text | yes | Exact wording |
| hebrew_text | text | no | Hebrew wording |
| source | source_ref | yes | Canonical source |
| source_type | enum | yes | Biblical \| Talmudic \| Kabbalistic |
| conditions | [text] | no | Requirements to receive it |
| beneficiaries | [text] | no | Who is promised |
| category | enum | yes | Protection \| Prosperity \| Health \| Children \| Redemption |
| authority_level | enum | yes | Biblical \| Talmudic \| Kabbalistic \| Chassidic |
| related_mitzvot | [mitzvah_ref] | no | Mitzvot connected to this promise |
| is_disputed | boolean | yes | Whether conditions are disputed |

#### Tikkun
A spiritual repair or correction.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| canonical_name | string | yes | Name |
| hebrew_name | string | yes | Hebrew name |
| sin_or_damage | text | yes | What is being repaired |
| correction_method | text | yes | How to repair |
| source | source_ref | yes | Primary source |
| source_type | enum | yes | Biblical \| Talmudic \| Kabbalistic \| Chassidic |
| efficacy | text | no | Expected outcome |
| conditions | [text] | no | Requirements |
| related_sefirot | [sefirah_ref] | no | Sefirot involved |
| is_disputed | boolean | yes | Whether method is disputed |

#### Place
A geographical location.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| canonical_name | string | yes | Name |
| hebrew_name | string | yes | Hebrew name |
| aliases | [string] | no | Alternative names |
| modern_name | string | no | Contemporary name |
| country | string | no | Modern country |
| coordinates | lat/lng | no | GPS coordinates |
| significance | enum | yes | Temple \| Burial \| Miracle \| Border \| City |
| is_holy_city | boolean | yes | One of the 4 holy cities |
| is_in_israel | boolean | yes | Within modern Israel |
| tribe | string | no | Tribal allocation |

#### Event
A historical event.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| canonical_name | string | yes | Name |
| hebrew_name | string | yes | Hebrew name |
| date_hebrew | string | no | Hebrew date |
| date_gregorian | string | no | Approximate Gregorian date |
| era | enum | yes | Biblical \| Tannaitic \| etc. |
| participants | [person_ref] | no | Key people involved |
| location | place_ref | no | Primary location |
| significance | text | yes | Theological/historical meaning |
| source_verses | [verse_ref] | yes | Primary biblical references |
| is_disputed | boolean | yes | Whether date or participants are disputed |

#### SoulRoot
A root of souls in Kabbalah (RESTRICTED — authoritative sources only).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| canonical_name | string | yes | Name |
| hebrew_name | string | yes | Hebrew name |
| source_authority | enum | yes | Zohar \| Arizal \| Rashash \| VilnaGaon |
| source_location | source_ref | yes | Exact source |
| description | text | yes | Description |
| is_disputed | boolean | yes | Whether different schools disagree |
| **REQUIREMENT** | | | **Only sources from Zohar, Etz Chaim, Shaar HaGilgulim, or writings of Arizal/Rashash/Vilna Gaon** |

#### Opinion
A specific position held by an authority.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| canonical_name | string | yes | Brief description of position |
| holder | person_ref | yes | Who holds this opinion |
| topic | concept_ref | yes | What it is about |
| position | text | yes | What they say |
| source | source_ref | yes | Where they say it |
| reasoning | text | no | Their reasoning |
| contradicts | [opinion_ref] | no | Opinions it contradicts |
| agrees_with | [opinion_ref] | no | Opinions it agrees with |
| is_majority_opinion | boolean | yes | Whether it is the majority view |
| authority_level | enum | yes | How authoritative this opinion is |

#### Dispute
A disagreement between authorities.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| canonical_name | string | yes | Brief description |
| topic | concept_ref | yes | What the dispute is about |
| opinion_a | opinion_ref | yes | First opinion |
| opinion_b | opinion_ref | yes | Second opinion |
| additional_opinions | [opinion_ref] | no | Other opinions in the dispute |
| resolution | text | no | How later authorities resolved it |
| is_resolved | boolean | yes | Whether there is a consensus resolution |
| era | enum | yes | When the dispute occurred |
| primary_source | source_ref | yes | Where the dispute is recorded |
| is_active | boolean | yes | Whether it is still disputed |

---

## 4. Ontology Rules

### R1: Concept Multi-Domain Rule
If a concept appears in multiple domains with different meanings, it MUST be modeled as separate concept instances with domain tags, NOT as a single concept with multiple definitions.

Example: "Teshuvah" in Torah (return to God), in Halacha (process of repentance), in Musar (character trait of remorse), in Kabbalah (tikkun of sins). These are 4 distinct concept instances linked by RELATED_TO.

### R2: Dispute Preservation Rule
When authorities disagree about a concept, the ontology MUST create:
1. A Dispute entity
2. An Opinion entity for EACH authority
3. Links between opinions and the dispute

The base concept remains neutral. It does NOT contain a "correct" definition.

### R3: Source Minimum Rule
Every entity MUST have at least one Source. Every relationship MUST have at least one Source. Entities without sources are INVALID.

### R4: Authority Level Rule
Every entity MUST be tagged with an authority_level:
- Biblical: Torah, Nevi'im, Ketuvim
- Talmudic: Mishnah, Talmud Bavli, Talmud Yerushalmi
- Geonic: Gaonic responsa
- Rishonic: 11th-15th century authorities
- Achronic: 16th-19th century authorities
- Modern: 20th-21st century authorities

### R5: Context Rule
When a concept appears in different contexts (e.g., Rashi vs. Ramban on the same verse), the ontology MUST track:
- The specific source where the usage appears
- The authority using it
- The specific meaning in that context

### R6: Soul Root Restriction Rule
SoulRoot entities are RESTRICTED. They may ONLY be created from:
- Zohar (all volumes)
- Writings of the Arizal (Etz Chaim, Pri Etz Chaim, Shaar HaKavanot, etc.)
- Writings of Rashash (Siddur HaAri)
- Writings of the Vilna Gaon (commentary on Sifra DeTzni'uta)

NO other sources may be used for SoulRoot. NO AI extraction. NO modern interpretation.

### R7: Segulah Efficacy Rule
Segulah entities MUST include:
- The specific conditions required
- The specific source claiming efficacy
- The authority_level of that claim

Segulah without conditions or without a named source is INVALID.

### R8: Promise Condition Rule
Promise entities MUST include:
- The exact conditions for receiving the promise
- The exact source of the promise
- Whether the promise is conditional or unconditional

Promises without conditions (where conditions exist in the text) are INCOMPLETE.

### R9: Dispute Engine Rule
For every Dispute, the ontology MUST be able to answer:
1. Who holds each opinion?
2. What is their source?
3. What is their reasoning?
4. Who agrees with each side?
5. Who resolved it (if resolved)?
6. What is the resolution source?

### R10: Learning Engine Rule
When a new book enters the system, the ontology MUST:
1. Extract new concepts
2. Propose new relationships
3. Flag potential disputes
4. NEVER overwrite verified knowledge
5. Queue all proposals for human validation

---

## 5. Validation Rules

### V1: Authenticity Check
Every concept name MUST be verifiable in at least one of:
- Sefaria database
- Academic Torah concordance
- Recognized Torah encyclopedia (Otzar Yisrael, Encyclopedia Talmudit, etc.)

### V2: Source Check
Every entity MUST have at least one source with:
- Book name
- Chapter/verse/page
- Exact text or URL

### V3: Domain Check
Every concept MUST have a domain. If it spans domains, it must be split per R1.

### V4: Dispute Check
If `is_disputed=true`, the entity MUST have at least 2 linked Opinion entities and 1 Dispute entity.

### V5: Cross-Domain Check
If two concepts with the same name exist in different domains, they MUST be linked by RELATED_TO with relationship_type="cross_domain_equivalent".

### V6: Authority Consistency Check
An entity tagged with authority_level="Biblical" MUST have a source from Tanakh.
An entity tagged with authority_level="Talmudic" MUST have a source from Mishnah or Talmud.

### V7: Soul Root Source Check
Every SoulRoot entity MUST have a source_authority in [Zohar, Arizal, Rashash, VilnaGaon].

---

## 6. Aliases System

Concepts in Torah have many alternative names. The ontology MUST track:

### Alias Types
1. **Hebrew variant**: Different Hebrew spelling or vocalization
2. **Aramaic equivalent**: Aramaic term used in Talmud/Zohar
3. **English translation**: Standard English rendering
4. **Commentator's term**: Name used by a specific authority
5. **Domain-specific**: Name used in a specific domain
6. **Euphemism**: Polite alternative (e.g., "Hashem" for YHVH)
7. **Acronym**: Shortened form (e.g., "Rashi" for "Rabbi Shlomo Yitzchaki")

### Alias Rules
- Every entity MUST have at least its Hebrew name and one English name
- Aliases MUST include their source (who uses this name)
- Aliases MUST include their domain (where this name is used)
- The canonical_name is the most widely recognized name in English scholarship

---

## 7. Known Ontological Challenges

### Challenge 1: The Same Word, Different Meanings
Hebrew words like "Kedushah" have radically different meanings in different contexts:
- Torah: separation/consecration
- Halacha: marital prohibition categories
- Kabbalah: divine emanation quality
- Chassidut: spiritual elevation state
- Musar: character trait of holiness

Solution: R1 (Multi-Domain Rule) — create separate instances.

### Challenge 2: Nested Commentaries
A verse has Rashi's commentary. On Rashi, there is Maharsha. On Maharsha, there is a modern explanation. The chain of commentary is theoretically infinite.

Solution: Model COMMENTARY_ON as recursive. Any Verse/Concept can be commented on by any Book/Person.

### Challenge 3: The Dispute That Is Not a Dispute
Beit Hillel and Beit Shammai often disagree, but sometimes they say the same thing in different words. The ontology must distinguish:
- Actual disagreement (different conclusions)
- Semantic disagreement (same conclusion, different reasoning)
- Apparent disagreement (different cases, not actually in conflict)

Solution: Dispute entity includes a `dispute_type` field: "substantive" | "semantic" | "apparent".

### Challenge 4: The Anonymous Authority
Some sources in the Talmud are attributed to "Tanna Kamma" (first opinion) or "Stam Mishnah" (anonymous Mishnah). The ontology must represent authority without a named Person.

Solution: Allow pseudo-persons like "Tanna Kamma", "Stam Mishnah", "Stam Gemara" with authority_level but no personal details.

### Challenge 5: The Evolving Concept
The concept of "Mashiach" evolved from a biblical military leader to a rabbinic eschatological figure to a kabbalistic divine unifier to a chassidic spiritual force. The ontology must represent this evolution without flattening it.

Solution: Create Event entities for conceptual evolution and link concepts to their historical context.

### Challenge 6: The Non-Existent Concept
Some concepts in Torah are defined by negation or absence (e.g., "Tohu" = formless void, defined by what it lacks). The ontology must represent negative concepts.

Solution: Allow concepts with `definition_type` = "positive" | "negative" | "relational".

---

## 8. Ontology Metrics

### Coverage Metrics
- **Concept coverage**: % of real Torah concepts that can be modeled
- **Relationship coverage**: % of real relationships that can be modeled
- **Dispute coverage**: % of known disputes that can be represented
- **Source coverage**: % of concepts that have required minimum sources

### Quality Metrics
- **Ambiguity count**: Concepts with unclear domain assignment
- **Failure count**: Concepts that cannot be modeled under current rules
- **Overlap count**: Concepts that appear in multiple domains with unclear boundaries
- **Dispute representation quality**: How well disputes capture all opinions

### Validation Metrics
- **Source completeness**: % of entities with full source citations
- **Authority consistency**: % of entities with correct authority_level
- **Cross-domain link quality**: % of cross-domain equivalents with valid links
