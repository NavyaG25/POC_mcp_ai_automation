
import { test } from '@playwright/test';
import { expect } from '@playwright/test';

test('AdminLogin_2025-08-06', async ({ page, context }) => {
  
    // Navigate to URL
    await page.goto('https://automationintesting.online/');

    // Take screenshot
    await page.screenshot({ path: 'homepage_loaded.png' });

    // Click element
    await page.click('a[href="/admin"]');

    // Take screenshot
    await page.screenshot({ path: 'admin_page_loaded.png' });

    // Fill input field
    await page.fill('#username', 'admin');

    // Fill input field
    await page.fill('#password', 'password');

    // Click element
    await page.click('#doLogin');

    // Take screenshot
    await page.screenshot({ path: 'after_login_attempt.png' });
});