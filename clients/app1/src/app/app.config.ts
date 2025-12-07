import { ApplicationConfig } from '@angular/core';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { authInterceptor } from './infrastructure/interceptors/auth.interceptor';
import { errorInterceptor } from './infrastructure/interceptors/error.interceptor';
import { mockApiInterceptor } from './infrastructure/interceptors/mock-api.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideAnimations(),
    provideHttpClient(
      withInterceptors([
        authInterceptor, // Add JWT token to requests
        errorInterceptor, // Handle error responses
        mockApiInterceptor, // Mock API for frontend demo (TODO: remove when backend is ready)
      ]),
    ),
    provideRouter(routes),
  ],
};
