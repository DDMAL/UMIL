import Masonry from 'masonry-layout';
import imagesLoaded from 'imagesloaded';
import { DisplayMode } from './Types';

class DisplayManager {
  private masonryBtn: HTMLElement;
  private stdBtn: HTMLElement;
  private masonryView: HTMLElement;
  private stdView: HTMLElement;
  private currentMasonry: Masonry | null = null; // Keep track of the current masonry instance

  constructor() {
    // Initialize DOM elements
    this.masonryBtn = document.getElementById('masonry-btn');
    this.stdBtn = document.getElementById('std-btn');
    this.masonryView = document.getElementById('masonry-view');
    this.stdView = document.getElementById('std-view');

    if (
      !this.masonryBtn ||
      !this.stdBtn ||
      !this.masonryView ||
      !this.stdView
    ) {
      console.error('Required DOM elements not found');
      return;
    }

    this.initializeEventListeners();
    this.updateDisplayMode();
  }

  private initializeEventListeners(): void {
    // Switch to masonry mode
    this.masonryBtn.addEventListener('click', () => {
      if (this.getDisplayMode() !== 'masonry') {
        this.setDisplayMode('masonry');
        this.updateDisplayMode();
      }
    });

    // Switch to standard mode
    this.stdBtn.addEventListener('click', () => {
      if (this.getDisplayMode() !== 'standard') {
        this.setDisplayMode('standard');
        this.updateDisplayMode();
      }
    });

    // Handle window resize for masonry layout
    window.addEventListener('resize', () => {
      if (this.getDisplayMode() === 'masonry' && this.currentMasonry) {
        this.currentMasonry.layout();
      }
    });
  }

  private setDisplayMode(displayMode: DisplayMode): void {
    localStorage.setItem('displayMode', displayMode);
  }

  private getDisplayMode(): DisplayMode {
    return (localStorage.getItem('displayMode') || 'masonry') as DisplayMode;
  }

  private updateDisplayMode(): void {
    const currentDisplayMode = this.getDisplayMode();

    // Update button states
    this.masonryBtn.classList.remove('highlighted-btn');
    this.stdBtn.classList.remove('highlighted-btn');

    switch (currentDisplayMode) {
      case 'masonry':
        this.initializeMasonryView();
        this.masonryView.style.display = '';
        this.stdView.style.display = 'none';
        this.masonryBtn.classList.add('highlighted-btn');
        break;
      case 'standard':
        this.destroyMasonryView();
        this.masonryView.style.display = 'none';
        this.stdView.style.display = '';
        this.stdBtn.classList.add('highlighted-btn');
        break;
    }
  }

  private initializeMasonryView(): void {
    // Clean up any existing masonry instance
    this.destroyMasonryView();

    // Initialize new masonry instance
    this.currentMasonry = new Masonry(this.masonryView, {
      itemSelector: '.col',
      percentPosition: true,
      transitionDuration: 0,
    });

    // Handle image loading
    const imgLoad = imagesLoaded(this.masonryView);

    // Update layout as each image loads
    imgLoad.on('progress', () => {
      this.currentMasonry?.layout();
    });

    // Final layout update when all images are loaded
    imgLoad.on('always', () => {
      this.currentMasonry?.layout();
    });
  }

  private destroyMasonryView(): void {
    if (this.currentMasonry) {
      this.currentMasonry.destroy();
      this.currentMasonry = null;
    }
  }
}

// Initialize display manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new DisplayManager();
});
