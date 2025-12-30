import { Component, ChangeDetectionStrategy, input, signal, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Icon, IconName } from 'shared-ui';
import { NavigationService } from '../../../application/services/navigation.service';

// DTOs matching backend structure
export interface DTOFolderDetails {
  name: string;
}

export interface DTOProjectDetails {
  name: string;
  key?: string | null;
  description?: string | null;
  folder_id?: string | null;
}

export interface DTOSpaceDetails {
  name: string;
  key?: string | null;
  description?: string | null;
  folder_id?: string | null;
}

export interface DTOItemFolder {
  type: 'folder';
  id: string;
  organization_id: string;
  position: number;
  details: DTOFolderDetails;
  parent_id?: string | null; // Added for folder hierarchy
}

export interface DTOItemProject {
  type: 'project';
  id: string;
  organization_id: string;
  details: DTOProjectDetails;
}

export interface DTOItemSpace {
  type: 'space';
  id: string;
  organization_id: string;
  details: DTOSpaceDetails;
}

// Workspace node is a union of the three types
export type WorkspaceNode = DTOItemFolder | DTOItemProject | DTOItemSpace;

// Helper type for workspace nodes with children (for tree structure)
export type WorkspaceNodeWithChildren =
  | (DTOItemFolder & { children?: WorkspaceNodeWithChildren[] })
  | (DTOItemProject & { children?: WorkspaceNodeWithChildren[] })
  | (DTOItemSpace & { children?: WorkspaceNodeWithChildren[] });

@Component({
  selector: 'app-workspace-tree-item',
  imports: [CommonModule, Icon],
  template: `
    @if (hasChildren()) {
      <div class="workspace-tree-item_container">
        <button
          class="workspace-tree-item"
          [class.workspace-tree-item--open]="isOpen()"
          [style.padding-left.px]="8 + level() * 12"
          (click)="toggle()"
        >
          <lib-icon
            name="chevron-right"
            size="xs"
            [class.workspace-tree-item_chevron--open]="isOpen()"
            class="workspace-tree-item_chevron"
          />
          <lib-icon [name]="iconName()" size="sm" />
          <span class="workspace-tree-item_title">{{ getNodeName() }}</span>
        </button>
        @if (isOpen()) {
          <div class="workspace-tree-item_children">
            @for (child of node().children; track child.id) {
              <app-workspace-tree-item [node]="child" [level]="level() + 1" />
            }
          </div>
        }
      </div>
    } @else {
      <button
        class="workspace-tree-item"
        [style.padding-left.px]="20 + level() * 12"
        (click)="handleClick()"
      >
        <lib-icon [name]="iconName()" size="sm" />
        <span class="workspace-tree-item_title">{{ getNodeName() }}</span>
      </button>
    }
  `,
  styles: [
    `
      @reference "#mainstyles";

      .workspace-tree-item {
        @apply flex items-center gap-2 w-full px-2 py-1.5 rounded-md text-sm;
        @apply text-navigation-foreground;
        @apply hover:bg-navigation-accent hover:text-navigation-accent-foreground;
        @apply transition-colors;
        @apply border-none bg-transparent cursor-pointer;
      }

      .workspace-tree-item_chevron {
        @apply transition-transform;
      }

      .workspace-tree-item_chevron--open {
        @apply rotate-90;
      }

      .workspace-tree-item_title {
        @apply truncate flex-1 text-left;
      }

      .workspace-tree-item_container {
        @apply w-full;
      }

      .workspace-tree-item_children {
        @apply w-full;
      }
    `,
  ],
  standalone: true,
})
export class WorkspaceTreeItem {
  private readonly router = inject(Router);
  private readonly navigationService = inject(NavigationService);

  node = input.required<WorkspaceNodeWithChildren>();
  level = input(0);

  readonly isOpen = signal(false);

  readonly hasChildren = computed(() => {
    return !!(this.node().children && this.node().children!.length > 0);
  });

  readonly iconName = computed<IconName>(() => {
    switch (this.node().type) {
      case 'folder':
        return 'folder';
      case 'space':
        return 'book';
      case 'project':
        return 'kanban';
      default:
        return 'folder';
    }
  });

  toggle(): void {
    this.isOpen.update((current) => !current);
  }

  setIsOpen(open: boolean): void {
    this.isOpen.set(open);
  }

  readonly getNodeName = computed(() => {
    const node = this.node();
    switch (node.type) {
      case 'folder':
        return node.details.name;
      case 'project':
        return node.details.name;
      case 'space':
        return node.details.name;
    }
  });

  handleClick(): void {
    const node = this.node();
    const orgId = this.navigationService.currentOrganizationId();

    if (!orgId) {
      return;
    }

    switch (node.type) {
      case 'folder':
        // Folders are workspace nodes - navigation TBD
        // For now, folders don't have a dedicated route
        break;
      case 'space':
        // Navigate to space
        this.router.navigate(this.navigationService.getSpaceRoute(orgId, node.id));
        break;
      case 'project':
        // Navigate to project
        this.router.navigate(this.navigationService.getProjectRoute(orgId, node.id));
        break;
    }
  }
}
