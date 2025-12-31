import { inject } from '@angular/core';
import { Router, type CanActivateFn } from '@angular/router';
import { AuthService } from '../auth.service';

/**
 * Auth guard that protects routes requiring authentication.
 * Waits for auth initialization to complete before checking authentication.
 * Redirects to login page if user is not authenticated.
 */
export const authGuard: CanActivateFn = async () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Wait for auth initialization to complete
  await authService.initialized;

  // Check if user is authenticated (has token and user data)
  if (authService.isAuthenticated() && authService.hasAccessToken()) {
    return true;
  }

  // Redirect to login page if not authenticated
  router.navigate(['/login']);
  return false;
};
