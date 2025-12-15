import { Injectable, inject, signal, effect } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { DOCUMENT } from '@angular/common';

export type SupportedLanguage = 'en' | 'fr';

@Injectable({
  providedIn: 'root',
})
export class LanguageService {
  private readonly translateService = inject(TranslateService);
  private readonly document = inject(DOCUMENT);

  // Supported languages
  readonly supportedLanguages: SupportedLanguage[] = ['en', 'fr'];

  // Current language signal
  readonly currentLanguage = signal<SupportedLanguage>('en');

  // Language names mapping
  readonly languageNames: Record<SupportedLanguage, string> = {
    en: 'English',
    fr: 'Français',
  };

  constructor() {
    // Add supported languages to TranslateService
    this.translateService.addLangs(this.supportedLanguages);
    this.translateService.setDefaultLang('en');

    // Initialize language on service creation
    this.initializeLanguage();

    // Update document language attribute when language changes
    effect(() => {
      const lang = this.currentLanguage();
      if (this.document.documentElement) {
        this.document.documentElement.lang = lang;
      }
    });
  }

  /**
   * Initialize language from browser, localStorage, or default to 'en'
   */
  private initializeLanguage(): void {
    // Try to get language from localStorage
    const savedLanguage = localStorage.getItem('app-language') as SupportedLanguage | null;

    if (savedLanguage && this.supportedLanguages.includes(savedLanguage)) {
      this.setLanguage(savedLanguage);
      return;
    }

    // Try to detect from browser
    const browserLang = this.detectBrowserLanguage();
    if (browserLang && this.supportedLanguages.includes(browserLang)) {
      this.setLanguage(browserLang);
      return;
    }

    // Default to English
    this.setLanguage('en');
  }

  /**
   * Detect browser language
   */
  private detectBrowserLanguage(): SupportedLanguage | null {
    if (typeof navigator === 'undefined') {
      return null;
    }

    const browserLang = navigator.language || (navigator as any).userLanguage;
    if (!browserLang) {
      return null;
    }

    // Extract language code (e.g., 'fr-FR' -> 'fr')
    const langCode = browserLang.split('-')[0].toLowerCase();

    // Map to supported language
    if (langCode === 'fr') {
      return 'fr';
    }

    // Default to English for other languages
    return 'en';
  }

  /**
   * Set the current language
   */
  setLanguage(lang: SupportedLanguage): void {
    if (!this.supportedLanguages.includes(lang)) {
      console.warn(`Language ${lang} is not supported. Falling back to 'en'.`);
      lang = 'en';
    }

    this.currentLanguage.set(lang);
    this.translateService.use(lang);
    localStorage.setItem('app-language', lang);

    // Update document language attribute
    if (this.document.documentElement) {
      this.document.documentElement.lang = lang;
    }
  }

  /**
   * Get the current language
   */
  getCurrentLanguage(): SupportedLanguage {
    return this.currentLanguage();
  }

  /**
   * Get language name
   */
  getLanguageName(lang: SupportedLanguage): string {
    return this.languageNames[lang] || lang;
  }

  /**
   * Get all supported languages with their names
   */
  getSupportedLanguages(): Array<{ code: SupportedLanguage; name: string }> {
    return this.supportedLanguages.map((code) => ({
      code,
      name: this.languageNames[code],
    }));
  }
}
