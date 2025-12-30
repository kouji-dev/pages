import { Injectable, signal, inject, computed, effect } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import { NavigationService } from './navigation.service';
import { SpaceService } from './space.service';
import { ProjectService } from './project.service';
import { ListItemData, IconName } from 'shared-ui';

export interface Favorite {
  id: string;
  type: 'project' | 'space' | 'page';
  itemId: string;
  title: string;
  icon?: IconName;
  iconColor?: string;
  rightIcon?: IconName;
  organizationId: string;
  createdAt?: string;
}

export interface FavoriteApiResponse {
  id: string;
  user_id: string;
  entity_type: 'project' | 'space' | 'page';
  entity_id: string;
  created_at: string;
  updated_at: string;
}

export interface FavoriteListApiResponse {
  favorites: FavoriteApiResponse[];
  total: number;
}

@Injectable({
  providedIn: 'root',
})
export class FavoriteService {
  private readonly http = inject(HttpClient);
  private readonly navigationService = inject(NavigationService);
  private readonly spaceService = inject(SpaceService);
  private readonly projectService = inject(ProjectService);
  private readonly apiUrl = `${environment.apiUrl}/users/me/favorites`;

  // Favorites signal
  private readonly _favorites = signal<Favorite[]>([]);
  readonly favorites = this._favorites.asReadonly();

  readonly isLoading = signal(false);
  readonly error = signal<Error | null>(null);

  constructor() {
    // Load favorites when organization changes
    effect(() => {
      const orgId = this.navigationService.currentOrganizationId();
      if (orgId) {
        this.loadFavorites(orgId);
      } else {
        this._favorites.set([]);
      }
    });
  }

  /**
   * Load favorites for current organization
   */
  async loadFavorites(organizationId: string): Promise<void> {
    this.isLoading.set(true);
    this.error.set(null);

    try {
      // Try to fetch from API first
      try {
        const response = await firstValueFrom(this.http.get<FavoriteListApiResponse>(this.apiUrl));
        // Filter favorites by organization and enrich with entity details
        const favorites = await Promise.all(
          response.favorites
            .filter((f) => {
              // We need to check if the entity belongs to this organization
              // For now, we'll fetch all and filter by checking entity details
              return true; // Will filter after fetching entity details
            })
            .map(async (f) => await this.enrichFavorite(f, organizationId)),
        );
        // Filter out favorites that don't belong to this organization
        const orgFavorites = favorites.filter(
          (f) => f !== null && f.organizationId === organizationId,
        ) as Favorite[];
        this._favorites.set(orgFavorites);
      } catch (apiError: any) {
        // If API doesn't exist yet, fall back to local storage
        if (apiError.status === 404 || apiError.status === 0) {
          const localFavorites = this.loadFromLocalStorage(organizationId);
          this._favorites.set(localFavorites);
        } else {
          throw apiError;
        }
      }
    } catch (error) {
      console.error('Error loading favorites:', error);
      this.error.set(error instanceof Error ? error : new Error('Failed to load favorites'));
      // Fall back to local storage on error
      const orgId = this.navigationService.currentOrganizationId();
      if (orgId) {
        const localFavorites = this.loadFromLocalStorage(orgId);
        this._favorites.set(localFavorites);
      }
    } finally {
      this.isLoading.set(false);
    }
  }

