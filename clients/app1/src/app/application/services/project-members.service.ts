import { Injectable, signal, inject, computed } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import { NavigationService } from './navigation.service';

export interface ProjectMember {
  user_id: string;
  project_id: string;
  role: 'admin' | 'member' | 'viewer';
  user_name: string;
  user_email: string;
  avatar_url?: string;
  joined_at: string;
}

export interface ProjectMemberList {
  members: ProjectMember[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface AddProjectMemberRequest {
  user_id: string;
  role: 'admin' | 'member' | 'viewer';
}

export interface UpdateProjectMemberRoleRequest {
  role: 'admin' | 'member' | 'viewer';
}

@Injectable({
  providedIn: 'root',
})
export class ProjectMembersService {
  private readonly http = inject(HttpClient);
  private readonly navigationService = inject(NavigationService);

  // Base URL pattern for project members (includes /members)
  private readonly membersApiUrl = (projectId: string): string =>
    `${environment.apiUrl}/projects/${projectId}/members`;

  // Current project ID from navigation service
  private readonly currentProjectId = computed(() => {
    return this.navigationService.currentProjectId();
  });

  // Members resource using httpResource with computed URL
  // Automatically updates when currentProjectId changes
  private readonly membersResource = httpResource<ProjectMemberList>(() => {
    const id = this.currentProjectId();
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
   * Reload members for the current project
   */
  reloadMembers(): void {
    this.membersResource.reload();
  }

  /**
   * Search project members by query
   * @param projectId Project ID (optional, uses current project from navigation if not provided)
   * @param query Search query (name or email). If empty, returns all members.
   * @param limit Maximum number of results (default: 20)
   */
  async searchProjectMembers(
    projectId?: string,
    query: string = '',
    limit: number = 20,
  ): Promise<ProjectMember[]> {
    const targetProjectId = projectId || this.currentProjectId();
    if (!targetProjectId) {
      throw new Error('No project ID available for searching members');
    }

    let params = new HttpParams().set('page', '1').set('limit', limit.toString());

    // Only add search parameter if query is not empty
    if (query.trim()) {
      params = params.set('search', query.trim());
    }

    const response = await firstValueFrom(
      this.http.get<ProjectMemberList>(this.membersApiUrl(targetProjectId), {
        params,
      }),
    );

    return response?.members || [];
  }

  /**
   * Add a member to a project
   */
  async addMember(projectId: string, request: AddProjectMemberRequest): Promise<ProjectMember> {
    const response = await firstValueFrom(
      this.http.post<ProjectMember>(this.membersApiUrl(projectId), request),
    );
    if (!response) {
      throw new Error('Failed to add member: No response from server');
    }

    // Reload members if this project's members are currently loaded
    if (this.currentProjectId() === projectId) {
      this.membersResource.reload();
    }

    return response;
  }

  /**
   * Update a member's role
   */
  async updateMemberRole(
    projectId: string,
    userId: string,
    request: UpdateProjectMemberRoleRequest,
  ): Promise<ProjectMember> {
    const response = await firstValueFrom(
      this.http.put<ProjectMember>(`${this.membersApiUrl(projectId)}/${userId}`, request),
    );
    if (!response) {
      throw new Error('Failed to update member role: No response from server');
    }

    // Reload members if this project's members are currently loaded
    if (this.currentProjectId() === projectId) {
      this.membersResource.reload();
    }

    return response;
  }

  /**
   * Remove a member from a project
   */
  async removeMember(projectId: string, userId: string): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.membersApiUrl(projectId)}/${userId}`));

    // Reload members if this project's members are currently loaded
    if (this.currentProjectId() === projectId) {
      this.membersResource.reload();
    }
  }
}
