import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { Router } from '@angular/router';
import { AuthService } from '../../application/services/auth.service';
import { ErrorHandlerService } from '../../application/services/error-handler.service';
import { environment } from '../../../environments/environment';

/**
 * Error Interceptor
 * Handles HTTP error responses and provides user-friendly error messages
 */
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  const authService = inject(AuthService);
  const errorHandler = inject(ErrorHandlerService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // Handle different error status codes
      switch (error.status) {
        case 401: // Unauthorized
          // Clear tokens and redirect to login (unless it's an auth endpoint)
          if (!req.url.includes('/auth/')) {
            authService.clearTokens();
            authService.logout();
            errorHandler.handleError(error, 'Your session has expired. Please log in again.');
          } else {
            // For auth endpoints, just show the error message
            errorHandler.handleError(error);
          }
          break;

        case 403: // Forbidden
          errorHandler.handleError(error, 'You do not have permission to perform this action.');
          break;

        case 404: // Not Found
          // Don't show toast for 404s on API calls (let components handle it)
          if (req.url.includes(environment.apiUrl)) {
            // Only log, don't show toast for API 404s
            console.warn('API resource not found:', req.url);
          } else {
            errorHandler.handleError(error, 'The requested resource was not found.');
          }
          break;

        case 500: // Internal Server Error
        case 502: // Bad Gateway
        case 503: // Service Unavailable
          errorHandler.handleError(error, 'A server error occurred. Please try again later.');
          break;

        default:
          // Extract error message from response
          const errorMessage = errorHandler.extractErrorMessage(error);
          errorHandler.handleError(error, errorMessage);
      }

      return throwError(() => error);
    }),
  );
};
