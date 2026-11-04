import { defineConfig } from 'vite';

export default defineConfig({
  base: './',
  server: { port: 5173, strictPort: true },
  preview: { port: 4173, strictPort: true },
  build: {
    rollupOptions: {
      output: { manualChunks: { editor: ['codemirror'], 'language-cpp': ['@codemirror/lang-cpp'], 'language-python': ['@codemirror/lang-python'] } },
    },
  },
});
