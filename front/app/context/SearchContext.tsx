"use client";

import React, { createContext, useContext, useState, useCallback, useRef } from "react";
import { useLocale } from "next-intl";
import { api } from "../lib/api";
import type {
  SearchDoc,
  Facets,
  Filters,
  Pagination,
  FullFacetConfig,
  FacetsConfigResponse,
  LogicalQuery,
  SavedSearchData,
  PermissionsMap,
  PermissionInfo,
  PermissionStatus,
  Organization,
} from "../types";

interface SearchContextValue {
  query: string;
  setQuery: (q: string) => void;
  results: SearchDoc[];
  facets: Facets;
  filters: Filters;
  addFilter: (field: string, value: string) => void;
  removeFilter: (field: string, value: string) => void;
  clearFilters: () => void;
  pagination: Pagination;
  setPage: (page: number) => void;
  total: number;
  loading: boolean;
  error: string | null;
  executeSearch: () => Promise<void>;
  loadSearch: (data: SavedSearchData) => void;
  suggestions: string[];
  fetchSuggestions: (q: string) => Promise<void>;
  loadingSuggestions: boolean;
  logicalQuery: LogicalQuery | null;
  setLogicalQuery: (q: LogicalQuery | null) => void;
  searchMode: "simple" | "advanced";
  setSearchMode: (m: "simple" | "advanced") => void;
  facetConfig: FullFacetConfig | null;
  /** Champs de recherche avancée chargés depuis /facets/config (null = pas encore chargé) */
  searchFields: string[] | null;
  /** Statut d'accès par URL — chargé de façon asynchrone après les résultats */
  permissions: PermissionsMap;
  loadingPermissions: boolean;
  /** Organisation détectée pour l'IP courante (null si anonyme) */
  organization: Organization | null;
  /** Filtres actifs sous forme de liste plate — calculé une seule fois */
  activeFilters: { identifier: string; value: string }[];
  /** Vrai si une recherche est active (query, filtres ou requête logique non vides) */
  hasActiveSearch: boolean;
}

const SearchContext = createContext<SearchContextValue | null>(null);

