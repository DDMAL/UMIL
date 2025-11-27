import { defineConfig, mergeConfig } from 'vitest/config';
import viteConfig from './vite.config.js';

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'happy-dom',
      globals: true,
      include: ['src/**/*.{test,spec}.ts'],
      coverage: {
        provider: 'v8',
        reporter: ['text', 'html'],
        // Use Vitest's default exclusions (test files, config files, node_modules, etc.)

        // Optional: Set thresholds later if needed
        // thresholds: {
        //   lines: 60,
        //   functions: 60,
        //   branches: 60,
        //   statements: 60,
        // },
      },
    },
  }),
);
