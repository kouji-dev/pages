import { Component, ChangeDetectionStrategy, input, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Icon, IconName } from 'shared-ui';

export interface WorkspaceNode {
  id: string;
  title: string;
  type: 'folder' | 'project' | 'page';
  children?: WorkspaceNode[];
}

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
          <span class="workspace-tree-item_title">{{ node().title }}</span>
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
        <span class="workspace-tree-item_title">{{ node().title }}</span>
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
  node = input.required<WorkspaceNode>();
  level = input(0);

  readonly isOpen = signal(false);

  readonly hasChildren = computed(() => {
    return !!(this.node().children && this.node().children!.length > 0);
  });

  readonly iconName = computed<IconName>(() => {
    switch (this.node().type) {
      case 'folder':
        return 'folder';
      case 'project':
        return 'kanban';
      case 'page':
        return 'file-text';
    }
  });

  toggle(): void {
    this.isOpen.update((current) => !current);
  }

  setIsOpen(open: boolean): void {
    this.isOpen.set(open);
  }

  handleClick(): void {
    // Handle navigation to workspace item
    // TODO: Implement navigation
  }
}

