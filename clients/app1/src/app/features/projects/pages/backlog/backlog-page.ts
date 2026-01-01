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
  Button,
  LoadingState,
  ErrorState,
  Badge,
  ToastService,
  Input,
  Pagination,
  Select,
  SelectOption,
  Icon,
} from 'shared-ui';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { IssueService, IssueListItem } from '../../../../application/services/issue.service';
import { IssueCard } from '../../../../shared/components/issue-card';
import { NavigationService } from '../../../../application/services/navigation.service';

const ITEMS_PER_PAGE = 20;

@Component({
  selector: 'app-backlog-page',
  standalone: true,
  imports: [
    CommonModule,
    LoadingState,
    ErrorState,
    Badge,
    Button,
    Input,
    Pagination,
    Select,
    Icon,
    IssueCard,
    TranslatePipe,
  ],
  template: `
    <div class="backlog-page">
      @if (isLoading()) {
        <lib-loading-state [message]="'backlog.loading' | translate" />
      } @else if (hasError()) {
        <lib-error-state
          [title]="'backlog.failedToLoad' | translate"
          [message]="errorMessage()"
          [retryLabel]="'common.retry' | translate"
          (onRetry)="loadBacklogIssues()"
        />
      } @else {
        <div class="backlog-page_content">
          <!-- Header with stats and Add Issue button -->
          <div class="backlog-page_header">
            <lib-badge variant="default" class="backlog-page_stats">
              {{ backlogDisplayCount() }} {{ 'backlog.issues' | translate }} • {{ backlogPoints() }}
              {{ 'backlog.points' | translate }}
            </lib-badge>
            <lib-button
              variant="primary"
              size="md"
              (clicked)="handleCreateIssue()"
              class="backlog-page_add-button"
            >
              <lib-icon name="plus" [size]="'xs'" />
              {{ 'backlog.addIssue' | translate }}
            </lib-button>
          </div>

          <!-- Filters -->
          <div class="backlog-page_filters">
            <div class="backlog-page_search">
              <lib-input
                [placeholder]="'backlog.searchPlaceholder' | translate"
                [(model)]="search"
                (modelChange)="handleSearchChange($event)"
                [size]="'sm'"
                [leftAction]="{ icon: 'search' }"
              />
            </div>
            <lib-select
              [(model)]="statusFilter"
              [options]="statusOptions()"
              [placeholder]="'backlog.statusFilter' | translate"
              [size]="'sm'"
              class="backlog-page_filter-select"
            />
            <lib-select
              [(model)]="priorityFilter"
              [options]="priorityOptions()"
              [placeholder]="'backlog.priorityFilter' | translate"
              [size]="'sm'"
              class="backlog-page_filter-select"
            />
          </div>

          <!-- Issues Grid -->
          @if (paginatedBacklogIssues().length > 0) {
            <div class="backlog-page_issues-grid">
              @for (issue of paginatedBacklogIssues(); track issue.id) {
                <div class="backlog-page_issue-wrapper">
                  <app-issue-card
                    [issue]="issue"
                    [showStoryPoints]="true"
                    (onClick)="handleIssueClick($event)"
                  />
                </div>
              }
            </div>
          } @else {
            <div class="backlog-page_empty">
              <p class="backlog-page_empty-text">
                @if (search() || statusFilter() !== 'all' || priorityFilter() !== 'all') {
                  {{ 'backlog.noMatchingIssues' | translate }}
                } @else {
                  {{ 'backlog.noIssues' | translate }}
                }
              </p>
            </div>
          }

          <!-- Pagination -->
          <lib-pagination
            [currentPage]="currentPage()"
            [totalItems]="backlogTotal()"
            [itemsPerPage]="ITEMS_PER_PAGE"
            [itemLabel]="'backlog.issues' | translate"
            (pageChange)="handlePageChange($event)"
          />
        </div>
      }
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      :host {
        @apply block w-full h-full flex-1 min-h-0;
      }

      .backlog-page {
        @apply w-full h-full flex flex-col min-h-0;
      }

      .backlog-page_content {
        @apply flex flex-col gap-4 h-full min-h-0;
        @apply py-6 px-4 sm:px-6 lg:px-8;
      }

      .backlog-page_header {
        @apply flex items-center justify-between gap-4;
        @apply flex-shrink-0;
      }

      .backlog-page_stats {
        @apply text-sm;
      }

      .backlog-page_add-button {
        @apply flex items-center gap-2;
      }

      .backlog-page_filters {
        @apply flex items-center gap-3;
        @apply flex-shrink-0;
      }

      .backlog-page_search {
        @apply flex-1 max-w-sm;
      }

      .backlog-page_filter-select {
        @apply w-[140px];
      }

      .backlog-page_issues-grid {
        @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4;
        @apply flex-1 content-start;
        @apply overflow-y-auto;
        @apply min-h-0;
      }

      .backlog-page_issue-wrapper {
        @apply w-full;
      }

      .backlog-page_empty {
        @apply flex-1 flex items-center justify-center;
        @apply py-12;
      }

      .backlog-page_empty-text {
        @apply text-base text-muted-foreground text-center;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BacklogPage {
  private readonly issueService = inject(IssueService);
  private readonly navigationService = inject(NavigationService);
  private readonly toast = inject(ToastService);
  private readonly translateService = inject(TranslateService);
  private readonly destroyRef = inject(DestroyRef);

  readonly ITEMS_PER_PAGE = ITEMS_PER_PAGE;

  // State
  readonly backlogIssues = signal<IssueListItem[]>([]);
  readonly backlogTotal = signal<number>(0);
  readonly currentPage = signal<number>(1);
  readonly isLoading = signal<boolean>(false);
  readonly hasError = signal<boolean>(false);
  readonly errorMessage = signal<string>('');

  // Filters
  readonly search = signal<string>('');
  readonly statusFilter = signal<string>('all');
  readonly priorityFilter = signal<string>('all');

  // Search debouncing
  private readonly searchSubject = new Subject<string>();

  // Computed
  readonly projectId = computed(() => {
    return this.navigationService.currentProjectId() || '';
  });

  readonly backlogPoints = computed(() => {
    return this.backlogIssues().reduce((sum, issue) => sum + (issue.story_points || 0), 0);
  });

  readonly backlogDisplayCount = computed(() => {
    // Show filtered count if filters are applied, otherwise show total
    if (this.statusFilter() !== 'all' || this.priorityFilter() !== 'all') {
      return this.backlogIssues().length;
    }
    return this.backlogTotal();
  });

  readonly backlogTotalPages = computed(() => {
    const total = this.backlogTotal();
    return total > 0 ? Math.ceil(total / ITEMS_PER_PAGE) : 1;
  });

  readonly paginatedBacklogIssues = computed(() => {
    return this.backlogIssues();
  });

  readonly statusOptions = computed<SelectOption[]>(() => {
    return [
      { value: 'all', label: this.translateService.instant('backlog.allStatus') },
      { value: 'todo', label: this.translateService.instant('issues.status.todo') },
      { value: 'in-progress', label: this.translateService.instant('issues.status.inProgress') },
      { value: 'done', label: this.translateService.instant('issues.status.done') },
    ];
  });

  readonly priorityOptions = computed<SelectOption[]>(() => {
    return [
      { value: 'all', label: this.translateService.instant('backlog.allPriority') },
      { value: 'low', label: this.translateService.instant('issues.priority.low') },
      { value: 'medium', label: this.translateService.instant('issues.priority.medium') },
      { value: 'high', label: this.translateService.instant('issues.priority.high') },
      { value: 'critical', label: this.translateService.instant('issues.priority.critical') },
    ];
  });

  constructor() {
    // Setup search debouncing
    this.searchSubject
      .pipe(debounceTime(300), distinctUntilChanged(), takeUntilDestroyed(this.destroyRef))
      .subscribe(() => {
        this.currentPage.set(1);
        this.loadBacklogIssues();
      });

    // Load initial data
    this.loadBacklogIssues();

    // Watch for page changes
    effect(
      () => {
        const page = this.currentPage();
        if (page > 0) {
          this.loadBacklogIssues();
        }
      },
      { allowSignalWrites: true },
    );

    // Watch for status filter changes
    effect(
      () => {
        const status = this.statusFilter();
        if (status) {
          this.currentPage.set(1);
          this.loadBacklogIssues();
        }
      },
      { allowSignalWrites: true },
    );

    // Watch for priority filter changes
    effect(
      () => {
        const priority = this.priorityFilter();
        if (priority) {
          this.currentPage.set(1);
          this.loadBacklogIssues();
        }
      },
      { allowSignalWrites: true },
    );
  }

  handleSearchChange(value: string): void {
    this.search.set(value);
    this.searchSubject.next(value);
  }

  handlePageChange(page: number): void {
    this.currentPage.set(page);
  }

  async loadBacklogIssues(): Promise<void> {
    const projectId = this.projectId();
    if (!projectId) {
      return;
    }

    this.isLoading.set(true);
    this.hasError.set(false);

    try {
      const searchQuery = this.search().trim() || undefined;
      const result = await this.issueService.getBacklogIssues(
        projectId,
        this.currentPage(),
        ITEMS_PER_PAGE,
        searchQuery,
      );

      // Apply frontend filters for status and priority
      let filteredIssues = result.issues;

      if (this.statusFilter() !== 'all') {
        filteredIssues = filteredIssues.filter((issue) => issue.status === this.statusFilter());
      }

      if (this.priorityFilter() !== 'all') {
        filteredIssues = filteredIssues.filter((issue) => issue.priority === this.priorityFilter());
      }

      this.backlogIssues.set(filteredIssues);
      // Use API total for pagination (it accounts for search)
      // Note: Status and priority filters are frontend-only, so pagination total
      // reflects search results, not filtered results
      this.backlogTotal.set(result.total);
    } catch (error) {
      console.error('Failed to load backlog issues:', error);
      this.hasError.set(true);
      this.errorMessage.set(
        error instanceof Error
          ? error.message
          : this.translateService.instant('backlog.failedToLoad'),
      );
      this.backlogIssues.set([]);
      this.backlogTotal.set(0);
    } finally {
      this.isLoading.set(false);
    }
  }

  handleIssueClick(issue: IssueListItem): void {
    // Navigate to issue detail
    const orgId = this.navigationService.currentOrganizationId();
    const projId = this.projectId();
    if (orgId && projId) {
      // TODO: Implement issue detail navigation
      console.log('Navigate to issue:', issue.id);
    }
  }

  handleCreateIssue(): void {
    // TODO: Open create issue modal
    this.toast.info(this.translateService.instant('backlog.createIssueComingSoon'));
  }
}
