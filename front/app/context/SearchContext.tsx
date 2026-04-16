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

  // Ref always holding the latest search params — avoids stale closure in executeSearch
  const latestRef = useRef({ query, filters, pagination, logicalQuery, searchMode, facetConfig, locale });
  // Prevents the filters/pagination useEffect from firing a second runSearch when loadSearch already called it
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
      const res = await api.permissions(validUrls);
      if (!res.ok) return;
      const data = await res.json();
      const docs: Array<{ url: string; isPermitted: boolean; formats?: string[] }> | null = data?.data?.docs ?? null;
      const org: Organization | null = data?.data?.organization ?? null;
      const purchased: boolean = org?.purchased ?? false;
      setOrganization(org);
      const map: PermissionsMap = {};
      if (!docs) {
        validUrls.forEach((url) => {
          map[url] = { status: "unknown" as PermissionStatus, formats: [] };
        });
      } else {
        docs.forEach(({ url, isPermitted, formats }) => {
          const status: PermissionStatus = !isPermitted ? "restricted" : purchased ? "institutional" : "open";
          map[url] = { status, formats: formats ?? [] };
        });
      }
      setPermissions(map);
    } catch {
      // Échec silencieux — les badges restent en état neutre
    } finally {
      setLoadingPermissions(false);
    }
  }, []);

  // Core search — reads from latestRef so it's always stable (empty deps)
  const runSearch = useCallback(async (overrides?: Partial<typeof latestRef.current>) => {
    const { query: q, filters: f, pagination: pg, logicalQuery: lq, searchMode: sm, facetConfig: fc, locale: l } = {
      ...latestRef.current,
      ...overrides,
    };

    const hasFilters = Object.values(f).some((v) => v.length > 0);
    const hasLogical = sm === "advanced" && lq && lq.rules?.length > 0;

    if (!q && !hasFilters && !hasLogical) {
      setResults([]);
      setTotal(0);
      return;
    }

    setLoading(true);
    setError(null);
    setPermissions({});
    setOrganization(null);

    try {
      const formattedFilters = Object.entries(f).flatMap(([field, values]) =>
        values.map((value) => ({ identifier: field, value }))
      );

      const body = {
        query: { query: q || "*" },
        logical_query: sm === "advanced" ? lq : null,
        filters: formattedFilters,
        facets: fc
          ? Object.keys(fc.common || {}).map(fk => ({ identifier: fk, type: "list" }))
          : [
              { identifier: "platform", type: "list" },
              { identifier: "type", type: "list" },
            ],
        pagination: { from: pg.from, size: pg.size },
      };

      const res = await api.search(body, l);

      if (!res.ok) throw new Error(res.statusText);

      const data = await res.json();
      const pageResults: SearchDoc[] = data.results || [];
      setResults(pageResults);
      setTotal(data.total || 0);
      setFacets(data.facets || {});
      // Permissions — non-bloquant, fire-and-forget
      const pageUrls = pageResults.map((d) => d.url).filter((u): u is string => !!u);
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
  const executeSearch = useCallback(() => runSearch(), [runSearch]);

  // Load a saved search: updates state + executes immediately with the new values
  const loadSearch = useCallback((data: SavedSearchData) => {
    const q = data.query ?? "";
    const f = data.filters ?? {};
    const m = data.searchMode ?? "simple";
    const lq = data.logicalQuery ?? null;
    const pg = { ...latestRef.current.pagination, from: 0 };

    // Prevent the filters/pagination useEffect from firing a redundant runSearch
    skipEffectRef.current = true;

    // Update React state (for UI consistency on next render)
    setQuery(q);
    setSearchMode(m);
    setLogicalQuery(lq);
    setFilters(f);
    setPagination(pg);

    // Patch ref immediately so runSearch sees the new values right away
    latestRef.current = { ...latestRef.current, query: q, filters: f, searchMode: m, logicalQuery: lq, pagination: pg };

    runSearch({ query: q, filters: f, searchMode: m, logicalQuery: lq, pagination: pg });
  }, [runSearch]);

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
      const cur = (prev[field] || []).filter((v) => v !== value);
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
    // Skip if loadSearch already called runSearch directly
    if (skipEffectRef.current) {
      skipEffectRef.current = false;
      return;
    }
    const hasActive =
      query || (searchMode === "advanced" && Array.isArray(logicalQuery?.rules) && logicalQuery.rules.length > 0);
    if (!hasActive) return;
    runSearch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters, pagination.from, pagination.size]);

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
