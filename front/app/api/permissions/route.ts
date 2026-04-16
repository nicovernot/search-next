import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8003";

/**
 * Route handler proxy pour /permissions.
 * Relaie la requête vers le backend FastAPI en injectant l'IP réelle
 * de l'utilisateur via X-Forwarded-For — ce que le browser ne peut pas faire directement.
 */
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const urls = searchParams.get("urls");

  if (!urls) {
    return NextResponse.json({ error: "urls parameter is required" }, { status: 400 });
  }

  // Lire l'IP réelle depuis les headers de l'infrastructure (Nginx, Cloudflare, etc.)
  const realUserIp =
    request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ||
    request.headers.get("x-real-ip") ||
    "127.0.0.1";

  try {
    const backendUrl = `${API_BASE_URL}/permissions?urls=${encodeURIComponent(urls)}`;
    const backendResponse = await fetch(backendUrl, {
      headers: {
        "X-Forwarded-For": realUserIp,
      },
    });

    const permissionsResult = await backendResponse.json();
    return NextResponse.json(permissionsResult, { status: backendResponse.status });
  } catch {
    return NextResponse.json(
      { data: { organization: null, docs: null }, info: { error: "permissions_proxy_failed" } },
      { status: 502 }
    );
  }
}
