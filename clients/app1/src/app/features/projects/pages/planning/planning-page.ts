import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  signal,
  effect,
  DestroyRef,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { Subject } from 'rxjs';
import { CommonModule } from '@angular/common';
import {
  CdkDragDrop,
  DragDropModule,
  moveItemInArray,
  transferArrayItem,
} from '@angular/cdk/drag-drop';
import {
  Button,
  LoadingState,
  ErrorState,
  Badge,
  ToastService,
  Input,
  Pagination,
} from 'shared-ui';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { SprintService, Sprint } from '../../../../application/services/sprint.service';
import { IssueService, IssueListItem } from '../../../../application/services/issue.service';
import { IssueCard } from '../../../../shared/components/issue-card';
import { PageFooter } from '../../../../shared/layout/page-footer/page-footer';
import { NavigationService } from '../../../../application/services/navigation.service';

@Component({
  selector: 'app-planning-page',
  standalone: true,
  imports: [
    CommonModule,
    LoadingState,
    ErrorState,
    Badge,
    Button,
    Input,
    Pagination,
    DragDropModule,
    IssueCard,
    TranslatePipe,
    PageFooter,
  ],
  template: `
    @if (isLoading()) {
      <lib-loading-state [message]="'sprints.planning.loading' | translate" />
    } @else if (hasError()) {
      <lib-error-state
        [title]="'sprints.planning.failedToLoad' | translate"
        [message]="errorMessage()"
        [retryLabel]="'common.retry' | translate"
        (onRetry)="loadData()"
      />
    } @else {
      <div class="planning-page_content">
        <!-- Two Column Layout: Backlog | Sprint -->
        <div class="planning-page_grid">
          <!-- Backlog Panel -->
          <div
            class="planning-page_panel"
            cdkDropList
            id="backlogList"
            #backlogList="cdkDropList"
            [cdkDropListData]="backlogIssues()"
            [cdkDropListConnectedTo]="[sprintList]"
            (cdkDropListDropped)="handleDrop($event, 'backlog')"
            (cdkDropListEntered)="dragOverBacklog.set(true)"
            (cdkDropListExited)="dragOverBacklog.set(false)"
            [class.planning-page_panel--drag-over]="dragOverBacklog()"
          >
            <div class="planning-page_panel-header">
              <div class="planning-page_panel-title">
                <h3>{{ 'backlog.title' | translate }}</h3>
                <lib-badge variant="default">
                  {{ backlogIssues().length }} {{ 'backlog.issues' | translate }} •
                  {{ backlogPoints() }} {{ 'backlog.points' | translate }}
                </lib-badge>
              </div>
              <p class="planning-page_panel-placeholder">{{ ' ' }}</p>
              <div class="planning-page_panel-search">
                <lib-input
                  [placeholder]="'sprints.planning.searchBacklog' | translate"
                  [(model)]="backlogSearch"
                  (modelChange)="handleBacklogSearchChange($event)"
                  [size]="'sm'"
                  [leftAction]="{ icon: 'search' }"
                />
              </div>
            </div>
            <div class="planning-page_panel-content">
              <div class="planning-page_content-wrapper">
                @if (paginatedBacklogIssues().length > 0) {
                  <div class="planning-page_issues-grid">
                    @for (issue of paginatedBacklogIssues(); track issue.id) {
                      <div cdkDrag [cdkDragData]="issue" class="planning-page_issue-wrapper">
                        <div class="planning-page_issue-content">
                          <app-issue-card
                            [issue]="issue"
                            [assignee]="getAssignee(issue)"
                            [showStoryPoints]="true"
                            (onClick)="handleIssueClick($event)"
                          />
                          <lib-button
                            variant="ghost"
                            size="sm"
                            [iconOnly]="true"
                            leftIcon="arrow-right"
                            class="planning-page_issue-action"
                            (clicked)="handleMoveToSprint(issue.id)"
                            [disabled]="!selectedSprint()"
                          />
                        </div>
                      </div>
                    }
                  </div>
                } @else {
                  <div class="planning-page_empty">
                    {{
                      backlogSearch()
                        ? ('sprints.planning.noMatchingIssues' | translate)
                        : ('backlog.noItems' | translate)
                    }}
                  </div>
                }
              </div>
              <app-page-footer>
                <lib-pagination
                  [currentPage]="backlogPage()"
                  [totalItems]="backlogTotal()"
                  [itemsPerPage]="ITEMS_PER_PAGE"
                  [itemLabel]="'backlog.issues' | translate"
                  (pageChange)="backlogPage.set($event)"
                />
              </app-page-footer>
            </div>
          </div>

          <!-- Sprint Panel -->
          <div
            class="planning-page_panel"
            cdkDropList
            id="sprintList"
            #sprintList="cdkDropList"
            [cdkDropListData]="sprintIssues()"
            [cdkDropListConnectedTo]="[backlogList]"
            (cdkDropListDropped)="handleDrop($event, 'sprint')"
            (cdkDropListEntered)="dragOverSprint.set(true)"
            (cdkDropListExited)="dragOverSprint.set(false)"
            [class.planning-page_panel--drag-over]="dragOverSprint()"
          >
            <div class="planning-page_panel-header">
              <div class="planning-page_panel-title">
                <h3>
                  {{ selectedSprint()?.name || ('sprints.planning.selectSprint' | translate) }}
                </h3>
                <lib-badge variant="default">
                  {{ sprintTotal() }} {{ 'backlog.issues' | translate }} • {{ sprintPoints() }}
                  {{ 'backlog.points' | translate }}
                </lib-badge>
              </div>
              <p class="planning-page_panel-goal">
                {{
                  selectedSprint()?.goal
                    ? ('sprints.goal' | translate) + ': ' + selectedSprint()?.goal
                    : ' '
                }}
              </p>
              <div class="planning-page_panel-search">
                <lib-input
                  [placeholder]="'sprints.planning.searchSprint' | translate"
                  [(model)]="sprintSearch"
                  (modelChange)="handleSprintSearchChange($event)"
                  [size]="'sm'"
                  [leftAction]="{ icon: 'search' }"
                />
              </div>
            </div>
            <div class="planning-page_panel-content">
              <div class="planning-page_content-wrapper">
                @if (isLoadingSprintIssues()) {
                  <div class="planning-page_loading">
                    <lib-loading-state [message]="'sprints.planning.loadingIssues' | translate" />
                  </div>
                } @else if (paginatedSprintIssues().length > 0) {
                  <div class="planning-page_issues-grid">
                    @for (issue of paginatedSprintIssues(); track issue.id) {
                      <div cdkDrag [cdkDragData]="issue" class="planning-page_issue-wrapper">
                        <app-issue-card
                          [issue]="issue"
                          [assignee]="getAssignee(issue)"
                          [showStoryPoints]="true"
                          (onClick)="handleIssueClick($event)"
                        />
                      </div>
                    }
                  </div>
                } @else {
                  <div class="planning-page_empty">
                    {{
                      sprintSearch()
                        ? ('sprints.planning.noMatchingIssues' | translate)
                        : selectedSprint()
                          ? ('sprints.planning.dragIssuesHere' | translate)
                          : ('sprints.planning.selectSprintToStart' | translate)
                    }}
                  </div>
                }
              </div>
              <app-page-footer>
                <lib-pagination
                  [currentPage]="sprintPage()"
                  [totalItems]="sprintTotal()"
                  [itemsPerPage]="ITEMS_PER_PAGE"
                  [itemLabel]="'backlog.issues' | translate"
                  (pageChange)="sprintPage.set($event)"
                />
              </app-page-footer>
            </div>
          </div>
        </div>
      </div>
    }
  `,
  styles: [
    `
      @reference "#mainstyles";

      :host {
        @apply block;
        @apply w-full;
        @apply h-full;
        @apply flex-1;
        @apply min-h-0;
        @apply flex flex-col;
      }

      .planning-page_content {
        @apply flex flex-col;
        @apply flex-1;
        @apply min-h-0;
        @apply w-full;
      }

      .planning-page_grid {
        @apply grid grid-cols-1 lg:grid-cols-2;
        @apply gap-6;
        @apply flex-1;
        @apply min-h-0;
        @apply w-full;
      }

      .planning-page_panel {
        @apply flex flex-col;
        @apply rounded-lg;
        @apply border;
        @apply border-border;
        @apply bg-card;
        @apply shadow-sm;
        @apply min-h-0;
        @apply h-full;
        @apply transition-all;
      }

      .planning-page_panel--drag-over {
        @apply ring-2;
        @apply ring-primary;
        @apply ring-offset-2;
      }

      .planning-page_panel-header {
        @apply flex flex-col;
        @apply gap-2;
        @apply p-4;
        @apply border-b;
        @apply border-border;
        height: 120px;
        flex-shrink: 0;
      }

      .planning-page_panel-title {
        @apply flex items-center justify-between;
        @apply gap-2;
      }

      .planning-page_panel-title h3 {
        @apply text-lg font-semibold;
        @apply text-foreground;
        margin: 0;
      }

      .planning-page_panel-goal {
        @apply text-sm;
        @apply text-muted-foreground;
        @apply truncate;
        margin: 0;
      }

      .planning-page_panel-placeholder {
        @apply text-sm;
        @apply text-muted-foreground;
        @apply invisible;
        margin: 0;
      }

      .planning-page_panel-search {
        @apply mt-3;
      }

      .planning-page_panel-content {
        @apply flex-1;
        @apply flex flex-col;
        @apply overflow-auto;
        @apply p-4;
        @apply min-h-0;
      }

      .planning-page_content-wrapper {
        @apply flex-1;
        @apply flex flex-col;
        @apply min-h-0;
      }

      .planning-page_issues-grid {
        @apply grid grid-cols-2;
        @apply gap-3;
        @apply flex-1;
        @apply content-start;
      }

      .planning-page_issue-wrapper {
        @apply relative;
        @apply w-full;
      }

      .planning-page_issue-wrapper:hover .planning-page_issue-action {
        opacity: 1;
      }

      .planning-page_issue-content {
        @apply flex items-center;
        @apply gap-2;
        @apply w-full;
      }

      .planning-page_issue-content app-issue-card {
        @apply flex-1;
        @apply min-w-0;
      }

      .planning-page_issue-action {
        @apply opacity-0;
        @apply transition-opacity;
      }

      .planning-page_empty {
        @apply text-center;
        @apply py-12;
        @apply text-sm;
        @apply text-muted-foreground;
        @apply flex-1;
        @apply flex items-center justify-center;
      }

      .planning-page_loading {
        @apply flex-1;
        @apply flex items-center justify-center;
        @apply min-h-0;
      }

      .cdk-drag-preview {
        @apply opacity-50;
        @apply rotate-2;
        @apply shadow-lg;
      }

      .cdk-drag-placeholder {
        @apply opacity-30;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PlanningPage {
  private readonly sprintService = inject(SprintService);
  private readonly issueService = inject(IssueService);
  private readonly navigationService = inject(NavigationService);
  private readonly translateService = inject(TranslateService);
  private readonly toast = inject(ToastService);

  readonly isLoading = signal(false);
  readonly hasError = signal(false);
  readonly errorMessage = signal<string>('');
  readonly dragOverBacklog = signal(false);
  readonly dragOverSprint = signal(false);

  readonly selectedSprint = computed(() => this.sprintService.currentSprint());

  // Search and pagination state
  readonly backlogSearch = signal('');
  readonly sprintSearch = signal('');
  readonly backlogPage = signal(1);
  readonly sprintPage = signal(1);

  readonly ITEMS_PER_PAGE = 10;

  // Track previous sprint ID to detect actual changes
  private previousSprintId: string | null = null;

  // Backlog issues - loaded separately via backlog API
  readonly backlogIssues = signal<IssueListItem[]>([]);
  readonly backlogTotal = signal(0);

  // Sprint issues - loaded via issue service with sprint filter
  readonly sprintIssues = signal<IssueListItem[]>([]);
  readonly sprintTotal = signal(0);

  // Debounced search subjects
  private readonly backlogSearchSubject = new Subject<string>();
  private readonly sprintSearchSubject = new Subject<string>();

  // Paginated backlog issues (already paginated from API)
  readonly paginatedBacklogIssues = computed(() => this.backlogIssues());

  // Paginated sprint issues (already paginated from API)
  readonly paginatedSprintIssues = computed(() => this.sprintIssues());

  readonly backlogTotalPages = computed(() => {
    return Math.ceil(this.backlogTotal() / this.ITEMS_PER_PAGE);
  });

  readonly sprintTotalPages = computed(() => {
    return Math.ceil(this.sprintTotal() / this.ITEMS_PER_PAGE);
  });

  readonly backlogPoints = computed(() => {
    return this.backlogIssues().reduce((sum, issue) => sum + (issue.story_points || 0), 0);
  });

  readonly sprintPoints = computed(() => {
    return this.sprintIssues().reduce((sum, issue) => sum + (issue.story_points || 0), 0);
  });

  // Loading state for sprint issues
  readonly isLoadingSprintIssues = computed(() => {
    const sprint = this.selectedSprint();
    if (!sprint) return false;

    const filters = this.issueService.currentFilters();
    // Only show loading if we're loading issues for the current sprint
    return this.issueService.isLoading() && filters.sprint_id === sprint.id;
  });

  private readonly destroyRef = inject(DestroyRef);

  constructor() {
    // Setup debounced search for backlog
    this.backlogSearchSubject
      .pipe(debounceTime(300), distinctUntilChanged(), takeUntilDestroyed(this.destroyRef))
      .subscribe((search) => {
        this.backlogPage.set(1);
        this.loadBacklogIssues();
      });

    // Setup debounced search for sprint
    this.sprintSearchSubject
      .pipe(debounceTime(300), distinctUntilChanged(), takeUntilDestroyed(this.destroyRef))
      .subscribe((search) => {
        this.sprintPage.set(1);
        this.loadSprintIssues();
      });

    // Watch for backlog page changes - only reload backlog
    effect(() => {
      const backlogPage = this.backlogPage();
      // Only reload backlog when page changes
      this.loadBacklogIssues();
    });

    // Watch for sprint page changes - only reload sprint
    effect(() => {
      const sprint = this.selectedSprint();
      const sprintPage = this.sprintPage();

      if (sprint) {
        // Only reload sprint when page changes
        this.loadSprintIssues();
      }
    });

    // Watch for sprint selection changes - reload both to update counts
    effect(() => {
      const sprint = this.selectedSprint();
      const currentSprintId = sprint?.id || null;

      // Only reload if sprint actually changed (not just accessed)
      if (currentSprintId !== this.previousSprintId) {
        this.previousSprintId = currentSprintId;

        if (sprint) {
          // When sprint changes, reload both to update counts
          this.loadSprintIssues();
          this.loadBacklogIssues();
        } else {
          // Clear sprint issues when no sprint is selected
          this.sprintIssues.set([]);
          this.sprintTotal.set(0);
        }
      }
    });

    // Watch for issue service updates and sync sprint issues
    effect(() => {
      const sprint = this.selectedSprint();
      if (!sprint) {
        this.sprintIssues.set([]);
        this.sprintTotal.set(0);
        return;
      }

      // Check if the issue service has the right filters
      const filters = this.issueService.currentFilters();
      const issuesList = this.issueService.issuesList();
      const issuesTotal = this.issueService.issuesTotal();

      if (filters.sprint_id === sprint.id) {
        this.sprintIssues.set(issuesList);
        this.sprintTotal.set(issuesTotal);
      }
    });

    // Initial load
    this.loadData();
  }

  async loadData(): Promise<void> {
    this.isLoading.set(true);
    this.hasError.set(false);
    this.errorMessage.set('');

    try {
      await this.loadBacklogIssues();
      // Sprint issues are loaded automatically when sprint is selected
      // via the issue service
    } catch (error) {
      console.error('Failed to load planning data:', error);
      this.hasError.set(true);
      this.errorMessage.set(
        error instanceof Error
          ? error.message
          : this.translateService.instant('sprints.planning.failedToLoad'),
      );
    } finally {
      this.isLoading.set(false);
    }
  }

  async loadBacklogIssues(): Promise<void> {
    const projectId = this.navigationService.currentProjectId();
    if (!projectId) return;

    try {
      const search = this.backlogSearch().trim() || undefined;
      const response = await this.issueService.getBacklogIssues(
        projectId,
        this.backlogPage(),
        this.ITEMS_PER_PAGE,
        search,
      );
      this.backlogIssues.set(response.issues);
      this.backlogTotal.set(response.total);
    } catch (error) {
      console.error('Failed to load backlog issues:', error);
      throw error;
    }
  }

  async loadSprintIssues(): Promise<void> {
    const sprint = this.selectedSprint();
    if (!sprint) {
      this.sprintIssues.set([]);
      this.sprintTotal.set(0);
      return;
    }

    const projectId = this.navigationService.currentProjectId();
    if (!projectId) return;

    try {
      const search = this.sprintSearch().trim() || undefined;
      const page = this.sprintPage();

      // Use issue service with sprint_id filter, search, and pagination
      this.issueService.setFilters({
        sprint_id: sprint.id,
        search: search,
        page: page,
        limit: this.ITEMS_PER_PAGE,
      });

      // Trigger reload - the effect will pick up the changes
      this.issueService.loadIssues();
    } catch (error) {
      console.error('Failed to load sprint issues:', error);
      throw error;
    }
  }

  handleDrop(event: CdkDragDrop<IssueListItem[]>, target: 'backlog' | 'sprint'): void {
    // Reset drag-over states
    this.dragOverBacklog.set(false);
    this.dragOverSprint.set(false);

    const issue = event.item.data as IssueListItem;
    if (!issue || !issue.id) {
      console.error('Invalid issue data in drop event');
      return;
    }

    // Determine source by checking container ID (using explicit IDs we set)
    const previousContainerId = event.previousContainer.id;
    const source = previousContainerId === 'backlogList' ? 'backlog' : 'sprint';

    if (source === target) {
      // Reordering within the same list
      if (event.previousIndex !== event.currentIndex) {
        moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
        // TODO: Implement reordering API call if needed
      }
      return;
    }

    // Moving between lists
    if (target === 'sprint') {
      this.handleMoveToSprint(issue.id);
    } else {
      this.handleMoveToBacklog(issue.id);
    }
  }

  async handleMoveToSprint(issueId: string): Promise<void> {
    const sprint = this.selectedSprint();
    if (!sprint) {
      this.toast.error(this.translateService.instant('sprints.planning.noSprintSelected'));
      return;
    }

    try {
      await this.sprintService.addIssueToSprint(sprint.id, issueId);
      // Reload both backlog and sprint issues to reflect the changes
      await Promise.all([this.loadBacklogIssues(), this.loadSprintIssues()]);
      this.toast.success(this.translateService.instant('sprints.planning.issueAddedToSprint'));
    } catch (error) {
      console.error('Failed to add issue to sprint:', error);
      this.toast.error(
        error instanceof Error
          ? error.message
          : this.translateService.instant('sprints.planning.failedToAddIssue'),
      );
    }
  }

  async handleMoveToBacklog(issueId: string): Promise<void> {
    const sprint = this.selectedSprint();
    if (!sprint) {
      return;
    }

    try {
      await this.sprintService.removeIssueFromSprint(sprint.id, issueId);
      // Reload both backlog and sprint issues to reflect the changes
      await Promise.all([this.loadBacklogIssues(), this.loadSprintIssues()]);
      this.toast.success(this.translateService.instant('sprints.planning.issueRemovedFromSprint'));
    } catch (error) {
      console.error('Failed to remove issue from sprint:', error);
      this.toast.error(
        error instanceof Error
          ? error.message
          : this.translateService.instant('sprints.planning.failedToRemoveIssue'),
      );
    }
  }

  handleIssueClick(issue: IssueListItem): void {
    const orgId = this.navigationService.currentOrganizationId();
    const projectId = this.navigationService.currentProjectId();
    if (orgId && projectId) {
      this.navigationService.navigateToIssue(orgId, projectId, issue.id);
    }
  }

  getAssignee(issue: IssueListItem): { user_name: string; avatar_url?: string } | null {
    // TODO: Get assignee data from project members service
    // For now, return null
    return null;
  }

  handleBacklogSearchChange(value: string): void {
    this.backlogSearch.set(value);
    this.backlogSearchSubject.next(value);
  }

  handleSprintSearchChange(value: string): void {
    this.sprintSearch.set(value);
    this.sprintSearchSubject.next(value);
  }
}
