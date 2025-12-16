import { Component, ChangeDetectionStrategy, signal, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { Button, Icon } from 'shared-ui';
import { ThemeToggle } from '../../shared/components/theme-toggle/theme-toggle';
import { TranslatePipe } from '@ngx-translate/core';

@Component({
  selector: 'app-public-nav',
  imports: [RouterLink, RouterLinkActive, Button, Icon, ThemeToggle, TranslatePipe],
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
            <a
              routerLink="/"
              routerLinkActive="public-nav_link--active"
              class="public-nav_link"
              [routerLinkActiveOptions]="{ exact: true }"
              >{{ 'public.home' | translate }}</a
            >
            <a
              routerLink="/features"
              routerLinkActive="public-nav_link--active"
              class="public-nav_link"
              >{{ 'public.features' | translate }}</a
            >
            <a
              routerLink="/pricing"
              routerLinkActive="public-nav_link--active"
              class="public-nav_link"
              >{{ 'public.pricing' | translate }}</a
            >
            <a
              routerLink="/demo"
              routerLinkActive="public-nav_link--active"
              class="public-nav_link public-nav_link--demo"
              >{{ 'public.demo' | translate }}</a
            >
          </div>
          <div class="public-nav_actions">
            <app-theme-toggle />
            <lib-button variant="ghost" size="md" [link]="['/login']">{{
              'public.logIn' | translate
            }}</lib-button>
            <lib-button variant="primary" size="md" [link]="['/register']">{{
              'public.signUp' | translate
            }}</lib-button>
          </div>
        </div>

        <!-- Mobile Menu Button -->
        <button
          class="public-nav_mobile-toggle"
          type="button"
          (click)="toggleMobileMenu()"
          [attr.aria-expanded]="isMobileMenuOpen()"
          [attr.aria-label]="'public.toggleMobileMenu' | translate"
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
              >{{ 'public.home' | translate }}</a
            >
            <a
              routerLink="/features"
              routerLinkActive="public-nav_mobile-link--active"
              class="public-nav_mobile-link"
              (click)="closeMobileMenu()"
              >{{ 'public.features' | translate }}</a
            >
            <a
              routerLink="/pricing"
              routerLinkActive="public-nav_mobile-link--active"
              class="public-nav_mobile-link"
              (click)="closeMobileMenu()"
              >{{ 'public.pricing' | translate }}</a
            >
            <a
              routerLink="/demo"
              routerLinkActive="public-nav_mobile-link--active"
              class="public-nav_mobile-link public-nav_mobile-link--demo"
              (click)="closeMobileMenu()"
              >{{ 'public.demo' | translate }}</a
            >
          </div>
          <div class="public-nav_mobile-actions">
            <lib-button variant="ghost" size="md" [link]="['/login']" (click)="closeMobileMenu()">{{
              'public.logIn' | translate
            }}</lib-button>
            <lib-button
              variant="primary"
              size="md"
              [link]="['/register']"
              (click)="closeMobileMenu()"
              >{{ 'public.signUp' | translate }}</lib-button
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
        @apply border-border;
        @apply bg-background/80 backdrop-blur-md;
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
        @apply text-foreground;
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
        @apply text-muted-foreground;
        text-decoration: none;
        @apply transition-colors;
        @apply relative;
        @apply hover:opacity-80;
      }

      .public-nav_link:hover {
        @apply text-primary;
      }

      .public-nav_link::after {
        content: '';
        @apply absolute bottom-0 left-0;
        @apply h-0.5;
        width: 0;
        @apply bg-primary;
        @apply transform -translate-y-1;
        @apply transition-all duration-300 ease-in-out;
      }

      .public-nav_link:hover::after {
        width: 100%;
      }

      .public-nav_link--active {
        @apply text-foreground;
      }

      .public-nav_link--active::after {
        width: 100%;
      }

      .public-nav_link--demo {
        @apply text-primary;
        font-weight: 600;
      }

      .public-nav_link--demo:hover {
        @apply text-primary;
      }

      .public-nav_link--demo::after {
        @apply bg-primary;
      }

      .public-nav_actions {
        @apply flex items-center gap-3;
      }

      .public-nav_mobile-toggle {
        @apply md:hidden;
        @apply p-2;
        @apply border-none bg-transparent;
        @apply text-foreground;
        @apply cursor-pointer;
        @apply hover:bg-muted rounded;
      }

      .public-nav_mobile {
        @apply md:hidden;
        @apply border-t;
        @apply border-border;
        @apply px-4 py-4;
        @apply bg-background;
      }

      .public-nav_mobile-links {
        @apply flex flex-col gap-4;
        @apply mb-4;
      }

      .public-nav_mobile-link {
        @apply text-base font-medium;
        @apply text-muted-foreground;
        text-decoration: none;
        @apply transition-colors;
        @apply py-2;
        @apply hover:opacity-80;
      }

      .public-nav_mobile-link:hover {
        @apply text-primary;
      }

      .public-nav_mobile-link--active {
        @apply text-foreground;
      }

      .public-nav_mobile-link--demo {
        @apply text-primary;
        font-weight: 600;
      }

      .public-nav_mobile-link--demo:hover {
        @apply text-primary;
      }

      .public-nav_mobile-actions {
        @apply flex flex-col gap-3;
        @apply pt-4 border-t;
        @apply border-border;
      }

      .public-nav_mobile-theme {
        @apply flex justify-center;
        @apply pb-2;
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
