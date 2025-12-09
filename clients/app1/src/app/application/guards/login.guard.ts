import { inject } from '@angular/core';
import { Router, type CanActivateFn } from '@angular/router';
import { toObservable } from '@angular/core/rxjs-interop';
import { filter, take, map, timeout, catchError, of } from 'rxjs';
import { AuthService } from '../services/auth.service';

/**
 * Guard for login page that redirects authenticated users to /app
 * Also handles the case where there's a valid token but no user data
 */
export const loginGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  const hasToken = authService.hasAccessToken();
  const user = authService.getUser();

  // If user is already authenticated, redirect to app
  if (hasToken && user) {
    router.navigate(['/app']);
    return false;
  }

  // If there's a token but no user, load the user and wait for it
  if (hasToken && !user) {
    authService.loadCurrentUser();

    // Wait for user to be loaded (with timeout)
    return toObservable(authService.currentUser).pipe(
      filter((u) => u !== null), // Wait until user is loaded
      take(1), // Take first non-null value
      timeout(5000), // 5 second timeout
      map(() => {
        // User loaded successfully, redirect to app
        router.navigate(['/app']);
        return false;
      }),
      catchError(() => {
        // Timeout or error loading user - allow access to login page
        return of(true);
      }),
    );
  }

  // No token - allow access to login page
  return true;
};
