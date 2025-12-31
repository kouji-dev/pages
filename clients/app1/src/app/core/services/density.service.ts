import { Injectable, signal, effect } from '@angular/core';

export type Density = 'default' | 'compact';

const DENSITY_STORAGE_KEY = 'pages-density';

@Injectable({
  providedIn: 'root',
})
export class DensityService {
  private readonly densitySignal = signal<Density>(this.getInitialDensity());

  readonly density = this.densitySignal.asReadonly();

  private readonly densityEffect = effect(() => {
    const currentDensity = this.densitySignal();
    this.applyDensity(currentDensity);
    this.persistDensity(currentDensity);
  });

  constructor() {
    // Apply density on initialization
    this.applyDensity(this.densitySignal());
  }

  /**
   * Get initial density from localStorage or default to 'default'
   */
  private getInitialDensity(): Density {
    // Check localStorage first
    const stored = localStorage.getItem(DENSITY_STORAGE_KEY) as Density | null;
    if (stored === 'default' || stored === 'compact') {
      return stored;
    }

    // Default to default
    return 'default';
  }

  /**
   * Apply density to document
   */
  private applyDensity(density: Density): void {
    if (typeof document === 'undefined') {
      return;
    }

    const html = document.documentElement;
    if (density === 'compact') {
      html.setAttribute('data-density', 'compact');
    } else {
      html.removeAttribute('data-density');
    }
  }

  /**
   * Persist density to localStorage
   */
  private persistDensity(density: Density): void {
    if (typeof localStorage === 'undefined') {
      return;
    }
    localStorage.setItem(DENSITY_STORAGE_KEY, density);
  }

  /**
   * Toggle between default and compact density
   */
  toggleDensity(): void {
    this.densitySignal.update((current) => (current === 'compact' ? 'default' : 'compact'));
  }

  /**
   * Set density explicitly
   */
  setDensity(density: Density): void {
    this.densitySignal.set(density);
  }
}

