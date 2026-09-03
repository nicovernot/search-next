import pytest

from app.models.search_models import PaginationModel, QueryModel, SearchRequest
from app.services.field_config import get_qf_params
from app.services.search_builder import SearchBuilder
from app.services.solr_core_registry import SolrCoreRegistry


@pytest.fixture
def builder(tmp_path):
    (tmp_path / "documents.json").write_text(
        '{"base_url": "http://localhost:8983/solr", "default": true}'
    )
    return SearchBuilder(core_registry=SolrCoreRegistry(config_dir=tmp_path))

def test_get_qf_params_format():
    """Vérifie que get_qf_params retourne une chaîne correctement formatée"""
    qf_str = get_qf_params()
    assert "naked_titre^8.0" in qf_str
    assert "parts_titre^6.0" in qf_str
    assert "siteid^0.1" in qf_str
    # Vérifier que c'est bien séparé par des espaces
    assert " " in qf_str

def test_build_search_url_includes_qf(builder):
    """Vérifie que l'URL générée contient le paramètre qf"""
    request = SearchRequest(
        query=QueryModel(query="test"),
        filters=[],
        pagination=PaginationModel(from_=0, size=10),
        facets=[]
    )

    url = builder.build_search_url(request)

    # Vérifier la présence de qf dans l'URL
    assert "qf=" in url
    # Vérifier quelques champs spécifiques encodés ou non (urlencode encode les espaces en + ou %20)
    # On vérifie juste que la chaîne qf est présente d'une manière ou d'une autre
    # Comme c'est encodé, on peut décoder pour vérifier ou vérifier des fragments
    from urllib.parse import unquote
    decoded_url = unquote(url)
    assert "qf=naked_titre^8.0" in decoded_url
    assert "parts_titre^6.0" in decoded_url
