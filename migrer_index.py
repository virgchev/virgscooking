import re
import sys
from pathlib import Path

DOSSIER = Path("src/content/recettes")
APPLIQUER = "--appliquer" in sys.argv

RE_INDEX = re.compile(
    r'^<p class="index-ingredients"><strong>[^<]*</strong>\s*(.*?)</p>[ \t]*\n?',
    re.M,
)
RE_TITRE = re.compile(r'^\*\*Ingr[ée]dients?[ \t]*:?[ \t]*\*\*[ \t]*$', re.M)


def yaml_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


for fichier in sorted(DOSSIER.glob("*.md")):
    texte = fichier.read_text(encoding="utf-8")
    if not texte.startswith("---\n"):
        print(f"IGNORÉ (pas de frontmatter) : {fichier.name}")
        continue

    fin = texte.find("\n---\n", 4)
    front, corps = texte[: fin + 1], texte[fin + 5 :]
    modifie = False

    m = RE_INDEX.search(corps)
    if m and "index_ingredients:" not in front:
        items = [i.strip() for i in m.group(1).split(";") if i.strip()]
        if items:
            front += "index_ingredients:\n" + "".join(f"  - {yaml_str(i)}\n" for i in items)
            corps = RE_INDEX.sub("", corps, count=1)
            modifie = True

    corps, n = RE_TITRE.subn("**Liste des ingrédients :**", corps)
    modifie = modifie or n > 0

    if modifie:
        print(f"{'MODIFIÉ' if APPLIQUER else 'À MODIFIER'} : {fichier.name}")
        if APPLIQUER:
            fichier.write_text(front + "---\n" + corps, encoding="utf-8")

if not APPLIQUER:
    print("\nSimulation terminée. Relance avec --appliquer pour écrire les fichiers.")