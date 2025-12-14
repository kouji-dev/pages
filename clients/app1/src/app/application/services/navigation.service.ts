import { Injectable, inject, computed } from '@angular/core';
import { Router, ActivatedRoute, NavigationEnd, ActivatedRouteSnapshot } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { filter, map } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class NavigationService {
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);

  /**
   * Convert route paramMap to signal by traversing the route tree
   */
  private readonly routeParams = toSignal(
    this.router.events.pipe(
      filter((event) => event instanceof NavigationEnd),
      map(() => this.extractRouteParams()),
    ),
    { initialValue: this.extractRouteParams() },
  );

  /**
   * Convert query params to signal by traversing the route tree
   */
  private readonly queryParams = toSignal(
    this.router.events.pipe(
      filter((event) => event instanceof NavigationEnd),
      map(() => this.extractQueryParams()),
    ),
    { initialValue: this.extractQueryParams() },
  );

  /**
   * Extract route parameters from the route tree using DFS
   * Traverses from root to leaves (children only) to avoid infinite loops
   */
  private extractRouteParams(): {
    organizationId?: string;
    projectId?: string;
    issueId?: string;
    spaceId?: string;
    pageId?: string;
  } {
    const params: {
      organizationId?: string;
      projectId?: string;
      issueId?: string;
      spaceId?: string;
      pageId?: string;
    } = {};

    // Get the root route snapshot from router state
    const rootRoute = this.router.routerState.snapshot.root;
    const visited = new Set<ActivatedRouteSnapshot>();

    // DFS traversal to collect all route params (only traverse children, not parents)
    const traverse = (route: ActivatedRouteSnapshot | null): void => {
      if (!route || visited.has(route)) {
        return;
      }

      visited.add(route);

      // Extract organizationId
      if (route.paramMap.has('organizationId') && !params.organizationId) {
        params.organizationId = route.paramMap.get('organizationId') || undefined;
      }

      // Extract projectId
      if (route.paramMap.has('projectId') && !params.projectId) {
        params.projectId = route.paramMap.get('projectId') || undefined;
      }

      // Extract issueId
      if (route.paramMap.has('issueId') && !params.issueId) {
        params.issueId = route.paramMap.get('issueId') || undefined;
      }

      // Extract spaceId
      if (route.paramMap.has('spaceId') && !params.spaceId) {
        params.spaceId = route.paramMap.get('spaceId') || undefined;
      }

      // Extract pageId
      if (route.paramMap.has('pageId') && !params.pageId) {
        params.pageId = route.paramMap.get('pageId') || undefined;
      }

      // Traverse children only (DFS from root to leaves)
      if (route.children && route.children.length > 0) {
        for (const child of route.children) {
          traverse(child);
        }
      }
    };

    traverse(rootRoute);

    return params;
  }

  /**
   * Extract query parameters from the route tree using DFS
   * Traverses from root to leaves (children only) to avoid infinite loops
   * Merges query params from all active routes, with child routes overriding parent values
   */
  private extractQueryParams(): Record<string, string> {
    const queryParams: Record<string, string> = {};

    // Get the root route snapshot from router state
    const rootRoute = this.router.routerState.snapshot.root;
    const visited = new Set<ActivatedRouteSnapshot>();

    // DFS traversal to collect all query params (only traverse children, not parents)
    const traverse = (route: ActivatedRouteSnapshot | null): void => {
      if (!route || visited.has(route)) {
        return;
      }

      visited.add(route);

      // Merge query params from this route (child routes override parent values)
      if (route.queryParams && Object.keys(route.queryParams).length > 0) {
        Object.assign(queryParams, route.queryParams);
      }

      // Traverse children only (DFS from root to leaves)
      if (route.children && route.children.length > 0) {
        for (const child of route.children) {
          traverse(child);
        }
      }
    };

    traverse(rootRoute);

    return queryParams;
  }

  /**
   * Get current organization ID from route
   */
  readonly currentOrganizationId = computed(() => {
    return this.routeParams()?.organizationId || null;
  });

  /**
   * Get current project ID from route
   */
  readonly currentProjectId = computed(() => {
    return this.routeParams()?.projectId || null;
  });

  /**
   * Get current issue ID from route
   */
  readonly currentIssueId = computed(() => {
    return this.routeParams()?.issueId || null;
  });

  /**
   * Get current space ID from route
   */
  readonly currentSpaceId = computed(() => {
    return this.routeParams()?.spaceId || null;
  });

  /**
   * Get current page ID from route
   */
  readonly currentPageId = computed(() => {
    return this.routeParams()?.pageId || null;
  });

  /**
   * Get current tab from query params
   */
  readonly currentTab = computed(() => {
    return this.queryParams()?.['tab'] || null;
  });

  /**
   * Get the route path to the current organization's projects
   * Returns empty array if no organization is in route
   */
  currentOrganizationRoute(): string[] {
    const orgId = this.currentOrganizationId();
    if (!orgId) return [];
    return ['/app/organizations', orgId];
  }

  /**
   * Get the route path to the current organization's settings
   * Returns empty array if no organization is in route
   */
  currentOrganizationSettingsRoute(): string[] {
    const orgId = this.currentOrganizationId();
    if (!orgId) return [];
    return ['/app/organizations', orgId, 'settings'];
  }

  /**
   * Navigate to organizations list
   */
  navigateToOrganizations(): void {
    this.router.navigate(['/app/organizations']);
  }

  /**
   * Navigate to organization's projects
   */
  navigateToOrganizationProjects(organizationId: string): void {
    this.router.navigate(['/app/organizations', organizationId, 'projects']);
  }

  /**
   * Navigate to organization settings
   */
  navigateToOrganizationSettings(organizationId: string): void {
    this.router.navigate(['/app/organizations', organizationId, 'settings']);
  }

  /**
   * Navigate to project detail
   */
  navigateToProject(organizationId: string, projectId: string, tab?: string): void {
    const navigationExtras = tab ? { queryParams: { tab } } : {};
    this.router.navigate(
      ['/app/organizations', organizationId, 'projects', projectId],
      navigationExtras,
    );
  }

  /**
   * Navigate to project settings
   */
  navigateToProjectSettings(organizationId: string, projectId: string): void {
    this.router.navigate(['/app/organizations', organizationId, 'projects', projectId], {
      queryParams: { tab: 'settings' },
    });
  }

  /**
   * Navigate to issue detail
   */
  navigateToIssue(organizationId: string, projectId: string, issueId: string): void {
    this.router.navigate([
      '/app/organizations',
      organizationId,
      'projects',
      projectId,
      'issues',
      issueId,
    ]);
  }

  /**
   * Get route for organization's projects
   */
  getOrganizationProjectsRoute(organizationId: string): string[] {
    return ['/app/organizations', organizationId, 'projects'];
  }

  /**
   * Get route for organization settings
   */
  getOrganizationSettingsRoute(organizationId: string): string[] {
    return ['/app/organizations', organizationId, 'settings'];
  }

  /**
   * Get route for project detail
   */
  getProjectRoute(organizationId: string, projectId: string, tab?: string): string[] {
    return ['/app/organizations', organizationId, 'projects', projectId];
  }

  /**
   * Update query params for current route
   * Uses current route path to preserve route structure
   */
  updateQueryParams(params: Record<string, string | null>): void {
    const currentUrl = this.router.url.split('?')[0]; // Get current URL without query params
    this.router.navigate([currentUrl], {
      queryParams: params,
      queryParamsHandling: 'merge',
    });
  }

  /**
   * Get route for project settings
   */
  getProjectSettingsRoute(organizationId: string, projectId: string): string[] {
    return ['/app/organizations', organizationId, 'projects', projectId, 'settings'];
  }

  /**
   * Get route for issue detail
   */
  getIssueRoute(organizationId: string, projectId: string, issueId: string): string[] {
    return ['/app/organizations', organizationId, 'projects', projectId, 'issues', issueId];
  }

  /**
   * Navigate to organization's spaces
   */
  navigateToOrganizationSpaces(organizationId: string): void {
    this.router.navigate(['/app/organizations', organizationId, 'spaces']);
  }

  /**
   * Navigate to space detail
   */
  navigateToSpace(organizationId: string, spaceId: string): void {
    this.router.navigate(['/app/organizations', organizationId, 'spaces', spaceId]);
  }

  navigateToSpaceSettings(organizationId: string, spaceId: string): void {
    this.router.navigate(['/app/organizations', organizationId, 'spaces', spaceId, 'settings']);
  }

  /**
   * Navigate to page detail
   */
  navigateToPage(organizationId: string, spaceId: string, pageId: string): void {
    this.router.navigate([
      '/app/organizations',
      organizationId,
      'spaces',
      spaceId,
      'pages',
      pageId,
    ]);
  }

  /**
   * Get route for organization's spaces
   */
  getOrganizationSpacesRoute(organizationId: string): string[] {
    return ['/app/organizations', organizationId, 'spaces'];
  }

  /**
   * Get route for space detail
   */
  getSpaceRoute(organizationId: string, spaceId: string): string[] {
    return ['/app/organizations', organizationId, 'spaces', spaceId];
  }

  /**
   * Get route for page detail
   */
  getPageRoute(organizationId: string, spaceId: string, pageId: string): string[] {
    return ['/app/organizations', organizationId, 'spaces', spaceId, 'pages', pageId];
  }
}
