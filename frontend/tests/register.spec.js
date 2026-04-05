import { test, expect } from '@playwright/test'

test.describe('Register Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/register')
  })

  test('should display registration form with all elements', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Emergency Platform')
    await expect(page.getByText('Create your account')).toBeVisible()
    await expect(page.getByLabel('Email')).toBeVisible()
    await expect(page.getByByLabel('Password')).toBeVisible()
    await expect(page.getByLabel('Confirm Password')).toBeVisible()
    await expect(page.getByText('I want to...')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Create Account' })).toBeVisible()
  })

  test('should display all role options', async ({ page }) => {
    await expect(page.getByText('Report Emergencies')).toBeVisible()
    await expect(page.getByText('Volunteer')).toBeVisible()
    await expect(page.getByText('Admin')).toBeVisible()
  })

  test('should allow selecting a role', async ({ page }) => {
    await page.getByText('Volunteer').click()
    await expect(page.locator('input[name="role"][value="volunteer"]')).toBeChecked()
  })

  test('should show validation error for empty fields', async ({ page }) => {
    await page.getByLabel('Email').focus()
    await page.getByLabel('Email').blur()
    await expect(page.locator('text=Email is required')).toBeVisible()
  })

  test('should show validation error for password mismatch', async ({ page }) => {
    await page.getByLabel('Email').fill('test@example.com')
    await page.getByLabel('Password').fill('password123')
    await page.getByLabel('Confirm Password').fill('differentpassword')
    await page.getByRole('button', { name: 'Create Account' }).click()
    await expect(page.getByText('Passwords do not match')).toBeVisible()
  })

  test('should show validation error for short password', async ({ page }) => {
    await page.getByLabel('Email').fill('test@example.com')
    await page.getByLabel('Password').fill('12345')
    await page.getByLabel('Confirm Password').fill('12345')
    await page.getByRole('button', { name: 'Create Account' }).click()
    await expect(page.getByText('Password must be at least 6 characters')).toBeVisible()
  })

  test('should have link to login page', async ({ page }) => {
    await page.getByRole('link', { name: 'Sign in' }).click()
    await expect(page).toHaveURL('/login')
    await expect(page.getByText('Sign in to your account')).toBeVisible()
  })
})
