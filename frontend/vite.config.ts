import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: Number(process.env.FRONTEND_PORT) || 3000,
    strictPort: true,
  },
  test: {
    environment: "jsdom",
    setupFiles: "./tests/setup.ts",
    coverage: {
      provider: "v8",
      reporter: ["text", "cobertura"],
      reportsDirectory: "./coverage",
      include: ["src/app/**/*.{ts,tsx}"],
      thresholds: {
        lines: 80,
        branches: 75,
      },
    },
  },
});
