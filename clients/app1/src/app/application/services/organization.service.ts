import { Injectable, signal, inject, computed, effect } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { NavigationService } from './navigation.service';

export interface Organization {
  id: string;
  name: string;
  slug: string;
  description?: string;
  memberCount?: number;
}

export interface OrganizationListItemResponse {
  id: string;
  name: string;
  slug: string;
  description?: string;
  member_count: number;
  created_at: string;
  updated_at?: string;
}

export interface OrganizationResponse {
  id: string;
  name: string;
  slug: string;
  description?: string;
  member_count: number;
  created_at: string;
  updated_at?: string;
}

export interface OrganizationListResponse {
  organizations: OrganizationListItemResponse[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface CreateOrganizationRequest {
  name: string;
  slug: string;
  description?: string;
}

@Injectable({
  providedIn: 'root',
})
export class OrganizationService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/organizations`;
  private readonly navigationService = inject(NavigationService);

  // Organizations list resource using httpResource
  readonly organizations = httpResource<OrganizationListResponse>(() => this.apiUrl);

  // Public accessors for organizations list
  readonly organizationsList = computed(() => {
    const value = this.organizations.value();
    if (!value) return [];
    // Handle both array response (legacy) and OrganizationListResponse
    if (Array.isArray(value)) {
      return value;
    }
    // Map OrganizationListItemResponse to Organization (snake_case to camelCase)
    return (value.organizations || []).map((org) => this.mapToOrganization(org));
  });

  readonly isLoading = computed(() => this.organizations.isLoading());
  readonly error = computed(() => this.organizations.error());
  readonly hasError = computed(() => this.organizations.error() !== undefined);

  // Current organization ID signal
  private readonly currentOrganizationId = signal<string | null>(null);

  // Public accessor for current organization ID
  readonly currentOrganizationIdSignal = computed(() => this.currentOrganizationId());

  // Single organization resource using httpResource with computed URL
  private readonly organizationResource = httpResource<OrganizationResponse>(() => {
    const id = this.currentOrganizationId();
    return id ? `${this.apiUrl}/${id}` : undefined;
  });

  // Current organization computed from resource (mapped to camelCase)
  readonly currentOrganization = computed(() => {
    const response = this.organizationResource.value();
    if (!response) return undefined;
    // Map OrganizationResponse to Organization (snake_case to camelCase)
    return this.mapOrganizationResponseToOrganization(response);
  });

  /**
   * Map backend response (snake_case) to frontend model (camelCase)
   */
  private mapToOrganization(response: OrganizationListItemResponse): Organization {
    return {
      id: response.id,
      name: response.name,
      slug: response.slug,
      description: response.description,
      memberCount: response.member_count,
    };
  }

  /**
   * Map OrganizationResponse (snake_case) to Organization (camelCase)
   */
  private mapOrganizationResponseToOrganization(response: OrganizationResponse): Organization {
    return {
      id: response.id,
      name: response.name,
      slug: response.slug,
      description: response.description,
      memberCount: response.member_count,
    };
  }

  // Public accessors for current organization
  readonly isFetchingOrganization = computed(() => this.organizationResource.isLoading());
  readonly organizationError = computed(() => this.organizationResource.error());
  readonly hasOrganizationError = computed(() => this.organizationResource.error() !== undefined);

  // Effect to sync current organization with URL
  private readonly syncOrganizationFromUrlEffect = effect(() => {
    const urlOrgId = this.navigationService.currentOrganizationId();

    if (urlOrgId) {
      // URL has an organization ID - fetch and set it
      const currentOrgId = this.currentOrganizationId();

      // Only fetch if it's different from current
      if (currentOrgId !== urlOrgId) {
        const orgs = this.organizationsList();
        const org = orgs.find((o) => o.id === urlOrgId);

        if (org) {
          // Organization is already in the list, just set it
          this.setCurrentOrganization(urlOrgId, org);
        } else {
          // Organization not in list, fetch it
          this.fetchOrganization(urlOrgId);
        }
      }
    } else {
      // No organization in URL - try to restore from storage or use first available
      const orgs = this.organizationsList();
      const storedOrgId = this.getStoredCurrentOrganizationId();

      if (orgs.length > 0 && !this.currentOrganizationId()) {
        if (storedOrgId) {
          const org = orgs.find((o) => o.id === storedOrgId);
          if (org) {
            this.setCurrentOrganization(storedOrgId, org);
            return;
          }
        }
        // Otherwise, set the first organization as current
        this.setCurrentOrganization(orgs[0].id, orgs[0]);
      }
    }
  });

  /**
   * Reload organizations from API
   */
  loadOrganizations(): void {
    this.organizations.reload();
  }

  /**
   * Fetch a single organization by ID using httpResource
   */
  fetchOrganization(id: string): void {
    this.currentOrganizationId.set(id);
    // Resource will reload automatically when ID changes
  }

  /**
   * Set current organization without navigation
   * Used internally and by components that need to set org before navigating
   */
  setCurrentOrganization(organizationId: string, organization?: Organization): void {
    const org = organization || this.organizationsList().find((o) => o.id === organizationId);
    if (org) {
      this.currentOrganizationId.set(organizationId);
      this.persistCurrentOrganizationToStorage(org);
    }
  }

  /**
   * Switch to a different organization (from selector)
   * Navigates to the organization's projects page, which will trigger URL-driven sync
   */
  switchOrganization(organizationId: string): void {
    // Navigation will be handled by NavigationService
    // The URL change will trigger syncOrganizationFromUrlEffect
    this.navigationService.navigateToOrganizationProjects(organizationId);
  }

  /**
   * Get current organization signal
   * Returns readonly signal - consumers can convert to Observable using toObservable() if needed
   */
  getCurrentOrganization(): typeof this.currentOrganization {
    return this.currentOrganization;
  }

  /**
   * Get all organizations signal
   * Returns readonly signal - consumers can convert to Observable using toObservable() if needed
   */
  getOrganizations(): typeof this.organizationsList {
    return this.organizationsList;
  }

  /**
   * Persist current organization to localStorage
   */
  private persistCurrentOrganizationToStorage(organization: Organization): void {
    try {
      localStorage.setItem('current_organization_id', organization.id);
    } catch (error) {
      console.error('Failed to persist organization to localStorage:', error);
    }
  }

  /**
   * Get stored current organization ID from localStorage
   */
  private getStoredCurrentOrganizationId(): string | null {
    try {
      return localStorage.getItem('current_organization_id');
    } catch (error) {
      console.error('Failed to load organization ID from localStorage:', error);
      return null;
    }
  }

  /**
   * Create a new organization
   */
  async createOrganization(request: CreateOrganizationRequest): Promise<Organization> {
    const response = await this.http.post<OrganizationResponse>(this.apiUrl, request).toPromise();
    if (!response) {
      throw new Error('Failed to create organization: No response from server');
    }

    // Reload organizations to get updated list
    this.loadOrganizations();

    // Map response to Organization (snake_case to camelCase)
    return this.mapOrganizationResponseToOrganization(response);
  }

  /**
   * Update an organization
   */
  async updateOrganization(id: string, updates: Partial<Organization>): Promise<Organization> {
    const response = await this.http
      .put<OrganizationResponse>(`${this.apiUrl}/${id}`, updates)
      .toPromise();
    if (!response) {
      throw new Error('Failed to update organization: No response from server');
    }

    // Reload organizations list and current organization to get updated data
    this.loadOrganizations();
    if (this.currentOrganizationId() === id) {
      this.organizationResource.reload();
    }

    // Map response to Organization (snake_case to camelCase)
    return this.mapOrganizationResponseToOrganization(response);
  }

  /**
   * Delete an organization
   */
  async deleteOrganization(id: string): Promise<void> {
    await this.http.delete(`${this.apiUrl}/${id}`).toPromise();

    // Reload organizations to get updated list
    this.loadOrganizations();

    // If deleted organization was current, switch to another one
    if (this.currentOrganizationId() === id) {
      const orgs = this.organizationsList();
      if (orgs.length > 0) {
        this.switchOrganization(orgs[0].id);
      } else {
        this.currentOrganizationId.set(null);
      }
    }
  }
}
