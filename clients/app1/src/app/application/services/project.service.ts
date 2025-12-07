import { Injectable, signal, inject, computed, effect } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Project {
  id: string;
  name: string;
  key: string;
  description?: string;
  organizationId: string;
  memberCount?: number;
  createdAt?: string;
  updatedAt?: string;
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

@Injectable({
  providedIn: 'root',
})
export class ProjectService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/projects`;

  // Projects list resource using httpResource
  readonly projects = httpResource(() => this.apiUrl);

  // Public accessors for projects list
  readonly projectsList = computed(() => {
    const value = this.projects.value();
    return Array.isArray(value) ? value : [];
  });
  readonly isLoading = computed(() => this.projects.isLoading());
  readonly error = computed(() => this.projects.error());
  readonly hasError = computed(() => this.projects.error() !== undefined);

  // Current project ID signal
  private readonly currentProjectId = signal<string | null>(null);

  // Single project resource using httpResource with computed URL
  private readonly projectResource = httpResource<Project>(() => {
    const id = this.currentProjectId();
    return id ? `${this.apiUrl}/${id}` : undefined;
  });

  // Current project computed from resource
  readonly currentProject = computed(() => {
    return this.projectResource.value() as Project | undefined;
  });

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
   */
  fetchProject(id: string): void {
    this.currentProjectId.set(id);
    // Resource will reload automatically when ID changes
  }

  /**
   * Switch to a different project (from list)
   * Sets the project ID, which triggers the resource to reload automatically
   */
  switchProject(projectId: string): void {
    const project = this.projectsList().find((p) => p.id === projectId);
    if (project) {
      this.currentProjectId.set(projectId);
      this.persistCurrentProjectToStorage(project);
    }
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
    const response = await firstValueFrom(this.http.post<Project>(this.apiUrl, request));
    if (!response) {
      throw new Error('Failed to create project: No response from server');
    }

    // Reload projects to get updated list
    this.loadProjects();

    return response;
  }

  /**
   * Update a project
   */
  async updateProject(id: string, updates: UpdateProjectRequest): Promise<Project> {
    const response = await firstValueFrom(this.http.put<Project>(`${this.apiUrl}/${id}`, updates));
    if (!response) {
      throw new Error('Failed to update project: No response from server');
    }

    // Reload projects list and current project to get updated data
    this.loadProjects();
    if (this.currentProjectId() === id) {
      this.projectResource.reload();
    }

    return response;
  }

  /**
   * Delete a project
   */
  async deleteProject(id: string): Promise<void> {
    await firstValueFrom(this.http.delete(`${this.apiUrl}/${id}`));

    // Reload projects to get updated list
    this.loadProjects();

    // If deleted project was current, clear it
    if (this.currentProjectId() === id) {
      this.currentProjectId.set(null);
      try {
        localStorage.removeItem('current_project_id');
      } catch (error) {
        console.error('Failed to remove project ID from localStorage:', error);
      }
    }
  }
}
