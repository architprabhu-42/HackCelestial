import { expect, test } from '@playwright/test'
import { applyD1, generatePlans, loadDemo, previewF3 } from './helpers'

test('T18 core demo works with external traffic denied and local map fallback', async ({ page }) => {
  await page.route('**/*', route => {
    const host = new URL(route.request().url()).hostname
    return host === '127.0.0.1' || host === 'localhost' ? route.continue() : route.abort()
  })
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await loadDemo(page, '?map=fallback')
  await expect(page.getByLabel('Route list map fallback')).toBeVisible()
  await page.getByLabel('Route list map fallback').getByRole('button', { name: /Train T1 to Madgaon/i }).click()
  await expect(page.getByText('Selected step')).toBeVisible()
  await applyD1(page); await generatePlans(page); await previewF3(page)
  await expect(page).toHaveScreenshot('offline-map-fallback.png', { animations: 'disabled', fullPage: true })
  await page.getByRole('button', { name: 'Use this plan' }).click()
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Use simulated plan' }).click()
  await expect(page.getByText(/No external booking was changed/i)).toBeVisible()
  await page.getByRole('button', { name: 'Reset scenario' }).click()
  await expect(page.getByRole('heading', { name: /Your journey is on track/i })).toBeVisible()
})
