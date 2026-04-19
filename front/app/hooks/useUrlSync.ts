"use client";

import { useEffect, useRef } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import type { useSearchState } from "./useSearchState";
import type { SavedSearchData, LogicalQuery, Filters } from "../types";

interface UrlSyncParams {
  searchState: ReturnType<typeof useSearchState>;
  loadSearch: (data: SavedSearchData) => void;
}

function buildUrlParams(
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

function readFiltersFromParams(params: URLSearchParams): Filters {
  const filters: Filters = {};
  for (const [key, value] of params.entries()) {
    if (!key.startsWith("f_")) continue;
    const field = key.slice(2);
    filters[field] = [...(filters[field] ?? []), value];
  }
  return filters;
}

export function useUrlSync({ searchState, loadSearch }: UrlSyncParams) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const isHydrated = useRef(false);

  // Hydrate state from URL on mount — runs only once
  useEffect(() => {
    const q = searchParams.get("q") ?? "";
    const mode = searchParams.get("mode") === "advanced" ? "advanced" : "simple";
    const lqRaw = searchParams.get("lq");
    const page = Math.max(1, parseInt(searchParams.get("page") ?? "1", 10));
    const size = Math.max(1, parseInt(searchParams.get("size") ?? "10", 10));
    const filters = readFiltersFromParams(searchParams);

    const hasUrlState =
      q || mode === "advanced" || lqRaw || Object.keys(filters).length > 0 || page > 1;

    if (hasUrlState) {
      let logicalQuery: LogicalQuery | null = null;
      if (lqRaw) {
        try {
          logicalQuery = JSON.parse(lqRaw);
        } catch {
          // malformed lq param — ignore
        }
      }
      loadSearch({
        query: q,
        searchMode: mode,
        logicalQuery,
        filters,
        pagination: { from: (page - 1) * size, size },
      });
    }

    isHydrated.current = true;
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Keep URL in sync with state — skipped until after hydration
  useEffect(() => {
    if (!isHydrated.current) return;
    const { query, searchMode, logicalQuery, filters, pagination } = searchState;
    const params = buildUrlParams(query, searchMode, logicalQuery, filters, pagination.from, pagination.size);
    const qs = params.toString();
    router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
  }, [
    searchState.query,
    searchState.searchMode,
    searchState.logicalQuery,
    searchState.filters,
    searchState.pagination,
    pathname,
    router,
  ]);
}
