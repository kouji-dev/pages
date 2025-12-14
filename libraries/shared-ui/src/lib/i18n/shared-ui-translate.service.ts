import { Injectable, inject, Optional } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { Observable } from 'rxjs';

/**
 * Translation service for shared-ui library components
 * This service provides a wrapper around TranslateService with a namespace prefix
 * to isolate shared-ui translations from app translations
 */
@Injectable({
  providedIn: 'root',
})
export class SharedUiTranslateService {
  private readonly translateService = inject(TranslateService, { optional: true });
  private readonly namespace = 'shared-ui';

  /**
   * Get translation for a key within the shared-ui namespace
   */
  get(key: string, params?: any): Observable<string> {
    if (!this.translateService) {
      // Fallback to key if TranslateService is not available
      return new Observable((observer) => {
        observer.next(key);
        observer.complete();
      });
    }

    const fullKey = `${this.namespace}.${key}`;
    return this.translateService.get(fullKey, params);
  }

  /**
   * Get translation synchronously (returns key if not available)
   */
  instant(key: string, params?: any): string {
    if (!this.translateService) {
      return key;
    }

    const fullKey = `${this.namespace}.${key}`;
    return this.translateService.instant(fullKey, params) || key;
  }

  /**
   * Stream of translation changes
   */
  get onLangChange(): Observable<any> {
    if (!this.translateService) {
      return new Observable((observer) => {
        observer.complete();
      });
    }
    return this.translateService.onLangChange;
  }

  /**
   * Stream of default language changes
   */
  get onDefaultLangChange(): Observable<string> {
    if (!this.translateService) {
      return new Observable((observer) => {
        observer.complete();
      });
    }
    return this.translateService.onDefaultLangChange;
  }
}
