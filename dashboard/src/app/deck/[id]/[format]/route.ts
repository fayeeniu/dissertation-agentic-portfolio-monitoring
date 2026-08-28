import { NextResponse } from "next/server";

const ORIGIN = process.env.PORTFOLIO_API_ORIGIN ?? "http://127.0.0.1:8000";

/** Streams an approved profile deck from the research service's export route. */
export async function GET(
  _request: Request,
  context: { params: Promise<{ id: string; format: string }> },
) {
  const { id, format } = await context.params;
  if (format !== "json" && format !== "html") {
    return NextResponse.json({ detail: "Unknown deck format." }, { status: 404 });
  }
  const upstream = await fetch(
    `${ORIGIN}/profile-versions/${encodeURIComponent(id)}/deck/${format}`,
    { cache: "no-store" },
  );
  const body = await upstream.text();
  return new NextResponse(body, {
    status: upstream.status,
    headers: {
      "content-type": upstream.headers.get("content-type") ?? "text/plain",
      "cache-control": "no-store",
    },
  });
}

export const dynamic = "force-dynamic";
