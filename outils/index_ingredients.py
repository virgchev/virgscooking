#!/usr/bin/env python3
"""Ajoute en haut de chaque recette une ligne d'index des ingrédients.

Exemple obtenu : Ingrédients : pâte brisée ; citrons non traités ; fécule de maïs ; sucre

Les quantités et les unités sont retirées. Le texte de la recette n'est pas modifié.

Usage :
  python outils/index_ingredients.py            essai : affiche seulement le résultat
  python outils/index_ingredients.py --ecrire   modifie réellement les fichiers

Annulation possible : git restore src
"""
import argparse
import html
import re
from pathlib import Path

UNITES = (
    r"(?:kg|mg|grammes?|g|cl|ml|dl|litres?|l|"
    r"c\.?\s*à\s*(?:soupe|café|s|c)\.?|cuill?[eè]res?\s+à\s+(?:soupe|café)|"
    r"càs|càc|cs|cc|sachets?|pincées?|gousses?|tranches?|feuilles?|brins?|"
    r"poignées?|boîtes?|pots?|verres?|bouquets?)"
)
QTE = r"(?:\d+\s+\d+/\d+|\d+/\d+|\d+(?:[.,]\d+)?|[½¼¾])"
MARQUEUR = 'class="index-ingredients"'


def est_sous_titre(s):
    return (
        len(s) <= 60
        and not re.match(r"^\d+[.)]\s", s)
        and (s.endswith(":") or s.endswith(":**") or (s.startswith("**") and s.endswith("**")))
    )


def trouver_bloc(lignes):
    """Renvoie la liste des lignes d'ingrédients du premier bloc trouvé, ou None."""
    for i, titre in enumerate(lignes):
        if not re.match(r"^[\s*_#>]*ingr[eé]dients?\b", titre, re.I):
            continue
        puces, fin = [], i
        for j in range(i + 1, len(lignes)):
            s = lignes[j].strip()
            if re.match(r"^[-*•]\s+\S", s):
                puces.append(lignes[j])
            elif not s or est_sous_titre(s):
                continue
            else:
                break
        if puces:
            return puces
        simples = []
        for j in range(i + 1, min(len(lignes), i + 31)):
            s = lignes[j].strip()
            if not s:
                if simples:
                    break
                continue
            if re.match(r"^\d+[.)]\s", s):
                break
            if not est_sous_titre(s):
                simples.append(s)
        if simples:
            return simples
    return None


def nom_ingredient(ligne):
    t = re.sub(r"[*_]{1,3}", "", ligne.strip().lstrip("-*•")).strip()
    t = re.sub(r"\(.*?\)", "", t)
    t = t.split(",")[0].strip()
    m = re.match(rf"^{QTE}(?:\s*(?:à|ou|-|–)\s*{QTE})?\s*", t)
    if m:
        t = t[m.end():]
    t = re.sub(r"^(?:un|une)\s+", "", t, flags=re.I)
    t = re.sub(rf"^{UNITES}(?=\s|$|d['’])\.?\s*", "", t, flags=re.I)
    t = re.sub(r"^(?:de\s+la\s+|de\s+l['’]|de\s+|du\s+|des\s+|d['’])", "", t, flags=re.I)
    t = t.strip(" .;:")
    return t[:1].lower() + t[1:] if t else ""


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--dossier", default="src/content/recettes")
    p.add_argument("--ecrire", action="store_true")
    args = p.parse_args()

    faits, introuvables, deja = [], [], 0
    for f in sorted(Path(args.dossier).glob("*.md")):
        texte = f.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", texte, re.S)
        if not m:
            continue
        entete, corps = m.group(1), m.group(2)
        if MARQUEUR in corps:
            deja += 1
            continue
        lignes = trouver_bloc(corps.split("\n"))
        if not lignes:
            introuvables.append(f.name)
            continue
        noms = []
        for l in lignes:
            n = nom_ingredient(l)
            if n and n not in noms:
                noms.append(n)
        if not noms:
            introuvables.append(f.name)
            continue
        index = " ; ".join(noms)
        faits.append((f.name, index))

        if args.ecrire:
            ligne = f'<p {MARQUEUR}><strong>Ingrédients :</strong> {html.escape(index, quote=False)}</p>'
            with open(f, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("---\n" + entete + "\n---\n\n" + ligne + "\n\n" + corps.lstrip("\n"))

    print("MODIFIÉES" if args.ecrire else "ESSAI (rien n'est modifié)")
    for nom, index in faits:
        print(f"✓ {nom}\n    {index}")
    if deja:
        print(f"\n{deja} recette(s) déjà indexée(s).")
    if introuvables:
        print(f"\nAucun bloc d'ingrédients trouvé ({len(introuvables)}) :")
        for nom in introuvables:
            print("  -", nom)
    print(f"\n{len(faits)} recette(s) {'modifiée(s)' if args.ecrire else 'à modifier'}.")
    if not args.ecrire:
        print("Si le résultat te convient : python outils/index_ingredients.py --ecrire")


if __name__ == "__main__":
    main()
