"use client";

import { useState, useEffect } from "react";

/** Retourne true uniquement côté client (après hydratation) — évite le guard SSR dupliqué */
export function useIsClient(): boolean {
  const [isClient, setIsClient] = useState(false);
  useEffect(() => { setIsClient(true); }, []);
  return isClient;
}
