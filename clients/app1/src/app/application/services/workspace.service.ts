import { Injectable, signal, inject, computed, effect } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import { SpaceService } from './space.service';
import { ProjectService } from './project.service';
import { NavigationService } from './navigation.service';
import { WorkspaceNode } from '../../presentation/layout/app-sidebar/workspace-tree-item';

export interface PageTreeItem {
  id: string;
  space_id: string;
  title: string;
  slug: string;
  content?: string | null;
  parent_id?: string | null;
  created_by?: string | null;
  updated_by?: string | null;
  position: number;
  children: PageTreeItem[];
  created_at: string;
  updated_at: string;
}

export interface PageTreeResponse {
  pages: PageTreeItem[];
}

@Injectable({
  providedIn: 'root',
})
export class WorkspaceService {
  private readonly http = inject(HttpClient);
  private readonly spaceService = inject(SpaceService);
  private readonly projectService = inject(ProjectService);
  private readonly navigationService = inject(NavigationService);
  private readonly apiUrl = `${environment.apiUrl}/pages`;

  // Workspace nodes signal
  private readonly _workspaceNodes = signal<WorkspaceNode[]>([]);
  readonly workspaceNodes = this._workspaceNodes.asReadonly();

  readonly isLoading = signal(false);
  readonly error = signal<Error | null>(null);

  constructor() {
    // Load workspaces when organization changes
    effect(() => {
      const orgId = this.navigationService.currentOrganizationId();
      if (orgId) {
        // Also depend on spaces and projects to reload when they change
        this.spaceService.spacesList();
        this.projectService.projectsList();
        this.loadWorkspaces(orgId);
      } else {
        this._workspaceNodes.set([]);
      }
    });
  }

  /**
   * Load workspace tree for current organization
   */
  async loadWorkspaces(organizationId: string): Promise<void> {
    this.isLoading.set(true);
    this.error.set(null);

    try {
      // Get spaces and projects for the organization
      const spaces = this.spaceService.getSpacesByOrganization(organizationId);
      const projects = this.projectService.getProjectsByOrganization(organizationId);

      const workspaceNodes: WorkspaceNode[] = [];

      // Add spaces with their page trees
      for (const space of spaces) {
        try {
          const pageTree = await this.getPageTree(space.id);
          const spaceNode: WorkspaceNode = {
            id: space.id,
            title: space.name,
            type: 'space',
            children: this.convertPageTreeToNodes(pageTree.pages, space.id),
          };
          workspaceNodes.push(spaceNode);
        } catch (error) {
          // If page tree fails, still add the space without pages
          console.warn(`Failed to load page tree for space ${space.id}:`, error);
          const spaceNode: WorkspaceNode = {
            id: space.id,
            title: space.name,
            type: 'space',
            children: [],
          };
          workspaceNodes.push(spaceNode);
        }
      }

      // Add projects as separate items
      for (const project of projects) {
        workspaceNodes.push({
          id: project.id,
          title: project.name,
          type: 'project',
        });
      }

      this._workspaceNodes.set(workspaceNodes);
    } catch (error) {
      console.error('Error loading workspace tree:', error);
      this.error.set(error instanceof Error ? error : new Error('Failed to load workspaces'));
      this._workspaceNodes.set([]);
    } finally {
      this.isLoading.set(false);
    }
  }

  /**
   * Get page tree for a space
   */
  async getPageTree(spaceId: string): Promise<PageTreeResponse> {
    const url = `${this.apiUrl}/spaces/${spaceId}/tree`;
    return firstValueFrom(this.http.get<PageTreeResponse>(url));
  }

  /**
   * Convert page tree items to workspace nodes
   */
  private convertPageTreeToNodes(pages: PageTreeItem[], spaceId: string): WorkspaceNode[] {
    return pages.map((page) => {
      const node: WorkspaceNode = {
        id: page.id,
        title: page.title,
        type: 'page',
        spaceId: spaceId, // Store space_id for navigation
        children:
          page.children.length > 0
            ? this.convertPageTreeToNodes(page.children, spaceId)
            : undefined,
      };
      return node;
    });
  }

  /**
   * Reload workspaces
   */
  reload(): void {
    const orgId = this.navigationService.currentOrganizationId();
    if (orgId) {
      this.loadWorkspaces(orgId);
    }
  }

  /**
   * Create a folder (workspace node)
   */
  async createFolder(request: {
    organizationId: string;
    title: string;
    parentId?: string;
  }): Promise<{ id: string; title: string }> {
    const url = `${environment.apiUrl}/workspaces/folders`;
    const response = await firstValueFrom(
      this.http.post<{ id: string; title: string }>(url, {
        organization_id: request.organizationId,
        title: request.title,
        parent_id: request.parentId || null,
      }),
    );

    // Reload workspaces after creating folder
    this.reload();

    return response;
  }
}
