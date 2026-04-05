import { test, expect } from '@playwright/test'

test.describe('Login Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
  })

  test('should display login form with all elements', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Emergency Platform')
    await expect(page.locator('text=Sign in to your account')).toBeVisible()
    await expect(page.getByLabel('Email')).toBeVisible()
    await expect(page.getByLabel('Password')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Sign In' })).toBeVisible()
    await expect(page.getByText("Don't have an account?")).toBeVisible()
    await expect(page.getByRole('link', { name: 'Register here' })).toBeVisible()
  })

  test('should have link to register page', async ({ page }) => {
    await page.getByRole('link', { name: 'Register here' }).click()
    await expect(page).toHaveURL('/register')
    await expect(page.locator('h1')).toContainText('Emergency Platform')
    await expect(page.getByText('Create your account')).toBeVisible()
  })

  test('should show validation error for empty email', async ({ page }) => {
    await page.getByLabel('Email').focus()
    await page.getByLabel('Email').blur()
    await expect(page.locator('text=Email is required')).toBeVisible()
  })

  test('should show validation error for empty password', async ({ page }) => {
    await page.getByLabel('Password').focus()
    await page.getByLabel('Password').blur()
    await expect(page.locator('text=Password is required')).toBeVisible()
  })

  test('should show validation error for invalid email format', async ({ page }) => {
    await page.getByLabel('Email').fill('invalid-email')
    await page.getByLabel('Email').blur()
    await expect(page.locator('text=Please enter a valid email')).toBeVisible()
  })
})
