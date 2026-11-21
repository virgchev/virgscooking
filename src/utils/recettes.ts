import { getCollection, type CollectionEntry } from "astro:content";

export const NIVEAUX = ["Initiation", "Accessible", "Confirmé", "Expert"];

export const slugify = (s: string) =>
  s.normalize("NFD").replace(/[\u0300-\u036f]/g, "")
   .toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");

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