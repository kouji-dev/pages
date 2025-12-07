import { Injectable, signal, inject, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { environment } from '../../../environments/environment';

export interface OrganizationMember {
  user_id: string;
  organization_id: string;
  role: 'admin' | 'member' | 'viewer';
  user_name: string;
  user_email: string;
  avatar_url?: string;
  joined_at: string;
}

export interface OrganizationMemberList {
  members: OrganizationMember[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface AddMemberRequest {
  user_id: string;
  role: 'admin' | 'member' | 'viewer';
}

export interface UpdateMemberRoleRequest {
  role: 'admin' | 'member' | 'viewer';
}

@Injectable({
  providedIn: 'root',
})
export class OrganizationMembersService {
  private readonly http = inject(HttpClient);

  // Base URL pattern for organization members (includes /members)
  private readonly membersApiUrl = (organizationId: string): string =>
    `${environment.apiUrl}/api/v1/organizations/${organizationId}/members`;

  // Current organization ID signal for members
  private readonly currentOrganizationId = signal<string | null>(null);

  // Members resource using httpResource with computed URL
  private readonly membersResource = httpResource<OrganizationMemberList>(() => {
    const id = this.currentOrganizationId();
    return id ? this.membersApiUrl(id) : undefined;
  });

  // Public accessors
  readonly members = computed(() => {
    const value = this.membersResource.value();
    return value?.members || [];
  });
  readonly isLoading = computed(() => this.membersResource.isLoading());
  readonly error = computed(() => this.membersResource.error());
  readonly hasError = computed(() => this.membersResource.error() !== undefined);

  /**
   * Load members for an organization
   */
  loadMembers(organizationId: string): void {
    this.currentOrganizationId.set(organizationId);
    // Resource will reload automatically when ID changes
  }

  /**
   * Add a member to an organization
   */
  async addMember(organizationId: string, request: AddMemberRequest): Promise<OrganizationMember> {
    const response = await this.http
      .post<OrganizationMember>(this.membersApiUrl(organizationId), request)
      .toPromise();
    if (!response) {
      throw new Error('Failed to add member: No response from server');
    }

    // Reload members if this organization's members are currently loaded
    if (this.currentOrganizationId() === organizationId) {
      this.membersResource.reload();
    }

    return response;
  }

  /**
   * Update a member's role
   */
  async updateMemberRole(
    organizationId: string,
    userId: string,
    request: UpdateMemberRoleRequest,
  ): Promise<OrganizationMember> {
    const response = await this.http
      .put<OrganizationMember>(`${this.membersApiUrl(organizationId)}/${userId}`, request)
      .toPromise();
    if (!response) {
      throw new Error('Failed to update member role: No response from server');
    }

    // Reload members if this organization's members are currently loaded
    if (this.currentOrganizationId() === organizationId) {
      this.membersResource.reload();
    }

    return response;
  }

  /**
   * Remove a member from an organization
   */
  async removeMember(organizationId: string, userId: string): Promise<void> {
    await this.http.delete(`${this.membersApiUrl(organizationId)}/${userId}`).toPromise();

    // Reload members if this organization's members are currently loaded
    if (this.currentOrganizationId() === organizationId) {
      this.membersResource.reload();
    }
  }
}
