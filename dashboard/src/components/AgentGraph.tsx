"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from "react";
import type { GraphNode, NodeStatus, SourceLane } from "@/lib/types";
import { formatDuration, shortModel, statusLabel } from "@/lib/format";
import { useElapsed, usePrefersReducedMotion } from "@/lib/hooks";

const CAPTURE_ID = "capture_sources";
const EXTRACT_ID = "extract_claims";

interface Point {
  x: number;
  y: number;
}

interface Box {
  left: number;
  right: number;
  top: number;
  bottom: number;
  cx: number;
  cy: number;
}

type Selection =
  | { kind: "node"; id: string }
  | { kind: "lane"; id: string }
  | null;

export interface AgentGraphProps {
  nodes: GraphNode[];
  lanes: SourceLane[];
  selection: Selection;
  onSelect: (selection: Selection) => void;
  /** Wall-clock start of the stage currently executing in this browser, if any. */
  runningSince: number | null;
}

function measure(element: HTMLElement, origin: DOMRect): Box {
  const rect = element.getBoundingClientRect();
  return {
    left: rect.left - origin.left,
    right: rect.right - origin.left,
    top: rect.top - origin.top,
    bottom: rect.bottom - origin.top,
    cx: rect.left - origin.left + rect.width / 2,
    cy: rect.top - origin.top + rect.height / 2,
  };
}

function spinePath(from: Box, to: Box, horizontal: boolean): string {
  if (horizontal) {
    const start: Point = { x: from.right + 4, y: from.cy };
    const end: Point = { x: to.left - 4, y: to.cy };
    const mid = (start.x + end.x) / 2;
    return `M ${start.x} ${start.y} C ${mid} ${start.y}, ${mid} ${end.y}, ${end.x} ${end.y}`;
  }
  const start: Point = { x: from.cx, y: from.bottom + 4 };
  const end: Point = { x: to.cx, y: to.top - 4 };
  const mid = (start.y + end.y) / 2;
  return `M ${start.x} ${start.y} C ${start.x} ${mid}, ${end.x} ${mid}, ${end.x} ${end.y}`;
}

function branchPath(from: Box, to: Box): string {
  const start: Point = { x: from.cx, y: from.bottom + 4 };
  const end: Point = { x: to.cx, y: to.top - 4 };
  const lift = Math.max(22, (end.y - start.y) * 0.45);
  return `M ${start.x} ${start.y} C ${start.x} ${start.y + lift}, ${end.x} ${end.y - lift}, ${end.x} ${end.y}`;
}

function returnPath(from: Box, to: Box): string {
  const start: Point = { x: from.cx, y: from.top - 4 };
  const end: Point = { x: to.cx, y: to.bottom + 4 };
  const lift = Math.max(24, (start.y - end.y) * 0.5);
  return `M ${start.x} ${start.y} C ${start.x} ${start.y - lift}, ${end.x} ${end.y + lift}, ${end.x} ${end.y}`;
}

interface Drawn {
  id: string;
  d: string;
  tone: "idle" | "armed" | "flowing" | "done" | "severed";
  role: "spine" | "branch" | "return";
  emphasised: boolean;
}

const TONE_STROKE: Record<Drawn["tone"], string> = {
  idle: "var(--rule-3)",
  armed: "var(--evidence-glow)",
  flowing: "var(--evidence)",
  done: "var(--evidence)",
  severed: "var(--danger)",
};

