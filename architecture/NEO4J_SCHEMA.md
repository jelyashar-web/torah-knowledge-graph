# Torah Knowledge Graph — Neo4j Schema Design

## 1. Design Philosophy

The schema models Jewish textual and mystical knowledge as a typed, directed property graph. Every node represents a real-world entity; every relationship represents a documented connection with provenance. The schema supports:

- **Structural traversal**: Navigate Tanakh → Book → Chapter → Verse → Commentary.
- **Conceptual linking**: Connect verses to concepts, sefirot, divine names, and tikkunim.
- **Linguistic patterns**: Store gematria, notarikon, and atbash correspondences as first-class edges.
- **Provenance tracking**: Every edge carries `source`, `confidence`, and `validated_by` properties.

---

## 2. Node Labels

All nodes share a set of **common properties**:

| Property | Type | Description |
|----------|------|-------------|
| `id` | `STRING` | UUID v4, globally unique |
| `name` | `STRING` | Primary display name (Hebrew or English) |
| `name_hebrew` | `STRING` | Hebrew name where applicable |
| `description` | `STRING` | Short description (max 2000 chars) |
| `created_at` | `DATETIME` | Node creation timestamp |
| `updated_at` | `DATETIME` | Last update timestamp |
| `status` | `STRING` | `public` \| `pending` \| `rejected` |
| `created_by` | `STRING` | User ID of creator |
| `source_citation` | `STRING` | Primary textual source |

---

### 2.1 Verse
Represents a single verse from the Tanakh.

| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| `id` | `STRING` | Unique | UUID |
| `book` | `STRING` | Exists | Book name (e.g., `Genesis`) |
| `chapter_number` | `INTEGER` | Exists | Chapter index |
| `verse_number` | `INTEGER` | Exists | Verse index |
| `hebrew_text` | `STRING` | Exists | Original Hebrew text |
| `english_text` | `STRING` | | English translation |
| `tiberian_text` | `STRING` | | Tiberian vocalization |
| `sefer_temani_text` | `STRING` | | Yemenite variant |
| `gematria_value` | `INTEGER` | | Numerical value of Hebrew text |
| `word_count` | `INTEGER` | | Number of Hebrew words |
| `letter_count` | `INTEGER` | | Number of Hebrew letters |

**Composite Constraint:** `(book, chapter_number, verse_number)` must be unique per textual tradition.

---

### 2.2 Chapter
Represents a chapter within a book.

| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| `id` | `STRING` | Unique | UUID |
| `book` | `STRING` | Exists | Parent book |
| `chapter_number` | `INTEGER` | Exists | Chapter index |
| `title_hebrew` | `STRING` | | Hebrew chapter title if any |
| `title_english` | `STRING` | | English chapter title |
| `verse_count` | `INTEGER` | | Number of verses |

**Composite Constraint:** `(book, chapter_number)` must be unique.

---

### 2.3 Book
Represents a book of the Tanakh or other canonical text.

| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| `id` | `STRING` | Unique | UUID |
| `canonical_name` | `STRING` | Unique, Exists | Standardized name |
| `hebrew_name` | `STRING` | Exists | Hebrew name |
| `english_name` | `STRING` | Exists | English name |
| `section` | `STRING` | Exists | `Torah` \| `Neviim` \| `Ketuvim` \| `Talmud` \| `Zohar` |
| `order_index` | `INTEGER` | | Canonical ordering |
| `chapter_count` | `INTEGER` | | Number of chapters |
| `author_tradition` | `STRING` | | Traditional attribution |

---

### 2.4 Person
Represents a named individual in Jewish texts (biblical, talmudic, or historical).

| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| `id` | `STRING` | Unique | UUID |
| `name` | `STRING` | Unique, Exists | Primary name |
| `name_hebrew` | `STRING` | Exists | Hebrew name |
| `aliases` | `STRING[]` | | Alternative names |
| `birth_year` | `INTEGER` | | Estimated or known birth year (BCE negative) |
| `death_year` | `INTEGER` | | Estimated or known death year |
| `gender` | `STRING` | | `male` \| `female` |
| `nationality` | `STRING` | | e.g., `Israelite`, `Babylonian` |
| `tribe` | `STRING` | | Tribal affiliation if known |
| `role` | `STRING` | | `prophet`, `king`, `judge`, `sage`, `scribe` |
| `biography` | `STRING` | | Extended biographical note |

---

### 2.5 Tzaddik
Represents a righteous figure in the Jewish mystical tradition (especially Chassidic).

| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| `id` | `STRING` | Unique | UUID |
| `name` | `STRING` | Unique, Exists | Common name |
| `name_hebrew` | `STRING` | Exists | Hebrew name |
| `birth_year` | `INTEGER` | | Hebrew or Gregorian year |
| `death_year` | `INTEGER` | | Yahrzeit or death year |
| `death_date_hebrew` | `STRING` | | Hebrew date of passing |
| `dynasty` | `STRING` | | e.g., `Breslov`, `Chabad`, `Ger` |
| `teacher_id` | `STRING` | | Neo4j ID of primary teacher |
| `burial_place` | `STRING` | | Burial site |
| `teachings_summary` | `STRING` | | Summary of key teachings |

---

### 2.6 Mitzvah
Represents a commandment or religious obligation.

| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| `id` | `STRING` | Unique | UUID |
| `name` | `STRING` | Unique, Exists | Name of the mitzvah |
| `name_hebrew` | `STRING` | Exists | Hebrew name |
| `category` | `STRING` | Exists | `positive` \| `negative` |
| `source_verse_id` | `STRING` | | Neo4j ID of primary source verse |
| `rambam_number` | `INTEGER` | | Maimonides enumeration if applicable |
| `sefer_hachinukh_number` | `INTEGER` | | Sefer HaChinukh enumeration |
| `applicability` | `STRING` | | `all_time` \| `temple_era` \| `land_of_israel` |
| `details` | `STRING` | | Detailed halachic description |

---

### 2.7 Concept
Represents an abstract idea, theme, or principle.

| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| `id` | `STRING` | Unique | UUID |
| `name` | `STRING` | Unique, Exists | Concept name |
| `name_hebrew` | `STRING` | Exists | Hebrew term |
| `category` | `STRING` | | `ethical`, `theological`, `mystical`, `legal`, `narrative` |
| `definition` | `STRING` | | Clear definition |
| `related_concepts` | `STRING[]` | | Human-curated related concept names |

---

### 2.8 Sefirah
Represents one of the ten sefirot in Kabbalistic cosmology.

| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| `id` | `STRING` | Unique | UUID |
| `name` | `STRING` | Unique, Exists | Sefirah name (e.g., `Keter`, `Chokhmah`) |
| `name_hebrew` | `STRING` | Exists | Hebrew name |
| `number` | `INTEGER` | Unique, Exists | 1–10 |
| `attribute` | `STRING` | Exists | E.g., `Crown`, `Wisdom`, `Understanding` |
| `world` | `STRING` | | `Atzilut`, `Beriah`, `Yetzirah`, `Asiyah` |
| `partzuf` | `STRING` | | Associated Partzuf if any |
| `divine_name_association` | `STRING` | | Linked Divine Name |
| `color` | `STRING` | | Traditional color for visualization |
| `body_correspondence` | `STRING` | | Body part correspondence |
| `description` | `STRING` | | Extended description |

---

### 2.9 DivineName
Represents a Divine Name or Name of God.

| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| `id` | `STRING` | Unique | UUID |
| `name` | `STRING` | Unique, Exists | The name itself (e.g., `YHVH`, `Elohim`) |
| `name_hebrew` | `STRING` | Exists | Hebrew letters |
| `pronunciation_note` | `STRING` | | Pronunciation guidance |
| `meaning` | `STRING` | | Theological meaning |
| `gematria_value` | `INTEGER` | | Numerical value |
| `letter_count` | `INTEGER` | | Number of letters |
| `associated_sefirah` | `STRING` | | Primary sefirah association |
| `usage_context` | `STRING` | | `prayer`, `Torah`, `meditation`, `creation` |
| `kavanot` | `STRING` | | Meditation intentions |

---

### 2.10 Prayer
Represents a liturgical prayer or blessing.

| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| `id` | `STRING` | Unique | UUID |
| `name` | `STRING` | Unique, Exists | Prayer name |
| `name_hebrew` | `STRING` | Exists | Hebrew name |
| `text_hebrew` | `STRING` | | Full Hebrew text |
| `text_english` | `STRING` | | English translation |
| `text_transliteration` | `STRING` | | Transliterated text |
| `category` | `STRING` | Exists | `shacharit`, `mincha`, `maariv`, `shabbat`, `holiday`, `personal`, `blessing` |
| `occasion` | `STRING` | | When it is recited |
| `source_reference` | `STRING` | | Talmudic or Zohar source |
| `author_attribution` | `STRING` | | If attributed to a specific sage |
| `segulot_notes` | `STRING` | | Associated benefits |

---

### 2.11 Promise
Represents a Divine or prophetic promise.

| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| `id` | `STRING` | Unique | UUID |
| `name` | `STRING` | Unique, Exists | Promise title |
| `promise_text` | `STRING` | Exists | The promise as quoted |
| `source_verse_id` | `STRING` | | Source verse |
| `speaker` | `STRING` | | Who made the promise (e.g., `God`, `Moses`) |
| `recipient` | `STRING` | | To whom the promise was made |
| `conditions` | `STRING` | | Conditions for fulfillment |
| `fulfillment_status` | `STRING` | | `fulfilled`, `partial`, `future`, `ongoing` |
| `fulfillment_verse_id` | `STRING` | | Verse documenting fulfillment |
| `category` | `STRING` | | `land`, `children`, `protection`, `messianic` |

---

### 2.12 Segulah
Represents a protective or beneficial practice/remedy.

| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| `id` | `STRING` | Unique | UUID |
| `name` | `STRING` | Unique, Exists | Segulah name |
| `name_hebrew` | `STRING` | Exists | Hebrew name |
| `practice_description` | `STRING` | Exists | What to do |
| `intended_benefit` | `STRING` | Exists | What it protects or brings |
| `source_reference` | `STRING` | | Textual source |
| `authority` | `STRING` | | Tzaddik or tradition backing it |
| `materials_needed` | `STRING[]` | | Physical items required |
| `time_requirement` | `STRING` | | When to perform |
| `location_requirement` | `STRING` | | Where to perform |
| `caveats` | `STRING` | | Warnings or prerequisites |

---

### 2.13 Tikkun
Represents a rectification, repair, or spiritual correction.

| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| `id` | `STRING` | Unique | UUID |
| `name` | `STRING` | Unique, Exists | Tikkun name |
| `name_hebrew` | `STRING` | Exists | Hebrew name |
| `description` | `STRING` | Exists | What is being repaired and how |
| `source_verse_id` | `STRING` | | Source verse |
| `associated_mitzvah_id` | `STRING` | | Mitzvah that performs this tikkun |
| `associated_sefirah` | `STRING` | | Sefirah being repaired |
| `level` | `STRING` | | `personal`, `communal`, `cosmic` |
| `practice` | `STRING` | | How to accomplish |

---

### 2.14 Place
Represents a geographic location mentioned in Jewish texts.

| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| `id` | `STRING` | Unique | UUID |
| `name` | `STRING` | Unique, Exists | Common name |
| `name_hebrew` | `STRING` | Exists | Hebrew name |
| `aliases` | `STRING[]` | | Alternative names |
| `modern_name` | `STRING` | | Contemporary name if different |
| `latitude` | `FLOAT` | | Geographic latitude |
| `longitude` | `FLOAT` | | Geographic longitude |
| `region` | `STRING` | | `Canaan`, `Babylonia`, `Egypt`, `Europe` |
| `significance` | `STRING` | | Why it matters |
| `is_holy_site` | `BOOLEAN` | | Whether it is a pilgrimage site |

---

### 2.15 HistoricalEvent
Represents a dated historical or biblical event.

| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| `id` | `STRING` | Unique | UUID |
| `name` | `STRING` | Unique, Exists | Event name |
| `name_hebrew` | `STRING` | Exists | Hebrew name |
| `hebrew_date` | `STRING` | | Date in Hebrew calendar |
| `gregorian_date` | `DATE` | | Estimated Gregorian date |
| `year_bce` | `INTEGER` | | Year BCE if known |
| `year_hebrew` | `INTEGER` | | Hebrew year |
| `event_type` | `STRING` | | `miracle`, `war`, `covenant`, `exile`, `redemption` |
| `primary_verse_id` | `STRING` | | Key verse describing it |
| `description` | `STRING` | | Narrative summary |
| `participants` | `STRING[]` | | Key people involved |

---

### 2.16 HalachicTopic
Represents a halachic (legal) topic or subject.

| Property | Type | Constraints | Description |
|----------|------|-------------|-------------|
| `id` | `STRING` | Unique | UUID |
| `name` | `STRING` | Unique, Exists | Topic name |
| `name_hebrew` | `STRING` | Exists | Hebrew name |
| `category` | `STRING` | | `Shabbat`, `Kashrut`, `Family Purity`, `Prayer`, `Business` |
| `shulchan_aruch_section` | `STRING` | | SA reference |
| `summary` | `STRING` | | Brief overview |
| `key_sources` | `STRING[]` | | Primary Talmudic or halachic sources |

---

## 3. Relationship Types

All relationships share a set of **common properties**:

| Property | Type | Description |
|----------|------|-------------|
| `id` | `STRING` | UUID for the relationship instance |
| `source_citation` | `STRING` | Textual source justifying the relationship |
| `confidence` | `FLOAT` | 0.0–1.0 confidence score (1.0 = explicitly stated) |
| `validated_by` | `STRING[]` | User IDs of validators who approved |
| `created_at` | `DATETIME` | Relationship creation timestamp |
| `created_by` | `STRING` | User ID of creator |
| `status` | `STRING` | `public` \| `pending` \| `rejected` |
| `notes` | `STRING` | Human-readable explanation |

---

### 3.1 COMMENTARY_ON
A text (or commentary node, often a `Concept` or additional `Book`) comments on a source verse or text.

| Property | Type | Description |
|----------|------|-------------|
| `commentary_type` | `STRING` | `Rashi`, `Ramban`, `Ibn Ezra`, `Midrash`, `Zohar`, `Chassidic` |
| `commentary_text` | `STRING` | The commentary content |
| `language` | `STRING` | `hebrew`, `aramaic`, `english`, `yiddish` |

**Allowed:** Any node → `Verse`, `Chapter`, `Book`, `Concept`

---

### 3.2 QUOTES
A node directly quotes another node (e.g., a later text quotes a verse).

| Property | Type | Description |
|----------|------|-------------|
| `quote_context` | `STRING` | How the quote is used |
| `partial` | `BOOLEAN` | Whether it is a partial quote |

**Allowed:** `Book`, `Concept`, `Prayer`, `Tzaddik` → `Verse`, `Book`, `Concept`

---

### 3.3 MENTIONS
A node mentions another node in passing.

| Property | Type | Description |
|----------|------|-------------|
| `mention_context` | `STRING` | Context of the mention |

**Allowed:** Any node → Any node

---

### 3.4 RELATED_TO
General semantic or thematic relationship.

| Property | Type | Description |
|----------|------|-------------|
| `relation_type` | `STRING` | `thematic`, `historical`, `linguistic`, `numerical` |
| `strength` | `FLOAT` | Semantic strength 0.0–1.0 |

**Allowed:** Any node → Any node

---

### 3.5 ALLUDES_TO
A node alludes to another node (e.g., a verse alludes to a future event).

| Property | Type | Description |
|----------|------|-------------|
| `allusion_type` | `STRING` | `prophecy`, `remez`, `drash`, `sod` |

**Allowed:** `Verse`, `Concept`, `Prayer` → `Verse`, `Person`, `HistoricalEvent`, `Concept`, `Promise`

---

### 3.6 GEMATRIA_MATCH
Two nodes share a gematria (numerical) equivalence.

