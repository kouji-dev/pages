import { Injectable, signal, inject, computed } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { environment } from '../../../environments/environment';

export interface OrganizationInvitation {
  id: string;
  organization_id: string;
  email: string;
  role: 'admin' | 'member' | 'viewer';
  invited_by: string;
  expires_at: string;
  accepted_at: string | null;
  created_at: string;
}

export interface OrganizationInvitationList {
  invitations: OrganizationInvitation[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface SendInvitationRequest {
  email: string;
  role: 'admin' | 'member' | 'viewer';
}

export interface AcceptInvitationResponse {
  organization_id: string;
  organization_name: string;
  organization_slug: string;
  role: string;
  message: string;
}

@Injectable({
  providedIn: 'root',
})
export class OrganizationInvitationsService {
  private readonly http = inject(HttpClient);

  // Base URL pattern for organization invitations
  private readonly invitationsApiUrl = (organizationId: string): string =>
    `${environment.apiUrl}/organizations/${organizationId}/invitations`;

  // Current organization ID signal for invitations
  private readonly currentOrganizationId = signal<string | null>(null);

  // Invitations resource using httpResource with computed URL
  private readonly invitationsResource = httpResource<OrganizationInvitationList>(() => {
    const id = this.currentOrganizationId();
    if (!id) {
      return undefined;
    }

    // Always fetch pending_only=true for the list
    const params = new HttpParams()
      .set('page', '1')
      .set('limit', '100')
      .set('pending_only', 'true');
    return `${this.invitationsApiUrl(id)}?${params.toString()}`;
  });

  // Public accessors
  readonly invitations = computed(() => {
    const value = this.invitationsResource.value();
    return value?.invitations || [];
  });
  readonly isLoading = computed(() => this.invitationsResource.isLoading());
  readonly error = computed(() => this.invitationsResource.error());
  readonly hasError = computed(() => this.invitationsResource.error() !== undefined);

  /**
   * Load invitations for an organization
   */
  loadInvitations(organizationId: string): void {
    this.currentOrganizationId.set(organizationId);
    // Resource will reload automatically when ID changes
  }

  /**
   * Send an invitation to join an organization
   */
  async sendInvitation(
    organizationId: string,
    request: SendInvitationRequest,
  ): Promise<OrganizationInvitation> {
    const response = await this.http
      .post<OrganizationInvitation>(
        `${environment.apiUrl}/organizations/${organizationId}/members/invite`,
        request,
      )
      .toPromise();
    if (!response) {
      throw new Error('Failed to send invitation: No response from server');
    }

    // Reload invitations if this organization's invitations are currently loaded
    if (this.currentOrganizationId() === organizationId) {
      this.invitationsResource.reload();
    }

    return response;
  }

  /**
   * Cancel an invitation
   */
  async cancelInvitation(invitationId: string): Promise<void> {
    await this.http
      .delete(`${environment.apiUrl}/organizations/invitations/${invitationId}`)
      .toPromise();

    // Reload invitations if currently loaded
    if (this.currentOrganizationId()) {
      this.invitationsResource.reload();
    }
  }

  /**
   * Accept an invitation by token
   */
  async acceptInvitation(token: string): Promise<AcceptInvitationResponse> {
    const response = await this.http
      .post<AcceptInvitationResponse>(
        `${environment.apiUrl}/organizations/invitations/${token}/accept`,
        {},
      )
      .toPromise();
    if (!response) {
      throw new Error('Failed to accept invitation: No response from server');
    }
    return response;
  }
}
