import { test, expect } from '@playwright/test';

test.describe('Issues & Insights Tracker E2E', () => {
  test('happy path - user registration, login, and issue creation', async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:3000');
    
    // Test registration
    await page.click('text=Need an account? Sign up');
    await page.fill('input[type="email"]', 'e2e-test@example.com');
    await page.fill('input[type="password"]', 'e2e-password');
    await page.click('button[type="submit"]');
    
    // Wait for registration success message
    await expect(page.locator('text=Registration successful! Please log in.')).toBeVisible();
    
    // Test login
    await page.click('text=Already have an account? Sign in');
    await page.fill('input[type="email"]', 'e2e-test@example.com');
    await page.fill('input[type="password"]', 'e2e-password');
    await page.click('button[type="submit"]');
    
    // Should redirect to issues page
    await expect(page).toHaveURL('http://localhost:3000/issues');
    await expect(page.locator('h1:has-text("Issues Dashboard")')).toBeVisible();
    
    // Test creating an issue
    await page.click('text=Create New Issue');
    await page.fill('#title', 'E2E Test Issue');
    await page.fill('#description', 'This is a test issue created by E2E tests');
    await page.selectOption('#severity', 'HIGH');
    await page.click('text=Create Issue');
    
    // Verify issue was created
    await expect(page.locator('text=E2E Test Issue')).toBeVisible();
    await expect(page.locator('text=HIGH')).toBeVisible();
    await expect(page.locator('text=OPEN')).toBeVisible();
    
    // Test dashboard navigation
    await page.click('text=Dashboard');
    await expect(page).toHaveURL('http://localhost:3000/dashboard');
    await expect(page.locator('h1:has-text("Dashboard")')).toBeVisible();
    
    // Verify dashboard shows the created issue
    await expect(page.locator('text=1')).toBeVisible(); // Total issues
    await expect(page.locator('text=1')).toBeVisible(); // Open issues
    
    // Test logout
    await page.click('text=Logout');
    await expect(page).toHaveURL('http://localhost:3000/');
    await expect(page.locator('h2:has-text("Sign in to your account")')).toBeVisible();
  });
  
  test('authentication flow', async ({ page }) => {
    await page.goto('http://localhost:3000');
    
    // Test invalid login
    await page.fill('input[type="email"]', 'invalid@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');
    
    // Should show error message
    await expect(page.locator('text=Incorrect username or password')).toBeVisible();
  });
  
  test('issue management', async ({ page }) => {
    // Login first
    await page.goto('http://localhost:3000');
    await page.fill('input[type="email"]', 'e2e-test@example.com');
    await page.fill('input[type="password"]', 'e2e-password');
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL('http://localhost:3000/issues');
    
    // Create multiple issues
    for (let i = 1; i <= 3; i++) {
      await page.click('text=Create New Issue');
      await page.fill('#title', `Test Issue ${i}`);
      await page.fill('#description', `Description for test issue ${i}`);
      await page.selectOption('#severity', i === 1 ? 'CRITICAL' : i === 2 ? 'HIGH' : 'MEDIUM');
      await page.click('text=Create Issue');
      
      await expect(page.locator(`text=Test Issue ${i}`)).toBeVisible();
    }
    
    // Verify all issues are visible
    await expect(page.locator('text=Test Issue 1')).toBeVisible();
    await expect(page.locator('text=Test Issue 2')).toBeVisible();
    await expect(page.locator('text=Test Issue 3')).toBeVisible();
  });
}); 