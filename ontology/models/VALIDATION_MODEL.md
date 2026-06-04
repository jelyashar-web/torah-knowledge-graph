# Torah Ontology — Validation Model V1.0
## Chief Torah Ontology Scientist — Research Document

---

## 1. Purpose

The Validation Model ensures that ONLY authentic, sourced, and accurately modeled Torah knowledge enters the ontology. It is the GATEKEEPER.

**Principle:** The ontology must be MORE rigorous than Wikipedia, because it deals with sacred knowledge.

---

## 2. Validation Levels

### Level 1: Automated Validation (Machine-Only)
**Scope:** Structural checks, format validation, cross-references.
**Speed:** Instant.
**Checks:**
- Does the entity have all required fields?
- Does the source reference point to a real book?
- Does the Hebrew text contain valid UTF-8?
- Are relationship domain restrictions satisfied?
- Are hierarchical relationships acyclic?
- Are confidence scores within valid ranges?

### Level 2: Source Verification (Machine + Database)
**Scope:** Verifying that cited sources actually exist and say what is claimed.
**Speed:** Minutes to hours.
**Checks:**
- Does the cited book exist in Sefaria / HebrewBooks / Bar-Ilan?
- Does the cited chapter/verse/page exist?
- Does the cited text actually contain the quoted passage?
- Are page numbers consistent across editions?
- Are there variant readings that affect the claim?

### Level 3: Expert Review (Human Validator)
**Scope:** Torah scholars verify accuracy, context, and representation.
**Speed:** Days to weeks.
**Checks:**
- Is the concept accurately defined?
- Is the source correctly interpreted?
- Are alternative opinions represented?
- Is the authority level appropriate?
- Are aliases complete and accurate?
- Are context rules correct?
- Are there missing disputes?
- Are cross-domain links appropriate?

### Level 4: Peer Review (Multiple Experts)
**Scope:** Multiple scholars independently review.
**Speed:** Weeks to months.
**Checks:**
- Do independent experts agree on the definition?
- Are there scholars who would dispute the representation?
- Is the entity culturally sensitive (e.g., Soul Root, disputes between denominations)?
- Are modern applications handled appropriately?

### Level 5: Community Consensus (Broad Validation)
**Scope:** Wider community of Torah scholars validates.
**Speed:** Months.
**Checks:**
- Does the entity reflect consensus where consensus exists?
- Does it fairly represent disputes where they exist?
- Is it useful to researchers, educators, and learners?
- Does it avoid theological bias?

---

## 3. Validation Rules

### VR1: Biblical Concepts Require Biblical Sources
Any concept tagged as `domain=Torah` and `authority_level=Biblical` MUST have at least one source from Tanakh.
**Failure:** If no biblical source exists, the concept is either mis-tagged or requires a lower authority level.

### VR2: Talmudic Concepts Require Talmudic Sources
Any concept requiring Talmudic authority MUST have a Mishnah, Talmud Bavli, or Talmud Yerushalmi source.
**Failure:** If the concept is attributed to "Chazal" without a specific tractate, it is marked as ATTRIBUTION_NEEDED.

