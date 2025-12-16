import { Component, signal, input, computed, inject } from '@angular/core';
import { RouterOutlet, Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { filter, map } from 'rxjs';
import { AppSidebar } from './app-sidebar/app-sidebar';
import { Breadcrumbs, BreadcrumbItem } from '../../shared/components/breadcrumbs/breadcrumbs';
import { SearchBar } from '../../shared/components/search-bar/search-bar';
import { AvatarStack, AvatarStackItem } from '../../shared/components/avatar-stack/avatar-stack';
import { Button, Icon, IconName } from 'shared-ui';
import { UserMenu } from '../../shared/components/user-menu/user-menu';
import { NotificationBell } from '../../shared/components/notification-bell/notification-bell';
import { LanguageSwitcher } from '../../shared/components/language-switcher/language-switcher';

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
    UserMenu,
    NotificationBell,
    LanguageSwitcher,
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

              <!-- Quick Actions -->
              <div class="layout_quick-actions">
                <app-language-switcher />
              </div>

              <!-- Notifications -->
              <div class="layout_notifications">
                <app-notification-bell />
              </div>

              <!-- User Menu -->
              <div class="layout_user-menu">
                <app-user-menu />
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

      .layout_header-content {
        @apply flex items-center justify-between;
        width: 100%;
        gap: 1rem;
      }

      .layout_header-left {
        @apply flex items-center;
        gap: 0.5rem;
        flex: 0 0 auto;
        min-width: 0;
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
        flex: 1 1 auto;
        min-width: 0;
        max-width: none;
        @apply hidden lg:flex;
      }

      .layout_search > * {
        @apply w-full;
      }

      /* Header Right Actions */
      .layout_header-right {
        @apply flex items-center;
        gap: 0.75rem;
        flex-shrink: 0;
      }

      .layout_avatars {
        @apply flex items-center;
        @apply -space-x-2;
      }

      /* Quick Actions */
      .layout_quick-actions {
        @apply flex items-center;
        gap: 0.5rem;
      }

      /* Notifications */
      .layout_notifications {
        @apply flex items-center;
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

        .layout_search {
          @apply hidden;
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
    const url = this.currentUrl();
    // Simple breadcrumb logic - can be enhanced
    if (url.startsWith('/app/organizations')) {
      return [{ label: 'Organizations' }];
    }
    if (url.startsWith('/app/organizations') && url.includes('/projects')) {
      return [{ label: 'Organizations', href: '/app/organizations' }, { label: 'Projects' }];
    }
    return [{ label: 'Dashboard' }];
  });

  readonly actionButton = computed<{ label: string; icon: IconName } | null>(() => {
    const url = this.currentUrl();
    if (url.includes('/projects')) {
      return { label: 'New Task', icon: 'plus' };
    }
    if (url.includes('/docs')) {
      return { label: 'Upload', icon: 'upload' };
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
