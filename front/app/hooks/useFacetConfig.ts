/**
 * Charge la configuration des facettes et les champs de recherche avancée depuis /facets/config au démarrage.
 * Résultat : expose `facetConfig` (groupes de facettes) et `searchFields` (champs QB) — null tant que non chargés.
 */
import { useState, useEffect } from "react";
import { api } from "../lib/api";
import { logger } from "../lib/logger";
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
      .catch(() => logger.error("Failed to load facet config"));
  }, []);

  return { facetConfig, searchFields };
}
