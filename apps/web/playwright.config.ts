import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  fullyParallel: false,
  workers: 1,
  forbidOnly: Boolean(process.env.CI),
  retries: 0,
  reporter: [['list']],
  use: {
    baseURL: 'http://127.0.0.1:8000',
    browserName: 'chromium',
    viewport: { width: 1440, height: 900 },
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  webServer: {
    command: '.\\.venv\\Scripts\\python.exe -m uvicorn resilitrip.main:app --host 127.0.0.1 --port 8000',
    cwd: '../api',
    url: 'http://127.0.0.1:8000/api/health/ready',
    reuseExistingServer: false,
    timeout: 30_000,
    env: {
      RESILITRIP_DATABASE_PATH: '../../data/local/browser-e2e.sqlite3',
      RESILITRIP_TEST_CONTROLS: '1',
    },
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
})
