import re
import unicodedata
from pathlib import Path

DOSSIER = Path("src/content/recettes")

# Exclus du végétarisme : viandes, charcuterie, poissons, fruits de mer
VIANDE_POISSON = [
    "boeuf", "veau", "porc", "agneau", "mouton", "poulet", "dinde", "canard", "magret",
    "oie", "lapin", "gibier", "cerf", "sanglier", "pintade", "caille", "volaille",
    "steak", "viande", "jambon", "lardon", "lard", "poitrine", "bacon", "chorizo",
    "saucisse", "saucisson", "merguez", "chipolata", "rillettes", "terrine",
    "mortadelle", "speck", "grisons", "pancetta", "prosciutto", "bresaola",
    "andouille", "boudin", "foie gras", "foie", "escalope", "gigot", "entrecote",
    "tournedos", "carpaccio", "saindoux", "saumon", "thon", "cabillaud", "morue",
    "merlu", "truite", "sardine", "maquereau", "anchois", "colin", "dorade", "lotte",
    "haddock", "poisson", "crevette", "gambas", "langoustine", "homard", "crabe",
    "surimi", "moules", "huitre", "calamar", "encornet", "poulpe", "seiche",
    "saint-jacques", "fruits de mer", "tarama", "caviar", "nuoc-mam", "worcestershire",
]

# Exclus en plus du végétalisme : œufs, produits laitiers, miel, gélatine
PRODUITS_ANIMAUX = [
    "oeuf", "meringue", "mayonnaise", "yaourt", "yogourt", "fromage", "mascarpone",
    "ricotta", "mozzarella", "burrata", "chevre", "feta", "parmesan", "grana",
    "pecorino", "comte", "gruyere", "emmental", "roquefort", "gorgonzola", "cheddar",
    "camembert", "brie", "reblochon", "raclette", "philadelphia", "boursin",
    "chantilly", "miel", "gelatine", "colle de poisson", "presure", "nutella",
    "chocolat blanc", "chocolat au lait", "lait concentre",
]

# Ces mots comptent, sauf suivis d'un complément végétal (lait de coco, beurre de cacahuète…)
SAUF_VEGETAL = [
    r"lait(?!\s+(?:de|d')\s*(?:coco|amande|soja|avoine|riz|noisette|chataigne|cajou)|\s+vegetal)",
    r"beurre(?!\s+(?:de|d')\s*(?:cacahuete|cacao|karite|amande|cajou|noisette|coco))",
    r"creme(?!\s+(?:de|d')\s*(?:coco|riz|soja|amande|avoine|marron|cajou|chataigne))",
]

# Peuvent contenir du lait, des œufs ou du beurre : à contrôler à la main
A_VERIFIER = [
    "chocolat", "pate feuilletee", "pate brisee", "pate sablee", "brioche", "biscuit",
    "speculoos", "margarine", "bouillon", "caramel",
]


def norm(s: str) -> str:
    s = s.lower().replace("œ", "oe").replace("’", "'")
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def motif(mots, speciaux=()):
    parts = []
    for m in mots:
        m = re.escape(norm(m))
        parts.append(m if m.endswith("s") else m + "s?")
    parts.extend(speciaux)
    return re.compile(r"\b(?:" + "|".join(parts) + r")\b")


RE_EXCLUS = motif(VIANDE_POISSON + PRODUITS_ANIMAUX, SAUF_VEGETAL)
RE_VERIF = motif(A_VERIFIER)

candidates, ecartees = [], []
for f in sorted(DOSSIER.glob("*.md")):
    texte = f.read_text(encoding="utf-8")
    texte = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", texte)
    texte = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", texte)
    t = norm(texte)

    m = re.search(r'^titre:\s*"?(.*?)"?\s*$', texte, re.M)
    titre = m.group(1) if m else f.stem
    deja = bool(re.search(r"^regimes:.*V[ée]g[ée]talien", texte, re.M))

    trouves = sorted({x.group(0) for x in RE_EXCLUS.finditer(t)})
    verif = sorted({x.group(0) for x in RE_VERIF.finditer(t)})
    if trouves:
        ecartees.append((titre, trouves))
    else:
        candidates.append((titre, verif, deja))

print(f"\n=== Candidates végétaliennes ({len(candidates)}) : aucun ingrédient animal trouvé ===")
for titre, verif, deja in candidates:
    ligne = f" - {titre}"
    if deja:
        ligne += "  [déjà marquée Végétalien]"
    if verif:
        ligne += f"  (à vérifier : {', '.join(verif)})"
    print(ligne)

print(f"\n=== Écartées ({len(ecartees)}) : mot trouvé ===")
for titre, trouves in ecartees:
    print(f" - {titre}  ->  {', '.join(trouves)}")