| Property | Type | Description |
|----------|------|-------------|
| `gematria_value` | `INTEGER` | The shared numerical value |
| `match_type` | `STRING` | `exact`, `reduced`, `squared`, `colel` |

**Allowed:** Any node with `gematria_value` → Any node with `gematria_value`

---

### 3.7 NOTARIKON
An acrostic or abbreviation relationship (notarikon).

| Property | Type | Description |
|----------|------|-------------|
| `acrostic_type` | `STRING` | `initial`, `final`, `scattered` |
| `expanded_form` | `STRING` | The expanded meaning |

**Allowed:** `Verse`, `DivineName`, `Concept` → `Concept`, `DivineName`, `Sefirah`

---

### 3.8 ATBASH
An Atbash cipher transformation relationship.

| Property | Type | Description |
|----------|------|-------------|
| `cipher_type` | `STRING` | `atbash`, `albam`, `aikbek` |
| `original_word` | `STRING` | The original Hebrew word |
| `transformed_word` | `STRING` | The cipher result |

**Allowed:** `Verse`, `DivineName`, `Concept` → `Verse`, `DivineName`, `Concept`

---

### 3.9 HALACHA_SOURCE
A verse or text is the source for a halachic ruling or topic.

| Property | Type | Description |
|----------|------|-------------|
| `halachic_authority` | `STRING` | `Rambam`, `Shulchan Aruch`, `Talmud`, `Mishnah` |
| `ruling_summary` | `STRING` | Brief summary of the derived ruling |

**Allowed:** `Verse`, `Book` → `HalachicTopic`, `Mitzvah`

---

### 3.10 KABBALAH_SOURCE
A verse or text is the source for a kabbalistic concept or practice.

| Property | Type | Description |
|----------|------|-------------|
| `kabbalistic_authority` | `STRING` | `Zohar`, `Arizal`, `Baal Shem Tov`, `Ramak` |
| `teaching_summary` | `STRING` | Summary of the mystical teaching |

**Allowed:** `Verse`, `Book`, `Prayer` → `Sefirah`, `DivineName`, `Concept`, `Tikkun`

---

### 3.11 PART_OF
Hierarchical composition.

| Property | Type | Description |
|----------|------|-------------|
| `order_index` | `INTEGER` | Position within parent |

**Allowed:** `Verse` → `Chapter`, `Chapter` → `Book`, `Book` → `Concept` (for anthology), `Sefirah` → `Sefirah` (for Partzufim)

---

### 3.12 CAUSES
A node causes or leads to another node (e.g., a sin causes an exile).

| Property | Type | Description |
|----------|------|-------------|
| `causation_type` | `STRING` | `direct`, `spiritual`, `historical` |

**Allowed:** `Verse`, `Concept`, `Mitzvah`, `HistoricalEvent` → `HistoricalEvent`, `Concept`, `Tikkun`

---

### 3.13 REPAIRS
A node repairs or rectifies the damage caused by another node.

| Property | Type | Description |
|----------|------|-------------|
| `repair_mechanism` | `STRING` | How the repair works |

**Allowed:** `Mitzvah`, `Prayer`, `Tzaddik`, `Concept` → `Concept`, `Tikkun`, `HistoricalEvent`

---

### 3.14 PROMISES
A person (or God via a verse) promises something.

| Property | Type | Description |
|----------|------|-------------|
| `promise_type` | `STRING` | `conditional`, `unconditional` |

**Allowed:** `Person`, `Verse` → `Promise`, `Person`, `Place`

---

### 3.15 SEGULAH_FOR
A segulah is recommended for a specific purpose.

| Property | Type | Description |
|----------|------|-------------|
| `effectiveness_note` | `STRING` | Tradition about its efficacy |

**Allowed:** `Segulah` → `Concept`, `Mitzvah`, `Prayer`, `Tzaddik`

---

### 3.16 TIKKUN_FOR
A tikkun repairs a specific problem or concept.

| Property | Type | Description |
|----------|------|-------------|
| `repair_depth` | `STRING` | `surface`, `deep`, `soul_level` |

**Allowed:** `Tikkun` → `Concept`, `Mitzvah`, `HistoricalEvent`, `Sefirah`

---

### 3.17 OPPOSITE_OF
Two nodes represent opposing or complementary ideas.

| Property | Type | Description |
|----------|------|-------------|
| `complementarity` | `BOOLEAN` | Whether they are complementary rather than purely opposed |

**Allowed:** Any node → Any node of the same label

---

### 3.18 DERIVED_FROM
A concept, mitzvah, or teaching is derived from another node.

| Property | Type | Description |
|----------|------|-------------|
| `derivation_method` | `STRING` | `kal vachomer`, `gezerah shavah`, `binyan av`, `mystical` |

**Allowed:** `Concept`, `Mitzvah`, `HalachicTopic`, `Prayer` → `Verse`, `Book`, `Concept`, `Tzaddik`

---

## 4. Constraints

### 4.1 Uniqueness Constraints
Every node label must enforce uniqueness on its primary identifier:

