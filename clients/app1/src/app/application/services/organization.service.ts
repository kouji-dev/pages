import { Injectable, inject, computed } from '@angular/core';
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

  // Single organization resource using httpResource with computed URL
  // Organization ID is now URL-driven via NavigationService
  private readonly organizationResource = httpResource<OrganizationResponse>(() => {
    const id = this.navigationService.currentOrganizationId();
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

  // Organization ID is now URL-driven via NavigationService
  // No need for sync effect - the resource automatically reacts to URL changes

  /**
   * Reload organizations from API
   */
  loadOrganizations(): void {
    this.organizations.reload();
  }

  /**
   * Reload current organization from API
   * Useful when organization data needs to be refreshed after updates
   */
  reloadCurrentOrganization(): void {
    this.organizationResource.reload();
  }

  /**
   * Switch to a different organization (from selector)
   * Navigates to the organization's projects page
   * The organization resource will automatically reload when the URL changes
   */
  switchOrganization(organizationId: string): void {
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
    const currentOrgId = this.navigationService.currentOrganizationId();
    if (currentOrgId === id) {
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
    const currentOrgId = this.navigationService.currentOrganizationId();
    if (currentOrgId === id) {
      const orgs = this.organizationsList();
      if (orgs.length > 0) {
        this.switchOrganization(orgs[0].id);
      } else {
        // Navigate to organizations list if no organizations remain
        this.navigationService.navigateToOrganizations();
      }
    }
  }
}
