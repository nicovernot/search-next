"use client";

import { useEffect, useRef } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import type { useSearchState } from "./useSearchState";
import type { SavedSearchData } from "../types";
import { buildUrlParams, parseSavedSearchData } from "../lib/url-search-state";

interface UrlSyncParams {
  searchState: ReturnType<typeof useSearchState>;
  loadSearch: (data: SavedSearchData) => void;
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
  const { query, searchMode, logicalQuery, filters, pagination } = searchState;
  useEffect(() => {
    if (!isHydrated.current) return;
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
  }, [query, searchMode, logicalQuery, filters, pagination, pathname, router]);
}
