#!/usr/bin/env python3
"""Remplace les émoticônes texte (:) ;-) :D ...) par de vrais emojis dans les recettes.

Usage :
  python outils/emoticones.py            essai : affiche seulement les remplacements
  python outils/emoticones.py --ecrire   modifie réellement les fichiers

Seul le texte des recettes est touché (pas l'en-tête). Annulation : git restore src
"""
import argparse
import re
from pathlib import Path

# (motif, emoji). Une émoticône n'est remplacée que si elle est isolée :
# précédée d'un espace, d'une parenthèse ou du début de ligne, et non suivie d'une lettre ou d'un chiffre.
EMOTICONES = [
    (r":-?\)+", "😊"),
    (r";-?\)+", "😉"),
    (r":-?D", "😃"),
    (r":-?\(+", "🙁"),
    (r":-?[pP]", "😛"),
    (r":'\(", "😢"),
    (r":-?[oO]", "😮"),
    (r"\^\^", "😄"),
    (r"(?:<|&lt;)3", "❤️"),
]


def remplacer(texte, compteur):
    for motif, emoji in EMOTICONES:
        regle = re.compile(rf"(?<![^\s(])(?:{motif})(?![A-Za-z0-9])")
        texte, n = regle.subn(emoji, texte)
        if n:
            compteur[emoji] = compteur.get(emoji, 0) + n
    return texte


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--dossier", default="src/content/recettes")
    p.add_argument("--ecrire", action="store_true")
    args = p.parse_args()

    total, fichiers = {}, 0
    for f in sorted(Path(args.dossier).glob("*.md")):
        texte = f.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", texte, re.S)
        if not m:
            continue
        entete, corps = m.group(1), m.group(2)
        compteur = {}
        nouveau = remplacer(corps, compteur)
        if not compteur:
            continue
        fichiers += 1
        for e, n in compteur.items():
            total[e] = total.get(e, 0) + n
        print(f"✓ {f.stem}: " + ", ".join(f"{n} × {e}" for e, n in compteur.items()))
        for avant, apres in zip(corps.split("\n"), nouveau.split("\n")):
            if avant != apres:
                print("    avant :", avant.strip()[-90:])
                print("    après :", apres.strip()[-90:])
        if args.ecrire:
            with open(f, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("---\n" + entete + "\n---\n" + nouveau)

    print("\nMODIFIÉES" if args.ecrire else "\nESSAI (rien n'est modifié)")
    print(f"{sum(total.values())} émoticône(s) dans {fichiers} recette(s) : " + ", ".join(f"{n} × {e}" for e, n in total.items()))
    if not args.ecrire and total:
        print("Si le résultat te convient : python outils/emoticones.py --ecrire")


if __name__ == "__main__":
    main()
