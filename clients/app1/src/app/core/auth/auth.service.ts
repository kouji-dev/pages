import { Injectable, signal, inject, effect } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import {
  Observable,
  catchError,
  map,
  of,
  tap,
  throwError,
  firstValueFrom,
  timeout,
  filter,
  take,
} from 'rxjs';
import { toObservable } from '@angular/core/rxjs-interop';
import { environment } from '../../../environments/environment';
import { UserStore } from '../user/user.store';

export interface User {
  id: string;
  name: string;
  email: string;
  avatarUrl?: string;
  isActive?: boolean;
  isVerified?: boolean;
}

interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

interface RegisterResponse {
  id: string;
  email: string;
  name: string;
  access_token: string;
  refresh_token: string;
  token_type: string;
  message: string;
}

interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    email: string;
    name: string;
    avatar_url: string | null;
    is_verified: boolean;
  };
}

interface RefreshTokenRequest {
  refresh_token: string;
}

interface RefreshTokenResponse {
  access_token: string;
  refresh_token: string | null;
  token_type: string;
  expires_in: number;
}

interface UserResponse {
  id: string;
  email: string;
  name: string;
  avatar_url: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

interface PasswordResetRequest {
  email: string;
}

interface PasswordResetRequestResponse {
  message: string;
}

interface PasswordResetConfirm {
  token: string;
  new_password: string;
}

interface PasswordResetConfirmResponse {
  message: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly router = inject(Router);
  private readonly http = inject(HttpClient);
  private readonly userStore = inject(UserStore);
  private readonly apiUrl = environment.apiUrl;

  // Current user signal
  readonly currentUser = signal<User | null>(null);

  // Authentication state signal
  readonly isAuthenticated = signal(false);

  // Initialization promise - resolves when initializeAuth is complete
  private readonly initializedPromise: Promise<void>;
  private resolveInitialized!: () => void;

  /**
   * Get the initialization promise
   * This promise resolves when initializeAuth has completed
   */
  get initialized(): Promise<void> {
    return this.initializedPromise;
  }

  // Update isAuthenticated when currentUser changes
  private readonly authStateEffect = effect(() => {
    const user = this.currentUser();
    this.isAuthenticated.set(!!user && !!this.getAccessToken());
  });

  // Watch user profile signal and update currentUser
  private readonly profileWatchEffect = effect(() => {
    const accessToken = this.getAccessToken();
    if (accessToken) {
      const profileSignal = this.userStore.getProfile();
      const profile = profileSignal();

      if (profile) {
        this.currentUser.set({
          id: profile.id,
          email: profile.email,
          name: profile.name,
          avatarUrl: profile.avatarUrl || undefined,
          isActive: profile.isActive,
          isVerified: profile.isVerified,
        });
      } else {
        // If profile is null/undefined and we have an error, clear tokens
        const error = this.userStore.error();
        if (error) {
          this.clearTokens();
        }
      }
    }
  });

  constructor() {
    // Create initialization promise
    this.initializedPromise = new Promise<void>((resolve) => {
      this.resolveInitialized = resolve;
    });

    // Load user from token on initialization
    this.initializeAuth();
  }

  /**
   * Initialize authentication state from stored tokens
   * This method completes the initialization promise when done
   */
  private async initializeAuth(): Promise<void> {
    try {
      const accessToken = this.getAccessToken();
      if (accessToken) {
        // Load user profile from API - the effect will handle updating currentUser
        this.userStore.loadProfile();

        // Wait for profile to load (or error) with timeout
        const isLoading = this.userStore.isLoading;
        const hasError = this.userStore.hasError;
        const profile = this.userStore.getProfile();

        // Wait for loading to complete (either success or error)
        // Check if already loaded or if we need to wait
        if (isLoading()) {
          // Currently loading - wait for it to complete
          try {
            await firstValueFrom(
              toObservable(isLoading).pipe(
                filter((loading) => !loading), // Wait until not loading
                take(1),
                timeout(5000), // 5 second timeout
              ),
            );
          } catch (timeoutError) {
            // Timeout loading profile - clear tokens (user is not authenticated)
            this.clearTokens();
            this.resolveInitialized();
            return;
          }
        }

        // Check if there was an error loading profile
        if (hasError() && !profile()) {
          // Profile load failed - clear tokens (user is not authenticated)
          this.clearTokens();
        }
      }
      // Resolve promise - initialization is complete (even if it failed)
      this.resolveInitialized();
    } catch (error) {
      // Unexpected error - clear tokens and still resolve (initialization is complete)
      this.clearTokens();
      this.resolveInitialized();
    }
  }

