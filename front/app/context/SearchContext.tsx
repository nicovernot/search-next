"use client";

import React, { createContext, useContext } from "react";
import { useLocale } from "next-intl";
import type {
  SearchDoc, Facets, Filters, Pagination, FullFacetConfig,
  LogicalQuery, SavedSearchData, PermissionsMap, Organization,
} from "../types";
import { useFacetConfig } from "../hooks/useFacetConfig";
import { useSuggestions } from "../hooks/useSuggestions";
import { usePermissions } from "../hooks/usePermissions";
import { useSearchState } from "../hooks/useSearchState";
import { useSearchApi } from "../hooks/useSearchApi";

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
  const { facetConfig, searchFields } = useFacetConfig();
  const { suggestions, fetchSuggestions, loadingSuggestions } = useSuggestions();
  const { permissions, loadingPermissions, organization, fetchPermissions, resetPermissions } = usePermissions();
  const searchState = useSearchState();
  const { executeSearch, loadSearch } = useSearchApi({
    searchState, facetConfig, locale, fetchPermissions, resetPermissions,
  });

  return (
    <SearchContext.Provider
      value={{
        query: searchState.query, setQuery: searchState.setQuery,
        results: searchState.results, facets: searchState.facets,
        filters: searchState.filters,
        addFilter: searchState.addFilter, removeFilter: searchState.removeFilter,
        clearFilters: searchState.clearFilters,
        pagination: searchState.pagination, setPage: searchState.setPage,
        total: searchState.total, loading: searchState.loading, error: searchState.error,
        logicalQuery: searchState.logicalQuery, setLogicalQuery: searchState.setLogicalQuery,
        searchMode: searchState.searchMode, setSearchMode: searchState.setSearchMode,
        activeFilters: searchState.activeFilters, hasActiveSearch: searchState.hasActiveSearch,
        facetConfig, searchFields,
        suggestions, fetchSuggestions, loadingSuggestions,
        permissions, loadingPermissions, organization,
        executeSearch, loadSearch,
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
