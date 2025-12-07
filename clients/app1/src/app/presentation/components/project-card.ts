import { Component, ChangeDetectionStrategy, input, output, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Icon, Dropdown, Button } from 'shared-ui';
import { Project } from '../../application/services/project.service';

@Component({
  selector: 'app-project-card',
  imports: [Icon, Dropdown, RouterLink, Button],
  template: `
    <div class="project-card">
      <a
        [routerLink]="['/app/projects', project().id]"
        class="project-card_link"
        [attr.aria-label]="'View ' + project().name"
      >
        <div class="project-card_content">
          <div class="project-card_header">
            <div class="project-card_icon">
              <lib-icon name="folder" size="lg" />
            </div>
            <div class="project-card_key">{{ project().key }}</div>
          </div>
          <div class="project-card_info">
            <h3 class="project-card_name">{{ project().name }}</h3>
            @if (project().description) {
              <p class="project-card_description">{{ project().description }}</p>
            }
            <div class="project-card_meta">
              <div class="project-card_member-count">
                <lib-icon name="users" size="sm" />
                <span>{{ project().memberCount || 0 }} member(s)</span>
              </div>
            </div>
          </div>
        </div>
      </a>
      <div class="project-card_actions">
        <lib-button
          variant="ghost"
          size="sm"
          [iconOnly]="true"
          leftIcon="menu"
          [libDropdown]="actionsDropdownTemplate"
          [position]="'below'"
          class="project-card_actions-button"
          #actionsDropdown="libDropdown"
        >
        </lib-button>
        <ng-template #actionsDropdownTemplate>
          <div class="project-card_actions-menu">
            <lib-button
              variant="ghost"
              size="md"
              class="project-card_action-item"
              (clicked)="handleSettings(actionsDropdown)"
            >
              <lib-icon name="settings" size="sm" class="project-card_action-icon" />
              <span>Settings</span>
            </lib-button>
          </div>
        </ng-template>
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .project-card {
        @apply relative;
        @apply flex flex-col;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-primary;
        @apply transition-all;
        @apply hover:shadow-lg;
        min-height: 180px;
      }

      .project-card_link {
        @apply flex-1;
        @apply p-6;
        text-decoration: none;
        color: inherit;
        @apply cursor-pointer;
        @apply transition-colors;
      }

      .project-card_link:hover {
        color: inherit;
      }

      .project-card_content {
        @apply flex flex-col;
        @apply gap-4;
      }

      .project-card_header {
        @apply flex items-center justify-between;
        @apply gap-3;
      }

      .project-card_icon {
        @apply flex items-center justify-center;
        @apply w-12 h-12;
        @apply rounded-lg;
        @apply bg-bg-tertiary;
        @apply text-primary-500;
      }

      .project-card_key {
        @apply text-xs font-mono font-semibold;
        @apply px-2 py-1;
        @apply rounded;
        @apply bg-bg-secondary;
        @apply text-text-secondary;
      }

      .project-card_info {
        @apply flex flex-col;
        @apply gap-2;
        @apply flex-1;
      }

      .project-card_name {
        @apply text-xl font-semibold;
        @apply text-text-primary;
        margin: 0;
      }

      .project-card_description {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
        @apply line-clamp-2;
      }

      .project-card_meta {
        @apply flex items-center;
        @apply gap-4;
        @apply mt-auto;
      }

      .project-card_member-count {
        @apply flex items-center;
        @apply gap-2;
        @apply text-sm;
        @apply text-text-secondary;
      }

      .project-card_actions {
        @apply absolute;
        @apply top-4 right-4;
      }

      .project-card_actions-button {
        @apply z-10;
      }

      .project-card_actions-menu {
        @apply py-1;
        min-width: 10rem;
      }

      .project-card_action-item {
        @apply w-full;
        @apply justify-start;
        @apply px-4 py-2;
      }

      .project-card_action-icon {
        @apply flex-shrink-0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProjectCard {
  readonly project = input.required<Project>();
  readonly onSettings = output<Project>();

  handleSettings(dropdown: Dropdown): void {
    dropdown.open.set(false);
    this.onSettings.emit(this.project());
  }
}
