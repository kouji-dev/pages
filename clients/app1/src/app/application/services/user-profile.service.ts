import { Injectable, signal, inject, computed } from '@angular/core';
import { HttpClient, HttpEvent } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { environment } from '../../../environments/environment';

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatarUrl?: string;
  createdAt?: string;
}

export interface UpdateProfileRequest {
  name: string;
}

export interface UpdateEmailRequest {
  newEmail: string;
  currentPassword: string;
}

export interface UpdatePasswordRequest {
  currentPassword: string;
  newPassword: string;
}

@Injectable({
  providedIn: 'root',
})
export class UserProfileService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/api/v1/users/me`;

  // User profile resource using httpResource
  readonly profile = httpResource<UserProfile>(() => this.apiUrl);

  // Public accessors
  readonly userProfile = computed(() => {
    return this.profile.value() as UserProfile | undefined;
  });
  readonly isLoading = computed(() => this.profile.isLoading());
  readonly error = computed(() => this.profile.error());
  readonly hasError = computed(() => this.profile.error() !== undefined);

  /**
   * Load user profile from API
   */
  loadProfile(): void {
    this.profile.reload();
  }

  /**
   * Update user profile (name only)
   */
  async updateProfile(request: UpdateProfileRequest): Promise<UserProfile> {
    const response = await this.http.put<UserProfile>(this.apiUrl, request).toPromise();
    if (!response) {
      throw new Error('Failed to update profile: No response from server');
    }

    // Reload profile to get updated data
    this.loadProfile();

    return response;
  }

  /**
   * Update user email
   */
  async updateEmail(request: UpdateEmailRequest): Promise<UserProfile> {
    const response = await this.http.put<UserProfile>(`${this.apiUrl}/email`, request).toPromise();
    if (!response) {
      throw new Error('Failed to update email: No response from server');
    }

    // Reload profile to get updated data
    this.loadProfile();

    return response;
  }

  /**
   * Update user password
   */
  async updatePassword(request: UpdatePasswordRequest): Promise<void> {
    await this.http.put(`${this.apiUrl}/password`, request).toPromise();
  }

  /**
   * Upload user avatar
   */
  async uploadAvatar(file: File): Promise<UserProfile> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.http
      .post<UserProfile>(`${this.apiUrl}/avatar`, formData)
      .toPromise();
    if (!response) {
      throw new Error('Failed to upload avatar: No response from server');
    }

    // Reload profile to get updated data
    this.loadProfile();

    return response;
  }

  /**
   * Delete user avatar
   */
  async deleteAvatar(): Promise<UserProfile> {
    const response = await this.http.delete<UserProfile>(`${this.apiUrl}/avatar`).toPromise();
    if (!response) {
      throw new Error('Failed to delete avatar: No response from server');
    }

    // Reload profile to get updated data
    this.loadProfile();

    return response;
  }
}
