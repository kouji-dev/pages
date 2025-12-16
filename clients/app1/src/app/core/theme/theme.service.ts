import { Injectable, signal, effect, EffectRef } from '@angular/core';

export type Theme = 'light' | 'dark';

const THEME_STORAGE_KEY = 'pages-theme';

@Injectable({
  providedIn: 'root',
})
export class ThemeService {
  private readonly themeSignal = signal<Theme>(this.getInitialTheme());

  readonly theme = this.themeSignal.asReadonly();

  private readonly themeEffect = effect(() => {
    const currentTheme = this.themeSignal();
    this.applyTheme(currentTheme);
    this.persistTheme(currentTheme);
  });

  constructor() {
    // Apply theme on initialization
    this.applyTheme(this.themeSignal());
  }

  /**
   * Get initial theme from localStorage or system preference
   */
  private getInitialTheme(): Theme {
    // Check localStorage first
    const stored = localStorage.getItem(THEME_STORAGE_KEY) as Theme | null;
    if (stored === 'light' || stored === 'dark') {
      return stored;
    }

    // Fall back to system preference
    if (typeof window !== 'undefined' && window.matchMedia) {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      return prefersDark ? 'dark' : 'light';
    }

    // Default to light
    return 'light';
  }

  /**
   * Apply theme to document
   */
  private applyTheme(theme: Theme): void {
    if (typeof document === 'undefined') {
      return;
    }

    const html = document.documentElement;
    if (theme === 'dark') {
      html.setAttribute('data-theme', 'dark');
    } else {
      html.removeAttribute('data-theme');
    }
  }

  /**
   * Persist theme to localStorage
   */
  private persistTheme(theme: Theme): void {
    if (typeof localStorage === 'undefined') {
      return;
    }
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  }

  /**
   * Toggle between light and dark theme
   */
  toggleTheme(): void {
    this.themeSignal.update((current) => (current === 'dark' ? 'light' : 'dark'));
  }

  /**
   * Set theme explicitly
   */
  setTheme(theme: Theme): void {
    this.themeSignal.set(theme);
  }
}
