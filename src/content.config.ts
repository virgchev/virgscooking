import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const THEMES = ['Halloween', 'Noël', 'Saint-Valentin', 'Pâques', 'Anniversaire', 'Canicule'] as const;
const REGIMES = ['Sans Gluten', 'Sans Lactose', 'Végétarien', 'Végétalien', 'Sans Œufs'] as const;

const recettes = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/recettes' }),
  schema: z.object({
    titre: z.string(),
    themes: z.array(z.enum(THEMES)).default([]),
    regimes: z.array(z.enum(REGIMES)).default([]),
    categories: z.array(z.string()).default(['Divers']),
    difficulte: z.number().min(1).max(4).optional(),
    minutes: z.number().optional(),
    portions: z.number().default(4),
    date: z.coerce.date(),index_ingredients: z.array(z.string()).default([]),
    ingredients: z
      .array(z.object({ nom: z.string(), qte: z.number().optional(), unite: z.string().optional() }))
      .default([]),
  }),
});

export const collections = { recettes };


