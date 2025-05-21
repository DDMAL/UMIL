import { defineConfig } from 'vite';
import { resolve } from 'path';
import FullReload from 'vite-plugin-full-reload';

export default defineConfig({
  publicDir: 'assets',
  base: '/static/',
  plugins: [FullReload(['./assets/**/*'])],
  build: {
    outDir: 'static',
    manifest: 'manifest.json',
    emptyOutDir: true,
    sourcemap: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'src/main.ts'),
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name]-[hash].js',
        assetFileNames: '[name].[ext]',
      },
    },
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    hmr: true,
    host: 'localhost',
    port: 5173,
  },
});
