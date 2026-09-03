"""
Tests pour SolrCoreRegistry
"""
import pytest

from app.core.exceptions import SolrCoreNotFoundError
from app.services.solr_core_registry import SolrCoreRegistry


def _write_core(tmp_path, name: str, base_url: str, default: bool = False):
    content = '{"base_url": "%s"%s}' % (
        base_url,
        ', "default": true' if default else "",
    )
    (tmp_path / f"{name}.json").write_text(content)


class TestSolrCoreRegistry:
    """Tests unitaires du registre (FR-007)"""

    def test_empty_registry_fails_to_load(self, tmp_path):
        """Une configuration vide DOIT échouer clairement au démarrage."""
        with pytest.raises(ValueError):
            SolrCoreRegistry(config_dir=tmp_path)

    def test_missing_directory_fails_to_load(self, tmp_path):
        """Un dossier de config absent est équivalent à une configuration vide."""
        with pytest.raises(ValueError):
            SolrCoreRegistry(config_dir=tmp_path / "does-not-exist")

    def test_no_default_core_fails_to_load(self, tmp_path):
        """Aucun core marqué `default: true` DOIT échouer au démarrage."""
        _write_core(tmp_path, "documents", "https://solr.example.org/solr/documents")
        with pytest.raises(ValueError):
            SolrCoreRegistry(config_dir=tmp_path)

    def test_two_default_cores_fails_to_load(self, tmp_path):
        """Deux cores marqués `default: true` DOIVENT échouer au démarrage (ambiguïté)."""
        _write_core(tmp_path, "documents", "https://solr.example.org/solr/documents", default=True)
        _write_core(tmp_path, "journals", "https://solr.example.org/solr/journals", default=True)
        with pytest.raises(ValueError):
            SolrCoreRegistry(config_dir=tmp_path)

    def test_missing_base_url_fails_to_load(self, tmp_path):
        """Un core sans `base_url` DOIT échouer au démarrage."""
        (tmp_path / "broken.json").write_text('{"default": true}')
        with pytest.raises(ValueError):
            SolrCoreRegistry(config_dir=tmp_path)

    def test_resolve_none_returns_default_core(self, tmp_path):
        """`resolve(None)` retourne le core par défaut (FR-003)."""
        _write_core(tmp_path, "documents", "https://solr.example.org/solr/documents", default=True)
        _write_core(tmp_path, "journals", "https://solr.example.org/solr/journals")

        registry = SolrCoreRegistry(config_dir=tmp_path)

        assert registry.default_core_name == "documents"
        assert registry.resolve(None).base_url == "https://solr.example.org/solr/documents"

    def test_resolve_known_core_returns_its_definition(self, tmp_path):
        """`resolve("journals")` retourne la définition exacte de ce core (FR-003)."""
        _write_core(tmp_path, "documents", "https://solr.example.org/solr/documents", default=True)
        _write_core(tmp_path, "journals", "https://solr.example.org/solr/journals")

        registry = SolrCoreRegistry(config_dir=tmp_path)

        resolved = registry.resolve("journals")
        assert resolved.name == "journals"
        assert resolved.base_url == "https://solr.example.org/solr/journals"
        assert resolved.is_default is False

    def test_resolve_unknown_core_raises_not_found(self, tmp_path):
        """`resolve("inconnu")` lève `SolrCoreNotFoundError` (FR-004)."""
        _write_core(tmp_path, "documents", "https://solr.example.org/solr/documents", default=True)
        registry = SolrCoreRegistry(config_dir=tmp_path)

        with pytest.raises(SolrCoreNotFoundError) as exc_info:
            registry.resolve("inconnu")
        assert exc_info.value.core_name == "inconnu"

    def test_cores_property_lists_all_configured_cores(self, tmp_path):
        """FR-008/US4 — le registre liste bien tous les cores actifs."""
        _write_core(tmp_path, "documents", "https://solr.example.org/solr/documents", default=True)
        _write_core(tmp_path, "journals", "https://solr.example.org/solr/journals")
        _write_core(tmp_path, "books", "https://solr.example.org/solr/books")

        registry = SolrCoreRegistry(config_dir=tmp_path)

        assert set(registry.cores.keys()) == {"documents", "journals", "books"}
        assert registry.default_core_name == "documents"

    def test_startup_log_lists_cores_and_default(self, tmp_path, caplog):
        """FR-008/US4 — le chargement journalise la liste des cores et le core par défaut."""
        _write_core(tmp_path, "documents", "https://solr.example.org/solr/documents", default=True)
        _write_core(tmp_path, "journals", "https://solr.example.org/solr/journals")

        with caplog.at_level("INFO"):
            SolrCoreRegistry(config_dir=tmp_path)

        messages = [r.message for r in caplog.records if r.name == "app.services.solr_core_registry"]
        assert any("Solr core registry loaded" in m for m in messages)
        record = next(
            r for r in caplog.records if "Solr core registry loaded" in r.message
        )
        assert record.context["default_core"] == "documents"
        assert set(record.context["cores"]) == {"documents", "journals"}

    def test_real_migrated_config_loads_successfully(self):
        """La configuration réelle migrée (app/services/solr_cores/) doit rester valide."""
        registry = SolrCoreRegistry()

        assert "documents" in registry.cores
        assert registry.default_core_name == "documents"


class TestSharedRegistryAcrossServices:
    """US3/FR-006 — SearchBuilder, SuggestService et PermissionsService partagent
    la même instance de SolrCoreRegistry (pas de résolution indépendante)."""

    def test_search_builder_and_permissions_service_share_the_singleton(self):
        from app.api.dependencies import (
            _solr_core_registry,
            get_permissions_service,
            get_search_builder,
        )

        builder = get_search_builder(registry=_solr_core_registry)
        permissions_service = get_permissions_service(registry=_solr_core_registry)

        assert builder.core_registry is _solr_core_registry
        assert permissions_service.core_registry is _solr_core_registry

    def test_suggest_service_builder_shares_the_singleton(self):
        from app.api.dependencies import (
            _solr_core_registry,
            get_search_builder,
            get_solr_client,
            get_suggest_service,
        )

        builder = get_search_builder(registry=_solr_core_registry)
        suggest_service = get_suggest_service(builder=builder, solr_client=get_solr_client())

        assert suggest_service.builder.core_registry is _solr_core_registry
