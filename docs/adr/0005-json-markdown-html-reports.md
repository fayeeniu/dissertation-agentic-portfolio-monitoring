# ADR-0005: Canonical JSON with Markdown and accessible HTML reports

- Status: Accepted
- Date: 2026-08-26
- Scope: P0 review and export artifacts

## Context

The artifact needs a machine-readable research/audit format, a human-readable text format, and a
browser-viewable report. The supervisor places presentation/slides outside the core scope. PDF is
common but introduces rendering/template/accessibility validation that is not needed to test claim
verification and human approval.

## Decision

- Treat versioned JSON as the canonical export contract, including report/run/dataset IDs,
  sections, claims, verification, provenance, and review decisions—but not raw evidence content.
- Generate Markdown for readable/versionable text and appendix use.
- Generate self-contained semantic HTML with escaped content, headings, lists, responsive layout,
  and no scripts/external assets.
- Export all three together only after approval of the current report version.
- Keep artifacts in ignored versioned local storage with a bundle hash.
- Defer PDF and slides to P1/P2 respectively.

## Options considered

1. **JSON + Markdown + HTML** — chosen for auditability, accessibility, and low complexity.
2. **JSON only** — machine-readable but poor review/dissertation demonstration experience.
3. **PDF as primary** — fixed presentation but weak structured reuse and higher rendering QA.
4. **PowerPoint/slides** — explicitly non-core and risks shifting work from evaluation to polish.
5. **LLM-authored narrative report** — unnecessary for P0 and could obscure deterministic claim
   provenance; optional composition research would need its own condition.

## Consequences

Positive:

- claims/provenance/audit are directly machine-scored;
- Markdown and HTML can be inspected without proprietary software;
- no browser JavaScript or remote resources are required; and
- format generation is deterministic and testable.

Negative/limits:

- the Markdown renderer/export supports a deliberately small subset;
- HTML has not yet undergone a formal WCAG audit across assistive technologies;
- no paginated print/PDF styling; and
- JSON schema versioning/compatibility policy would be needed for external consumers.

## Validation and revisit trigger

The e2e test proves pre-approval export failure and post-approval creation of all formats with
verification/provenance. Revisit PDF only if dissertation submission or an authorised user study
requires it and a visual/accessibility verification process is added.
