// Regroupe « Liste des ingrédients » + sous-titres + listes à puces dans un seul post-it

const texte = (n) =>
  n.type === 'text'
    ? n.value
    : n.type === 'raw'
      ? n.value.replace(/<[^>]*>/g, '')
      : (n.children ?? []).map(texte).join('');

const estBalise = (n, nom) =>
  (n?.type === 'element' && n.tagName === nom) ||
  (n?.type === 'raw' && new RegExp(`^\\s*<${nom}[\\s>]`, 'i').test(n.value));

const estVide = (n) => n.type === 'text' && !n.value.trim();

const estTitre = (n) =>
  estBalise(n, 'p') && /^\s*liste des ingr[ée]dients/i.test(texte(n));

export default function rehypePostit() {
  return (arbre) => {
    const noeuds = arbre.children;
    const debut = noeuds.findIndex(estTitre);
    if (debut === -1) return;

    // index du prochain nœud non vide après i
    const suivant = (i) => {
      let j = i + 1;
      while (j < noeuds.length && estVide(noeuds[j])) j++;
      return j;
    };

    let fin = debut;
    let i = suivant(debut);
    while (i < noeuds.length) {
      if (estBalise(noeuds[i], 'ul')) {
        fin = i;
        i = suivant(i);
      } else if (estBalise(noeuds[i], 'p') && estBalise(noeuds[suivant(i)], 'ul')) {
        i = suivant(i); // sous-titre : on passe à la liste qui le suit
      } else {
        break;
      }
    }
    if (fin === debut) return;

    const bloc = noeuds.slice(debut, fin + 1);
    noeuds.splice(debut, bloc.length, {
      type: 'element',
      tagName: 'div',
      properties: { className: ['postit'] },
      children: bloc,
    });
  };
}