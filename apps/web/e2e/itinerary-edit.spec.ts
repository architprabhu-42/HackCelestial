import { expect, test } from '@playwright/test'
import { applyD1, generatePlans, loadDemo, previewF3 } from './helpers'

test('T16/T21 journey editor retains the hard-removal draft and requires acknowledgement', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await loadDemo(page); await applyD1(page); await generatePlans(page); await previewF3(page)
  await page.getByRole('button', { name: 'Edit remaining journey' }).click()
  const editor = page.getByRole('dialog', { name: 'Edit journey' })
  await expect(editor.getByText(/Fixed service.*locked/i)).toBeVisible()
  await expect(editor.getByRole('button', { name: 'Remove' }).first()).toBeDisabled()
  const hotel = editor.locator('li').filter({ hasText: 'Hotel check-in' })
  await hotel.getByRole('button', { name: 'Remove' }).click()
  await expect(editor.getByText(/Acknowledgement is required/i)).toBeVisible()
  await expect(editor.getByRole('button', { name: 'Save and recalculate' })).toBeDisabled()
  await expect(editor.getByText('Hotel check-in')).not.toBeVisible()
  await expect(page).toHaveScreenshot('journey-editor-warning.png', { animations: 'disabled', fullPage: true })
  await editor.getByRole('checkbox').check()
  await editor.getByRole('button', { name: 'Save and recalculate' }).click()
  await expect(page.getByRole('heading', { name: 'Your journey has changed' })).toBeVisible()
})

test('a real valid edit marks existing previews stale', async ({ page }) => {
  await loadDemo(page); await applyD1(page); await generatePlans(page); await previewF3(page)
  await page.getByRole('button', { name: 'Edit remaining journey' }).click()
  const editor = page.getByRole('dialog', { name: 'Edit journey' })
  await editor.getByRole('button', { name: 'Move 3 down' }).click()
  await editor.getByRole('button', { name: 'Save and recalculate' }).click()
  await expect(page.getByRole('heading', { name: 'Your journey has changed' })).toBeVisible()
})
