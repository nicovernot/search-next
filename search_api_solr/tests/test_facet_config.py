"""
Tests pour la configuration des facettes
"""

import pytest
from app.services.facet_config import (
    COMMON_FACETS_MAPPING,
    FACET_SUBCATEGORIES,
    PLATFORM_SPECIFIC_FACETS,
    get_filter_values,
    FACET_CONFIG,
)


class TestFacetConfiguration:
    """Tests pour le chargement de la configuration des facettes"""

    def test_facet_config_loaded(self):
        """Vérifie que les fichiers JSON sont chargés"""
        assert "common" in FACET_CONFIG
        assert "books" in FACET_CONFIG
        assert "journals" in FACET_CONFIG
        assert "hypotheses" in FACET_CONFIG
        assert "calenda" in FACET_CONFIG

    def test_common_facets_mapping(self):
        """Vérifie que les facettes communes sont chargées"""
        assert "platform" in COMMON_FACETS_MAPPING
        assert COMMON_FACETS_MAPPING["platform"] == "platformID"

        assert "type" in COMMON_FACETS_MAPPING
        assert COMMON_FACETS_MAPPING["type"] == "type"

        assert "author" in COMMON_FACETS_MAPPING
        assert COMMON_FACETS_MAPPING["author"] == "contributeurFacetR_auteur"

    def test_facet_subcategories_loaded(self):
        """Vérifie que les sous-catégories sont chargées"""
        assert "type" in FACET_SUBCATEGORIES

        # Vérifier quelques sous-catégories
        type_subcats = FACET_SUBCATEGORIES["type"]
        assert "livre" in type_subcats
        assert type_subcats["livre"] == ["livre"]

        assert "article" in type_subcats
        assert type_subcats["article"] == ["article", "articlepdf"]

        assert "compterendu" in type_subcats
        assert len(type_subcats["compterendu"]) == 7

    def test_platform_specific_facets(self):
        """Vérifie que les facettes spécifiques par plateforme sont chargées"""
        assert "OB" in PLATFORM_SPECIFIC_FACETS
        assert "site_title" in PLATFORM_SPECIFIC_FACETS["OB"]

        assert "OJ" in PLATFORM_SPECIFIC_FACETS
        assert "site_title" in PLATFORM_SPECIFIC_FACETS["OJ"]

        assert "HO" in PLATFORM_SPECIFIC_FACETS
        assert "site_title" in PLATFORM_SPECIFIC_FACETS["HO"]


class TestGetFilterValues:
    """Tests pour la fonction get_filter_values"""

    def test_simple_value_no_subcategory(self):
        """Test avec une valeur simple sans sous-catégorie"""
        result = get_filter_values("platform", "OB")
        assert result == ["OB"]

    def test_subcategory_single_value(self):
        """Test avec une sous-catégorie à valeur unique"""
        result = get_filter_values("type", "livre")
        assert result == ["livre"]

    def test_subcategory_multiple_values(self):
        """Test avec une sous-catégorie à valeurs multiples"""
        result = get_filter_values("type", "article")
        assert result == ["article", "articlepdf"]

    def test_subcategory_complex(self):
        """Test avec une sous-catégorie complexe (7 valeurs)"""
        result = get_filter_values("type", "compterendu")
        assert len(result) == 7
        assert "compterendu" in result
        assert "notedelecture" in result
        assert "noticebibliolivre" in result

    def test_unknown_facet(self):
        """Test avec une facette inconnue"""
        result = get_filter_values("unknown", "value")
        assert result == ["value"]

    def test_unknown_subcategory_value(self):
        """Test avec une valeur de sous-catégorie inconnue"""
        result = get_filter_values("type", "unknown_type")
        assert result == ["unknown_type"]
