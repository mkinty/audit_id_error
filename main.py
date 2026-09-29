"""
Point d'entrée de l'outil d'audit "ID erreur".

Formats supportés : .xlsx, .xlsm, .xls, .csv
Dépendances : pandas, openpyxl
"""

import logging

from config import FICHIER_LOG, NOM_LOGGER
from ui import Application
from utils.logs import configurer_logs


def main():
    configurer_logs()
    logging.getLogger(NOM_LOGGER).info("Démarrage de l'application (logs : %s)", FICHIER_LOG)
    Application().mainloop()


if __name__ == "__main__":
    main()
