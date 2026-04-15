# POM Patterns — Execute Test Case Frontend

Reference patterns for generating Page Object Model (TypeScript) and Playwright test specs.
Agents MUST follow these patterns exactly when generating code.

---

## FormPage.ts — Page Object Model

```typescript
import { Page, Locator } from '@playwright/test';

export class FormPage {
  readonly page: Page;

  // Locators — use data-testid > id > name > getByLabel > CSS class
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly phoneInput: Locator;
  readonly submitButton: Locator;

  // Error message locators — match class patterns: error, invalid, alert, danger
  readonly emailError: Locator;
  readonly passwordError: Locator;
  readonly generalError: Locator;

  constructor(page: Page) {
    this.page = page;

    // Input fields — priority: data-testid > id > name > getByLabel
    this.emailInput = page.locator('[data-testid="email-input"]');
    this.passwordInput = page.locator('input[name="password"]');
    this.phoneInput = page.getByLabel('Phone number');
    this.submitButton = page.locator('button[type="submit"]');

    // Error messages — look for aria-invalid or error class siblings
    this.emailError = page.locator('[data-testid="email-error"], .field-error[for="email"]').first();
    this.passwordError = page.locator('input[name="password"] ~ .error, [aria-invalid="true"]').first();
    this.generalError = page.locator('[role="alert"], .alert-danger, .error-summary').first();
  }

  async goto(url: string) {
    await this.page.goto(url);
    await this.page.waitForLoadState('networkidle');
  }

  async fillEmail(value: string) {
    await this.emailInput.fill(value);
  }

  async fillPassword(value: string) {
    await this.passwordInput.fill(value);
  }

  async fillPhone(value: string) {
    await this.phoneInput.fill(value);
  }

  async submit() {
    await this.submitButton.click();
    // Wait for validation state to settle
    await this.page.waitForTimeout(500);
  }

  async clearAll() {
    const inputs = await this.page.locator('input:not([type="hidden"]), textarea').all();
    for (const input of inputs) {
      await input.fill('');
    }
  }

  async getFieldError(fieldSelector: string): Promise<string> {
    // Try multiple strategies to find error text
    const strategies = [
      `${fieldSelector} ~ .error`,
      `${fieldSelector} ~ [class*="error"]`,
      `${fieldSelector} ~ [class*="invalid"]`,
      `${fieldSelector} + span.error`,
      `[aria-describedby]`, // field with aria-describedby pointing to error
    ];

    for (const selector of strategies) {
      const el = this.page.locator(selector).first();
      if (await el.count() > 0) {
        return (await el.textContent()) ?? '';
      }
    }

    // Fallback: check aria-invalid
    const field = this.page.locator(fieldSelector).first();
    const isInvalid = await field.getAttribute('aria-invalid');
    if (isInvalid === 'true') {
      return 'Field marked invalid (aria-invalid=true)';
    }

    return '';
  }

  async isFieldInvalid(fieldSelector: string): Promise<boolean> {
    const errorText = await this.getFieldError(fieldSelector);
    if (errorText) return true;

    const field = this.page.locator(fieldSelector).first();
    const ariaInvalid = await field.getAttribute('aria-invalid');
    return ariaInvalid === 'true';
  }
}
```

---

## form-validate.spec.ts — Data-Driven Validation Spec

