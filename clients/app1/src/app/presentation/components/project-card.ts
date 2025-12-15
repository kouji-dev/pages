import { Component, ChangeDetectionStrategy, input, output, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Icon, Button } from 'shared-ui';
import { OrganizationService } from '../../application/services/organization.service';
import { NavigationService } from '../../application/services/navigation.service';
import { Project } from '../../application/services/project.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-project-card',
  imports: [Icon, RouterLink, Button, TranslatePipe],
  template: `
    <div class="project-card">
      <a
        [routerLink]="getProjectRoute()"
        class="project-card_link"
        [attr.aria-label]="('projects.viewProject' | translate) + ': ' + project().name"
      >
        <div class="project-card_content">
          <div class="project-card_header">
            <div class="project-card_icon">
              <lib-icon name="folder" size="lg" />
            </div>
          </div>
          <div class="project-card_info">
            <div class="project-card_title-row">
              <div class="project-card_key">{{ project().key }}</div>
              <h3 class="project-card_name">{{ project().name }}</h3>
            </div>
            @if (project().description) {
              <p class="project-card_description">{{ project().description }}</p>
            }
            <div class="project-card_meta">
              <div class="project-card_member-count">
                <lib-icon name="users" size="sm" />
                <span>{{ project().memberCount || 0 }} {{ 'projects.members' | translate }}</span>
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
          leftIcon="settings"
          class="project-card_action-item"
          (clicked)="handleSettings()"
        >
        </lib-button>
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
        @apply flex items-center;
        @apply gap-3;
      }

      .project-card_icon {
        @apply flex items-center justify-center;
        @apply w-12 h-12;
        @apply rounded-lg;
        @apply bg-bg-tertiary;
        @apply text-primary-500;
      }

      .project-card_info {
        @apply flex flex-col;
        @apply gap-2;
        @apply flex-1;
      }

      .project-card_title-row {
        @apply flex items-center;
        @apply gap-2;
        @apply flex-wrap;
      }

      .project-card_key {
        @apply text-xs font-mono font-semibold;
        @apply px-2 py-1;
        @apply rounded;
        @apply bg-bg-secondary;
        @apply text-text-secondary;
        @apply flex-shrink-0;
      }

      .project-card_name {
        @apply text-xl font-semibold;
        @apply text-text-primary;
        @apply flex-1;
        @apply min-w-0;
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
        @apply flex items-center;
        @apply gap-1;
        @apply z-10;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProjectCard {
  private readonly organizationService = inject(OrganizationService);
  private readonly navigationService = inject(NavigationService);

  readonly project = input.required<Project>();
  readonly onSettings = output<Project>();

  getProjectRoute(): string[] {
    const orgId = this.organizationService.currentOrganization()?.id;
    const projectId = this.project().id;
    if (orgId) {
      return this.navigationService.getProjectRoute(orgId, projectId);
    }
    // Fallback if no org (shouldn't happen)
    return ['/app/organizations'];
  }

  handleSettings(): void {
    this.onSettings.emit(this.project());
  }
}
