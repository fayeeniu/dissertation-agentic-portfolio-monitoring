```yaml
review:
  skill: dissertation-reviewer
  gate: PASS
  verdict: APPROVED
  mode: RE_REVIEW
  section: "4.4 Intake and legal-identity control"
  section_type: "system design and implementation"
  round: 3
  scope: "Dissertation/chapters/04_system_design.tex lines 49-65, including Figure 4.3 SYS-F3"
  evidence_confidence: HIGH
  findings:
    blocker: 0
    major: 0
    minor: 0
    optional: 0
  previous_findings:
    resolved: 2
    partially_resolved: 0
    unresolved: 0
    regression: 0
    user_waived: 0
  next_owner: none
```

# Section 4.4 independent re-review

## 1. Decision

**APPROVED.** `SYS44-001` and `SYS44-R2-001` are resolved. SYS-F3 now has a truthful,
fully matching 27-input stable seal; the changing control-room and workflow test surfaces are
explicitly supplementary and unpinned; and no semantic, evidence-status, test or layout regression
was found.

## 2. Scope and evidence consulted

- The round-two review and acceptance condition for `SYS44-R2-001`, with continued regression
  checks for `SYS44-001`.
- `Dissertation/chapters/04_system_design.tex` lines 49--65, the Section 4.4 evidence packet,
  claim-ledger rows `4.4-P1`--`4.4-P4`, and the Section 4.4 audit-ledger row.
- `Dissertation/exhibits/sys_f3_legal_identity_decision_flow.{py,svg,pdf,txt}` and provenance JSON;
  independent SHA-256 verification of all declared inputs and outputs.
- Current `src/portfolio_agent/company_research.py`,
  `tests/integration/test_company_research.py`, `tests/integration/test_control_room_api.py`, the
  exact fake/synthetic workflow case and the 15-case scoped selection.
- Exact word/citation extraction, strict source checker, fresh Tectonic build, PDF metadata and
  fresh raster inspection of physical pages 54--56.

The re-review was restricted to the two prior findings and dependent regression checks. No live
Companies House, public-web or external-model action was run or inferred. Section 4.5 was not
reviewed.

## 3. Blocking findings

None.

## 4. Previous-finding reconciliation

| Finding | Prior severity | Status | Resolution evidence |
|---|---:|---|---|
| `SYS44-001` | MAJOR | **RESOLVED** | No current provenance, evidence-packet, claim-ledger or section-ledger surface reinstates the obsolete workflow-failure assertion. The provenance records the passing fake/synthetic snapshot at `company_research.py` SHA `4988b8f03601d0432da6e1753677fbee299c5102a492511273839b243c5986b7` and `test_company_research.py` SHA `5cc13f1c1168c496b516f42a6be309c545cc706b6c525bf112273842a1a9ff9c`, explicitly outside the stable seal. The exact case passes at those unchanged hashes, with no live-source, empirical or production claim. |
| `SYS44-R2-001` | MAJOR | **RESOLVED** | Provenance SHA-256 is `a119b67b132f2b81ccc2f75cff53b741d10e481efb1fd6eb75b0a6dc1a8e8b98`. All 27 declared stable inputs and all four outputs match. `tests/integration/test_control_room_api.py` is absent from the declared inputs and described consistently as supplementary unpinned validation; its two selected cases pass within the 15-case selection. The evidence packet, claim ledger and section ledger use the same 27/27 boundary and contain no stale 28/28 or sealed-control-room assertion. |

No partially resolved, unresolved, waived or regression finding remains.

## 5. Non-blocking notes

None.

## 6. Section-level assessment

- **Purpose, evidence and style — meets.** Section 4.4 remains exactly 350 citation-stripped words
  across four substantive paragraphs with 2/2/3/3 distinct admitted citations. Its accepted British
  MSc-level argument and exact source/repository boundaries are unchanged.
- **Technical and evidence-status validity — meets.** Structural number validation remains
  separate from registry confirmation; submitted claims, named decisions, explicit holds, no
  fuzzy/name-only auto-merge, synchronous-local reuse and G2-held registry retrieval remain
  accurately bounded. No live, empirical, production, compliance or user-benefit claim appears.
- **Provenance and reproducibility — meets.** The requested provenance SHA matches; all 27 stable
  inputs and four outputs verify. The control-room test and two workflow files are unsealed and
  explicitly limited to supplementary fake/synthetic validation.
- **Figure integrity and placement — meets.** Visible PY/SVG/PDF/TXT hashes remain
  `ed1cf107c12cca113849caef0e815d374db53379657f14f26b48a0101b3ac923`,
  `d1b8021e25339361f691f16e4e7953d8658fb75451cafb17cbd747d9aee5bcca`,
  `95bda14a1832977fd847f5e698f3fbe47ab21dd1484102139fd9bd7c5a378ff4` and
  `3a9f0d9e0a3e1905f1abf1b0958672fa4f50ba4bd3168c9364ca1ff28c066cb4`.
  Fresh pages 54--56 contain the complete prose, Figure 4.3 and then Section 4.5 without a blank
  page, clipping, overlap, unreadable element or float-order regression.
- **Validation — meets.** The exact workflow and all 15 scoped cases pass; the only diagnostics are
  the disclosed Starlette and Python 3.12 SQLite deprecation warnings. The strict source gate passes
  with 38 local PDFs/hashes, two immutable captures, 89 substantive paragraphs and 34 cited
  sources. Tectonic builds the 72-page A4 report; emitted warnings originate outside Section 4.4
  and SYS-F3.

## 7. Handoff

Section 4.4 and SYS-F3 are approved at round three. No further Section 4.4 revision or reviewer
handoff is required. This approval does not review or pre-approve Section 4.5.
