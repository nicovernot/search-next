/**
 * Fonctions pures de construction du payload envoyé à POST /search.
 * Sans dépendances React — testables sans monter un composant.
 */
import type { Filters, FullFacetConfig, LogicalQuery } from "../types";

export function buildSearchPayload(
  query: string,
  searchMode: "simple" | "advanced",
  logicalQuery: LogicalQuery | null,
  filters: Filters,
  pagination: { from: number; size: number },
  facetConfig: FullFacetConfig | null,
): object {
  const formattedFilters = Object.entries(filters).flatMap(([field, values]) =>
    values.map((value) => ({ identifier: field, value }))
  );

  const facets = facetConfig
    ? Object.keys(facetConfig.common || {}).map((fk) => ({ identifier: fk, type: "list" }))
    : [
        { identifier: "platform", type: "list" },
        { identifier: "type", type: "list" },
      ];

  return {
    query: { query: query || "*" },
    logical_query: searchMode === "advanced" ? logicalQuery : null,
    filters: formattedFilters,
    facets,
    pagination: { from: pagination.from, size: pagination.size },
  };
}

export function hasActiveSearch(
  query: string,
  filters: Filters,
  searchMode: "simple" | "advanced",
  logicalQuery: LogicalQuery | null,
): boolean {
  const hasFilters = Object.values(filters).some((values) => values.length > 0);
  const hasLogical =
    searchMode === "advanced" && logicalQuery != null && logicalQuery.rules?.length > 0;
  return !!(query || hasFilters || hasLogical);
}
