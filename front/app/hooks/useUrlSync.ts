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

function parseSavedSearchData(params: URLSearchParams): SavedSearchData {
  const q = params.get("q") ?? "";
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
      // malformed lq param — ignore
    }
  }

  return {
    query: q,
    searchMode: mode,
    logicalQuery,
    filters,
    pagination: { from: (page - 1) * size, size },
  };
}

export function useUrlSync({ searchState, loadSearch }: UrlSyncParams) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const isHydrated = useRef(false);
  // Tracks the last QS string we wrote, to distinguish our writes from back/forward
  const lastWrittenQsRef = useRef<string>("");
  // Tracks previous query to decide push vs replace
  const prevQueryRef = useRef<string>("");
  // Set before calling loadSearch from back/forward, prevents spurious push
  const skipNextPushRef = useRef(false);

  // Hydrate state from URL on mount — runs only once
  useEffect(() => {
    const data = parseSavedSearchData(searchParams);
    const hasUrlState =
      data.query ||
      data.searchMode === "advanced" ||
      data.logicalQuery ||
      Object.keys(data.filters ?? {}).length > 0 ||
      (data.pagination?.from ?? 0) > 0;

    lastWrittenQsRef.current = searchParams.toString();
    prevQueryRef.current = data.query ?? "";

    if (hasUrlState) {
      skipNextPushRef.current = true;
      loadSearch(data);
    }

    isHydrated.current = true;
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Back/forward: re-hydrate when the URL changes externally (not by us)
  useEffect(() => {
    if (!isHydrated.current) return;
    const currentQs = searchParams.toString();
    if (currentQs === lastWrittenQsRef.current) return;

    skipNextPushRef.current = true;
    loadSearch(parseSavedSearchData(searchParams));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  // Keep URL in sync with state after any state change
  // New search (query changed) → pushState; refinements (filter, page, mode) → replaceState
  useEffect(() => {
    if (!isHydrated.current) return;
    const { query, searchMode, logicalQuery, filters, pagination } = searchState;
    const params = buildUrlParams(query, searchMode, logicalQuery, filters, pagination.from, pagination.size);
    const qs = params.toString();
    const url = qs ? `${pathname}?${qs}` : pathname;

    const isNewSearch = !skipNextPushRef.current && query !== prevQueryRef.current;
    skipNextPushRef.current = false;
    prevQueryRef.current = query;
    lastWrittenQsRef.current = qs;

    if (isNewSearch) {
      router.push(url, { scroll: false });
    } else {
      router.replace(url, { scroll: false });
    }
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
