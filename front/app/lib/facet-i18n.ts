import type { FacetConfig } from "../types";

/** Mapping clés backend Solr → clés de traduction i18n */
export const FACET_I18N: Record<string, string> = {
  platform: "platform",
  type: "documentType",
  access: "access",
  translations: "languageFilter",
  author: "qb_fieldAuthor",
  date: "facet_date",
  subscribers: "facet_subscribers",
};

/**
 * Retourne le label affiché pour une facette.
 * Priorité : nom issu de la config backend → clé i18n → clé brute.
 */
export function getFacetLabel(
  key: string,
  t: (key: string) => string,
  config?: Record<string, FacetConfig>
): string {
  const configName = config?.[""]?.name;
  if (configName) return configName;
  const i18nKey = FACET_I18N[key];
  return i18nKey ? t(i18nKey) : key;
}
