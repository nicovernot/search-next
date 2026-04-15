/**
 * Champs disponibles dans le QueryBuilder avancé.
 * Modifier ici pour ajouter/retirer un champ de recherche avancée
 * sans toucher au composant AdvancedQueryBuilder.
 *
 * `name`     — identifiant Solr du champ
 * `labelKey` — clé i18n dans messages/*.json
 */
export interface QBFieldDef {
  name: string;
  labelKey: string;
}

export const QB_FIELDS: QBFieldDef[] = [
  { name: "titre", labelKey: "qb_fieldTitle" },
  { name: "author", labelKey: "qb_fieldAuthor" },
  { name: "naked_texte", labelKey: "qb_fieldFullText" },
  { name: "disciplinary_field", labelKey: "qb_fieldKeywords" },
];
