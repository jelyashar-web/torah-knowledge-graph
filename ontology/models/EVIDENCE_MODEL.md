# Torah Ontology — Evidence Model V1.0
## Chief Torah Ontology Scientist — Research Document

---

## 1. Core Principle

**Nothing exists in the ontology without provenance.**

Every concept, relationship, opinion, and dispute must be traceable to:
- A specific book
- A specific location in that book
- A specific passage of text
- A specific authority who said it
- A specific confidence level

If evidence is missing, the entity is INVALID and must be flagged.

---

## 2. Evidence Hierarchy

### Level 1: Biblical Evidence
**Weight:** Absolute (for biblical concepts)
**Requirements:**
- Book name (Torah, Nevi'im, Ketuvim)
- Chapter and verse
- Hebrew text (Masoretic text)
- Translation (if applicable)
- Masoretic notes (if relevant)
**Example:** "Genesis 1:1 — בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ"

### Level 2: Talmudic Evidence
**Weight:** Very High (for rabbinic concepts)
**Requirements:**
- Tractate name
- Daf and amud (e.g., "Berachot 2a")
- Line number (if available in standard editions)
- Hebrew/Aramaic text
- Context (Mishnah, Gemara, Tosafot, etc.)
**Example:** "Berachot 2a, line 3 — מִקָּלֵי עַלְּיָא בְּרֵאשִׁית..."

### Level 3: Geonic Evidence
**Weight:** High
**Requirements:**
- Responsum or commentary title
- Page or section number
- Hebrew/Aramaic text
**Example:** "Shaarei Teshuvah #45 — ..."

### Level 4: Rishonic Evidence
**Weight:** High
**Requirements:**
- Commentary title
- Book and chapter/verse being commented on
- Page in standard edition (if applicable)
- Hebrew text of the commentary
**Example:** "Rashi Genesis 1:1 — בְּרֵאשִׁית בָּרָא אֱלֹהִים — ..."

### Level 5: Achronic Evidence
**Weight:** Medium-High
**Requirements:**
- Book title
- Chapter/section/page
- Hebrew text
**Example:** "Shulchan Aruch OC 1:1 — יְקִיא קוֹמָה..."

### Level 6: Modern Evidence
**Weight:** Medium (for contemporary application)
**Requirements:**
- Book/article title
- Author
- Publication year
- Page or URL
- Hebrew/English text
**Example:** "Rav Moshe Feinstein, Iggerot Moshe OC 1:1 (1959) — ..."

### Level 7: Oral Tradition
**Weight:** Low (for customs and traditions without written source)
**Requirements:**
- Description of the tradition
- Community or dynasty that practices it
- Earliest written record of the tradition
- **Flag:** "Oral tradition — written source may not exist"
**Example:** "Minhag Ashkenaz: not eating kitniyot on Pesach — earliest written source: 13th century responsa"

---

## 3. Evidence Types

### Direct Quotation
The exact words of the authority. Highest confidence.
**Format:** "[Authority] says: '[exact quote]' ([source])"

### Paraphrase
A faithful restatement of the authority's position. High confidence.
**Format:** "[Authority] holds that [paraphrase] ([source])"
**Requirement:** Must be clearly marked as paraphrase, not quote.

### Inference
A logical deduction from the authority's position. Medium confidence.
**Format:** "Based on [Authority]'s position in [source], it follows that [inference]"
**Requirement:** Must show the reasoning chain.

### Attribution
A claim that the authority held a position, without direct textual evidence. Lower confidence.
**Format:** "[Secondary authority] attributes to [Primary authority] the view that [position]"
**Requirement:** Must name the secondary authority and their source.

### Consensus
A claim that "all authorities agree" or "the majority holds." Medium confidence.
**Format:** "Consensus of [list of authorities] holds that [position]"
**Requirement:** Must list the authorities or cite a source that establishes consensus.

---

## 4. Evidence Validation Rules

### EVR1: Source Existence
The source MUST exist. Citing a non-existent book or page is FORGERY.
**Validation method:** Check against Sefaria, HebrewBooks.org, or academic bibliography.

### EVR2: Text Accuracy
The quoted text MUST match the source. Misquoting is CORRUPTION.
**Validation method:** Compare against digital text (Sefaria, Bar-Ilan Responsa, etc.).

### EVR3: Attribution Accuracy
The cited authority MUST have actually said what is attributed to them.
**Validation method:** Verify in the primary source or a reliable secondary source.

### EVR4: Context Preservation
The quote MUST include enough context to avoid misrepresentation.
**Minimum context:** 3 sentences before and after the quote, or the entire paragraph.

### EVR5: Translation Accuracy
If the evidence includes a translation, the translation MUST be accurate and labeled.
**Requirement:** Translation must be attributed to a named translator or translation.

### EVR6: Multiple Attestation
For important claims, evidence from multiple independent sources is STRONGER than single attestation.
**Rule:** Disputed concepts should have evidence from at least 2 authorities.

### EVR7: Chain of Transmission
For oral traditions, the chain of transmission (mesorah) SHOULD be recorded if known.
**Example:** "Minhag received from Rabbi X, who received from Rabbi Y, who received from the Vilna Gaon."

---

## 5. Evidence Failure Modes

### Failure 1: The Lost Source
**Problem:** The Talmud quotes sources that no longer exist (e.g., Baraita of Rabbi Eliezer, Sifra, some Tosefta passages).
**Ontology Response:** Mark the source as `status=extant` or `status=lost`. Lost sources are valid evidence but with lower confidence.

### Failure 2: The Variant Text
**Problem:** Different manuscripts of the same text have different readings. Which one is "correct"?
**Example:** Some manuscripts of Rashi have different readings than the standard printed edition.
**Ontology Response:** Create TextVariant entities. The evidence entity links to a specific variant with manuscript provenance.

### Failure 3: The Pseudepigraphon
**Problem:** Some texts are falsely attributed (e.g., some Zohar passages may be later additions; some "Rambam" letters may be forgeries).
**Ontology Response:** Mark authorship as `attribution=certain`, `attribution=probable`, or `attribution=doubtful`. Doubtful attributions require additional evidence.

### Failure 4: The Modern Fabrication
**Problem:** Fake Torah sources circulate on the internet.
**Example:** "The Baal Shem Tov said..." quotes that are not found in any authentic text.
**Ontology Response:** All evidence must be traceable to a printed text or authenticated digital source. Internet memes are REJECTED unless traced to a real book.

### Failure 5: The Out-of-Context Quote
**Problem:** A quote is technically accurate but means the opposite when read in context.
**Example:** "Rambam says [X]" — but Rambam says X as a straw man he intends to refute.
**Ontology Response:** EVR4 (Context Preservation) is mandatory. The ontology must include the surrounding text.

### Failure 6: The Overlapping Evidence
**Problem:** Two sources look independent but are actually quoting the same lost earlier source.
**Example:** Rashi and Ibn Ezra may both quote a lost Midrash.
**Ontology Response:** Evidence entities include `ultimate_source` field to trace back to the original source if known.

---

## 6. Evidence Engine for AI-Extracted Relationships

### Input: Raw AI Extraction
The AI claims: "Rambam holds that [X]."

### Evidence Engine Steps:
1. **Authority Check:** Is Rambam a real authority? (YES — known person)
2. **Source Check:** Does the AI provide a source? (MUST have source)
3. **Text Check:** Does the source text actually say X? (HUMAN VALIDATION REQUIRED)
4. **Context Check:** Is X the actual position or a straw man? (HUMAN VALIDATION REQUIRED)
5. **Confidence Assignment:**
   - Direct quote + correct context = confidence 0.95-1.0
   - Paraphrase + correct context = confidence 0.85-0.95
   - Inference + clear reasoning = confidence 0.7-0.85
   - Attribution without direct text = confidence 0.5-0.7
   - No source = REJECTED

### Output: Validated Evidence Entity
```
evidence_id: UUID
claim: "Rambam holds X"
authority: Rambam
source: Moreh Nevuchim III:26
source_text: "...exact quote..."
context_before: "...3 sentences before..."
context_after: "...3 sentences after..."
evidence_type: direct_quotation | paraphrase | inference | attribution
confidence: 0.95
validator: human_expert_name
validation_date: date
status: validated | pending | rejected
rejection_reason: (if rejected)
```

---

## 7. Evidence Model Stress Test

### Test: Modeling "Rambam on Techiyat HaMetim"
**Claim:** Rambam believes in physical resurrection.
**Evidence:**
1. Rambam's 13th Principle: "I believe with perfect faith in the resurrection of the dead."
2. BUT: Rambam's Moreh Nevuchim seems to describe a spiritual afterlife, not physical resurrection.
3. BUT: Rambam later wrote Maamar Techiyat HaMetim defending physical resurrection against critics.

**Evidence Engine Result:**
- The 13th Principle is DIRECT QUOTATION (confidence 1.0)
- The Moreh Nevuchim passages are DIRECT QUOTATION but require context (confidence 0.85 — need to show he was writing for a philosophical audience)
- Maamar Techiyat HaMetim is DIRECT QUOTATION (confidence 1.0)
- The "contradiction" is actually a TEMPORAL DISPUTE — Rambam's views evolved or were expressed differently for different audiences.

**Ontology Conclusion:** Rambam's position is correctly modeled as:
- Public position (13th Principle, Maamar): Physical resurrection
- Philosophical work (Moreh): Spiritual immortality (possibly for a different audience)
- Temporal evolution: Later writings clarify earlier ambiguity

**This demonstrates that the Evidence Model can handle AUTHORITY COMPLEXITY — authorities who hold different views in different contexts or at different times.**

---

## 8. Evidence Model V2 Improvements

1. **VariantText entity:** For manuscripts with different readings.
2. **UltimateSource field:** For tracing quotes back to original sources.
3. **AudienceTag field:** For tracking whether a text was written for philosophers, laypeople, or mystics.
4. **TemporalPhase field:** For authorities whose views evolved.
5. **ForgeryDetection flag:** For marking known or suspected pseudepigrapha.
