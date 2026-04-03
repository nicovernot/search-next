"use client";

import { useState, useMemo } from "react";
import { ChevronDown, ChevronUp, Search, X } from "lucide-react";
import type { FacetBucket } from "../types";
import { useTranslations } from "../context/I18nContext";

interface FacetGroupProps {
  label: string;
  field: string;
  buckets: FacetBucket[];
  activeFilters: { identifier: string; value: string }[];
  onFilterChange: (field: string, value: string, checked: boolean) => void;
}

export default function FacetGroup({ label, field, buckets, activeFilters, onFilterChange }: FacetGroupProps) {
  const { t } = useTranslations();
  const [expanded, setExpanded] = useState(true);
  const [showAll, setShowAll] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  const maxVisible = 6;

  const filteredBuckets = useMemo(() => {
    if (!searchTerm) return buckets;
    return buckets.filter(b => 
      b.key.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [buckets, searchTerm]);

  const visible = showAll ? filteredBuckets : filteredBuckets.slice(0, maxVisible);

  const isChecked = (value: string) =>
    activeFilters.some((f) => f.identifier === field && f.value === value);

  return (
    <div className="group/facet border-b border-[#e6e4e2] pb-6 mb-2 last:border-0">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full text-left mb-3 group-hover/facet:translate-x-0.5 transition-transform"
      >
        <span className="text-xs font-bold text-[rgba(16,13,13,1)] uppercase tracking-wider">{label}</span>
        <div className={`transition-transform duration-300 ${expanded ? "rotate-0" : "-rotate-180"}`}>
          <ChevronDown size={14} className="text-[#969493]" />
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
                className="w-full pl-8 pr-8 py-1.5 text-xs bg-[#f9f6f4] border border-[#e6e4e2] rounded-md focus:outline-none focus:ring-1 focus:ring-[#f03603]/30 focus:border-[#f03603]/50 transition-all"
              />
              <Search size={12} className="absolute left-2.5 top-2.5 text-[#969493]" />
              {searchTerm && (
                <button 
                  onClick={() => setSearchTerm("")}
                  className="absolute right-2.5 top-2.5 text-[#969493] hover:text-[#f03603]"
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
                        className="peer w-4 h-4 appearance-none border border-[#e6e4e2] rounded checked:bg-[#f03603] checked:border-[#f03603] transition-all cursor-pointer"
                      />
                      <div className="absolute opacity-0 peer-checked:opacity-100 pointer-events-none transition-opacity">
                        <svg width="10" height="8" viewBox="0 0 10 8" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M1 4L4 7L9 1" />
                        </svg>
                      </div>
                    </div>
                    <span className={`text-sm flex-1 truncate transition-colors ${
                      isChecked(bucket.key) ? "text-[#f03603] font-medium" : "text-[#4a4848] group-hover/item:text-[rgba(16,13,13,1)]"
                    }`}>
                      {bucket.key}
                    </span>
                    <span className={`text-[10px] tabular-nums px-1.5 py-0.5 rounded-full transition-colors ${
                      isChecked(bucket.key) ? "bg-[#f03603]/10 text-[#f03603]" : "bg-[#f9f6f4] text-[#969493]"
                    }`}>
                      {bucket.doc_count.toLocaleString()}
                    </span>
                  </label>
                </li>
              ))
            ) : (
              <li className="text-xs text-[#969493] italic py-2">
                Aucun résultat pour "{searchTerm}"
              </li>
            )}

            {filteredBuckets.length > maxVisible && (
              <li>
                <button
                  onClick={() => setShowAll(!showAll)}
                  className="flex items-center gap-1 text-xs font-semibold text-[#f03603] hover:text-[#d23003] mt-2 transition-colors"
                >
                  {showAll ? (
                    <>Voir moins <ChevronUp size={12} /></>
                  ) : (
                    <>Voir plus ({filteredBuckets.length - maxVisible}) <ChevronDown size={12} /></>
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
