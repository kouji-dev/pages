import { HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from '../../application/services/auth.service';
import { environment } from '../../../environments/environment';

/**
 * Auth Interceptor
 * Adds JWT token to request headers and handles token refresh on 401 errors
 */
export const authInterceptor: HttpInterceptorFn = (req: HttpRequest<unknown>, next) => {
  const authService = inject(AuthService);

  // Skip adding token for auth endpoints and non-API requests
  if (req.url.includes('/auth/') || !req.url.includes(environment.apiUrl)) {
    return next(req);
  }

  // Get access token
  const accessToken = authService.getAccessToken();

  // If no token, proceed without it (will be handled by error interceptor)
  if (!accessToken) {
    return next(req);
  }

  // Clone request and add Authorization header
  const clonedReq = req.clone({
    setHeaders: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  // Execute request
  return next(clonedReq).pipe(
    catchError((error) => {
      // Handle 401 Unauthorized - token might be expired
      if (error.status === 401) {
        const refreshToken = authService.getRefreshToken();

        // If no refresh token, let error interceptor handle logout
        if (!refreshToken) {
          return throwError(() => error);
        }

        // Try to refresh the token
        return authService.refreshToken().pipe(
          switchMap((tokenResponse) => {
            // Retry the original request with new token
            const retryReq = req.clone({
              setHeaders: {
                Authorization: `Bearer ${tokenResponse.access_token}`,
              },
            });
            return next(retryReq);
          }),
          catchError((refreshError) => {
            // If refresh fails, let error interceptor handle logout
            return throwError(() => refreshError);
          }),
        );
      }

      return throwError(() => error);
    }),
  );
};
