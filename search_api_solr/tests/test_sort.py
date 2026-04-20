import pytest

from app.models.search_models import PaginationModel, QueryModel, SearchRequest
from app.services.search_builder import SearchBuilder


@pytest.fixture
def builder():
    return SearchBuilder("http://localhost:8983/solr")

def test_build_search_url_with_sort(builder):
    """Vérifie que l'URL générée contient le paramètre sort"""
    request = SearchRequest(
        query=QueryModel(query="test"),
        filters=[],
        pagination=PaginationModel(from_=0, size=10),
        facets=[],
        sort="anneedatepubli desc"
    )

    url = builder.build_search_url(request)

    # Vérifier la présence de sort dans l'URL
    assert "sort=" in url

    from urllib.parse import unquote_plus
    decoded_url = unquote_plus(url)
    assert "sort=anneedatepubli desc" in decoded_url

def test_build_search_url_without_sort(builder):
    """Vérifie que l'URL générée ne contient pas sort par défaut"""
    request = SearchRequest(
        query=QueryModel(query="test"),
        filters=[],
        pagination=PaginationModel(from_=0, size=10),
        facets=[]
    )

    url = builder.build_search_url(request)
    assert "sort=" not in url