  /**
   * Add a favorite
   */
  async addFavorite(
    type: 'project' | 'space' | 'page',
    itemId: string,
    title: string,
    organizationId: string,
    icon?: IconName,
    iconColor?: string,
    rightIcon?: IconName,
  ): Promise<Favorite> {
    try {
      // Try to save to API
      try {
        const response = await firstValueFrom(
          this.http.post<FavoriteApiResponse>(this.apiUrl, {
            entity_type: type,
            entity_id: itemId,
          }),
        );
        // Enrich with entity details
        const enrichedFavorite = await this.enrichFavorite(response, organizationId);
        if (enrichedFavorite) {
          this._favorites.update((favs) => [...favs, enrichedFavorite]);
          return enrichedFavorite;
        } else {
          throw new Error('Failed to enrich favorite');
        }
      } catch (apiError: any) {
        // If API doesn't exist, save to local storage
        if (apiError.status === 404 || apiError.status === 0) {
          const favorite: Favorite = {
            id: `${type}-${itemId}`,
            type,
            itemId,
            title,
            icon: icon || this.getDefaultIcon(type),
            iconColor: iconColor || '#fbbf24',
            rightIcon: rightIcon || this.getDefaultRightIcon(type),
            organizationId,
            createdAt: new Date().toISOString(),
          };
          this.saveToLocalStorage(favorite);
          this._favorites.update((favs) => [...favs, favorite]);
          return favorite;
        } else {
          throw apiError;
        }
      }
    } catch (error) {
      console.error('Error adding favorite:', error);
      // Fall back to local storage
      const favorite: Favorite = {
        id: `${type}-${itemId}`,
        type,
        itemId,
        title,
        icon: icon || this.getDefaultIcon(type),
        iconColor: iconColor || '#fbbf24',
        rightIcon: rightIcon || this.getDefaultRightIcon(type),
        organizationId,
        createdAt: new Date().toISOString(),
      };
      this.saveToLocalStorage(favorite);
      this._favorites.update((favs) => [...favs, favorite]);
      return favorite;
    }
  }

  /**
   * Remove a favorite
   */
  async removeFavorite(favoriteId: string): Promise<void> {
    try {
      // Try to delete from API
      try {
        await firstValueFrom(this.http.delete(`${this.apiUrl}/${favoriteId}`));
      } catch (apiError: any) {
        // If API doesn't exist, remove from local storage
        if (apiError.status === 404 || apiError.status === 0) {
          this.removeFromLocalStorage(favoriteId);
        } else {
          throw apiError;
        }
      }
    } catch (error) {
      console.error('Error removing favorite:', error);
      // Fall back to local storage
      this.removeFromLocalStorage(favoriteId);
    }

    this._favorites.update((favs) => favs.filter((f) => f.id !== favoriteId));
  }

  /**
   * Check if an item is favorited
   */
  isFavorited(type: 'project' | 'space' | 'page', itemId: string): boolean {
    return this.favorites().some((f) => f.type === type && f.itemId === itemId);
  }

  /**
   * Get favorites as ListItemData for sidebar
   */
  readonly favoritesItems = computed<ListItemData[]>(() => {
    const orgId = this.navigationService.currentOrganizationId();
    if (!orgId) {
      return [];
    }

    return this.favorites()
      .filter((f) => f.organizationId === orgId)
      .map((favorite) => ({
        id: favorite.id,
        label: favorite.title,
        icon: (favorite.icon || 'star') as IconName,
        iconColor: favorite.iconColor || '#fbbf24',
        rightIcon: favorite.rightIcon ? (favorite.rightIcon as IconName) : undefined,
        routerLink: this.getRouterLink(favorite),
      }));
  });

  /**
   * Get router link for a favorite
   */
  private getRouterLink(favorite: Favorite): string[] {
    const orgId = favorite.organizationId;
    switch (favorite.type) {
      case 'project':
        return this.navigationService.getProjectRoute(orgId, favorite.itemId);
      case 'space':
        return this.navigationService.getSpaceRoute(orgId, favorite.itemId);
      case 'page':
        // For pages, we'd need spaceId - this is a limitation
        // We could store spaceId in the favorite if needed
        return ['/app/organizations', orgId, 'spaces', favorite.itemId];
      default:
        return ['/app/organizations', orgId];
    }
  }

  /**
   * Get default icon for favorite type
   */
  private getDefaultIcon(type: 'project' | 'space' | 'page'): IconName {
    switch (type) {
      case 'project':
        return 'kanban';
      case 'space':
        return 'file-text';
      case 'page':
        return 'file-text';
    }
  }

