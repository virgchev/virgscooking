#!/usr/bin/env python3
"""Ajoute le niveau de difficulté (1 à 4) de chaque recette d'après outils/difficultes.txt.

Usage :
  python outils/appliquer_difficultes.py            essai : affiche seulement les changements
  python outils/appliquer_difficultes.py --ecrire   modifie réellement les fichiers

Annulation possible : git restore src
"""
import argparse
import re
from pathlib import Path


def lire_liste(fichier):
    carte, erreurs = {}, []
    for ligne in Path(fichier).read_text(encoding="utf-8-sig").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or ";" not in ligne:
            continue
        nom, niveau = (x.strip() for x in ligne.split(";", 1))
        if niveau not in {"1", "2", "3", "4"}:
            erreurs.append(ligne)
            continue
        carte[nom if nom.endswith(".md") else nom + ".md"] = int(niveau)
    return carte, erreurs


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--liste", default="outils/difficultes.txt")
    p.add_argument("--dossier", default="src/content/recettes")
    p.add_argument("--ecrire", action="store_true")
    args = p.parse_args()

    dossier = Path(args.dossier)
    carte, erreurs = lire_liste(args.liste)
    absents, changes, inchanges = [], [], 0

    for nom, niveau in carte.items():
        f = dossier / nom
        if not f.exists():
            absents.append(nom)
            continue
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", f.read_text(encoding="utf-8"), re.S)
        if not m:
            continue
        entete, corps = m.group(1), m.group(2)
        ancien = re.search(r"^difficulte:\s*(\d)\s*$", entete, re.M)
        ancien = int(ancien.group(1)) if ancien else None
        if ancien == niveau:
            inchanges += 1
            continue
        ligne = f"difficulte: {niveau}"
        if re.search(r"^difficulte:", entete, re.M):
            entete = re.sub(r"^difficulte:.*$", lambda _: ligne, entete, flags=re.M)
        else:
            entete += "\n" + ligne
        changes.append((nom, ancien, niveau))
        if args.ecrire:
            with open(f, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("---\n" + entete + "\n---\n" + corps)

    print("MODIFIÉES" if args.ecrire else "ESSAI (rien n'est modifié)")
    for nom, ancien, niveau in changes:
        print(f"✓ {nom[:-3]}: {ancien or '(aucun)'} → {niveau}")
    if inchanges:
        print(f"\n{inchanges} déjà à jour.")
    non_listees = sorted(x.name for x in dossier.glob("*.md") if x.name not in carte)
    if non_listees:
        print(f"\nRecettes absentes de la liste, sans difficulté ({len(non_listees)}) :")
        for nom in non_listees:
            print("  -", nom[:-3])
    if absents:
        print(f"\nDans la liste mais fichier introuvable ({len(absents)}) :")
        for nom in absents:
            print("  -", nom[:-3])
    if erreurs:
        print(f"\nLignes ignorées (le niveau doit être 1, 2, 3 ou 4) :")
        for l in erreurs:
            print("  -", l)
    print(f"\n{len(changes)} recette(s) {'modifiée(s)' if args.ecrire else 'à modifier'}.")
    if not args.ecrire:
        print("Si le résultat te convient : python outils/appliquer_difficultes.py --ecrire")


if __name__ == "__main__":
    main()
