import { Component, signal, input, computed } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-base-layout',
  imports: [RouterOutlet],
  template: `
    <div class="layout" [class.layout--sidebar-open]="sidebarOpen()">
      <!-- Header Toolbar (Jira/Confluence Style) -->
      <header class="layout_header">
        <div class="layout_header-content">
          <div class="layout_header-left">
            <button
              class="layout_sidebar-toggle"
              (click)="toggleSidebar()"
              type="button"
              aria-label="Toggle sidebar"
            >
              <span class="layout_sidebar-toggle-icon">☰</span>
            </button>
            <!-- Logo/Branding Area -->
            <div class="layout_logo">
              <span class="layout_logo-text">Pages</span>
            </div>
            <!-- Breadcrumb Navigation (Jira/Confluence Style) -->
            <div class="layout_breadcrumbs">
              <ng-content select="[slot=breadcrumbs]"></ng-content>
            </div>
          </div>
          <!-- Global Search (Center) -->
          <div class="layout_search">
            <ng-content select="[slot=search]"></ng-content>
          </div>
          <!-- Header Right Actions -->
          <div class="layout_header-right">
            <!-- Navigation Menu -->
            <nav class="layout_nav" [class.layout_nav--hidden]="!showNav()">
              <ng-content select="[slot=nav]"></ng-content>
            </nav>
            <!-- Quick Actions -->
            <div class="layout_quick-actions">
              <ng-content select="[slot=quick-actions]"></ng-content>
            </div>
            <!-- Notifications -->
            <div class="layout_notifications">
              <ng-content select="[slot=notifications]"></ng-content>
            </div>
            <!-- User Menu -->
            <div class="layout_user-menu">
              <ng-content select="[slot=user-menu]"></ng-content>
            </div>
          </div>
        </div>
      </header>

      <div class="layout_body">
        <!-- Sidebar -->
        <aside class="layout_sidebar" [class.layout_sidebar--hidden]="!sidebarOpen()">
          <nav class="layout_sidebar-nav">
            <ng-content select="[slot=sidebar-nav]"></ng-content>
          </nav>
        </aside>

        <!-- Main Content Area (Notion Style: Generous padding, wide readable max-width) -->
        <main class="layout_main">
          <div class="layout_main-content">
            <router-outlet></router-outlet>
          </div>
        </main>
      </div>

      <!-- Footer -->
      @if (showFooter()) {
        <footer class="layout_footer">
          <div class="layout_footer-content">
            <div class="layout_footer-links">
              <ng-content select="[slot=footer-links]"></ng-content>
            </div>
            <div class="layout_footer-copyright">
              <p>&copy; {{ currentYear() }} Pages. All rights reserved.</p>
            </div>
          </div>
        </footer>
      }
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .layout {
        @apply flex flex-col min-h-screen;
        background-color: var(--color-bg-primary);
      }

      /* Header Toolbar (Jira/Confluence Style) */
      .layout_header {
        @apply sticky top-0 z-50;
        background-color: var(--color-bg-primary);
        border-bottom: 1px solid var(--color-border-default);
        box-shadow: var(--shadow-sm);
      }

      .layout_header-content {
        @apply flex items-center justify-between;
        height: 3.5rem; /* 56px - Jira/Confluence style */
        padding: 0 1rem;
        @apply lg:px-6;
      }

      .layout_header-left {
        @apply flex items-center;
        gap: 1rem;
        flex: 1;
        min-width: 0;
      }

      .layout_sidebar-toggle {
        @apply lg:hidden p-2 rounded-md transition-colors;
        @apply border-none bg-transparent cursor-pointer;
        color: var(--color-text-secondary);
      }

      .layout_sidebar-toggle:hover {
        color: var(--color-text-primary);
        background-color: var(--color-bg-hover);
      }

      .layout_sidebar-toggle-icon {
        @apply text-xl;
      }

      /* Logo/Branding Area */
      .layout_logo {
        @apply flex items-center;
        flex-shrink: 0;
      }

      .layout_logo-text {
        @apply text-xl font-bold;
        color: var(--color-text-primary);
      }

      /* Breadcrumb Navigation (Jira/Confluence Style) */
      .layout_breadcrumbs {
        @apply flex items-center;
        flex: 1;
        min-width: 0;
        margin-left: 1.5rem;
        @apply hidden md:flex;
      }

      /* Global Search (Center) */
      .layout_search {
        @apply flex items-center justify-center;
        flex: 1;
        max-width: 600px;
        margin: 0 1rem;
        @apply hidden lg:flex;
      }

      /* Header Right Actions */
      .layout_header-right {
        @apply flex items-center;
        gap: 0.75rem;
        flex-shrink: 0;
      }

      /* Navigation Menu */
      .layout_nav {
        @apply hidden lg:flex items-center;
        gap: 1.5rem;
      }

      .layout_nav--hidden {
        @apply hidden;
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

      /* Body */
      .layout_body {
        @apply flex flex-1 overflow-hidden;
      }

      /* Sidebar (Notion Style) */
      .layout_sidebar {
        @apply hidden lg:flex lg:flex-col;
        width: 17.5rem; /* 280px - Notion style, wider than typical */
        background-color: var(--color-bg-secondary); /* Notion's light beige */
        border-right: 1px solid var(--color-border-default);
        @apply transition-transform duration-300 ease-in-out;
      }

      .layout_sidebar--hidden {
        @apply hidden;
      }

      .layout_sidebar-nav {
        @apply flex flex-col overflow-y-auto flex-1;
        padding: 1rem;
        gap: 0.25rem; /* Generous spacing between items (Notion style) */
      }

      /* Mobile sidebar overlay */
      @media (max-width: 1023px) {
        .layout--sidebar-open .layout_sidebar {
          @apply fixed inset-y-0 left-0 z-40 flex flex-col shadow-lg;
          width: 17.5rem;
          background-color: var(--color-bg-secondary);
          top: 3.5rem; /* Match header height */
        }

        .layout--sidebar-open::before {
          content: '';
          @apply fixed inset-0 z-30;
          background-color: var(--color-bg-overlay);
          @apply lg:hidden;
        }
      }

      /* Main Content Area (Notion Style: Generous padding, wide readable max-width) */
      .layout_main {
        @apply flex-1 overflow-y-auto;
        background-color: var(--color-bg-primary);
      }

      .layout_main-content {
        @apply mx-auto;
        width: 100%;
        max-width: 62.5rem; /* 1000px - wide but readable */
        padding: 2rem;
        @apply lg:px-24; /* ~96px sides on desktop (Notion style) */
        @apply lg:py-8;
      }

      /* Footer */
      .layout_footer {
        @apply mt-auto;
        background-color: var(--color-bg-primary);
        border-top: 1px solid var(--color-border-default);
      }

      .layout_footer-content {
        @apply mx-auto;
        max-width: 62.5rem; /* Match main content max-width */
        padding: 1.5rem 2rem;
        @apply lg:px-24;
      }

      .layout_footer-links {
        @apply flex flex-wrap;
        gap: 1rem;
        margin-bottom: 0.75rem;
      }

      .layout_footer-copyright {
        @apply text-sm;
        color: var(--color-text-secondary);
      }

      /* Responsive adjustments */
      @media (max-width: 1023px) {
        .layout_header-content {
          padding: 0 0.75rem;
        }

        .layout_search {
          @apply hidden;
        }

        .layout_breadcrumbs {
          @apply hidden;
        }
      }

      @media (max-width: 639px) {
        .layout_main-content {
          padding: 1rem;
        }

        .layout_header-content {
          padding: 0 0.5rem;
        }

        .layout_footer-content {
          padding: 1rem;
        }
      }
    `,
  ],
  standalone: true,
})
export class BaseLayout {
  // Inputs
  showNav = input(true);
  showFooter = input(true);
  initialSidebarOpen = input(false);

  // Sidebar state
  readonly sidebarOpen = signal(this.initialSidebarOpen());

  // Computed
  readonly currentYear = computed(() => new Date().getFullYear());

  // Methods
  toggleSidebar(): void {
    this.sidebarOpen.update((open) => !open);
  }

  closeSidebar(): void {
    this.sidebarOpen.set(false);
  }
}
