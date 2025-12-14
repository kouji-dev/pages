import { Component, ChangeDetectionStrategy } from '@angular/core';
import { BaseLayout } from './base-layout';
import { UserMenu } from '../components/user-menu';
import { OrganizationSelector } from '../components/organization-selector';
import { ThemeToggle } from '../components/theme-toggle';
import { SearchBar } from '../components/search-bar';
import { NotificationBell } from '../components/notification-bell';
import { LanguageSwitcher } from '../components/language-switcher';

@Component({
  selector: 'app-authenticated-layout',
  imports: [
    BaseLayout,
    UserMenu,
    OrganizationSelector,
    ThemeToggle,
    SearchBar,
    NotificationBell,
    LanguageSwitcher,
  ],
  styles: [
    `
      @reference "#mainstyles";

      .authenticated-layout_search-wrapper {
        @apply w-full;
        @apply h-full;
      }
    `,
  ],
  template: `
    <app-base-layout>
      <!-- Breadcrumbs slot (Jira/Confluence style) -->
      <div slot="breadcrumbs">
        <app-organization-selector />
      </div>

      <!-- Global search slot (Jira/Confluence style) -->
      <div slot="search" class="authenticated-layout_search-wrapper">
        <app-search-bar />
      </div>

      <!-- Navigation menu slot -->
      <div slot="nav">
        <!-- Navigation links will be added here -->
      </div>

      <!-- Quick actions slot -->
      <div slot="quick-actions" style="display: flex; align-items: center; gap: 0.5rem;">
        <app-language-switcher />
        <app-theme-toggle />
      </div>

      <!-- Notifications slot -->
      <div slot="notifications">
        <app-notification-bell />
      </div>

      <!-- User menu slot -->
      <div slot="user-menu">
        <app-user-menu />
      </div>

      <!-- Sidebar navigation slot (Notion style) -->
      <div slot="sidebar-nav">
        <!-- Sidebar navigation links will be added here -->
      </div>

      <!-- Footer links slot -->
      <div slot="footer-links">
        <!-- Footer links will be added here -->
      </div>
    </app-base-layout>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AuthenticatedLayout {}
