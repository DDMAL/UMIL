import { Locator } from '@playwright/test';
import { BasePage } from './BasePage';

export class RegisterPage extends BasePage {
  async goto() {
    await super.goto('/register/');
  }

  getUsernameInput(): Locator {
    return this.page.locator('input[name="username"]');
  }

  getPassword1Input(): Locator {
    return this.page.locator('input[name="password1"]');
  }

  getPassword2Input(): Locator {
    return this.page.locator('input[name="password2"]');
  }

  getSubmitButton(): Locator {
    return this.page.locator('button[type="submit"]:has-text("Register")');
  }

  getLoginLink(): Locator {
    return this.page.locator('a[href*="login"]');
  }

  async register(username: string, password1: string, password2: string) {
    await this.getUsernameInput().fill(username);
    await this.getPassword1Input().fill(password1);
    await this.getPassword2Input().fill(password2);
    await this.getSubmitButton().click();
  }
}
