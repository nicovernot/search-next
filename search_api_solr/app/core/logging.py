# app/core/logging.py
"""
Configuration centralisée du logging structuré pour l'application
"""
import logging
import sys

from pythonjsonlogger import jsonlogger


def setup_logging():
    """
    Configure le logging structuré pour l'application

    Returns:
        logging.Logger: Logger configuré avec format JSON
    """
    # Créer un logger pour l'application
    logger = logging.getLogger("openedition_search")
    logger.setLevel(logging.INFO)

    # Supprimer les handlers existants pour éviter les doublons
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Configuration du formatter JSON
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s',
        rename_fields={'levelname': 'severity', 'asctime': 'timestamp'},
        datefmt='%Y-%m-%dT%H:%M:%SZ'
    )

    # Configuration du handler pour la sortie standard
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def get_logger(name: str = "openedition_search") -> logging.Logger:
    """
    Récupère un logger configuré pour un module spécifique

    Args:
        name: Nom du module pour le logger

    Returns:
        logging.Logger: Logger configuré
    """
    logger = logging.getLogger(name)

    # Si le logger n'a pas de handlers, le configurer
    if not logger.handlers:
        setup_logging()

    return logger
