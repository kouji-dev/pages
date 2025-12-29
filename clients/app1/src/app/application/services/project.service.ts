import { Injectable, signal, inject, computed, effect } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import { NavigationService } from './navigation.service';
import { IssueUser } from './issue.service';

export interface Project {
  id: string;
  name: string;
  key: string;
  description?: string;
  organizationId: string;
  memberCount?: number;
  createdAt?: string;
  updatedAt?: string;
  // Design alignment fields (TODO: Add to backend)
  color?: string; // Project color for icon background
  taskCount?: number; // Total tasks
  completedTasks?: number; // Completed tasks
  status?: 'active' | 'completed' | 'on-hold'; // Project status
  members?: IssueUser[]; // Project members
  lastUpdated?: string; // Formatted "X ago" timestamp
}

export interface CreateProjectRequest {
  name: string;
  key?: string;
  description?: string;
  organization_id: string;
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
}

export interface ProjectListItemResponse {
  id: string;
  organization_id: string;
  name: string;
  key: string;
  description?: string;
  member_count: number;
  issue_count: number;
  created_at: string;
  updated_at?: string;
}

export interface ProjectResponse {
  id: string;
  organization_id: string;
  name: string;
  key: string;
  description?: string;
  member_count: number;
  issue_count: number;
  created_at: string;
  updated_at?: string;
}

export interface ProjectListResponse {
  projects: ProjectListItemResponse[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

@Injectable({
  providedIn: 'root',
})
export class ProjectService {
  private readonly http = inject(HttpClient);
  private readonly navigationService = inject(NavigationService);
  private readonly apiUrl = `${environment.apiUrl}/projects`;

  // Projects list resource using httpResource - driven by URL organizationId
  readonly projects = httpResource<ProjectListResponse>(() => {
    const orgId = this.navigationService.currentOrganizationId();
    if (!orgId) return undefined; // Don't load if no organization

    const params = new HttpParams().set('organization_id', orgId);
    return `${this.apiUrl}?${params.toString()}`;
  });

  // Public accessors for projects list
  readonly projectsList = computed(() => {
    const value = this.projects.value();
    if (!value) return [];
    // Handle both array response (legacy) and ProjectListResponse
    if (Array.isArray(value)) {
      return value;
    }
    // Map ProjectListItemResponse to Project (snake_case to camelCase)
    return (value.projects || []).map((p) => this.mapToProject(p));
  });

  /**
   * Map backend response (snake_case) to frontend model (camelCase)
   */
  private mapToProject(response: ProjectListItemResponse): Project {
    return {
      id: response.id,
      name: response.name,
      key: response.key,
      description: response.description,
      organizationId: response.organization_id,
      memberCount: response.member_count,
      createdAt: response.created_at,
      updatedAt: response.updated_at,
    };
  }
  readonly isLoading = computed(() => this.projects.isLoading());
  readonly error = computed(() => this.projects.error());
  readonly hasError = computed(() => this.projects.error() !== undefined);

  // Single project resource using httpResource - driven by URL projectId
  private readonly projectResource = httpResource<ProjectResponse>(() => {
    const id = this.navigationService.currentProjectId();
    return id ? `${this.apiUrl}/${id}` : undefined;
  });

  // Current project computed from resource (mapped to camelCase)
  readonly currentProject = computed(() => {
    const response = this.projectResource.value();
    if (!response) return undefined;
    // Map ProjectResponse to Project (snake_case to camelCase)
    return this.mapProjectResponseToProject(response);
  });

  /**
   * Map ProjectResponse (snake_case) to Project (camelCase)
   */
  private mapProjectResponseToProject(response: ProjectResponse): Project {
    return {
      id: response.id,
      name: response.name,
      key: response.key,
      description: response.description,
      organizationId: response.organization_id,
      memberCount: response.member_count,
      createdAt: response.created_at,
      updatedAt: response.updated_at,
    };
  }

  // Public accessors for current project
  readonly isFetchingProject = computed(() => this.projectResource.isLoading());
  readonly projectError = computed(() => this.projectResource.error());
  readonly hasProjectError = computed(() => this.projectResource.error() !== undefined);

  /**
   * Reload projects from API
   */
  loadProjects(): void {
    this.projects.reload();
  }

  /**
   * Fetch a single project by ID using httpResource
   * @deprecated Project fetching is now URL-driven via navigationService.currentProjectId()
   * The project will be automatically fetched when URL projectId changes
   */
  fetchProject(id: string): void {
    // Project fetching is now URL-driven
    // This method is kept for backward compatibility
  }

  /**
   * Switch to a different project (from list)
   * @deprecated Project switching is now URL-driven - navigate to the project URL instead
   */
  switchProject(projectId: string): void {
    // Project switching is now URL-driven
    // This method is kept for backward compatibility
  }

  /**
   * Get current project signal
   * Returns readonly signal - consumers can convert to Observable using toObservable() if needed
   */
  getCurrentProject(): typeof this.currentProject {
    return this.currentProject;
  }

  /**
   * Get all projects signal
   * Returns readonly signal - consumers can convert to Observable using toObservable() if needed
   */
  getProjects(): typeof this.projectsList {
    return this.projectsList;
  }

  /**
   * Get projects filtered by organization
   */
  getProjectsByOrganization(organizationId: string): Project[] {
    return this.projectsList().filter((p) => p.organizationId === organizationId);
  }

  /**
   * Persist current project to localStorage
   */
  private persistCurrentProjectToStorage(project: Project): void {
    try {
      localStorage.setItem('current_project_id', project.id);
    } catch (error) {
      console.error('Failed to persist project to localStorage:', error);
    }
  }

  /**
   * Get stored current project ID from localStorage
   */
  private getStoredCurrentProjectId(): string | null {
    try {
      return localStorage.getItem('current_project_id');
    } catch (error) {
      console.error('Failed to load project ID from localStorage:', error);
      return null;
    }
  }

  /**
   * Create a new project
   */
  async createProject(request: CreateProjectRequest): Promise<Project> {
    const response = await firstValueFrom(this.http.post<ProjectResponse>(this.apiUrl, request));
    if (!response) {
      throw new Error('Failed to create project: No response from server');
    }

    // Reload projects to get updated list
    this.loadProjects();

    // Map response to Project (snake_case to camelCase)
    return this.mapProjectResponseToProject(response);
  }

  /**
   * Update a project
   */
  async updateProject(id: string, updates: UpdateProjectRequest): Promise<Project> {
    const response = await firstValueFrom(
      this.http.put<ProjectResponse>(`${this.apiUrl}/${id}`, updates),
    );
    if (!response) {
      throw new Error('Failed to update project: No response from server');
    }

    // Reload projects list and current project to get updated data
    this.loadProjects();
    const currentProjectId = this.navigationService.currentProjectId();
    if (currentProjectId === id) {
      this.projectResource.reload();
    }

    // Map response to Project (snake_case to camelCase)
    return this.mapProjectResponseToProject(response);
  }

  /**
   * Delete a project
   */
  async deleteProject(id: string): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.apiUrl}/${id}`));

    // Reload projects to get updated list
    this.loadProjects();

    // If deleted project was current, navigation will handle clearing it
    // (user will be redirected or URL will change)
  }
}
