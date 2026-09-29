"""Configuration des logs de l'application."""

import logging

from config import FICHIER_LOG, NOM_LOGGER

logger = logging.getLogger(NOM_LOGGER)


def configurer_logs():
    """Logs dans la console et dans le fichier audit_id_erreur.log."""
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return
    format_log = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    for handler in (logging.StreamHandler(), logging.FileHandler(FICHIER_LOG, encoding="utf-8")):
        handler.setFormatter(format_log)
        logger.addHandler(handler)
