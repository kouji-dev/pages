import { Injectable, inject, computed, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { environment } from '../../../environments/environment';

export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserListResponse {
  users: User[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface ListUsersParams {
  page?: number;
  limit?: number;
  search?: string;
  organization_id?: string;
}

@Injectable({
  providedIn: 'root',
})
export class UserService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/users`;

  // Search query signal
  private readonly searchQuery = signal<string>('');
  private readonly currentPage = signal<number>(1);
  private readonly pageLimit = signal<number>(20);

  // Users resource using httpResource with computed URL
  private readonly usersResource = httpResource<UserListResponse>(() => {
    const search = this.searchQuery();
    const page = this.currentPage();
    const limit = this.pageLimit();

    if (!search || search.trim().length < 2) {
      return undefined; // Don't search if query is too short
    }

    const params = new HttpParams()
      .set('page', page.toString())
      .set('limit', limit.toString())
      .set('search', search.trim());

    return `${this.apiUrl}?${params.toString()}`;
  });

  // Public accessors
  readonly users = computed(() => {
    const value = this.usersResource.value();
    return value?.users || [];
  });
  readonly isLoading = computed(() => this.usersResource.isLoading());
  readonly error = computed(() => this.usersResource.error());
  readonly hasError = computed(() => this.usersResource.error() !== undefined);
  readonly totalResults = computed(() => {
    const value = this.usersResource.value();
    return value?.total || 0;
  });

  /**
   * Search users by name or email
   */
  searchUsers(query: string, page: number = 1, limit: number = 20): void {
    this.searchQuery.set(query);
    this.currentPage.set(page);
    this.pageLimit.set(limit);
    // Resource will reload automatically when query changes
  }

  /**
   * Clear search and reset state
   */
  clearSearch(): void {
    this.searchQuery.set('');
    this.currentPage.set(1);
  }
}
