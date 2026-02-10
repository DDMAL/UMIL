import { defineConfig } from 'vite';
import { resolve } from 'path';
import FullReload from 'vite-plugin-full-reload';

export default defineConfig({
  base: '/static/', // Same as STATIC_URL in settings.py
  plugins: [FullReload(['./assets/**/*'])],
  build: {
    outDir: 'dist', // Need to be listed in STATICFILES_DIRS in settings.py
    manifest: 'manifest.json',
    emptyOutDir: true,
    sourcemap: true,
    rollupOptions: {
      input: {
        addName: resolve(__dirname, 'src/instruments/AddName.ts'),
        barCharts: resolve(__dirname, 'src/stats/BarCharts.ts'),
        createInstrument: resolve(
          __dirname,
          'src/instruments/CreateInstrument.ts',
        ),
        deleteName: resolve(__dirname, 'src/instruments/DeleteName.ts'),
        deleteInstrument: resolve(
          __dirname,
          'src/instruments/DeleteInstrument.ts',
        ),
        displaySettings: resolve(
          __dirname,
          'src/instruments/DisplaySettings.ts',
        ),
        jumpToTop: resolve(__dirname, 'src/instruments/JumpToTop.ts'),
        languageList: resolve(__dirname, 'src/LanguageList.ts'),
        main: resolve(__dirname, 'src/main.ts'),
        paginationTools: resolve(
          __dirname,
          'src/instruments/PaginationTools.ts',
        ),
        resendEmailCountdown: resolve(
          __dirname,
          'src/auth/ResendEmailCountdown.ts',
        ),
        statsAnimation: resolve(__dirname, 'src/stats/StatsAnimation.ts'),
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name]-[hash].js',
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
