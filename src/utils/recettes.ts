import { getCollection, type CollectionEntry } from "astro:content";

export const NIVEAUX = ["Initiation", "Accessible", "Confirmé", "Expert"];

export const slugify = (s: string) =>
  s.toLowerCase().replace(/œ/g, "oe").replace(/æ/g, "ae")
   .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
   .replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");

// 1re image locale du Markdown : ![](/images/xxx.jpg)
export function premiereImage(r: CollectionEntry<"recettes">): string | null {
  return r.body?.match(/!\[[^\]]*\]\((\/[^)\s]+)\)/)?.[1] ?? null;
}

export async function getCategories() {
  const recettes = (await getCollection("recettes"))
    .sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
  const map = new Map<string, { slug: string; nom: string; count: number; cover: string | null }>();
  for (const r of recettes) {
    for (const nom of r.data.categories) {
      const slug = slugify(nom);
      const e = map.get(slug) ?? { slug, nom, count: 0, cover: null };
      e.count++;
      e.cover ??= premiereImage(r); // image de la recette la plus récente
      map.set(slug, e);
    }
  }
  return [...map.values()].sort((a, b) => a.nom.localeCompare(b.nom, "fr"));
}

export type ChampIndex = "categories" | "themes" | "regimes";

// Liste des valeurs utilisées (avec le nombre de recettes), pour les tuiles
export async function getIndex(champ: ChampIndex) {
  const recettes = await getCollection("recettes");
  const map = new Map<string, { slug: string; nom: string; count: number }>();
  for (const r of recettes) {
    for (const nom of r.data[champ] as string[]) {
      const slug = slugify(nom);
      const e = map.get(slug) ?? { slug, nom, count: 0 };
      e.count++;
      map.set(slug, e);
    }
  }
  return [...map.values()].sort((a, b) => a.nom.localeCompare(b.nom, "fr"));
}

// Une page par valeur, avec ses recettes (de la plus récente à la plus ancienne)
export async function cheminsIndex(champ: ChampIndex) {
  const items = await getIndex(champ);
  const toutes = (await getCollection("recettes")).sort(
    (a, b) => b.data.date.getTime() - a.data.date.getTime()
  );
  return items.map((c) => ({
    params: { slug: c.slug },
    props: {
      nom: c.nom,
      recettes: toutes.filter((r) => (r.data[champ] as string[]).some((n) => slugify(n) === c.slug)),
    },
  }));
}