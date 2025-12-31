import { Injectable, signal, inject, computed, effect } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import { SpaceService } from './space.service';
import { ProjectService } from './project.service';
import { NavigationService } from './navigation.service';
import {
  WorkspaceNode,
  DTOItemFolder,
  DTOItemProject,
  DTOItemSpace,
  WorkspaceNodeWithChildren,
} from '../../presentation/layout/app-sidebar/workspace-tree-item';

// Backend API response types
export interface UnifiedListApiResponse {
  items: Array<DTOItemFolder | DTOItemProject | DTOItemSpace>;
  folders_count: number;
  nodes_count: number;
  total: number;
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

  // Workspace nodes signal (with children for tree structure)
  private readonly _workspaceNodes = signal<WorkspaceNodeWithChildren[]>([]);
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
   * Uses the unified API endpoint to get folders, projects, and spaces
   */
  async loadWorkspaces(organizationId: string): Promise<void> {
    this.isLoading.set(true);
    this.error.set(null);

    try {
      // Use unified API endpoint to get folders and nodes
      const url = `${environment.apiUrl}/organizations/${organizationId}/items`;
      const response = await firstValueFrom(this.http.get<UnifiedListApiResponse>(url));

      // Convert API response to workspace nodes with tree structure
      const workspaceNodes = this.buildWorkspaceTree(response.items, organizationId);

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
   * Build workspace tree structure from flat list of items
   * Groups items by folders and builds hierarchy
   */
  private buildWorkspaceTree(
    items: Array<DTOItemFolder | DTOItemProject | DTOItemSpace>,
    organizationId: string,
  ): WorkspaceNodeWithChildren[] {
    // Separate items by type
    const folders = items.filter((item): item is DTOItemFolder => item.type === 'folder');
    const projects = items.filter((item): item is DTOItemProject => item.type === 'project');
    const spaces = items.filter((item): item is DTOItemSpace => item.type === 'space');

    // Build folder tree with hierarchy
    const folderTree = this.buildFolderTree(folders);

    // Add projects and spaces to their respective folders or root
    const result: WorkspaceNodeWithChildren[] = [];

    // Process root folders (no parent_id)
    const rootFolders = folderTree.filter((f) => !f.parent_id);
    for (const folder of rootFolders) {
      const folderWithChildren: WorkspaceNodeWithChildren = {
        ...folder,
        children: [
          ...this.getFolderChildren(folder.id, folderTree),
          ...this.getItemsInFolder(folder.id, projects, spaces),
        ],
      };
      result.push(folderWithChildren);
    }

    // Add root-level projects and spaces (not in any folder)
    const rootProjects = projects.filter((p) => !p.details.folder_id);
    const rootSpaces = spaces.filter((s) => !s.details.folder_id);

    result.push(...rootProjects.map((p) => ({ ...p, children: undefined })));
    result.push(...rootSpaces.map((s) => ({ ...s, children: undefined })));

    // Sort by position for folders, then by name
    return result.sort((a, b) => {
      if (a.type === 'folder' && b.type === 'folder') {
        return a.position - b.position;
      }
      if (a.type === 'folder') return -1;
      if (b.type === 'folder') return 1;
      return a.details.name.localeCompare(b.details.name);
    });
  }

  /**
   * Build folder tree structure (handles folder hierarchy)
   */
  private buildFolderTree(folders: DTOItemFolder[]): DTOItemFolder[] {
    // Folders are returned as-is from API, with parent_id already set
    return folders;
  }

  /**
   * Get child folders of a parent folder
   */
  private getFolderChildren(
    parentFolderId: string,
    folders: DTOItemFolder[],
  ): WorkspaceNodeWithChildren[] {
    return folders
      .filter((f) => f.parent_id === parentFolderId)
      .map((f) => {
        // Recursively build children for nested folders
        const children: WorkspaceNodeWithChildren[] = [...this.getFolderChildren(f.id, folders)];
        return {
          ...f,
          children: children.length > 0 ? children : undefined,
        } as WorkspaceNodeWithChildren;
      });
  }

  /**
   * Get projects and spaces assigned to a folder
   */
  private getItemsInFolder(
    folderId: string,
    projects: DTOItemProject[],
    spaces: DTOItemSpace[],
  ): WorkspaceNodeWithChildren[] {
    const folderProjects = projects
      .filter((p) => p.details.folder_id === folderId)
      .map((p) => ({ ...p, children: undefined }));
    const folderSpaces = spaces
      .filter((s) => s.details.folder_id === folderId)
      .map((s) => ({ ...s, children: undefined }));
    return [...folderProjects, ...folderSpaces];
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
  }): Promise<{ id: string; name: string }> {
    const url = `${environment.apiUrl}/organizations/${request.organizationId}/folders`;
    const response = await firstValueFrom(
      this.http.post<{
        id: string;
        organization_id: string;
        name: string;
        parent_id: string | null;
        position: number;
        created_at: string;
        updated_at: string;
      }>(url, {
        organization_id: request.organizationId,
        name: request.title, // Backend expects "name" not "title"
        parent_id: request.parentId || null,
        position: 0,
      }),
    );

    // Reload workspaces after creating folder
    this.reload();

    return { id: response.id, name: response.name };
  }
}
