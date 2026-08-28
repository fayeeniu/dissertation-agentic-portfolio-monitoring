"use client";

import Link from "next/link";
import { IntakeConsole } from "@/components/IntakeConsole";
import { EmptyState, ErrorNote, Panel, Pill, Skeleton, StatRail } from "@/components/ui";
import { formatDate, formatNumber, statusLabel } from "@/lib/format";
import { useResource } from "@/lib/hooks";
import type { CompaniesPayload } from "@/lib/types";

export default function CompaniesPage() {
  const { data, error, refresh } = useResource<CompaniesPayload>("companies");

  return (
    <div className="stack">
      <section className="stack-sm">
        <p className="eyebrow">Hybrid intake</p>
        <h1>Start from a company number</h1>
        <p className="lede">
          Every research case is rooted in one exact legal identity. A Companies House number opens
          a case on its own; a name or a domain never does.
        </p>
      </section>

      <Panel title="Register a company" eyebrow="Intake">
        <IntakeConsole onCreated={refresh} />
      </Panel>

      {error ? <ErrorNote message={error.message} /> : null}

      {!data ? (
        <div className="panel">
          <div className="panel-body">
            <Skeleton lines={5} />
          </div>
        </div>
      ) : (
        <>
          <StatRail
            items={[
              { label: "Companies", value: formatNumber(data.counts.total) },
              {
                label: "Identity resolved",
                value: formatNumber(data.counts.resolved),
                tone: "evidence",
              },
              {
                label: "Open decisions",
                value: formatNumber(data.counts.identity_holds),
                tone: data.counts.identity_holds ? "human" : "muted",
              },
              { label: "With research runs", value: formatNumber(data.counts.with_runs) },
            ]}
          />

          <Panel title="Companies ledger" eyebrow="List to detail" flush>
            {data.companies.length === 0 ? (
              <EmptyState
                title="The ledger is empty."
                detail="Register a Companies House number above to create the first research case."
              />
            ) : (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th scope="col">Company</th>
                      <th scope="col">Number</th>
                      <th scope="col">Identity</th>
                      <th scope="col">Domain</th>
                      <th scope="col">Evidence</th>
                      <th scope="col">Latest run</th>
                      <th scope="col">Next action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.companies.map((company) => (
                      <tr key={company.id}>
                        <td>
                          <Link href={`/companies/${company.id}`} style={{ fontWeight: 500 }}>
                            {company.name}
                          </Link>
                          <div className="muted" style={{ fontSize: "0.6875rem" }}>
                            {company.classification} · {formatDate(company.created_at)}
                          </div>
                        </td>
                        <td className="mono">{company.identifier?.value ?? "—"}</td>
                        <td>
                          <Pill status={company.resolution_status} />
                          {company.open_decisions > 0 ? (
                            <div
                              className="muted"
                              style={{ fontSize: "0.6875rem", marginTop: "0.2rem" }}
                            >
                              {company.open_decisions} open
                            </div>
                          ) : null}
                        </td>
                        <td className="mono muted">{company.verified_domain ?? "—"}</td>
                        <td className="mono">
                          {company.claim_count > 0 ? `${company.claim_count} claims` : "—"}
                        </td>
                        <td>
                          {company.latest_run ? (
                            <Link href={`/runs/${company.latest_run.id}`}>
                              <Pill status={company.latest_run.status} />
                            </Link>
                          ) : (
                            <span className="muted">—</span>
                          )}
                        </td>
                        <td>
                          <Link href={company.next_action.href ?? `/companies/${company.id}`}>
                            {company.next_action.label} →
                          </Link>
                          <div className="muted" style={{ fontSize: "0.6875rem" }}>
                            {statusLabel(company.lifecycle_status)}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Panel>
        </>
      )}
    </div>
  );
}