export function AgentGraph({
  nodes,
  lanes,
  selection,
  onSelect,
  runningSince,
}: AgentGraphProps) {
  const wrapper = useRef<HTMLDivElement | null>(null);
  const nodeRefs = useRef(new Map<string, HTMLElement>());
  const laneRefs = useRef(new Map<string, HTMLElement>());
  const [boxes, setBoxes] = useState<Map<string, Box>>(new Map());
  const [size, setSize] = useState({ width: 0, height: 0 });
  const reduced = usePrefersReducedMotion();
  const uid = useId().replace(/[^a-zA-Z0-9]/g, "");

  const remeasure = useCallback(() => {
    const host = wrapper.current;
    if (!host) return;
    const origin = host.getBoundingClientRect();
    const next = new Map<string, Box>();
    nodeRefs.current.forEach((element, key) => {
      if (element.isConnected) next.set(`node:${key}`, measure(element, origin));
    });
    laneRefs.current.forEach((element, key) => {
      if (element.isConnected) next.set(`lane:${key}`, measure(element, origin));
    });
    setBoxes(next);
    setSize({ width: origin.width, height: origin.height });
  }, []);

  useLayoutEffect(() => {
    remeasure();
  }, [remeasure, nodes, lanes]);

  useEffect(() => {
    const host = wrapper.current;
    if (!host) return;
    const observer = new ResizeObserver(() => remeasure());
    observer.observe(host);
    window.addEventListener("resize", remeasure);
    return () => {
      observer.disconnect();
      window.removeEventListener("resize", remeasure);
    };
  }, [remeasure]);

  const statusById = new Map<string, NodeStatus>(nodes.map((node) => [node.id, node.status]));
  const first = boxes.get(`node:${nodes[0]?.id ?? ""}`);
  const second = boxes.get(`node:${nodes[1]?.id ?? ""}`);
  const horizontal = first && second ? Math.abs(first.cy - second.cy) < 24 : true;

  const selectedLane = selection?.kind === "lane" ? selection.id : null;
  const selectedNode = selection?.kind === "node" ? selection.id : null;

  const drawn: Drawn[] = [];
  for (let index = 0; index < nodes.length - 1; index += 1) {
    const from = nodes[index];
    const to = nodes[index + 1];
    if (!from || !to) continue;
    const fromBox = boxes.get(`node:${from.id}`);
    const toBox = boxes.get(`node:${to.id}`);
    if (!fromBox || !toBox) continue;
    let tone: Drawn["tone"] = "idle";
    if (to.status === "running") tone = "flowing";
    else if (to.status === "failed" || to.status === "cancelled") tone = "severed";
    else if (to.status === "succeeded" || to.status === "awaiting") tone = "done";
    else if (from.status === "succeeded") tone = "armed";
    drawn.push({
      id: `spine-${from.id}-${to.id}`,
      d: spinePath(fromBox, toBox, horizontal),
      tone,
      role: "spine",
      emphasised: selectedNode === from.id || selectedNode === to.id,
    });
  }

  const captureBox = boxes.get(`node:${CAPTURE_ID}`);
  const extractBox = boxes.get(`node:${EXTRACT_ID}`);
  const captureStatus = statusById.get(CAPTURE_ID);
  // Stacked layouts put the lane band far below the fetcher; curves would then
  // cross unrelated stages, so the fan-out is drawn only when the spine is a row.
  for (const lane of horizontal ? lanes : []) {
    const laneBox = boxes.get(`lane:${lane.id}`);
    if (!laneBox || !captureBox) continue;
    const captured = lane.status === "fetched";
    const withheld = lane.status === "blocked" || lane.status === "failed";
    drawn.push({
      id: `branch-${lane.id}`,
      d: branchPath(captureBox, laneBox),
      tone:
        captureStatus === "running" && lane.status === "discovered"
          ? "flowing"
          : withheld
            ? "severed"
            : captured
              ? "done"
              : "idle",
      role: "branch",
      emphasised: selectedLane === lane.id || selectedNode === CAPTURE_ID,
    });
    if (captured && extractBox) {
      drawn.push({
        id: `return-${lane.id}`,
        d: returnPath(laneBox, extractBox),
        tone: statusById.get(EXTRACT_ID) === "running" ? "flowing" : "done",
        role: "return",
        emphasised: selectedLane === lane.id || selectedNode === EXTRACT_ID,
      });
    }
  }

  const anythingSelected = selection !== null;

  return (
    <div className="graph">
      <div className="graph-scroll">
        <div className="graph-inner" ref={wrapper}>
        <svg
          className="graph-edges"
          viewBox={`0 0 ${Math.max(size.width, 1)} ${Math.max(size.height, 1)}`}
          width={size.width || undefined}
          height={size.height || undefined}
          aria-hidden="true"
          focusable="false"
        >
          <defs>
            {drawn.map((edge) => (
              <path key={`def-${edge.id}`} id={`${uid}-${edge.id}`} d={edge.d} fill="none" />
            ))}
          </defs>
          {drawn.map((edge) => {
            const branchish = edge.role !== "spine";
            const baseOpacity = branchish ? 0.42 : 1;
            return (
              <g key={edge.id}>
                <path
                  d={edge.d}
                  fill="none"
                  stroke={TONE_STROKE[edge.tone]}
                  strokeWidth={edge.role === "spine" ? 1.4 : 1}
                  strokeDasharray={edge.tone === "idle" ? "3 5" : undefined}
                  opacity={
                    anythingSelected && !edge.emphasised
                      ? baseOpacity * 0.3
                      : edge.emphasised
                        ? 1
                        : baseOpacity
                  }
                  style={{ transition: "opacity 220ms ease, stroke 220ms ease" }}
                />
                {edge.tone === "flowing" && !reduced ? (
                  <circle r={edge.role === "spine" ? 3 : 2} fill="var(--evidence)">
                    <animateMotion
                      dur={edge.role === "spine" ? "1.5s" : "2.1s"}
                      repeatCount="indefinite"
                      rotate="auto"
                    >
                      <mpath href={`#${uid}-${edge.id}`} />
                    </animateMotion>
                    <animate
                      attributeName="opacity"
                      values="0;1;1;0"
                      dur={edge.role === "spine" ? "1.5s" : "2.1s"}
                      repeatCount="indefinite"
                    />
                  </circle>
                ) : null}
              </g>
            );
          })}
        </svg>

        <ol className="graph-spine" aria-label="Bounded agent execution sequence">
          {nodes.map((node, index) => (
            <li
              key={node.id}
              className="graph-cell"
              data-kind={node.kind}
              style={{ listStyle: "none" }}
            >
              <GraphNodeCard
                node={node}
                hasInbound={index > 0}
                hasOutbound={index < nodes.length - 1}
                selected={selectedNode === node.id}
                dimmed={anythingSelected && selectedNode !== node.id && selection?.kind === "node"}
                runningSince={runningSince}
                onSelect={() => onSelect(selectedNode === node.id ? null : { kind: "node", id: node.id })}
                register={(element) => {
                  if (element) nodeRefs.current.set(node.id, element);
                  else nodeRefs.current.delete(node.id);
                }}
              />
            </li>
          ))}
        </ol>

        {lanes.length > 0 ? (
          <section className="graph-lanes" aria-label="Source acquisition lanes">
            <div className="graph-lanes-head">
              <h3 style={{ fontSize: "0.75rem", letterSpacing: "0.08em", textTransform: "uppercase", fontFamily: "var(--mono)", color: "var(--ink-3)", fontWeight: 500 }}>
                Source lanes · {lanes.length}
              </h3>
              <p className="muted" style={{ fontSize: "0.6875rem" }}>
                One lane per discovered source. Only captured lanes return evidence to extraction.
              </p>
            </div>
            <div className="lane-grid">
              <AnimatePresence initial={false}>
                {lanes.map((lane, index) => (
                  <motion.button
                    key={lane.id}
                    type="button"
                    className="lane"
                    data-status={lane.status}
                    data-tier={lane.source_tier}
                    data-selected={selectedLane === lane.id}
                    data-dimmed={selection?.kind === "lane" && selectedLane !== lane.id}
                    initial={reduced ? false : { opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={reduced ? undefined : { opacity: 0, y: -6 }}
                    transition={{ duration: 0.28, delay: reduced ? 0 : Math.min(index * 0.03, 0.3) }}
                    onClick={() =>
                      onSelect(selectedLane === lane.id ? null : { kind: "lane", id: lane.id })
                    }
                    ref={(element) => {
                      if (element) laneRefs.current.set(lane.id, element);
                      else laneRefs.current.delete(lane.id);
                    }}
                  >
                    <span className="lane-top">
                      <span className="lane-domain">{lane.publisher_domain}</span>
                      <span className="lane-tier">
                        {lane.source_tier === "official" ? "official" : lane.source_tier === "first_party" ? "1st party" : "public"}
                      </span>
                    </span>
                    <span className="lane-meta">
                      <span className="lane-state">{statusLabel(lane.status)}</span>
                      {lane.claim_count > 0 ? <span>{lane.claim_count} claims</span> : null}
                      {lane.http_status ? <span>HTTP {lane.http_status}</span> : null}
                    </span>
                  </motion.button>
                ))}
              </AnimatePresence>
            </div>
          </section>
        ) : null}
        </div>
      </div>

      <div className="graph-legend">
        <span>
          <i style={{ background: "var(--model)" }} /> reasoning model
        </span>
        <span>
          <i style={{ background: "var(--model)", opacity: 0.45 }} /> repair model
        </span>
        <span>
          <i style={{ background: "var(--evidence)", borderRadius: 1 }} /> deterministic stage
        </span>
        <span>
          <i style={{ background: "var(--human)", transform: "rotate(45deg)", borderRadius: 0 }} /> human gate
        </span>
        <span>
          <i style={{ background: "var(--danger)" }} /> withheld or failed
        </span>
      </div>
    </div>
  );
}

interface CardProps {
  node: GraphNode;
  selected: boolean;
  dimmed: boolean;
  hasInbound: boolean;
  hasOutbound: boolean;
  runningSince: number | null;
  onSelect: () => void;
  register: (element: HTMLElement | null) => void;
}

function GraphNodeCard({
  node,
  selected,
  dimmed,
  hasInbound,
  hasOutbound,
  runningSince,
  onSelect,
  register,
}: CardProps) {
  const live = node.status === "running";
  const elapsed = useElapsed(live, runningSince);
  return (
    <button
      type="button"
      className="gnode"
      data-status={node.status}
      data-selected={selected}
      data-dimmed={dimmed}
      onClick={onSelect}
      ref={register}
      aria-pressed={selected}
    >
      {hasInbound ? <span className="gnode-port" data-side="in" aria-hidden="true" /> : null}
      {hasOutbound ? <span className="gnode-port" data-side="out" aria-hidden="true" /> : null}
      <span className="gnode-top">
        <span className="gnode-layer">{node.layer}</span>
        <span
          className="gnode-engine"
          data-engine={node.engine}
          data-tier={node.route?.tier ?? undefined}
          title={
            node.route
              ? `Routed to ${node.route.model} at ${node.route.effort} reasoning effort`
              : undefined
          }
        >
          {node.engine === "model"
            ? shortModel(node.route?.model)
            : node.engine === "human"
              ? "human"
              : "code"}
        </span>
      </span>
      <span className="gnode-label">{node.label}</span>
      <span className="gnode-detail">{node.detail}</span>
      <span className="gnode-foot">
        <span>{statusLabel(node.status)}</span>
        {live && runningSince !== null ? (
          <span className="gnode-timer">{formatDuration(elapsed)}</span>
        ) : node.duration_ms !== null ? (
          <span>{formatDuration(node.duration_ms)}</span>
        ) : node.attempts ? (
          <span>
            {node.attempts.count}/{node.attempts.max}
          </span>
        ) : null}
      </span>
    </button>
  );
}
