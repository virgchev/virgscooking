---
# ============================================================
#  MODÈLE DE RECETTE
#  Copie ce fichier dans src/content/recettes/ et renomme-le :
#  minuscules, sans accent, avec des tirets (ex. tarte-aux-pommes.md).
#  Le nom du fichier devient l'adresse de la page.
# ============================================================

titre: "Titre de la recette"

# Une ou plusieurs : Apéritif, Brunch, Dessert, Entrée, Goûter, Plat
categories: ["Dessert"]

# Facultatif. Valeurs définies dans src/content.config.ts (THEMES).
# Ex. : Halloween, Noël, Saint-Valentin, Pâques, Anniversaire, Canicule
themes: []

# Facultatif. Valeurs définies dans src/content.config.ts (REGIMES).
# Ex. : Sans gluten, Sans lactose, Végétarien, Végétalien, Sans Œuf
# Un régime ne doit être indiqué que s'il est garanti (allergies) :
# vérifie les étiquettes des produits utilisés.
regimes: []

# Format AAAA-MM-JJ : sert à classer les recettes de la plus récente à la plus ancienne.
date: 2026-11-23

# 1 = Initiation, 2 = Accessible, 3 = Confirmé, 4 = Expert
difficulte: 1

# Facultatif : temps total en minutes (supprime la ligne sinon).
minutes: 30

# Ingrédients clés : ils alimentent la recherche et l'index par ingrédient.
# Écris-les en minuscules, au singulier, toujours de la même façon
# d'une recette à l'autre (oeuf, farine, beurre, sucre...).
index_ingredients:
  - "farine"
  - "sucre"
  - "oeuf"

# Facultatif et rare : encadré « Pour X personnes » avec quantités recalculables.
# Il s'ajoute à la liste du texte. Décommente les lignes pour l'utiliser.
# portions: 4
# ingredients:
#   - { nom: "farine", qte: 200, unite: "g" }
#   - { nom: "oeuf", qte: 2 }

# ------------------------------------------------------------
#  RÈGLES POUR LE TEXTE (sous la ligne --- qui ferme ce bloc)
#  1. La première image du texte sert de vignette sur les cartes.
#  2. Le titre de la liste doit être exactement : **Liste des ingrédients :**
#  3. Un sous-titre (Pâte :, Garniture :...) se met seul sur sa ligne, suivi
#     d'une ligne vide, puis de sa liste.
#  4. Tape les tirets des listes à la main : un copier-coller peut y glisser
#     un espace invisible qui casse la liste.
#  5. Étapes : « 1. », « 2. »... Une photo ou un paragraphe qui appartient à
#     une étape s'indente de 3 espaces, sinon il sort de la liste.
#  6. Le texte de fin n'est pas indenté : il est séparé des étapes par un
#     filet en pointillés.
#  7. La source (facultative) commence par > et se place en dernier.
# ------------------------------------------------------------
---

![Photo du plat terminé](/images/nom-de-la-photo.jpg)

Quelques lignes d'introduction : l'histoire de la recette, une occasion, un conseil...

**Liste des ingrédients :**

Pour la pâte :

- 200 g de farine
- 100 g de beurre

Pour la garniture :

- 3 oeufs
- 50 g de sucre

1. Préchauffez le four à 180°C.

   ![Étape 1](/images/nom-photo-etape-1.jpg)

2. Mélangez la farine et le beurre. Ajoutez les oeufs un à un.

3. Enfournez 25 min, puis laissez refroidir avant de servir.

Bonne dégustation ! 😊

> Recette inspirée du livre « Titre du livre » de Nom de l'auteur
