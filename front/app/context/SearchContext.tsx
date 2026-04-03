"use client";

import React, { createContext, useContext, useState, useCallback } from "react";
import type { SearchDoc, Facets, Filters, Pagination, FullFacetConfig } from "../types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8007";



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
  suggestions: string[];
  fetchSuggestions: (q: string) => Promise<void>;
  loadingSuggestions: boolean;
  logicalQuery: any;
  setLogicalQuery: (q: any) => void;
  searchMode: "simple" | "advanced";
  setSearchMode: (m: "simple" | "advanced") => void;
  facetConfig: FullFacetConfig | null;
}

const SearchContext = createContext<SearchContextValue | null>(null);

export function SearchProvider({ children }: { children: React.ReactNode }) {
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
  const [logicalQuery, setLogicalQuery] = useState<any>(null);
  const [searchMode, setSearchMode] = useState<"simple" | "advanced">("simple");
  const [facetConfig, setFacetConfig] = useState<FullFacetConfig | null>(null);

  // Charger la configuration des facettes au démarrage
  React.useEffect(() => {
    fetch(`${API_BASE_URL}/facets/config`)
      .then(res => res.json())
      .then(config => setFacetConfig(config))
      .catch(err => console.error("Failed to load facet config", err));
  }, []);

  const executeSearch = useCallback(async () => {
    const hasFilters = Object.values(filters).some((v) => v.length > 0);
    const hasLogical = searchMode === "advanced" && logicalQuery && logicalQuery.rules.length > 0;
    
    if (!query && !hasFilters && !hasLogical) {
      setResults([]);
      setTotal(0);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formattedFilters = Object.entries(filters).flatMap(([field, values]) =>
        values.map((value) => ({ identifier: field, value }))
      );

      const body = {
        query: { query: query || "*" },
        logical_query: searchMode === "advanced" ? logicalQuery : null,
        filters: formattedFilters,
        facets: facetConfig 
          ? Object.keys(facetConfig.common || {}).map(f => ({ identifier: f, type: "list" }))
          : [
            { identifier: "platform", type: "list" },
            { identifier: "type", type: "list" },
          ],
        pagination: { from: pagination.from, size: pagination.size },
      };

      const lang =
        typeof navigator !== "undefined"
          ? (navigator.language || "en").split("-")[0]
          : "en";

      const res = await fetch(`${API_BASE_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept-Language": lang },
        body: JSON.stringify(body),
      });

      if (!res.ok) throw new Error(res.statusText);

      const data = await res.json();
      setResults(data.results || []); // Backend returns 'results' and 'total'
      setTotal(data.total || 0);

      const rawFacets = data.facets || {};
      const transformed: Facets = {};
      // Simplifié : le backend renvoie déjà un format plus propre ou on adapte
      setFacets(rawFacets);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
      setResults([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [query, filters, pagination, logicalQuery, searchMode, facetConfig]);

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
        const { [field]: _, ...rest } = prev;
        return rest;
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

  const fetchSuggestions = useCallback(async (q: string) => {
    if (!q || q.length < 2) {
      setSuggestions([]);
      return;
    }

    setLoadingSuggestions(true);
    try {
      const res = await fetch(`${API_BASE_URL}/suggest?q=${encodeURIComponent(q)}`);
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
        pagination, setPage, total, loading, error, executeSearch,
        suggestions, fetchSuggestions, loadingSuggestions,
        logicalQuery, setLogicalQuery, searchMode, setSearchMode,
        facetConfig,
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
