import { NextRequest, NextResponse } from "next/server";

// Force dynamic — chaque requête doit être proxifiée, pas mise en cache
export const dynamic = "force-dynamic";

// INTERNAL_API_URL est utilisé côté serveur (route handler, Docker : http://api:8007)
// NEXT_PUBLIC_API_URL est le fallback (dev local : http://localhost:8003)
const API_BASE_URL =
  process.env.INTERNAL_API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8003";

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
  // Ne pas envoyer X-Forwarded-For si l'IP est loopback ou privée (Docker, LAN) —
  // le backend utilisera son propre fallback (TEST_IP en dev, request.client.host en prod)
  const rawIp =
    request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ||
    request.headers.get("x-real-ip");
  const isNonRoutableIp = (ip: string | null | undefined): boolean => {
    if (!ip) return true;
    return (
      ip === "127.0.0.1" ||
      ip === "::1" ||
      ip.startsWith("10.") ||
      ip.startsWith("172.16.") || ip.startsWith("172.17.") || ip.startsWith("172.18.") ||
      ip.startsWith("172.19.") || ip.startsWith("172.20.") || ip.startsWith("172.21.") ||
      ip.startsWith("172.22.") || ip.startsWith("172.23.") || ip.startsWith("172.24.") ||
      ip.startsWith("172.25.") || ip.startsWith("172.26.") || ip.startsWith("172.27.") ||
      ip.startsWith("172.28.") || ip.startsWith("172.29.") || ip.startsWith("172.30.") ||
      ip.startsWith("172.31.") ||
      ip.startsWith("192.168.")
    );
  };
  const isLoopback = isNonRoutableIp(rawIp);

  try {
    const backendUrl = `${API_BASE_URL}/permissions?urls=${encodeURIComponent(urls)}`;
    const backendResponse = await fetch(backendUrl, {
      headers: isLoopback ? {} : { "X-Forwarded-For": rawIp as string },
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
