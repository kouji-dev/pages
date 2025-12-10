import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  signal,
  ViewContainerRef,
  effect,
} from '@angular/core';
import { Button, LoadingState, ErrorState, Modal, TextEditor } from 'shared-ui';
import { IssueService } from '../../application/services/issue.service';
import { NavigationService } from '../../application/services/navigation.service';
import { IssueTypeBadge } from '../components/issue-type-badge';
import { IssueStatusBadge } from '../components/issue-status-badge';
import { IssuePriorityIndicator } from '../components/issue-priority-indicator';
import { EditIssueModal } from '../components/edit-issue-modal';
import { CommentList } from '../components/comment-list';
import { AttachmentList } from '../components/attachment-list';

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
    TextEditor,
  ],
  template: `
    <div class="issue-detail-page">
      @if (issueService.isFetchingIssue()) {
        <lib-loading-state message="Loading issue..." />
      } @else if (issueService.hasIssueError()) {
        <lib-error-state
          title="Failed to Load Issue"
          [message]="errorMessage()"
          [retryLabel]="'Retry'"
          (onRetry)="handleRetry()"
        />
      } @else if (!issue()) {
        <lib-error-state
          title="Issue Not Found"
          message="The issue you're looking for doesn't exist or you don't have access to it."
          [showRetry]="false"
        />
      } @else {
        <div class="issue-detail-page_header">
          <div class="issue-detail-page_header-content">
            <div class="issue-detail-page_header-main">
              <div class="issue-detail-page_header-info">
                <div class="issue-detail-page_key">{{ issue()?.key }}</div>
                <h1 class="issue-detail-page_title">{{ issue()?.title }}</h1>
                <div class="issue-detail-page_badges">
                  <app-issue-type-badge [type]="issue()!.type" />
                  <app-issue-status-badge [status]="issue()!.status" />
                  <app-issue-priority-indicator [priority]="issue()!.priority" />
                </div>
              </div>
              <lib-button variant="primary" size="md" (clicked)="handleEditIssue()">
                Edit Issue
              </lib-button>
            </div>
          </div>
        </div>

        <div class="issue-detail-page_content">
          <div class="issue-detail-page_container">
            <div class="issue-detail-page_main">
              <div class="issue-detail-page_section">
                <h2 class="issue-detail-page_section-title">Description</h2>
                <div class="issue-detail-page_description">
                  @if (issue()?.description) {
                    <lib-text-editor
                      [initialValue]="issue()!.description"
                      [readOnly]="true"
                      [showToolbar]="false"
                      class="issue-detail-page_description-editor"
                    />
                  } @else {
                    <p class="issue-detail-page_no-description">No description provided.</p>
                  }
                </div>
              </div>

              <div class="issue-detail-page_section">
                <app-comment-list [issueId]="issueId()" />
              </div>

              <div class="issue-detail-page_section">
                <app-attachment-list [issueId]="issueId()" />
              </div>

              <div class="issue-detail-page_section">
                <h2 class="issue-detail-page_section-title">Activity</h2>
                <p class="issue-detail-page_placeholder">Activity log will be shown here</p>
              </div>
            </div>
            <div class="issue-detail-page_sidebar">
              <div class="issue-detail-page_metadata">
                <h3 class="issue-detail-page_metadata-title">Details</h3>
                <div class="issue-detail-page_metadata-item">
                  <span class="issue-detail-page_metadata-label">Type</span>
                  <app-issue-type-badge [type]="issue()!.type" />
                </div>
                <div class="issue-detail-page_metadata-item">
                  <span class="issue-detail-page_metadata-label">Status</span>
                  <app-issue-status-badge [status]="issue()!.status" />
                </div>
                <div class="issue-detail-page_metadata-item">
                  <span class="issue-detail-page_metadata-label">Priority</span>
                  <app-issue-priority-indicator [priority]="issue()!.priority" />
                </div>
                @if (issue()?.assignee_id) {
                  <div class="issue-detail-page_metadata-item">
                    <span class="issue-detail-page_metadata-label">Assignee</span>
                    <span class="issue-detail-page_metadata-value">Assigned</span>
                  </div>
                }
                @if (issue()?.reporter_id) {
                  <div class="issue-detail-page_metadata-item">
                    <span class="issue-detail-page_metadata-label">Reporter</span>
                    <span class="issue-detail-page_metadata-value">Reported</span>
                  </div>
                }
                @if (issue()?.due_date) {
                  <div class="issue-detail-page_metadata-item">
                    <span class="issue-detail-page_metadata-label">Due Date</span>
                    <span class="issue-detail-page_metadata-value">{{
                      formatDate(issue()!.due_date!)
                    }}</span>
                  </div>
                }
                @if (issue()?.story_points) {
                  <div class="issue-detail-page_metadata-item">
                    <span class="issue-detail-page_metadata-label">Story Points</span>
                    <span class="issue-detail-page_metadata-value">{{
                      issue()!.story_points
                    }}</span>
                  </div>
                }
                <div class="issue-detail-page_metadata-item">
                  <span class="issue-detail-page_metadata-label">Created</span>
                  <span class="issue-detail-page_metadata-value">{{
                    formatDate(issue()!.created_at)
                  }}</span>
                </div>
                <div class="issue-detail-page_metadata-item">
                  <span class="issue-detail-page_metadata-label">Updated</span>
                  <span class="issue-detail-page_metadata-value">{{
                    formatDate(issue()!.updated_at)
                  }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      }
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .issue-detail-page {
        @apply min-h-screen;
        @apply flex flex-col;
        @apply bg-bg-primary;
      }

      .issue-detail-page_header {
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
        @apply border-b;
        @apply border-border-default;
      }

      .issue-detail-page_header-content {
        @apply max-w-7xl mx-auto;
      }

      .issue-detail-page_header-main {
        @apply flex items-start justify-between;
        @apply gap-4;
        @apply flex-wrap;
      }

      .issue-detail-page_header-info {
        @apply flex flex-col;
        @apply gap-3;
        @apply flex-1;
      }

      .issue-detail-page_key {
        @apply text-xs font-mono font-semibold;
        @apply px-2 py-1;
        @apply rounded;
        @apply bg-bg-secondary;
        @apply text-text-secondary;
        @apply inline-block;
        @apply w-fit;
      }

      .issue-detail-page_title {
        @apply text-3xl font-bold;
        @apply text-text-primary;
        margin: 0;
      }

      .issue-detail-page_badges {
        @apply flex items-center gap-2;
        @apply flex-wrap;
      }

      .issue-detail-page_content {
        @apply flex-1;
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
      }

      .issue-detail-page_container {
        @apply max-w-7xl mx-auto;
        @apply grid grid-cols-1 lg:grid-cols-3;
        @apply gap-8;
      }

      .issue-detail-page_main {
        @apply lg:col-span-2;
        @apply flex flex-col;
        @apply gap-6;
      }

      .issue-detail-page_sidebar {
        @apply lg:col-span-1;
      }

      .issue-detail-page_section {
        @apply flex flex-col;
        @apply gap-4;
      }

      .issue-detail-page_section-title {
        @apply text-lg font-semibold;
        @apply text-text-primary;
        margin: 0;
      }

      .issue-detail-page_description {
        @apply flex flex-col;
      }

      .issue-detail-page_description-editor {
        @apply border-none;
      }

      .issue-detail-page_description-editor ::ng-deep .text-editor_wrapper {
        @apply border-none;
      }

      .issue-detail-page_no-description {
        @apply text-text-secondary;
        @apply italic;
        margin: 0;
      }

      .issue-detail-page_placeholder {
        @apply text-base;
        @apply text-text-secondary;
        @apply text-center;
        @apply py-8;
        margin: 0;
      }

      .issue-detail-page_metadata {
        @apply flex flex-col;
        @apply gap-4;
        @apply p-6;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-secondary;
      }

      .issue-detail-page_metadata-title {
        @apply text-lg font-semibold;
        @apply text-text-primary;
        margin: 0 0 1rem 0;
      }

      .issue-detail-page_metadata-item {
        @apply flex flex-col;
        @apply gap-2;
      }

      .issue-detail-page_metadata-label {
        @apply text-sm font-medium;
        @apply text-text-secondary;
      }

      .issue-detail-page_metadata-value {
        @apply text-sm;
        @apply text-text-primary;
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

  readonly issueId = computed(() => {
    return this.navigationService.currentIssueId() || '';
  });
  readonly issue = computed(() => this.issueService.currentIssue());

  readonly errorMessage = computed(() => {
    const error = this.issueService.issueError();
    if (error) {
      return error instanceof Error ? error.message : 'An error occurred while loading the issue.';
    }
    return 'An unknown error occurred.';
  });

  handleEditIssue(): void {
    const id = this.issueId();
    const issue = this.issue();
    if (!id || !issue) return;

    this.modal.open(EditIssueModal, this.viewContainerRef, {
      size: 'lg',
      data: { issueId: id, issue: issue },
    });
  }

  handleRetry(): void {
    const id = this.issueId();
    if (id) {
      this.issueService.fetchIssue(id);
    }
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  }
}
