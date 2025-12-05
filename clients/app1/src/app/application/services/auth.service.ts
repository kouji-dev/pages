import { Injectable, signal, inject } from '@angular/core';
import { Router } from '@angular/router';

export interface User {
  id: string;
  name: string;
  email: string;
  avatarUrl?: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly router = inject(Router);

  // Current user signal (will be populated from API later)
  readonly currentUser = signal<User | null>(null);

  // Authentication state signal
  readonly isAuthenticated = signal(false);

  constructor() {
    // TODO: Load user from localStorage/API on initialization
    // For now, using placeholder
    this.currentUser.set({
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
    });
    this.isAuthenticated.set(true);
  }

  /**
   * Logout the current user
   * Clears authentication tokens and redirects to login
   */
  logout(): void {
    // TODO: Clear tokens from localStorage
    // TODO: Call logout API endpoint
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    this.currentUser.set(null);
    this.isAuthenticated.set(false);

    // Redirect to login page
    this.router.navigate(['/login']);
  }

  /**
   * Get current user
   */
  getUser(): User | null {
    return this.currentUser();
  }
}
