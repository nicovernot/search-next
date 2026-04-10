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
    <div className="bg-card border border-border rounded-3xl p-6 premium-shadow sticky top-24">
      <div className="flex items-center justify-between mb-5 px-1">
        <h3 className="font-bold text-foreground tracking-tight uppercase text-xs">{t("filters")}</h3>
        {activeFilters.length > 0 && (
          <button
            onClick={clearFilters}
            className="text-[10px] font-bold text-highlight hover:text-primary transition-colors uppercase tracking-wider bg-highlight/10 px-2 py-1 rounded-full"
          >
            {t("resetFilters") || "Réinitialiser"}
          </button>
        )}
      </div>

      {activeFilters.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-6 p-3 bg-secondary/50 rounded-2xl border border-border shadow-inner">
          {activeFilters.map((f, i) => (
            <span
              key={i}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-card border border-highlight/30 text-highlight text-xs font-bold shadow-sm animate-fade-in hover:scale-105 transition-transform"
            >
              {f.value}
              <button 
                onClick={() => handleChange(f.identifier, f.value, false)} 
                className="hover:scale-125 transition-transform font-bold ml-1 text-muted-foreground hover:text-destructive"
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
