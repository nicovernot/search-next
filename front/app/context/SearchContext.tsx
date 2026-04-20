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
import { useUrlSync } from "../hooks/useUrlSync";

// Sous-interfaces par domaine — permet aux composants de dépendre uniquement du sous-ensemble qu'ils consomment.

interface SearchQuerySlice {
  query: string;
  setQuery: (q: string) => void;
  searchMode: "simple" | "advanced";
  setSearchMode: (m: "simple" | "advanced") => void;
  logicalQuery: LogicalQuery | null;
  setLogicalQuery: (q: LogicalQuery | null) => void;
  /** Vrai si une recherche est active (query, filtres ou requête logique non vides) */
  hasActiveSearch: boolean;
  executeSearch: () => Promise<void>;
  loadSearch: (data: SavedSearchData) => void;
}

interface SearchResultsSlice {
  results: SearchDoc[];
  total: number;
  loading: boolean;
  error: string | null;
  pagination: Pagination;
  setPage: (page: number) => void;
}

interface SearchFiltersSlice {
  facets: Facets;
  filters: Filters;
  addFilter: (field: string, value: string) => void;
  removeFilter: (field: string, value: string) => void;
  clearFilters: () => void;
  /** Filtres actifs sous forme de liste plate — calculé une seule fois depuis useSearchState */
  activeFilters: { identifier: string; value: string }[];
  facetConfig: FullFacetConfig | null;
  /** Champs de recherche avancée chargés depuis /facets/config (null = pas encore chargé) */
  searchFields: string[] | null;
}

interface SearchSuggestionsSlice {
  suggestions: string[];
  fetchSuggestions: (q: string) => Promise<void>;
  loadingSuggestions: boolean;
}

interface SearchPermissionsSlice {
  /** Statut d'accès par URL — chargé de façon asynchrone après les résultats */
  permissions: PermissionsMap;
  loadingPermissions: boolean;
  /** Organisation détectée pour l'IP courante (null si anonyme) */
  organization: Organization | null;
}

interface SearchContextValue
  extends SearchQuerySlice,
    SearchResultsSlice,
    SearchFiltersSlice,
    SearchSuggestionsSlice,
    SearchPermissionsSlice {}

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
  useUrlSync({ searchState, loadSearch });

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

/** Slice : requête, mode, logicalQuery, executeSearch, loadSearch */
export function useSearchQuery(): SearchQuerySlice {
  const ctx = useContext(SearchContext);
  if (!ctx) throw new Error("useSearchQuery must be used within SearchProvider");
  const { query, setQuery, searchMode, setSearchMode, logicalQuery, setLogicalQuery, hasActiveSearch, executeSearch, loadSearch } = ctx;
  return { query, setQuery, searchMode, setSearchMode, logicalQuery, setLogicalQuery, hasActiveSearch, executeSearch, loadSearch };
}

/** Slice : résultats, total, loading, error, pagination */
export function useSearchResults(): SearchResultsSlice {
  const ctx = useContext(SearchContext);
  if (!ctx) throw new Error("useSearchResults must be used within SearchProvider");
  const { results, total, loading, error, pagination, setPage } = ctx;
  return { results, total, loading, error, pagination, setPage };
}

/** Slice : facettes, filtres actifs, facetConfig, searchFields */
export function useSearchFilters(): SearchFiltersSlice {
  const ctx = useContext(SearchContext);
  if (!ctx) throw new Error("useSearchFilters must be used within SearchProvider");
  const { facets, filters, addFilter, removeFilter, clearFilters, activeFilters, facetConfig, searchFields } = ctx;
  return { facets, filters, addFilter, removeFilter, clearFilters, activeFilters, facetConfig, searchFields };
}

/** Slice : suggestions d'autocomplétion */
export function useSearchSuggestions(): SearchSuggestionsSlice {
  const ctx = useContext(SearchContext);
  if (!ctx) throw new Error("useSearchSuggestions must be used within SearchProvider");
  const { suggestions, fetchSuggestions, loadingSuggestions } = ctx;
  return { suggestions, fetchSuggestions, loadingSuggestions };
}

/** Slice : permissions d'accès et organisation détectée */
export function useSearchPermissions(): SearchPermissionsSlice {
  const ctx = useContext(SearchContext);
  if (!ctx) throw new Error("useSearchPermissions must be used within SearchProvider");
  const { permissions, loadingPermissions, organization } = ctx;
  return { permissions, loadingPermissions, organization };
}
