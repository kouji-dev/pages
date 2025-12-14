import {
  Component,
  ChangeDetectionStrategy,
  signal,
  inject,
  computed,
  output,
  effect,
} from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Icon, Button } from 'shared-ui';
import { NotificationService, Notification } from '../../application/services/notification.service';
import { NavigationService } from '../../application/services/navigation.service';

@Component({
  selector: 'app-notification-dropdown',
  imports: [CommonModule, Icon, Button],
  template: `
    <div class="notification-dropdown">
      <div class="notification-dropdown_header">
        <h3 class="notification-dropdown_title">Notifications</h3>
        @if (unreadCount() > 0) {
          <lib-button
            variant="ghost"
            size="sm"
            (clicked)="handleMarkAllAsRead()"
            [disabled]="isMarkingAllAsRead()"
          >
            Mark all as read
          </lib-button>
        }
      </div>

      <div class="notification-dropdown_content">
        @if (isLoading()) {
          <div class="notification-dropdown_loading">
            <lib-icon name="loader" size="md" class="notification-dropdown_loading-icon" />
            <span class="notification-dropdown_loading-text">Loading...</span>
          </div>
        } @else if (hasError()) {
          <div class="notification-dropdown_error">
            <lib-icon name="circle-alert" size="md" />
            <span>Failed to load notifications</span>
            <lib-button variant="ghost" size="sm" (clicked)="handleRetry()">Retry</lib-button>
          </div>
        } @else if (notifications().length === 0) {
          <div class="notification-dropdown_empty">
            <lib-icon name="bell" size="md" />
            <span>No notifications</span>
          </div>
        } @else {
          <div class="notification-dropdown_list">
            @for (notification of notifications(); track notification.id) {
              <button
                type="button"
                class="notification-dropdown_item"
                [class.notification-dropdown_item--unread]="!notification.read"
                (click)="handleNotificationClick(notification)"
                [attr.aria-label]="notification.title"
              >
                <div class="notification-dropdown_item-icon">
                  <lib-icon [name]="getNotificationIcon(notification.type)" size="sm" />
                </div>
                <div class="notification-dropdown_item-content">
                  <div class="notification-dropdown_item-title">{{ notification.title }}</div>
                  @if (notification.content) {
                    <div class="notification-dropdown_item-content-text">
                      {{ notification.content }}
                    </div>
                  }
                  <div class="notification-dropdown_item-time">
                    {{ formatTime(notification.createdAt) }}
                  </div>
                </div>
                @if (!notification.read) {
                  <div class="notification-dropdown_item-indicator"></div>
                }
              </button>
            }
          </div>
        }
      </div>

      @if (notifications().length > 0 && totalPages() > 1) {
        <div class="notification-dropdown_footer">
          <lib-button variant="ghost" size="sm" [fullWidth]="true" (clicked)="handleViewAll()">
            View all notifications
          </lib-button>
        </div>
      }
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .notification-dropdown {
        @apply bg-bg-primary;
        @apply border border-border-default;
        @apply rounded-lg;
        @apply shadow-lg;
        @apply w-full;
        min-width: 360px;
        max-width: 420px;
        max-height: 600px;
        @apply flex flex-col;
        @apply overflow-hidden;
      }

      .notification-dropdown_header {
        @apply flex items-center justify-between;
        @apply px-4 py-3;
        @apply border-b border-border-default;
      }

      .notification-dropdown_title {
        @apply text-base font-semibold;
        @apply text-text-primary;
        margin: 0;
      }

      .notification-dropdown_content {
        @apply flex-1;
        @apply overflow-y-auto;
        min-height: 200px;
        max-height: 400px;
      }

      .notification-dropdown_loading,
      .notification-dropdown_error,
      .notification-dropdown_empty {
        @apply flex flex-col items-center justify-center;
        @apply p-8;
        @apply gap-3;
        @apply text-text-secondary;
      }

      .notification-dropdown_loading-icon {
        @apply animate-spin;
      }

      .notification-dropdown_loading-text {
        @apply text-sm;
      }

      .notification-dropdown_error {
        @apply text-error;
      }

      .notification-dropdown_list {
        @apply flex flex-col;
      }

      .notification-dropdown_item {
        @apply flex items-start;
        @apply gap-3;
        @apply px-4 py-3;
        @apply w-full;
        @apply text-left;
        @apply bg-transparent;
        @apply border-none;
        @apply border-b border-border-default;
        @apply cursor-pointer;
        @apply transition-colors;
        @apply hover:bg-bg-hover;
        @apply relative;
      }

      .notification-dropdown_item:last-child {
        @apply border-b-0;
      }

      .notification-dropdown_item--unread {
        @apply bg-bg-secondary;
      }

      .notification-dropdown_item-icon {
        @apply flex-shrink-0;
        @apply mt-0.5;
        @apply text-text-tertiary;
      }

      .notification-dropdown_item-content {
        @apply flex-1;
        @apply min-w-0;
      }

      .notification-dropdown_item-title {
        @apply text-sm font-medium;
        @apply text-text-primary;
        @apply mb-1;
      }

      .notification-dropdown_item-content-text {
        @apply text-xs;
        @apply text-text-secondary;
        @apply line-clamp-2;
        @apply mb-1;
      }

      .notification-dropdown_item-time {
        @apply text-xs;
        @apply text-text-tertiary;
      }

      .notification-dropdown_item-indicator {
        @apply absolute left-0 top-0 bottom-0;
        @apply w-1;
        @apply bg-primary-500;
        @apply rounded-r;
      }

      .notification-dropdown_footer {
        @apply p-3;
        @apply border-t border-border-default;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class NotificationDropdown {
  private readonly router = inject(Router);
  private readonly notificationService = inject(NotificationService);
  private readonly navigationService = inject(NavigationService);

  readonly close = output<void>();

  readonly notifications = this.notificationService.notificationsList;
  readonly unreadCount = this.notificationService.unreadCountValue;
  readonly isLoading = this.notificationService.isLoading;
  readonly hasError = this.notificationService.hasError;
  readonly totalPages = this.notificationService.totalPages;

  readonly isMarkingAllAsRead = signal<boolean>(false);

  constructor() {
    // Load notifications when component is created
    effect(() => {
      this.notificationService.setFilters({ page: 1, limit: 20, read: null });
    });
  }

  /**
   * Get icon name for notification type
   */
  getNotificationIcon(type: string): string {
    const iconMap: Record<string, string> = {
      issue_assigned: 'user-check',
      issue_mentioned: 'at-sign',
      issue_commented: 'message-circle',
      issue_status_changed: 'arrow-right',
      issue_priority_changed: 'flag',
      issue_due_date_changed: 'calendar',
      page_mentioned: 'at-sign',
      page_commented: 'message-circle',
      organization_invitation: 'user-plus',
      project_invitation: 'user-plus',
      generic: 'bell',
    };
    return iconMap[type] || 'bell';
  }

  /**
   * Format time relative to now
   */
  formatTime(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) {
      return 'Just now';
    } else if (diffMins < 60) {
      return `${diffMins}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  }

  /**
   * Handle notification click - navigate and mark as read
   */
  async handleNotificationClick(notification: Notification): Promise<void> {
    // Mark as read if unread
    if (!notification.read) {
      try {
        await this.notificationService.markAsRead(notification.id);
      } catch (error) {
        console.error('Failed to mark notification as read:', error);
      }
    }

    // Navigate to related entity
    if (notification.entityType && notification.entityId) {
      const organizationId = this.navigationService.currentOrganizationId();
      if (!organizationId) return;

      switch (notification.entityType) {
        case 'issue':
          // Need project ID - could be in notification.data or we need to fetch it
          // For now, just navigate to issues list
          this.router.navigate(['/app/organizations', organizationId, 'projects']);
          break;
        case 'page':
          // Need space ID - could be in notification.data or we need to fetch it
          // For now, just navigate to spaces list
          this.router.navigate(['/app/organizations', organizationId, 'spaces']);
          break;
        default:
          // Generic navigation
          break;
      }
    }

    this.close.emit();
  }

  /**
   * Mark all notifications as read
   */
  async handleMarkAllAsRead(): Promise<void> {
    this.isMarkingAllAsRead.set(true);
    try {
      await this.notificationService.markAllAsRead();
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    } finally {
      this.isMarkingAllAsRead.set(false);
    }
  }

  /**
   * Retry loading notifications
   */
  handleRetry(): void {
    this.notificationService.reload();
  }

  /**
   * Navigate to notifications page (if we create one later)
   */
  handleViewAll(): void {
    // TODO: Navigate to notifications page when created
    this.close.emit();
  }
}