  /**
   * Get default right icon for favorite type
   */
  private getDefaultRightIcon(type: 'project' | 'space' | 'page'): IconName {
    switch (type) {
      case 'project':
        return 'kanban';
      case 'space':
        return 'file-text';
      case 'page':
        return 'file-text';
    }
  }

  /**
   * Enrich favorite API response with entity details (title, icon, etc.)
   */
  private async enrichFavorite(
    apiResponse: FavoriteApiResponse,
    organizationId: string,
  ): Promise<Favorite | null> {
    try {
      let title = '';
      let orgId = organizationId;
      let icon: IconName | undefined;
      let iconColor: string | undefined;
      let rightIcon: IconName | undefined;

      switch (apiResponse.entity_type) {
        case 'project': {
          const project = this.projectService.getProjectById(apiResponse.entity_id);
          if (project) {
            title = project.name;
            orgId = project.organizationId;
            icon = 'kanban';
            rightIcon = 'kanban';
          } else {
            // Project not found in cache, skip this favorite
            return null;
          }
          break;
        }
        case 'space': {
          const space = this.spaceService.getSpaceById(apiResponse.entity_id);
          if (space) {
            title = space.name;
            orgId = space.organizationId;
            icon = space.icon ? (space.icon as IconName) : 'book';
            rightIcon = 'book';
          } else {
            // Space not found in cache, skip this favorite
            return null;
          }
          break;
        }
        case 'page': {
          // For pages, we'd need to fetch from space service
          // This is more complex - for now, use a generic approach
          title = `Page ${apiResponse.entity_id.substring(0, 8)}`;
          icon = 'file-text';
          rightIcon = 'file-text';
          // Note: Pages don't have organizationId directly, they're under spaces
          // We might need to store spaceId in favorites or fetch page details
          break;
        }
      }

      return {
        id: apiResponse.id,
        type: apiResponse.entity_type,
        itemId: apiResponse.entity_id,
        title,
        icon: icon || this.getDefaultIcon(apiResponse.entity_type),
        iconColor: iconColor || '#fbbf24',
        rightIcon: rightIcon || this.getDefaultRightIcon(apiResponse.entity_type),
        organizationId: orgId,
        createdAt: apiResponse.created_at,
      };
    } catch (error) {
      console.error('Error enriching favorite:', error);
      return null;
    }
  }

  /**
   * Load favorites from local storage
   */
  private loadFromLocalStorage(organizationId: string): Favorite[] {
    try {
      const key = `favorites_${organizationId}`;
      const stored = localStorage.getItem(key);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (error) {
      console.error('Error loading favorites from localStorage:', error);
    }
    return [];
  }

  /**
   * Save favorite to local storage
   */
  private saveToLocalStorage(favorite: Favorite): void {
    try {
      const key = `favorites_${favorite.organizationId}`;
      const current = this.loadFromLocalStorage(favorite.organizationId);
      const updated = [...current, favorite];
      localStorage.setItem(key, JSON.stringify(updated));
    } catch (error) {
      console.error('Error saving favorite to localStorage:', error);
    }
  }

  /**
   * Remove favorite from local storage
   */
  private removeFromLocalStorage(favoriteId: string): void {
    try {
      const orgId = this.navigationService.currentOrganizationId();
      if (!orgId) return;

      const key = `favorites_${orgId}`;
      const current = this.loadFromLocalStorage(orgId);
      const updated = current.filter((f) => f.id !== favoriteId);
      localStorage.setItem(key, JSON.stringify(updated));
    } catch (error) {
      console.error('Error removing favorite from localStorage:', error);
    }
  }

  /**
   * Reload favorites
   */
  reload(): void {
    const orgId = this.navigationService.currentOrganizationId();
    if (orgId) {
      this.loadFavorites(orgId);
    }
  }
}
