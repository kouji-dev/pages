import { Injectable, signal, inject, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

export interface Organization {
  id: string;
  name: string;
  slug: string;
  description?: string;
  memberCount?: number;
}

@Injectable({
  providedIn: 'root',
})
export class OrganizationService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/api/organizations`;

  // Current selected organization signal
  readonly currentOrganization = signal<Organization | null>(null);

  // User's organizations list signal
  readonly organizations = signal<Organization[]>([]);

  // Loading state signal
  readonly isLoading = signal(false);

  constructor() {
    // Load current organization from localStorage on initialization
    this.loadCurrentOrganizationFromStorage();

    // TODO: Load organizations from API when backend is ready
    // For now, using placeholder data
    this.loadOrganizations();
  }

  /**
   * Load user's organizations from API
   */
  loadOrganizations(): void {
    this.isLoading.set(true);

    // TODO: Replace with actual API call when backend is ready
    // this.http.get<Organization[]>(this.apiUrl).subscribe({
    //   next: (orgs) => {
    //     this.organizations.set(orgs);
    //     this.isLoading.set(false);
    //   },
    //   error: (error) => {
    //     console.error('Failed to load organizations:', error);
    //     this.isLoading.set(false);
    //   },
    // });

    // Placeholder data for now
    setTimeout(() => {
      this.organizations.set([
        {
          id: '1',
          name: 'Acme Corp',
          slug: 'acme-corp',
          description: 'Main organization',
          memberCount: 5,
        },
        {
          id: '2',
          name: 'Personal',
          slug: 'personal',
          description: 'Personal workspace',
          memberCount: 1,
        },
      ]);

      // Set first organization as current if none is set
      if (!this.currentOrganization()) {
        const firstOrg = this.organizations()[0];
        if (firstOrg) {
          this.switchOrganization(firstOrg.id);
        }
      }

      this.isLoading.set(false);
    }, 300);
  }

  /**
   * Switch to a different organization
   */
  switchOrganization(organizationId: string): void {
    const organization = this.organizations().find((org) => org.id === organizationId);
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
    return this.organizations();
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
   * Load current organization from localStorage
   */
  private loadCurrentOrganizationFromStorage(): void {
    try {
      const organizationId = localStorage.getItem('current_organization_id');
      if (organizationId) {
        // Organization will be set after loadOrganizations() completes
        // This is just to restore the ID preference
      }
    } catch (error) {
      console.error('Failed to load organization from localStorage:', error);
    }
  }
}
