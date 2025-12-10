import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  input,
  signal,
  effect,
} from '@angular/core';
import {
  CdkDragDrop,
  DragDropModule,
  moveItemInArray,
  transferArrayItem,
} from '@angular/cdk/drag-drop';
import { LoadingState, ErrorState } from 'shared-ui';
import { IssueService, IssueListItem } from '../../application/services/issue.service';
import { OrganizationService } from '../../application/services/organization.service';
import { NavigationService } from '../../application/services/navigation.service';
import { IssueTypeBadge } from './issue-type-badge';
import { IssuePriorityIndicator } from './issue-priority-indicator';

type IssueStatus = 'todo' | 'in_progress' | 'done' | 'cancelled';

interface StatusColumn {
  status: IssueStatus;
  label: string;
  issues: IssueListItem[];
}

@Component({
  selector: 'app-kanban-board',
  standalone: true,
  imports: [LoadingState, ErrorState, DragDropModule, IssueTypeBadge, IssuePriorityIndicator],
  template: `
    <div class="kanban-board">
      <div class="kanban-board_header">
        <h2 class="kanban-board_title">Kanban Board</h2>
      </div>

      <div class="kanban-board_content">
        @if (issueService.isLoading()) {
          <lib-loading-state message="Loading issues..." />
        } @else if (issueService.hasError()) {
          <lib-error-state
            title="Failed to Load Issues"
            [message]="errorMessage()"
            [retryLabel]="'Retry'"
            (onRetry)="handleRetry()"
          />
        } @else {
          <div class="kanban-board_columns" cdkDropListGroup>
            @for (column of columns(); track column.status) {
              <div
                class="kanban-board_column"
                cdkDropList
                [cdkDropListData]="column.issues"
                (cdkDropListDropped)="handleDrop($event, column.status)"
              >
                <div class="kanban-board_column-header">
                  <h3 class="kanban-board_column-title">
                    {{ column.label }}
                    <span class="kanban-board_column-count">({{ column.issues.length }})</span>
                  </h3>
                </div>
                <div class="kanban-board_column-content">
                  @for (issue of column.issues; track issue.id) {
                    <div class="kanban-board_card" cdkDrag (click)="handleIssueClick(issue)">
                      <div class="kanban-board_card-header">
                        <span class="kanban-board_card-key">{{ issue.key }}</span>
                        <app-issue-type-badge [type]="issue.type" />
                      </div>
                      <div class="kanban-board_card-title">{{ issue.title }}</div>
                      <div class="kanban-board_card-footer">
                        <app-issue-priority-indicator [priority]="issue.priority" />
                        @if (issue.assignee_id) {
                          <span class="kanban-board_card-assignee">Assigned</span>
                        }
                      </div>
                    </div>
                  }
                  @if (column.issues.length === 0) {
                    <div class="kanban-board_empty">No issues</div>
                  }
                </div>
              </div>
            }
          </div>
        }
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .kanban-board {
        @apply flex flex-col;
        @apply gap-4;
        @apply w-full;
        @apply h-full;
      }

      .kanban-board_header {
        @apply flex items-center justify-between;
      }

      .kanban-board_title {
        @apply text-xl font-semibold;
        @apply text-text-primary;
        margin: 0;
      }

      .kanban-board_content {
        @apply flex-1;
        @apply w-full;
        @apply overflow-hidden;
      }

      .kanban-board_columns {
        @apply grid;
        @apply grid-cols-4;
        @apply gap-4;
        @apply h-full;
        @apply w-full;
        @apply overflow-x-auto;
      }

      .kanban-board_column {
        @apply flex flex-col;
        @apply min-w-0;
        @apply bg-bg-secondary;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply h-full;
      }

      .kanban-board_column-header {
        @apply p-4;
        @apply border-b;
        @apply border-border-default;
      }

      .kanban-board_column-title {
        @apply text-base font-semibold;
        @apply text-text-primary;
        margin: 0;
      }

      .kanban-board_column-count {
        @apply text-sm font-normal;
        @apply text-text-secondary;
      }

      .kanban-board_column-content {
        @apply flex-1;
        @apply p-4;
        @apply flex flex-col;
        @apply gap-3;
        @apply min-h-[200px];
      }

      .kanban-board_card {
        @apply p-4;
        @apply bg-bg-primary;
        @apply border;
        @apply border-border-default;
        @apply rounded-lg;
        @apply cursor-move;
        @apply hover:shadow-md;
        @apply transition-shadow;
      }

      .kanban-board_card.cdk-drag-animating {
        @apply transition-transform;
      }

      .kanban-board_card-header {
        @apply flex items-center justify-between;
        @apply mb-2;
      }

      .kanban-board_card-key {
        @apply text-xs font-mono font-semibold;
        @apply text-text-secondary;
      }

      .kanban-board_card-title {
        @apply text-sm font-medium;
        @apply text-text-primary;
        @apply mb-3;
        @apply line-clamp-2;
      }

      .kanban-board_card-footer {
        @apply flex items-center justify-between;
        @apply gap-2;
      }

      .kanban-board_card-assignee {
        @apply text-xs;
        @apply text-text-secondary;
      }

      .kanban-board_empty {
        @apply text-sm;
        @apply text-text-secondary;
        @apply text-center;
        @apply py-8;
      }

      .cdk-drag-preview {
        @apply shadow-lg;
        @apply opacity-90;
      }

      .cdk-drag-placeholder {
        @apply opacity-50;
      }

      .cdk-drop-list-dragging .kanban-board_card:not(.cdk-drag-placeholder) {
        @apply transition-transform;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class KanbanBoard {
  readonly issueService = inject(IssueService);
  readonly organizationService = inject(OrganizationService);
  readonly navigationService = inject(NavigationService);

  readonly projectId = input.required<string>();

  readonly organizationId = computed(() => {
    return this.navigationService.currentOrganizationId() || '';
  });

  readonly issues = computed(() => this.issueService.issuesList());

  readonly columns = computed<StatusColumn[]>(() => {
    const issues = this.issues();
    const statusColumns: StatusColumn[] = [
      { status: 'todo', label: 'To Do', issues: [] },
      { status: 'in_progress', label: 'In Progress', issues: [] },
      { status: 'done', label: 'Done', issues: [] },
      { status: 'cancelled', label: 'Cancelled', issues: [] },
    ];

    // Group issues by status
    issues.forEach((issue) => {
      const column = statusColumns.find((col) => col.status === issue.status);
      if (column) {
        column.issues.push(issue);
      }
    });

    return statusColumns;
  });

  readonly errorMessage = computed(() => {
    const error = this.issueService.error();
    if (error) {
      return error instanceof Error ? error.message : 'An error occurred while loading issues.';
    }
    return 'An unknown error occurred.';
  });

  // Issues are now automatically loaded when URL organizationId and projectId change
  // No need for manual initialization effect

  async handleDrop(event: CdkDragDrop<IssueListItem[]>, newStatus: IssueStatus): Promise<void> {
    const previousContainer = event.previousContainer;
    const currentContainer = event.container;

    if (previousContainer === currentContainer) {
      // Reorder within same column
      moveItemInArray(currentContainer.data, event.previousIndex, event.currentIndex);
    } else {
      // Move to different column
      transferArrayItem(
        previousContainer.data,
        currentContainer.data,
        event.previousIndex,
        event.currentIndex,
      );

      // Update issue status
      const issue = currentContainer.data[event.currentIndex];
      if (issue) {
        try {
          await this.issueService.updateIssue(issue.id, { status: newStatus });
        } catch (error) {
          console.error('Failed to update issue status:', error);
          // Revert the move on error
          transferArrayItem(
            currentContainer.data,
            previousContainer.data,
            event.currentIndex,
            event.previousIndex,
          );
        }
      }
    }
  }

  handleIssueClick(issue: IssueListItem): void {
    const orgId = this.organizationId();
    const projectId = this.projectId();
    if (orgId && projectId) {
      this.navigationService.navigateToIssue(orgId, projectId, issue.id);
    }
  }

  handleRetry(): void {
    this.issueService.loadIssues();
  }
}
