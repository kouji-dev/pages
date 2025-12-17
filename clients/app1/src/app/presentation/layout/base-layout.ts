import { Component, signal, input, computed, inject } from '@angular/core';
import { RouterOutlet, Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { filter, map } from 'rxjs';
import { TranslateService } from '@ngx-translate/core';
import { AppSidebar } from './app-sidebar/app-sidebar';
import { Breadcrumbs, BreadcrumbItem } from '../../shared/components/breadcrumbs/breadcrumbs';
import { SearchBar } from '../../shared/components/search-bar/search-bar';
import { AvatarStack, AvatarStackItem } from '../../shared/components/avatar-stack/avatar-stack';
import { Button, Icon, IconName } from 'shared-ui';
import { NotificationBell } from '../../shared/components/notification-bell/notification-bell';
import { LanguageService } from '../../core/i18n/language.service';

const teamMembers: AvatarStackItem[] = [
  { name: 'Alice', avatarUrl: 'https://i.pravatar.cc/150?img=1', initials: 'AL' },
  { name: 'Bob', avatarUrl: 'https://i.pravatar.cc/150?img=2', initials: 'BO' },
  { name: 'Charlie', avatarUrl: 'https://i.pravatar.cc/150?img=3', initials: 'CH' },
  { name: 'Diana', avatarUrl: 'https://i.pravatar.cc/150?img=4', initials: 'DI' },
];

@Component({
  selector: 'app-base-layout',
  imports: [
    RouterOutlet,
    AppSidebar,
    Breadcrumbs,
    SearchBar,
    AvatarStack,
    Button,
    Icon,
    NotificationBell,
  ],
  template: `
    <div class="layout" [class.layout--sidebar-open]="sidebarOpen()">
      <!-- Sidebar -->
      <aside class="layout_sidebar" [class.layout_sidebar--hidden]="!sidebarOpen()">
        <app-app-sidebar />
      </aside>

      <!-- Main Content Area -->
      <main class="layout_main">
        <!-- Header Toolbar -->
        <header class="layout_header">
          <div class="layout_header-content">
            <div class="layout_header-left">
              <!-- Sidebar Toggle (always visible) -->
              <button
                class="layout_sidebar-toggle"
                [class.layout_sidebar-toggle--open]="sidebarOpen()"
                (click)="toggleSidebar()"
                type="button"
                [attr.aria-label]="sidebarOpen() ? 'Hide sidebar' : 'Show sidebar'"
              >
                <lib-icon name="menu" size="sm" class="layout_sidebar-toggle-icon" />
              </button>

              <!-- Breadcrumbs -->
              <app-breadcrumbs [items]="breadcrumbs()" />
            </div>

            <!-- Global Search (Center) -->
            <div class="layout_search">
              <app-search-bar />
            </div>

            <!-- Header Right Actions -->
            <div class="layout_header-right">
              <!-- Stacked Avatars -->
              <div class="layout_avatars">
                <app-avatar-stack [items]="teamMembers" [limit]="4" size="sm" />
              </div>

              <!-- Action Button (context-aware) -->
              @if (actionButton()) {
                <lib-button
                  [variant]="'primary'"
                  [size]="'sm'"
                  [leftIcon]="actionButton()!.icon"
                  (clicked)="handleActionClick()"
                >
                  {{ actionButton()!.label }}
                </lib-button>
              }

              <!-- Notifications -->
              <div class="layout_notifications">
                <app-notification-bell />
              </div>
            </div>
          </div>
        </header>

        <!-- Content Area (scrollable) -->
        <div class="layout_content">
          <router-outlet />
        </div>
      </main>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .layout {
        @apply flex w-full;
        height: 100vh;
        @apply bg-background;
      }

      /* Sidebar */
      .layout_sidebar {
        @apply flex flex-col;
        width: 17.5rem; /* 280px */
        height: 100%;
        @apply bg-navigation;
        @apply border-r border-navigation-border;
        @apply transition-all duration-300 ease-in-out;
        flex-shrink: 0;
        overflow: hidden;
      }

      /* Compact mode - narrower sidebar */
      :host-context([data-density='compact']) .layout_sidebar {
        width: 14rem; /* 224px - narrower in compact mode */
      }

      .layout_sidebar--hidden {
        width: 0;
        min-width: 0;
        border-right: none;
        transform: translateX(-100%);
      }

      /* Main Content Area */
      .layout_main {
        @apply flex-1 flex flex-col;
        @apply bg-background;
        min-width: 0; /* Prevent flex item from overflowing */
        overflow: hidden;
      }

      /* Header Toolbar */
      .layout_header {
        @apply flex items-center;
        height: 4rem; /* 64px - matches React implementation */
        @apply bg-background;
        @apply border-b border-border;
        padding: 0 1rem;
        @apply lg:px-4;
        flex-shrink: 0;
      }

      /* Compact mode - shorter header to match sidebar org selector */
      :host-context([data-density='compact']) .layout_header {
        height: 3rem !important;
      }

      .layout_header-content {
        display: grid;
        grid-template-columns: 20rem 1fr 18rem;
        @apply items-center;
        width: 100%;
        gap: 1rem;
      }

      .layout_header-left {
        @apply flex items-center;
        gap: 0.5rem;
        min-width: 0;
        max-width: 20rem;
        overflow: hidden;
      }

      .layout_sidebar-toggle {
        @apply p-2 rounded-md transition-colors;
        @apply border-none bg-transparent cursor-pointer;
        @apply text-muted-foreground;
        @apply hover:text-foreground hover:bg-accent;
        margin-right: 0.5rem;
      }

      .layout_sidebar-toggle-icon {
        @apply transition-transform duration-300 ease-in-out;
      }

      .layout_sidebar-toggle--open .layout_sidebar-toggle-icon {
        @apply rotate-90;
      }

      /* Global Search (Center) */
      .layout_search {
        @apply flex items-center justify-center;
        min-width: 0;
        max-width: none;
        @apply hidden lg:flex;
        @apply px-4;
        @apply mx-4;
      }

      .layout_search > * {
        @apply w-full;
        max-width: 32rem; /* Limit search bar width */
      }

      /* Header Right Actions */
      .layout_header-right {
        @apply flex items-center;
        gap: 0.75rem;
        flex-shrink: 0;
        height: 100%;
        width: 18rem;
        min-width: 18rem;
        max-width: 18rem;
        @apply justify-end;
      }

      .layout_avatars {
        @apply flex items-center;
        @apply -space-x-2;
        @apply h-full;
        @apply items-center;
      }

      /* Notifications */
      .layout_notifications {
        @apply flex items-center justify-center;
        @apply h-full;
      }

      .layout_notifications ::ng-deep .notification-bell {
        @apply h-full;
        @apply flex items-center;
      }

      .layout_notifications ::ng-deep .notification-bell_button {
        @apply h-full;
        @apply flex items-center justify-center;
      }

      /* User Menu */
      .layout_user-menu {
        @apply flex items-center;
      }

      /* Content Area (scrollable) */
      .layout_content {
        @apply flex-1 overflow-y-auto;
        @apply bg-muted/30;
      }

      /* Responsive adjustments */
      @media (max-width: 1023px) {
        .layout_header {
          padding: 0 0.75rem;
        }

        .layout_header-content {
          grid-template-columns: 1fr auto;
        }

        .layout_header-left {
          max-width: none;
        }

        .layout_header-right {
          width: auto;
          min-width: auto;
          max-width: none;
        }

        .layout_search {
          @apply hidden;
          display: none !important;
        }
      }

      @media (max-width: 639px) {
        .layout_header {
          padding: 0 0.5rem;
        }
      }
    `,
  ],
  standalone: true,
})
export class BaseLayout {
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly languageService = inject(LanguageService);
  private readonly translateService = inject(TranslateService);

