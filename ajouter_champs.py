import sys
from pathlib import Path

DOSSIER = Path("src/content/recettes")
APPLIQUER = "--appliquer" in sys.argv


def point_insertion(lignes):
    """Juste après 'categories:' (et sa liste si elle est sur plusieurs lignes)."""
    for i, l in enumerate(lignes):
        if l.startswith("categories:"):
            j = i + 1
            while j < len(lignes) and lignes[j].startswith((" ", "\t", "-")):
                j += 1
            return j
    return len(lignes)


for fichier in sorted(DOSSIER.glob("*.md")):
    texte = fichier.read_text(encoding="utf-8")
    fin = texte.find("\n---\n", 4)
    if not texte.startswith("---\n") or fin == -1:
        print(f"IGNORÉ (pas de frontmatter) : {fichier.name}")
        continue

    lignes = texte[: fin + 1].splitlines(keepends=True)
    reste = texte[fin + 1 :]

    ajouts = []
    if not any(l.startswith("themes:") for l in lignes):
        ajouts.append("themes: []\n")
    if not any(l.startswith("regimes:") for l in lignes):
        ajouts.append("regimes: []\n")
    if not ajouts:
        continue

    lignes[point_insertion(lignes):point_insertion(lignes)] = ajouts
    print(f"{'MODIFIÉ' if APPLIQUER else 'À MODIFIER'} : {fichier.name}")
    if APPLIQUER:
        fichier.write_text("".join(lignes) + reste, encoding="utf-8")

if not APPLIQUER:
    print("\nSimulation terminée. Relance avec --appliquer pour écrire les fichiers.")