```cypher
CREATE CONSTRAINT verse_id_unique IF NOT EXISTS
FOR (v:Verse) REQUIRE v.id IS UNIQUE;

CREATE CONSTRAINT chapter_id_unique IF NOT EXISTS
FOR (c:Chapter) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT book_canonical_name_unique IF NOT EXISTS
FOR (b:Book) REQUIRE b.canonical_name IS UNIQUE;

CREATE CONSTRAINT person_name_unique IF NOT EXISTS
FOR (p:Person) REQUIRE p.name IS UNIQUE;

CREATE CONSTRAINT tzaddik_name_unique IF NOT EXISTS
FOR (t:Tzaddik) REQUIRE t.name IS UNIQUE;

CREATE CONSTRAINT mitzvah_name_unique IF NOT EXISTS
FOR (m:Mitzvah) REQUIRE m.name IS UNIQUE;

CREATE CONSTRAINT concept_name_unique IF NOT EXISTS
FOR (c:Concept) REQUIRE c.name IS UNIQUE;

CREATE CONSTRAINT sefirah_name_unique IF NOT EXISTS
FOR (s:Sefirah) REQUIRE s.name IS UNIQUE;

CREATE CONSTRAINT sefirah_number_unique IF NOT EXISTS
FOR (s:Sefirah) REQUIRE s.number IS UNIQUE;

CREATE CONSTRAINT divinename_name_unique IF NOT EXISTS
FOR (d:DivineName) REQUIRE d.name IS UNIQUE;

CREATE CONSTRAINT prayer_name_unique IF NOT EXISTS
FOR (pr:Prayer) REQUIRE pr.name IS UNIQUE;

CREATE CONSTRAINT promise_name_unique IF NOT EXISTS
FOR (prom:Promise) REQUIRE prom.name IS UNIQUE;

CREATE CONSTRAINT segulah_name_unique IF NOT EXISTS
FOR (seg:Segulah) REQUIRE seg.name IS UNIQUE;

CREATE CONSTRAINT tikkun_name_unique IF NOT EXISTS
FOR (t:Tikkun) REQUIRE t.name IS UNIQUE;

CREATE CONSTRAINT place_name_unique IF NOT EXISTS
FOR (pl:Place) REQUIRE pl.name IS UNIQUE;

CREATE CONSTRAINT historicalevent_name_unique IF NOT EXISTS
FOR (he:HistoricalEvent) REQUIRE he.name IS UNIQUE;

CREATE CONSTRAINT halachictopic_name_unique IF NOT EXISTS
FOR (ht:HalachicTopic) REQUIRE ht.name IS UNIQUE;
```

### 4.2 Existence Constraints
Critical properties that must always be present:

```cypher
CREATE CONSTRAINT verse_book_exists IF NOT EXISTS
FOR (v:Verse) REQUIRE v.book IS NOT NULL;

CREATE CONSTRAINT verse_chapter_exists IF NOT EXISTS
FOR (v:Verse) REQUIRE v.chapter_number IS NOT NULL;

CREATE CONSTRAINT verse_verse_exists IF NOT EXISTS
FOR (v:Verse) REQUIRE v.verse_number IS NOT NULL;

CREATE CONSTRAINT verse_hebrew_text_exists IF NOT EXISTS
FOR (v:Verse) REQUIRE v.hebrew_text IS NOT NULL;

CREATE CONSTRAINT book_section_exists IF NOT EXISTS
FOR (b:Book) REQUIRE b.section IS NOT NULL;

CREATE CONSTRAINT sefirah_number_exists IF NOT EXISTS
FOR (s:Sefirah) REQUIRE s.number IS NOT NULL;

CREATE CONSTRAINT mitzvah_category_exists IF NOT EXISTS
FOR (m:Mitzvah) REQUIRE m.category IS NOT NULL;

CREATE CONSTRAINT prayer_category_exists IF NOT EXISTS
FOR (pr:Prayer) REQUIRE pr.category IS NOT NULL;
```

### 4.3 Composite Constraints

```cypher
CREATE CONSTRAINT verse_location_unique IF NOT EXISTS
FOR (v:Verse) REQUIRE (v.book, v.chapter_number, v.verse_number) IS UNIQUE;

CREATE CONSTRAINT chapter_location_unique IF NOT EXISTS
FOR (c:Chapter) REQUIRE (c.book, c.chapter_number) IS UNIQUE;
```

## 5. Indexes

### 5.1 Full-Text Indexes
For Hebrew and English text search across nodes:

```cypher
CREATE FULLTEXT INDEX verseTextIndex IF NOT EXISTS
FOR (v:Verse) ON EACH [v.hebrew_text, v.english_text, v.tiberian_text];

CREATE FULLTEXT INDEX bookNameIndex IF NOT EXISTS
FOR (b:Book) ON EACH [b.canonical_name, b.hebrew_name, b.english_name];

CREATE FULLTEXT INDEX personNameIndex IF NOT EXISTS
FOR (p:Person) ON EACH [p.name, p.name_hebrew, p.aliases];

CREATE FULLTEXT INDEX conceptNameIndex IF NOT EXISTS
FOR (c:Concept) ON EACH [c.name, c.name_hebrew, c.definition];

CREATE FULLTEXT INDEX prayerTextIndex IF NOT EXISTS
FOR (pr:Prayer) ON EACH [pr.name, pr.name_hebrew, pr.text_hebrew, pr.text_english];

CREATE FULLTEXT INDEX tzaddikNameIndex IF NOT EXISTS
FOR (t:Tzaddik) ON EACH [t.name, t.name_hebrew];

CREATE FULLTEXT INDEX sefirahNameIndex IF NOT EXISTS
FOR (s:Sefirah) ON EACH [s.name, s.name_hebrew, s.attribute];

CREATE FULLTEXT INDEX divinenameNameIndex IF NOT EXISTS
FOR (d:DivineName) ON EACH [d.name, d.name_hebrew, d.meaning];

CREATE FULLTEXT INDEX promiseTextIndex IF NOT EXISTS
FOR (prom:Promise) ON EACH [prom.name, prom.promise_text];

CREATE FULLTEXT INDEX segulahNameIndex IF NOT EXISTS
FOR (seg:Segulah) ON EACH [seg.name, seg.name_hebrew, seg.practice_description];

CREATE FULLTEXT INDEX tikkunNameIndex IF NOT EXISTS
FOR (t:Tikkun) ON EACH [t.name, t.name_hebrew, t.description];

CREATE FULLTEXT INDEX placeNameIndex IF NOT EXISTS
FOR (pl:Place) ON EACH [pl.name, pl.name_hebrew, pl.aliases];

CREATE FULLTEXT INDEX historicaleventNameIndex IF NOT EXISTS
FOR (he:HistoricalEvent) ON EACH [he.name, he.name_hebrew, he.description];

CREATE FULLTEXT INDEX halachictopicNameIndex IF NOT EXISTS
FOR (ht:HalachicTopic) ON EACH [ht.name, ht.name_hebrew, ht.summary];
```

