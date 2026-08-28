import { NextRequest, NextResponse } from "next/server";

/**
 * Server-side proxy to the loopback FastAPI research service.
 *
 * The research service only accepts loopback clients and enforces a
 * double-submit CSRF contract. This handler is the one place that holds the
 * process token, so the browser never needs it and no request from the browser
 * ever reaches the research service directly.
 */

const ORIGIN = process.env.PORTFOLIO_API_ORIGIN ?? "http://127.0.0.1:8000";
const COOKIE_NAME = "portfolio_csrf";

let cachedToken: string | null = null;

async function readToken(force = false): Promise<string> {
  if (cachedToken && !force) return cachedToken;
  const response = await fetch(`${ORIGIN}/api/session`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Research service returned ${response.status} for the session handshake.`);
  }
  const payload = (await response.json()) as { csrf_token?: string };
  if (!payload.csrf_token) {
    throw new Error("Research service did not issue a CSRF token.");
  }
  cachedToken = payload.csrf_token;
  return cachedToken;
}

async function call(
  method: string,
  path: string,
  search: string,
  body: unknown,
  token: string,
): Promise<Response> {
  return fetch(`${ORIGIN}/api/${path}${search}`, {
    method,
    cache: "no-store",
    headers: {
      "content-type": "application/json",
      "x-csrf-token": token,
      cookie: `${COOKIE_NAME}=${token}`,
    },
    body: method === "GET" ? undefined : JSON.stringify(body ?? {}),
  });
}

async function proxy(request: NextRequest, segments: string[], method: string) {
  const path = segments.map(encodeURIComponent).join("/");
  const search = request.nextUrl.search;
  let body: unknown = undefined;
  if (method !== "GET") {
    try {
      body = await request.json();
    } catch {
      body = {};
    }
  }

  try {
    let token = await readToken();
    let payload: Record<string, unknown> | undefined;
    if (method !== "GET") {
      payload = { ...(body as Record<string, unknown>), csrf_token: token };
    }
    let upstream = await call(method, path, search, payload, token);
    if (upstream.status === 403) {
      // The research service restarts with a new process token; re-handshake once.
      token = await readToken(true);
      if (method !== "GET") {
        payload = { ...(body as Record<string, unknown>), csrf_token: token };
      }
      upstream = await call(method, path, search, payload, token);
    }
    const text = await upstream.text();
    return new NextResponse(text, {
      status: upstream.status,
      headers: {
        "content-type": upstream.headers.get("content-type") ?? "application/json",
        "cache-control": "no-store",
      },
    });
  } catch (error) {
    cachedToken = null;
    return NextResponse.json(
      {
        detail: {
          code: "service_unreachable",
          message:
            error instanceof Error
              ? `The research service at ${ORIGIN} did not respond: ${error.message}`
              : `The research service at ${ORIGIN} did not respond.`,
        },
      },
      { status: 503, headers: { "cache-control": "no-store" } },
    );
  }
}

type Context = { params: Promise<{ path: string[] }> };

export async function GET(request: NextRequest, context: Context) {
  const { path } = await context.params;
  return proxy(request, path, "GET");
}

export async function POST(request: NextRequest, context: Context) {
  const { path } = await context.params;
  return proxy(request, path, "POST");
}

export const dynamic = "force-dynamic";
