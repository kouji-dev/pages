import { HttpClient } from '@angular/common/http';
import { TranslateLoader } from '@ngx-translate/core';
import { forkJoin, Observable, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

/**
 * Custom TranslateLoader that loads translations from multiple sources and merges them
 * 1. App translations from assets/i18n
 * 2. Shared-ui library translations from assets/shared-ui/i18n
 */
export class MultiTranslateHttpLoader implements TranslateLoader {
  constructor(
    private http: HttpClient,
    private appPrefix: string = 'assets/i18n/',
    private libraryPrefix: string = 'assets/shared-ui/i18n/',
    private suffix: string = '.json',
  ) {}

  getTranslation(lang: string): Observable<any> {
    const appTranslations$ = this.http.get(`${this.appPrefix}${lang}${this.suffix}`).pipe(
      catchError(() => of({})), // Return empty object if file doesn't exist
    );

    const libraryTranslations$ = this.http.get(`${this.libraryPrefix}${lang}${this.suffix}`).pipe(
      catchError(() => of({})), // Return empty object if file doesn't exist
    );

    return forkJoin([appTranslations$, libraryTranslations$]).pipe(
      map(([appTranslations, libraryTranslations]) => {
        // Deep merge: library translations override app translations for same keys
        return this.deepMerge(appTranslations, libraryTranslations);
      }),
    );
  }

  /**
   * Deep merge two objects, with source2 taking precedence
   */
  private deepMerge(target: any, source: any): any {
    const output = { ...target };
    if (this.isObject(target) && this.isObject(source)) {
      Object.keys(source).forEach((key) => {
        if (this.isObject(source[key])) {
          if (!(key in target)) {
            Object.assign(output, { [key]: source[key] });
          } else {
            output[key] = this.deepMerge(target[key], source[key]);
          }
        } else {
          Object.assign(output, { [key]: source[key] });
        }
      });
    }
    return output;
  }

  private isObject(item: any): boolean {
    return item && typeof item === 'object' && !Array.isArray(item);
  }
}

/**
 * Factory function for MultiTranslateHttpLoader
 * Loads translations from multiple sources and merges them
 */
export function MultiLoaderFactory(http: HttpClient): TranslateLoader {
  return new MultiTranslateHttpLoader(http);
}
