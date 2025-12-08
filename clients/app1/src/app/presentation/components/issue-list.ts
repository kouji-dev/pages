import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  input,
  signal,
  ViewContainerRef,
  effect,
  ViewChild,
  TemplateRef,
} from '@angular/core';
import { Router } from '@angular/router';
import {
  Button,
  LoadingState,
  ErrorState,
  EmptyState,
  Modal,
  Input,
  Table,
  TableColumn,
  SortEvent,
} from 'shared-ui';
import { IssueService, IssueListItem } from '../../application/services/issue.service';
import { IssueTypeBadge } from './issue-type-badge';
import { IssueStatusBadge } from './issue-status-badge';
import { IssuePriorityIndicator } from './issue-priority-indicator';
import { CreateIssueModal } from './create-issue-modal';

@Component({
  selector: 'app-issue-list',
  imports: [
    Button,
    LoadingState,
    ErrorState,
    EmptyState,
    IssueTypeBadge,
    IssueStatusBadge,
    IssuePriorityIndicator,
    Input,
    Table,
  ],
  template: `
    <div class="issue-list">
      <div class="issue-list_header">
        <div class="issue-list_header-content">
          <h2 class="issue-list_title">Issues</h2>
          <lib-button variant="primary" size="md" leftIcon="plus" (clicked)="handleCreateIssue()">
            Create Issue
          </lib-button>
        </div>
      </div>

      <div class="issue-list_filters">
        <lib-input
          placeholder="Search issues..."
          [(model)]="searchQuery"
          (modelChange)="handleSearch()"
          class="issue-list_search"
        />
      </div>

      <div class="issue-list_content">
        @if (issueService.isLoading()) {
          <lib-loading-state message="Loading issues..." />
        } @else if (issueService.hasError()) {
          <lib-error-state
            title="Failed to Load Issues"
            [message]="errorMessage()"
            [retryLabel]="'Retry'"
            (onRetry)="handleRetry()"
          />
        } @else if (issues().length === 0) {
          <lib-empty-state
            title="No issues yet"
            message="Get started by creating your first issue to track work in this project."
            icon="file-text"
            actionLabel="Create Issue"
            actionIcon="plus"
            (onAction)="handleCreateIssue()"
          />
        } @else {
          <lib-table
            [data]="issues()"
            [columns]="columns()"
            [trackByFn]="trackByIssueId"
            [hoverable]="true"
            [clickable]="true"
            [cellTemplate]="cellTemplate"
            (sort)="handleSort($event)"
            (rowClick)="handleRowClick($event)"
          />

          @if (totalPages() > 1) {
            <div class="issue-list_pagination">
              <lib-button
                variant="ghost"
                size="sm"
                [disabled]="currentPage() === 1"
                (clicked)="handlePreviousPage()"
              >
                Previous
              </lib-button>
              <span class="issue-list_pagination-info">
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

      <!-- Cell Template -->
      <ng-template #cellTemplate let-issue let-column="column">
        @if (column.key === 'key') {
          <span class="issue-list_key">{{ issue.key }}</span>
        } @else if (column.key === 'title') {
          <span class="issue-list_title-text">{{ issue.title }}</span>
        } @else if (column.key === 'type') {
          <app-issue-type-badge [type]="issue.type" />
        } @else if (column.key === 'status') {
          <app-issue-status-badge [status]="issue.status" />
        } @else if (column.key === 'priority') {
          <app-issue-priority-indicator [priority]="issue.priority" />
        } @else if (column.key === 'assignee') {
          <span class="issue-list_assignee">
            {{ issue.assignee_id ? 'Assigned' : 'Unassigned' }}
          </span>
        } @else if (column.key === 'created_at') {
          <span class="issue-list_date">{{ formatDate(issue.created_at) }}</span>
        }
      </ng-template>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .issue-list {
        @apply flex flex-col;
        @apply gap-4;
      }

      .issue-list_header {
        @apply flex items-center justify-between;
      }

      .issue-list_header-content {
        @apply flex items-center justify-between;
        @apply w-full;
      }

      .issue-list_title {
        @apply text-xl font-semibold;
        @apply text-text-primary;
        margin: 0;
      }

      .issue-list_filters {
        @apply flex items-center gap-4;
      }

      .issue-list_search {
        @apply flex-1;
        @apply max-w-md;
      }

      .issue-list_content {
        @apply flex flex-col;
        @apply gap-4;
      }

      .issue-list_key {
        @apply font-mono font-semibold;
        @apply text-text-secondary;
      }

      .issue-list_title-text {
        @apply font-medium;
        @apply text-text-primary;
      }

      .issue-list_assignee {
        @apply text-text-secondary;
      }

      .issue-list_date {
        @apply text-text-secondary;
      }

      .issue-list_pagination {
        @apply flex items-center justify-center;
        @apply gap-4;
        @apply pt-4;
      }

      .issue-list_pagination-info {
        @apply text-sm;
        @apply text-text-secondary;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IssueList {
  readonly issueService = inject(IssueService);
  readonly router = inject(Router);
  readonly modal = inject(Modal);
  readonly viewContainerRef = inject(ViewContainerRef);

  readonly projectId = input.required<string>();
  readonly searchQuery = signal('');

  @ViewChild('cellTemplate') cellTemplate!: TemplateRef<{
    $implicit: IssueListItem;
    column: TableColumn<IssueListItem>;
    index: number;
  }>;

  readonly issues = computed(() => this.issueService.issuesList());
  readonly currentPage = computed(() => this.issueService.issuesPage());
  readonly totalPages = computed(() => this.issueService.issuesPages());
  readonly totalIssues = computed(() => this.issueService.issuesTotal());

  readonly columns = computed<TableColumn<IssueListItem>[]>(() => [
    {
      key: 'key',
      label: 'Key',
      width: '120px',
      sortable: false,
    },
    {
      key: 'title',
      label: 'Title',
      width: '40%',
      sortable: true,
    },
    {
      key: 'type',
      label: 'Type',
      width: '100px',
      sortable: true,
    },
    {
      key: 'status',
      label: 'Status',
      width: '120px',
      sortable: true,
    },
    {
      key: 'priority',
      label: 'Priority',
      width: '100px',
      sortable: true,
    },
    {
      key: 'assignee',
      label: 'Assignee',
      width: '120px',
      sortable: false,
    },
    {
      key: 'created_at',
      label: 'Created',
      width: '120px',
      sortable: true,
      align: 'right',
    },
  ]);

  readonly errorMessage = computed(() => {
    const error = this.issueService.error();
    if (error) {
      return error instanceof Error ? error.message : 'An error occurred while loading issues.';
    }
    return 'An unknown error occurred.';
  });

  private readonly initializeEffect = effect(
    () => {
      const projectId = this.projectId();
      if (projectId) {
        this.issueService.setProject(projectId);
        this.issueService.loadIssues();
      }
    },
    { allowSignalWrites: true },
  );

  handleCreateIssue(): void {
    const projectId = this.projectId();
    if (!projectId) return;

    this.modal.open(CreateIssueModal, this.viewContainerRef, {
      size: 'lg',
      data: { projectId },
    });
  }

  trackByIssueId = (issue: IssueListItem): string => issue.id;

  handleSort(event: SortEvent): void {
    // For now, sorting is handled by the backend via filters
    // We could enhance this to support client-side sorting or pass to backend
    if (event.direction) {
      // Backend sorting would be implemented here
      // For now, we'll just log it
      console.log('Sort:', event);
    }
  }

  handleRowClick(event: { row: IssueListItem; index: number }): void {
    this.router.navigate(['/app/issues', event.row.id]);
  }

  handleSearch(): void {
    const query = this.searchQuery().trim();
    this.issueService.setFilters({ search: query || undefined, page: 1 });
  }

  handlePreviousPage(): void {
    const current = this.currentPage();
    if (current > 1) {
      this.issueService.setFilters({ page: current - 1 });
    }
  }

  handleNextPage(): void {
    const current = this.currentPage();
    const total = this.totalPages();
    if (current < total) {
      this.issueService.setFilters({ page: current + 1 });
    }
  }

  handleRetry(): void {
    this.issueService.loadIssues();
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  }
}
