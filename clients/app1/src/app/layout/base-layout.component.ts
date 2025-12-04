import { Component, signal, input, computed } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-base-layout',
  imports: [RouterOutlet],
  template: `
    <div class="layout" [class.layout--sidebar-open]="sidebarOpen()">
      <!-- Header -->
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
            <div class="layout_logo">
              <span class="layout_logo-text">Pages</span>
            </div>
          </div>
          <nav class="layout_nav" [class.layout_nav--hidden]="!showNav()">
            <ng-content select="[slot=nav]"></ng-content>
          </nav>
          <div class="layout_header-right">
            <ng-content select="[slot=user-menu]"></ng-content>
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

        <!-- Main Content -->
        <main class="layout_main">
          <router-outlet></router-outlet>
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
      @reference "#theme";

      .layout {
        @apply flex flex-col min-h-screen bg-gray-50;
      }

      /* Header */
      .layout_header {
        @apply bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50;
      }

      .layout_header-content {
        @apply flex items-center justify-between px-4 lg:px-6 h-16;
      }

      .layout_header-left {
        @apply flex items-center gap-4;
      }

      .layout_sidebar-toggle {
        @apply lg:hidden p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors;
        @apply border-none bg-transparent cursor-pointer;
      }

      .layout_sidebar-toggle-icon {
        @apply text-xl;
      }

      .layout_logo {
        @apply flex items-center;
      }

      .layout_logo-text {
        @apply text-xl font-bold text-gray-900;
      }

      .layout_nav {
        @apply hidden lg:flex items-center gap-6;
      }

      .layout_nav--hidden {
        @apply hidden;
      }

      .layout_header-right {
        @apply flex items-center;
      }

      /* Body */
      .layout_body {
        @apply flex flex-1 overflow-hidden;
      }

      /* Sidebar */
      .layout_sidebar {
        @apply hidden lg:flex lg:flex-col w-64 bg-white border-r border-gray-200;
        @apply transition-transform duration-300 ease-in-out;
      }

      .layout_sidebar--hidden {
        @apply hidden;
      }

      .layout_sidebar-nav {
        @apply flex flex-col p-4 space-y-1 overflow-y-auto flex-1;
      }

      /* Mobile sidebar overlay */
      @media (max-width: 1023px) {
        .layout--sidebar-open .layout_sidebar {
          @apply fixed inset-y-0 left-0 z-40 flex flex-col w-64 bg-white shadow-lg;
          @apply top-16;
        }

        .layout--sidebar-open::before {
          content: '';
          @apply fixed inset-0 z-30;
          background-color: rgba(0, 0, 0, 0.5);
          @apply lg:hidden;
        }
      }

      /* Main Content */
      .layout_main {
        @apply flex-1 overflow-y-auto p-6 lg:p-8;
      }

      /* Footer */
      .layout_footer {
        @apply bg-white border-t border-gray-200 mt-auto;
      }

      .layout_footer-content {
        @apply container mx-auto px-6 py-4;
      }

      .layout_footer-links {
        @apply flex flex-wrap gap-4 mb-2;
      }

      .layout_footer-copyright {
        @apply text-sm text-gray-600;
      }

      /* Responsive adjustments */
      @media (max-width: 640px) {
        .layout_main {
          @apply p-4;
        }
      }
    `,
  ],
  standalone: true,
})
export class BaseLayoutComponent {
  // Inputs
  showNav = input(true);
  showFooter = input(true);
  initialSidebarOpen = input(false);

  // Sidebar state
  protected readonly sidebarOpen = signal(this.initialSidebarOpen());

  // Computed
  protected readonly currentYear = computed(() => new Date().getFullYear());

  // Methods
  toggleSidebar(): void {
    this.sidebarOpen.update((open) => !open);
  }

  closeSidebar(): void {
    this.sidebarOpen.set(false);
  }
}
