import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const recettes = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/recettes' }),
  schema: z.object({
    titre: z.string(),
    categories: z.array(z.string()).default(['Divers']),
    difficulte: z.number().min(1).max(4).optional(),
    minutes: z.number().optional(),
    portions: z.number().default(4),
    date: z.coerce.date(),
    ingredients: z
      .array(z.object({ nom: z.string(), qte: z.number().optional(), unite: z.string().optional() }))
      .default([]),
  }),
});

export const collections = { recettes };
