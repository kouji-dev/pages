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
  model,
} from '@angular/core';
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
  Select,
  SelectOption,
} from 'shared-ui';
import { IssueService, IssueListItem } from '../../application/services/issue.service';
import { OrganizationService } from '../../application/services/organization.service';
import { NavigationService } from '../../application/services/navigation.service';
import { ProjectMembersService } from '../../application/services/project-members.service';
import { IssueTypeBadge } from './issue-type-badge';
import { IssueStatusBadge } from './issue-status-badge';
import { IssuePriorityIndicator } from './issue-priority-indicator';
import { CreateIssueModal } from './create-issue-modal';
import { Dropdown, Icon } from 'shared-ui';
import { CommonModule } from '@angular/common';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

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
    Dropdown,
    Select,
    CommonModule,
    TranslatePipe,
  ],
  template: `
    <div class="issue-list">
      <div class="issue-list_header">
        <div class="issue-list_header-content">
          <h2 class="issue-list_title">{{ 'issues.title' | translate }}</h2>
          <lib-button variant="primary" size="md" leftIcon="plus" (clicked)="handleCreateIssue()">
            {{ 'issues.createIssue' | translate }}
          </lib-button>
        </div>
      </div>

      <div class="issue-list_filters">
        <lib-input
          [placeholder]="'issues.searchIssues' | translate"
          [(model)]="searchQuery"
          (modelChange)="handleSearch()"
          class="issue-list_search"
        />
        <div class="issue-list_filter-group">
          <lib-button
            variant="ghost"
            size="sm"
            [iconOnly]="true"
            leftIcon="list-filter"
            [libDropdown]="filterDropdownTemplate"
            [position]="'below'"
            [containerClass]="'lib-dropdown-panel--fit-content'"
            class="issue-list_filter-button"
            #filterDropdown="libDropdown"
          >
          </lib-button>
          <ng-template #filterDropdownTemplate>
            <div class="issue-list_filter-menu">
              <div class="issue-list_filter-section">
                <lib-select
                  [label]="'issues.filters.status' | translate"
                  [options]="statusFilterOptions()"
                  [(model)]="statusFilterModel"
                  [placeholder]="'issues.filters.allStatuses' | translate"
                />
              </div>
              <div class="issue-list_filter-section">
                <lib-select
                  [label]="'issues.filters.type' | translate"
                  [options]="typeFilterOptions()"
                  [(model)]="typeFilterModel"
                  [placeholder]="'issues.filters.allTypes' | translate"
                />
              </div>
              <div class="issue-list_filter-section">
                <lib-select
                  [label]="'issues.filters.assignee' | translate"
                  [options]="assigneeFilterOptions()"
                  [(model)]="assigneeFilterModel"
                  [placeholder]="'issues.filters.allAssignees' | translate"
                />
              </div>
              @if (hasActiveFilters()) {
                <div class="issue-list_filter-actions">
                  <lib-button
                    variant="ghost"
                    size="sm"
                    [fullWidth]="true"
                    (clicked)="clearFilters(filterDropdown)"
                  >
                    {{ 'issues.filters.clearFilters' | translate }}
                  </lib-button>
                </div>
              }
            </div>
          </ng-template>
        </div>
      </div>

      <div class="issue-list_content">
        @if (issueService.isLoading()) {
          <lib-loading-state [message]="'issues.loadingIssues' | translate" />
        } @else if (issueService.hasError()) {
          <lib-error-state
            [title]="'issues.failedToLoad' | translate"
            [message]="errorMessage()"
            [retryLabel]="'common.retry' | translate"
            (onRetry)="handleRetry()"
          />
        } @else if (issues().length === 0) {
          <lib-empty-state
            [title]="'issues.noIssues' | translate"
            [message]="'issues.noIssuesDescription' | translate"
            icon="file-text"
            [actionLabel]="'issues.createIssue' | translate"
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
                {{ 'common.previous' | translate }}
              </lib-button>
              <span class="issue-list_pagination-info">
                {{ 'issues.pagination.page' | translate }} {{ currentPage() }}
                {{ 'issues.pagination.of' | translate }} {{ totalPages() }}
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
            {{
              issue.assignee_id
                ? ('issues.assigned' | translate)
                : ('issues.unassigned' | translate)
            }}
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

      .issue-list_filter-group {
        @apply flex items-center;
      }

      .issue-list_filter-button {
        @apply flex-shrink-0;
      }

      .issue-list_filter-menu {
        @apply flex flex-col;
        @apply gap-4;
        @apply p-4;
        @apply min-w-[200px];
      }

      .issue-list_filter-section {
        @apply flex flex-col;
        @apply gap-2;
      }

      .issue-list_filter-label {
        @apply text-sm font-medium;
        @apply text-text-primary;
      }

      .issue-list_filter-actions {
        @apply flex items-center;
        @apply pt-2;
        @apply border-t;
        @apply border-border-default;
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
  readonly organizationService = inject(OrganizationService);
  readonly navigationService = inject(NavigationService);
  readonly projectMembersService = inject(ProjectMembersService);
  readonly modal = inject(Modal);
  readonly viewContainerRef = inject(ViewContainerRef);
  private readonly translateService = inject(TranslateService);

  readonly projectId = input.required<string>();
  readonly searchQuery = signal('');
  readonly filterStatus = signal<'todo' | 'in_progress' | 'done' | 'cancelled' | null>(null);
  readonly filterType = signal<'task' | 'bug' | 'story' | 'epic' | null>(null);
  readonly filterAssignee = signal<string | null>(null);
  readonly sortBy = signal<
    'created_at' | 'title' | 'type' | 'status' | 'priority' | 'updated_at' | null
  >(null);
  readonly sortOrder = signal<'asc' | 'desc' | null>(null);

  // Model signals for lib-select
  readonly statusFilterModel = model<'todo' | 'in_progress' | 'done' | 'cancelled' | null>(null);
  readonly typeFilterModel = model<'task' | 'bug' | 'story' | 'epic' | null>(null);
  readonly assigneeFilterModel = model<string | 'unassigned' | null>(null);

  // Sync model signals with regular signals
  private readonly syncStatusFilterEffect = effect(() => {
    this.filterStatus.set(this.statusFilterModel());
  });

  private readonly syncTypeFilterEffect = effect(() => {
    this.filterType.set(this.typeFilterModel());
  });

  private readonly syncAssigneeFilterEffect = effect(() => {
    this.filterAssignee.set(this.assigneeFilterModel());
  });

  readonly organizationId = computed(() => {
    return this.navigationService.currentOrganizationId() || '';
  });

  readonly projectMembers = computed(() => this.projectMembersService.members());

  readonly hasActiveFilters = computed(() => {
    return (
      this.filterStatus() !== null || this.filterType() !== null || this.filterAssignee() !== null
    );
  });

  // Members resource automatically loads when projectId changes via navigation service

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
    if (!event.direction) {
      // Clear sorting if direction is null
      this.sortBy.set(null);
      this.sortOrder.set(null);
    } else {
      // Map column key to sort_by parameter
      const sortByMap: Record<
        string,
        'created_at' | 'title' | 'type' | 'status' | 'priority' | 'updated_at'
      > = {
        key: 'created_at', // Use created_at for key sorting
        title: 'title',
        type: 'type',
        status: 'status',
        priority: 'priority',
        created_at: 'created_at',
        updated_at: 'updated_at',
      };

      const sortByValue = sortByMap[event.column] || 'created_at';
      this.sortBy.set(sortByValue);
      this.sortOrder.set(event.direction === 'asc' ? 'asc' : 'desc');
    }

    // Apply filters with new sort parameters
    this.applyFilters();
  }

  handleRowClick(event: { row: IssueListItem; index: number }): void {
    const orgId = this.organizationId();
    const projectId = this.projectId();
    if (orgId && projectId) {
      this.navigationService.navigateToIssue(orgId, projectId, event.row.id);
    }
  }

  handleSearch(): void {
    const query = this.searchQuery().trim();
    this.issueService.setFilters({ search: query || undefined, page: 1 });
  }

  readonly statusFilterOptions = computed<
    SelectOption<'todo' | 'in_progress' | 'done' | 'cancelled' | null>[]
  >(() => [
    { value: null, label: this.translateService.instant('issues.filters.allStatuses') },
    { value: 'todo', label: this.translateService.instant('issues.status.todo') },
    { value: 'in_progress', label: this.translateService.instant('issues.status.inProgress') },
    { value: 'done', label: this.translateService.instant('issues.status.done') },
    { value: 'cancelled', label: this.translateService.instant('issues.status.cancelled') },
  ]);

  readonly typeFilterOptions = computed<SelectOption<'task' | 'bug' | 'story' | 'epic' | null>[]>(
    () => [
      { value: null, label: this.translateService.instant('issues.filters.allTypes') },
      { value: 'task', label: this.translateService.instant('issues.type.task') },
      { value: 'bug', label: this.translateService.instant('issues.type.bug') },
      { value: 'story', label: this.translateService.instant('issues.type.story') },
      { value: 'epic', label: this.translateService.instant('issues.type.epic') },
    ],
  );

  readonly assigneeFilterOptions = computed<SelectOption<string | 'unassigned' | null>[]>(() => {
    const options: SelectOption<string | 'unassigned' | null>[] = [
      { value: null, label: this.translateService.instant('issues.filters.allAssignees') },
      { value: 'unassigned', label: this.translateService.instant('issues.unassigned') },
    ];
    return options.concat(
      this.projectMembers().map((member) => ({
        value: member.user_id,
        label: member.user_name,
      })),
    );
  });

  // Apply filters when model signals change
  private readonly applyFiltersEffect = effect(() => {
    // Trigger when any filter model changes
    this.statusFilterModel();
    this.typeFilterModel();
    this.assigneeFilterModel();
    this.applyFilters();
  });

  applyFilters(): void {
    const assigneeFilter = this.filterAssignee();
    // Handle 'unassigned' special case - we need to filter for null assignee_id
    // For now, we'll pass undefined and handle unassigned filtering on the backend
    // or we can filter client-side if needed
    this.issueService.setFilters({
      status: this.filterStatus() || undefined,
      type: this.filterType() || undefined,
      assignee_id: assigneeFilter === 'unassigned' ? undefined : assigneeFilter || undefined,
      sort_by: this.sortBy() || undefined,
      sort_order: this.sortOrder() || undefined,
      page: 1,
    });
  }

  clearFilters(dropdown: Dropdown): void {
    this.statusFilterModel.set(null);
    this.typeFilterModel.set(null);
    this.assigneeFilterModel.set(null);
    dropdown.open.set(false);
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
