import { Component, ChangeDetectionStrategy, computed, inject, input, effect } from '@angular/core';
import { LoadingState, ErrorState, EmptyState, Button, Icon } from 'shared-ui';
import { IssueActivityService } from '../../application/services/issue-activity.service';

@Component({
  selector: 'app-issue-activity-list',
  standalone: true,
  imports: [LoadingState, ErrorState, EmptyState, Button, Icon],
  template: `
    <div class="activity-list">
      @if (activityService.isLoading()) {
        <lib-loading-state message="Loading activity..." />
      } @else if (activityService.hasError()) {
        <lib-error-state
          title="Failed to Load Activity"
          [message]="errorMessage()"
          [retryLabel]="'Retry'"
          (onRetry)="handleRetry()"
        />
      } @else if (activities().length === 0) {
        <lib-empty-state
          title="No activity yet"
          message="Activity logs will appear here when changes are made to this issue."
          icon="clock"
          [showAction]="false"
        />
      } @else {
        <div class="activity-list_items">
          @for (activity of activities(); track activity.id) {
            <div class="activity-list_item">
              <div class="activity-list_item-icon">
                <lib-icon [name]="getActivityIcon(activity.action)" [size]="'sm'" />
              </div>
              <div class="activity-list_item-content">
                <div class="activity-list_item-header">
                  <span class="activity-list_item-user">{{ getUserName(activity) }}</span>
                  <span class="activity-list_item-action">{{
                    getActivityDescription(activity)
                  }}</span>
                  <span class="activity-list_item-time">{{ formatTime(activity.created_at) }}</span>
                </div>
                @if (
                  activity.field_name && activity.old_value !== null && activity.new_value !== null
                ) {
                  <div class="activity-list_item-change">
                    <span class="activity-list_item-field">{{
                      formatFieldName(activity.field_name)
                    }}</span>
                    <span class="activity-list_item-value-change">
                      <span class="activity-list_item-old-value">{{
                        activity.old_value || 'empty'
                      }}</span>
                      <lib-icon name="arrow-right" [size]="'xs'" />
                      <span class="activity-list_item-new-value">{{
                        activity.new_value || 'empty'
                      }}</span>
                    </span>
                  </div>
                }
              </div>
            </div>
          }
        </div>

        @if (totalPages() > 1) {
          <div class="activity-list_pagination">
            <lib-button
              variant="ghost"
              size="sm"
              [disabled]="currentPage() === 1"
              (clicked)="handlePreviousPage()"
            >
              Previous
            </lib-button>
            <span class="activity-list_pagination-info">
              Page {{ currentPage() }} of {{ totalPages() }}
            </span>
            <lib-button
              variant="ghost"
              size="sm"
              [disabled]="currentPage() === totalPages()"
              (clicked)="handleNextPage()"
            >
              Next
            </lib-button>
          </div>
        }
      }
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .activity-list {
        @apply flex flex-col;
        @apply gap-4;
      }

      .activity-list_items {
        @apply flex flex-col;
        @apply gap-4;
      }

      .activity-list_item {
        @apply flex items-start;
        @apply gap-3;
        @apply p-4;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-secondary;
      }

      .activity-list_item-icon {
        @apply flex-shrink-0;
        @apply w-8 h-8;
        @apply flex items-center justify-center;
        @apply rounded-full;
        @apply bg-bg-primary;
        @apply text-text-secondary;
      }

      .activity-list_item-content {
        @apply flex-1;
        @apply flex flex-col;
        @apply gap-2;
      }

      .activity-list_item-header {
        @apply flex items-center;
        @apply gap-2;
        @apply flex-wrap;
      }

      .activity-list_item-user {
        @apply font-semibold;
        @apply text-text-primary;
      }

      .activity-list_item-action {
        @apply text-text-secondary;
      }

      .activity-list_item-time {
        @apply text-xs;
        @apply text-text-secondary;
        @apply ml-auto;
      }

      .activity-list_item-change {
        @apply flex items-center;
        @apply gap-2;
        @apply pt-2;
        @apply border-t;
        @apply border-border-default;
        @apply flex-wrap;
      }

      .activity-list_item-field {
        @apply text-sm font-medium;
        @apply text-text-secondary;
      }

      .activity-list_item-value-change {
        @apply flex items-center;
        @apply gap-2;
        @apply text-sm;
      }

      .activity-list_item-old-value {
        @apply px-2 py-1;
        @apply rounded;
        @apply bg-error-50;
        @apply text-error-800;
        @apply line-through;
      }

      .activity-list_item-new-value {
        @apply px-2 py-1;
        @apply rounded;
        @apply bg-success-50;
        @apply text-success-800;
      }

      .activity-list_pagination {
        @apply flex items-center justify-center;
        @apply gap-4;
        @apply pt-4;
        @apply border-t;
        @apply border-border-default;
      }

      .activity-list_pagination-info {
        @apply text-sm;
        @apply text-text-secondary;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IssueActivityList {
  readonly activityService = inject(IssueActivityService);

  readonly issueId = input.required<string>();

  readonly activities = computed(() => this.activityService.activities());
  readonly currentPage = computed(() => this.activityService.currentPageNumber());
  readonly totalPages = computed(() => this.activityService.totalPages());

  // Load activities when issueId changes
  private readonly loadActivitiesEffect = effect(() => {
    const id = this.issueId();
    if (id) {
      this.activityService.loadActivities(id);
    }
  });

  readonly errorMessage = computed(() => {
    const error = this.activityService.error();
    if (error) {
      return error instanceof Error ? error.message : 'An error occurred while loading activity.';
    }
    return 'An unknown error occurred.';
  });

  getUserName(activity: { user_name?: string; user_email?: string }): string {
    return activity.user_name || activity.user_email || 'System';
  }

  getActivityIcon(action: string): string {
    switch (action) {
      case 'created':
        return 'plus';
      case 'updated':
        return 'edit';
      case 'deleted':
        return 'trash';
      case 'status_changed':
        return 'arrow-right';
      case 'assigned':
        return 'user-plus';
      default:
        return 'circle';
    }
  }

  getActivityDescription(activity: {
    action: string;
    field_name?: string;
    old_value?: string;
    new_value?: string;
  }): string {
    switch (activity.action) {
      case 'created':
        return 'created this issue';
      case 'updated':
        if (activity.field_name) {
          return `updated ${this.formatFieldName(activity.field_name)}`;
        }
        return 'updated this issue';
      case 'deleted':
        return 'deleted this issue';
      case 'status_changed':
        return 'changed status';
      case 'assigned':
        return 'assigned this issue';
      default:
        return activity.action.replace(/_/g, ' ');
    }
  }

  formatFieldName(fieldName: string): string {
    // Convert snake_case to Title Case
    return fieldName
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  formatTime(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) {
      return 'just now';
    } else if (diffMins < 60) {
      return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else if (diffDays < 7) {
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else {
      return date.toLocaleDateString();
    }
  }

  handleRetry(): void {
    const id = this.issueId();
    if (id) {
      this.activityService.reloadActivities();
    }
  }

  handleNextPage(): void {
    this.activityService.nextPage();
  }

  handlePreviousPage(): void {
    this.activityService.previousPage();
  }
}