### VR3: Kabbalistic Concepts Require Kabbalistic Sources
Any concept tagged as `domain=Kabbalah` MUST have a source from Zohar, Arizal's writings, Ramak, or recognized Kabbalistic text.
**Exception:** Concepts that bridge Torah and Kabbalah (e.g., Ma'aseh Merkavah) may have both.

### VR4: Soul Root Sources Are Restricted
Any SoulRoot entity MUST be sourced ONLY from:
- Zohar (all volumes)
- Writings of the Arizal (Etz Chaim, Pri Etz Chaim, Shaar HaKavanot, Shaar HaGilgulim, etc.)
- Writings of Rashash (Siddur HaAri)
- Writings of the Vilna Gaon on Kabbalah
**Violation:** A SoulRoot sourced from any other text is REJECTED.

### VR5: Modern Concepts Require Modern Sources
Any concept introduced by modern authorities (20th-21st century) MUST have a published responsum, book, or article.
**Exception:** Widely accepted customs (minhagim) may have oral tradition evidence with community validation.

### VR6: Disputed Concepts Must Show All Sides
If a concept is marked `is_disputed=true`, the ontology MUST have at least 2 Opinion entities and 1 Dispute entity.
**Failure:** If fewer than 2 opinions exist, the dispute flag is removed or the concept is marked as INCOMPLETE.

### VR7: Cross-Domain Concepts Must Be Split
If a concept appears in multiple domains with different meanings, it MUST be modeled as separate instances per R1.
**Failure:** If a single concept has multiple contradictory definitions, it is SPLIT by the validation engine.

### VR8: Aliases Must Be Sourced
Every alias MUST have a source showing who uses that name.
**Failure:** Unsourced aliases are removed.

### VR9: Relationships Must Have Evidence
Every relationship MUST have at least one source.
**Failure:** Unsourced relationships are REJECTED.

### VR10: Confidence Must Match Evidence
The confidence score MUST reflect the evidence quality:
- Direct quote + correct context = 0.95-1.0
- Paraphrase + correct context = 0.85-0.95
- Inference = 0.7-0.85
- Attribution = 0.5-0.7
**Failure:** Confidence that does not match evidence is ADJUSTED by the validator.

---

## 4. Validation Failure Report

### Failure 1: The Edition Problem
**Problem:** Page numbers in Rishonic texts vary across editions. A source cited as "Ramban Genesis 1:26" is unambiguous, but "Ramban page 45" depends on the edition.
**Solution:** Standardized citation format: `[Authority] [Book] [Chapter:Verse or Section]` for biblical/commentary; `[Tractate] [Daf] [Amud]` for Talmud; `[Book] [Siman] [Seif]` for Shulchan Aruch.

### Failure 2: The Translation Trap
**Problem:** Validators may work from translations, missing Hebrew nuances.
**Example:** "Ruach" translated as "spirit" loses the wind/breath/spirit ambiguity.
**Solution:** Validation MUST be done with Hebrew/Aramaic text visible. Translation is secondary.

### Failure 3: The Denominational Bias
**Problem:** A validator from one denomination may unconsciously bias the ontology.
**Example:** A Chabad validator may over-represent Chabad perspectives; a MO validator may under-represent Kabbalah.
**Solution:** Validation team must include representatives from: Litvak, Chassidic, Sefardi, Yemenite, Modern Orthodox, and academic perspectives. No single denomination dominates.

### Failure 4: The Gender Gap
**Problem:** Most Torah authorities in the canon are male. Concepts related to women's obligations may be under-represented or filtered through male perspectives.
**Example:** Niddah and mikvah concepts are often defined by male authorities.
**Solution:** Where possible, include female perspectives (e.g., Iggeret HaRamban to his son includes motherly advice; modern female Torah scholars). Mark when a concept is defined exclusively by male authorities.

### Failure 5: The Geographical Bias
**Problem:** The ontology may over-represent Ashkenazi authorities and under-represent Sefardi, Mizrahi, and Yemenite traditions.
**Example:** Minhagim may default to Ashkenazi customs.
**Solution:** Geographic tagging of concepts: `origin: Ashkenaz | Sefarad | Mizrahi | Yemen | Edot HaMizrah | universal`.

---

## 5. Validation Metrics

### Coverage Metrics
- **% of concepts with biblical sources**
- **% of concepts with Talmudic sources**
- **% of concepts with Rishonic sources**
- **% of concepts with modern sources**
- **% of disputed concepts with multiple opinions**

### Quality Metrics
- **Average confidence score**
- **% of entities with full source citations**
- **% of aliases with sources**
- **% of relationships with evidence**
- **Dispute representation ratio** (disputed concepts / total concepts)

### Diversity Metrics
- **% of concepts from each domain** (Torah, Halacha, Kabbalah, Chassidut, Musar)
- **% of concepts from each era** (Biblical, Talmudic, Rishonic, Achronic, Modern)
- **Geographic distribution of sources**
- **Gender representation of authorities**

---

## 6. Validation Model V2 Improvements

1. **EditionStandardizer:** Automatically maps page numbers across editions.
2. **TranslationWarning:** Flags when validation is done from translation alone.
3. **DiversityDashboard:** Real-time metrics on denominational/geographic/gender balance.
4. **AdversarialReview:** Deliberately assign validators who disagree with the concept's current representation.
5. **CommunityFeedback:** Allow Torah learners to flag potential errors for expert review.
