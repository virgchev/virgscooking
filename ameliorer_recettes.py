import re
import sys
from pathlib import Path

DOSSIER = Path("src/content/recettes")
APPLIQUER = "--appliquer" in sys.argv

# « Ingrédients: », « **Ingrédients :** », « Les ingrédients : »…
RE_TITRE = re.compile(
    r"^(?:\*\*)?(?:Les[ \t]+)?[Ii]ngr[ée]dients?[ \t]*:?[ \t]*(?:\*\*)?[ \t]*$", re.M
)
# « Recette inspirée du livre… », « Recette adaptée de… »
RE_SOURCE = re.compile(
    r"^(Recette[ \t]+(?:inspirée|adaptée|tirée|issue|trouvée|extraite)[^\n]*?)[ \t]*$", re.M
)

for fichier in sorted(DOSSIER.glob("*.md")):
    texte = fichier.read_text(encoding="utf-8")
    fin = texte.find("\n---\n", 4)
    if not texte.startswith("---\n") or fin == -1:
        print(f"IGNORÉ (pas de frontmatter) : {fichier.name}")
        continue
    front, corps = texte[: fin + 5], texte[fin + 5 :]

    corps, n_titre = RE_TITRE.subn("**Liste des ingrédients :**", corps)
    sources = RE_SOURCE.findall(corps)
    corps = RE_SOURCE.sub(lambda m: f"\n> {m.group(1)}\n", corps)

    if n_titre or sources:
        print(f"{'MODIFIÉ' if APPLIQUER else 'À MODIFIER'} : {fichier.name}")
        for s in sources:
            print(f"    citation : {s[:70]}")
        if APPLIQUER:
            fichier.write_text(front + corps, encoding="utf-8")

if not APPLIQUER:
    print("\nSimulation terminée. Relance avec --appliquer pour écrire les fichiers.")