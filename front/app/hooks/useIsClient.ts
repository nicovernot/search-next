"use client";

import { useSyncExternalStore } from "react";

/** Retourne true uniquement côté client (après hydratation) — évite le guard SSR dupliqué */
export function useIsClient(): boolean {
  return useSyncExternalStore(
    () => () => {},
    () => true,
    () => false,
  );
}
