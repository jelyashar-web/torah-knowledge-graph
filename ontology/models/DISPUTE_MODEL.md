# Torah Ontology — Dispute Model V1.0
## Chief Torah Ontology Scientist — Research Document

---

## 1. Core Problem

The Torah is not a monolithic system. It is a 3,000-year conversation between authorities who frequently disagree. The ontology must represent multiple opinions simultaneously without:
- Corrupting any single opinion
- Creating a false "synthesis" that no authority actually held
- Privileging one opinion as "default"

This is the hardest problem in the ontology.

---

## 2. Dispute Taxonomy

### Type 1: Substantive Dispute
**Definition:** Authorities reach different conclusions about the same question.
**Example:** Beit Hillel says Chanukah candles increase (1,2,3...8); Beit Shammai says decrease (8,7,6...1). Same question, opposite answers.
**Modeling:** Two Opinion entities with contradictory positions. Dispute entity links them with type="substantive".

### Type 2: Semantic Dispute
**Definition:** Authorities agree on the conclusion but disagree on the reasoning.
**Example:** Rashi and Ramban both say a particular mitzvah applies, but Rashi derives it from one verse and Ramban from another.
**Modeling:** Two Opinion entities with same conclusion but different reasoning fields. Dispute entity links them with type="semantic".

### Type 3: Apparent Dispute
**Definition:** Authorities seem to disagree but are actually addressing different cases or using different definitions.
**Example:** Rambam says angels have no free will; some Kabbalists say angels have limited free will. They may be using "free will" differently.
**Modeling:** Dispute entity with type="apparent". Resolution field explains that the disagreement dissolves upon closer analysis.

### Type 4: Methodological Dispute
**Definition:** Authorities disagree about the METHOD of deriving law, not the law itself.
**Example:** Rambam uses the Talmudic method of codification; Rosh uses a different organizing principle. Both are "correct" within their frameworks.
**Modeling:** Dispute entity with type="methodological". No Opinion entities needed — instead, two Method entities.

### Type 5: Worldview Dispute
**Definition:** Authorities hold fundamentally different metaphysical frameworks that affect many concepts simultaneously.
**Example:** Rambam's Aristotelian rationalism vs. the Zohar's theosophical Kabbalah. These are not disagreements about single concepts but about the NATURE of reality.
**Modeling:** This requires a new entity type: **Worldview** (see Section 6).

### Type 6: Temporal Dispute
**Definition:** An authority's opinion changed over their lifetime, or a later authority reinterpreted an earlier one.
**Example:** Rambam's early vs. late writings on resurrection; Rav Moshe Feinstein's evolving positions on eruvin.
**Modeling:** Opinion entities include `date_of_opinion` and `phase_of_authority` fields. Dispute links opinions from different periods.

### Type 7: Textual Dispute
**Definition:** Authorities disagree about what the text says (variant readings, different manuscripts).
**Example:** Rashi had a different Talmud text than Ramban; some debates depend on which manuscript is used.
**Modeling:** TextVariant entities. Dispute includes `depends_on_textual_variant` flag.

---

## 3. Dispute Engine Architecture

### 3.1 Core Entities

#### Dispute
```
id: UUID
canonical_name: "Dispute about [topic]"
topic: concept_ref
dispute_type: substantive | semantic | apparent | methodological | worldview | temporal | textual
opinions: [opinion_ref]
primary_source: source_ref
era: enum
creation_date: date
resolution_status: unresolved | partially_resolved | resolved | perpetually_disputed
resolution_opinion: opinion_ref (if resolved)
resolution_source: source_ref
resolution_authority: person_ref
is_active: boolean (still debated today?)
affected_concepts: [concept_ref] (worldview disputes affect many concepts)
```

#### Opinion
```
id: UUID
holder: person_ref
topic: concept_ref
position: text
reasoning: text
source: source_ref
date_of_opinion: date
phase_of_authority: early | middle | late (for evolving opinions)
method_used: string (e.g., "kal_vachomer", "gezeirah_shavah", "philosophical")
contradicts: [opinion_ref]
agrees_with: [opinion_ref]
qualified_by: [opinion_ref] ("Rambam holds X, but only in case Y")
is_majority_opinion: boolean
authority_level: biblical | talmudic | rishonic | achronic | modern
confidence: float
```

#### Worldview (NEW — required for Type 5)
```
id: UUID
name: "Rambam's Aristotelian Rationalism" | "Lurianic Kabbalah" | "Chassidic Panentheism"
holder: person_ref | dynasty_ref
foundational_assumptions: [text]
affected_concepts: [concept_ref]
methodology: text
textual_preferences: [book_ref]
opposing_worldviews: [worldview_ref]
is_dominant_in_era: enum
timeline: [event_ref]
```

