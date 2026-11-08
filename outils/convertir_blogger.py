#!/usr/bin/env python3
"""Convertit un export Blogger (XML) en fichiers Markdown pour le site Astro.

Installation : pip install markdownify
Usage        : python outils/convertir_blogger.py blog-export.xml
Options      : --telecharger   copie aussi les images dans public/images/
"""
import argparse
import hashlib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlretrieve

from markdownify import markdownify

NS = {"a": "http://www.w3.org/2005/Atom", "app": "http://purl.org/atom/app#"}
TYPE_ARTICLE = "http://schemas.google.com/blogger/2008/kind#post"
SCHEMA_LIBELLE = "http://www.blogger.com/atom/ns#"


def slugify(texte):
    texte = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", texte.lower()).strip("-") or "recette"


def nom_local(balise):
    return balise.rsplit("}", 1)[-1]


def enfant(entree, nom):
    for c in entree:
        if nom_local(c.tag) == nom:
            return c
    return None


def texte(entree, nom):
    c = enfant(entree, nom)
    return (c.text or "").strip() if c is not None else ""


def est_article(entree):
    ancien = any(c.get("term") == TYPE_ARTICLE for c in entree if nom_local(c.tag) == "category")
    return ancien or texte(entree, "type").upper() == "POST"


def est_brouillon(entree):
    controle = enfant(entree, "control")
    if controle is not None and texte(controle, "draft") == "yes":
        return True
    statut = texte(entree, "status")
    return bool(statut) and statut.upper() != "LIVE"


def libelles_de(entree):
    termes = []
    for c in entree:
        if nom_local(c.tag) == "category":
            terme = c.get("term") or ""
            if c.get("scheme") == SCHEMA_LIBELLE or (terme and not terme.startswith("http")):
                termes.append(terme)
    return termes


def slug_de(entree, titre):
    chemin = texte(entree, "filename")
    if chemin:
        return Path(chemin).stem
    for lien in entree:
        if nom_local(lien.tag) == "link" and lien.get("rel") == "alternate":
            nom = Path(urlparse(lien.get("href")).path).stem
            if nom:
                return nom
    return slugify(titre)


def image_pleine_taille(url):
    # Blogger sert des miniatures (/s320/) : on demande la grande version.
    return re.sub(r"/s\d+(-c)?/", "/s1600/", url) if "googleusercontent" in url else url


def traiter_images(md, telecharger, dossier_images):
    def remplace(m):
        alt, url = m.group(1), image_pleine_taille(m.group(2))
        if telecharger:
            ext = Path(urlparse(url).path).suffix or ".jpg"
            nom = hashlib.md5(url.encode()).hexdigest()[:10] + ext
            try:
                urlretrieve(url, dossier_images / nom)
                url = f"/images/{nom}"
            except Exception as err:
                print(f"  image non téléchargée ({err}) : {url}")
        return f"![{alt}]({url})"

    return re.sub(r"!\[([^\]]*)\]\((\S+?)\)", remplace, md)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("export_xml")
    p.add_argument("--sortie", default="src/content/recettes")
    p.add_argument("--telecharger", action="store_true")
    args = p.parse_args()

    sortie = Path(args.sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    dossier_images = Path("public/images")
    if args.telecharger:
        dossier_images.mkdir(parents=True, exist_ok=True)

    racine = ET.parse(args.export_xml).getroot()
    total = 0
    entrees = [e for e in racine.iter() if nom_local(e.tag) == "entry"]
    for e in entrees:
        if not est_article(e) or est_brouillon(e):
            continue
        titre = texte(e, "title") or "Sans titre"
        date = texte(e, "published")[:10] or "2000-01-01"
        libelles = libelles_de(e)
        categorie = libelles[0] if libelles else "Divers"

        corps = markdownify(texte(e, "content"), heading_style="ATX")
        corps = re.sub(r"\n{3,}", "\n\n", corps).strip()
        corps = traiter_images(corps, args.telecharger, dossier_images)

        slug = slug_de(e, titre)
        fichier, i = sortie / f"{slug}.md", 2
        while fichier.exists():
            fichier = sortie / f"{slug}-{i}.md"
            i += 1

        entete = (
            "---\n"
            f"titre: {json.dumps(titre, ensure_ascii=False)}\n"
            f"categorie: {json.dumps(categorie, ensure_ascii=False)}\n"
            f"date: {date}\n"
            "---\n\n"
        )
        fichier.write_text(entete + corps + "\n", encoding="utf-8")
        total += 1
        print(f"✓ {fichier.name}")

    print(f"\n{total} article(s) converti(s) dans {sortie}")
    if total == 0:
        print(f"Aucun article reconnu ({len(entrees)} entrée(s) dans le fichier).")
        if entrees:
            print("Balises de la première entrée :", sorted({nom_local(c.tag) for c in entrees[0]}))


if __name__ == "__main__":
    main()
