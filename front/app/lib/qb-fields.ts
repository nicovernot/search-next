/**
 * Registre des labels i18n pour les champs du QueryBuilder avancé.
 *
 * `QB_LABELS_MAP`  — mappe un nom de champ Solr vers une clé i18n.
 *                    Utilisé pour traduire les champs chargés depuis l'API.
 *
 * `QB_FIELDS`      — liste de fallback utilisée quand /facets/config est indisponible.
 *                    Modifier ici pour ajouter/retirer un champ sans toucher au composant.
 *
 * `name`     — identifiant Solr du champ (doit correspondre à SEARCH_FIELDS_MAPPING backend)
 * `labelKey` — clé i18n dans messages/*.json
 */

export interface QBFieldDef {
  name: string;
  labelKey: string;
}

export const QB_LABELS_MAP: Record<string, string> = {
  titre: "qb_fieldTitle",
  author: "qb_fieldAuthor",
  naked_texte: "qb_fieldFullText",
};

export const QB_FIELDS: QBFieldDef[] = Object.entries(QB_LABELS_MAP).map(
  ([name, labelKey]) => ({ name, labelKey })
);
