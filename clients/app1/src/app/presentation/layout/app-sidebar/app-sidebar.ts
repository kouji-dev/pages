import { Component, ChangeDetectionStrategy, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateService } from '@ngx-translate/core';
import { List, ListItemData, ListHeader, ListHeaderAction } from 'shared-ui';
import { UserMenu } from '../../../shared/components/user-menu/user-menu';
import { WorkspaceTreeItem, WorkspaceNode } from './workspace-tree-item';
import { SidebarOrgSelector } from './components/sidebar-org-selector/sidebar-org-selector';
import { OrganizationService } from '../../../application/services/organization.service';
import { LanguageService } from '../../../core/i18n/language.service';

const favorites: ListItemData[] = [
  {
    id: '1',
    label: 'Marketing Website',
    icon: 'star',
    iconColor: '#fbbf24',
    rightIcon: 'kanban',
  },
  {
    id: '2',
    label: 'API Documentation',
    icon: 'star',
    iconColor: '#fbbf24',
    rightIcon: 'file-text',
  },
  {
    id: '3',
    label: 'Design System',
    icon: 'star',
    iconColor: '#fbbf24',
    rightIcon: 'kanban',
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
  imports: [CommonModule, List, ListHeader, UserMenu, WorkspaceTreeItem, SidebarOrgSelector],
  template: `
    <aside class="app-sidebar">
      <header class="app-sidebar_header">
        <div class="app-sidebar_header-content">
          <app-sidebar-org-selector />
        </div>
      </header>

      <nav class="app-sidebar_content pages-scrollbar">
        <div class="app-sidebar_section">
          <lib-list [items]="mainNavItems()">
            <lib-list-header title="Main" />
          </lib-list>
        </div>

        <div class="app-sidebar_section">
          <lib-list [items]="favoritesItems()">
            <lib-list-header title="Favorites" />
          </lib-list>
        </div>

        <div class="app-sidebar_section">
          <lib-list>
            <lib-list-header title="Workspaces" [actions]="workspacesActions()" />
            @for (node of workspaces; track node.id) {
              <app-workspace-tree-item [node]="node" />
            }
          </lib-list>
        </div>
      </nav>

      <footer class="app-sidebar_footer">
        <div class="app-sidebar_footer-content">
          <app-user-menu />
        </div>
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
        width: 100%; /* Full width of parent container */
        min-height: 0; /* Important for flexbox scrolling */
      }

      .app-sidebar_header {
        height: 4rem; /* 64px - matches main header height */
        @apply border-b border-navigation-border;
        @apply flex-shrink-0;
        @apply px-4;
        @apply py-0;
        @apply flex items-center;
      }

      /* Compact mode adjustments */
      :host-context([data-density='compact']) .app-sidebar_header {
        height: 3rem; /* 48px - compact header height */
        @apply px-3;
      }

      .app-sidebar_header-content {
        display: flex;
        @apply items-center;
        width: 100%;
        min-width: 0;
        height: 100%;
      }

      .app-sidebar_content {
        @apply flex-1 overflow-y-auto px-2 py-4;
        min-height: 0; /* Important for flexbox scrolling */
      }

      .app-sidebar_section {
        @apply mb-6;
        @apply px-2;
      }

      .app-sidebar_section:last-child {
        @apply mb-0;
      }

      .app-sidebar_section ::ng-deep .list-header_title {
        @apply px-2 mb-1;
      }

      .app-sidebar_footer {
        @apply p-3 border-t border-navigation-border;
        @apply flex-shrink-0;
        margin-top: auto;
        @apply bg-navigation;
      }

      .app-sidebar_footer-content {
        @apply w-full;
      }

      .app-sidebar_footer-content .user-menu {
        @apply w-full;
      }

      .app-sidebar_footer-content .user-menu_trigger {
        @apply w-full;
        @apply justify-start;
        @apply px-2.5 py-2;
        @apply rounded-md;
        @apply hover:bg-muted/50;
      }

      .app-sidebar_footer-content .user-menu_info {
        @apply flex;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
})
export class AppSidebar {
  private readonly organizationService = inject(OrganizationService);
  private readonly translateService = inject(TranslateService);
  private readonly languageService = inject(LanguageService);

  readonly mainNavItems = computed<ListItemData[]>(() => {
    // Depend on currentLang to trigger recomputation when language changes
    this.languageService.currentLanguage();

    const currentOrg = this.organizationService.currentOrganization();
    if (!currentOrg) {
      return [];
    }

    // Show Dashboard, Projects, and Docs (Spaces) when in organization context
    return [
      {
        id: 'dashboard',
        label: this.translateService.instant('navigation.dashboard'),
        routerLink: ['/app/organizations', currentOrg.id, 'dashboard'],
        icon: 'layout-dashboard',
      },
      {
        id: 'projects',
        label: this.translateService.instant('navigation.projects'),
        routerLink: ['/app/organizations', currentOrg.id, 'projects'],
        icon: 'folder',
      },
      {
        id: 'docs',
        label: this.translateService.instant('navigation.spaces'),
        routerLink: ['/app/organizations', currentOrg.id, 'spaces'],
        icon: 'file-text',
      },
    ];
  });
  readonly favoritesItems = computed<ListItemData[]>(() => favorites);
  readonly workspaces = workspaces;

  readonly workspacesActions = computed<ListHeaderAction[]>(() => [
    { icon: 'ellipsis', onClick: () => {} },
    { icon: 'plus', onClick: () => {} },
  ]);
}
