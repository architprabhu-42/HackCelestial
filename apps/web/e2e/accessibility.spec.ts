import { expect, test } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'
import { applyD1, generatePlans, loadDemo, previewF3 } from './helpers'

async function noSeriousOrCritical(page: import('@playwright/test').Page) {
  const scan = await new AxeBuilder({ page }).analyze()
  const blocking = scan.violations.filter(item => item.impact === 'critical' || item.impact === 'serious')
  expect(blocking, JSON.stringify(blocking, null, 2)).toEqual([])
}

test('T26 has no serious or critical axe violations through setup, workspace, recovery and adoption', async ({ page }) => {
  await page.goto('/')
  await noSeriousOrCritical(page)
  await page.getByRole('button', { name: 'Try Mumbai to Goa demo' }).click()
  await expect(page.getByRole('heading', { name: /Your journey is on track/i })).toBeVisible()
  await noSeriousOrCritical(page)
  await applyD1(page); await generatePlans(page)
  await noSeriousOrCritical(page)
  await previewF3(page)
  await page.getByRole('button', { name: 'Use this plan' }).click()
  await expect(page.getByRole('dialog', { name: /Use this as your new plan/i })).toBeVisible()
  await noSeriousOrCritical(page)
})

test('T26 keyboard dialogs, focus, reduced motion and desktop/mobile overflow are usable', async ({ page }) => {
  await loadDemo(page)
  await page.getByRole('button', { name: 'Report a problem' }).focus()
  await page.keyboard.press('Enter')
  const dialog = page.getByRole('dialog', { name: /What changed/i })
  await expect(dialog.getByLabel('Close report problem sheet')).toBeFocused()
  await page.keyboard.press('Escape')
  await expect(dialog).toBeHidden()
  await expect(page.getByRole('button', { name: 'Report a problem' })).toBeFocused()
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await expect(page.locator('.sheet')).toHaveCount(0)
  for (const viewport of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) {
    await page.setViewportSize(viewport)
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy()
  }
  await expect(page.getByText('✓ Connected journey')).toBeVisible()
})
