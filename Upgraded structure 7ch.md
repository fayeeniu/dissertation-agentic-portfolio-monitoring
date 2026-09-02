# Upgraded Dissertation Structure — Seven Chapters

*1 September 2026. Responds to Georgi's six feedback points. Full styled version: artifact **Seven-Chapter Rebuild**.*

---

## The core diagnosis

All six of Georgi's points are symptoms of one thing: **the report is organised around the system, and it needs to be organised around the evidence.**

Arranged by system layer, the artefact chapter must describe everything built, so it grows; unrun protocols must be accounted for, so they fill appendices and get referenced in the body; and because capability sits structurally next to result, every passage carries its own caveat to keep them apart. That is where the twelve repeated limitations come from and why the technical chapters read as a tour rather than an argument.

Arranged by evidence, one table in Chapter 3 separates *validated* from *built but not evaluated*, the caveats become unnecessary, the artefact chapter only describes what the evaluation touches, and the unrun protocols leave the body entirely.

## Shape


| Now — 8 chapters, 19,719 w  | Rebuilt — 7 chapters, 15,300 w                     |
| --------------------------- | -------------------------------------------------- |
| 1 Introduction — 2,296      | 1 Introduction — 1,400                             |
| 2 Literature Review — 4,990 | 2 Literature Review — 3,400                        |
| 3 Methodology — 1,606       | 3 Methodology (+ ethics, + evidence scope) — 2,500 |
| 4 System Design — 3,265     | 4 The Artefact: the life of a claim — 2,200        |
| 5 Evaluation — 3,402        | 5 Evaluation and Results — 2,400                   |
| 6 Discussion — 2,191        | 6 Discussion (+ pilot, + limitations) — 2,700      |
| 7 Ethics/Limitations — 989  | *dissolved*                                        |
| 8 Conclusion — 980          | 7 Conclusion and Future Work — 900                 |


Chapter 7 is dissolved, not deleted: ethics → Methodology (§3.7), limitations → one section at the end of Discussion (§6.6). This removes the chapter whose existence invited caveats to be sprinkled everywhere else.

## Where each of Georgi's points lands


