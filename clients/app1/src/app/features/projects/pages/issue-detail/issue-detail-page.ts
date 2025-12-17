import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  signal,
  ViewContainerRef,
  effect,
} from '@angular/core';
import {
  Button,
  LoadingState,
  ErrorState,
  Modal,
  TextEditor,
  Icon,
  Select,
  Avatar,
  Badge,
  IconName,
} from 'shared-ui';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { IssueService } from '../../../../application/services/issue.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import { IssueTypeBadge } from '../../components/issue-type-badge/issue-type-badge';
import { IssueStatusBadge } from '../../components/issue-status-badge/issue-status-badge';
import { IssuePriorityIndicator } from '../../components/issue-priority-indicator/issue-priority-indicator';
import { CommentList } from '../../components/comment-list/comment-list';
import { AttachmentList } from '../../components/attachment-list/attachment-list';
import { IssueActivityList } from '../../components/issue-activity-list/issue-activity-list';
import { PageBody } from '../../../../shared/layout/page-body/page-body';
import { PageContent } from '../../../../shared/layout/page-content/page-content';

// Placeholder interfaces for future features
interface Subtask {
  id: string;
  title: string;
  completed: boolean;
}

interface LinkedIssue {
  id: string;
  key: string;
  title: string;
  status: string;
  type: 'blocks' | 'linked';
}

