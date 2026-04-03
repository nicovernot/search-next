"use client";

import { useSearch } from "../context/SearchContext";
import { useTranslations } from "../context/I18nContext";
import FacetGroup from "./FacetGroup";

export default function Facets() {
  const { facets, filters, addFilter, removeFilter, clearFilters, facetConfig } = useSearch();
  const { t } = useTranslations();

  const activeFilters = Object.entries(filters).flatMap(([field, values]) =>
    values.map((value) => ({ identifier: field, value }))
  );

  // Générer les configurations de facettes dynamiquement à partir du backend
  const dynamicFacetConfigs = facetConfig?.common 
    ? Object.entries(facetConfig.common).map(([key, config]) => ({
        key,
        label: (config as any)[""]?.name || t(key as any) || key
      }))
    : [
        { key: "platform", label: t("platform") },
        { key: "type", label: t("documentType") },
      ];

  const handleChange = (field: string, value: string, checked: boolean) => {
    checked ? addFilter(field, value) : removeFilter(field, value);
  };

  return (
    <div className="bg-white border border-[#e6e4e2] rounded-xl p-5 shadow-sm sticky top-24">
      <div className="flex items-center justify-between mb-5 px-1">
        <h3 className="font-bold text-[rgba(16,13,13,1)] tracking-tight uppercase text-xs">{t("filters")}</h3>
        {activeFilters.length > 0 && (
          <button
            onClick={clearFilters}
            className="text-[10px] font-bold text-[#f03603] hover:text-[#d23003] transition-colors uppercase tracking-wider"
          >
            {t("resetFilters") || "Réinitialiser"}
          </button>
        )}
      </div>

      {activeFilters.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-6 p-2.5 bg-[#f9f6f4] rounded-lg border border-[#e6e4e2]/50 shadow-inner">
          {activeFilters.map((f, i) => (
            <span
              key={i}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white border border-[#f03603]/20 text-[#f03603] text-xs font-medium shadow-sm animate-in fade-in zoom-in duration-200"
            >
              {f.value}
              <button 
                onClick={() => handleChange(f.identifier, f.value, false)} 
                className="hover:scale-125 transition-transform font-bold"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}

      <div className="space-y-2">
        {dynamicFacetConfigs.map((config) => {
          const data = facets[config.key];
          if (!data?.buckets?.length) return null;
          return (
            <FacetGroup
              key={config.key}
              label={config.label}
              field={config.key}
              buckets={data.buckets}
              activeFilters={activeFilters}
              onFilterChange={handleChange}
            />
          );
        })}
      </div>
    </div>
  );
}
