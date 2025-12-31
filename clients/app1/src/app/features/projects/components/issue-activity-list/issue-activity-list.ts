import { Component, ChangeDetectionStrategy, computed, inject, input, effect } from '@angular/core';
import { LoadingState, ErrorState, EmptyState, Button, Icon, IconName } from 'shared-ui';
import { IssueActivityService } from '../../../../application/services/issue-activity.service';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-issue-activity-list',
  standalone: true,
  imports: [LoadingState, ErrorState, EmptyState, Button, Icon, TranslatePipe],
  template: `
    <div class="activity-list">
      @if (activityService.isLoading()) {
        <lib-loading-state [message]="'activity.loading' | translate" />
      } @else if (activityService.hasError()) {
        <lib-error-state
          [title]="'activity.failedToLoad' | translate"
          [message]="errorMessage()"
          [retryLabel]="'common.retry' | translate"
          (onRetry)="handleRetry()"
        />
      } @else if (activities().length === 0) {
        <lib-empty-state
          [title]="'activity.noActivity' | translate"
          [message]="'activity.noActivityDescription' | translate"
          icon="clock"
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
                        activity.old_value || ('activity.empty' | translate)
                      }}</span>
                      <lib-icon name="arrow-right" [size]="'xs'" />
                      <span class="activity-list_item-new-value">{{
                        activity.new_value || ('activity.empty' | translate)
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
              {{ 'common.previous' | translate }}
            </lib-button>
            <span class="activity-list_pagination-info">
              {{ 'common.page' | translate }} {{ currentPage() }} {{ 'common.of' | translate }}
              {{ totalPages() }}
            </span>
            <lib-button
              variant="ghost"
              size="sm"
              [disabled]="currentPage() === totalPages()"
              (clicked)="handleNextPage()"
            >
              {{ 'common.next' | translate }}
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
        @apply border-border;
        @apply bg-muted;
      }

      .activity-list_item-icon {
        @apply flex-shrink-0;
        @apply w-8 h-8;
        @apply flex items-center justify-center;
        @apply rounded-full;
        @apply bg-background;
        @apply text-muted-foreground;
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
        @apply text-foreground;
      }

      .activity-list_item-action {
        @apply text-muted-foreground;
      }

      .activity-list_item-time {
        @apply text-xs;
        @apply text-muted-foreground;
        @apply ml-auto;
      }

      .activity-list_item-change {
        @apply flex items-center;
        @apply gap-2;
        @apply pt-2;
        @apply border-t;
        @apply border-border;
        @apply flex-wrap;
      }

      .activity-list_item-field {
        @apply text-sm font-medium;
        @apply text-muted-foreground;
      }

      .activity-list_item-value-change {
        @apply flex items-center;
        @apply gap-2;
        @apply text-sm;
      }

      .activity-list_item-old-value {
        @apply px-2 py-1;
        @apply rounded;
        @apply bg-destructive/10;
        @apply text-destructive;
        @apply line-through;
      }

      .activity-list_item-new-value {
        @apply px-2 py-1;
        @apply rounded;
        @apply bg-success/10;
        @apply text-success;
      }

      .activity-list_pagination {
        @apply flex items-center justify-center;
        @apply gap-4;
        @apply pt-4;
        @apply border-t;
        @apply border-border;
      }

      .activity-list_pagination-info {
        @apply text-sm;
        @apply text-muted-foreground;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IssueActivityList {
  readonly activityService = inject(IssueActivityService);
  private readonly translateService = inject(TranslateService);

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
      return error instanceof Error
        ? error.message
        : this.translateService.instant('activity.loadError');
    }
    return this.translateService.instant('common.unknownError');
  });

  getUserName(activity: { user_name?: string; user_email?: string }): string {
    return (
      activity.user_name || activity.user_email || this.translateService.instant('activity.system')
    );
  }

  getActivityIcon(action: string): IconName {
    switch (action) {
      case 'created':
        return 'plus';
      case 'updated':
        return 'pen';
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
        return this.translateService.instant('activity.createdIssue');
      case 'updated':
        if (activity.field_name) {
          return this.translateService.instant('activity.updatedField', {
            field: this.formatFieldName(activity.field_name),
          });
        }
        return this.translateService.instant('activity.updatedIssue');
      case 'deleted':
        return this.translateService.instant('activity.deletedIssue');
      case 'status_changed':
        return this.translateService.instant('activity.changedStatus');
      case 'assigned':
        return this.translateService.instant('activity.assignedIssue');
      default:
        return (
          this.translateService.instant(`activity.${activity.action.replace(/_/g, '')}`) ||
          activity.action.replace(/_/g, ' ')
        );
    }
  }

  formatFieldName(fieldName: string): string {
    // Use translation if available, otherwise convert snake_case to Title Case
    const translationKey = `activity.field.${fieldName}`;
    const translated = this.translateService.instant(translationKey);
    if (translated !== translationKey) {
      return translated;
    }
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
      return this.translateService.instant('activity.justNow');
    } else if (diffMins < 60) {
      return this.translateService.instant('activity.minutesAgo', { count: diffMins });
    } else if (diffHours < 24) {
      return this.translateService.instant('activity.hoursAgo', { count: diffHours });
    } else if (diffDays < 7) {
      return this.translateService.instant('activity.daysAgo', { count: diffDays });
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
