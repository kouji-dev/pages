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
  EmptyState,
  Modal,
  ToastService,
  Select,
  SelectOption,
  Badge,
  Input,
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
import { CreateLabelModal, CreateLabelModalResult } from '../create-label-modal/create-label-modal';
import { AddBoardColumnModal } from '../add-board-column-modal/add-board-column-modal';
import { IssueCard } from '../../../../shared/components/issue-card';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { firstValueFrom } from 'rxjs';

type IssueStatus = 'todo' | 'in_progress' | 'done' | 'cancelled';

interface BoardColumn {
  id: string;
  title: string;
  issues: IssueListItem[];
  listType: string;
  position: number;
}

/** Column with optional client-side search filter applied to `issues`. */
interface BoardColumnView extends BoardColumn {
  fullIssueCount: number;
  columnSearchActive: boolean;
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
    EmptyState,
    Select,
    TranslatePipe,
    Badge,
    Input,
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
          @if (showNoLabelsMessage()) {
            <div class="kanban-board_no-labels">
              <lib-empty-state
                title="No labels yet"
                message="Create your first label directly from this board."
                icon="tag"
                actionLabel="Create Label"
                actionIcon="plus"
                (onAction)="handleCreateLabelFromEmptyState()"
              />
            </div>
          }
          <div class="kanban-board_columns" cdkDropListGroup>
            @for (column of visibleColumns(); track column.id) {
              <div
                class="kanban-board_column"
                cdkDropList
                [cdkDropListData]="column.issues"
                [cdkDropListDisabled]="boardHasColumnSearch()"
                (cdkDropListDropped)="handleDrop($event, column.id)"
              >
                <div class="kanban-board_column-header">
                  <div class="kanban-board_column-header-left">
                    <span class="kanban-board_column-title">
                      {{ column.title }}
                    </span>
                    <lib-badge variant="default" class="kanban-board_column-badge">
                      @if (column.columnSearchActive) {
                        {{ column.issues.length }} / {{ column.fullIssueCount }}
                      } @else {
                        {{ column.issues.length }}
                      }
                    </lib-badge>
                  </div>
                  <div class="kanban-board_column-header-actions">
                    <lib-button
                      variant="ghost"
                      size="sm"
                      [iconOnly]="true"
                      leftIcon="plus"
                      class="kanban-board_column-action"
                      (clicked)="handleAddColumn()"
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
                <div class="kanban-board_column-search">
                  <lib-input
                    type="search"
                    size="sm"
                    [placeholder]="'board.columnSearchPlaceholder' | translate"
                    [model]="columnSearchQueries()[column.id] || ''"
                    (modelChange)="onColumnSearchChange(column.id, $event)"
                    [leftAction]="{ icon: 'search' }"
                  />
                </div>
                <div class="kanban-board_column-content">
                  @for (issue of column.issues; track issue.id) {
                    <div cdkDrag [cdkDragDisabled]="boardHasColumnSearch()">
                      <app-issue-card
                        [issue]="issue"
                        [assignee]="getAssignee(issue.assignee_id) || null"
                        (onClick)="handleIssueClick($event)"
                      />
                    </div>
                  }
                  @if (column.issues.length === 0) {
                    <div class="kanban-board_empty">
                      @if (column.columnSearchActive) {
                        {{ 'board.noIssuesMatchSearch' | translate }}
                      } @else {
                        {{ 'board.noIssues' | translate }}
                      }
                    </div>
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

      :host {
        @apply flex flex-1 min-h-0 w-full flex-col;
      }

      .kanban-board {
        @apply flex flex-1 min-h-0 w-full flex-col gap-4;
      }

      .kanban-board_header {
        @apply flex flex-shrink-0 items-center justify-end gap-4;
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
        @apply flex flex-1 min-h-0 w-full flex-col overflow-hidden;
      }

      /* Fills remaining height below header; columns stretch to this height (max = board body) */
      .kanban-board_columns {
        @apply flex flex-1 min-h-0 min-w-0 flex-row items-stretch gap-4 overflow-x-auto pb-4;
      }

      .kanban-board_no-labels {
        @apply w-full mb-4;
      }

      .kanban-board_column {
        @apply flex w-[360px] min-w-[360px] max-h-full flex-shrink-0 flex-col min-h-0 border border-border rounded-lg p-4;
      }

      .kanban-board_column-header {
        @apply mb-3 flex flex-shrink-0 items-center justify-between;
      }

      .kanban-board_column-search {
        @apply mb-3 w-full min-w-0 flex-shrink-0;
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

      /* Grows within column up to remaining height; scrolls when issues overflow */
      .kanban-board_column-content {
        /* Inline-end padding so the scrollbar/track sits farther from issue cards */
        @apply flex flex-1 min-h-0 flex-col gap-3 overflow-y-auto overflow-x-hidden pe-4;
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
  readonly showNoLabelsMessage = computed(() => this.projectLabels().length === 0);

  readonly organizationId = computed(() => {
    return this.navigationService.currentOrganizationId() || '';
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

  /** Per-column client-side search (title, description, labels, type, priority, key, assignee, …) */
  readonly columnSearchQueries = signal<Record<string, string>>({});

  /** Drag-and-drop is disabled while any column search is active (filtered lists break CDK indices). */
  readonly boardHasColumnSearch = computed(() =>
    Object.values(this.columnSearchQueries()).some((v) => (v ?? '').trim().length > 0),
  );

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

  constructor() {
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

    effect(() => {
      this.boardId();
      this.columnSearchQueries.set({});
    });
  }

  readonly issues = computed<IssueListItem[]>(() => {
    const response = this.boardIssuesResponse();
    if (!response) return [];

    const uniqueIssues = new Map<string, IssueListItem>();
    const labelsById = new Map(this.projectLabels().map((label) => [label.id, label]));
    const lists =
      response.swimlane_type === 'none'
        ? response.lists
        : response.swimlanes.flatMap((swimlane) => swimlane.lists);

    for (const list of lists) {
      for (const issue of list.issues) {
        if (!uniqueIssues.has(issue.id)) {
          uniqueIssues.set(issue.id, this.mapBoardIssueToIssueListItem(issue, labelsById));
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

  readonly columns = computed<BoardColumn[]>(() => {
    const filteredIds = new Set(this.filteredIssues().map((issue) => issue.id));
    const labelsById = new Map(this.projectLabels().map((label) => [label.id, label]));
    return this.boardIssueLists()
      .slice()
      .sort((a, b) => a.position - b.position)
      .map((list) => {
        const issues = list.issues
          .map((issue) => this.mapBoardIssueToIssueListItem(issue, labelsById))
          .filter((issue) => filteredIds.has(issue.id));

        return {
          id: list.id,
          title: this.getBoardListTitle(list),
          issues,
          listType: list.list_type,
          position: list.position,
        };
      });
  });

  readonly visibleColumns = computed<BoardColumnView[]>(() => {
    const queries = this.columnSearchQueries();
    return this.columns().map((col) => {
      const raw = queries[col.id] ?? '';
      const q = raw.trim().toLowerCase();
      const columnSearchActive = q.length > 0;
      const fullIssueCount = col.issues.length;
      const issues = columnSearchActive
        ? col.issues.filter((issue) => this.issueMatchesColumnSearch(issue, q))
        : col.issues;
      return {
        ...col,
        issues,
        fullIssueCount,
        columnSearchActive,
      };
    });
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

      // Ensure newly created labels are mapped to label ids returned by board issues.
      await this.ensureLabelsMappedForBoard(response);
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

  private mapBoardIssueToIssueListItem(
    issue: BoardIssueItemResponse,
    labelsById: Map<string, Label>,
  ): IssueListItem {
    return {
      id: issue.id,
      project_id: issue.project_id,
      issue_number: issue.issue_number,
      key: issue.key,
      project_key: issue.project_key,
      title: issue.title,
      description: issue.description ?? undefined,
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

  async handleDrop(event: CdkDragDrop<IssueListItem[]>, targetListId: string): Promise<void> {
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
    void this.openCreateIssueModal();
  }

  handleAddColumn(): void {
    void this.openAddBoardColumnModal();
  }

  private async openAddBoardColumnModal(): Promise<void> {
    const projectId = this.projectId();
    const boardId = this.boardId();
    if (!projectId || !boardId) {
      return;
    }

    const created = await firstValueFrom(
      this.modal.open<boolean | null>(AddBoardColumnModal, this.viewContainerRef, {
        size: 'md',
        closable: true,
        data: {
          boardId,
          projectId,
          labels: this.projectLabels(),
          members: this.projectMembers(),
        },
      }),
    );

    if (created) {
      await this.loadBoardIssues(boardId);
    }
  }

  handleCreateLabelFromEmptyState(): void {
    void this.createLabelFromPopup();
  }

  private async createLabelFromPopup(): Promise<void> {
    const projectId = this.projectId();
    if (!projectId) {
      return;
    }

    const result = await firstValueFrom(
      this.modal.open<CreateLabelModalResult | null>(CreateLabelModal, this.viewContainerRef, {
        size: 'sm',
        data: {
          existingLabelNames: this.projectLabels().map((label) => label.name),
        },
      }),
    );

    if (!result) {
      return;
    }

    try {
      await this.labelService.createLabel(projectId, result);
      await this.loadProjectLabels(projectId);
      this.toast.success('Label created');
    } catch {
      this.toast.error('Failed to create label');
    }
  }

  private async openCreateIssueModal(): Promise<void> {
    const projectId = this.projectId();
    const boardId = this.boardId();

    await firstValueFrom(
      this.modal.open(CreateIssueModal, this.viewContainerRef, {
        size: 'md',
        closable: true,
        data: {
          projectId,
        },
      }),
    );

    if (projectId) {
      await this.loadProjectLabels(projectId);
    }
    if (boardId) {
      await this.loadBoardIssues(boardId);
    }
  }

  private async ensureLabelsMappedForBoard(response: BoardIssuesResponse): Promise<void> {
    const projectId = this.projectId();
    if (!projectId) {
      return;
    }

    const currentIds = new Set(this.projectLabels().map((label) => label.id));
    const boardLabelIds = new Set<string>();
    const lists =
      response.swimlane_type === 'none'
        ? response.lists
        : response.swimlanes.flatMap((swimlane) => swimlane.lists);

    for (const list of lists) {
      for (const issue of list.issues) {
        for (const labelId of issue.label_ids || []) {
          boardLabelIds.add(labelId);
        }
      }
    }

    const hasMissingMapping = Array.from(boardLabelIds).some((id) => !currentIds.has(id));
    if (hasMissingMapping) {
      await this.loadProjectLabels(projectId);
    }
  }

  resetSettings(dropdown: Dropdown): void {
    this.clearFilters(dropdown);
    this.swimlaneTypeModel.set('none');
    void this.handleSwimlaneChange('none');
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
        limit: 100,
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

  onColumnSearchChange(columnId: string, value: string): void {
    this.columnSearchQueries.update((prev) => ({ ...prev, [columnId]: value }));
  }

  private issueMatchesColumnSearch(issue: IssueListItem, qLower: string): boolean {
    const tokens = qLower.split(/\s+/).filter(Boolean);
    if (!tokens.length) return true;
    const haystack = this.buildIssueSearchHaystack(issue);
    return tokens.every((tok) => haystack.includes(tok));
  }

  private buildIssueSearchHaystack(issue: IssueListItem): string {
    const statusKey = this.issueStatusTranslationKey(issue.status);
    const statusLabel = this.translateService.instant(`issues.status.${statusKey}`);
    const typeLabel = this.translateService.instant(`issues.type.${issue.type}`);
    const priorityLabel = this.translateService.instant(`issues.priority.${issue.priority}`);
    const assignee = issue.assignee_id ? this.getAssignee(issue.assignee_id) : undefined;
    const assigneeName = assignee?.user_name ?? '';
    const labelNames = (issue.labels ?? []).map((l) => l.name).join(' ');
    const description = (issue.description ?? '').replace(/<[^>]+>/g, ' ');
    const parts = [
      issue.title,
      description,
      issue.key,
      issue.project_key,
      String(issue.issue_number),
      issue.type,
      issue.status,
      issue.priority,
      typeLabel,
      priorityLabel,
      statusLabel,
      assigneeName,
      labelNames,
      issue.story_points != null ? String(issue.story_points) : '',
    ];
    return parts.filter(Boolean).join(' ').toLowerCase();
  }

  private issueStatusTranslationKey(status: IssueListItem['status']): string {
    const map: Record<IssueListItem['status'], string> = {
      todo: 'todo',
      in_progress: 'inProgress',
      done: 'done',
      cancelled: 'cancelled',
    };
    return map[status];
  }

  private getBoardListTitle(list: BoardListWithIssuesResponse): string {
    const config = (list.list_config ?? {}) as Record<string, unknown>;
    const explicitTitle =
      (typeof config['title'] === 'string' && config['title']) ||
      (typeof config['name'] === 'string' && config['name']) ||
      (typeof config['status'] === 'string' && config['status']);

    if (explicitTitle) {
      return explicitTitle;
    }

    return `${list.list_type} ${list.position + 1}`;
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
