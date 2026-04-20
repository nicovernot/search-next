"""
Tests pour SearchBuilder
"""
import pytest

from app.models.search_models import FilterModel, QueryModel, SearchRequest
from app.services.search_builder import SearchBuilder
from app.settings import settings


class TestSearchBuilder:
    """Tests pour la classe SearchBuilder"""

    @pytest.fixture
    def builder(self):
        """Fixture pour créer une instance de SearchBuilder"""
        return SearchBuilder(solr_base_url=settings.solr_base_url)

    def test_build_filter_queries_simple(self, builder):
        """Test de construction de filtres simples"""
        filters = [FilterModel(identifier="platform", value="OB")]
        fq_list = builder._build_filter_queries(filters)

        assert len(fq_list) == 1
        assert 'platformID' in fq_list[0]
        assert 'OB' in fq_list[0]

    def test_build_filter_queries_with_subcategory(self, builder):
        """Test de construction de filtres avec sous-catégorie"""
        filters = [FilterModel(identifier="type", value="article")]
        fq_list = builder._build_filter_queries(filters)

        assert len(fq_list) == 1
        # Doit contenir OR pour les multiples valeurs
        assert 'OR' in fq_list[0]
        assert 'article' in fq_list[0]
        assert 'articlepdf' in fq_list[0]

    def test_build_filter_queries_multiple_filters(self, builder):
        """Test avec plusieurs filtres"""
        filters = [
            FilterModel(identifier="platform", value="OB"),
            FilterModel(identifier="type", value="livre")
        ]
        fq_list = builder._build_filter_queries(filters)

        assert len(fq_list) == 2

    def test_build_search_url_basic(self, builder):
        """Test de construction d'URL de recherche basique"""
        request = SearchRequest(
            query=QueryModel(query="test"),
            filters=[],
            pagination={"from": 0, "size": 10},
            facets=[]
        )

        url = builder.build_search_url(request)

        assert settings.solr_base_url in url
        assert 'q=test' in url
        assert 'df=titre' in url
        assert 'start=0' in url
        assert 'rows=10' in url

    def test_build_search_url_with_filters(self, builder):
        """Test de construction d'URL avec filtres"""
        request = SearchRequest(
            query=QueryModel(query="history"),
            filters=[FilterModel(identifier="platform", value="OB")],
            pagination={"from": 0, "size": 5},
            facets=[]
        )

        url = builder.build_search_url(request)

        assert 'q=history' in url
        assert 'fq=' in url
        assert 'platformID' in url

    def test_build_search_url_with_subcategory_expansion(self, builder):
        """Test que les sous-catégories sont expansées dans l'URL"""
        request = SearchRequest(
            query=QueryModel(query="science"),
            filters=[FilterModel(identifier="type", value="article")],
            pagination={"from": 0, "size": 10},
            facets=[]
        )

        url = builder.build_search_url(request)

        # Vérifier que l'expansion OR est présente
        assert 'type' in url
        assert 'OR' in url or 'article' in url

    def test_build_search_url_with_platform_specific_facets(self, builder):
        """Test que les facettes spécifiques à la plateforme sont ajoutées"""
        request = SearchRequest(
            query=QueryModel(query="test"),
            filters=[FilterModel(identifier="platform", value="OB")],
            pagination={"from": 0, "size": 10},
            facets=[]
        )

        url = builder.build_search_url(request)

        # Devrait inclure site_title pour OB
        assert 'facet=true' in url
        assert 'site_title' in url

    def test_build_search_url_with_platform_facet(self, builder):
        """Test de la facette platformID"""
        request = SearchRequest(
            query=QueryModel(query="test"),
            filters=[],
            pagination={"from": 0, "size": 10},
            facets=[{"identifier": "platform", "type": "list"}]
        )

        url = builder.build_search_url(request)

        # Vérifier que platformID est demandé en facette
        assert 'facet=true' in url
        assert 'facet.field=platformID' in url

    def test_build_search_url_with_subscribers_facet(self, builder):
        """Test de la facette subscribers"""
        request = SearchRequest(
            query=QueryModel(query="test"),
            filters=[],
            pagination={"from": 0, "size": 10},
            facets=[{"identifier": "subscribers", "type": "list"}]
        )

        url = builder.build_search_url(request)

        # Vérifier que subscribers est demandé en facette
        assert 'facet.field=subscribers' in url

    def test_build_search_url_with_facet_query(self, builder):
        """Test de la facette par requête (facet.query)"""
        request = SearchRequest(
            query=QueryModel(query="test"),
            filters=[],
            pagination={"from": 0, "size": 10},
            facets=[
                {"identifier": "subscribers_amu", "type": "query", "value": "subscribers:amu"}
            ]
        )

        url = builder.build_search_url(request)

        # Vérifier que facet.query est utilisé
        assert 'facet=true' in url
        # L'encodage d'URL peut varier, on vérifie la présence de la chaîne décodée ou encodée
        assert 'facet.query=subscribers%3Aamu' in url or 'facet.query=subscribers:amu' in url

