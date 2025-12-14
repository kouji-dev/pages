import { HttpClient } from '@angular/common/http';
import { TranslateLoader } from '@ngx-translate/core';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';

/**
 * Factory function for TranslateHttpLoader
 * Creates an HTTP loader that loads translation files from the assets/i18n directory
 */
export function HttpLoaderFactory(http: HttpClient): TranslateLoader {
  // TranslateHttpLoader implements TranslateLoader interface
  // Type assertion needed due to Observable<Object> vs Observable<TranslationObject> type mismatch
  return new TranslateHttpLoader(http, './assets/i18n/', '.json') as unknown as TranslateLoader;
}
