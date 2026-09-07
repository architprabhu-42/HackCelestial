import { expect, type Page } from '@playwright/test'

export async function loadDemo(page: Page, suffix = '') {
  await page.goto(`/${suffix}`)
  await page.getByRole('button', { name: 'Try Mumbai to Goa demo' }).click()
  await expect(page.getByRole('heading', { name: /Your journey is on track|Your arrival plan has changed/i })).toBeVisible()
}

export async function applyD1(page: Page) {
  await page.getByRole('button', { name: 'Report a problem' }).click()
  await expect(page.getByRole('dialog', { name: /What changed/i })).toBeVisible()
  await page.getByRole('button', { name: 'Apply delay' }).click()
  await expect(page.getByRole('heading', { name: /Your arrival plan has changed/i })).toBeVisible()
}

export async function generatePlans(page: Page) {
  await page.getByRole('button', { name: 'Find another way' }).click()
  await expect(page.getByRole('heading', { name: 'Choose a new way forward' })).toBeVisible()
}

export async function previewF3(page: Page) {
  const card = page.locator('.plan-card').filter({ has: page.getByRole('heading', { name: 'Fly F3 to Goa' }) })
  await card.getByRole('button', { name: 'Preview this plan' }).click()
  await expect(page.getByRole('heading', { name: 'Fly F3 to Goa' }).last()).toBeVisible()
}
