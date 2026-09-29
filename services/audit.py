"""
Audit de deux fichiers via la colonne "ID erreur".

Pour chaque fichier, une colonne "ID erreur exist-il ?" est ajoutée :
  - pour chaque ligne dont l'ID erreur fait partie de la liste saisie,
    la valeur est "oui" si cet ID existe aussi dans l'autre fichier, sinon "non" ;
  - les lignes dont l'ID erreur n'est pas dans la liste restent vides.

Les fichiers audités sont enregistrés à côté des originaux avec le suffixe "_audit"
(les fichiers d'origine ne sont jamais modifiés).
"""

import logging
import time

import pandas as pd

from config import COLONNE_RESULTAT, NOM_LOGGER
from services.fichiers import ecrire_fichier, lire_fichier, trouver_colonne

logger = logging.getLogger(NOM_LOGGER)


def normaliser_id(valeur):
    """Transforme un ID en texte comparable (ex. 123.0 -> '123', ' abc ' -> 'abc')."""
    if pd.isna(valeur):
        return ""
    if isinstance(valeur, float) and valeur.is_integer():
        valeur = int(valeur)
    return str(valeur).strip()


def auditer(chemin1, chemin2, ids_a_auditer, nom_colonne):
    debut = time.perf_counter()
    logger.info("=== Début de l'audit : %d ID à auditer, colonne '%s' ===", len(ids_a_auditer), nom_colonne)

    logger.info("[1/4] Lecture des fichiers")
    df1 = lire_fichier(chemin1)
    df2 = lire_fichier(chemin2)
    col1 = trouver_colonne(df1, nom_colonne, chemin1)
    col2 = trouver_colonne(df2, nom_colonne, chemin2)

    logger.info("[2/4] Extraction des ID distincts")
    ids1 = set(df1[col1].map(normaliser_id)) - {""}
    ids2 = set(df2[col2].map(normaliser_id)) - {""}
    logger.info("  -> Fichier 1 : %d ID distinct(s) | Fichier 2 : %d ID distinct(s)", len(ids1), len(ids2))

    def marquer(df, col, ids_autre_fichier, libelle):
        def statut(valeur):
            id_ = normaliser_id(valeur)
            if id_ not in ids_a_auditer:
                return ""
            return "oui" if id_ in ids_autre_fichier else "non"
        df[COLONNE_RESULTAT] = df[col].map(statut)
        comptes = df[COLONNE_RESULTAT].value_counts()
        logger.info(
            "  -> %s : %d ligne(s) 'oui', %d ligne(s) 'non'",
            libelle, comptes.get("oui", 0), comptes.get("non", 0),
        )

    logger.info("[3/4] Marquage des lignes")
    marquer(df1, col1, ids2, "Fichier 1")
    marquer(df2, col2, ids1, "Fichier 2")

    logger.info("[4/4] Écriture des fichiers audités")
    sortie1 = ecrire_fichier(df1, chemin1)
    sortie2 = ecrire_fichier(df2, chemin2)

    # Récapitulatif par ID audité
    recap = [
        (id_, "oui" if id_ in ids1 else "non", "oui" if id_ in ids2 else "non")
        for id_ in sorted(ids_a_auditer)
    ]
    absents = [id_ for id_, p1, p2 in recap if p1 == "non" and p2 == "non"]
    if absents:
        logger.warning("%d ID absent(s) des deux fichiers : %s", len(absents), ", ".join(absents))
    logger.info("=== Audit terminé en %.2f s ===", time.perf_counter() - debut)
    return sortie1, sortie2, recap
