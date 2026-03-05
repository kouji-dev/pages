import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  input,
  signal,
  effect,
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
  Dropdown,
  Modal,
  ToastService,
  Select,
  SelectOption,
  Badge,
} from 'shared-ui';
import { IssueListItem } from '../../../../application/services/issue.service';
import {
  BoardService,
  BoardIssueItemResponse,
  BoardIssuesResponse,
  BoardListWithIssuesResponse,
} from '../../../../application/services/board.service';
import { LabelService, Label } from '../../../../application/services/label.service';
import { OrganizationService } from '../../../../application/services/organization.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import {
  ProjectMembersService,
  ProjectMember,
} from '../../../../application/services/project-members.service';
import { CreateIssueModal } from '../create-issue-modal/create-issue-modal';
import { IssueCard } from '../../../../shared/components/issue-card';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

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
    IssueCard,
    Button,
    Dropdown,
    Select,
    TranslatePipe,
    Badge,
  ],
  template: `
    <div class="kanban-board">
      <div class="kanban-board_header">
        <div class="kanban-board_header-actions">
          <lib-button variant="primary" size="md" leftIcon="plus" (clicked)="handleCreateIssue()">
            {{ 'board.createIssue' | translate }}
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
                    [label]="'board.assignee' | translate"
                    [options]="assigneeFilterOptions()"
                    [(model)]="assigneeFilterModel"
                    [placeholder]="'board.allAssignees' | translate"
                  />
                </div>
                <div class="kanban-board_filter-section">
                  <lib-select
                    [label]="'board.type' | translate"
                    [options]="typeFilterOptions()"
                    [(model)]="typeFilterModel"
                    [placeholder]="'board.allTypes' | translate"
                  />
                </div>
                <div class="kanban-board_filter-section">
                  <lib-select
                    [label]="'board.priority' | translate"
                    [options]="priorityFilterOptions()"
                    [(model)]="priorityFilterModel"
                    [placeholder]="'board.allPriorities' | translate"
                  />
                </div>
                @if (hasActiveFilters()) {
                  <div class="kanban-board_filter-actions">
                    <lib-button variant="ghost" size="sm" (clicked)="clearFilters(filterDropdown)">
                      {{ 'board.clearFilters' | translate }}
                    </lib-button>
                  </div>
                }
              </div>
            </ng-template>
            <ng-template #settingsDropdownTemplate>
              <div class="kanban-board_settings-menu">
                <div class="kanban-board_settings-section">
                  <label class="kanban-board_settings-label">{{
                    'board.columnVisibility' | translate
                  }}</label>
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
                <div class="kanban-board_settings-section">
                  <lib-select
                    [label]="'Swimlanes'"
                    [options]="swimlaneTypeOptions()"
                    [(model)]="swimlaneTypeModel"
                  />
                </div>
                <div class="kanban-board_settings-actions">
                  <lib-button variant="ghost" size="sm" (clicked)="resetSettings(settingsDropdown)">
                    {{ 'board.resetAll' | translate }}
                  </lib-button>
                </div>
              </div>
            </ng-template>
          </div>
        </div>
      </div>

      <div class="kanban-board_content">
        @if (isLoadingBoardIssues()) {
          <lib-loading-state [message]="'board.loadingIssues' | translate" />
        } @else if (hasBoardIssuesError()) {
          <lib-error-state
            [title]="'board.failedToLoad' | translate"
            [message]="errorMessage()"
            [retryLabel]="'common.retry' | translate"
            (onRetry)="handleRetry()"
          />
        } @else {
          <div class="kanban-board_columns" cdkDropListGroup>
            @for (column of visibleColumns(); track column.status) {
              <div
                class="kanban-board_column"
                cdkDropList
                [cdkDropListData]="column.issues"
                (cdkDropListDropped)="handleDrop($event, column.status)"
              >
                <div class="kanban-board_column-header">
                  <div class="kanban-board_column-header-left">
                    <span
                      class="kanban-board_column-title"
                      [class]="getColumnColorClass(column.status)"
                    >
                      {{ column.label }}
                    </span>
                    <lib-badge variant="default" class="kanban-board_column-badge">
                      {{ column.issues.length }}
                    </lib-badge>
                  </div>
                  <div class="kanban-board_column-header-actions">
                    <lib-button
                      variant="ghost"
                      size="sm"
                      [iconOnly]="true"
                      leftIcon="plus"
                      class="kanban-board_column-action"
                    >
                    </lib-button>
                    <lib-button
                      variant="ghost"
                      size="sm"
                      [iconOnly]="true"
                      leftIcon="grip-horizontal"
                      class="kanban-board_column-action"
                    >
                    </lib-button>
                  </div>
                </div>
                <div class="kanban-board_column-content">
                  @for (issue of column.issues; track issue.id) {
                    <div cdkDrag>
                      <app-issue-card
                        [issue]="issue"
                        [assignee]="getAssignee(issue.assignee_id) || null"
                        (onClick)="handleIssueClick($event)"
                      />
                    </div>
                  }
                  @if (column.issues.length === 0) {
                    <div class="kanban-board_empty">{{ 'board.noIssues' | translate }}</div>
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
        @apply flex-1;
        @apply min-h-0;
      }

      .kanban-board_header {
        @apply flex items-center justify-end;
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
        @apply text-foreground;
      }

      .kanban-board_settings-checkbox {
        @apply flex items-center;
        @apply gap-2;
        @apply cursor-pointer;
        @apply text-sm;
        @apply text-foreground;
      }

      .kanban-board_settings-checkbox input[type='checkbox'] {
        @apply cursor-pointer;
      }

      .kanban-board_settings-actions {
        @apply flex items-center;
        @apply pt-2;
        @apply border-t;
        @apply border-border;
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
        @apply text-foreground;
      }

      .kanban-board_filter-actions {
        @apply flex items-center;
        @apply pt-2;
        @apply border-t;
        @apply border-border;
      }

      .kanban-board_content {
        @apply flex-1;
        @apply w-full;
        @apply overflow-hidden;
      }

      .kanban-board_columns {
        @apply flex;
        @apply gap-4;
        @apply h-full;
        @apply overflow-x-auto;
        @apply pb-4;
        @apply min-w-max;
      }

      .kanban-board_column {
        @apply w-72;
        @apply flex flex-col;
        @apply flex-shrink-0;
        @apply h-full;
        @apply border;
        @apply border-border;
        @apply rounded-lg;
        @apply p-4;
      }

      .kanban-board_column-header {
        @apply flex items-center justify-between;
        @apply mb-4;
      }

      .kanban-board_column-header-left {
        @apply flex items-center;
        @apply gap-2;
      }

      .kanban-board_column-title {
        @apply text-sm font-semibold;
        margin: 0;
      }

      .kanban-board_column-badge {
        @apply text-xs;
        @apply h-5 w-5;
        @apply p-0;
        @apply flex items-center justify-center;
        @apply rounded-full;
      }

      .kanban-board_column-header-actions {
        @apply flex items-center;
        @apply gap-1;
      }

      .kanban-board_column-action {
        @apply h-6 w-6;
      }

      .kanban-board_column-content {
        @apply flex-1;
        @apply space-y-3;
        @apply min-h-0;
      }

      .kanban-board_empty {
        @apply text-sm;
        @apply text-muted-foreground;
        @apply text-center;
        @apply py-8;
      }

      /* Column color classes */
      .kanban-board_column-title.text-muted-foreground {
        @apply text-muted-foreground;
      }

      .kanban-board_column-title.text-amber-500 {
        @apply text-amber-500;
      }

      .kanban-board_column-title.text-green-500 {
        @apply text-green-500;
      }

      .cdk-drag-preview {
        @apply shadow-lg;
        @apply opacity-90;
      }

      .cdk-drag-placeholder {
        @apply opacity-50;
      }

      .cdk-drop-list-dragging app-issue-card:not(.cdk-drag-placeholder) {
        @apply transition-transform;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class KanbanBoard {
  readonly boardService = inject(BoardService);
  readonly labelService = inject(LabelService);
  readonly organizationService = inject(OrganizationService);
  readonly navigationService = inject(NavigationService);
  readonly projectMembersService = inject(ProjectMembersService);
  readonly modal = inject(Modal);
  readonly viewContainerRef = inject(ViewContainerRef);
  readonly toast = inject(ToastService);
  private readonly translateService = inject(TranslateService);
  readonly projectId = input.required<string>();
  readonly boardId = input.required<string>();

  readonly boardIssuesResponse = signal<BoardIssuesResponse | null>(null);
  readonly boardIssueLists = signal<BoardListWithIssuesResponse[]>([]);
  readonly issueListMap = signal<Map<string, string>>(new Map());
  readonly projectLabels = signal<Label[]>([]);
  readonly swimlaneTypeModel = model<'none' | 'epic' | 'assignee'>('none');
  readonly isApplyingScope = signal(false);
  readonly isLoadingBoardIssues = signal(false);
  readonly boardIssuesError = signal<unknown | null>(null);
  readonly hasBoardIssuesError = computed(() => this.boardIssuesError() !== null);

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
  private scopeSyncTimeout: ReturnType<typeof setTimeout> | null = null;

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

  private readonly syncScopeToBoardEffect = effect(() => {
    const boardId = this.boardId();
    const assignee = this.filterAssignee();
    const type = this.filterType();
    const priority = this.filterPriority();
    if (!boardId) return;
    if (this.scopeSyncTimeout) {
      clearTimeout(this.scopeSyncTimeout);
    }
    this.scopeSyncTimeout = setTimeout(() => {
      void this.applyScope(boardId, assignee, type, priority);
    }, 250);
  });

  // Load project members for assignee filter
  readonly projectMembers = computed(() => this.projectMembersService.members());

  // Initialize members loading
  // Members resource automatically loads when projectId changes via navigation service

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

    effect(() => {
      const boardId = this.boardId();
      if (!boardId) return;
      this.loadBoardIssues(boardId);
    });

    effect(() => {
      const projectId = this.projectId();
      if (!projectId) return;
      void this.loadProjectLabels(projectId);
    });

    effect(() => {
      const boardId = this.boardId();
      const swimlaneType = this.swimlaneTypeModel();
      if (!boardId) return;
      const currentSwimlane = this.boardIssuesResponse()?.swimlane_type;
      if (!currentSwimlane || currentSwimlane === swimlaneType) return;
      void this.handleSwimlaneChange(swimlaneType);
    });
  }

  readonly issues = computed<IssueListItem[]>(() => {
    const response = this.boardIssuesResponse();
    if (!response) return [];

    const uniqueIssues = new Map<string, IssueListItem>();
    const lists =
      response.swimlane_type === 'none'
        ? response.lists
        : response.swimlanes.flatMap((swimlane) => swimlane.lists);

    for (const list of lists) {
      for (const issue of list.issues) {
        if (!uniqueIssues.has(issue.id)) {
          uniqueIssues.set(issue.id, this.mapBoardIssueToIssueListItem(issue));
        }
      }
    }

    return Array.from(uniqueIssues.values());
  });

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
    const options: SelectOption<string | null>[] = [
      { value: null, label: this.translateService.instant('board.allAssignees') },
    ];
    return options.concat(
      this.projectMembers().map((member) => ({
        value: member.user_id,
        label: member.user_name,
      })),
    );
  });

  readonly typeFilterOptions = computed<SelectOption<'task' | 'bug' | 'story' | 'epic' | null>[]>(
    () => [
      { value: null, label: this.translateService.instant('board.allTypes') },
      { value: 'task', label: this.translateService.instant('issues.type.task') },
      { value: 'bug', label: this.translateService.instant('issues.type.bug') },
      { value: 'story', label: this.translateService.instant('issues.type.story') },
      { value: 'epic', label: this.translateService.instant('issues.type.epic') },
    ],
  );

  readonly priorityFilterOptions = computed<
    SelectOption<'low' | 'medium' | 'high' | 'critical' | null>[]
  >(() => [
    { value: null, label: this.translateService.instant('board.allPriorities') },
    { value: 'low', label: this.translateService.instant('issues.priority.low') },
    { value: 'medium', label: this.translateService.instant('issues.priority.medium') },
    { value: 'high', label: this.translateService.instant('issues.priority.high') },
    { value: 'critical', label: this.translateService.instant('issues.priority.critical') },
  ]);

  readonly swimlaneTypeOptions = computed<SelectOption<'none' | 'epic' | 'assignee'>[]>(() => [
    { value: 'none', label: 'No swimlanes' },
    { value: 'epic', label: 'By epic' },
    { value: 'assignee', label: 'By assignee' },
  ]);

  // All available columns (for settings)
  readonly allColumns = computed<StatusColumn[]>(() => {
    return [
      {
        status: 'todo',
        label: this.translateService.instant('issues.status.todo'),
        issues: [],
        visible: true,
      },
      {
        status: 'in_progress',
        label: this.translateService.instant('issues.status.inProgress'),
        issues: [],
        visible: true,
      },
      {
        status: 'done',
        label: this.translateService.instant('issues.status.done'),
        issues: [],
        visible: true,
      },
      {
        status: 'cancelled',
        label: this.translateService.instant('issues.status.cancelled'),
        issues: [],
        visible: true,
      },
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
    const error = this.boardIssuesError();
    if (error) {
      return error instanceof Error
        ? error.message
        : this.translateService.instant('issues.failedToLoad');
    }
    return this.translateService.instant('common.unknownError');
  });

  // Issues are now automatically loaded when URL organizationId and projectId change
  // No need for manual initialization effect

  private async loadBoardIssues(boardId: string): Promise<void> {
    this.isLoadingBoardIssues.set(true);
    this.boardIssuesError.set(null);
    try {
      const response = await this.boardService.getBoardIssues(boardId);
      this.boardIssuesResponse.set(response);
      this.swimlaneTypeModel.set(response.swimlane_type || 'none');

      const lists = this.extractLists(response);
      this.boardIssueLists.set(lists);

      const issueListMap = new Map<string, string>();
      for (const list of lists) {
        for (const issue of list.issues) {
          if (!issueListMap.has(issue.id)) {
            issueListMap.set(issue.id, list.id);
          }
        }
      }
      this.issueListMap.set(issueListMap);
    } catch (error) {
      this.boardIssuesError.set(error);
      this.boardIssuesResponse.set(null);
      this.boardIssueLists.set([]);
      this.issueListMap.set(new Map());
    } finally {
      this.isLoadingBoardIssues.set(false);
    }
  }

  private extractLists(response: BoardIssuesResponse): BoardListWithIssuesResponse[] {
    const sourceLists =
      response.swimlane_type === 'none'
        ? response.lists
        : response.swimlanes.flatMap((swimlane) => swimlane.lists);
    const uniqueListMap = new Map<string, BoardListWithIssuesResponse>();
    for (const list of sourceLists) {
      if (!uniqueListMap.has(list.id)) {
        uniqueListMap.set(list.id, list);
      }
    }
    return Array.from(uniqueListMap.values()).sort((a, b) => a.position - b.position);
  }

  private mapBoardIssueToIssueListItem(issue: BoardIssueItemResponse): IssueListItem {
    const labelsById = new Map(this.projectLabels().map((label) => [label.id, label]));
    return {
      id: issue.id,
      project_id: issue.project_id,
      issue_number: issue.issue_number,
      key: issue.key,
      project_key: issue.project_key,
      title: issue.title,
      type: this.normalizeIssueType(issue.type),
      status: this.normalizeIssueStatus(issue.status),
      priority: this.normalizeIssuePriority(issue.priority),
      assignee_id: issue.assignee_id ?? undefined,
      story_points: issue.story_points ?? undefined,
      labels: (issue.label_ids || []).map((id) => {
        const label = labelsById.get(id);
        return {
          id,
          name: label?.name || id.slice(0, 6),
          color: label?.color || '#64748B',
        };
      }),
      comment_count: issue.comment_count,
      subtask_count: issue.subtask_count,
      created_at: '',
      updated_at: '',
    };
  }

  private normalizeIssueStatus(value: string): IssueStatus {
    const allowed: IssueStatus[] = ['todo', 'in_progress', 'done', 'cancelled'];
    return allowed.includes(value as IssueStatus) ? (value as IssueStatus) : 'todo';
  }

  private normalizeIssueType(value: string): 'task' | 'bug' | 'story' | 'epic' {
    const allowed = ['task', 'bug', 'story', 'epic'] as const;
    return allowed.includes(value as (typeof allowed)[number])
      ? (value as (typeof allowed)[number])
      : 'task';
  }

  private normalizeIssuePriority(value: string): 'low' | 'medium' | 'high' | 'critical' {
    const allowed = ['low', 'medium', 'high', 'critical'] as const;
    return allowed.includes(value as (typeof allowed)[number])
      ? (value as (typeof allowed)[number])
      : 'medium';
  }

  private resolveTargetListId(newStatus: IssueStatus, sourceListId?: string): string | undefined {
    const lists = this.boardIssueLists();
    const statusAliases: Record<IssueStatus, string[]> = {
      todo: ['todo', 'to_do', 'to-do', 'backlog'],
      in_progress: ['in_progress', 'in-progress', 'inprogress', 'doing'],
      done: ['done', 'closed', 'complete', 'completed'],
      cancelled: ['cancelled', 'canceled'],
    };

    const target = lists.find((list) => {
      const config = (list.list_config ?? {}) as Record<string, unknown>;
      const candidates = [
        config['status'],
        config['issue_status'],
        config['column_status'],
        config['name'],
        config['title'],
      ]
        .filter((value): value is string => typeof value === 'string')
        .map((value) => value.toLowerCase().replace(/\s+/g, '_'));

      return candidates.some((candidate) => statusAliases[newStatus].includes(candidate));
    });

    return target?.id ?? sourceListId ?? lists[0]?.id;
  }

  async handleDrop(event: CdkDragDrop<IssueListItem[]>, newStatus: IssueStatus): Promise<void> {
    const previousContainer = event.previousContainer;
    const currentContainer = event.container;
    const movedIssue = previousContainer.data[event.previousIndex];

    if (previousContainer === currentContainer) {
      // Reorder within same status column (frontend-only for now)
      moveItemInArray(currentContainer.data, event.previousIndex, event.currentIndex);
    } else {
      transferArrayItem(
        previousContainer.data,
        currentContainer.data,
        event.previousIndex,
        event.currentIndex,
      );

      if (movedIssue) {
        try {
          const boardId = this.boardId();
          const sourceListId = this.issueListMap().get(movedIssue.id);
          const targetListId = this.resolveTargetListId(newStatus, sourceListId);

          if (!sourceListId || !targetListId) {
            throw new Error('Unable to resolve board lists for move');
          }

          await this.boardService.moveBoardIssue(boardId, movedIssue.id, {
            source_list_id: sourceListId,
            target_list_id: targetListId,
          });

          await this.loadBoardIssues(boardId);
        } catch {
          this.toast.error(this.translateService.instant('issues.updateStatusError'));

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

  handleEditIssue(event: Event, issue: IssueListItem): void {
    event.stopPropagation();
    // Navigate to issue detail page (same as clicking the card)
    this.handleIssueClick(issue);
  }

  handleIssueClick(issue: IssueListItem): void {
    const orgId = this.organizationId();
    const projectId = this.projectId();
    if (orgId && projectId) {
      this.navigationService.navigateToIssue(orgId, projectId, issue.id);
    }
  }

  handleRetry(): void {
    const boardId = this.boardId();
    if (!boardId) return;
    this.loadBoardIssues(boardId);
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
      todo: this.translateService.instant('issues.status.todo'),
      in_progress: this.translateService.instant('issues.status.inProgress'),
      done: this.translateService.instant('issues.status.done'),
      cancelled: this.translateService.instant('issues.status.cancelled'),
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
    this.swimlaneTypeModel.set('none');
    void this.handleSwimlaneChange('none');
    dropdown.open.set(false);
  }

  async handleSwimlaneChange(swimlaneType: 'none' | 'epic' | 'assignee'): Promise<void> {
    const boardId = this.boardId();
    if (!boardId) return;
    try {
      await this.boardService.updateBoardSwimlanes(boardId, { swimlane_type: swimlaneType });
      await this.loadBoardIssues(boardId);
    } catch {
      this.toast.error('Failed to update swimlane');
    }
  }

  private async loadProjectLabels(projectId: string): Promise<void> {
    try {
      const response = await this.labelService.listProjectLabels(projectId, {
        page: 1,
        limit: 200,
      });
      this.projectLabels.set(response.labels || []);
    } catch {
      this.projectLabels.set([]);
    }
  }

  private async applyScope(
    boardId: string,
    assignee: string | null,
    type: 'task' | 'bug' | 'story' | 'epic' | null,
    priority: 'low' | 'medium' | 'high' | 'critical' | null,
  ): Promise<void> {
    if (this.isApplyingScope()) return;
    this.isApplyingScope.set(true);
    try {
      await this.boardService.updateBoardScope(boardId, {
        assignee_id: assignee || undefined,
        types: type ? [type] : undefined,
        priorities: priority ? [priority] : undefined,
      });
      await this.loadBoardIssues(boardId);
    } catch {
      this.toast.error('Failed to apply board scope');
    } finally {
      this.isApplyingScope.set(false);
    }
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

  getColumnColorClass(status: IssueStatus): string {
    const colorMap: Record<IssueStatus, string> = {
      todo: 'text-muted-foreground',
      in_progress: 'text-amber-500',
      done: 'text-green-500',
      cancelled: 'text-muted-foreground',
    };
    return colorMap[status];
  }

  getAssignee(assigneeId: string | undefined): ProjectMember | undefined {
    if (!assigneeId) return undefined;
    return this.projectMembers().find((member) => member.user_id === assigneeId);
  }

  getInitials(name: string): string {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  }
}
