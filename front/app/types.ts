import type { RuleGroupType } from "react-querybuilder";

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

/** Réponse brute de GET /facets/config — inclut search_fields en plus des groupes de facettes */
export interface FacetsConfigResponse extends Record<string, unknown> {
  search_fields?: string[];
}

export type LogicalQuery = RuleGroupType;

export interface SavedSearchData {
  query?: string;
  filters?: Filters;
  searchMode?: "simple" | "advanced";
  logicalQuery?: LogicalQuery | null;
  pagination?: Pagination;
}

export interface SavedSearchRecord {
  id: number;
  name: string;
  query_json: SavedSearchData;
  created_at: string;
}

export type PermissionStatus = "open" | "institutional" | "restricted" | "unknown";

export interface PermissionInfo {
  status: PermissionStatus;
  formats: string[];
}

export type PermissionsMap = Record<string, PermissionInfo>;

export interface Organization {
  name?: string;
  shortname?: string;
  longname?: string;
  logoUrl?: string;
  formats?: string[];
  purchased?: boolean;
}
