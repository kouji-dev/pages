import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  input,
  signal,
  effect,
  TemplateRef,
  ViewChild,
  ViewContainerRef,
  model,
} from '@angular/core';
import {
  CdkDragDrop,
  DragDropModule,
  moveItemInArray,
  transferArrayItem,
} from '@angular/cdk/drag-drop';
import {
  LoadingState,
  ErrorState,
  Button,
  Icon,
  Dropdown,
  Modal,
  ToastService,
  Select,
  SelectOption,
} from 'shared-ui';
import { IssueService, IssueListItem } from '../../application/services/issue.service';
import { OrganizationService } from '../../application/services/organization.service';
import { NavigationService } from '../../application/services/navigation.service';
import { ProjectMembersService } from '../../application/services/project-members.service';
import { IssueTypeBadge } from './issue-type-badge';
import { IssuePriorityIndicator } from './issue-priority-indicator';
import { CreateIssueModal } from './create-issue-modal';

type IssueStatus = 'todo' | 'in_progress' | 'done' | 'cancelled';

interface StatusColumn {
  status: IssueStatus;
  label: string;
  issues: IssueListItem[];
  visible: boolean;
  width?: number;
}

interface BoardSettings {
  columnOrder: IssueStatus[];
  columnVisibility: Record<IssueStatus, boolean>;
  columnWidths: Record<IssueStatus, number>;
}