| Point                                    | Address        | Change                                                                                                                             |
| ---------------------------------------- | -------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Focus on what you actually validated     | §3.3 + §5.1    | Single evidence-scope table: validated / built but not evaluated / planned only. Unrun protocols leave the body.                   |
| Business problem, users, current process | §1.1–1.2, §2.2 | Five user roles move up from §6.7; current reporting cycle described as steps with where time, rework and error enter.             |
| Why multi-agent, not simpler             | §2.6           | Whole argument moves out of §1.5 (where the reader has no criteria) into the literature chapter. Table 2.2 as summary.             |
| Lit review has no flow                   | Ch. 2          | Six buried adjudications promoted; enumeration → argument; connectives 21% → 45%. See LitReview_Rebuild_[Plan.md](http://Plan.md). |
| Technical sections have no flow          | Ch. 4          | Nine layer-by-layer sections → eight stages of one claim's journey.                                                                |
| Remove repeated limitations              | §6.6 only      | Twelve restatements → one 400-word section. −1,200 to −1,800 words.                                                                |
| Move large tables to appendices          | throughout     | Body keeps eight argument-carrying tables; four appendix tables come the other way.                                                |
| Examples of accepted/rejected claims     | §4.7 + §5.4    | Two claims traced end to end through all eight stages as the spine of Ch. 4.                                                       |
| Business pilot plan                      | §6.5           | Expanded from §6.7 into six named sub-parts.                                                                                       |


---

## Chapter outlines

### Ch. 1 — Introduction (1,400 w)

1.1 The reporting problem (keep existing opening) · 1.2 Why it matters **[NEW, 1 para]** · 1.3 Aim, RQs, objectives · 1.4 Scope and boundary (one para, only caveat before §6.6) · 1.5 Contribution and roadmap. **Out:** current §1.5 architecture argument (1,100 w) → §2.6.

### Ch. 2 — Literature Review (3,400 w)

2.1 What this review has to establish (200) · 2.2 The reporting problem: market, users, current process **[NEW]** (600) · 2.3 Why public early-stage evidence resists consolidation (650, ends on gap + competitor matrix) · 2.4 What makes a claim defensible (750, old 2.3+2.4 merged, ALCE vs RARR sub-head) · 2.5 Retrieval as remedy and vulnerability (450) · 2.6 Who is allowed to decide (700, + architecture argument) · 2.7 Settled / contested / gap (300 + traceability table). **In:** architecture argument from §1.5, user roles from §6.7. **Out:** Ribeiro/Kapoor → §3.1; Table 2.1 and Figs 2.1, 2.2 → Ch. 4 or appendix.

### Ch. 3 — Research Design and Methodology (2,500 w) — the only chapter that grows

3.1 Design-science strategy and what counts as evidence (+ Ribeiro from §2.7; fix Fig 3.1 "RQ1–RQ3") · **3.2 Design decisions and rejected alternatives [NEW, 700 w]** — why 14 cases, why one per category, why 3 repeats, why synthetic, why precision/recall/F1 rather than cost-weighted, why C1 vs C2 · **3.3 What was validated and what was not [NEW, 350 w + table]** · 3.4 D0 fixture · 3.5 Measures and denominators (promote Table F.1) · **3.6 Scope decisions: no interviews, no manual baseline [NEW, 250 w]** · 3.7 Ethics, data classification, reproducibility (from Ch. 7).

### Ch. 4 — The Artefact: the life of a claim (2,200 w)

4.1 Requirements and trust boundary (promote Table C.1) · 4.2 Architecture in one page (merge Figs 4.1+4.2) · 4.3 Stages 1–3 intake, identity, capture · 4.4 Stages 4–5 extraction and normalisation (the eight missing states) · 4.5 Stage 6 separate verification (keep Fig 4.4 as the anchor) · 4.6 Stages 7–8 composition, approval, export · **4.7 Two claims traced end to end [NEW, 400 w + table]** · 4.8 Built but not evaluated (6 sentences → §3.3). **Out:** connector manifests and public-web capture detail → Appendix C; Figs 4.3, 4.5 → appendix. **Why:** a layer tour asks the reader to hold nine subsystems in mind and assemble them; a journey gives them one thing to follow and hangs each control off the moment it fires.

The two examples for §4.7: the **accepted observed-zero** (jobs created = 0; submission 0, evidence 0, agree → supported, emitted with source record) and the **rejected contradiction** (grant £100k proposed, register evidence £200k same period → contradicted, claim withheld, disagreement retained for a named person, no averaging or newest-wins).

### Ch. 5 — Evaluation and Results (2,400 w)

5.1 What was run, when, on what (+ one sentence resolving the 28 Aug / 1 Sep / migration-0010 discrepancy) · 5.2 Engineering validation · 5.3 C1 vs C2 (**cut Fig 5.1**) · 5.4 Case-level results (Table 5.3, cross-ref from §4.7) · 5.5 Company-research and adversarial (condense to half) · 5.6 Negative, null and unavailable outcomes (absorb old §5.6). **Delete throughout:** the "these results do not establish…" closer on every subsection.

### Ch. 6 — Discussion (2,700 w)

6.1 What the workflow demonstrates (RQ1) — claim first (+ promote Table H.5) · 6.2 What separate verification changed (RQ2) — precision 0.455→1.000, unsupported 0.545→0.000, recall unchanged; then "selective admission, not better discovery" · 6.3 Role separation revisited (short, refer back to §2.6) · **6.4 What this means for an investment team [NEW]** — consultant voice + screenshots · **6.5 Business pilot plan [EXPANDED]** — integration / staff responsibilities / cost model / time-saving hypotheses / success metrics and go-no-go thresholds / testing still required · **6.6 What this study cannot show [400 w — the ONLY limitations section]** · 6.7 Transferring the design elsewhere (promote Table H.4).

### Ch. 7 — Conclusion and Future Work (900 w)

7.1 Answers to primary question, RQ1, RQ2 (+3 sentences naming the binding limits, cross-ref §6.6) · 7.2 Contribution · 7.3 Sequenced future evidence (keep as written) · **7.4 Closing statement [NEW, 3–4 sentences]** — the report currently stops rather than closes.

---

## Exhibits

Eight process diagrams is itself a flow problem — several are overlapping versions of the same pipeline.


| Exhibit                         | Now        | Rebuilt                                                             |
| ------------------------------- | ---------- | ------------------------------------------------------------------- |
| Fig 2.1 source→claim            | §2.4       | Merge (overlaps Fig 4.4; author-designed, not a literature finding) |
| Fig 2.2 finding ≠ evidence      | §2.5       | Appendix                                                            |
| Fig 3.1 evidence boundary       | §3.1       | Keep — fix "RQ1–RQ3"                                                |
| Fig 4.1 + 4.2                   | §4.2, §4.3 | Merge into one                                                      |
| Fig 4.3 identity intake         | §4.4       | Appendix                                                            |
| Fig 4.4 workflow states         | §4.5       | **Keep — make it the anchor**                                       |
| Fig 4.5 public-web funnel       | §4.7       | Appendix                                                            |
| Fig 5.1 metric profile          | §5.4       | **Cut** — Table 5.2 with a border round it                          |
| —                               | —          | **Add 3–4 screenshots → §6.4**                                      |
| Table F.1 measures              | Appendix F | Promote → §3.5                                                      |
| Table C.1 requirements          | Appendix C | Promote → §4.1                                                      |
| Table H.4 transfer checklist    | Appendix H | Promote → §6.7                                                      |
| Table H.5 results vs literature | Appendix H | Promote → §6.1                                                      |
| Table 2.1 role permissions      | §2.6       | → Appendix (full page, shatters the chapter mid-argument)           |


---

## Order of work

1. **Delete repeated limitations** — write §6.6, then sweep. Do this first: most of the word cut, fixes tone, makes room. *(2–3 h, −1,200 to −1,800 w)*
2. **Write §3.3 evidence-scope table** — everything downstream cross-references it. *(1.5 h)*
3. **Move the four blocks** — §1.5→§2.6, §6.7 roles→§2.2, §2.7 Ribeiro→§3.1, Ch. 7 ethics→§3.7. *(2 h)*
4. **Rebuild Ch. 2** into six argued sections + competitor matrix + traceability table. *(4 h)*
5. **Re-order Ch. 4 as the life of a claim; write §4.7.** *(3 h)*
6. **Write §3.2 and §3.6** in your own voice. *(2.5 h)*
7. **Rewrite Ch. 6; expand the pilot into six named parts; add §6.4 + screenshots.** *(3.5 h)*
8. **Exhibits pass** — cut, merge, promote, screenshot, publish repo and demo. *(2.5 h)*
9. **Sentence pass, errata, references, Turnitin.** *(3 h — reference check last, do not skip)*

