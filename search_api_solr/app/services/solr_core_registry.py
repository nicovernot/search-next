# app/services/solr_core_registry.py
"""
Registre des cores Solr configurés.

Un core = un fichier JSON dans `solr_cores/`, nommé par le core
(`<nom>.json`), contenant `{"base_url": "...", "default": true|false}`.
Même patron de chargement que `facet_config.py::load_facet_config_from_json`.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.core.exceptions import SolrCoreNotFoundError
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class SolrCoreDefinition:
    """Une entrée de configuration pour un core Solr interrogeable."""

    name: str
    base_url: str
    is_default: bool


def _load_core_definitions(config_dir: Path) -> dict[str, SolrCoreDefinition]:
    cores: dict[str, SolrCoreDefinition] = {}
    if not config_dir.exists():
        return cores

    for file_path in sorted(config_dir.glob("*.json")):
        name = file_path.stem
        with open(file_path, encoding="utf-8") as f:
            raw = json.load(f)

        base_url = raw.get("base_url")
        if not base_url:
            raise ValueError(
                f"Solr core config '{file_path}' is missing a non-empty 'base_url'"
            )

        cores[name] = SolrCoreDefinition(
            name=name,
            base_url=base_url,
            is_default=bool(raw.get("default", False)),
        )

    return cores


class SolrCoreRegistry:
    """Résout un nom de core vers sa définition, à partir de la configuration chargée."""

    _cores: dict[str, SolrCoreDefinition]

    def __init__(self, config_dir: Path | None = None):
        config_dir = config_dir or (Path(__file__).parent / "solr_cores")
        self._cores = _load_core_definitions(config_dir)
        self._validate()

        logger.info(
            "Solr core registry loaded",
            extra={
                "context": {
                    "cores": sorted(self._cores.keys()),
                    "default_core": self.default_core_name,
                }
            },
        )

    def _validate(self) -> None:
        if not self._cores:
            raise ValueError(
                "Solr core registry is empty — at least one core must be "
                + "configured in app/services/solr_cores/*.json"
            )

        defaults = [c.name for c in self._cores.values() if c.is_default]
        if len(defaults) != 1:
            raise ValueError(
                f"Solr core registry must have exactly one default core (found {len(defaults)}: {defaults})"
            )

    @property
    def cores(self) -> dict[str, SolrCoreDefinition]:
        return dict(self._cores)

    @property
    def default_core_name(self) -> str:
        return next(c.name for c in self._cores.values() if c.is_default)

    def resolve(self, core: str | None) -> SolrCoreDefinition:
        """Résout un nom de core explicite, ou retourne le core par défaut si `core` est None."""
        if core is None:
            return self._cores[self.default_core_name]
        try:
            return self._cores[core]
        except KeyError:
            raise SolrCoreNotFoundError(core) from None