### 5.2 Range Indexes
For temporal and numeric range queries:

```cypher
CREATE INDEX verse_gematria_range IF NOT EXISTS
FOR (v:Verse) ON (v.gematria_value);

CREATE INDEX person_birth_year_range IF NOT EXISTS
FOR (p:Person) ON (p.birth_year);

CREATE INDEX person_death_year_range IF NOT EXISTS
FOR (p:Person) ON (p.death_year);

CREATE INDEX tzaddik_birth_year_range IF NOT EXISTS
FOR (t:Tzaddik) ON (t.birth_year);

CREATE INDEX tzaddik_death_year_range IF NOT EXISTS
FOR (t:Tzaddik) ON (t.death_year);

CREATE INDEX sefirah_number_range IF NOT EXISTS
FOR (s:Sefirah) ON (s.number);

CREATE INDEX divinename_gematria_range IF NOT EXISTS
FOR (d:DivineName) ON (d.gematria_value);

CREATE INDEX historicalevent_year_bce_range IF NOT EXISTS
FOR (he:HistoricalEvent) ON (he.year_bce);

CREATE INDEX historicalevent_hebrew_year_range IF NOT EXISTS
FOR (he:HistoricalEvent) ON (he.year_hebrew);

CREATE INDEX node_created_at_range IF NOT EXISTS
FOR (n) ON (n.created_at);
```

### 5.3 Text Indexes
For exact string lookups and prefix search:

```cypher
CREATE INDEX book_section_text IF NOT EXISTS
FOR (b:Book) ON (b.section);

CREATE INDEX person_role_text IF NOT EXISTS
FOR (p:Person) ON (p.role);

CREATE INDEX mitzvah_category_text IF NOT EXISTS
FOR (m:Mitzvah) ON (m.category);

CREATE INDEX concept_category_text IF NOT EXISTS
FOR (c:Concept) ON (c.category);

CREATE INDEX prayer_category_text IF NOT EXISTS
FOR (pr:Prayer) ON (pr.category);

CREATE INDEX sefirah_world_text IF NOT EXISTS
FOR (s:Sefirah) ON (s.world);

CREATE INDEX promise_category_text IF NOT EXISTS
FOR (prom:Promise) ON (prom.category);

CREATE INDEX promise_fulfillment_status_text IF NOT EXISTS
FOR (prom:Promise) ON (prom.fulfillment_status);

CREATE INDEX tikkun_level_text IF NOT EXISTS
FOR (t:Tikkun) ON (t.level);

CREATE INDEX node_status_text IF NOT EXISTS
FOR (n) ON (n.status);
```

## 6. Example Cypher Queries

### 6.1 Create a Verse Node

```cypher
CREATE (v:Verse {
  id: 'verse-gen-1-1',
  book: 'Genesis',
  chapter_number: 1,
  verse_number: 1,
  hebrew_text: 'בראשית ברא אלהים את השמים ואת הארץ',
  english_text: 'In the beginning God created the heaven and the earth.',
  gematria_value: 2701,
  word_count: 7,
  letter_count: 28,
  created_at: datetime(),
  updated_at: datetime(),
  status: 'public',
  created_by: 'system',
  source_citation: 'Tanakh'
})
RETURN v;
```

### 6.2 Create a Relationship (Commentary)

```cypher
MATCH (rashi:Concept {name: 'Rashi Commentary'}),
      (v:Verse {book: 'Genesis', chapter_number: 1, verse_number: 1})
CREATE (rashi)-[:COMMENTARY_ON {
  id: 'rel-001',
  commentary_type: 'Rashi',
  commentary_text: 'For the sake of the Torah and Israel, God created the world...',
  language: 'hebrew',
  source_citation: 'Rashi on Genesis 1:1',
  confidence: 1.0,
  validated_by: ['validator-001'],
  created_at: datetime(),
  created_by: 'contributor-001',
  status: 'public',
  notes: 'Classic medieval commentary'
}]->(v)
RETURN rashi, v;
```

### 6.3 Graph Traversal: All Verses in a Book

```cypher
MATCH (b:Book {canonical_name: 'Genesis'})<-[:PART_OF]-(c:Chapter)<-[:PART_OF]-(v:Verse)
RETURN b, c, v
ORDER BY c.chapter_number, v.verse_number;
```

