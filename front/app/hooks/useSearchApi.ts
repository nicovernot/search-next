/**
 * Orchestre les appels à /search : exécution, chargement d'une recherche sauvegardée, re-déclenchement sur filtre/page.
 * Résultat : expose `executeSearch` et `loadSearch` — stables grâce au pattern latestRef/skipEffectRef.
 */
import { useCallback, useRef, useEffect } from "react";
import { api } from "../lib/api";
import type { FullFacetConfig, SavedSearchData, SearchDoc } from "../types";
import type { useSearchState } from "./useSearchState";

interface SearchApiParams {
  searchState: ReturnType<typeof useSearchState>;
  facetConfig: FullFacetConfig | null;
  locale: string;
  fetchPermissions: (urls: string[]) => Promise<void>;
  resetPermissions: () => void;
}

export function useSearchApi({
  searchState,
  facetConfig,
  locale,
  fetchPermissions,
  resetPermissions,
}: SearchApiParams) {
  const {
    setResults, setTotal, setFacets,
    setLoading, setError,
    setQuery, setSearchMode, setLogicalQuery, setFilters, setPagination,
  } = searchState;

  // Ref always holding the latest search params — avoids stale closure in executeSearchWithOverrides
  const latestRef = useRef({
    query: searchState.query,
    filters: searchState.filters,
    pagination: searchState.pagination,
    logicalQuery: searchState.logicalQuery,
    searchMode: searchState.searchMode,
    facetConfig,
    locale,
  });

  // Prevents the filters/pagination useEffect from firing a redundant executeSearchWithOverrides
  // when loadSearch already called it directly
  const skipEffectRef = useRef(false);

  // Sync ref after every render (no deps = runs unconditionally after each render)
  useEffect(() => {
    latestRef.current = {
      query: searchState.query,
      filters: searchState.filters,
      pagination: searchState.pagination,
      logicalQuery: searchState.logicalQuery,
      searchMode: searchState.searchMode,
      facetConfig,
      locale,
    };
  });

  // Core search — reads from latestRef so it's always stable (empty deps)
  const executeSearchWithOverrides = useCallback(
    async (stateOverrides?: Partial<typeof latestRef.current>) => {
      const {
        query: searchQuery,
        filters: activeFilters,
        pagination: paginationConfig,
        logicalQuery: logicalQueryRules,
        searchMode: currentSearchMode,
        facetConfig: facetConfiguration,
        locale: currentLocale,
      } = { ...latestRef.current, ...stateOverrides };

      const hasFilters = Object.values(activeFilters).some((filterValues) => filterValues.length > 0);
      const hasLogical =
        currentSearchMode === "advanced" &&
        logicalQueryRules &&
        logicalQueryRules.rules?.length > 0;

      if (!searchQuery && !hasFilters && !hasLogical) {
        setResults([]);
        setTotal(0);
        return;
      }

      setLoading(true);
      setError(null);
      resetPermissions();

      try {
        const formattedFilters = Object.entries(activeFilters).flatMap(([field, values]) =>
          values.map((value) => ({ identifier: field, value }))
        );

        const body = {
          query: { query: searchQuery || "*" },
          logical_query: currentSearchMode === "advanced" ? logicalQueryRules : null,
          filters: formattedFilters,
          facets: facetConfiguration
            ? Object.keys(facetConfiguration.common || {}).map((fk) => ({ identifier: fk, type: "list" }))
            : [
                { identifier: "platform", type: "list" },
                { identifier: "type", type: "list" },
              ],
          pagination: { from: paginationConfig.from, size: paginationConfig.size },
        };

        const searchHttpResponse = await api.search(body, currentLocale);
        if (!searchHttpResponse.ok) throw new Error(searchHttpResponse.statusText);

        const searchResult = await searchHttpResponse.json();
        const pageResults: SearchDoc[] = searchResult.results || [];
        setResults(pageResults);
        setTotal(searchResult.total || 0);
        setFacets(searchResult.facets || {});

        // Permissions — non-bloquant, fire-and-forget
        const pageUrls = pageResults
          .map((doc) => doc.url)
          .filter((url): url is string => !!url);
        if (pageUrls.length > 0) fetchPermissions(pageUrls);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Search failed");
        setResults([]);
        setTotal(0);
      } finally {
        setLoading(false);
      }
    },
    // All deps are stable: setState dispatchers never change, fetchPermissions/resetPermissions are useCallback([])
    [setResults, setTotal, setFacets, setLoading, setError, fetchPermissions, resetPermissions]
  );

  // Public executeSearch: no args, uses latest ref (called from SearchBar, AdvancedQueryBuilder)
  const executeSearch = useCallback(
    () => executeSearchWithOverrides(),
    [executeSearchWithOverrides]
  );

  // Load a saved search: updates state + executes immediately with the new values
  const loadSearch = useCallback(
    (data: SavedSearchData) => {
      const restoredQuery = data.query ?? "";
      const restoredFilters = data.filters ?? {};
      const restoredSearchMode = data.searchMode ?? "simple";
      const restoredLogicalQuery = data.logicalQuery ?? null;
      const resetPagination = { ...latestRef.current.pagination, from: 0 };

      // Prevent the filters/pagination useEffect from firing a redundant executeSearchWithOverrides
      skipEffectRef.current = true;

      // Update React state (for UI consistency on next render)
      setQuery(restoredQuery);
      setSearchMode(restoredSearchMode);
      setLogicalQuery(restoredLogicalQuery);
      setFilters(restoredFilters);
      setPagination(resetPagination);

      // Patch ref immediately so executeSearchWithOverrides sees the new values right away
      latestRef.current = {
        ...latestRef.current,
        query: restoredQuery,
        filters: restoredFilters,
        searchMode: restoredSearchMode,
        logicalQuery: restoredLogicalQuery,
        pagination: resetPagination,
      };

      executeSearchWithOverrides({
        query: restoredQuery,
        filters: restoredFilters,
        searchMode: restoredSearchMode,
        logicalQuery: restoredLogicalQuery,
        pagination: resetPagination,
      });
    },
    [executeSearchWithOverrides, setQuery, setSearchMode, setLogicalQuery, setFilters, setPagination]
  );

  // Re-déclenche la recherche quand les filtres ou la page changent (si une recherche est active)
  useEffect(() => {
    if (skipEffectRef.current) {
      skipEffectRef.current = false;
      return;
    }
    const hasActive =
      searchState.query ||
      (searchState.searchMode === "advanced" &&
        Array.isArray(searchState.logicalQuery?.rules) &&
        searchState.logicalQuery.rules.length > 0);
    if (!hasActive) return;
    executeSearchWithOverrides();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchState.filters, searchState.pagination.from, searchState.pagination.size]);

  return { executeSearch, loadSearch };
}
