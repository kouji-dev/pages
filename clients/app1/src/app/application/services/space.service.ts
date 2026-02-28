import { Injectable, signal, inject, computed } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import { NavigationService } from './navigation.service';
import { IssueUser } from './issue.service';

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
  status?: 'draft' | 'in-review' | 'published';
  owner?: IssueUser;
  viewCount?: number;
  lastUpdated?: string;
  icon?: string;
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
  icon?: string;
  status?: string;
  view_count?: number;
  page_count: number;
  owner?: { id: string; name: string; email?: string; avatar_url?: string | null };
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

  // Search query signal for filtering
  readonly searchQuery = signal<string>('');

  // Spaces list resource using httpResource - driven by URL organizationId and search query
  readonly spaces = httpResource<SpaceListResponse>(() => {
    const orgId = this.navigationService.currentOrganizationId();
    if (!orgId) return undefined; // Don't load if no organization

    let params = new HttpParams().set('organization_id', orgId);
    const search = this.searchQuery().trim();
    if (search) {
      params = params.set('search', search);
    }
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

    const owner: IssueUser | undefined =
      'owner' in response && response.owner
        ? {
            id: response.owner.id,
            name: response.owner.name,
            avatar_url: response.owner.avatar_url,
          }
        : undefined;

    const status =
      'status' in response && response.status ? (response.status as Space['status']) : undefined;

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
      status,
      owner,
      viewCount: 'view_count' in response ? response.view_count : undefined,
      lastUpdated: response.updated_at ? this.formatRelativeTime(response.updated_at) : undefined,
      icon: 'icon' in response ? (response.icon ?? undefined) : undefined,
    };
  }

  private formatRelativeTime(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMinutes = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);
    const diffWeeks = Math.floor(diffDays / 7);

    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    if (diffWeeks < 4) return `${diffWeeks}w ago`;
    return date.toLocaleDateString();
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
   * Get space by ID (from cached list)
   */
  getSpaceById(spaceId: string): Space | undefined {
    return this.spacesList().find((space) => space.id === spaceId);
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

  /**
   * Reload current space
   */
  reloadCurrentSpace(): void {
    this.spaceResource.reload();
  }
}
