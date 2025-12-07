import { Injectable, signal, inject, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';

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

  // Base URL pattern for project members (includes /members)
  private readonly membersApiUrl = (projectId: string): string =>
    `${environment.apiUrl}/projects/${projectId}/members`;

  // Current project ID signal for members
  private readonly currentProjectId = signal<string | null>(null);

  // Members resource using httpResource with computed URL
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
   * Load members for a project
   */
  loadMembers(projectId: string): void {
    this.currentProjectId.set(projectId);
    // Resource will reload automatically when ID changes
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
