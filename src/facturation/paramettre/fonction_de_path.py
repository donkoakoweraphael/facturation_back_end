from pathlib import Path


def dossier_du_projet_django():
    return Path(__file__).resolve().parent.parent

