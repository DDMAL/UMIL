/**
 * Resend Email Countdown Timer
 * Provides countdown UI for email verification resend button.
 * Backend enforces actual rate limiting for security.
 */
class ResendEmailCountdown {
  private button: HTMLButtonElement | null;
  private form: HTMLFormElement | null;
  private cooldownRemaining: number = 60;
  private cooldownDuration: number = 60; // Default, will be synced with backend
  private timer: number | null = null;
  private readonly originalButtonText: string = 'Resend email';

  constructor() {
    this.button = document.getElementById('resendBtn') as HTMLButtonElement;
    this.form = document.getElementById('resendForm') as HTMLFormElement;

    if (this.button && this.form) {
      this.init();
    }
  }

  private init(): void {
    // Read cooldown duration from backend settings
    const durationAttr = this.button?.getAttribute('data-cooldown-duration');
    this.cooldownDuration = durationAttr ? parseInt(durationAttr, 10) : 60;

    // Read initial cooldown from backend (syncs with server-side rate limit)
    const cooldownAttr = this.button?.getAttribute('data-cooldown-remaining');
    const initialCooldown = cooldownAttr ? parseInt(cooldownAttr, 10) : 0;

    // Start countdown if cooldown is active
    if (initialCooldown > 0) {
      this.cooldownRemaining = initialCooldown;
      this.startCountdown();
    }

    // Handle form submission (countdown will restart after page reload)
    this.form?.addEventListener('submit', () => {
      if (!this.button?.disabled) {
        this.cooldownRemaining = this.cooldownDuration;
      }
    });
  }

  private startCountdown(): void {
    this.button!.disabled = true;

    this.timer = window.setInterval(() => {
      this.cooldownRemaining--;
      this.button!.textContent = `Resend email (${this.cooldownRemaining}s)`;

      if (this.cooldownRemaining <= 0) {
        this.stopCountdown();
      }
    }, 1000);
  }

  private stopCountdown(): void {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    this.button!.disabled = false;
    this.button!.textContent = this.originalButtonText;
    this.cooldownRemaining = this.cooldownDuration;
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener(
    'DOMContentLoaded',
    () => new ResendEmailCountdown(),
  );
} else {
  new ResendEmailCountdown();
}
