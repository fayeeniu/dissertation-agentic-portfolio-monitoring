"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Overview", mark: "01" },
  { href: "/companies", label: "Companies", mark: "02" },
  { href: "/reports", label: "Reports & exports", mark: "03" },
];

export function Nav() {
  const pathname = usePathname();
  return (
    <nav className="nav" aria-label="Primary">
      <p className="nav-label">Workspace</p>
      {LINKS.map((link) => {
        const active =
          link.href === "/" ? pathname === "/" : pathname.startsWith(link.href);
        return (
          <Link key={link.href} href={link.href} aria-current={active ? "page" : undefined}>
            <span className="nav-mark" aria-hidden="true">{link.mark}</span>
            <span>{link.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