### 6.4 Graph Traversal: Sefirot Tree with Relationships

```cypher
MATCH (s:Sefirah)
OPTIONAL MATCH (s)-[r:PART_OF|RELATED_TO|OPPOSITE_OF]-(t:Sefirah)
RETURN s, collect({relationship: type(r), target: t}) as connections
ORDER BY s.number;
```

### 6.5 Full-Text Search

```cypher
CALL db.index.fulltext.queryNodes('verseTextIndex', 'בראשית') YIELD node, score
RETURN node.book, node.chapter_number, node.verse_number, node.hebrew_text, score
ORDER BY score DESC
LIMIT 20;
```

### 6.6 Find Gematria Matches

```cypher
MATCH (a {gematria_value: 2701}), (b {gematria_value: 2701})
WHERE a.id <> b.id
CREATE (a)-[:GEMATRIA_MATCH {
  id: 'rel-gem-' + a.id + '-' + b.id,
  gematria_value: 2701,
  match_type: 'exact',
  source_citation: 'Numerical equivalence',
  confidence: 1.0,
  created_at: datetime(),
  status: 'public'
}]->(b)
RETURN a.name, b.name;
```

### 6.7 Find All Promises and Their Fulfillment Status

```cypher
MATCH (p:Promise)
OPTIONAL MATCH (p)<-[:PROMISES]-(speaker)
OPTIONAL MATCH (p)-[:PART_OF|ALLUDES_TO]->(fulfillment_verse:Verse)
RETURN p.name, p.promise_text, p.fulfillment_status, speaker.name AS speaker,
       collect(fulfillment_verse.hebrew_text) AS fulfillment_texts
ORDER BY p.created_at DESC;
```

### 6.8 Find Tikkunim for a Given Concept

```cypher
MATCH (c:Concept {name: 'Anger'})
OPTIONAL MATCH (t:Tikkun)-[:TIKKUN_FOR]->(c)
OPTIONAL MATCH (t)-[:DERIVED_FROM]->(source:Verse)
RETURN c.name, c.definition,
       collect({tikkun: t.name, practice: t.practice, source: source.hebrew_text}) AS tikkunim;
```

### 6.9 Neighborhood Query for Visualization

```cypher
MATCH (center {id: $node_id})
OPTIONAL MATCH (center)-[r1]-(n1)
OPTIONAL MATCH (n1)-[r2]-(n2)
WHERE n2 <> center
RETURN center, collect(DISTINCT {node: n1, rel: r1}) AS first_hop,
       collect(DISTINCT {node: n2, rel: r2}) AS second_hop;
```

### 6.10 Path Finding Between Two Nodes

```cypher
MATCH path = shortestPath(
  (start {id: $start_id})-[:COMMENTARY_ON|QUOTES|MENTIONS|RELATED_TO|ALLUDES_TO|PART_OF|CAUSES|REPAIRS|PROMISES|DERIVED_FROM*..6]-(end {id: $end_id})
)
RETURN [node IN nodes(path) | {id: node.id, name: node.name, label: labels(node)[0]}] AS node_path,
       [rel IN relationships(path) | {type: type(rel), source: rel.source_citation}] AS rel_path,
       length(path) AS hops;
```

## 7. Graph Layer Views

The Torah Knowledge Graph supports **layered views** — filtered subgraphs that expose specific dimensions of the knowledge model. Each view is a logical perspective, not a separate physical graph.

### 7.1 Promises Layer
All `Promise` nodes and their speakers, recipients, conditions, and fulfillment verses.

```cypher
// Promises Layer Query
MATCH (p:Promise)
OPTIONAL MATCH (p)<-[r1:PROMISES]-(speaker)
OPTIONAL MATCH (p)-[r2:PART_OF|ALLUDES_TO]->(verse:Verse)
OPTIONAL MATCH (p)-[r3:MENTIONS|RELATED_TO]->(recipient)
WHERE p.status = 'public'
RETURN p, collect(DISTINCT speaker) AS speakers,
       collect(DISTINCT verse) AS verses,
       collect(DISTINCT recipient) AS recipients;
```

**Use case**: Users exploring Divine promises throughout Tanakh, their conditions, and fulfillment timelines.

### 7.2 Segulot Layer
All `Segulah` nodes and what they are for, their sources, and required materials.

```cypher
// Segulot Layer Query
MATCH (s:Segulah)
OPTIONAL MATCH (s)-[r:SEGULAH_FOR]->(target)
OPTIONAL MATCH (s)-[r2:DERIVED_FROM|KABBALAH_SOURCE]->(source)
WHERE s.status = 'public'
RETURN s, collect(DISTINCT target) AS targets,
       collect(DISTINCT source) AS sources;
```

**Use case**: Users looking for protective practices and their traditional sources.

### 7.3 Tikkun Layer
All `Tikkun` nodes, what they repair, associated mitzvot, and source texts.

```cypher
// Tikkun Layer Query
MATCH (t:Tikkun)
OPTIONAL MATCH (t)-[r:TIKKUN_FOR]->(repair_target)
OPTIONAL MATCH (t)-[r2:DERIVED_FROM]->(source)
OPTIONAL MATCH (m:Mitzvah)-[r3:REPAIRS]->(repair_target)
WHERE t.status = 'public'
RETURN t, collect(DISTINCT repair_target) AS targets,
       collect(DISTINCT source) AS sources,
       collect(DISTINCT m) AS related_mitzvot;
```

