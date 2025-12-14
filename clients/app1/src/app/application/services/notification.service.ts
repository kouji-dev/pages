import { Injectable, inject, computed, signal, effect, OnDestroy } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { httpResource } from '@angular/common/http';
import { firstValueFrom, interval, Subscription } from 'rxjs';
import { environment } from '../../../environments/environment';

export type NotificationType =
  | 'issue_assigned'
  | 'issue_mentioned'
  | 'issue_commented'
  | 'issue_status_changed'
  | 'issue_priority_changed'
  | 'issue_due_date_changed'
  | 'page_mentioned'
  | 'page_commented'
  | 'organization_invitation'
  | 'project_invitation'
  | 'generic';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  content: string | null;
  entityType: string | null;
  entityId: string | null;
  read: boolean;
  createdAt: string;
}

export interface NotificationListItemResponse {
  id: string;
  type: NotificationType;
  title: string;
  content: string | null;
  entity_type: string | null;
  entity_id: string | null;
  read: boolean;
  created_at: string;
}

export interface NotificationListResponse {
  notifications: NotificationListItemResponse[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface UnreadCountResponse {
  unread_count: number;
}

export interface MarkAsReadResponse {
  id: string;
  read: boolean;
}

export interface MarkAllAsReadResponse {
  marked_count: number;
}

export interface NotificationFilters {
  page?: number;
  limit?: number;
  read?: boolean | null;
}

@Injectable({
  providedIn: 'root',
})
export class NotificationService implements OnDestroy {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/notifications`;

  // Polling interval in milliseconds (30 seconds)
  private readonly POLL_INTERVAL = 30000;
  private pollingSubscription?: Subscription;

  // Filters signal
  readonly filters = signal<NotificationFilters>({
    page: 1,
    limit: 20,
    read: null, // null = all, true = read only, false = unread only
  });

  // Notifications list resource using httpResource
  readonly notifications = httpResource<NotificationListResponse>(() => {
    const filters = this.filters();
    const params = new HttpParams()
      .set('page', (filters.page || 1).toString())
      .set('limit', (filters.limit || 20).toString());

    if (filters.read !== null && filters.read !== undefined) {
      params.set('read', filters.read.toString());
    }

    return `${this.apiUrl}?${params.toString()}`;
  });

  // Unread count resource using httpResource
  readonly unreadCount = httpResource<UnreadCountResponse>(() => `${this.apiUrl}/unread-count`);

  // Public accessors
  readonly notificationsList = computed(() => {
    const value = this.notifications.value();
    if (!value) return [];
    return value.notifications.map((n) => this.mapToNotification(n));
  });

  readonly totalNotifications = computed(() => {
    const value = this.notifications.value();
    return value?.total || 0;
  });

  readonly currentPage = computed(() => {
    const value = this.notifications.value();
    return value?.page || 1;
  });

  readonly totalPages = computed(() => {
    const value = this.notifications.value();
    if (!value) return 0;
    return Math.ceil(value.total / value.limit);
  });

  readonly unreadCountValue = computed(() => {
    const value = this.unreadCount.value();
    return value?.unread_count || 0;
  });

  readonly isLoading = computed(() => this.notifications.isLoading());
  readonly isLoadingCount = computed(() => this.unreadCount.isLoading());
  readonly error = computed(() => this.notifications.error());
  readonly hasError = computed(() => this.notifications.error() !== undefined);

  constructor() {
    // Start polling for unread count when service is created
    this.startPolling();
  }

  ngOnDestroy(): void {
    this.stopPolling();
  }

  /**
   * Start polling for unread count
   */
  startPolling(): void {
    if (this.pollingSubscription) {
      return; // Already polling
    }

    // Initial fetch
    this.unreadCount.reload();

    // Poll every POLL_INTERVAL milliseconds
    this.pollingSubscription = interval(this.POLL_INTERVAL).subscribe(() => {
      this.unreadCount.reload();
    });
  }

  /**
   * Stop polling for unread count
   */
  stopPolling(): void {
    if (this.pollingSubscription) {
      this.pollingSubscription.unsubscribe();
      this.pollingSubscription = undefined;
    }
  }

  /**
   * Map backend response (snake_case) to frontend model (camelCase)
   */
  private mapToNotification(response: NotificationListItemResponse): Notification {
    return {
      id: response.id,
      type: response.type,
      title: response.title,
      content: response.content,
      entityType: response.entity_type,
      entityId: response.entity_id,
      read: response.read,
      createdAt: response.created_at,
    };
  }

  /**
   * Set filters and trigger reload
   */
  setFilters(filters: Partial<NotificationFilters>): void {
    this.filters.update((current) => ({ ...current, ...filters }));
    // Resource will reload automatically when filters change
  }

  /**
   * Reload notifications list
   */
  reload(): void {
    this.notifications.reload();
  }

  /**
   * Reload unread count
   */
  reloadCount(): void {
    this.unreadCount.reload();
  }

  /**
   * Mark notification as read
   */
  async markAsRead(notificationId: string): Promise<void> {
    try {
      await firstValueFrom(
        this.http.put<MarkAsReadResponse>(`${this.apiUrl}/${notificationId}/read`, {}),
      );
      // Reload notifications and count
      this.notifications.reload();
      this.unreadCount.reload();
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
      throw error;
    }
  }

  /**
   * Mark all notifications as read
   */
  async markAllAsRead(): Promise<void> {
    try {
      await firstValueFrom(this.http.put<MarkAllAsReadResponse>(`${this.apiUrl}/read-all`, {}));
      // Reload notifications and count
      this.notifications.reload();
      this.unreadCount.reload();
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
      throw error;
    }
  }
}
