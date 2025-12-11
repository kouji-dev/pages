import { Injectable, signal, inject, computed } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import { NavigationService } from './navigation.service';

export interface Space {
  id: string;
  name: string;
  key: string;
  description?: string;
  organizationId: string;
  pageCount?: number;
  recentPages?: RecentPage[];
  createdAt?: string;
  updatedAt?: string;
}

export interface RecentPage {
  id: string;
  title: string;
  slug: string;
  updatedAt: string;
}

export interface CreateSpaceRequest {
  name: string;
  key?: string;
  description?: string;
  organization_id: string;
}

export interface UpdateSpaceRequest {
  name?: string;
  description?: string;
}

export interface SpaceListItemResponse {
  id: string;
  organization_id: string;
  name: string;
  key: string;
  description?: string;
  page_count: number;
  created_at: string;
  updated_at?: string;
}

export interface SpaceResponse {
  id: string;
  organization_id: string;
  name: string;
  key: string;
  description?: string;
  page_count: number;
  recent_pages: Array<{
    id: string;
    title: string;
    slug: string;
    updated_at: string;
  }>;
  created_at: string;
  updated_at?: string;
}

export interface SpaceListResponse {
  spaces: SpaceListItemResponse[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

@Injectable({
  providedIn: 'root',
})
export class SpaceService {
  private readonly http = inject(HttpClient);
  private readonly navigationService = inject(NavigationService);
  private readonly apiUrl = `${environment.apiUrl}/spaces`;

  // Spaces list resource using httpResource - driven by URL organizationId
  readonly spaces = httpResource<SpaceListResponse>(() => {
    const orgId = this.navigationService.currentOrganizationId();
    if (!orgId) return undefined; // Don't load if no organization

    const params = new HttpParams().set('organization_id', orgId);
    return `${this.apiUrl}?${params.toString()}`;
  });

  // Public accessors for spaces list
  readonly spacesList = computed(() => {
    const value = this.spaces.value();
    if (!value) return [];
    // Handle both array response (legacy) and SpaceListResponse
    if (Array.isArray(value)) {
      return value;
    }
    // Map SpaceListItemResponse to Space (snake_case to camelCase)
    return (value.spaces || []).map((s) => this.mapToSpace(s));
  });

  /**
   * Map backend response (snake_case) to frontend model (camelCase)
   */
  private mapToSpace(response: SpaceListItemResponse | SpaceResponse): Space {
    const recentPages =
      'recent_pages' in response
        ? response.recent_pages.map((p) => ({
            id: p.id,
            title: p.title,
            slug: p.slug,
            updatedAt: p.updated_at,
          }))
        : undefined;

    return {
      id: response.id,
      name: response.name,
      key: response.key,
      description: response.description,
      organizationId: response.organization_id,
      pageCount: response.page_count,
      recentPages,
      createdAt: response.created_at,
      updatedAt: response.updated_at,
    };
  }

  readonly isLoading = computed(() => this.spaces.isLoading());
  readonly error = computed(() => this.spaces.error());
  readonly hasError = computed(() => this.spaces.error() !== undefined);

  // Single space resource using httpResource - driven by URL spaceId
  private readonly spaceResource = httpResource<SpaceResponse>(() => {
    const id = this.navigationService.currentSpaceId();
    return id ? `${this.apiUrl}/${id}` : undefined;
  });

  // Current space computed from resource (mapped to camelCase)
  readonly currentSpace = computed(() => {
    const response = this.spaceResource.value();
    if (!response) return undefined;
    return this.mapToSpace(response);
  });

  readonly isFetchingSpace = computed(() => this.spaceResource.isLoading());
  readonly spaceError = computed(() => this.spaceResource.error());
  readonly hasSpaceError = computed(() => this.spaceResource.error() !== undefined);

  /**
   * Get spaces by organization ID
   */
  getSpacesByOrganization(organizationId: string): Space[] {
    return this.spacesList().filter((space) => space.organizationId === organizationId);
  }

  /**
   * Create a new space
   */
  async createSpace(request: CreateSpaceRequest): Promise<Space> {
    const response = await firstValueFrom(this.http.post<SpaceResponse>(this.apiUrl, request));
    if (!response) {
      throw new Error('Failed to create space: No response from server');
    }

    // Reload spaces list
    this.spaces.reload();

    return this.mapToSpace(response);
  }

  /**
   * Update a space
   */
  async updateSpace(spaceId: string, request: UpdateSpaceRequest): Promise<Space> {
    const response = await firstValueFrom(
      this.http.put<SpaceResponse>(`${this.apiUrl}/${spaceId}`, request),
    );
    if (!response) {
      throw new Error('Failed to update space: No response from server');
    }

    // Reload spaces list and current space
    this.spaces.reload();
    this.spaceResource.reload();

    return this.mapToSpace(response);
  }

  /**
   * Delete a space
   */
  async deleteSpace(spaceId: string): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.apiUrl}/${spaceId}`));

    // Reload spaces list
    this.spaces.reload();
  }

  /**
   * Fetch a specific space by ID
   */
  fetchSpace(spaceId: string): void {
    // Space ID is now URL-driven via NavigationService
    // This method is kept for backward compatibility
    // The spaceResource will automatically load when URL spaceId changes
  }
}
