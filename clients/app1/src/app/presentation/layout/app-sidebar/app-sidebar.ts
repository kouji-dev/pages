import {
  Component,
  ChangeDetectionStrategy,
  inject,
  computed,
  viewChild,
  TemplateRef,
  ViewContainerRef,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateService } from '@ngx-translate/core';
import {
  List,
  ListItemData,
  ListHeader,
  ListHeaderAction,
  LoadingState,
  Icon,
  Modal,
  IconName,
} from 'shared-ui';
import { UserMenu } from '../../../shared/components/user-menu/user-menu';
import { WorkspaceTreeItem, WorkspaceNode } from './workspace-tree-item';
import { SidebarOrgSelector } from './components/sidebar-org-selector/sidebar-org-selector';
import { OrganizationService } from '../../../application/services/organization.service';
import { WorkspaceService } from '../../../application/services/workspace.service';
import { FavoriteService } from '../../../application/services/favorite.service';
import { LanguageService } from '../../../core/i18n/language.service';
import { CreateProjectModal } from '../../../features/projects/components/create-project-modal/create-project-modal';
import { CreateSpaceModal } from '../../../features/spaces/components/create-space-modal/create-space-modal';
import { CreateFolderModal } from '../../../features/spaces/components/create-folder-modal/create-folder-modal';
import { CreatePageModal } from '../../../features/pages/components/create-page-modal/create-page-modal';
import { firstValueFrom } from 'rxjs';

@Component({
  selector: 'app-app-sidebar',
  imports: [
    CommonModule,
    List,
    ListHeader,
    UserMenu,
    WorkspaceTreeItem,
    SidebarOrgSelector,
    LoadingState,
  ],
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
          <lib-list>
            <lib-list-header title="Favorites" />
            @if (favoriteService.isLoading()) {
              <lib-loading-state [message]="'Loading favorites...'" />
            } @else if (favoriteService.error()) {
              <div class="app-sidebar_error">
                {{ 'Failed to load favorites' }}
              </div>
            } @else {
              @if (favoriteService.favoritesItems().length > 0) {
                <lib-list [items]="favoriteService.favoritesItems()" />
              } @else {
                <div class="app-sidebar_empty">
                  {{ 'No favorites yet' }}
                </div>
              }
            }
          </lib-list>
        </div>

        <div class="app-sidebar_section">
          <lib-list>
            <ng-template #workspaceAddDropdown>
              <lib-list [items]="workspaceAddOptions()" />
            </ng-template>
            <lib-list-header title="Workspaces" [actions]="workspacesActions()" />
            @if (workspaceService.isLoading()) {
              <lib-loading-state [message]="'Loading workspaces...'" />
            } @else if (workspaceService.error()) {
              <div class="app-sidebar_error">
                {{ 'Failed to load workspaces' }}
              </div>
            } @else {
              @for (node of workspaceService.workspaceNodes(); track node.id) {
                <app-workspace-tree-item [node]="node" />
              }
              @if (workspaceService.workspaceNodes().length === 0) {
                <div class="app-sidebar_empty">
                  {{ 'No workspaces found' }}
                </div>
              }
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
        @apply text-xs font-medium text-muted-foreground uppercase tracking-wider px-2 mb-1;
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

      .app-sidebar_error {
        @apply text-sm text-destructive px-2 py-2;
      }

      .app-sidebar_empty {
        @apply text-sm text-muted-foreground px-2 py-2;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
})
export class AppSidebar {
  readonly workspaceAddDropdownTemplate = viewChild<TemplateRef<any>>('workspaceAddDropdown');

  private readonly organizationService = inject(OrganizationService);
  private readonly translateService = inject(TranslateService);
  private readonly languageService = inject(LanguageService);
  private readonly modal = inject(Modal);
  private readonly viewContainerRef = inject(ViewContainerRef);
  readonly workspaceService = inject(WorkspaceService);
  readonly favoriteService = inject(FavoriteService);

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

  readonly workspaceAddOptions = computed<ListItemData[]>(() => {
    return [
      {
        id: 'space',
        label: 'Folder (Space)',
        icon: 'folder',
        onClick: () => this.handleCreateSpace(),
      },
      {
        id: 'project',
        label: 'Project',
        icon: 'kanban',
        onClick: () => this.handleCreateProject(),
      },
      {
        id: 'folder',
        label: 'Folder',
        icon: 'folder',
        onClick: () => this.handleCreateFolder(),
      },
    ];
  });

  readonly workspacesActions = computed<ListHeaderAction[]>(() => {
    const template = this.workspaceAddDropdownTemplate();
    return [
      { icon: 'ellipsis' as IconName, onClick: () => this.handleWorkspaceMenu() },
      ...(template
        ? [
            {
              icon: 'plus' as IconName,
              dropdownTemplate: template,
            },
          ]
        : []),
    ];
  });

  handleWorkspaceMenu(): void {
    // TODO: Implement workspace menu (settings, etc.)
  }

  async handleCreateSpace(): Promise<void> {
    const orgId = this.organizationService.currentOrganization()?.id;
    if (!orgId) return;

    try {
      await firstValueFrom(
        this.modal.open(CreateSpaceModal, this.viewContainerRef, {
          size: 'md',
          data: { organizationId: orgId },
        }),
      );
      this.workspaceService.reload();
    } catch (error) {
      // Modal was closed/cancelled
    }
  }

  async handleCreateProject(): Promise<void> {
    const orgId = this.organizationService.currentOrganization()?.id;
    if (!orgId) return;

    try {
      await firstValueFrom(
        this.modal.open(CreateProjectModal, this.viewContainerRef, {
          size: 'md',
          data: { organizationId: orgId },
        }),
      );
      this.workspaceService.reload();
    } catch (error) {
      // Modal was closed/cancelled
    }
  }

  async handleCreateFolder(): Promise<void> {
    const orgId = this.organizationService.currentOrganization()?.id;
    if (!orgId) return;

    try {
      await firstValueFrom(
        this.modal.open(CreateFolderModal, this.viewContainerRef, {
          size: 'md',
          data: { organizationId: orgId },
        }),
      );
      this.workspaceService.reload();
    } catch (error) {
      // Modal was closed/cancelled
    }
  }
}