### 3.2 Dispute Integrity Rules

**DIR1: No Privileging**
The ontology MUST NOT mark any opinion as "correct" or "true." It may mark an opinion as `is_majority_opinion=true` or `is_accepted_by_community=X`, but never `is_true=true`.

**DIR2: Full Representation**
If a dispute has 5 opinions, all 5 MUST be represented. Omitting minority opinions is CORRUPTION.

**DIR3: Source Anchoring**
Every Opinion MUST have a primary source. "Tradition says..." without a named source is INVALID.

**DIR4: Reasoning Preservation**
The reasoning field MUST contain the actual reasoning of the authority, not a summary or reinterpretation. Paraphrase is allowed, but the original reasoning structure must be preserved.

**DIR5: Context Preservation**
An opinion about "Shabbat" in a halachic context is different from an opinion about "Shabbat" in a chassidic discourse. The context MUST be recorded.

**DIR6: Evolution Tracking**
If an authority changed their opinion, BOTH opinions MUST be preserved with dates. The ontology must not flatten them into a single opinion.

**DIR7: Cross-Worldview Neutrality**
When a rationalist worldview and a mystical worldview disagree, the ontology must not use the language of one worldview to describe the other. Example: Do not describe Kabbalah as "irrational" or Rambam as "soulless."

---

## 4. Stress Test: Rambam vs. Ramban

### Dispute: Reasons for Mitzvot
**Rambam's Position (Sefer HaMitzvot, Moreh Nevuchim):**
- Most mitzvot have rational purposes (health, social order, intellectual perfection)
- Some mitzvot are "chukim" (decrees without revealed reason)
- The purpose of mitzvot is to perfect the human intellect and society

**Ramban's Position (Commentary on Torah):**
- Every mitzvah has a hidden spiritual reason
- "Chukim" are not irrational — their reasons are hidden in Kabbalah
- The purpose of mitzvot is to connect the physical world to the divine

**Dispute Modeling:**
```
Dispute:
  name: "Reasons for Mitzvot — Rational vs. Hidden"
  topic: Mitzvah
  dispute_type: worldview
  opinions: [Rambam_opinion, Ramban_opinion]
  affected_concepts: [Mitzvah, Chok, Taamei HaMitzvot, Olam, Neshamah, Kabbalah, Philosophy]
  primary_source: Rambam Moreh Nevuchim III:26-49, Ramban Leviticus 19:2

Opinion (Rambam):
  holder: Rambam
  topic: Mitzvah
  position: "Mitzvot have rational purposes — health, social order, intellectual perfection"
  reasoning: "God gave commandments that perfect the body and soul. Chukim are decrees without revealed reason, but they too have reasons in God's wisdom."
  source: Moreh Nevuchim III:26-49
  method_used: philosophical
  worldview: Rambam_Aristotelian_Rationalism

Opinion (Ramban):
  holder: Ramban
  topic: Mitzvah
  position: "Every mitzvah has a hidden spiritual reason connected to the structure of creation"
  reasoning: "The Torah is all divine names. Each mitzvah repairs a specific aspect of the cosmic order. What appears as 'no reason' is only because the reason is hidden in Kabbalah."
  source: Ramban Leviticus 19:2, Deuteronomy 22:6
  method_used: kabbalistic
  worldview: Ramban_Theosophical_Kabbalah
```

**Analysis:** This is a WORLDVIEW DISPUTE (Type 5). It affects not just Mitzvah but also Chok, Taamei HaMitzvot, Olam (the nature of the physical world), and Neshamah (the nature of the soul). The ontology correctly models this by linking the Dispute to 7 affected concepts and assigning each Opinion to a Worldview.

---

## 5. Stress Test: Ramak vs. Ari (Cordovero vs. Luria)

### Dispute: Nature of the Sefirot
**Ramak's Position (Pardes Rimmonim):**
- Sefirot are vessels (kelim) that contain divine light (ohr)
- The vessels are created entities, distinct from God
- The relationship between vessels and light is one of container/contained

**Ari's Position (Etz Chaim):**
- Sefirot are BOTH vessels and light simultaneously
- The vessels are made of divine light that has "thickened" or "coarsened"
- The distinction between vessel and light is relative, not absolute
- Tzimtzum (contraction) creates the illusion of separation

