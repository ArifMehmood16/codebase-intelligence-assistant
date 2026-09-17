import { defineConfig, devices } from "@playwright/test";

const apiPort = 8010;
const webPort = 3010;
const apiBase = `http://127.0.0.1:${apiPort}`;
const webBase = `http://127.0.0.1:${webPort}`;

export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  reporter: "list",
  use: {
    ...devices["Desktop Chrome"],
    baseURL: webBase,
    trace: "on-first-retry",
  },
  webServer: [
    {
      command: `../backend/.venv/bin/python -m codebase_assistant.ops.e2e_api --host 127.0.0.1 --port ${apiPort}`,
      url: `${apiBase}/api/health/live`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        ...process.env,
        // Dedicated e2e ports; do not inherit developer CORS from config/app.env alone.
        CORS_ALLOW_ORIGIN: webBase,
      },
    },
    {
      command: `npm --prefix ../frontend run dev -- --host 127.0.0.1 --port ${webPort}`,
      url: webBase,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        ...process.env,
        VITE_API_BASE_URL: apiBase,
      },
    },
  ],
});
