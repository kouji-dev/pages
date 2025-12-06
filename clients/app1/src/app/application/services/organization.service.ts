import { Injectable, signal, inject, computed, effect } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { environment } from '../../../environments/environment';

export interface Organization {
  id: string;
  name: string;
  slug: string;
  description?: string;
  memberCount?: number;
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
  private readonly apiUrl = `${environment.apiUrl}/api/organizations`;

  // Organizations resource using httpResource (mocked by mockApiInterceptor until backend is ready)
  // httpResource expects a function that returns a URL string or HttpResourceRequest
  readonly organizations = httpResource(() => this.apiUrl);

  // Public accessors for easier access
  readonly organizationsList = computed(() => {
    const value = this.organizations.value();
    return Array.isArray(value) ? value : [];
  });
  readonly isLoading = computed(() => this.organizations.isLoading());
  readonly error = computed(() => this.organizations.error());
  readonly hasError = computed(() => this.organizations.error() !== undefined);

  // Current selected organization signal
  readonly currentOrganization = signal<Organization | null>(null);

  constructor() {
    // Set current organization after organizations are loaded
    effect(() => {
      const orgs = this.organizationsList();
      const currentOrgId = this.getStoredCurrentOrganizationId();

      if (orgs.length > 0) {
        // If we have a stored organization ID, try to restore it
        if (currentOrgId) {
          const org = orgs.find((o) => o.id === currentOrgId);
          if (org) {
            this.currentOrganization.set(org);
            return;
          }
        }

        // Otherwise, set the first organization as current
        if (!this.currentOrganization()) {
          this.switchOrganization(orgs[0].id);
        }
      }
    });
  }

  /**
   * Reload organizations from API
   */
  loadOrganizations(): void {
    this.organizations.reload();
  }

  /**
   * Switch to a different organization
   */
  switchOrganization(organizationId: string): void {
    const organization = this.organizationsList().find((org) => org.id === organizationId);
    if (organization) {
      this.currentOrganization.set(organization);
      this.persistCurrentOrganizationToStorage(organization);
    }
  }

  /**
   * Get current organization
   */
  getCurrentOrganization(): Organization | null {
    return this.currentOrganization();
  }

  /**
   * Get all organizations
   */
  getOrganizations(): Organization[] {
    return this.organizationsList();
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
   * Uses HTTP POST (mocked by mockApiInterceptor until backend is ready)
   */
  async createOrganization(request: CreateOrganizationRequest): Promise<Organization> {
    const response = await this.http.post<Organization>(this.apiUrl, request).toPromise();
    if (!response) {
      throw new Error('Failed to create organization: No response from server');
    }

    // Reload organizations to get updated list
    this.loadOrganizations();

    return response;
  }

  /**
   * Update an organization
   * Uses HTTP PUT/PATCH (mocked by mockApiInterceptor until backend is ready)
   */
  async updateOrganization(id: string, updates: Partial<Organization>): Promise<Organization> {
    const response = await this.http.put<Organization>(`${this.apiUrl}/${id}`, updates).toPromise();
    if (!response) {
      throw new Error('Failed to update organization: No response from server');
    }

    // Reload organizations to get updated list
    this.loadOrganizations();

    return response;
  }

  /**
   * Delete an organization
   * Uses HTTP DELETE (mocked by mockApiInterceptor until backend is ready)
   */
  async deleteOrganization(id: string): Promise<void> {
    await this.http.delete(`${this.apiUrl}/${id}`).toPromise();

    // Reload organizations to get updated list
    this.loadOrganizations();

    // If deleted organization was current, clear it
    if (this.currentOrganization()?.id === id) {
      const orgs = this.organizationsList();
      if (orgs.length > 0) {
        this.switchOrganization(orgs[0].id);
      } else {
        this.currentOrganization.set(null);
      }
    }
  }
}
