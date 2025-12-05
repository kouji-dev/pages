import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { BaseLayout } from './base-layout';

@Component({
  selector: 'app-authenticated-layout',
  imports: [BaseLayout, RouterOutlet],
  template: `
    <app-base-layout>
      <!-- Breadcrumbs slot (Jira/Confluence style) -->
      <div slot="breadcrumbs">
        <!-- Breadcrumb navigation will be added here -->
      </div>

      <!-- Global search slot (Jira/Confluence style) -->
      <div slot="search">
        <!-- Global search will be added here -->
      </div>

      <!-- Navigation menu slot -->
      <div slot="nav">
        <!-- Navigation links will be added here -->
      </div>

      <!-- Quick actions slot -->
      <div slot="quick-actions">
        <!-- Quick actions will be added here -->
      </div>

      <!-- Notifications slot -->
      <div slot="notifications">
        <!-- Notifications will be added here -->
      </div>

      <!-- User menu slot -->
      <div slot="user-menu">
        <!-- User menu will be added here -->
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
