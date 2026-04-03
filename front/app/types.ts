export interface SearchDoc {
  url?: string;
  titre?: string;
  title?: string;
  naked_titre?: string;
  naked_resume?: string;
  naked_texte?: string;
  description?: string;
  site_title?: string;
  platformID?: string;
  type?: string;
  contributeurFacet_auteur?: string | string[];
  contributeurFacetR_auteur?: string | string[];
  anneedatepubli?: string | number;
  [key: string]: unknown;
}

export interface FacetBucket {
  key: string;
  doc_count: number;
}

export interface FacetData {
  buckets: FacetBucket[];
}

export interface Facets {
  [key: string]: FacetData;
}

export interface Filters {
  [field: string]: string[];
}

export interface Pagination {
  from: number;
  size: number;
}

export interface FacetConfigOption {
  list: string[];
}

export interface FacetConfig {
  name: string;
  type: string;
  list: string[];
  options?: Record<string, FacetConfigOption>;
}

export interface FullFacetConfig {
  [group: string]: {
    [facetName: string]: Record<string, FacetConfig>;
  };
}

export interface SearchState {
  query: string;
  results: SearchDoc[];
  facets: Facets;
  filters: Filters;
  pagination: Pagination;
  total: number;
  loading: boolean;
  error: string | null;
  facetConfig: FullFacetConfig | null;
}
