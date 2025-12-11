import { ApplicationConfig, provideAppInitializer, inject } from '@angular/core';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideRouter } from '@angular/router';
import { provideAttachmentService, provideMentionListProvider } from 'shared-ui';

import { routes } from './app.routes';
import { authInterceptor } from './infrastructure/interceptors/auth.interceptor';
import { errorInterceptor } from './infrastructure/interceptors/error.interceptor';
import { ThemeService } from './application/services/theme.service';
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
    provideAppInitializer(() => void inject(ThemeService).theme()),
    // Text editor services
    provideAttachmentService(TextEditorAttachmentService),
    provideMentionListProvider(TextEditorMentionService),
  ],
};