**Use case**: Users studying spiritual rectification pathways in Kabbalistic and Chassidic literature.

### 7.4 Middot Layer (Ethical Qualities)
`Concept` nodes with `category = 'ethical'` connected to verses, people, and practices.

```cypher
// Middot Layer Query
MATCH (c:Concept {category: 'ethical'})
OPTIONAL MATCH (c)-[r:MENTIONS|RELATED_TO|ALLUDES_TO|DERIVED_FROM]-(connected)
WHERE c.status = 'public'
RETURN c, collect(DISTINCT connected) AS connected_nodes;
```

**Use case**: Users studying character development and ethical teachings.

### 7.5 Divine Names Layer
All `DivineName` nodes, their sefirot associations, gematria links, and verses where they appear.

```cypher
// Divine Names Layer Query
MATCH (d:DivineName)
OPTIONAL MATCH (d)-[r:RELATED_TO|GEMATRIA_MATCH]->(linked)
OPTIONAL MATCH (d)<-[r2:MENTIONS]-(verse:Verse)
OPTIONAL MATCH (d)-[r3:RELATED_TO]->(s:Sefirah)
WHERE d.status = 'public'
RETURN d, collect(DISTINCT linked) AS linked_names,
       collect(DISTINCT verse) AS mentioning_verses,
       collect(DISTINCT s) AS sefirot;
```

**Use case**: Users exploring the names of God, their meanings, numerical values, and mystical associations.

### 7.6 Sefirot Layer
All `Sefirah` nodes and their interconnections (Partzufim, worlds, opposites).

```cypher
// Sefirot Layer Query
MATCH (s:Sefirah)
OPTIONAL MATCH (s)-[r:PART_OF|RELATED_TO|OPPOSITE_OF|CAUSES|REPAIRS]->(t:Sefirah)
OPTIONAL MATCH (s)-[r2:RELATED_TO]->(d:DivineName)
OPTIONAL MATCH (s)<-[r3:KABBALAH_SOURCE]-(source)
WHERE s.status = 'public'
RETURN s, collect(DISTINCT {target: t, rel: r}) AS sefirot_connections,
       collect(DISTINCT d) AS divine_names,
       collect(DISTINCT source) AS sources;
```

**Use case**: Users navigating the Tree of Life, exploring emanations, and their correspondences.

### 7.7 Soul Root Layer (Shoresh Neshama)
`Tzaddik` nodes connected to their teachers, dynasties, teachings, and associated concepts.

```cypher
// Soul Root Layer Query
MATCH (t:Tzaddik)
OPTIONAL MATCH (t)-[r:MENTIONS|RELATED_TO|DERIVED_FROM]->(teaching)
OPTIONAL MATCH (t)<-[r2:MENTIONS|RELATED_TO]-(biographer)
OPTIONAL MATCH (teacher:Tzaddik)-[r3:MENTIONS|RELATED_TO]->(t)
WHERE t.status = 'public'
RETURN t, collect(DISTINCT teaching) AS teachings,
       collect(DISTINCT biographer) AS mentioned_by,
       collect(DISTINCT teacher) AS teachers;
```

**Use case**: Users tracing spiritual lineages, teacher-student chains, and dynasty histories.

## 8. Schema Maintenance

### 8.1 Running Schema Setup
All constraint and index creation should be run idempotently at application startup via a migration script:

```python
# backend/neo4j_schema.py
from neo4j import AsyncGraphDatabase

SCHEMA_CYPHER = """
// === CONSTRAINTS ===
CREATE CONSTRAINT verse_id_unique IF NOT EXISTS FOR (v:Verse) REQUIRE v.id IS UNIQUE;
CREATE CONSTRAINT chapter_id_unique IF NOT EXISTS FOR (c:Chapter) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT book_canonical_name_unique IF NOT EXISTS FOR (b:Book) REQUIRE b.canonical_name IS UNIQUE;
// ... (all constraints from section 4)

// === INDEXES ===
CREATE FULLTEXT INDEX verseTextIndex IF NOT EXISTS FOR (v:Verse) ON EACH [v.hebrew_text, v.english_text];
// ... (all indexes from section 5)
"""

async def init_schema(driver):
    async with driver.session() as session:
        await session.run(SCHEMA_CYPHER)
```

### 8.2 Schema Versioning
Store a `SchemaVersion` node in Neo4j to track which migration has been applied:

```cypher
MERGE (sv:SchemaVersion {version: '1.0.0'})
ON CREATE SET sv.applied_at = datetime(), sv.description = 'Initial schema with 16 node labels and 18 relationship types'
RETURN sv;
```

### 8.3 Consistency Checks
Periodic validation queries to ensure schema integrity:

```cypher
// Find nodes missing required properties
MATCH (v:Verse)
WHERE v.hebrew_text IS NULL OR v.book IS NULL
RETURN count(v) AS invalid_verse_count;

// Find orphaned relationships (should not happen with app-layer enforcement)
MATCH ()-[r]->()
WHERE r.status IS NULL
RETURN count(r) AS untagged_relationship_count;

// Find duplicate names (indicates data quality issue)
MATCH (n)
WITH n.name AS name, count(*) AS cnt
WHERE cnt > 1 AND name IS NOT NULL
RETURN name, cnt ORDER BY cnt DESC;
```
