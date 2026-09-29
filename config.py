"""Constantes partagées par l'application."""

import os

COLONNE_RESULTAT = "ID erreur exist-il ?"
COLONNE_ID_DEFAUT = "ID erreur"

NOM_LOGGER = "audit_id_erreur"
FICHIER_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit_id_erreur.log")