export function SearchProvider({ children }: { children: React.ReactNode }) {
  const locale = useLocale();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchDoc[]>([]);
  const [facets, setFacets] = useState<Facets>({});
  const [filters, setFilters] = useState<Filters>({});
  const [pagination, setPagination] = useState<Pagination>({ from: 0, size: 10 });
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [logicalQuery, setLogicalQuery] = useState<LogicalQuery | null>(null);
  const [searchMode, setSearchMode] = useState<"simple" | "advanced">("simple");
  const [facetConfig, setFacetConfig] = useState<FullFacetConfig | null>(null);
  const [searchFields, setSearchFields] = useState<string[] | null>(null);
  const [permissions, setPermissions] = useState<PermissionsMap>({});
  const [loadingPermissions, setLoadingPermissions] = useState(false);
  const [organization, setOrganization] = useState<Organization | null>(null);

  // Ref always holding the latest search params — avoids stale closure in executeSearchWithOverrides
  const latestRef = useRef({ query, filters, pagination, logicalQuery, searchMode, facetConfig, locale });
  // Prevents the filters/pagination useEffect from firing a second executeSearchWithOverrides when loadSearch already called it
  const skipEffectRef = useRef(false);

  // Sync ref after every render (no deps = runs unconditionally after each render)
  React.useEffect(() => {
    latestRef.current = { query, filters, pagination, logicalQuery, searchMode, facetConfig, locale };
  });

  // Charger la configuration des facettes + champs de recherche avancée au démarrage
  React.useEffect(() => {
    api.facetsConfig()
      .then(res => res.json())
      .then((raw: FacetsConfigResponse) => {
        const { search_fields, ...facetGroups } = raw;
        setFacetConfig(facetGroups as FullFacetConfig);
        if (Array.isArray(search_fields) && search_fields.length > 0) {
          setSearchFields(search_fields);
        }
      })
      .catch(err => console.error("Failed to load facet config", err));
  }, []);

  // Charge les statuts d'accès pour un lot d'URLs — non-bloquant, silencieux en cas d'erreur
  const fetchPermissions = useCallback(async (urls: string[]) => {
    const validUrls = urls.filter(Boolean);
    if (validUrls.length === 0) return;
    setLoadingPermissions(true);
    try {
      const permissionsHttpResponse = await api.permissions(validUrls);
      if (!permissionsHttpResponse.ok) return;
      const permissionsResult = await permissionsHttpResponse.json();
      const docs: Array<{ url: string; isPermitted: boolean; formats?: string[] }> | null = permissionsResult?.data?.docs ?? null;
      const org: Organization | null = permissionsResult?.data?.organization ?? null;
      const purchased: boolean = org?.purchased ?? false;
      setOrganization(org);
      const permissionsMap: PermissionsMap = {};
      if (!docs) {
        validUrls.forEach((url) => {
          permissionsMap[url] = { status: "unknown" as PermissionStatus, formats: [] };
        });
      } else {
        // Fallback unknown pour les URLs absentes de la réponse partielle
        validUrls.forEach((url) => {
          permissionsMap[url] = { status: "unknown" as PermissionStatus, formats: [] };
        });
        docs.forEach(({ url, isPermitted, formats }) => {
          const status: PermissionStatus = !isPermitted ? "restricted" : purchased ? "institutional" : "open";
          permissionsMap[url] = { status, formats: formats ?? [] };
        });
      }
      setPermissions(permissionsMap);
    } catch {
      // Échec silencieux — les badges restent en état neutre
    } finally {
      setLoadingPermissions(false);
    }
  }, []);

  // Core search — reads from latestRef so it's always stable (empty deps)
  const executeSearchWithOverrides = useCallback(async (stateOverrides?: Partial<typeof latestRef.current>) => {
    const {
      query: searchQuery,
      filters: activeFilters,
      pagination: paginationConfig,
      logicalQuery: logicalQueryRules,
      searchMode: currentSearchMode,
      facetConfig: facetConfiguration,
      locale: currentLocale,
    } = {
      ...latestRef.current,
      ...stateOverrides,
    };

    const hasFilters = Object.values(activeFilters).some((filterValues) => filterValues.length > 0);
    const hasLogical = currentSearchMode === "advanced" && logicalQueryRules && logicalQueryRules.rules?.length > 0;

    if (!searchQuery && !hasFilters && !hasLogical) {
      setResults([]);
      setTotal(0);
      return;
    }

    setLoading(true);
    setError(null);
    setPermissions({});
    setOrganization(null);

    try {
      const formattedFilters = Object.entries(activeFilters).flatMap(([field, values]) =>
        values.map((value) => ({ identifier: field, value }))
      );

      const body = {
        query: { query: searchQuery || "*" },
        logical_query: currentSearchMode === "advanced" ? logicalQueryRules : null,
        filters: formattedFilters,
        facets: facetConfiguration
          ? Object.keys(facetConfiguration.common || {}).map(fk => ({ identifier: fk, type: "list" }))
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
      const pageUrls = pageResults.map((doc) => doc.url).filter((url): url is string => !!url);
      if (pageUrls.length > 0) fetchPermissions(pageUrls);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
      setResults([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, []); // Stable forever — reads from ref

  // Public executeSearch: no args, uses latest ref (called from SearchBar, AdvancedQueryBuilder)
  const executeSearch = useCallback(() => executeSearchWithOverrides(), [executeSearchWithOverrides]);

  // Load a saved search: updates state + executes immediately with the new values
  const loadSearch = useCallback((data: SavedSearchData) => {
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
  }, [executeSearchWithOverrides]);

  const addFilter = useCallback((field: string, value: string) => {
    setFilters((prev) => {
      const cur = prev[field] || [];
      if (cur.includes(value)) return prev;
      return { ...prev, [field]: [...cur, value] };
    });
    setPagination((p) => ({ ...p, from: 0 }));
  }, []);

  const removeFilter = useCallback((field: string, value: string) => {
    setFilters((prev) => {
      const cur = (prev[field] || []).filter((existingValue) => existingValue !== value);
      if (cur.length === 0) {
        const next = { ...prev };
        delete next[field];
        return next;
      }
      return { ...prev, [field]: cur };
    });
    setPagination((p) => ({ ...p, from: 0 }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({});
    setPagination((p) => ({ ...p, from: 0 }));
  }, []);

  const setPage = useCallback((page: number) => {
    setPagination((p) => ({ ...p, from: (page - 1) * p.size }));
  }, []);

  // Re-déclenche la recherche quand les filtres ou la page changent (si une recherche est active)
  React.useEffect(() => {
    // Skip if loadSearch already called executeSearchWithOverrides directly
    if (skipEffectRef.current) {
      skipEffectRef.current = false;
      return;
    }
    const hasActive =
      query || (searchMode === "advanced" && Array.isArray(logicalQuery?.rules) && logicalQuery.rules.length > 0);
    if (!hasActive) return;
    executeSearchWithOverrides();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters, pagination.from, pagination.size]);

  const activeFilters = React.useMemo(
    () => Object.entries(filters).flatMap(([field, values]) => values.map((value) => ({ identifier: field, value }))),
    [filters]
  );

  const hasActiveSearch = React.useMemo(
    () => !!query || activeFilters.length > 0 || (searchMode === "advanced" && Array.isArray(logicalQuery?.rules) && logicalQuery.rules.length > 0),
    [query, activeFilters, searchMode, logicalQuery]
  );

  const fetchSuggestions = useCallback(async (q: string) => {
    if (!q || q.length < 2) {
      setSuggestions([]);
      return;
    }

    setLoadingSuggestions(true);
    try {
      const res = await api.suggest(q);
      if (!res.ok) throw new Error("Failed to fetch suggestions");
      const data = await res.json();
      setSuggestions(data.suggestions || []);
    } catch (err) {
      console.error("Suggestions error:", err);
      setSuggestions([]);
    } finally {
      setLoadingSuggestions(false);
    }
  }, []);

  return (
    <SearchContext.Provider
      value={{
        query, setQuery, results, facets, filters,
        addFilter, removeFilter, clearFilters,
        pagination, setPage, total, loading, error,
        executeSearch, loadSearch,
        suggestions, fetchSuggestions, loadingSuggestions,
        logicalQuery, setLogicalQuery, searchMode, setSearchMode,
        facetConfig, searchFields,
        permissions, loadingPermissions, organization,
        activeFilters, hasActiveSearch,
      }}
    >
      {children}
    </SearchContext.Provider>
  );
}

export function useSearch() {
  const ctx = useContext(SearchContext);
  if (!ctx) throw new Error("useSearch must be used within SearchProvider");
  return ctx;
}