```typescript
import { test, expect } from '@playwright/test';
import { FormPage } from '../pages/formPage';
import testData from '../test-data.json';

const FORM_URL = process.env.FORM_URL ?? 'http://localhost:3000/form';

test.describe('Form Validation', () => {
  let formPage: FormPage;

  test.beforeEach(async ({ page }) => {
    formPage = new FormPage(page);
    await formPage.goto(FORM_URL);
  });

  // ---- TC-001: Empty submit ----
  test('TC-001: Submit empty form - all required fields should show errors', async () => {
    await formPage.submit();

    // Expect at least one error indicator
    const errorCount = await formPage.page
      .locator('[aria-invalid="true"], [class*="error"], [class*="invalid"], [role="alert"]')
      .count();
    expect(errorCount, 'Expected validation errors to appear').toBeGreaterThan(0);
  });

  // ---- TC-002 to TC-00N: Data-driven from test-data.json ----
  for (const fieldData of testData) {
    for (const tc of fieldData.cases) {
      const testTitle = `[${fieldData.field}] ${tc.label}: value="${tc.value}" - expect${tc.expectError ? '' : ' NO'} error`;

      test(testTitle, async () => {
        // Reset form
        await formPage.goto(FORM_URL);

        // Fill target field
        const fieldLocator = formPage.page.locator(fieldData.selector).first();
        await fieldLocator.fill(tc.value);
        await formPage.submit();

        if (tc.expectError) {
          // Assert error is visible
          const isInvalid = await formPage.isFieldInvalid(fieldData.selector);
          expect(isInvalid, `Expected error for field "${fieldData.field}" with value "${tc.value}"`).toBe(true);
        } else {
          // Assert no error
          const isInvalid = await formPage.isFieldInvalid(fieldData.selector);
          expect(isInvalid, `Expected NO error for field "${fieldData.field}" with value "${tc.value}"`).toBe(false);
        }
      });
    }
  }

  // ---- TC-XSS: Basic XSS injection ----
  test('TC-XSS: XSS injection in text fields should not execute', async ({ page }) => {
    const xssPayload = '<script>alert(1)</script>';
    const textInputs = await page.locator('input[type="text"], input[type="email"], textarea').all();

    for (const input of textInputs) {
      await input.fill(xssPayload);
    }

    await formPage.submit();

    // Verify no alert dialog (XSS did not execute)
    let alertFired = false;
    page.once('dialog', async (dialog) => {
      alertFired = true;
      await dialog.dismiss();
    });

    await page.waitForTimeout(1000);
    expect(alertFired, 'XSS alert should not fire').toBe(false);
  });
});
```

---

## playwright.config.ts — Minimal Config

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './agent-workspace/tests',
  timeout: 30000,
  retries: 0,
  reporter: [
    ['json', { outputFile: 'agent-workspace/test-results/results.json' }],
    ['list'],
  ],
  use: {
    headless: true,
    screenshot: 'only-on-failure',
    screenshotsPath: 'agent-workspace/test-results/screenshots',
    video: 'off',
  },
});
```

---

## Assertion Pattern Reference

When generating assertions, use this priority:

```typescript
// Pattern 1: aria-invalid (most reliable)
await expect(page.locator('input[name="email"]')).toHaveAttribute('aria-invalid', 'true');

// Pattern 2: error class element visible
await expect(page.locator('.field-error, [class*="error"]').first()).toBeVisible();

// Pattern 3: error text content
await expect(page.locator('[role="alert"]').first()).toContainText('required');

// Pattern 4: Combined check (field + error message)
const field = page.locator('input[name="email"]');
const error = page.locator('input[name="email"] ~ .error, .email-error');
await expect(field).toHaveAttribute('aria-invalid', 'true');
await expect(error).toBeVisible();
```

---

## Locator Decision Tree

```
Has data-testid?
  YES → use [data-testid="..."]
  NO → Has id?
    YES → use #id or input[id="..."]
    NO → Has name attribute?
      YES → use input[name="..."] or select[name="..."]
      NO → Has aria-label?
        YES → use getByLabel("...")
        NO → Has placeholder?
          YES → use getByPlaceholder("...")
          NO → Use role + text: getByRole('button', { name: '...' })
```

---

## Self-Healing Patterns

When a locator fails, try these alternatives in order:

```typescript
// Original failed: page.locator('.submit-btn')
// Self-heal attempt 1: broader CSS
page.locator('button[type="submit"]')
// Self-heal attempt 2: role-based
page.getByRole('button', { name: /submit/i })
// Self-heal attempt 3: text content
page.getByText('Submit', { exact: false })
```

For timing issues:
```typescript
// Add before any assertion that may be flaky
await page.waitForLoadState('networkidle');
// OR
await page.waitForTimeout(500);
```
