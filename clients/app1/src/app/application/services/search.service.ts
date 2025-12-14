import { Injectable, inject, computed, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import { NavigationService } from './navigation.service';
import { OrganizationService, Organization } from './organization.service';
import { ProjectService, Project, ProjectListResponse } from './project.service';
import { SpaceService, Space, SpaceListResponse } from './space.service';

export type EntityType = 'issue' | 'page' | 'organization' | 'project' | 'space';

export interface SearchResultItem {
  entityType: EntityType;
  id: string;
  title: string;
  snippet: string | null;
  score?: number;
  projectId?: string | null;
  spaceId?: string | null;
  organizationId?: string | null;
}

export interface SearchResponse {
  items: SearchResultItem[];
  total: number;
  page: number;
  limit: number;
}

export interface SearchResultItemResponse {
  entity_type: 'issue' | 'page';
  id: string;
  title: string;
  snippet: string | null;
  score: number;
  project_id: string | null;
  space_id: string | null;
}

export interface SearchResponseResponse {
  items: SearchResultItemResponse[];
  total: number;
  page: number;
  limit: number;
}

export interface SearchFilters {
  query: string;
  type?: 'all' | 'issues' | 'pages';
  projectId?: string;
  spaceId?: string;
  page?: number;
  limit?: number;
  assigneeId?: string;
  reporterId?: string;
  status?: string;
  issueType?: string;
  priority?: string;
}

@Injectable({
  providedIn: 'root',
})
export class SearchService {
  private readonly http = inject(HttpClient);
  private readonly navigationService = inject(NavigationService);
  private readonly apiUrl = `${environment.apiUrl}/search`;

  // Search filters signal
  readonly filters = signal<SearchFilters>({
    query: '',
    type: 'all',
    page: 1,
    limit: 20,
  });

  // Search results resource using httpResource
  readonly searchResults = httpResource<SearchResponseResponse>(() => {
    const filters = this.filters();
    const query = filters.query.trim();

    // Don't search if query is empty
    if (!query) return undefined;

    const organizationId = this.navigationService.currentOrganizationId();
    if (!organizationId) return undefined;

    // Check what context we have
    const projectId = filters.projectId || this.navigationService.currentProjectId();
    const spaceId = filters.spaceId || this.navigationService.currentSpaceId();
    const searchType = filters.type || 'all';

    // API requires project_id for issues/all and space_id for pages/all
    // Only make the API call if we have the required context
    if (searchType === 'issues' && !projectId) {
      return undefined; // Can't search issues without project_id
    }
    if (searchType === 'pages' && !spaceId) {
      return undefined; // Can't search pages without space_id
    }
    if (searchType === 'all' && !projectId && !spaceId) {
      return undefined; // Can't search all without at least one context
    }

    let params = new HttpParams()
      .set('query', query)
      .set('type', searchType)
      .set('page', (filters.page || 1).toString())
      .set('limit', (filters.limit || 20).toString());

    // Add project_id if searching issues or all
    if (projectId && (searchType === 'issues' || searchType === 'all')) {
      params = params.set('project_id', projectId);
    }

    // Add space_id if searching pages or all
    if (spaceId && (searchType === 'pages' || searchType === 'all')) {
      params = params.set('space_id', spaceId);
    }

    // Add optional filters
    if (filters.assigneeId) {
      params = params.set('assignee_id', filters.assigneeId);
    }
    if (filters.reporterId) {
      params = params.set('reporter_id', filters.reporterId);
    }
    if (filters.status) {
      params = params.set('status', filters.status);
    }
    if (filters.issueType) {
      params = params.set('issue_type', filters.issueType);
    }
    if (filters.priority) {
      params = params.set('priority', filters.priority);
    }

    return `${this.apiUrl}?${params.toString()}`;
  });

  // Public accessors for search results
  readonly results = computed(() => {
    const value = this.searchResults.value();
    if (!value) return [];
    return value.items.map((item) => this.mapToSearchResult(item));
  });

  readonly totalResults = computed(() => {
    const value = this.searchResults.value();
    return value?.total || 0;
  });

  readonly currentPage = computed(() => {
    const value = this.searchResults.value();
    return value?.page || 1;
  });

  readonly totalPages = computed(() => {
    const value = this.searchResults.value();
    if (!value) return 0;
    return Math.ceil(value.total / value.limit);
  });

  readonly isLoading = computed(() => this.searchResults.isLoading());
  readonly error = computed(() => this.searchResults.error());
  readonly hasError = computed(() => this.searchResults.error() !== undefined);

  // Global search across all entity types
  private readonly organizationService = inject(OrganizationService);
  private readonly projectService = inject(ProjectService);
  private readonly spaceService = inject(SpaceService);

  /**
   * Perform global search across all entity types
   * Returns results grouped by entity type
   * All searches run in parallel for better performance
   */
  async searchGlobal(
    query: string,
    limit: number = 5,
  ): Promise<{
    issues: SearchResultItem[];
    pages: SearchResultItem[];
    organizations: SearchResultItem[];
    projects: SearchResultItem[];
    spaces: SearchResultItem[];
  }> {
    const trimmedQuery = query.trim();
    if (!trimmedQuery) {
      return {
        issues: [],
        pages: [],
        organizations: [],
        projects: [],
        spaces: [],
      };
    }

    const organizationId = this.navigationService.currentOrganizationId();
    const projectId = this.navigationService.currentProjectId();
    const spaceId = this.navigationService.currentSpaceId();

    // Prepare all search promises to run in parallel
    const searchPromises: Promise<void>[] = [];
    const results: {
      issues: SearchResultItem[];
      pages: SearchResultItem[];
      organizations: SearchResultItem[];
      projects: SearchResultItem[];
      spaces: SearchResultItem[];
    } = {
      issues: [],
      pages: [],
      organizations: [],
      projects: [],
      spaces: [],
    };

    // Search issues (if project context available)
    if (organizationId && projectId) {
      const issuesPromise = firstValueFrom(
        this.http.get<SearchResponseResponse>(
          `${this.apiUrl}?${new HttpParams()
            .set('query', trimmedQuery)
            .set('type', 'issues')
            .set('project_id', projectId)
            .set('page', '1')
            .set('limit', limit.toString())
            .toString()}`,
        ),
      )
        .then((searchResponse) => {
          const searchItems = searchResponse.items.map((item) => this.mapToSearchResult(item));
          results.issues = searchItems.slice(0, limit);
        })
        .catch((error) => {
          console.warn('Failed to search issues:', error);
        });
      searchPromises.push(issuesPromise);
    }

    // Search pages (if space context available)
    if (organizationId && spaceId) {
      const pagesPromise = firstValueFrom(
        this.http.get<SearchResponseResponse>(
          `${this.apiUrl}?${new HttpParams()
            .set('query', trimmedQuery)
            .set('type', 'pages')
            .set('space_id', spaceId)
            .set('page', '1')
            .set('limit', limit.toString())
            .toString()}`,
        ),
      )
        .then((searchResponse) => {
          const searchItems = searchResponse.items.map((item) => this.mapToSearchResult(item));
          results.pages = searchItems.slice(0, limit);
        })
        .catch((error) => {
          console.warn('Failed to search pages:', error);
        });
      searchPromises.push(pagesPromise);
    }

    // Search organizations (client-side from loaded list)
    // Always search organizations regardless of context
    const orgsPromise = Promise.resolve().then(() => {
      try {
        const orgs = this.organizationService.organizationsList();
        const filteredOrgs = orgs
          .filter(
            (org) =>
              org.name.toLowerCase().includes(trimmedQuery.toLowerCase()) ||
              org.slug.toLowerCase().includes(trimmedQuery.toLowerCase()) ||
              org.description?.toLowerCase().includes(trimmedQuery.toLowerCase()),
          )
          .slice(0, limit)
          .map((org) => this.mapOrganizationToSearchResult(org));
        results.organizations = filteredOrgs;
      } catch (error) {
        console.warn('Failed to search organizations:', error);
      }
    });
    searchPromises.push(orgsPromise);

    // Search projects (if organization context available)
    if (organizationId) {
      const projectsPromise = firstValueFrom(
        this.http.get<ProjectListResponse>(
          `${environment.apiUrl}/projects?${new HttpParams()
            .set('organization_id', organizationId)
            .set('search', trimmedQuery)
            .set('page', '1')
            .set('limit', limit.toString())
            .toString()}`,
        ),
      )
        .then((projectsResponse) => {
          results.projects = (projectsResponse.projects || [])
            .slice(0, limit)
            .map((p) => this.mapProjectToSearchResult(p));
        })
        .catch((error) => {
          console.warn('Failed to search projects:', error);
        });
      searchPromises.push(projectsPromise);
    }

    // Search spaces (if organization context available)
    if (organizationId) {
      const spacesPromise = firstValueFrom(
        this.http.get<SpaceListResponse>(
          `${environment.apiUrl}/spaces?${new HttpParams()
            .set('organization_id', organizationId)
            .set('search', trimmedQuery)
            .set('page', '1')
            .set('limit', limit.toString())
            .toString()}`,
        ),
      )
        .then((spacesResponse) => {
          results.spaces = (spacesResponse.spaces || [])
            .slice(0, limit)
            .map((s) => this.mapSpaceToSearchResult(s));
        })
        .catch((error) => {
          console.warn('Failed to search spaces:', error);
        });
      searchPromises.push(spacesPromise);
    }

    // Wait for all searches to complete in parallel
    await Promise.allSettled(searchPromises);

    return results;
  }

  private mapOrganizationToSearchResult(org: Organization): SearchResultItem {
    return {
      entityType: 'organization',
      id: org.id,
      title: org.name,
      snippet: org.description || null,
      organizationId: org.id,
    };
  }

  private mapProjectToSearchResult(project: any): SearchResultItem {
    return {
      entityType: 'project',
      id: project.id,
      title: project.name,
      snippet: project.description || null,
      organizationId: project.organization_id,
    };
  }

  private mapSpaceToSearchResult(space: any): SearchResultItem {
    return {
      entityType: 'space',
      id: space.id,
      title: space.name,
      snippet: space.description || null,
      organizationId: space.organization_id,
    };
  }

  /**
   * Map backend response (snake_case) to frontend model (camelCase)
   */
  private mapToSearchResult(response: SearchResultItemResponse): SearchResultItem {
    return {
      entityType: response.entity_type,
      id: response.id,
      title: response.title,
      snippet: response.snippet,
      score: response.score,
      projectId: response.project_id,
      spaceId: response.space_id,
    };
  }

  /**
   * Set search filters and trigger search
   */
  search(filters: Partial<SearchFilters>): void {
    this.filters.update((current) => ({ ...current, ...filters }));
    // Resource will reload automatically when filters change
  }

  /**
   * Reset search filters
   */
  reset(): void {
    this.filters.set({
      query: '',
      type: 'all',
      page: 1,
      limit: 20,
    });
  }

  /**
   * Reload search results
   */
  reload(): void {
    this.searchResults.reload();
  }
}
