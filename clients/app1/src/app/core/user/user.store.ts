import { Injectable, signal, inject, computed, type Signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { Observable, map, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatarUrl: string | null;
  isActive: boolean;
  isVerified: boolean;
  createdAt: string;
  updatedAt: string;
}

interface UserProfileResponse {
  id: string;
  name: string;
  email: string;
  avatar_url: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface UpdateProfileRequest {
  name?: string;
}

export interface UpdateEmailRequest {
  new_email: string;
  current_password: string;
}

export interface UpdatePasswordRequest {
  current_password: string;
  new_password: string;
}

@Injectable({
  providedIn: 'root',
})
export class UserStore {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/users/me`;

  // User profile resource using httpResource (with mapping)
  readonly profile = httpResource<UserProfileResponse>(() => this.apiUrl);

  // Public accessors (mapped to camelCase)
  readonly userProfile = computed(() => {
    const response = this.profile.value();
    if (!response) {
      return undefined;
    }
    return this.mapToUserProfile(response);
  });
  readonly isLoading = computed(() => this.profile.isLoading());
  readonly error = computed(() => this.profile.error());
  readonly hasError = computed(() => this.profile.error() !== undefined);

  /**
   * Map backend response (snake_case) to frontend model (camelCase)
   */
  private mapToUserProfile(response: UserProfileResponse): UserProfile {
    return {
      id: response.id,
      name: response.name,
      email: response.email,
      avatarUrl: response.avatar_url,
      isActive: response.is_active,
      isVerified: response.is_verified,
      createdAt: response.created_at,
      updatedAt: response.updated_at,
    };
  }

  /**
   * Load user profile from API
   */
  loadProfile(): void {
    this.profile.reload();
  }

  /**
   * Get current user profile signal
   * Returns readonly signal - consumers can convert to Observable using toObservable() if needed
   */
  getProfile(): Signal<UserProfile | undefined> {
    return this.userProfile;
  }

  /**
   * Update user profile (name only)
   */
  updateProfile(request: UpdateProfileRequest): Observable<UserProfile> {
    return this.http.put<UserProfileResponse>(this.apiUrl, request).pipe(
      tap(() => {
        // Reload resource after successful update
        this.profile.reload();
      }),
      map((response) => this.mapToUserProfile(response)),
    );
  }

  /**
   * Update user email
   */
  updateEmail(request: UpdateEmailRequest): Observable<UserProfile> {
    return this.http.put<UserProfileResponse>(`${this.apiUrl}/email`, request).pipe(
      tap(() => {
        // Reload resource after successful update
        this.profile.reload();
      }),
      map((response) => this.mapToUserProfile(response)),
    );
  }

  /**
   * Update user password
   */
  updatePassword(request: UpdatePasswordRequest): Observable<void> {
    return this.http.put<void>(`${this.apiUrl}/password`, request);
  }

  /**
   * Upload user avatar
   */
  uploadAvatar(file: File): Observable<UserProfile> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<UserProfileResponse>(`${this.apiUrl}/avatar`, formData).pipe(
      tap(() => {
        // Reload resource after successful upload
        this.profile.reload();
      }),
      map((response) => this.mapToUserProfile(response)),
    );
  }

  /**
   * Delete user avatar
   */
  deleteAvatar(): Observable<UserProfile> {
    return this.http.delete<UserProfileResponse>(`${this.apiUrl}/avatar`).pipe(
      tap(() => {
        // Reload resource after successful deletion
        this.profile.reload();
      }),
      map((response) => this.mapToUserProfile(response)),
    );
  }
}
