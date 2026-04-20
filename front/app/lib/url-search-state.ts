/**
 * Fonctions pures de sérialisation/désérialisation de l'état de recherche dans l'URL.
 * Intentionnellement sans dépendances React — testables sans monter un composant.
 *
 * Intention : encoder de façon stable toutes les dimensions de l'état de recherche
 * (query, mode, logicalQuery, filters, pagination) dans des paramètres URL lisibles.
 * Résultat : URLs partageables, back/forward natif, hydratation SSR sans flash.
 */
import type { Filters, LogicalQuery, SavedSearchData } from "../types";

export function buildUrlParams(
  query: string,
  searchMode: "simple" | "advanced",
  logicalQuery: LogicalQuery | null,
  filters: Filters,
  from: number,
  size: number,
): URLSearchParams {
  const params = new URLSearchParams();
  if (query) params.set("q", query);
  if (searchMode === "advanced") params.set("mode", "advanced");
  if (searchMode === "advanced" && logicalQuery) params.set("lq", JSON.stringify(logicalQuery));
  for (const [field, values] of Object.entries(filters)) {
    for (const value of values) params.append(`f_${field}`, value);
  }
  const page = Math.floor(from / size) + 1;
  if (page > 1) params.set("page", String(page));
  if (size !== 10) params.set("size", String(size));
  return params;
}

export function readFiltersFromParams(params: URLSearchParams): Filters {
  const filters: Filters = {};
  for (const [key, value] of params.entries()) {
    if (!key.startsWith("f_")) continue;
    const field = key.slice(2);
    filters[field] = [...(filters[field] ?? []), value];
  }
  return filters;
}

export function parseSavedSearchData(params: URLSearchParams): SavedSearchData {
  const query = params.get("q") ?? "";
  const mode = params.get("mode") === "advanced" ? "advanced" : "simple";
  const lqRaw = params.get("lq");
  const page = Math.max(1, parseInt(params.get("page") ?? "1", 10));
  const size = Math.max(1, parseInt(params.get("size") ?? "10", 10));
  const filters = readFiltersFromParams(params);

  let logicalQuery: LogicalQuery | null = null;
  if (lqRaw) {
    try {
      logicalQuery = JSON.parse(lqRaw);
    } catch {
      // malformed lq param — ignore silently
    }
  }

  return {
    query,
    searchMode: mode,
    logicalQuery,
    filters,
    pagination: { from: (page - 1) * size, size },
  };
}
