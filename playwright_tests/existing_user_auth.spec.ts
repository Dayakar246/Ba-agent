import { test, expect } from '@playwright/test';

// Existing Repository Spec: User Authentication Flow
test('Existing Test: Customer Login and Navigation', async ({ page }) => {
  await page.goto('https://app.valuemomentum.com/login');
  await page.fill('input[name="username"]', 'admin@valuemomentum.com');
  await page.fill('input[name="password"]', 'SecurePass123!');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('https://app.valuemomentum.com/dashboard');
});
