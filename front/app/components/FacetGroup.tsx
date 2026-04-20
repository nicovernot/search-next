"use client";

import { useState, useMemo } from "react";
import { ChevronDown, ChevronUp, Search, X } from "lucide-react";
import type { FacetBucket } from "../types";
import { useTranslations } from "next-intl";

interface FacetGroupProps {
  label: string;
  field: string;
  buckets: FacetBucket[];
  activeFilters: { identifier: string; value: string }[];
  onFilterChange: (field: string, value: string, checked: boolean) => void;
}

export default function FacetGroup({ label, field, buckets, activeFilters, onFilterChange }: FacetGroupProps) {
  const t = useTranslations();
  const [expanded, setExpanded] = useState(true);
  const [showAll, setShowAll] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  const maxVisible = 6;

  const filteredBuckets = useMemo(() => {
    if (!searchTerm) return buckets;
    return buckets.filter(bucket =>
      bucket.key.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [buckets, searchTerm]);

  const visible = showAll ? filteredBuckets : filteredBuckets.slice(0, maxVisible);

  const isChecked = (value: string) =>
    activeFilters.some((activeFilter) => activeFilter.identifier === field && activeFilter.value === value);

  return (
    <div className="group/facet border-b border-border pb-6 mb-2 last:border-0">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full text-left mb-3 group-hover/facet:translate-x-0.5 transition-transform"
      >
        <span className="text-xs font-bold text-foreground uppercase tracking-wider">{label}</span>
        <div className={`transition-transform duration-300 ${expanded ? "rotate-0" : "-rotate-180"}`}>
          <ChevronDown size={14} className="text-muted-foreground" />
        </div>
      </button>

      {expanded && (
        <div className="space-y-3 animate-in slide-in-from-top-1 duration-200">
          {/* Recherche interne pour les facettes avec beaucoup de choix */}
          {buckets.length > 10 && (
            <div className="relative mb-3">
              <input
                type="text"
                placeholder={t("searchFilters") || "Filtrer..."}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-8 pr-8 py-1.5 text-xs bg-secondary border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-highlight/30 focus:border-highlight/50 transition-all text-secondary-foreground"
              />
              <Search size={12} className="absolute left-2.5 top-2.5 text-muted-foreground" />
              {searchTerm && (
                <button 
                  onClick={() => setSearchTerm("")}
                  className="absolute right-2.5 top-2.5 text-muted-foreground hover:text-highlight"
                >
                  <X size={12} />
                </button>
              )}
            </div>
          )}

          <ul className="space-y-2">
            {visible.length > 0 ? (
              visible.map((bucket) => (
                <li key={bucket.key}>
                  <label className="flex items-center gap-2.5 cursor-pointer group/item">
                    <div className="relative flex items-center justify-center">
                      <input
                        type="checkbox"
                        checked={isChecked(bucket.key)}
                        onChange={(e) => onFilterChange(field, bucket.key, e.target.checked)}
                        className="peer w-4 h-4 appearance-none border border-border rounded checked:bg-highlight checked:border-highlight transition-all cursor-pointer"
                      />
                      <div className="absolute opacity-0 peer-checked:opacity-100 pointer-events-none transition-opacity">
                        <svg width="10" height="8" viewBox="0 0 10 8" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M1 4L4 7L9 1" />
                        </svg>
                      </div>
                    </div>
                    <span className={`text-sm flex-1 truncate transition-colors ${
                      isChecked(bucket.key) ? "text-highlight font-medium" : "text-foreground/80 group-hover/item:text-foreground"
                    }`}>
                      {bucket.key}
                    </span>
                    <span className={`text-[10px] tabular-nums px-1.5 py-0.5 rounded-full transition-colors ${
                      isChecked(bucket.key) ? "bg-highlight/10 text-highlight font-bold" : "bg-secondary text-muted-foreground"
                    }`}>
                      {bucket.doc_count.toLocaleString()}
                    </span>
                  </label>
                </li>
              ))
            ) : (
              <li className="text-xs text-muted-foreground italic py-2">
                {t("noFacetResults", { term: searchTerm })}
              </li>
            )}

            {filteredBuckets.length > maxVisible && (
              <li>
                <button
                  onClick={() => setShowAll(!showAll)}
                  className="flex items-center gap-1 text-xs font-semibold text-highlight hover:text-primary mt-2 transition-colors"
                >
                  {showAll ? (
                    <>{t("showLess")} <ChevronUp size={12} /></>
                  ) : (
                    <>{t("showMore", { count: filteredBuckets.length - maxVisible })} <ChevronDown size={12} /></>
                  )}
                </button>
              </li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}
