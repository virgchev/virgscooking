import re
import sys
from pathlib import Path

DOSSIER = Path("src/content/recettes")
APPLIQUER = "--appliquer" in sys.argv

INVISIBLES = "\u00a0\u200b\u200c\u200d\u2060\ufeff"
RE_TITRE = re.compile(r"^\*\*Liste des ingrédients :\*\*[ \t]*$", re.M)
RE_PUCE = re.compile(r"^[-*][ \t]")
BALISE = '<p class="titre-liste">'


def corriger(corps: str) -> str:
    # caractères invisibles devant ou derrière le tiret d'une puce
    corps = re.sub(rf"^[{INVISIBLES}]+(?=[-*])", "", corps, flags=re.M)
    corps = re.sub(rf"^([-*])[{INVISIBLES}]+", r"\1 ", corps, flags=re.M)

    corps = RE_TITRE.sub(BALISE + "Liste des ingrédients :</p>", corps)

    lignes = corps.split("\n")
    sortie = []
    for i, ligne in enumerate(lignes):
        prec = sortie[-1] if sortie else ""
        # ligne vide entre un intitulé et sa liste à puces
        if (
            RE_PUCE.match(ligne)
            and prec.strip()
            and not RE_PUCE.match(prec)
            and not prec.startswith((" ", "\t"))
        ):
            sortie.append("")
        sortie.append(ligne)
        # ligne vide après le titre HTML
        if ligne.startswith(BALISE) and i + 1 < len(lignes) and lignes[i + 1].strip():
            sortie.append("")
    return "\n".join(sortie)


for fichier in sorted(DOSSIER.glob("*.md")):
    texte = fichier.read_text(encoding="utf-8")
    fin = texte.find("\n---\n", 4)
    if not texte.startswith("---\n") or fin == -1:
        print(f"IGNORÉ (pas de frontmatter) : {fichier.name}")
        continue
    front, corps = texte[: fin + 5], texte[fin + 5 :]

    nouveau = corriger(corps)
    if nouveau != corps:
        print(f"{'MODIFIÉ' if APPLIQUER else 'À MODIFIER'} : {fichier.name}")
        if APPLIQUER:
            fichier.write_text(front + nouveau, encoding="utf-8")

if not APPLIQUER:
    print("\nSimulation terminée. Relance avec --appliquer pour écrire les fichiers.")