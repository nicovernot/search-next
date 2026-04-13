"use client";

import { useState } from "react";
import { X, Filter, LayoutGrid } from "lucide-react";
import { useSearch } from "../context/SearchContext";
import { useTranslations } from "next-intl";
import ResultItem from "./ResultItem";
import Facets from "./Facets";
import Pagination from "./Pagination";
import type { FacetConfig } from "../types";

export default function ResultsList() {
  const t = useTranslations();
  const {
    results, total, loading, error, query, logicalQuery, searchMode,
    filters, removeFilter, clearFilters, facetConfig, pagination
  } = useSearch();

  const activeFilters = Object.entries(filters).flatMap(([field, values]) =>
    values.map((value) => ({ identifier: field, value }))
  );

  const FACET_I18N: Record<string, string> = {
    platform: "platform", type: "documentType", access: "access",
    translations: "languageFilter", author: "qb_fieldAuthor",
    date: "facet_date", subscribers: "facet_subscribers",
  };
  const getFacetLabel = (identifier: string) => {
    const config = facetConfig?.common?.[identifier] || facetConfig?.platform?.[identifier];
    const configName = (config as Record<string, FacetConfig> | undefined)?.[""]?.name;
    if (configName) return configName;
    const i18nKey = FACET_I18N[identifier];
    return i18nKey ? t(i18nKey) : identifier;
  };

  const hasLogicalRules = Array.isArray(logicalQuery?.rules) && logicalQuery.rules.length > 0;
  const hasQuery = searchMode === "simple" ? !!query : hasLogicalRules;
  const [activeTab, setActiveTab] = useState<"results" | "filters">("results");

  const tabClass = (tab: "results" | "filters") =>
    `text-[10px] font-bold uppercase tracking-widest transition-all duration-300 cursor-pointer pb-3 border-b-2 flex items-center gap-2 ${
      activeTab === tab
        ? "text-highlight border-highlight"
        : "text-muted-foreground border-transparent hover:text-foreground"
    }`;

  return (
    <div className="animate-in fade-in duration-700" data-testid="results-list">
      {/* Tabs */}
      <div className="flex items-center gap-10 border-b border-border mb-8">
        <button onClick={() => setActiveTab("results")} className={tabClass("results")}>
          <LayoutGrid size={14} />
          {t("resultsTitle")}
          {total > 0 && (
            <span className="ml-1 px-2 py-0.5 rounded bg-highlight text-white text-[10px] font-bold shadow-sm ring-1 ring-highlight/20">
              {total.toLocaleString()}
            </span>
          )}
        </button>
        {/* Filtres tab visible uniquement sur mobile */}
        <button onClick={() => setActiveTab("filters")} className={`${tabClass("filters")} md:hidden`}>
          <Filter size={14} />
          {t("filters")}
          {activeFilters.length > 0 && (
            <span className="w-2 h-2 rounded-full bg-highlight animate-pulse" />
          )}
        </button>
      </div>

      {/* Active Filters Summary (Chips) */}
      {!loading && activeFilters.length > 0 && (
        <div className="flex flex-wrap items-center gap-2.5 mb-8 animate-in slide-in-from-left-2 duration-300">
          <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-[0.2em] mr-1">{t("filters")}:</span>
          {activeFilters.map((f, i) => (
            <div
              key={i}
              className="group flex items-center gap-2 px-3 py-1.5 bg-card border border-border rounded-full text-[11px] hover:border-highlight/30 hover:shadow-sm transition-all"
            >
              <span className="text-muted-foreground italic font-medium">{getFacetLabel(f.identifier)}</span>
              <span className="font-bold text-foreground">{f.value}</span>
              <button
                onClick={() => removeFilter(f.identifier, f.value)}
                className="ml-1 text-muted-foreground hover:text-highlight hover:scale-110 transition-all"
                title={t("removeFilter")}
              >
                <X size={12} strokeWidth={3} />
              </button>
            </div>
          ))}
          <button
            onClick={clearFilters}
            className="text-[10px] font-bold text-highlight hover:brightness-90 ml-3 uppercase tracking-wider transition-all"
          >
            {t("resetFilters")}
          </button>
        </div>
      )}

      {/* Mobile filters panel */}
      {activeTab === "filters" && (
        <div className="md:hidden mb-8 animate-in zoom-in-95 duration-200">
          <Facets />
        </div>
      )}

      {activeTab === "results" && (
        <>
          {loading && (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="bg-card border border-border rounded-xl p-6 animate-pulse shadow-sm">
                  <div className="flex gap-3 mb-4">
                    <div className="h-5 bg-muted rounded-full w-28" />
                    <div className="h-5 bg-muted rounded-full w-20" />
                  </div>
                  <div className="h-5 bg-muted rounded-lg w-3/4 mb-3" />
                  <div className="h-4 bg-muted rounded w-full mb-2" />
                  <div className="h-4 bg-muted rounded w-11/12" />
                </div>
              ))}
            </div>
          )}

          {!loading && error && (
            <div className="bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-xl p-5 text-red-700 dark:text-red-400 text-sm flex items-center gap-3 shadow-sm">
              <div className="w-2 h-2 rounded-full bg-red-400 shrink-0" />
              {t("searchError", { error })}
            </div>
          )}

          {!loading && !error && hasQuery && results.length === 0 && (
            <div className="text-center py-24 bg-card border border-border border-dashed rounded-2xl text-muted-foreground">
              <div className="text-4xl mb-4">🔍</div>
              <p className="font-medium text-sm">{t("noResults")}</p>
              <p className="text-xs mt-2 opacity-70">{t("noResultsHint")}</p>
            </div>
          )}

          {!loading && !error && results.length > 0 && (
            <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-500">
              <div className="space-y-4">
                {results.map((doc, i) => (
                  <ResultItem key={doc.url || i} doc={doc} />
                ))}
              </div>
              {total > pagination.size && (
                <div className="pt-8 flex justify-center">
                  <Pagination total={total} />
                </div>
              )}
            </div>
          )}

          {/* Empty state — pas de requête */}
          {!loading && !error && !hasQuery && (
            <div className="text-center py-24 text-muted-foreground opacity-60">
              <div className="text-3xl mb-4 opacity-50">✨</div>
              <p className="text-sm italic">{t("searchHint")}</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