  /**
   * Register a new user
   */
  register(request: RegisterRequest): Observable<User> {
    return this.http.post<RegisterResponse>(`${this.apiUrl}/auth/register`, request).pipe(
      tap((response) => {
        // Store tokens
        this.setAccessToken(response.access_token);
        this.setRefreshToken(response.refresh_token);

        // Set user data
        this.currentUser.set({
          id: response.id,
          email: response.email,
          name: response.name,
        });
      }),
      map((response) => ({
        id: response.id,
        email: response.email,
        name: response.name,
      })),
    );
  }

  /**
   * Login user
   */
  login(request: LoginRequest): Observable<User> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/auth/login`, request).pipe(
      tap((response) => {
        // Store tokens
        this.setAccessToken(response.access_token);
        this.setRefreshToken(response.refresh_token);

        // Set user data
        this.currentUser.set({
          id: response.user.id,
          email: response.user.email,
          name: response.user.name,
          avatarUrl: response.user.avatar_url || undefined,
          isVerified: response.user.is_verified,
        });
        this.isAuthenticated.set(true);
      }),
      map((response) => ({
        id: response.user.id,
        email: response.user.email,
        name: response.user.name,
        avatarUrl: response.user.avatar_url || undefined,
        isVerified: response.user.is_verified,
      })),
    );
  }

  /**
   * Refresh access token
   */
  refreshToken(): Observable<RefreshTokenResponse> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return throwError(() => new Error('No refresh token available'));
    }

    return this.http
      .post<RefreshTokenResponse>(`${this.apiUrl}/auth/refresh`, {
        refresh_token: refreshToken,
      } as RefreshTokenRequest)
      .pipe(
        tap((response) => {
          // Update tokens
          this.setAccessToken(response.access_token);
          if (response.refresh_token) {
            this.setRefreshToken(response.refresh_token);
          }
        }),
      );
  }

  /**
   * Load current user from API
   * Uses UserStore to get user data
   * The profileWatchEffect will automatically update currentUser when profile loads
   */
  loadCurrentUser(): void {
    // Load profile from API - the effect will handle updating currentUser
    this.userStore.loadProfile();
  }

  /**
   * Logout the current user
   * Clears authentication tokens and redirects to login
   */
  logout(): void {
    this.clearTokens();
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

  /**
   * Get access token from localStorage
   */
  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  /**
   * Get refresh token from localStorage
   */
  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  /**
   * Set access token in localStorage
   */
  setAccessToken(token: string): void {
    localStorage.setItem('access_token', token);
  }

  /**
   * Set refresh token in localStorage
   */
  setRefreshToken(token: string): void {
    localStorage.setItem('refresh_token', token);
  }

  /**
   * Clear all tokens from localStorage
   */
  clearTokens(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  /**
   * Check if user has a valid access token
   */
  hasAccessToken(): boolean {
    return !!this.getAccessToken();
  }

  /**
   * Request password reset
   */
  requestPasswordReset(email: string): Observable<PasswordResetRequestResponse> {
    return this.http.post<PasswordResetRequestResponse>(
      `${this.apiUrl}/auth/password/reset-request`,
      {
        email,
      } as PasswordResetRequest,
    );
  }

  /**
   * Reset password with token
   */
  resetPassword(token: string, newPassword: string): Observable<PasswordResetConfirmResponse> {
    return this.http.post<PasswordResetConfirmResponse>(`${this.apiUrl}/auth/password/reset`, {
      token,
      new_password: newPassword,
    } as PasswordResetConfirm);
  }
}
