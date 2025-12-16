import { Component, ChangeDetectionStrategy, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Button, Icon, Avatar, List, ListItemData } from 'shared-ui';
import { ThemeToggle } from '../../../shared/components/theme-toggle/theme-toggle';
import { DensityToggle } from '../../../shared/components/density-toggle/density-toggle';
import { WorkspaceTreeItem, WorkspaceNode } from './workspace-tree-item';
import { UserStore } from '../../../core/user/user.store';

const mainNav: ListItemData[] = [
  { id: 'dashboard', label: 'Dashboard', routerLink: '/app', icon: 'layout-dashboard' },
  { id: 'projects', label: 'Projects', routerLink: '/app/projects', icon: 'kanban' },
  { id: 'docs', label: 'Docs', routerLink: '/app/docs', icon: 'file-text' },
];

const favorites: ListItemData[] = [
  {
    id: '1',
    label: 'Marketing Website',
    icon: 'star',
    iconColor: 'warning',
    rightIcon: 'kanban',
    rightIconColor: 'muted-foreground',
  },
  {
    id: '2',
    label: 'API Documentation',
    icon: 'star',
    iconColor: 'warning',
    rightIcon: 'file-text',
    rightIconColor: 'muted-foreground',
  },
  {
    id: '3',
    label: 'Design System',
    icon: 'star',
    iconColor: 'warning',
    rightIcon: 'kanban',
    rightIconColor: 'muted-foreground',
  },
];

const workspaces: WorkspaceNode[] = [
  {
    id: 'w1',
    title: 'Engineering',
    type: 'folder',
    children: [
      { id: 'w1-1', title: 'Backend API', type: 'project' },
      { id: 'w1-2', title: 'Frontend App', type: 'project' },
      {
        id: 'w1-3',
        title: 'Documentation',
        type: 'folder',
        children: [
          { id: 'w1-3-1', title: 'Getting Started', type: 'page' },
          { id: 'w1-3-2', title: 'API Reference', type: 'page' },
        ],
      },
    ],
  },
  {
    id: 'w2',
    title: 'Product',
    type: 'folder',
    children: [
      { id: 'w2-1', title: 'Roadmap', type: 'page' },
      { id: 'w2-2', title: 'User Research', type: 'project' },
    ],
  },
  { id: 'w3', title: 'Quick Notes', type: 'page' },
];

@Component({
  selector: 'app-app-sidebar',
  imports: [
    CommonModule,
    Button,
    Icon,
    Avatar,
    List,
    ThemeToggle,
    DensityToggle,
    WorkspaceTreeItem,
  ],
  template: `
    <aside class="app-sidebar">
      <header class="app-sidebar_header">
        <div class="app-sidebar_header-content">
          <div class="app-sidebar_logo">
            <lib-icon name="file-text" size="md" color="primary-foreground" />
          </div>
          <span class="app-sidebar_brand">Pages</span>
        </div>
      </header>

      <nav class="app-sidebar_content pages-scrollbar">
        <div class="app-sidebar_section">
          <div class="app-sidebar_section-label">Main</div>
          <div class="app-sidebar_section-content">
            <lib-list [items]="mainNavItems()" />
          </div>
        </div>

        <div class="app-sidebar_section">
          <div class="app-sidebar_section-label">Favorites</div>
          <div class="app-sidebar_section-content">
            <lib-list [items]="favoritesItems()" />
          </div>
        </div>

        <div class="app-sidebar_section">
          <div class="app-sidebar_section-header">
            <div class="app-sidebar_section-label">Workspaces</div>
            <div class="app-sidebar_section-actions">
              <lib-button variant="ghost" size="sm" [iconOnly]="true" leftIcon="ellipsis" />
              <lib-button variant="ghost" size="sm" [iconOnly]="true" leftIcon="plus" />
            </div>
          </div>
          <div class="app-sidebar_section-content">
            @for (node of workspaces; track node.id) {
              <app-workspace-tree-item [node]="node" />
            }
          </div>
        </div>
      </nav>

      <footer class="app-sidebar_footer">
        @if (userProfile()) {
          <div class="app-sidebar_footer-content">
            <div class="app-sidebar_footer-user">
              <lib-avatar
                [name]="userProfile()!.name"
                [initials]="userInitials()"
                [avatarUrl]="userProfile()!.avatarUrl"
                size="sm"
              />
              <span class="app-sidebar_footer-user-name">{{ userProfile()!.name }}</span>
            </div>
            <div class="app-sidebar_footer-actions">
              <app-theme-toggle />
              <app-density-toggle />
              <lib-button
                variant="ghost"
                size="sm"
                [iconOnly]="true"
                leftIcon="settings"
                (clicked)="navigateToSettings()"
              />
            </div>
          </div>
        }
      </footer>
    </aside>
  `,
  styles: [
    `
      @reference "#mainstyles";

      :host {
        @apply flex flex-col h-full;
      }

      .app-sidebar {
        @apply flex flex-col;
        height: 100%;
        @apply bg-navigation;
        @apply border-r border-navigation-border;
        width: 17.5rem; /* 280px */
        min-height: 0; /* Important for flexbox scrolling */
      }

      .app-sidebar_header {
        @apply p-4 border-b border-navigation-border;
        @apply flex-shrink-0;
      }

      .app-sidebar_header-content {
        @apply flex items-center gap-2;
      }

      .app-sidebar_logo {
        @apply h-8 w-8 rounded-lg bg-primary flex items-center justify-center;
      }

      .app-sidebar_brand {
        @apply font-semibold text-lg text-navigation-accent-foreground;
      }

      .app-sidebar_content {
        @apply flex-1 overflow-y-auto px-2 py-4;
        min-height: 0; /* Important for flexbox scrolling */
      }

      .app-sidebar_section {
        @apply mb-6;
      }

      .app-sidebar_section:last-child {
        @apply mb-0;
      }

      .app-sidebar_section-header {
        @apply flex items-center justify-between px-2 mb-1;
      }

      .app-sidebar_section-label {
        @apply text-xs font-medium text-muted-foreground uppercase tracking-wider px-2;
      }

      .app-sidebar_section-actions {
        @apply flex items-center gap-1;
      }

      .app-sidebar_section-content {
        @apply space-y-0.5;
      }

      .app-sidebar_footer {
        @apply p-4 border-t border-navigation-border;
        @apply flex-shrink-0;
        margin-top: auto;
      }

      .app-sidebar_footer-content {
        @apply flex items-center justify-between;
      }

      .app-sidebar_footer-user {
        @apply flex items-center gap-3;
      }

      .app-sidebar_footer-user-name {
        @apply text-sm font-medium text-navigation-foreground truncate;
      }

      .app-sidebar_footer-actions {
        @apply flex items-center gap-1;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
})
export class AppSidebar {
  private readonly router = inject(Router);
  private readonly userStore = inject(UserStore);

  readonly mainNavItems = computed<ListItemData[]>(() => mainNav);
  readonly favoritesItems = computed<ListItemData[]>(() => favorites);
  readonly workspaces = workspaces;
  readonly userProfile = this.userStore.userProfile;

  readonly userInitials = computed<string>(() => {
    const profile = this.userProfile();
    if (!profile?.name) {
      return '';
    }
    const names = profile.name.trim().split(/\s+/);
    if (names.length >= 2) {
      return (names[0][0] + names[names.length - 1][0]).toUpperCase();
    }
    return profile.name.substring(0, 2).toUpperCase();
  });

  navigateToSettings(): void {
    this.router.navigate(['/app/profile']);
  }
}

