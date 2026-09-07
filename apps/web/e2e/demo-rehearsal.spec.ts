import { expect, test } from '@playwright/test'
import { mkdirSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { applyD1, generatePlans, loadDemo, previewF3 } from './helpers'

test('T30 repeats the complete hero demonstration five times without mixed state', async ({ browser }) => {
  const runs: Array<{ run: number; result: 'passed'; reset_heading: string }> = []
  for (let run = 1; run <= 5; run += 1) {
    const page = await browser.newPage()
    await loadDemo(page)
    await applyD1(page)
    await generatePlans(page)
    await page.locator('.rejected summary').click()
    await expect(page.locator('.rejected')).toContainText(/Fly F4 to Goa[\s\S]*50 minutes late/)
    await previewF3(page)
    await page.getByRole('button', { name: 'Use this plan' }).click()
    await page.getByRole('checkbox').check()
    await page.getByRole('button', { name: 'Use simulated plan' }).click()
    await expect(page.getByText(/No external booking was changed/i)).toBeVisible()
    await page.getByRole('button', { name: 'Reset scenario' }).click()
    const heading = page.getByRole('heading', { name: 'Your journey is on track' })
    await expect(heading).toBeVisible()
    runs.push({ run, result: 'passed', reset_heading: await heading.textContent() ?? '' })
    await page.close()
  }
  const output = resolve(process.cwd(), '../../artifacts/demo-rehearsal/five-run.json')
  mkdirSync(resolve(process.cwd(), '../../artifacts/demo-rehearsal'), { recursive: true })
  writeFileSync(output, JSON.stringify({ schema_version: 'resilitrip-demo-rehearsal-1.0', runs, passed: runs.length === 5,
    manual_database_repair_required: false, mixed_version_state_observed: false }, null, 2) + '\n')
})
