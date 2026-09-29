"""Interface Tkinter de l'outil d'audit."""

import logging
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from config import COLONNE_ID_DEFAUT, NOM_LOGGER
from services import auditer, normaliser_id

logger = logging.getLogger(NOM_LOGGER)


class HandlerStatut(logging.Handler):
    """Affiche le dernier message de log dans la barre de statut de la fenêtre."""

    def __init__(self, app):
        super().__init__()
        self.app = app

    def emit(self, record):
        try:
            self.app.statut.config(text=record.getMessage().strip())
            self.app.update_idletasks()
        except tk.TclError:
            pass


class Application(tk.Tk):
    TYPES_FICHIERS = [
        ("Fichiers Excel / CSV", "*.xlsx *.xlsm *.xls *.csv"),
        ("Tous les fichiers", "*.*"),
    ]

    def __init__(self):
        super().__init__()
        self.title("Audit ID erreur")
        self.geometry("820x640")
        self.minsize(640, 520)

        self.chemin1 = tk.StringVar()
        self.chemin2 = tk.StringVar()
        self.nom_colonne = tk.StringVar(value=COLONNE_ID_DEFAUT)

        self._construire()
        logger.addHandler(HandlerStatut(self))

    def _construire(self):
        cadre = ttk.Frame(self, padding=12)
        cadre.pack(fill="both", expand=True)
        cadre.columnconfigure(1, weight=1)

        # --- Fichiers ---
        ttk.Label(cadre, text="Fichier 1 :").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(cadre, textvariable=self.chemin1).grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(cadre, text="Parcourir…", command=lambda: self._choisir(self.chemin1)).grid(row=0, column=2)

        ttk.Label(cadre, text="Fichier 2 :").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(cadre, textvariable=self.chemin2).grid(row=1, column=1, sticky="ew", padx=6)
        ttk.Button(cadre, text="Parcourir…", command=lambda: self._choisir(self.chemin2)).grid(row=1, column=2)

        ttk.Label(cadre, text="Nom de la colonne ID :").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(cadre, textvariable=self.nom_colonne, width=30).grid(row=2, column=1, sticky="w", padx=6)

        # --- Liste des ID ---
        ttk.Label(cadre, text="Liste des ID erreur à auditer (un par ligne) :").grid(
            row=3, column=0, columnspan=3, sticky="w", pady=(12, 4)
        )
        self.zone_ids = scrolledtext.ScrolledText(cadre, height=10)
        self.zone_ids.grid(row=4, column=0, columnspan=3, sticky="nsew")
        cadre.rowconfigure(4, weight=1)

        # --- Boutons ---
        boutons = ttk.Frame(cadre)
        boutons.grid(row=5, column=0, columnspan=3, pady=10)
        ttk.Button(boutons, text="Lancer l'audit", command=self._lancer).pack(side="left", padx=5)
        ttk.Button(boutons, text="Effacer la liste", command=lambda: self.zone_ids.delete("1.0", "end")).pack(
            side="left", padx=5
        )

        # --- Récapitulatif ---
        ttk.Label(cadre, text="Récapitulatif :").grid(row=6, column=0, columnspan=3, sticky="w")
        colonnes = ("id", "f1", "f2")
        self.tableau = ttk.Treeview(cadre, columns=colonnes, show="headings", height=8)
        self.tableau.heading("id", text="ID erreur")
        self.tableau.heading("f1", text="Présent dans fichier 1")
        self.tableau.heading("f2", text="Présent dans fichier 2")
        for c in colonnes:
            self.tableau.column(c, anchor="center")
        self.tableau.grid(row=7, column=0, columnspan=3, sticky="nsew")
        cadre.rowconfigure(7, weight=1)

        self.statut = ttk.Label(cadre, text="", foreground="gray")
        self.statut.grid(row=8, column=0, columnspan=3, sticky="w", pady=(6, 0))

    def _choisir(self, variable):
        chemin = filedialog.askopenfilename(title="Choisir un fichier", filetypes=self.TYPES_FICHIERS)
        if chemin:
            variable.set(chemin)

    def _lancer(self):
        chemin1, chemin2 = self.chemin1.get().strip(), self.chemin2.get().strip()
        nom_colonne = self.nom_colonne.get().strip() or COLONNE_ID_DEFAUT

        for chemin in (chemin1, chemin2):
            if not chemin or not os.path.isfile(chemin):
                messagebox.showerror("Erreur", f"Fichier introuvable :\n{chemin or '(vide)'}")
                return

        ids = {normaliser_id(l) for l in self.zone_ids.get("1.0", "end").splitlines()} - {""}
        if not ids:
            messagebox.showerror("Erreur", "Veuillez saisir au moins un ID erreur.")
            return

        self.config(cursor="watch")
        self.update_idletasks()
        try:
            sortie1, sortie2, recap = auditer(chemin1, chemin2, ids, nom_colonne)
        except PermissionError as e:
            logger.error("Fichier ouvert ou protégé en écriture : %s", e.filename)
            messagebox.showerror("Erreur", f"Fichier ouvert ou protégé en écriture :\n{e.filename}")
            return
        except Exception as e:
            logger.exception("Échec de l'audit")
            messagebox.showerror("Erreur", str(e))
            return
        finally:
            self.config(cursor="")

        self.tableau.delete(*self.tableau.get_children())
        for ligne in recap:
            self.tableau.insert("", "end", values=ligne)

        self.statut.config(text=f"{len(ids)} ID audité(s). Résultats enregistrés.")
        messagebox.showinfo(
            "Audit terminé",
            f"Fichiers générés :\n\n{sortie1}\n{sortie2}",
        )
