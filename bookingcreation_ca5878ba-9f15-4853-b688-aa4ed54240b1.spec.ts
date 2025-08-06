
import { test } from '@playwright/test';
import { expect } from '@playwright/test';

test('BookingCreation_2025-08-06', async ({ page, context }) => {
  
    // Click element
    await page.click('#frontPageLink');

    // Take screenshot
    await page.screenshot({ path: 'front_page_for_booking.png' });

    // Click element
    await page.click('a[href="#booking"]');

    // Click element
    await page.click('button[type='button'].btn.btn-primary');

    // Take screenshot
    await page.screenshot({ path: 'booking_availability_checked.png' });
});