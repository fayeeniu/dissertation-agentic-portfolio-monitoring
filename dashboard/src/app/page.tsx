"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { RunPipeline } from "@/components/RunPipeline";
import { EmptyState, ErrorNote, NextActionBanner, Panel, Pill, Skeleton, StatRail } from "@/components/ui";
import { formatDate, formatNumber, statusLabel } from "@/lib/format";
import { usePrefersReducedMotion, useResource } from "@/lib/hooks";
import type { OverviewPayload } from "@/lib/types";

function modelRouteLabel(
  route: { model: string; effort: string } | undefined,
  fallbackModel: string,
  fallbackEffort: string,
): string {
  return `${route?.model ?? fallbackModel} · ${route?.effort ?? fallbackEffort}`;
}

export default function ControlRoomPage() {
  const reduced = usePrefersReducedMotion();
  // Poll only while something is genuinely executing; an idle control room is quiet.
  const { data, error, loading } = useResource<OverviewPayload>("overview", 4000);

  if (error) {
    return (
      <div className="stack">
        <ErrorNote message={error.message} />
        <p className="muted" style={{ fontSize: "0.8125rem" }}>
          Start the research service with <code className="mono">portfolio-agent serve</code> and
          reload.
        </p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="stack">
        <Skeleton lines={2} />
        <div className="panel">
          <div className="panel-body">
            <Skeleton lines={5} />
          </div>
        </div>
      </div>
    );
  }

  const { metrics, system } = data;
  const activeRuns = data.runs.filter(
    (run) => run.status === "running" || run.status === "pending",
  );
  const recentRuns = data.runs.slice(0, 6);

  return (
    <div className="stack">
      <section className="stack-sm">
        <p className="eyebrow">Bounded multi-agent research</p>
        <h1>What needs a person before evidence becomes a profile?</h1>
        <p className="lede">
          Six bounded roles move one company from an exact Companies House number to a cited
          profile. Each stage is persisted with its own input and output hash, and nothing exports
          without a named decision.
        </p>
      </section>

      <NextActionBanner
        label={data.next_action.label}
        detail={data.next_action.detail}
        href={data.next_action.href}
      />

      <StatRail
        items={[
          { label: "Companies", value: formatNumber(metrics.companies) },
          {
            label: "Identity holds",
            value: formatNumber(metrics.identity_holds),
            tone: metrics.identity_holds ? "human" : "muted",
          },
          {
            label: "Runs executing",
            value: formatNumber(metrics.runs_active),
            tone: metrics.runs_active ? "evidence" : "muted",
          },
          {
            label: "Awaiting review",
            value: formatNumber(metrics.runs_pending_review),
            tone: metrics.runs_pending_review ? "human" : "muted",
          },
          { label: "Claims admitted", value: formatNumber(metrics.claims), tone: "evidence" },
          { label: "Sources captured", value: formatNumber(metrics.sources_captured) },
          {
            label: "Sources withheld",
            value: formatNumber(metrics.sources_withheld),
            tone: metrics.sources_withheld ? "danger" : "muted",
          },
        ]}
      />

      <div className="split">
        <div className="stack">
          <Panel
            title="Execution"
            eyebrow={activeRuns.length ? "Live" : "Idle"}
            flush
            aside={
              <Link className="btn" data-size="sm" href="/companies">
                New research case
              </Link>
            }
          >
            {recentRuns.length === 0 ? (
              <EmptyState
                title="No research run has been recorded."
                detail="Register a Companies House number, accept the identity, then start a bounded public research run."
              />
            ) : (
              <ul className="list">
                {recentRuns.map((run) => (
                  <li key={run.id}>
                    <Link
                      href={`/runs/${run.id}`}
                      className="rowlink"
                      style={{ display: "grid", gap: "0.45rem" }}
                    >
                      <span className="row" style={{ justifyContent: "space-between" }}>
                        <span className="row" style={{ gap: "0.6rem", minWidth: 0 }}>
                          <strong style={{ fontWeight: 550, fontSize: "0.875rem" }}>
                            {run.company_name}
                          </strong>
                          <Pill status={run.status} />
                        </span>
                        <span className="mono muted" style={{ fontSize: "0.6875rem" }}>
                          cutoff {formatDate(run.cutoff)}
                        </span>
                      </span>
                      <RunPipeline run={run} />
                      <span className="row muted" style={{ gap: "1rem", fontSize: "0.6875rem" }}>
                        <span>
                          {run.sources.fetched ?? 0}/{run.sources.total} sources captured
                        </span>
                        <span>{run.claim_count} claims admitted</span>
                        {run.active_role ? <span>next · {run.active_role}</span> : null}
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </Panel>

          <Panel title="Attention queue" eyebrow="Blockers first" flush>
            {data.attention.length === 0 ? (
              <EmptyState
                title="Nothing is held, contradicted or failing."
                detail="Holds, blocked sources, failures and pending reviews appear here in severity order."
              />
            ) : (
              <ul className="list">
                {data.attention.map((item, index) => (
                  <motion.li
                    key={item.id}
                    initial={reduced ? false : { opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.24, delay: reduced ? 0 : index * 0.02 }}
                  >
                    <Link href={item.href} className="attention-row" data-severity={item.severity}>
                      <span className="attention-kind">{item.kind}</span>
                      <span style={{ minWidth: 0 }}>
                        <span style={{ display: "block", fontSize: "0.8125rem" }}>{item.title}</span>
                        <span className="muted" style={{ fontSize: "0.75rem" }}>
                          {item.detail}
                        </span>
                      </span>
                      <span className="mono muted" style={{ fontSize: "0.6875rem" }}>
                        {item.action_label} →
                      </span>
                    </Link>
                  </motion.li>
                ))}
              </ul>
            )}
          </Panel>
        </div>

        <div className="stack">
          <Panel title="Runtime boundary" eyebrow="Governance">
            <dl className="kv">
              <dt>Runtime</dt>
              <dd>{system.runtime}</dd>
              <dt>Reviewer</dt>
              <dd>{system.reviewer ?? "Not configured"}</dd>
              <dt>Reasoning model</dt>
              <dd className="mono">
                {system.external_model_enabled
                  ? modelRouteLabel(
                      system.model_route?.reasoning,
                      system.escalation_model,
                      "configured",
                    )
                  : "Closed by default"}
              </dd>
              <dt>Repair model</dt>
              <dd className="mono">
                {system.external_model_enabled
                  ? modelRouteLabel(system.model_route?.repair, system.model, "low")
                  : "Closed by default"}
              </dd>
              <dt>Selection model</dt>
              <dd className="mono">
                {system.external_model_enabled || system.research_mode === "fixture"
                  ? modelRouteLabel(system.model_route?.selection, system.model, "low")
                  : "Closed by default"}
              </dd>
              <dt>Live retrieval</dt>
              <dd>{system.live_retrieval_enabled ? "Open" : "Closed"}</dd>
              <dt>Export</dt>
              <dd>Named approval required</dd>
            </dl>
            <p className="muted" style={{ fontSize: "0.75rem", marginTop: "0.75rem" }}>
              {system.boundary}
            </p>
          </Panel>

          <Panel title="Agent roster" eyebrow="Bounded roles">
            <div className="stack-sm">
              {system.agents.map((agent) => (
                <div key={agent.key} className="roster-card">
                  <div className="row" style={{ justifyContent: "space-between" }}>
                    <h3>{agent.label}</h3>
                    <span className="gnode-engine" data-engine={agent.engine}>
                      {agent.engine === "model"
                        ? "model"
                        : agent.engine === "human"
                          ? "human"
                          : "code"}
                    </span>
                  </div>
                  <p className="eyebrow">{agent.layer}</p>
                  <p>{agent.summary}</p>
                </div>
              ))}
            </div>
          </Panel>
        </div>
      </div>

      <Panel
        title="Company ledger"
        eyebrow={`${data.companies.length} recorded`}
        flush
        aside={
          <Link className="btn" data-size="sm" href="/companies">
            Open ledger
          </Link>
        }
      >
        {data.companies.length === 0 ? (
          <EmptyState
            title="No company has been registered."
            detail="A Companies House number alone is enough to open a research case."
          />
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th scope="col">Company</th>
                  <th scope="col">Number</th>
                  <th scope="col">Identity</th>
                  <th scope="col">Claims</th>
                  <th scope="col">Latest run</th>
                  <th scope="col">Next action</th>
                </tr>
              </thead>
              <tbody>
                {data.companies.slice(0, 8).map((company) => (
                  <tr key={company.id}>
                    <td>
                      <Link href={`/companies/${company.id}`} style={{ fontWeight: 500 }}>
                        {company.name}
                      </Link>
                    </td>
                    <td className="mono">{company.identifier?.value ?? "—"}</td>
                    <td>
                      <Pill status={company.resolution_status} />
                    </td>
                    <td className="mono">{company.claim_count}</td>
                    <td>
                      {company.latest_run ? (
                        <Link href={`/runs/${company.latest_run.id}`} className="mono">
                          {statusLabel(company.latest_run.status)}
                        </Link>
                      ) : (
                        <span className="muted">—</span>
                      )}
                    </td>
                    <td className="muted">{company.next_action.label}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>

      {loading ? <span className="visually-hidden">Refreshing control room state</span> : null}
    </div>
  );
}
