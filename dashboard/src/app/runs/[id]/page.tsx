"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { use, useCallback, useRef, useState } from "react";
import { AgentGraph } from "@/components/AgentGraph";
import { ClaimLedger } from "@/components/ClaimLedger";
import { Inspector, type InspectorSelection } from "@/components/Inspector";
import { ReviewGate } from "@/components/ReviewGate";
import { EmptyState, ErrorNote, NextActionBanner, Panel, Pill, Skeleton } from "@/components/ui";
import { ApiError, apiPost } from "@/lib/api";
import { formatDate, formatDuration, humanize } from "@/lib/format";
import { useElapsed, useResource } from "@/lib/hooks";
import type { GraphNode, RunPayload, SessionPayload } from "@/lib/types";

const ACTIVE_STATUSES = new Set(["pending", "running"]);
const RESTARTABLE_STATUSES = new Set(["approved", "rejected", "failed", "cancelled"]);

export default function RunPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const [selection, setSelection] = useState<InspectorSelection>(null);
  const [inflight, setInflight] = useState<{ capability: string; since: number } | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [autoStatus, setAutoStatus] = useState<string | null>(null);
  const [autoRun, setAutoRun] = useState(false);
  const [restarting, setRestarting] = useState(false);
  const abort = useRef(false);

  const session = useResource<SessionPayload>("session");
  const active = inflight !== null;
  const run = useResource<RunPayload>(`research-runs/${id}`, active ? 1500 : 0);
  const payload = run.data;

  const elapsed = useElapsed(inflight !== null, inflight?.since ?? null);

  const advance = useCallback(async (showStageError = true): Promise<RunPayload | null> => {
    if (!payload) return null;
    const capability =
      payload.nodes.find(
        (node) => node.kind === "task" && (node.status === "pending" || node.status === "failed"),
      )?.id ?? "";
    setInflight({ capability, since: Date.now() });
    setActionError(null);
    try {
      const next = await apiPost<RunPayload>(`research-runs/${id}/advance`, {});
      run.set(next);
      if (next.advance && !next.advance.ok) {
        if (showStageError) {
          setActionError(next.advance.message ?? "The stage recorded a failure.");
        }
      }
      return next;
    } catch (caught) {
      setActionError(caught instanceof ApiError ? caught.message : "The stage could not run.");
      return null;
    } finally {
      setInflight(null);
    }
  }, [id, payload, run]);

  const runToReview = useCallback(async () => {
    abort.current = false;
    setAutoRun(true);
    setAutoStatus("Starting the next persisted stage.");
    try {
      for (let step = 0; step < 12; step += 1) {
        if (abort.current) break;
        const next = await advance(false);
        if (!next) break;
        if (next.advance && !next.advance.ok) {
          if (next.advance.retryable) {
            setAutoStatus(
              `${humanize(next.advance.capability)} attempt was rejected; retrying automatically ` +
                `with ${next.advance.attempts_remaining} attempt remaining.`,
            );
            continue;
          }
          setActionError(next.advance.message ?? "The stage recorded a non-retryable failure.");
          break;
        }
        setAutoStatus(
          next.advance?.capability
            ? `${humanize(next.advance.capability)} completed. Continuing to the next stage.`
            : "Stage completed. Continuing.",
        );
        if (!ACTIVE_STATUSES.has(next.run.status)) break;
      }
    } finally {
      setAutoRun(false);
      setAutoStatus(null);
    }
  }, [advance]);

  const restartFromStageOne = useCallback(async () => {
    setRestarting(true);
    setActionError(null);
    try {
      const next = await apiPost<RunPayload>(`research-runs/${id}/restart`, {});
      router.push(`/runs/${next.run.id}`);
    } catch (caught) {
      setActionError(
        caught instanceof ApiError ? caught.message : "A fresh run could not be created.",
      );
      setRestarting(false);
    }
  }, [id, router]);

  if (run.error) return <ErrorNote message={run.error.message} />;

  if (!payload) {
    return (
      <div className="stack">
        <Skeleton lines={2} />
        <div className="panel">
          <div className="panel-body">
            <Skeleton lines={6} />
          </div>
        </div>
      </div>
    );
  }

  const { run: meta } = payload;
  const nodes: GraphNode[] = payload.nodes.map((node) =>
    inflight && node.id === inflight.capability && node.status !== "running"
      ? { ...node, status: "running", detail: "Executing now. The stage holds an exclusive claim." }
      : node,
  );
  const runnable = ACTIVE_STATUSES.has(meta.status);
  const restartable = RESTARTABLE_STATUSES.has(meta.status);
  const busy = inflight !== null || autoRun || restarting;
  const highlightSource = selection?.kind === "lane" ? selection.id : null;

  return (
    <div className="stack">
      <nav className="row" style={{ fontSize: "0.75rem", color: "var(--ink-4)" }}>
        <Link href="/">Control room</Link>
        <span aria-hidden="true">/</span>
        <Link href={`/companies/${meta.company_id}`}>{meta.company_name}</Link>
        <span aria-hidden="true">/</span>
        <span className="mono">Run</span>
      </nav>

      <header className="run-head">
        <div className="stack-sm" style={{ gap: "0.4rem", minWidth: 0 }}>
          <p className="eyebrow">Research run · {meta.company_number ?? "no number"}</p>
          <div className="row" style={{ gap: "0.7rem" }}>
            <h1 style={{ fontSize: "1.6rem" }}>{meta.company_name}</h1>
            <Pill status={meta.status} />
          </div>
          <div className="run-meta">
            <span>
              cutoff <b>{formatDate(meta.cutoff)}</b>
            </span>
            <span>
              model <b>{meta.model}</b>
            </span>
            <span>
              policy <b>{meta.source_policy_version}</b>
            </span>
            <span>
              started by <b>{meta.created_by}</b>
            </span>
          </div>
        </div>
        <div className="run-controls">
          {runnable ? (
            <>
              <button
                type="button"
                className="btn"
                data-variant="primary"
                disabled={busy}
                onClick={() => void runToReview()}
              >
                {autoRun ? "Running…" : "Run to review"}
              </button>
              <button type="button" className="btn" disabled={busy} onClick={() => void advance(true)}>
                {inflight && !autoRun ? "Executing…" : "Advance one stage"}
              </button>
              {autoRun ? (
                <button
                  type="button"
                  className="btn"
                  data-variant="danger"
                  onClick={() => {
                    abort.current = true;
                  }}
                >
                  Stop after this stage
                </button>
              ) : null}
            </>
          ) : null}
          {restartable ? (
            <button
              type="button"
              className="btn"
              data-variant="primary"
              disabled={busy}
              onClick={() => void restartFromStageOne()}
            >
              {restarting ? "Creating fresh run…" : "Restart from stage one"}
            </button>
          ) : null}
          <button type="button" className="btn" data-size="sm" onClick={() => void run.refresh()}>
            Refresh
          </button>
        </div>
      </header>

      {actionError ? <ErrorNote message={actionError} /> : null}

      {autoStatus ? (
        <div className="run-notice" role="status" aria-live="polite">
          <span className="run-notice-dot" aria-hidden="true" />
          {autoStatus}
        </div>
      ) : null}

      {inflight ? (
        <p className="mono" style={{ fontSize: "0.75rem", color: "var(--evidence)" }}>
          Executing {humanize(inflight.capability)} — the stage holds an exclusive claim on this
          run. Elapsed {formatDuration(elapsed)}.
        </p>
      ) : null}

      <AgentGraph
        nodes={nodes}
        lanes={payload.lanes}
        selection={selection}
        onSelect={setSelection}
        runningSince={inflight?.since ?? null}
      />

      <NextActionBanner label={payload.next_action.label} detail={payload.next_action.detail} />

      <div className="split">
        <div className="stack">
          {payload.contradictions.length > 0 ? (
            <Panel
              title="Contradiction ledger"
              eyebrow="Requires named resolution"
              flush
              aside={<Pill tone="human" label={`${payload.contradictions.length} open`} />}
            >
              {payload.contradictions.map((item) => (
                <div className="contradiction" key={`${item.category}-${item.subject_key}`}>
                  <div className="row">
                    <span className="eyebrow">{humanize(item.category)}</span>
                    <span className="mono muted" style={{ fontSize: "0.6875rem" }}>
                      {item.subject_key}
                    </span>
                  </div>
                  <p className="muted" style={{ fontSize: "0.8125rem" }}>
                    Different sources state different things about the same subject. Neither value
                    enters the supported summary.
                  </p>
                  <ul className="contradiction-claims">
                    {item.claims.map((claim, index) => (
                      <li key={index}>
                        {claim.statement}
                        <div className="mono muted" style={{ fontSize: "0.625rem", marginTop: "0.2rem" }}>
                          {claim.source_url}
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </Panel>
          ) : null}

          <Panel
            title={highlightSource ? "Claims from the selected source" : "Claim and evidence ledger"}
            eyebrow={`${payload.claims.length} admitted`}
            flush
            aside={
              highlightSource ? (
                <button
                  type="button"
                  className="btn"
                  data-size="sm"
                  onClick={() => setSelection(null)}
                >
                  Clear filter
                </button>
              ) : null
            }
          >
            <ClaimLedger
              claims={payload.claims}
              lanes={payload.lanes}
              highlightSourceId={highlightSource}
            />
          </Panel>

          {payload.profile ? (
            <Panel title="Human review gate" eyebrow="Named decision">
              <ReviewGate
                profile={payload.profile}
                reviewer={session.data?.system.reviewer ?? null}
                onDecided={(next) => run.set(next)}
              />
            </Panel>
          ) : (
            <Panel title="Human review gate" eyebrow="Named decision">
              <EmptyState
                title="No profile version exists yet."
                detail="Composition creates one pending-review version. Nothing can be approved or exported before that."
              />
            </Panel>
          )}
        </div>

        <div>
          <Inspector payload={payload} selection={selection} />
        </div>
      </div>
    </div>
  );
}
