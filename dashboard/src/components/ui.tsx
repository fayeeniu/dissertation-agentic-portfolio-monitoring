"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { statusLabel, statusTone } from "@/lib/format";

export function Pill({
  status,
  tone,
  label,
}: {
  status?: string;
  tone?: string;
  label?: string;
}) {
  const resolved = tone ?? (status ? statusTone(status) : "idle");
  return (
    <span className="pill" data-tone={resolved}>
      {label ?? (status ? statusLabel(status) : "—")}
    </span>
  );
}

export function Panel({
  title,
  eyebrow,
  aside,
  children,
  flush = false,
}: {
  title: string;
  eyebrow?: string;
  aside?: ReactNode;
  children: ReactNode;
  flush?: boolean;
}) {
  return (
    <section className="panel">
      <header className="panel-head">
        <div className="stack-sm" style={{ gap: "0.15rem", minWidth: 0 }}>
          {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
          <h2>{title}</h2>
        </div>
        {aside ? <div className="row" style={{ flex: "none" }}>{aside}</div> : null}
      </header>
      <div className={flush ? "panel-body flush" : "panel-body"}>{children}</div>
    </section>
  );
}

export function StatRail({
  items,
}: {
  items: { label: string; value: string | number; tone?: string }[];
}) {
  return (
    <div className="stat-rail">
      {items.map((item) => (
        <div className="stat" key={item.label}>
          <span className="stat-value" data-tone={item.tone ?? undefined}>
            {item.value}
          </span>
          <span className="stat-label">{item.label}</span>
        </div>
      ))}
    </div>
  );
}

export function NextActionBanner({
  label,
  detail,
  href,
  action,
}: {
  label: string;
  detail: string;
  href?: string | null;
  action?: ReactNode;
}) {
  return (
    <div className="next-action">
      <div className="next-action-copy stack-sm" style={{ gap: "0.1rem" }}>
        <p className="eyebrow">Next safe action</p>
        <p className="next-action-title">{label}</p>
        <p className="muted" style={{ fontSize: "0.8125rem" }}>
          {detail}
        </p>
      </div>
      {action ??
        (href ? (
          <Link className="btn" href={href}>
            Open
          </Link>
        ) : null)}
    </div>
  );
}

export function EmptyState({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="empty stack-sm" style={{ alignItems: "center" }}>
      <p style={{ color: "var(--ink-2)", fontSize: "0.875rem" }}>{title}</p>
      <p style={{ maxWidth: "42ch" }}>{detail}</p>
    </div>
  );
}

export function ErrorNote({ message }: { message: string }) {
  return (
    <div
      role="alert"
      style={{
        padding: "0.7rem 0.9rem",
        borderRadius: "var(--r-sm)",
        border: "1px solid rgba(242, 112, 93, 0.34)",
        background: "var(--danger-wash)",
        color: "var(--danger)",
        fontSize: "0.8125rem",
      }}
    >
      {message}
    </div>
  );
}

export function Skeleton({ lines = 3 }: { lines?: number }) {
  return (
    <div className="stack-sm" aria-hidden="true">
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          style={{
            height: "0.85rem",
            borderRadius: "var(--r-xs)",
            background:
              "linear-gradient(90deg, var(--neutral-wash), rgba(24,34,30,0.07), var(--neutral-wash))",
            backgroundSize: "200% 100%",
            animation: "shimmer 1.4s linear infinite",
            width: index === lines - 1 ? "60%" : "100%",
          }}
        />
      ))}
      <style>{`@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}`}</style>
    </div>
  );
}