@Component({
  selector: 'app-issue-detail-page',
  imports: [
    Button,
    LoadingState,
    ErrorState,
    IssueTypeBadge,
    IssueStatusBadge,
    IssuePriorityIndicator,
    CommentList,
    AttachmentList,
    IssueActivityList,
    TextEditor,
    Icon,
    Select,
    Avatar,
    Badge,
    TranslatePipe,
    PageBody,
    PageContent,
  ],
  template: `
    <app-page-body>
      <app-page-content>
        @if (issueService.hasIssueError()) {
          <lib-error-state
            [title]="'issueDetail.failedToLoad' | translate"
            [message]="errorMessage()"
            [retryLabel]="'common.retry' | translate"
            (onRetry)="handleRetry()"
          />
        } @else if (!issue()) {
          <lib-error-state
            [title]="'issueDetail.notFound' | translate"
            [message]="'issueDetail.notFoundDescription' | translate"
            [showRetry]="false"
          />
        } @else {
          <div class="issue-detail-page_container">
            <!-- Main Content -->
            <div class="issue-detail-page_main">
              <div class="issue-detail-page_content">
                <!-- Top Actions -->
                <div class="issue-detail-page_actions">
                  <lib-button variant="ghost" leftIcon="link-2" (clicked)="handleLink()" />
                  <lib-button variant="ghost" leftIcon="share-2" (clicked)="handleShare()" />
                  <lib-button
                    variant="ghost"
                    leftIcon="ellipsis-vertical"
                    (clicked)="handleMore()"
                  />
                </div>

                <!-- Title -->
                <h1 class="issue-detail-page_title">{{ issue()?.title }}</h1>

                <!-- Status & Assignees -->
                <div class="issue-detail-page_status-section">
                  <lib-select
                    [options]="statusOptions()"
                    [(model)]="statusModel"
                    [class]="
                      'issue-detail-page_status-select issue-detail-page_status-select--' +
                      issue()!.status
                    "
                  />

                  <div class="issue-detail-page_assignees">
                    <div class="issue-detail-page_assignees-list">
                      @if (issue()?.assignee) {
                        <lib-avatar
                          [avatarUrl]="issue()!.assignee!.avatar_url || undefined"
                          [name]="issue()!.assignee!.name"
                          [initials]="getInitials(issue()!.assignee!.name)"
                          size="sm"
                        />
                      }
                    </div>
                    <lib-button
                      variant="ghost"
                      leftIcon="plus"
                      class="issue-detail-page_assignee-add"
                    />
                  </div>
                </div>

                <!-- Description -->
                <div class="issue-detail-page_section">
                  @if (issue()?.description) {
                    <div class="issue-detail-page_description">
                      <lib-text-editor
                        [initialValue]="issue()!.description"
                        [readOnly]="true"
                        [showToolbar]="false"
                        class="issue-detail-page_description-editor"
                      />
                    </div>
                  } @else {
                    <p class="issue-detail-page_no-description">
                      {{ 'issueDetail.noDescription' | translate }}
                    </p>
                  }
                </div>

                <!-- Subtasks -->
                @if (subtasks().length > 0) {
                  <div class="issue-detail-page_section">
                    <div class="issue-detail-page_section-header">
                      <h2 class="issue-detail-page_section-title">Subtasks</h2>
                      <lib-badge variant="default" size="sm">
                        {{ completedSubtasksCount() }}/{{ subtasks().length }} Done
                      </lib-badge>
                    </div>
                    <div class="issue-detail-page_subtasks">
                      @for (subtask of subtasks(); track subtask.id) {
                        <div class="issue-detail-page_subtask">
                          <input
                            type="checkbox"
                            [checked]="subtask.completed"
                            (change)="handleSubtaskToggle(subtask.id)"
                            class="issue-detail-page_subtask-checkbox"
                          />
                          <span
                            class="issue-detail-page_subtask-title"
                            [class.issue-detail-page_subtask-title--completed]="subtask.completed"
                          >
                            {{ subtask.title }}
                          </span>
                        </div>
                      }
                    </div>
                  </div>
                }

                <!-- Separator -->
                <div class="issue-detail-page_separator"></div>

                <!-- Comments -->
                <div class="issue-detail-page_section">
                  <app-comment-list [issueId]="issueId()" />
                </div>

                <!-- Attachments -->
                <div class="issue-detail-page_section">
                  <app-attachment-list [issueId]="issueId()" />
                </div>

                <!-- Activity -->
                <div class="issue-detail-page_section">
                  <h2 class="issue-detail-page_section-title">
                    {{ 'issueDetail.activity' | translate }}
                  </h2>
                  <app-issue-activity-list [issueId]="issueId()" />
                </div>
              </div>
            </div>

            <!-- Right Sidebar -->
            <div class="issue-detail-page_sidebar">
              <div class="issue-detail-page_sidebar-scroll">
                <div class="issue-detail-page_sidebar-content">
                  <!-- Mark Complete Button -->
                  @if (issue()!.status !== 'done') {
                    <lib-button
                      variant="primary"
                      size="md"
                      [fullWidth]="true"
                      leftIcon="check"
                      class="issue-detail-page_complete-button"
                      (clicked)="handleMarkComplete()"
                    >
                      Mark Complete
                    </lib-button>
                  }

                  <!-- Details -->
                  <div class="issue-detail-page_sidebar-section">
                    <h3 class="issue-detail-page_sidebar-title">Details</h3>

                    <div class="issue-detail-page_sidebar-details">
                      <div class="issue-detail-page_sidebar-detail-item">
                        <span class="issue-detail-page_sidebar-detail-label">Assignee</span>
                        <div class="issue-detail-page_sidebar-detail-value">
                          @if (issue()?.assignee) {
                            <span>{{ issue()!.assignee!.name }}</span>
                            <lib-avatar
                              [avatarUrl]="issue()!.assignee!.avatar_url || undefined"
                              [name]="issue()!.assignee!.name"
                              [initials]="getInitials(issue()!.assignee!.name)"
                              size="sm"
                            />
                          } @else {
                            <span class="issue-detail-page_unassigned">{{
                              'issues.unassigned' | translate
                            }}</span>
                          }
                        </div>
                      </div>

                      <div class="issue-detail-page_sidebar-detail-item">
                        <span class="issue-detail-page_sidebar-detail-label">Priority</span>
                        <div class="issue-detail-page_sidebar-detail-value">
                          <lib-icon
                            [name]="getPriorityIcon(issue()!.priority)"
                            size="xs"
                            [class]="
                              'issue-detail-page_priority-icon issue-detail-page_priority-icon--' +
                              issue()!.priority
                            "
                          />
                          <span>{{ getPriorityLabel(issue()!.priority) }}</span>
                        </div>
                      </div>

                      @if (issue()?.due_date) {
                        <div class="issue-detail-page_sidebar-detail-item">
                          <span class="issue-detail-page_sidebar-detail-label">Due Date</span>
                          <span
                            class="issue-detail-page_sidebar-detail-value issue-detail-page_due-date"
                          >
                            {{ formatDate(issue()!.due_date!) }}
                          </span>
                        </div>
                      }

                      @if (issue()?.story_points) {
                        <div class="issue-detail-page_sidebar-detail-item">
                          <span class="issue-detail-page_sidebar-detail-label">Estimate</span>
                          <span class="issue-detail-page_sidebar-detail-value"
                            >{{ issue()!.story_points }} pts</span
                          >
                        </div>
                      }
                    </div>
                  </div>

                  <div class="issue-detail-page_separator"></div>

                  <!-- Tags -->
                  <div class="issue-detail-page_sidebar-section">
                    <div class="issue-detail-page_sidebar-section-header">
                      <h3 class="issue-detail-page_sidebar-title">Tags</h3>
                      <lib-button
                        variant="ghost"
                        leftIcon="plus"
                        class="issue-detail-page_sidebar-action"
                      />
                    </div>
                    <div class="issue-detail-page_tags">
                      @for (tag of tags(); track tag) {
                        <lib-badge variant="default" size="sm">{{ tag }}</lib-badge>
                      }
                    </div>
                  </div>

                  <div class="issue-detail-page_separator"></div>

                  <!-- Linked Issues -->
                  <div class="issue-detail-page_sidebar-section">
                    <div class="issue-detail-page_sidebar-section-header">
                      <h3 class="issue-detail-page_sidebar-title">Linked Issues</h3>
                      <lib-button
                        variant="ghost"
                        leftIcon="plus"
                        class="issue-detail-page_sidebar-action"
                      />
                    </div>
                    <div class="issue-detail-page_linked-issues">
                      @for (linkedIssue of linkedIssues(); track linkedIssue.id) {
                        <div class="issue-detail-page_linked-issue-card">
                          <div class="issue-detail-page_linked-issue">
                            <div class="issue-detail-page_linked-issue-content">
                              <div class="issue-detail-page_linked-issue-header">
                                @if (linkedIssue.type === 'blocks') {
                                  <span class="issue-detail-page_linked-issue-block">🔴</span>
                                } @else {
                                  <lib-icon
                                    name="link-2"
                                    size="xs"
                                    class="issue-detail-page_linked-issue-link-icon"
                                  />
                                }
                                <span class="issue-detail-page_linked-issue-key">{{
                                  linkedIssue.key
                                }}</span>
                              </div>
                              <p class="issue-detail-page_linked-issue-title">
                                {{ linkedIssue.title }}
                              </p>
                              <lib-badge
                                variant="default"
                                size="sm"
                                [class.issue-detail-page_linked-issue-status--done]="
                                  linkedIssue.status === 'Done'
                                "
                              >
                                {{ linkedIssue.status }}
                              </lib-badge>
                            </div>
                            <lib-icon
                              name="external-link"
                              size="xs"
                              class="issue-detail-page_linked-issue-external"
                            />
                          </div>
                        </div>
                      }
                    </div>
                  </div>

                  <!-- Footer metadata -->
                  <div class="issue-detail-page_sidebar-footer">
                    <p class="issue-detail-page_sidebar-footer-text">
                      Created {{ formatDate(issue()!.created_at) }}
                    </p>
                    <p class="issue-detail-page_sidebar-footer-text">
                      Updated {{ formatRelativeTime(issue()!.updated_at) }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        }
      </app-page-content>
    </app-page-body>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .issue-detail-page_container {
        @apply flex w-full;
        @apply min-h-0;
      }

      /* Main Content */
      .issue-detail-page_main {
        @apply flex-1;
        @apply min-h-0;
        @apply h-full;
        @apply pb-8;
      }

      .issue-detail-page_content {
        @apply max-w-3xl;
        @apply w-full;
      }

      .issue-detail-page_actions {
        @apply flex items-center justify-end gap-2 mb-6;
      }

      .issue-detail-page_title {
        @apply text-3xl font-bold text-foreground;
        margin: 0 0 1.5rem 0;
      }

      .issue-detail-page_status-section {
        @apply flex items-center gap-4 mb-8;
      }

      .issue-detail-page_status-select {
        width: 140px;
        @apply flex-shrink-0;
      }

      .issue-detail-page_status-select ::ng-deep .select-trigger {
        @apply h-10;
        @apply flex items-center;
      }

      .issue-detail-page_status-select--todo ::ng-deep .select-trigger {
        @apply bg-status-todo/10 text-status-todo border-status-todo;
      }

      .issue-detail-page_status-select--todo ::ng-deep .select-trigger:hover:not(:disabled) {
        @apply border-status-todo;
      }

      .issue-detail-page_status-select--in_progress ::ng-deep .select-trigger {
        @apply bg-status-in-progress/10 text-status-in-progress border-status-in-progress;
      }

      .issue-detail-page_status-select--in_progress ::ng-deep .select-trigger:hover:not(:disabled) {
        @apply border-status-in-progress;
      }

      .issue-detail-page_status-select--done ::ng-deep .select-trigger {
        @apply bg-status-done/10 text-status-done border-status-done;
      }

      .issue-detail-page_status-select--done ::ng-deep .select-trigger:hover:not(:disabled) {
        @apply border-status-done;
      }

      .issue-detail-page_status-select--cancelled ::ng-deep .select-trigger {
        @apply bg-status-cancelled/10 text-status-cancelled border-status-cancelled;
      }

      .issue-detail-page_status-select--cancelled ::ng-deep .select-trigger:hover:not(:disabled) {
        @apply border-status-cancelled;
      }

      .issue-detail-page_assignees {
        @apply flex items-center gap-2;
      }

      .issue-detail-page_assignees-list {
        @apply flex -space-x-2;
        @apply items-center;
      }

      .issue-detail-page_assignee-add {
        @apply h-10 w-10 rounded-full;
        @apply flex items-center justify-center;
      }

      .issue-detail-page_section {
        @apply mb-8;
      }

      .issue-detail-page_section-header {
        @apply flex items-center justify-between mb-4;
      }

      .issue-detail-page_section-title {
        @apply text-xl font-semibold text-foreground mb-4;
        margin: 0;
      }

      .issue-detail-page_description {
        @apply text-muted-foreground leading-relaxed;
      }

      .issue-detail-page_description-editor {
        @apply border-none;
      }

      .issue-detail-page_description-editor ::ng-deep .text-editor_wrapper {
        @apply border-none;
      }

      .issue-detail-page_no-description {
        @apply text-muted-foreground italic;
        margin: 0;
      }

      .issue-detail-page_subtasks {
        @apply space-y-3;
      }

      .issue-detail-page_subtask {
        @apply flex items-center gap-3 p-3 rounded-lg hover:bg-accent/50 transition-colors;
      }

      .issue-detail-page_subtask-checkbox {
        @apply w-4 h-4 rounded border-border;
      }

      .issue-detail-page_subtask-title {
        @apply text-sm text-foreground;
      }

      .issue-detail-page_subtask-title--completed {
        @apply text-muted-foreground line-through;
      }

      .issue-detail-page_separator {
        @apply h-px bg-border my-8;
      }

      /* Right Sidebar */
      .issue-detail-page_sidebar {
        @apply w-80 border-l border-border bg-card/50 hidden lg:block;
      }

      .issue-detail-page_sidebar-scroll {
        @apply h-full;
      }

      .issue-detail-page_sidebar-content {
        @apply p-6;
      }

      .issue-detail-page_complete-button {
        @apply gap-2 mb-8;
      }

      .issue-detail-page_sidebar-section {
        @apply mb-6;
      }

      .issue-detail-page_sidebar-section-header {
        @apply flex items-baseline justify-end mb-4 w-full;
        gap: 0px;
      }

      .issue-detail-page_sidebar-title {
        @apply text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-6;
        margin: 0 0 1.5rem 0;
      }

      .issue-detail-page_sidebar-section-header .issue-detail-page_sidebar-title {
        @apply mb-0;
        @apply flex-1;
      }

      .issue-detail-page_sidebar-action {
        @apply h-6 w-6;
      }

      .issue-detail-page_sidebar-details {
        @apply space-y-4;
      }

      .issue-detail-page_sidebar-detail-item {
        @apply flex items-center justify-between;
      }

      .issue-detail-page_sidebar-detail-label {
        @apply text-sm text-muted-foreground;
      }

      .issue-detail-page_sidebar-detail-value {
        @apply flex items-center gap-2 text-sm text-foreground;
      }

      .issue-detail-page_unassigned {
        @apply text-muted-foreground;
      }

      .issue-detail-page_priority-icon {
        @apply flex-shrink-0;
      }

      .issue-detail-page_priority-icon--low {
        @apply text-blue-500;
      }

      .issue-detail-page_priority-icon--medium {
        @apply text-yellow-500;
      }

      .issue-detail-page_priority-icon--high {
        @apply text-orange-500;
      }

      .issue-detail-page_priority-icon--critical {
        @apply text-red-500;
      }

      .issue-detail-page_due-date {
        @apply text-red-500;
      }

      .issue-detail-page_tags {
        @apply flex flex-wrap gap-2;
      }

      .issue-detail-page_linked-issues {
        @apply space-y-3;
      }

      .issue-detail-page_linked-issue-card {
        @apply rounded-lg border border-border bg-card p-3 hover:bg-accent/50 cursor-pointer transition-colors;
      }

      .issue-detail-page_linked-issue {
        @apply flex items-start justify-between;
      }

      .issue-detail-page_linked-issue-content {
        @apply flex-1;
      }

      .issue-detail-page_linked-issue-header {
        @apply flex items-center gap-2 mb-1;
      }

      .issue-detail-page_linked-issue-block {
        @apply text-red-500;
      }

      .issue-detail-page_linked-issue-link-icon {
        @apply text-blue-500;
      }

      .issue-detail-page_linked-issue-key {
        @apply text-xs text-muted-foreground font-mono;
      }

      .issue-detail-page_linked-issue-title {
        @apply text-sm text-foreground mb-2;
        margin: 0;
      }

      .issue-detail-page_linked-issue-status--done {
        @apply bg-green-500/20 text-green-500;
      }

      .issue-detail-page_linked-issue-external {
        @apply text-muted-foreground flex-shrink-0;
      }

      .issue-detail-page_sidebar-footer {
        @apply text-xs text-muted-foreground mt-8;
      }

      .issue-detail-page_sidebar-footer-text {
        @apply mb-1;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IssueDetailPage {
  readonly issueService = inject(IssueService);
  readonly navigationService = inject(NavigationService);
  readonly modal = inject(Modal);
  readonly viewContainerRef = inject(ViewContainerRef);
  readonly translateService = inject(TranslateService);

  readonly issueId = computed(() => {
    return this.navigationService.currentIssueId() || '';
  });
  readonly issue = computed(() => this.issueService.currentIssue());

  readonly organizationId = computed(() => {
    return this.navigationService.currentOrganizationId() || '';
  });

  readonly projectId = computed(() => {
    return this.navigationService.currentProjectId() || '';
  });

  readonly errorMessage = computed(() => {
    const error = this.issueService.issueError();
    if (error) {
      return error instanceof Error ? error.message : 'An error occurred while loading the issue.';
    }
    return 'An unknown error occurred.';
  });

  // Placeholder data for future features
  readonly subtasks = signal<Subtask[]>([]);
  readonly tags = signal<string[]>([]);
  readonly linkedIssues = signal<LinkedIssue[]>([]);

  readonly completedSubtasksCount = computed(() => {
    return this.subtasks().filter((s) => s.completed).length;
  });

  readonly statusOptions = computed(() => {
    return [
      { value: 'todo', label: 'To Do' },
      { value: 'in_progress', label: 'In Progress' },
      { value: 'done', label: 'Done' },
      { value: 'cancelled', label: 'Cancelled' },
    ];
  });

  // Status model for two-way binding with select
  readonly statusModel = signal<string | null>(null);

  constructor() {
    // Sync status model with issue status
    effect(() => {
      const currentStatus = this.issue()?.status;
      if (currentStatus) {
        this.statusModel.set(currentStatus);
      }
    });

    // Handle status model changes from select component
    effect(() => {
      const newStatus = this.statusModel();
      const currentIssueStatus = this.issue()?.status;
      // Only update if the status actually changed and it's different from current issue status
      if (newStatus && newStatus !== currentIssueStatus) {
        this.handleStatusChange(newStatus);
      }
    });
  }

  handleLink(): void {
    // TODO: Implement link functionality
  }

  handleShare(): void {
    // TODO: Implement share functionality
  }

  handleMore(): void {
    // TODO: Implement more menu
  }

  handleStatusChange(status: string | null): void {
    if (!status) return;
    const id = this.issueId();
    if (id && status !== this.issue()?.status) {
      this.issueService.updateIssue(id, { status: status as any });
    }
  }

  handleSubtaskToggle(subtaskId: string): void {
    // TODO: Implement subtask toggle
  }

  handleMarkComplete(): void {
    const id = this.issueId();
    if (id) {
      this.issueService.updateIssue(id, { status: 'done' });
    }
  }

  getInitials(name: string): string {
    const words = name.trim().split(/\s+/);
    if (words.length >= 2) {
      return (words[0][0] + words[words.length - 1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  }

  getPriorityIcon(priority: string): IconName {
    switch (priority) {
      case 'low':
        return 'arrow-down';
      case 'medium':
        return 'minus';
      case 'high':
        return 'arrow-up';
      case 'critical':
        return 'flag';
      default:
        return 'minus';
    }
  }

  getPriorityLabel(priority: string): string {
    return this.translateService.instant(`issues.priority.${priority}`);
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  }

  formatRelativeTime(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) {
      return `${diffInSeconds}s ago`;
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return `${minutes}m ago`;
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return `${hours}h ago`;
    } else {
      const days = Math.floor(diffInSeconds / 86400);
      return `${days}d ago`;
    }
  }

  handleRetry(): void {
    const id = this.issueId();
    if (id) {
      this.issueService.fetchIssue(id);
    }
  }
}