**Dispute Modeling:**
```
Dispute:
  name: "Nature of the Sefirot — Vessels vs. Light"
  topic: Sefirah
  dispute_type: substantive
  opinions: [Ramak_opinion, Ari_opinion]
  affected_concepts: [Sefirah, Keli, Ohr, Tzimtzum, Ein Sof, Atzilut, Tikun]
  primary_source: Ramak Pardes Rimmonim Gate 3, Ari Etz Chaim Shaar 1
  era: Achronic
  is_active: true (disputed in contemporary Kabbalah)

Opinion (Ramak):
  holder: Ramak (Rabbi Moshe Cordovero)
  topic: Sefirah
  position: "Sefirot are vessels created to contain divine light"
  reasoning: "God created vessels to receive His light. The vessels are finite, the light is infinite. The vessels can break if too much light enters."
  source: Pardes Rimmonim, Shaar HaSefirot
  method_used: kabbalistic_theosophy
  worldview: Cordoverian_Kabbalah

Opinion (Ari):
  holder: Ari (Rabbi Isaac Luria)
  topic: Sefirah
  position: "Sefirot are coarsened divine light — vessels and light are of the same essence"
  reasoning: "God's light contracts (tzimtzum) and thickens to form vessels. The vessels are not created ex nihilo but are a transformation of divine light."
  source: Etz Chaim, Shaar Drushey HaIggulim VeHaYosher
  method_used: lurianic_kabbalah
  worldview: Lurianic_Kabbalah
```

**Analysis:** This dispute created a FUNDAMENTAL SHIFT in Kabbalah. Most later Kabbalah follows the Ari, but the Ramak's view is still preserved in some texts. The ontology captures that this is an `is_active=true` dispute — it is still discussed in contemporary Kabbalah.

---

## 6. Stress Test: Beit Hillel vs. Beit Shammai

### Dispute: Chanukah Candles
**Beit Hillel:** Light increases each night (1, 2, 3...8).
**Beit Shammai:** Light decreases each night (8, 7, 6...1).

**Dispute Modeling:**
```
Dispute:
  name: "Order of Chanukah Candle Lighting"
  topic: Chanukah
  dispute_type: substantive
  opinions: [Beit_Hillel_opinion, Beit_Shammai_opinion]
  primary_source: Talmud Shabbat 21b
  era: Tannaitic
  resolution_status: resolved
  resolution_opinion: Beit_Hillel_opinion
  resolution_source: Talmud Shabbat 21b ("The law follows Beit Hillel")
  resolution_authority: Talmudic consensus
  is_active: false (not disputed today — halacha follows Beit Hillel)
```

**Analysis:** This is a RESOLVED dispute. The Talmud explicitly rules like Beit Hillel. However, the ontology MUST preserve Beit Shammai's opinion because:
1. It is still studied
2. Some Chassidic customs follow Beit Shammai on some issues
3. The reasoning of Beit Shammai (decreasing miracles) is valuable

The ontology uses `resolution_status=resolved` and `is_active=false`, but preserves both opinions.

---

## 7. Stress Test: Different Explanations of the Same Verse

### Verse: "And God said, 'Let us make man in our image, after our likeness'" (Genesis 1:26)

**Rashi:** God consulted with the angels. This teaches humility — even God (so to speak) consults with lesser beings.

**Ramban:** "Our image" refers to the sefirot — man is created in the image of the divine structure (Tzelem Elokim = sefirot).

**Ibn Ezra:** "Let us" is the royal "we" (plural of majesty), common in Hebrew. No consultation with angels.

**Rashbam:** "Our image" means the image of the earth — man is created from the earth but with divine breath.

**Zohar (I:134b):** "Our image" refers to the union of the Holy One Blessed Be He (male) and the Shechinah (female). Man is created in the image of the divine couple.

**Dispute Modeling:**
```
Dispute:
  name: "Meaning of 'Let us make man' (Genesis 1:26)"
  topic: Adam
  dispute_type: semantic
  opinions: [Rashi_opinion, Ramban_opinion, Ibn_Ezra_opinion, Rashbam_opinion, Zohar_opinion]
  primary_source: Genesis 1:26
  era: Rishonic + Kabbalistic
  resolution_status: perpetually_disputed
  is_active: true
  affected_concepts: [Adam, Tzelem Elokim, Neshamah, Sefirah, Shechinah, Malchut]

Opinion (Rashi):
  holder: Rashi
  topic: Tzelem_Elokim
  position: "God consulted with the angels. Man is created with a body and soul, combining physical and spiritual."
  reasoning: "The plural 'us' indicates consultation. This teaches humility — a great person should consult with lesser ones."
  source: Rashi Genesis 1:26
  method_used: midrashic

Opinion (Ramban):
  holder: Ramban
  topic: Tzelem_Elokim
  position: "Man is created in the image of the sefirot — the divine structure."
  reasoning: "Tzelem refers to the sefirot. Man's form corresponds to the supernal form — head, body, arms, legs correspond to the Tree of Life."
  source: Ramban Genesis 1:26
  method_used: kabbalistic
  worldview: Ramban_Kabbalah

Opinion (Zohar):
  holder: Zohar
  topic: Tzelem_Elokim
  position: "Man is created in the image of the divine union — male and female aspects of God."
  reasoning: "The 'us' refers to the Holy One and the Shechinah. Man is created male and female to reflect this divine union."
  source: Zohar I:134b
  method_used: lurianic_kabbalah
  worldview: Lurianic_Kabbalah
```

