"""
Configuration centralisée du logging structuré pour l'application.

À appeler une seule fois au démarrage via setup_logging(log_level).
Tous les loggers applicatifs propagent vers le root logger configuré ici.
"""
import logging
import sys

from pythonjsonlogger import jsonlogger

# Loggers tiers verbeux — limités à WARNING pour ne pas polluer les logs métier
_NOISY_LOGGERS = (
    "uvicorn.access",
    "httpx",
    "httpcore",
    "multipart",
)


def setup_logging(log_level: str = "INFO") -> None:
    """Configure le root logger avec le formatter JSON et le niveau souhaité."""
    level = getattr(logging, log_level.upper(), logging.INFO)

    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"levelname": "severity", "asctime": "timestamp"},
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    for h in root.handlers[:]:
        root.removeHandler(h)
    root.addHandler(handler)

    for name in _NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Retourne le logger de module — propagation vers le root logger configuré."""
    return logging.getLogger(name)
