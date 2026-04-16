import { useState, useEffect } from "react";
import { api } from "../lib/api";
import type { FullFacetConfig, FacetsConfigResponse } from "../types";

export function useFacetConfig() {
  const [facetConfig, setFacetConfig] = useState<FullFacetConfig | null>(null);
  const [searchFields, setSearchFields] = useState<string[] | null>(null);

  useEffect(() => {
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

  return { facetConfig, searchFields };
}
