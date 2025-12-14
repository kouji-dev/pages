import { Injectable, inject, Optional } from '@angular/core';
import { TranslateService as NgxTranslateService } from '@ngx-translate/core';
import { Observable } from 'rxjs';

/**
 * Translation service for shared-ui library components
 * This service provides a wrapper around ngx-translate's TranslateService with a namespace prefix
 * to isolate shared-ui translations from app translations
 */
@Injectable({
  providedIn: 'root',
})
export class TranslateService {
  private readonly ngxTranslateService = inject(NgxTranslateService, { optional: true });
  private readonly namespace = 'shared-ui';

  /**
   * Get translation for a key within the shared-ui namespace
   */
  get(key: string, params?: any): Observable<string> {
    if (!this.ngxTranslateService) {
      // Fallback to key if TranslateService is not available
      return new Observable((observer) => {
        observer.next(key);
        observer.complete();
      });
    }

    const fullKey = `${this.namespace}.${key}`;
    return this.ngxTranslateService.get(fullKey, params);
  }

  /**
   * Get translation synchronously (returns key if not available)
   */
  instant(key: string, params?: any): string {
    if (!this.ngxTranslateService) {
      return key;
    }

    const fullKey = `${this.namespace}.${key}`;
    return this.ngxTranslateService.instant(fullKey, params) || key;
  }

  /**
   * Stream of translation changes
   */
  get onLangChange(): Observable<any> {
    if (!this.ngxTranslateService) {
      return new Observable((observer) => {
        observer.complete();
      });
    }
    return this.ngxTranslateService.onLangChange;
  }

  /**
   * Stream of default language changes
   */
  get onDefaultLangChange(): Observable<any> {
    if (!this.ngxTranslateService) {
      return new Observable((observer) => {
        observer.complete();
      });
    }
    return this.ngxTranslateService.onDefaultLangChange;
  }
}
