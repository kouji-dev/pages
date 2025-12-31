import { ApplicationConfig, provideAppInitializer, inject } from '@angular/core';
import { provideHttpClient, withInterceptors, HttpClient } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideRouter } from '@angular/router';
import { provideTranslateService, TranslateLoader } from '@ngx-translate/core';
import { provideAttachmentService, provideMentionListProvider } from 'shared-ui';

import { routes } from './app.routes';
import { authInterceptor } from './core/http/interceptors/auth.interceptor';
import { errorInterceptor } from './core/http/interceptors/error.interceptor';
import { MultiLoaderFactory } from './infrastructure/i18n/multi-loader.factory';
import { ThemeService } from './core/theme/theme.service';
import { LanguageService } from './core/i18n/language.service';
import { TextEditorAttachmentService } from './application/services/text-editor-attachment.service';
import { TextEditorMentionService } from './application/services/text-editor-mention.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideAnimations(),
    provideHttpClient(
      withInterceptors([
        authInterceptor, // Add JWT token to requests
        errorInterceptor, // Handle error responses
      ]),
    ),
    provideRouter(routes),
    // ngx-translate configuration with multiple loaders
    // Loads app translations from assets/i18n and library translations from assets/shared-ui/i18n
    provideTranslateService({
      loader: {
        provide: TranslateLoader,
        useFactory: MultiLoaderFactory,
        deps: [HttpClient],
      },
      fallbackLang: 'en',
      lang: 'en',
    }),
    // Initialize theme
    provideAppInitializer(() => void inject(ThemeService).theme()),
    // Initialize language service
    provideAppInitializer(() => {
      const languageService = inject(LanguageService);
      // Language service will initialize itself in constructor
      return Promise.resolve();
    }),
    // Text editor services
    provideAttachmentService(TextEditorAttachmentService),
    provideMentionListProvider(TextEditorMentionService),
  ],
};
