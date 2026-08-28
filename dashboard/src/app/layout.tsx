import type { Metadata, Viewport } from "next";
import Link from "next/link";
import { Nav } from "@/components/Nav";
import { BoundaryTag } from "@/components/BoundaryTag";
import "@/styles/globals.css";
import "@/styles/graph.css";

export const metadata: Metadata = {
  title: "Research control room",
  description:
    "Operating surface for a bounded multi-agent company research workflow with named human approval.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#f4f6f3",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <a className="skip-link" href="#main">
          Skip to main content
        </a>
        <div className="shell">
          <aside className="sidebar">
            <Link className="brand" href="/">
              <svg className="brand-mark" viewBox="0 0 26 26" aria-hidden="true" focusable="false">
                <circle cx="4.5" cy="13" r="2.3" fill="currentColor" />
                <circle cx="13" cy="5" r="2.3" fill="currentColor" opacity="0.75" />
                <circle cx="13" cy="21" r="2.3" fill="currentColor" opacity="0.75" />
                <circle
                  cx="21.5"
                  cy="13"
                  r="2.6"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                />
                <path
                  d="M6.6 11.4 10.9 6.9M6.6 14.6 10.9 19.1M15.1 6.9 19.4 11.4M15.1 19.1 19.4 14.6"
                  stroke="currentColor"
                  strokeWidth="1.1"
                  fill="none"
                  opacity="0.55"
                />
              </svg>
              <span className="brand-copy">
                <span className="brand-name">Research control room</span>
                <span className="brand-sub">Evidence-first company intelligence</span>
              </span>
            </Link>
            <Nav />
            <div className="sidebar-note">
              <p className="eyebrow">Research contract</p>
              <p>Every report is traceable to captured public evidence and a named review.</p>
            </div>
            <BoundaryTag />
          </aside>
          <div className="workspace">
            <header className="masthead">
              <div>
                <p className="eyebrow">Company intelligence</p>
                <p className="workspace-title">Investment research workbench</p>
              </div>
              <span className="masthead-spacer" />
              <Link className="btn" data-size="sm" href="/companies">
                New company
              </Link>
            </header>
            <main id="main" tabIndex={-1}>
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
