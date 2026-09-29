"""Lecture / écriture des fichiers Excel et CSV."""

import logging
import os
import time

import pandas as pd

from config import NOM_LOGGER

logger = logging.getLogger(NOM_LOGGER)


def lire_fichier(chemin):
    ext = os.path.splitext(chemin)[1].lower()
    logger.info("Lecture du fichier : %s", chemin)
    debut = time.perf_counter()
    if ext == ".csv":
        # Détection automatique du séparateur (; ou ,)
        df = pd.read_csv(chemin, sep=None, engine="python", dtype=str, encoding_errors="replace")
    elif ext in (".xlsx", ".xlsm", ".xls"):
        df = pd.read_excel(chemin, dtype=str)
    else:
        raise ValueError(f"Format non supporté : {ext}")
    logger.info(
        "  -> %d ligne(s), %d colonne(s) lues en %.2f s", len(df), len(df.columns), time.perf_counter() - debut
    )
    return df


def ecrire_fichier(df, chemin_origine):
    base, ext = os.path.splitext(chemin_origine)
    ext = ext.lower()
    debut = time.perf_counter()
    if ext == ".csv":
        sortie = f"{base}_audit.csv"
        df.to_csv(sortie, index=False, sep=";", encoding="utf-8-sig")
    else:
        sortie = f"{base}_audit.xlsx"
        df.to_excel(sortie, index=False)
    logger.info("Fichier audité enregistré en %.2f s : %s", time.perf_counter() - debut, sortie)
    return sortie


def trouver_colonne(df, nom_colonne, chemin):
    """Retrouve la colonne ID sans tenir compte de la casse ni des espaces."""
    cible = nom_colonne.strip().lower()
    for col in df.columns:
        if str(col).strip().lower() == cible:
            logger.info("Colonne ID trouvée : '%s'", col)
            return col
    raise KeyError(
        f"Colonne '{nom_colonne}' introuvable dans :\n{chemin}\n\n"
        f"Colonnes disponibles : {', '.join(map(str, df.columns))}"
    )
