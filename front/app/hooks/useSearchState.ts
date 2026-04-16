/**
 * Centralise tout l'état de recherche (query, filters, pagination, mode, résultats) et ses mutateurs.
 * Résultat : expose les valeurs + setters bruts pour useSearchApi, plus les dérivés publics (activeFilters, hasActiveSearch).
 */
import { useState, useCallback, useMemo } from "react";
import type { SearchDoc, Facets, Filters, Pagination, LogicalQuery } from "../types";

export function useSearchState() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchDoc[]>([]);
  const [facets, setFacets] = useState<Facets>({});
  const [filters, setFilters] = useState<Filters>({});
  const [pagination, setPagination] = useState<Pagination>({ from: 0, size: 10 });
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [logicalQuery, setLogicalQuery] = useState<LogicalQuery | null>(null);
  const [searchMode, setSearchMode] = useState<"simple" | "advanced">("simple");

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

  const activeFilters = useMemo(
    () =>
      Object.entries(filters).flatMap(([field, values]) =>
        values.map((value) => ({ identifier: field, value }))
      ),
    [filters]
  );

  const hasActiveSearch = useMemo(
    () =>
      !!query ||
      activeFilters.length > 0 ||
      (searchMode === "advanced" &&
        Array.isArray(logicalQuery?.rules) &&
        logicalQuery.rules.length > 0),
    [query, activeFilters, searchMode, logicalQuery]
  );

  return {
    query, setQuery,
    results, setResults,
    facets, setFacets,
    filters, setFilters,
    pagination, setPagination,
    total, setTotal,
    loading, setLoading,
    error, setError,
    logicalQuery, setLogicalQuery,
    searchMode, setSearchMode,
    addFilter, removeFilter, clearFilters, setPage,
    activeFilters, hasActiveSearch,
  };
}
