import { ApplicationConfig } from '@angular/core';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { mockApiInterceptor } from './infrastructure/interceptors/mock-api.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideAnimations(),
    // TODO: Remove mockApiInterceptor when backend API is ready
    provideHttpClient(withInterceptors([mockApiInterceptor])),
    provideRouter(routes),
  ],
};
