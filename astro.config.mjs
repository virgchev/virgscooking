import { defineConfig } from 'astro/config';
import { unified } from '@astrojs/markdown-remark';
import rehypePostit from './src/plugins/rehype-postit.mjs';

// Une fois en ligne, ajoute : site: 'https://ton-site.pages.dev'
export default defineConfig({
  markdown: {
    processor: unified({
      rehypePlugins: [rehypePostit],
    }),
  },
});