import { Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class LoginPage extends BasePage {
  async goto() {
    await super.goto('/login/');
  }

  getUsernameInput(): Locator {
    return this.page.locator('input[name="username"]');
  }

  getPasswordInput(): Locator {
    return this.page.locator('input[name="password"]');
  }

  getSubmitButton(): Locator {
    return this.page.locator('button[type="submit"]:has-text("Sign in")');
  }

  getRegisterLink(): Locator {
    return this.page.locator('a[href*="register"]');
  }

  async login(username: string, password: string) {
    await this.getUsernameInput().fill(username);
    await this.getPasswordInput().fill(password);
    await this.getSubmitButton().click();
  }

  getUserDropdown(): Locator {
    return this.page.locator('.dropdown:has(svg[aria-label="user icon"])');
  }

  getLogoutLink(): Locator {
    return this.page.locator('a[href*="logout"]');
  }

  async logout() {
    await this.getUserDropdown().click();
    await this.getLogoutLink().click();
  }

  async isLoggedIn(): Promise<boolean> {
    return await this.getUserDropdown().isVisible();
  }
}
