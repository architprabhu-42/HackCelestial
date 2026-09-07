import { expect, test } from '@playwright/test'
import { applyD1, loadDemo } from './helpers'

test('T16 shows no-feasible plans from the real ₹5,000 constraint', async ({ page }) => {
  await loadDemo(page, '?testMode=budget-5000')
  await applyD1(page)
  await page.getByRole('button', { name: 'Find another way' }).click()
  await expect(page.getByRole('heading', { name: 'No option fits all your current requirements' })).toBeVisible()
})

test('T16 shows needs-input for a real unsupported onboard state', async ({ page }) => {
  await loadDemo(page, '?testMode=needs-input')
  await applyD1(page)
  await page.getByRole('button', { name: 'Find another way' }).click()
  await expect(page.getByRole('heading', { name: 'We need one more detail' })).toBeVisible()
})

test('T16 shows partial-search and controlled local service failure states', async ({ page }) => {
  await loadDemo(page, '?testMode=partial')
  await applyD1(page)
  await page.getByRole('button', { name: 'Find another way' }).click()
  await expect(page.getByRole('heading', { name: 'Only some options were checked' })).toBeVisible()

  await loadDemo(page, '?testMode=planner-error')
  await applyD1(page)
  await page.getByRole('button', { name: 'Find another way' }).click()
  await expect(page.getByRole('heading', { name: 'We couldn’t update your journey' })).toBeVisible()
})