**Analysis:** This verse has FIVE distinct explanations from major authorities. None is "wrong" in the ontology. The ontology preserves all five with their reasoning and sources. A user viewing this verse would see all five opinions and their textual sources.

---

## 8. Dispute Engine Validation

### Test 1: Simultaneous Representation
**Question:** Can the ontology represent "Rashi says X" and "Ramban says not-X" without either being marked as "correct"?
**Result:** YES. Both are Opinion entities. The Dispute entity links them with no resolution bias.

### Test 2: Resolution Preservation
**Question:** If a later authority (e.g., Shulchan Aruch) rules like one side, is the other side still preserved?
**Result:** YES. The Dispute entity records `resolution_opinion` but does not delete the opposing Opinion.

### Test 3: Worldview Coherence
**Question:** Can the ontology represent that Rambam's opinion on Mitzvot is connected to his opinion on Prophecy, Soul, and Divine Attributes?
**Result:** YES. Both opinions link to the same Worldview entity. The ontology can answer: "Show me all opinions held by the Aristotelian Rationalist worldview."

### Test 4: Cross-Domain Disputes
**Question:** Can the ontology represent that a Halachic dispute (e.g., eruv) is influenced by a Metaphysical worldview (e.g., rationalism vs. mysticism)?
**Result:** PARTIAL. The ontology can link opinions to worldviews, but it cannot automatically detect when a halachic dispute is worldview-driven. This requires human analysis.

### Test 5: Temporal Evolution
**Question:** Can the ontology represent that Rav Moshe Feinstein changed his opinion on brain death between 1968 and 1990?
**Result:** YES. Two Opinion entities with different dates, linked by a Temporal Dispute.

---

## 9. Dispute Model Failure Analysis

### Failure 1: The Silent Majority
**Problem:** Some disputes are not recorded in texts. The majority opinion may be so obvious that no one writes it down. The recorded disputes may represent only the fringe cases.
**Example:** Most authorities probably agreed that pork is forbidden, but only the rare disputes about borderline cases are recorded.
**Ontology Weakness:** The ontology cannot infer silent agreement. It only knows what is written.

### Failure 2: The Composite Authority
**Problem:** Some "authorities" are actually composites. "Talmudic opinion" is not a single person but a synthesis of Amoraic debates.
**Example:** The Talmud often says "the rabbis say X" without naming anyone.
**Ontology Weakness:** The ontology requires a Person entity for every Opinion. Anonymous or composite opinions create ambiguity.

### Failure 3: The Cultural Dispute
**Problem:** Some disputes are not about Torah but about cultural context. Ashkenazim vs. Sefaradim may disagree because of different environments, not different Torah principles.
**Example:** Kitniyot on Pesach is partly a cultural/geographic dispute.
**Ontology Weakness:** The ontology does not model cultural/geographic factors as first-class dispute drivers.

### Failure 4: The Unresolvable Dispute
**Problem:** Some disputes are fundamentally unresolvable because the authorities are using different axioms.
**Example:** Rambam vs. Kabbalah on the nature of God. They are not disagreeing about a fact — they are using different conceptual frameworks.
**Ontology Weakness:** The Dispute entity assumes shared conceptual space. Worldview disputes may be incommensurable.

---

## 10. Dispute Model V2 Improvements

Based on the failures, Dispute Model V2 adds:

1. **SilentAgreement entity:** Records that an opinion is "universal" or "silent majority" even if not explicitly stated.
2. **CompositeAuthority entity:** For anonymous or collective opinions ("Chazal", "Geonim", "Rishonim").
3. **CulturalContext entity:** Tracks geographic, cultural, and historical factors that influence disputes.
4. **IncommensurabilityFlag:** Marks disputes where the sides are using fundamentally different frameworks.
5. **DialecticalChain entity:** For Talmudic disputes where opinions evolve through a chain of debate (A says X, B challenges, C resolves, D challenges the resolution...).
