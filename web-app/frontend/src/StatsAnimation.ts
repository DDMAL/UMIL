// Stats Animation for UMIL Homepage
class StatsAnimation {
  private observer: IntersectionObserver;
  private hasAnimated: boolean = false;

  constructor() {
    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !this.hasAnimated) {
            this.animateStats();
            this.hasAnimated = true;
          }
        });
      },
      {
        threshold: 0.5, // Trigger when 50% of the stats section is visible
      },
    );

    this.init();
  }

  private init(): void {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.setupObserver());
    } else {
      this.setupObserver();
    }
  }

  private setupObserver(): void {
    const statsSection = document.querySelector('.stats-section');
    if (statsSection) {
      this.observer.observe(statsSection);
    }
  }

  private animateStats(): void {
    const statNumbers = document.querySelectorAll('.stat-number');

    statNumbers.forEach((element) => {
      const htmlElement = element as HTMLElement;
      const targetText = htmlElement.textContent?.replace(/,/g, '') || '0';
      const targetValue = parseInt(targetText, 10);

      if (isNaN(targetValue)) return;

      this.animateNumber(htmlElement, 0, targetValue, 1000); // 1 second animation
    });
  }

  private animateNumber(
    element: HTMLElement,
    start: number,
    end: number,
    duration: number,
  ): void {
    const startTime = performance.now();

    const updateNumber = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Use easeOutCubic for smooth animation
      const easeProgress = 1 - Math.pow(1 - progress, 3);
      const currentValue = Math.floor(start + (end - start) * easeProgress);

      // Format number with commas
      element.textContent = this.formatNumberWithCommas(currentValue);

      if (progress < 1) {
        requestAnimationFrame(updateNumber);
      } else {
        // Ensure final value is exactly the target
        element.textContent = this.formatNumberWithCommas(end);
      }
    };

    requestAnimationFrame(updateNumber);
  }

  private formatNumberWithCommas(num: number): string {
    return num.toLocaleString();
  }
}

// Initialize the animation when this module is loaded
new StatsAnimation();
