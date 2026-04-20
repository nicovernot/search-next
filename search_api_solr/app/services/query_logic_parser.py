
from app.models.logical_query import QueryGroup, QueryRule

# Normalise les noms d'opérateurs envoyés par react-querybuilder (camelCase) vers les noms internes
_OPERATOR_ALIASES: dict[str, str] = {
    "beginswith": "begins_with",
    "endswith": "ends_with",
    "doesnotcontain": "does_not_contain",
    "doesnotbeginwith": "does_not_begin_with",
    "doesnotendwith": "does_not_end_with",
    "!=": "not_equal",
    "isnot": "not_equal",
}


class QueryLogicParser:
    @staticmethod
    def convert_to_solr_query_string(item: QueryRule | QueryGroup | dict) -> str:
        """
        Convertit récursivement une QueryGroup ou QueryRule (ou dict) en chaîne de requête Solr.
        """
        if isinstance(item, dict):
            # Tenter de convertir en Rule ou Group
            if "rules" in item:
                item = QueryGroup(**item)
            else:
                item = QueryRule(**item)

        if isinstance(item, QueryRule):
            return QueryLogicParser._build_solr_rule_fragment(item)
        elif isinstance(item, QueryGroup):
            return QueryLogicParser._build_solr_group_fragment(item)
        return ""

    @staticmethod
    def _build_solr_rule_fragment(rule: QueryRule) -> str:
        from app.services.facet_config import COMMON_FACETS_MAPPING, SEARCH_FIELDS_MAPPING

        field = SEARCH_FIELDS_MAPPING.get(rule.field,
                COMMON_FACETS_MAPPING.get(rule.field, rule.field))

        op = _OPERATOR_ALIASES.get(rule.operator.lower(), rule.operator.lower())
        val = rule.value

        if op in ("=", "is"):
            return f'{field}:"{val}"'
        elif op == "not_equal":
            return f'-{field}:"{val}"'
        elif op == "contains":
            if rule.field in SEARCH_FIELDS_MAPPING:
                return f'{field}:{val}'
            return f'{field}:*{val}*'
        elif op == "does_not_contain":
            if rule.field in SEARCH_FIELDS_MAPPING:
                return f'-{field}:{val}'
            return f'-{field}:*{val}*'
        elif op == "begins_with":
            return f'{field}:{val}*'
        elif op == "does_not_begin_with":
            return f'-{field}:{val}*'
        elif op == "ends_with":
            return f'{field}:*{val}'
        elif op == "does_not_end_with":
            return f'-{field}:*{val}'
        else:
            return f'{field}:{val}'

    @staticmethod
    def _build_solr_group_fragment(group: QueryGroup) -> str:
        if not group.rules:
            return ""

        parsed_rules = []
        for rule in group.rules:
            # Pydantic Union peut avoir besoin de discrimination manuelle ou isinstance
            # Ici on utilise la méthode statique récursive
            solr_rule = QueryLogicParser.convert_to_solr_query_string(rule)
            if solr_rule:
                parsed_rules.append(solr_rule)

        if not parsed_rules:
            return ""

        combinator = f" {group.combinator.upper()} "
        solr_rules_joined = combinator.join(parsed_rules)

        solr_group_fragment = f"({solr_rules_joined})"
        if group.not_:
            solr_group_fragment = f"NOT {solr_group_fragment}"

        return solr_group_fragment
