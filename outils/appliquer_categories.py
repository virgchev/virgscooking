#!/usr/bin/env python3
"""Remplace les catégories de chaque recette d'après le fichier outils/categories.txt.

Une recette peut avoir plusieurs catégories, séparées par des virgules dans la liste.

Usage :
  python outils/appliquer_categories.py            essai : affiche seulement les changements
  python outils/appliquer_categories.py --ecrire   modifie réellement les fichiers

Annulation possible : git restore src
"""
import argparse
import json
import re
from pathlib import Path


def lire_liste(fichier):
    carte = {}
    for ligne in Path(fichier).read_text(encoding="utf-8-sig").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or ";" not in ligne:
            continue
        nom, cat = (x.strip() for x in ligne.split(";", 1))
        cats = [c.strip() for c in cat.split(",") if c.strip()]
        if nom and cats:
            carte[nom if nom.endswith(".md") else nom + ".md"] = cats
    return carte


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--liste", default="outils/categories.txt")
    p.add_argument("--dossier", default="src/content/recettes")
    p.add_argument("--ecrire", action="store_true")
    args = p.parse_args()

    dossier = Path(args.dossier)
    carte = lire_liste(args.liste)
    absents, changes, inchanges = [], [], 0

    for nom, cat in carte.items():
        f = dossier / nom
        if not f.exists():
            absents.append(nom)
            continue
        texte = f.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", texte, re.S)
        if not m:
            continue
        entete, corps = m.group(1), m.group(2)
        ancien = []
        liste = re.search(r"^categories:\s*(\[.*\])\s*$", entete, re.M)
        if liste:
            try:
                ancien = json.loads(liste.group(1))
            except ValueError:
                pass
        else:
            seule = re.search(r'^categorie:\s*"?(.*?)"?\s*$', entete, re.M)
            ancien = [seule.group(1)] if seule else []
        if ancien == cat:
            inchanges += 1
            continue
        ligne = f"categories: {json.dumps(cat, ensure_ascii=False)}"
        nouvelles, place = [], False
        for l in entete.split("\n"):
            if l.startswith("categorie:") or l.startswith("categories:"):
                if not place:
                    nouvelles.append(ligne)
                    place = True
                continue
            nouvelles.append(l)
        if not place:
            nouvelles.append(ligne)
        entete = "\n".join(nouvelles)
        changes.append((nom, ", ".join(ancien) or "(aucune)", ", ".join(cat)))
        if args.ecrire:
            with open(f, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("---\n" + entete + "\n---\n" + corps)

    print("MODIFIÉES" if args.ecrire else "ESSAI (rien n'est modifié)")
    for nom, ancien, cat in changes:
        print(f"✓ {nom[:-3]}: {ancien} → {cat}")
    if inchanges:
        print(f"\n{inchanges} déjà à jour.")
    non_listees = sorted(x.name for x in dossier.glob("*.md") if x.name not in carte)
    if non_listees:
        print(f"\nRecettes absentes de la liste, non modifiées ({len(non_listees)}) :")
        for nom in non_listees:
            print("  -", nom[:-3])
    if absents:
        print(f"\nDans la liste mais fichier introuvable ({len(absents)}) :")
        for nom in absents:
            print("  -", nom[:-3])
    print(f"\n{len(changes)} recette(s) {'modifiée(s)' if args.ecrire else 'à modifier'}.")
    if not args.ecrire:
        print("Si le résultat te convient : python outils/appliquer_categories.py --ecrire")


if __name__ == "__main__":
    main()
