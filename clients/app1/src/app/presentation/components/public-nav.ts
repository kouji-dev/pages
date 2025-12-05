import { Component, ChangeDetectionStrategy, signal, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { Button, Icon } from 'shared-ui';

@Component({
  selector: 'app-public-nav',
  imports: [RouterLink, RouterLinkActive, Button, Icon],
  template: `
    <nav class="public-nav">
      <div class="public-nav_container">
        <a routerLink="/" class="public-nav_logo">
          <lib-icon name="file-text" size="lg" />
          <span class="public-nav_logo-text">Pages</span>
        </a>

        <!-- Desktop Navigation -->
        <div class="public-nav_desktop">
          <div class="public-nav_links">
            <a routerLink="/" routerLinkActive="public-nav_link--active" class="public-nav_link"
              >Home</a
            >
            <a
              routerLink="/features"
              routerLinkActive="public-nav_link--active"
              class="public-nav_link"
              >Features</a
            >
            <a
              routerLink="/pricing"
              routerLinkActive="public-nav_link--active"
              class="public-nav_link"
              >Pricing</a
            >
          </div>
          <div class="public-nav_actions">
            <lib-button variant="ghost" size="md" [routerLink]="['/login']">Log In</lib-button>
            <lib-button variant="primary" size="md" [routerLink]="['/register']"
              >Sign Up</lib-button
            >
          </div>
        </div>

        <!-- Mobile Menu Button -->
        <button
          class="public-nav_mobile-toggle"
          type="button"
          (click)="toggleMobileMenu()"
          [attr.aria-expanded]="isMobileMenuOpen()"
          aria-label="Toggle mobile menu"
        >
          <lib-icon [name]="isMobileMenuOpen() ? 'x' : 'menu'" size="md" />
        </button>
      </div>

      <!-- Mobile Navigation -->
      @if (isMobileMenuOpen()) {
        <div class="public-nav_mobile">
          <div class="public-nav_mobile-links">
            <a
              routerLink="/"
              routerLinkActive="public-nav_mobile-link--active"
              class="public-nav_mobile-link"
              (click)="closeMobileMenu()"
              >Home</a
            >
            <a
              routerLink="/features"
              routerLinkActive="public-nav_mobile-link--active"
              class="public-nav_mobile-link"
              (click)="closeMobileMenu()"
              >Features</a
            >
            <a
              routerLink="/pricing"
              routerLinkActive="public-nav_mobile-link--active"
              class="public-nav_mobile-link"
              (click)="closeMobileMenu()"
              >Pricing</a
            >
          </div>
          <div class="public-nav_mobile-actions">
            <lib-button
              variant="ghost"
              size="md"
              [routerLink]="['/login']"
              (click)="closeMobileMenu()"
              >Log In</lib-button
            >
            <lib-button
              variant="primary"
              size="md"
              [routerLink]="['/register']"
              (click)="closeMobileMenu()"
              >Sign Up</lib-button
            >
          </div>
        </div>
      }
    </nav>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .public-nav {
        @apply w-full;
        @apply border-b;
        border-color: var(--color-border-default);
        background: var(--color-bg-primary);
        @apply sticky top-0;
        z-index: 50;
        position: sticky;
      }

      .public-nav_container {
        @apply max-w-7xl mx-auto;
        @apply flex items-center justify-between;
        @apply px-4 sm:px-6 lg:px-8;
        @apply h-16;
      }

      .public-nav_logo {
        @apply flex items-center gap-2;
        @apply font-bold text-lg;
        color: var(--color-text-primary);
        text-decoration: none;
        @apply hover:opacity-80 transition-opacity;
      }

      .public-nav_logo-text {
        @apply hidden sm:inline;
      }

      .public-nav_desktop {
        @apply hidden md:flex items-center gap-6;
      }

      .public-nav_links {
        @apply flex items-center gap-6;
      }

      .public-nav_link {
        @apply text-sm font-medium;
        color: var(--color-text-secondary);
        text-decoration: none;
        @apply transition-colors;
        @apply relative;
        @apply hover:opacity-80;
      }

      .public-nav_link:hover {
        color: var(--color-primary-500);
      }

      .public-nav_link--active {
        color: var(--color-text-primary);
      }

      .public-nav_link--active::after {
        content: '';
        @apply absolute bottom-0 left-0 right-0;
        @apply h-0.5;
        background: var(--color-primary-500);
        @apply transform -translate-y-1;
      }

      .public-nav_actions {
        @apply flex items-center gap-3;
      }

      .public-nav_mobile-toggle {
        @apply md:hidden;
        @apply p-2;
        @apply border-none bg-transparent;
        color: var(--color-text-primary);
        @apply cursor-pointer;
        @apply hover:bg-gray-100 rounded;
      }

      .public-nav_mobile {
        @apply md:hidden;
        @apply border-t;
        border-color: var(--color-border-default);
        @apply px-4 py-4;
        background: var(--color-bg-primary);
      }

      .public-nav_mobile-links {
        @apply flex flex-col gap-4;
        @apply mb-4;
      }

      .public-nav_mobile-link {
        @apply text-base font-medium;
        color: var(--color-text-secondary);
        text-decoration: none;
        @apply transition-colors;
        @apply py-2;
        @apply hover:opacity-80;
      }

      .public-nav_mobile-link:hover {
        color: var(--color-primary-500);
      }

      .public-nav_mobile-link--active {
        color: var(--color-text-primary);
      }

      .public-nav_mobile-actions {
        @apply flex flex-col gap-3;
        @apply pt-4 border-t;
        border-color: var(--color-border-default);
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PublicNav {
  readonly isMobileMenuOpen = signal(false);

  toggleMobileMenu(): void {
    this.isMobileMenuOpen.update((open) => !open);
  }

  closeMobileMenu(): void {
    this.isMobileMenuOpen.set(false);
  }
}
