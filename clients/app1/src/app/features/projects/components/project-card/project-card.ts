import { Component, ChangeDetectionStrategy, input, output, inject, computed } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Icon, Button, Badge, Avatar } from 'shared-ui';
import { OrganizationService } from '../../../../application/services/organization.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import { Project } from '../../../../application/services/project.service';
import { IssueUser } from '../../../../application/services/issue.service';
import { TranslatePipe } from '@ngx-translate/core';

@Component({
  selector: 'app-project-card',
  imports: [Icon, RouterLink, Button, Badge, Avatar, TranslatePipe],
  template: `
    <div class="project-card">
      <a
        [routerLink]="getProjectRoute()"
        class="project-card_link"
        [attr.aria-label]="('projects.viewProject' | translate) + ': ' + project().name"
      >
        <div class="project-card_content">
          <div class="project-card_header">
            <div class="project-card_icon-wrapper">
              <div class="project-card_icon" [style.background-color]="projectColor()">
                <lib-icon name="folder" size="md" class="project-card_icon-svg" />
              </div>
              <div class="project-card_title-group">
                <h3 class="project-card_name">{{ project().name }}</h3>
                @if (project().lastUpdated) {
                  <p class="project-card_updated">{{ project().lastUpdated }}</p>
                }
              </div>
            </div>
            <lib-button
              variant="ghost"
              size="sm"
              [iconOnly]="true"
              leftIcon="ellipsis"
              class="project-card_more-button"
              (clicked)="handleSettings()"
            >
            </lib-button>
          </div>

          @if (project().description) {
            <p class="project-card_description">{{ project().description }}</p>
          }

          <!-- Progress Bar -->
          @if (project().taskCount !== undefined && project().taskCount! > 0) {
            <div class="project-card_progress">
              <div class="project-card_progress-header">
                <span class="project-card_progress-label">Progress</span>
                <span class="project-card_progress-count">
                  {{ project().completedTasks || 0 }}/{{ project().taskCount }} tasks
                </span>
              </div>
              <div class="project-card_progress-bar">
                <div
                  class="project-card_progress-fill"
                  [style.width.%]="progressPercentage()"
                  [style.background-color]="projectColor()"
                ></div>
              </div>
            </div>
          }

          <!-- Footer -->
          <div class="project-card_footer">
            <div class="project-card_members">
              @for (member of members(); track member.id) {
                <lib-avatar
                  [avatarUrl]="member.avatar_url || undefined"
                  [name]="member.name"
                  [initials]="getInitials(member.name)"
                  size="sm"
                  class="project-card_member-avatar"
                />
              }
              @if (members().length > 4) {
                <div class="project-card_member-more">+{{ members().length - 4 }}</div>
              }
            </div>
            @if (project().status) {
              <lib-badge [variant]="statusVariant()" size="sm">
                {{ statusLabel() }}
              </lib-badge>
            }
          </div>
        </div>
      </a>
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
        @apply border-border;
        @apply bg-card;
        @apply transition-all;
        @apply hover:shadow-lg;
        @apply hover:scale-[1.02];
        @apply cursor-pointer;
        min-height: 200px;
      }

      .project-card_link {
        @apply flex-1;
        @apply p-6;
        text-decoration: none;
        color: inherit;
        @apply cursor-pointer;
      }

      .project-card_content {
        @apply flex flex-col;
        @apply gap-4;
        @apply h-full;
      }

      .project-card_header {
        @apply flex items-start justify-between;
        @apply mb-4;
      }

      .project-card_icon-wrapper {
        @apply flex items-center gap-3;
        @apply flex-1;
      }

      .project-card_icon {
        @apply h-10 w-10 rounded-lg flex items-center justify-center;
        @apply flex-shrink-0;
      }

      .project-card_icon-svg {
        @apply text-white;
      }

      .project-card_title-group {
        @apply flex-1 min-w-0;
      }

      .project-card_name {
        @apply text-lg font-semibold text-foreground;
        @apply hover:text-primary transition-colors;
        @apply truncate;
        margin: 0;
      }

      .project-card_updated {
        @apply text-xs text-muted-foreground;
        margin: 0;
      }

      .project-card_more-button {
        @apply h-8 w-8 opacity-0;
      }

      .project-card:hover .project-card_more-button {
        @apply opacity-100;
      }

      .project-card_description {
        @apply text-sm text-muted-foreground;
        @apply line-clamp-2;
        margin: 0;
      }

      .project-card_progress {
        @apply mb-4;
      }

      .project-card_progress-header {
        @apply flex items-center justify-between text-sm mb-2;
      }

      .project-card_progress-label {
        @apply text-muted-foreground;
      }

      .project-card_progress-count {
        @apply font-medium;
      }

      .project-card_progress-bar {
        @apply h-2 bg-muted rounded-full overflow-hidden;
      }

      .project-card_progress-fill {
        @apply h-full transition-all;
      }

      .project-card_footer {
        @apply flex items-center justify-between;
        @apply mt-auto;
      }

      .project-card_members {
        @apply flex items-center -space-x-2;
      }

      .project-card_member-avatar {
        @apply border-2 border-background;
      }

      .project-card_member-more {
        @apply h-7 w-7 rounded-full bg-muted border-2 border-background flex items-center justify-center;
        @apply text-xs font-medium;
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

  readonly projectColor = computed(() => {
    // Mock data - return project color or default
    return this.project().color || '#3b82f6'; // blue-500 default
  });

  readonly progressPercentage = computed(() => {
    const total = this.project().taskCount || 0;
    if (total === 0) return 0;
    const completed = this.project().completedTasks || 0;
    return Math.round((completed / total) * 100);
  });

  readonly members = computed(() => {
    // Mock data - return project members or empty array
    return this.project().members || [];
  });

  readonly statusVariant = computed<'default' | 'success' | 'warning' | 'danger'>(() => {
    const status = this.project().status;
    if (status === 'active') return 'success';
    if (status === 'completed') return 'default';
    if (status === 'on-hold') return 'warning';
    return 'default';
  });

  readonly statusLabel = computed(() => {
    const status = this.project().status;
    const labels: Record<string, string> = {
      active: 'Active',
      completed: 'Completed',
      'on-hold': 'On Hold',
    };
    return labels[status || ''] || '';
  });

  getProjectRoute(): string[] {
    const orgId = this.organizationService.currentOrganization()?.id;
    const projectId = this.project().id;
    if (orgId) {
      return this.navigationService.getProjectRoute(orgId, projectId);
    }
    // Fallback if no org (shouldn't happen)
    return ['/app/organizations'];
  }

  getInitials(name: string): string {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  }

  handleSettings(): void {
    this.onSettings.emit(this.project());
  }
}
