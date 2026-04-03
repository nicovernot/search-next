from typing import Union
from app.models.logical_query import QueryRule, QueryGroup

class QueryLogicParser:
    @staticmethod
    def to_solr_query(item: Union[QueryRule, QueryGroup, dict]) -> str:
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
            return QueryLogicParser._parse_rule(item)
        elif isinstance(item, QueryGroup):
            return QueryLogicParser._parse_group(item)
        return ""

    @staticmethod
    def _parse_rule(rule: QueryRule) -> str:
        from app.services.facet_config import SEARCH_FIELDS_MAPPING, COMMON_FACETS_MAPPING
        
        # 1. Priorité au mapping des champs de recherche (Advanced Search)
        # 2. Repli vers le mapping des facettes
        field = SEARCH_FIELDS_MAPPING.get(rule.field, 
                COMMON_FACETS_MAPPING.get(rule.field, rule.field))
        
        op = rule.operator.lower()
        val = rule.value

        # Échappement des caractères spéciaux si nécessaire (simplifié ici)
        # On entoure de guillemets pour les recherches exactes sur champs de facettes
        if op == "=" or op == "is":
            return f'{field}:"{val}"'
        
        elif op == "contains":
            # Si le champ est un champ de recherche tokenisé (mappé), 
            # une recherche par terme simple est plus efficace qu'un wildcard.
            if rule.field in SEARCH_FIELDS_MAPPING:
                return f'{field}:{val}'
            # Sinon, pour les champs de facettes ou littéraux, wildcard.
            return f'{field}:*{val}*'
            
        elif op == "begins_with":
            return f'{field}:{val}*'
        elif op == "ends_with":
            return f'{field}:*{val}'
        else:
            # Par défaut, recherche par terme
            return f'{field}:{val}'

    @staticmethod
    def _parse_group(group: QueryGroup) -> str:
        if not group.rules:
            return ""
        
        parsed_rules = []
        for rule in group.rules:
            # Pydantic Union peut avoir besoin de discrimination manuelle ou isinstance
            # Ici on utilise la méthode statique récursive
            res = QueryLogicParser.to_solr_query(rule)
            if res:
                parsed_rules.append(res)
        
        if not parsed_rules:
            return ""

        combinator = f" {group.combinator.upper()} "
        joined = combinator.join(parsed_rules)
        
        query = f"({joined})"
        if group.not_:
            query = f"NOT {query}"
            
        return query