  // Inputs
  initialSidebarOpen = input(true); // Default to open

  // Sidebar state
  readonly sidebarOpen = signal(this.initialSidebarOpen());

  // Team members for avatar stack
  readonly teamMembers = teamMembers;

  // Make router URL reactive using toSignal
  private readonly currentUrl = toSignal(
    this.router.events.pipe(
      filter((event) => event instanceof NavigationEnd),
      map(() => this.router.url),
    ),
    { initialValue: this.router.url },
  );

  // Computed
  readonly currentYear = computed(() => new Date().getFullYear());

  readonly breadcrumbs = computed<BreadcrumbItem[]>(() => {
    // Depend on currentLanguage to trigger recomputation when language changes
    this.languageService.currentLanguage();
    const url = this.currentUrl();
    const segments = url.split('/').filter(Boolean);

    // Organizations list
    if (segments.length === 2 && segments[0] === 'app' && segments[1] === 'organizations') {
      return [{ label: this.translateService.instant('navigation.organizations') }];
    }

    // Organization settings
    if (
      segments.length === 3 &&
      segments[0] === 'app' &&
      segments[1] === 'organizations' &&
      segments[2] === 'settings'
    ) {
      return [
        {
          label: this.translateService.instant('navigation.organizations'),
          href: '/app/organizations',
        },
        { label: this.translateService.instant('navigation.settings') },
      ];
    }

    // Organization context routes (require organizationId)
    if (segments.length >= 3 && segments[0] === 'app' && segments[1] === 'organizations') {
      const organizationId = segments[2];
      const breadcrumbs: BreadcrumbItem[] = [
        {
          label: this.translateService.instant('navigation.organizations'),
          href: '/app/organizations',
        },
      ];

      // If we have organization context, try to get organization name
      // For now, use a generic label - can be enhanced with actual org name
      if (segments.length === 3) {
        // /app/organizations/:organizationId - redirects to projects
        breadcrumbs.push({ label: this.translateService.instant('navigation.projects') });
      } else if (segments[3] === 'dashboard') {
        // /app/organizations/:organizationId/dashboard
        breadcrumbs.push({ label: this.translateService.instant('navigation.dashboard') });
      } else if (segments[3] === 'projects') {
        breadcrumbs.push({ label: this.translateService.instant('navigation.projects') });
        if (segments.length >= 5 && segments[4]) {
          // /app/organizations/:organizationId/projects/:projectId
          const projectId = segments[4];
          if (segments.length === 5) {
            breadcrumbs.push({ label: this.translateService.instant('breadcrumbs.project') });
          } else if (segments[5] === 'settings') {
            // /app/organizations/:organizationId/projects/:projectId/settings
            breadcrumbs.push({
              label: this.translateService.instant('breadcrumbs.project'),
              href: `/app/organizations/${organizationId}/projects/${projectId}`,
            });
            breadcrumbs.push({ label: this.translateService.instant('navigation.settings') });
          } else if (segments[5] === 'issues' && segments[6]) {
            // /app/organizations/:organizationId/projects/:projectId/issues/:issueId
            breadcrumbs.push({
              label: this.translateService.instant('breadcrumbs.project'),
              href: `/app/organizations/${organizationId}/projects/${projectId}`,
            });
            breadcrumbs.push({ label: this.translateService.instant('breadcrumbs.issue') });
          }
        }
      } else if (segments[3] === 'spaces') {
        breadcrumbs.push({ label: this.translateService.instant('navigation.spaces') });
        if (segments.length >= 5 && segments[4]) {
          // /app/organizations/:organizationId/spaces/:spaceId
          const spaceId = segments[4];
          if (segments.length === 5) {
            breadcrumbs.push({ label: this.translateService.instant('breadcrumbs.space') });
          } else if (segments[5] === 'settings') {
            // /app/organizations/:organizationId/spaces/:spaceId/settings
            breadcrumbs.push({
              label: this.translateService.instant('breadcrumbs.space'),
              href: `/app/organizations/${organizationId}/spaces/${spaceId}`,
            });
            breadcrumbs.push({ label: this.translateService.instant('navigation.settings') });
          } else if (segments[5] === 'pages' && segments[6]) {
            // /app/organizations/:organizationId/spaces/:spaceId/pages/:pageId
            breadcrumbs.push({
              label: this.translateService.instant('breadcrumbs.space'),
              href: `/app/organizations/${organizationId}/spaces/${spaceId}`,
            });
            breadcrumbs.push({ label: this.translateService.instant('breadcrumbs.page') });
          }
        }
      }
      return breadcrumbs;
    }

    // Profile
    if (segments.length === 2 && segments[0] === 'app' && segments[1] === 'profile') {
      return [{ label: this.translateService.instant('navigation.profile') }];
    }

    // Default to Dashboard
    return [{ label: this.translateService.instant('navigation.dashboard') }];
  });

  readonly actionButton = computed<{ label: string; icon: IconName } | null>(() => {
    const url = this.currentUrl();
    if (url.includes('/projects')) {
      return { label: 'New Task', icon: 'plus' };
    }
    if (url.includes('/spaces')) {
      return { label: 'Add Page', icon: 'plus' };
    }
    return null;
  });

  // Methods
  toggleSidebar(): void {
    this.sidebarOpen.update((open) => !open);
  }

  closeSidebar(): void {
    this.sidebarOpen.set(false);
  }

  handleActionClick(): void {
    const action = this.actionButton();
    if (action) {
      // Handle action button click
      // TODO: Implement action handlers
    }
  }
}
