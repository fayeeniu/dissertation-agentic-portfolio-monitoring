"use client";

import Link from "next/link";
import { EmptyState, ErrorNote, Panel, Pill, Skeleton, StatRail } from "@/components/ui";
import { formatDate, formatNumber, humanize, shortHash } from "@/lib/format";
import { useResource } from "@/lib/hooks";
import type { OverviewPayload } from "@/lib/types";

export default function ReportsPage() {
  const { data, error } = useResource<OverviewPayload>("overview");

  if (error) return <ErrorNote message={error.message} />;
  if (!data) {
    return (
      <div className="stack">
        <Skeleton lines={2} />
        <div className="panel"><div className="panel-body"><Skeleton lines={6} /></div></div>
      </div>
    );
  }

  const reportRuns = data.runs.filter((run) => run.profile !== null);
  const approved = reportRuns.filter((run) => run.profile?.status === "approved");
  const review = reportRuns.filter((run) => run.profile?.status === "pending_review");

  return (
    <div className="stack">
      <section className="report-hero">
        <div>
          <p className="eyebrow">Research output</p>
          <h1>Reports & exports</h1>
          <p className="lede">
            Profiles become exportable reports only after evidence capture, exact-span admission,
            deterministic composition and a named decision on the immutable version.
          </p>
        </div>
        <Link className="btn" data-variant="primary" href="/companies">
          Start new research
        </Link>
      </section>

      <div className="report-flow" aria-label="Report generation flow">
        {[
          ["01", "Discover", "Broad public-source bucket"],
          ["02", "Capture", "Policy-checked snapshots"],
          ["03", "Select", "5.4-mini exact-span claims"],
          ["04", "Map metrics", "CBIT definitions and source boundaries"],
          ["05", "Compose", "Versioned IC report proposal"],
          ["06", "Review", "Named approval and export"],
        ].map(([step, label, detail]) => (
          <div key={step}>
            <span>{step}</span>
            <strong>{label}</strong>
            <small>{detail}</small>
          </div>
        ))}
      </div>

      <StatRail
        items={[
          { label: "Report versions", value: formatNumber(reportRuns.length) },
          { label: "Awaiting review", value: formatNumber(review.length), tone: review.length ? "human" : "muted" },
          { label: "Approved exports", value: formatNumber(approved.length), tone: "evidence" },
          { label: "Claims represented", value: formatNumber(reportRuns.reduce((sum, run) => sum + run.claim_count, 0)) },
          { label: "Sources represented", value: formatNumber(reportRuns.reduce((sum, run) => sum + (run.sources.fetched ?? 0), 0)) },
        ]}
      />

      <Panel title="Report library" eyebrow="Versioned and review-bound" flush>
        {reportRuns.length === 0 ? (
          <EmptyState
            title="No report version exists yet."
            detail="Complete a research run through composition. The resulting profile will appear here before approval, while exports remain gated."
          />
        ) : (
          <div className="report-grid">
            {reportRuns.map((run) => {
              const profile = run.profile;
              if (!profile) return null;
              const canExport = profile.status === "approved";
              return (
                <article className="report-card" key={profile.id}>
                  <div className="report-card-head">
                    <div>
                      <p className="eyebrow">Version {profile.version} · cutoff {formatDate(run.cutoff)}</p>
                      <h2>{run.company_name}</h2>
                    </div>
                    <Pill status={profile.status} />
                  </div>
                  <dl className="kv">
                    <dt>Claims</dt><dd>{run.claim_count}</dd>
                    <dt>Captured sources</dt><dd>{run.sources.fetched ?? 0}</dd>
                    <dt>Model route</dt><dd className="mono">{run.model}</dd>
                    <dt>Content hash</dt><dd className="hash">{shortHash(profile.content_sha256, 20)}</dd>
                  </dl>
                  <p className="muted" style={{ fontSize: "0.75rem" }}>
                    {canExport
                      ? "This exact version has named approval and is available as a readable report or machine-readable evidence package."
                      : `${humanize(profile.status)}. Export remains locked until the named review gate is complete.`}
                  </p>
                  <div className="row">
                    <Link className="btn" data-size="sm" href={`/runs/${run.id}`}>Open report workspace</Link>
                    {canExport ? (
                      <>
                        <a className="btn" data-size="sm" href={`/deck/${profile.id}/html`} target="_blank" rel="noreferrer noopener">HTML report</a>
                        <a className="btn" data-size="sm" href={`/deck/${profile.id}/json`} target="_blank" rel="noreferrer noopener">JSON</a>
                      </>
                    ) : null}
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </Panel>
    </div>
  );
}