@Component({
  selector: 'app-kanban-board',
  standalone: true,
  imports: [
    LoadingState,
    ErrorState,
    DragDropModule,
    IssueTypeBadge,
    IssuePriorityIndicator,
    Button,
    Icon,
    Dropdown,
    Select,
  ],
  template: `
    <div class="kanban-board">
      <div class="kanban-board_header">
        <h2 class="kanban-board_title">Kanban Board</h2>
        <div class="kanban-board_header-actions">
          <lib-button variant="primary" size="md" leftIcon="plus" (clicked)="handleCreateIssue()">
            Create Issue
          </lib-button>
          <div class="kanban-board_filters">
            <lib-button
              variant="ghost"
              size="sm"
              [iconOnly]="true"
              leftIcon="list-filter"
              [libDropdown]="filterDropdownTemplate"
              [position]="'below'"
              [containerClass]="'lib-dropdown-panel--fit-content'"
              class="kanban-board_filter-button"
              #filterDropdown="libDropdown"
            >
            </lib-button>
            <lib-button
              variant="ghost"
              size="sm"
              [iconOnly]="true"
              leftIcon="settings"
              [libDropdown]="settingsDropdownTemplate"
              [position]="'below'"
              [containerClass]="'lib-dropdown-panel--fit-content'"
              class="kanban-board_settings-button"
              #settingsDropdown="libDropdown"
            >
            </lib-button>
            <ng-template #filterDropdownTemplate>
              <div class="kanban-board_filter-menu">
                <div class="kanban-board_filter-section">
                  <lib-select
                    label="Assignee"
                    [options]="assigneeFilterOptions()"
                    [(model)]="assigneeFilterModel"
                    [placeholder]="'All Assignees'"
                  />
                </div>
                <div class="kanban-board_filter-section">
                  <lib-select
                    label="Type"
                    [options]="typeFilterOptions()"
                    [(model)]="typeFilterModel"
                    [placeholder]="'All Types'"
                  />
                </div>
                <div class="kanban-board_filter-section">
                  <lib-select
                    label="Priority"
                    [options]="priorityFilterOptions()"
                    [(model)]="priorityFilterModel"
                    [placeholder]="'All Priorities'"
                  />
                </div>
                @if (hasActiveFilters()) {
                  <div class="kanban-board_filter-actions">
                    <lib-button variant="ghost" size="sm" (clicked)="clearFilters(filterDropdown)">
                      Clear Filters
                    </lib-button>
                  </div>
                }
              </div>
            </ng-template>
            <ng-template #settingsDropdownTemplate>
              <div class="kanban-board_settings-menu">
                <div class="kanban-board_settings-section">
                  <label class="kanban-board_settings-label">Column Visibility</label>
                  @for (column of allColumns(); track column.status) {
                    <label class="kanban-board_settings-checkbox">
                      <input
                        type="checkbox"
                        [checked]="columnVisibility()[column.status]"
                        (change)="
                          toggleColumnVisibility(column.status, $any($event.target).checked)
                        "
                      />
                      <span>{{ column.label }}</span>
                    </label>
                  }
                </div>
                <div class="kanban-board_settings-actions">
                  <lib-button variant="ghost" size="sm" (clicked)="resetSettings(settingsDropdown)">
                    Reset All
                  </lib-button>
                </div>
              </div>
            </ng-template>
          </div>
        </div>
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
          <div
            class="kanban-board_columns"
            cdkDropListGroup
            [style.grid-template-columns]="gridTemplateColumns()"
          >
            @for (column of visibleColumns(); track column.status) {
              <div
                class="kanban-board_column"
                cdkDropList
                [cdkDropListData]="column.issues"
                (cdkDropListDropped)="handleDrop($event, column.status)"
                [style.width]="column.width ? column.width + 'px' : 'auto'"
                [style.min-width]="column.width ? column.width + 'px' : '250px'"
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
                        <div class="kanban-board_card-footer-left">
                          <app-issue-priority-indicator [priority]="issue.priority" />
                          @if (issue.assignee_id) {
                            <span class="kanban-board_card-assignee">Assigned</span>
                          }
                        </div>
                        @if (issue.due_date && isOverdue(issue.due_date)) {
                          <div
                            class="kanban-board_card-due-date"
                            [title]="'Due: ' + formatDate(issue.due_date)"
                          >
                            <lib-icon name="calendar" size="xs" />
                            <span>Overdue</span>
                          </div>
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
        @apply gap-4;
      }

      .kanban-board_header-actions {
        @apply flex items-center;
        @apply gap-2;
      }

      .kanban-board_filters {
        @apply flex items-center;
        @apply gap-2;
      }

      .kanban-board_filter-button,
      .kanban-board_settings-button {
        @apply flex-shrink-0;
      }

      .kanban-board_settings-menu {
        @apply flex flex-col;
        @apply gap-4;
        @apply p-4;
        @apply min-w-[250px];
      }

      .kanban-board_settings-section {
        @apply flex flex-col;
        @apply gap-3;
      }

      .kanban-board_settings-label {
        @apply text-sm font-medium;
        @apply text-text-primary;
      }

      .kanban-board_settings-checkbox {
        @apply flex items-center;
        @apply gap-2;
        @apply cursor-pointer;
        @apply text-sm;
        @apply text-text-primary;
      }

      .kanban-board_settings-checkbox input[type='checkbox'] {
        @apply cursor-pointer;
      }

      .kanban-board_settings-actions {
        @apply flex items-center;
        @apply pt-2;
        @apply border-t;
        @apply border-border-default;
      }

      .kanban-board_filter-menu {
        @apply flex flex-col;
        @apply gap-4;
        @apply p-4;
        @apply min-w-[200px];
      }

      .kanban-board_filter-section {
        @apply flex flex-col;
        @apply gap-2;
      }

      .kanban-board_filter-label {
        @apply text-sm font-medium;
        @apply text-text-primary;
      }

      .kanban-board_filter-actions {
        @apply flex items-center;
        @apply pt-2;
        @apply border-t;
        @apply border-border-default;
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

      .kanban-board_card-footer-left {
        @apply flex items-center;
        @apply gap-2;
      }

      .kanban-board_card-assignee {
        @apply text-xs;
        @apply text-text-secondary;
      }

      .kanban-board_card-due-date {
        @apply flex items-center;
        @apply gap-1;
        @apply text-xs;
        @apply font-medium;
        @apply text-error;
        @apply px-2 py-1;
        @apply rounded;
        @apply bg-error-50;
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
  readonly projectMembersService = inject(ProjectMembersService);
  readonly modal = inject(Modal);
  readonly viewContainerRef = inject(ViewContainerRef);
  readonly toast = inject(ToastService);
  readonly projectId = input.required<string>();

  readonly organizationId = computed(() => {
    return this.navigationService.currentOrganizationId() || '';
  });

  // Board settings storage key
  private readonly STORAGE_KEY = 'kanban_board_settings';

  // Default column order
  private readonly DEFAULT_COLUMN_ORDER: IssueStatus[] = [
    'todo',
    'in_progress',
    'done',
    'cancelled',
  ];

  // Flag to prevent saving during initial load
  private isInitializing = true;

  // Column visibility signal
  readonly columnVisibility = signal<Record<IssueStatus, boolean>>({
    todo: true,
    in_progress: true,
    done: true,
    cancelled: true,
  });

  // Column order signal
  readonly columnOrder = signal<IssueStatus[]>(this.DEFAULT_COLUMN_ORDER);

  // Column widths signal
  readonly columnWidths = signal<Record<IssueStatus, number>>({
    todo: 0,
    in_progress: 0,
    done: 0,
    cancelled: 0,
  });

  // Filter signals
  readonly filterAssignee = signal<string | null>(null);
  readonly filterType = signal<'task' | 'bug' | 'story' | 'epic' | null>(null);
  readonly filterPriority = signal<'low' | 'medium' | 'high' | 'critical' | null>(null);

  // Model signals for lib-select
  readonly assigneeFilterModel = model<string | null>(null);
  readonly typeFilterModel = model<'task' | 'bug' | 'story' | 'epic' | null>(null);
  readonly priorityFilterModel = model<'low' | 'medium' | 'high' | 'critical' | null>(null);

  // Sync model signals with regular signals
  private readonly syncAssigneeFilterEffect = effect(() => {
    this.filterAssignee.set(this.assigneeFilterModel());
  });

  private readonly syncTypeFilterEffect = effect(() => {
    this.filterType.set(this.typeFilterModel());
  });

  private readonly syncPriorityFilterEffect = effect(() => {
    this.filterPriority.set(this.priorityFilterModel());
  });

  // Load project members for assignee filter
  readonly projectMembers = computed(() => this.projectMembersService.members());

  // Initialize members loading
  private readonly initializeMembersEffect = effect(() => {
    const id = this.projectId();
    if (id) {
      this.projectMembersService.loadMembers(id);
    }
  });

  // Load board settings from localStorage on init
  constructor() {
    this.loadBoardSettings();
    this.isInitializing = false;

    // Save settings to localStorage when they change (but not during initial load)
    effect(() => {
      if (this.isInitializing) return;

      const visibility = this.columnVisibility();
      const order = this.columnOrder();
      const widths = this.columnWidths();
      this.saveBoardSettings({
        columnVisibility: visibility,
        columnOrder: order,
        columnWidths: widths,
      });
    });
  }

  readonly issues = computed(() => this.issueService.issuesList());

  // Filtered issues based on active filters
  readonly filteredIssues = computed(() => {
    let issues = this.issues();
    const assigneeFilter = this.filterAssignee();
    const typeFilter = this.filterType();
    const priorityFilter = this.filterPriority();

    if (assigneeFilter) {
      issues = issues.filter((issue) => issue.assignee_id === assigneeFilter);
    }
    if (typeFilter) {
      issues = issues.filter((issue) => issue.type === typeFilter);
    }
    if (priorityFilter) {
      issues = issues.filter((issue) => issue.priority === priorityFilter);
    }

    return issues;
  });

  readonly hasActiveFilters = computed(() => {
    return (
      this.filterAssignee() !== null || this.filterType() !== null || this.filterPriority() !== null
    );
  });

  readonly assigneeFilterOptions = computed<SelectOption<string | null>[]>(() => {
    const options: SelectOption<string | null>[] = [{ value: null, label: 'All Assignees' }];
    return options.concat(
      this.projectMembers().map((member) => ({
        value: member.user_id,
        label: member.user_name,
      })),
    );
  });

  readonly typeFilterOptions = computed<SelectOption<'task' | 'bug' | 'story' | 'epic' | null>[]>(
    () => [
      { value: null, label: 'All Types' },
      { value: 'task', label: 'Task' },
      { value: 'bug', label: 'Bug' },
      { value: 'story', label: 'Story' },
      { value: 'epic', label: 'Epic' },
    ],
  );

  readonly priorityFilterOptions = computed<
    SelectOption<'low' | 'medium' | 'high' | 'critical' | null>[]
  >(() => [
    { value: null, label: 'All Priorities' },
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'critical', label: 'Critical' },
  ]);

  // All available columns (for settings)
  readonly allColumns = computed<StatusColumn[]>(() => {
    return [
      { status: 'todo', label: 'To Do', issues: [], visible: true },
      { status: 'in_progress', label: 'In Progress', issues: [], visible: true },
      { status: 'done', label: 'Done', issues: [], visible: true },
      { status: 'cancelled', label: 'Cancelled', issues: [], visible: true },
    ];
  });

  // Columns with issues grouped, respecting order and visibility
  readonly columns = computed<StatusColumn[]>(() => {
    const issues = this.filteredIssues();
    const order = this.columnOrder();
    const visibility = this.columnVisibility();
    const widths = this.columnWidths();

    // Create columns in the specified order
    const statusColumns: StatusColumn[] = order.map((status) => {
      const label = this.getColumnLabel(status);
      return {
        status,
        label,
        issues: [],
        visible: visibility[status] ?? true,
        width: widths[status] || undefined,
      };
    });

    // Group issues by status
    issues.forEach((issue) => {
      const column = statusColumns.find((col) => col.status === issue.status);
      if (column) {
        column.issues.push(issue);
      }
    });

    return statusColumns;
  });

  // Only visible columns
  readonly visibleColumns = computed<StatusColumn[]>(() => {
    return this.columns().filter((col) => col.visible);
  });

  // Grid template columns for CSS
  readonly gridTemplateColumns = computed(() => {
    const visibleCols = this.visibleColumns();
    if (visibleCols.length === 0) return '1fr';

    return visibleCols.map((col) => (col.width ? `${col.width}px` : '1fr')).join(' ');
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
    const issue = currentContainer.data[event.currentIndex];

    if (previousContainer === currentContainer) {
      // Reorder within same column - optimistic update
      moveItemInArray(currentContainer.data, event.previousIndex, event.currentIndex);
      // Note: Backend doesn't support ordering yet, so we just update UI optimistically
    } else {
      // Move to different column - optimistic update
      transferArrayItem(
        previousContainer.data,
        currentContainer.data,
        event.previousIndex,
        event.currentIndex,
      );

      // Update issue status in background
      if (issue) {
        try {
          await this.issueService.updateIssue(issue.id, { status: newStatus });
          // Success - UI already updated optimistically
        } catch (error) {
          this.toast.error('Failed to update issue status');

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

  clearFilters(dropdown: Dropdown): void {
    this.assigneeFilterModel.set(null);
    this.typeFilterModel.set(null);
    this.priorityFilterModel.set(null);
    dropdown.open.set(false);
  }

  isOverdue(dueDate: string): boolean {
    const due = new Date(dueDate);
    const now = new Date();
    now.setHours(0, 0, 0, 0);
    due.setHours(0, 0, 0, 0);
    return due < now;
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString();
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

  handleCreateIssue(): void {
    this.modal.open(CreateIssueModal, this.viewContainerRef, {
      size: 'md',
      closable: true,
      data: {
        projectId: this.projectId(),
      },
    });
  }

  getColumnLabel(status: IssueStatus): string {
    const labels: Record<IssueStatus, string> = {
      todo: 'To Do',
      in_progress: 'In Progress',
      done: 'Done',
      cancelled: 'Cancelled',
    };
    return labels[status];
  }

  toggleColumnVisibility(status: IssueStatus, visible: boolean): void {
    this.columnVisibility.update((current) => ({
      ...current,
      [status]: visible,
    }));
  }

  resetColumnOrder(): void {
    this.columnOrder.set([...this.DEFAULT_COLUMN_ORDER]);
  }

  resetSettings(dropdown: Dropdown): void {
    this.columnVisibility.set({
      todo: true,
      in_progress: true,
      done: true,
      cancelled: true,
    });
    this.columnOrder.set([...this.DEFAULT_COLUMN_ORDER]);
    this.columnWidths.set({
      todo: 0,
      in_progress: 0,
      done: 0,
      cancelled: 0,
    });
    dropdown.open.set(false);
  }

  private loadBoardSettings(): void {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        const settings: BoardSettings = JSON.parse(stored);

        if (settings.columnVisibility) {
          this.columnVisibility.set({
            todo: settings.columnVisibility.todo ?? true,
            in_progress: settings.columnVisibility.in_progress ?? true,
            done: settings.columnVisibility.done ?? true,
            cancelled: settings.columnVisibility.cancelled ?? true,
          });
        }

        if (settings.columnOrder && settings.columnOrder.length === 4) {
          // Validate that all statuses are present
          const allStatuses: IssueStatus[] = ['todo', 'in_progress', 'done', 'cancelled'];
          const isValid = allStatuses.every((status) => settings.columnOrder.includes(status));
          if (isValid) {
            this.columnOrder.set(settings.columnOrder);
          }
        }

        if (settings.columnWidths) {
          this.columnWidths.set({
            todo: settings.columnWidths.todo || 0,
            in_progress: settings.columnWidths.in_progress || 0,
            done: settings.columnWidths.done || 0,
            cancelled: settings.columnWidths.cancelled || 0,
          });
        }
      }
    } catch (error) {
      console.error('Failed to load board settings:', error);
    }
  }

  private saveBoardSettings(settings: BoardSettings): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(settings));
    } catch (error) {
      console.error('Failed to save board settings:', error);
    }
  }
}
