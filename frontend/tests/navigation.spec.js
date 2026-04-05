import { test, expect } from '@playwright/test'

test.describe('Navigation', () => {
  test('should redirect to login when accessing protected route', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page).toHaveURL('/login')
  })

  test('should redirect to login when accessing volunteer route', async ({ page }) => {
    await page.goto('/volunteer')
    await expect(page).toHaveURL('/login')
  })

  test('should redirect to login when accessing admin route', async ({ page }) => {
    await page.goto('/admin')
    await expect(page).toHaveURL('/login')
  })

  test('should redirect already logged-in user from login to dashboard', async ({ page, context }) => {
    await context.addInitScript(() => {
      localStorage.setItem('access_token', 'fake-token')
      localStorage.setItem('user', JSON.stringify({ email: 'test@example.com', role: 'affected_user' }))
    })
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await expect(page).not.toHaveURL('/login')
  })

  test('should have working navigation from login to register', async ({ page }) => {
    await page.goto('/login')
    await page.getByRole('link', { name: 'Register here' }).click()
    await expect(page).toHaveURL('/register')
  })

  test('should have working navigation from register to login', async ({ page }) => {
    await page.goto('/register')
    await page.getByRole('link', { name: 'Sign in' }).click()
    await expect(page).toHaveURL('/login')
  })
})
