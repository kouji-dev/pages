import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  signal,
  effect,
  ViewContainerRef,
  ViewChild,
  TemplateRef,
  DestroyRef,
} from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { Button, Input, LoadingState, ErrorState, Modal, ToastService } from 'shared-ui';
import { ProjectService } from '../../../../application/services/project.service';
import { OrganizationService } from '../../../../application/services/organization.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import { ProjectMemberList } from '../../components/project-member-list/project-member-list';
import { IssueList } from '../../components/issue-list/issue-list';
import { KanbanBoard } from '../../components/kanban-board/kanban-board';
import { PageHeader, PageHeaderAction } from '../../../../shared/layout/page-header/page-header';
import { SprintSelector } from '../../components/sprint-selector/sprint-selector';
import { Progress, Icon } from 'shared-ui';
import { ProjectNav } from '../../components/project-nav/project-nav';
import { BacklogRibbon } from '../../components/backlog-ribbon/backlog-ribbon';
import { DeleteProjectModal } from '../../components/delete-project-modal/delete-project-modal';
import { CreateSprintModal } from '../../components/create-sprint-modal/create-sprint-modal';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { PageContent } from '../../../../shared/layout/page-content/page-content';
import { PageBody } from '../../../../shared/layout/page-body/page-body';
import { PageFooter } from '../../../../shared/layout/page-footer/page-footer';
import {
  SprintService,
  Sprint,
  SprintIssue,
} from '../../../../application/services/sprint.service';
import { IssueService, IssueListItem } from '../../../../application/services/issue.service';
import { ReviewPage } from '../review/review-page';
import { PlanningPage } from '../planning/planning-page';
import { BacklogPage } from '../backlog/backlog-page';
import { ReportsPage } from '../reports/reports-page';

type TabType =
  | 'issues'
  | 'board'
  | 'settings'
  | 'members'
  | 'review'
  | 'planning'
  | 'backlog'
  | 'reports';

@Component({
  selector: 'app-project-detail-page',
  imports: [
    Button,
    Input,
    LoadingState,
    ErrorState,
    ProjectMemberList,
    IssueList,
    KanbanBoard,
    PageHeader,
    SprintSelector,
    Progress,
    Icon,
    ProjectNav,
    BacklogRibbon,
    TranslatePipe,
    PageContent,
    PageBody,
    PageFooter,
    ReviewPage,
    PlanningPage,
    BacklogPage,
    ReportsPage,
  ],
  template: `
    @if (projectService.isFetchingProject()) {
      <lib-loading-state [message]="'projects.loadingProject' | translate" />
    } @else if (projectService.hasProjectError()) {
      <lib-error-state
        [title]="'projects.failedToLoad' | translate"
        [message]="errorMessage()"
        [retryLabel]="'common.retry' | translate"
        (onRetry)="handleRetry()"
      />
    } @else if (!project()) {
      <lib-error-state
        [title]="'projects.notFound' | translate"
        [message]="'projects.notFoundDescription' | translate"
        [showRetry]="false"
      />
    } @else {
      <app-page-body>
        <app-page-header
          [title]="project()?.name || ''"
          [subtitle]="project()?.description"
          [leftAction]="settingsAction()"
          [actionTemplate]="sprintActionsTemplate"
        >
          <ng-template #sprintActionsTemplate>
            <div class="project-detail-page_sprint-actions">
              @if (sprintService.currentSprint(); as sprint) {
                <!-- Progress indicator -->
                <div class="project-detail-page_progress">
                  <div class="project-detail-page_progress-bar">
                    <lib-progress [value]="sprintProgressPercent()" />
                  </div>
                  <span class="project-detail-page_progress-text">
                    {{ sprintProgressPercent() }}%
                  </span>
                  <span class="project-detail-page_progress-points">
                    ({{ sprint.completedIssues }}/{{ sprint.totalIssues }}
                    {{ 'sprints.issues' | translate }})
                  </span>
                </div>

                <!-- Dates -->
                <div class="project-detail-page_dates">
                  <lib-icon name="calendar" [size]="'xs'" />
                  <span>{{ formatSprintDate(sprint.startDate) }}</span>
                  <span>→</span>
                  <span>{{ formatSprintDate(sprint.endDate) }}</span>
                </div>

                @if (sprint.status === 'active') {
                  <lib-button variant="outline" size="sm" (clicked)="handleCompleteSprint()">
                    {{ 'sprints.complete' | translate }}
                  </lib-button>
                }
              }

              <app-sprint-selector
                [sprints]="sprintService.sprintsList()"
                [selectedSprint]="sprintService.currentSprint()"
                (onSprintSelect)="handleSprintSelect($event)"
                (onCreateSprint)="handleCreateSprint()"
              />
            </div>
          </ng-template>
        </app-page-header>
        <app-project-nav [projectId]="projectId()" />
        <app-page-content noPadding>
          <div class="project-detail-page_container">
            <div class="project-detail-page_main">
              @if (activeTab() === 'board') {
                <div class="project-detail-page_board-wrapper">
                  <app-kanban-board [projectId]="projectId()" />
                </div>
              } @else if (activeTab() === 'review') {
                <app-review-page />
              } @else if (activeTab() === 'planning') {
                <app-planning-page />
              } @else if (activeTab() === 'backlog') {
                <app-backlog-page />
              } @else if (activeTab() === 'reports') {
                <app-reports-page />
              } @else if (activeTab() === 'issues') {
                <app-issue-list [projectId]="projectId()" />
              } @else if (activeTab() === 'members') {
                <app-project-member-list [projectId]="projectId()" />
              } @else if (activeTab() === 'settings') {
                <div class="project-detail-page_settings">
                  <div class="project-detail-page_settings-container">
                    <!-- Project Details Section -->
                    <div class="project-detail-page_settings-section">
                      <h2 class="project-detail-page_settings-section-title">
                        {{ 'projects.settings.details' | translate }}
                      </h2>
                      <form
                        class="project-detail-page_settings-form"
                        (ngSubmit)="handleSaveProject()"
                      >
                        <lib-input
                          [label]="'projects.settings.name' | translate"
                          [placeholder]="'projects.settings.namePlaceholder' | translate"
                          [(model)]="name"
                          [required]="true"
                          [errorMessage]="nameError()"
                          [helperText]="'projects.settings.nameHelper' | translate"
                        />
                        <lib-input
                          [label]="'projects.settings.key' | translate"
                          placeholder="PROJ"
                          [(model)]="key"
                          [readonly]="true"
                          [helperText]="'projects.settings.keyHelper' | translate"
                        />
                        <lib-input
                          [label]="'projects.settings.description' | translate"
                          type="textarea"
                          [placeholder]="'projects.settings.descriptionPlaceholder' | translate"
                          [(model)]="description"
                          [rows]="4"
                          [helperText]="'projects.settings.descriptionHelper' | translate"
                        />
                        <div class="project-detail-page_settings-form-actions">
                          <lib-button
                            variant="primary"
                            type="submit"
                            [loading]="isSaving()"
                            [disabled]="!isFormValid() || !hasChanges()"
                          >
                            {{ 'common.saveChanges' | translate }}
                          </lib-button>
                          <lib-button
                            variant="secondary"
                            (clicked)="handleReset()"
                            [disabled]="!hasChanges() || isSaving()"
                          >
                            {{ 'common.cancel' | translate }}
                          </lib-button>
                        </div>
                      </form>
                    </div>

                    <!-- Danger Zone Section -->
                    <div
                      class="project-detail-page_settings-section project-detail-page_settings-section--danger"
                    >
                      <h2 class="project-detail-page_settings-section-title">
                        {{ 'projects.settings.dangerZone' | translate }}
                      </h2>
                      <div class="project-detail-page_settings-danger-content">
                        <div>
                          <h3 class="project-detail-page_settings-danger-title">
                            {{ 'projects.settings.deleteTitle' | translate }}
                          </h3>
                          <p class="project-detail-page_settings-danger-description">
                            {{ 'projects.settings.deleteDescription' | translate }}
                          </p>
                        </div>
                        <lib-button
                          variant="destructive"
                          size="md"
                          (clicked)="handleDeleteProject()"
                          [disabled]="isDeleting()"
                        >
                          {{ 'projects.deleteProject' | translate }}
                        </lib-button>
                      </div>
                    </div>
                  </div>
                </div>
              }
            </div>
          </div>
        </app-page-content>

        @if (activeTab() === 'board') {
          <app-page-footer>
            <app-backlog-ribbon
              [issues]="backlogIssues()"
              [search]="backlogSearch()"
              [page]="backlogPage()"
              [totalItems]="backlogTotal()"
              [totalPages]="backlogTotalPages()"
              [itemsPerPage]="ITEMS_PER_PAGE"
              [isLoading]="isLoadingBacklog()"
              (onIssueClick)="handleIssueClick($event)"
              (onSearchChange)="handleBacklogSearchChange($event)"
              (onPageChange)="handleBacklogPageChange($event)"
            />
          </app-page-footer>
        }
      </app-page-body>
    }
  `,
  styles: [
    `
      @reference "#mainstyles";

      :host {
        @apply flex flex-col flex-auto;
        @apply w-full;
        @apply min-h-0;
      }

      .project-detail-page_container {
        @apply w-full;
        @apply flex flex-col;
        @apply min-h-0;
        @apply flex-auto;
      }

      .project-detail-page_main {
        @apply flex flex-auto;
        @apply flex-col;
        @apply min-h-0;
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
      }

      .project-detail-page_main:has(app-backlog-page),
      .project-detail-page_main:has(app-reports-page) {
        @apply p-0;
      }

      .project-detail-page_board-wrapper {
        @apply flex flex-col;
        @apply min-h-0;
        @apply flex-shrink;
      }

      .project-detail-page_sprint-actions {
        @apply flex items-center;
        @apply gap-4;
        @apply flex-shrink-0;
      }

      .project-detail-page_progress {
        @apply flex items-center;
        @apply gap-2;
        @apply px-3 py-1.5;
        @apply rounded-md;
        background-color: hsl(var(--color-muted) / 0.5);
      }

      .project-detail-page_progress-bar {
        @apply w-20;
      }

      .project-detail-page_progress-text {
        @apply text-xs font-medium;
        @apply text-foreground;
      }

      .project-detail-page_progress-points {
        @apply text-xs;
        @apply text-muted-foreground;
      }

      .project-detail-page_dates {
        @apply flex items-center;
        @apply gap-1.5;
        @apply text-xs;
        @apply text-muted-foreground;
      }

      .project-detail-page_placeholder {
        @apply text-base;
        @apply text-muted-foreground;
        @apply text-center;
        @apply py-12;
        margin: 0;
      }

      .project-detail-page_settings {
        @apply w-full;
        @apply h-full;
        @apply overflow-auto;
      }

      .project-detail-page_settings-container {
        @apply max-w-4xl;
        @apply flex flex-col;
        @apply gap-8;
      }

      .project-detail-page_settings-section {
        @apply flex flex-col;
        @apply gap-6;
        @apply p-6;
        @apply rounded-lg;
        @apply border;
        @apply border-border;
        @apply bg-background;
      }

      .project-detail-page_settings-section--danger {
        @apply border-destructive;
      }

      .project-detail-page_settings-section-title {
        @apply text-xl font-semibold;
        @apply text-foreground;
        margin: 0;
      }

      .project-detail-page_settings-form {
        @apply flex flex-col;
        @apply gap-6;
      }

      .project-detail-page_settings-form-actions {
        @apply flex items-center;
        @apply gap-3;
        @apply pt-4;
        @apply border-t;
        @apply border-border;
      }

      .project-detail-page_settings-danger-content {
        @apply flex items-center justify-between;
        @apply gap-4;
        @apply flex-wrap;
      }

      .project-detail-page_settings-danger-title {
        @apply text-lg font-semibold;
        @apply text-foreground;
        margin: 0 0 0.5rem 0;
      }

      .project-detail-page_settings-danger-description {
        @apply text-sm;
        @apply text-muted-foreground;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProjectDetailPage {
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  readonly projectService = inject(ProjectService);
  readonly organizationService = inject(OrganizationService);
  readonly navigationService = inject(NavigationService);
  readonly sprintService = inject(SprintService);
  readonly issueService = inject(IssueService);
  readonly modal = inject(Modal);
  readonly toast = inject(ToastService);
  readonly viewContainerRef = inject(ViewContainerRef);
  private readonly translateService = inject(TranslateService);

  @ViewChild('sprintActionsTemplate', { static: true })
  sprintActionsTemplate!: TemplateRef<any>;

  readonly organizationId = computed(() => {
    return this.navigationService.currentOrganizationId() || '';
  });

  readonly projectId = computed(() => {
    return this.navigationService.currentProjectId() || '';
  });

  readonly project = computed(() => this.projectService.currentProject());

  // Backlog issues (issues not in any sprint)
  readonly backlogIssuesList = signal<IssueListItem[]>([]);
  readonly isLoadingBacklog = signal(false);
  readonly backlogSearch = signal('');
  readonly backlogPage = signal(1);
  readonly backlogTotal = signal(0);
  readonly backlogTotalPages = signal(0);
  readonly backlogSearchSubject = new Subject<string>();
  private readonly destroyRef = inject(DestroyRef);
  readonly ITEMS_PER_PAGE = 20;

  constructor() {
    // Debounce search input
    this.backlogSearchSubject
      .pipe(debounceTime(300), distinctUntilChanged(), takeUntilDestroyed(this.destroyRef))
      .subscribe((search) => {
        this.backlogSearch.set(search);
        this.backlogPage.set(1); // Reset to first page on search
        this.loadBacklogIssues();
      });
  }

  readonly backlogIssues = computed<SprintIssue[]>(() => {
    return this.backlogIssuesList().map((issue) => this.convertToSprintIssue(issue));
  });

  // Settings form state
  readonly name = signal('');
  readonly key = signal('');
  readonly description = signal('');
  readonly isSaving = signal(false);
  readonly isDeleting = signal(false);
  readonly originalName = signal('');
  readonly originalDescription = signal('');

  // Get tab from query params, default to 'board'
  readonly queryParams = toSignal(this.route.queryParams, {
    initialValue: {} as Record<string, string>,
  });

  readonly activeTab = computed<TabType>(() => {
    const params = this.queryParams();
    const tab = params?.['tab'];
    if (!tab || typeof tab !== 'string') return 'board';

    const validTabs: TabType[] = [
      'board',
      'review',
      'planning',
      'backlog',
      'reports',
      'issues',
      'members',
      'settings',
    ];
    return validTabs.includes(tab as TabType) ? (tab as TabType) : 'board';
  });

  readonly nameError = computed(() => {
    const value = this.name();
    if (!value.trim()) {
      return this.translateService.instant('projects.settings.nameRequired');
    }
    if (value.trim().length < 3) {
      return this.translateService.instant('projects.settings.nameMinLength');
    }
    return '';
  });

  readonly isFormValid = computed(() => {
    return !this.nameError() && this.name().trim().length > 0;
  });

  readonly hasChanges = computed(() => {
    return (
      this.name().trim() !== this.originalName() ||
      this.description().trim() !== this.originalDescription()
    );
  });

  // Initialize form when project changes
  private readonly initializeFormEffect = effect(() => {
    const project = this.project();
    if (project) {
      this.name.set(project.name);
      this.key.set(project.key);
      this.description.set(project.description || '');
      this.originalName.set(project.name);
      this.originalDescription.set(project.description || '');
    }
  });

  // Load backlog issues when board tab is active or page changes
  private readonly loadBacklogEffect = effect(() => {
    const projectId = this.projectId();
    const tab = this.activeTab();
    const page = this.backlogPage();
    const search = this.backlogSearch();
    if (projectId && tab === 'board') {
      this.loadBacklogIssues();
    }
  });

  readonly errorMessage = computed(() => {
    const error = this.projectService.projectError();
    if (error) {
      return error instanceof Error
        ? error.message
        : this.translateService.instant('projects.loadError');
    }
    return this.translateService.instant('common.unknownError');
  });

  async handleSaveProject(): Promise<void> {
    if (!this.isFormValid() || !this.hasChanges()) {
      return;
    }

    const id = this.projectId();
    if (!id) {
      return;
    }

    this.isSaving.set(true);

    try {
      await this.projectService.updateProject(id, {
        name: this.name().trim(),
        description: this.description().trim() || undefined,
      });
      this.originalName.set(this.name().trim());
      this.originalDescription.set(this.description().trim());
      this.toast.success(this.translateService.instant('projects.updateSuccess'));
    } catch (error) {
      console.error('Failed to update project:', error);
      const errorMessage =
        error instanceof Error
          ? error.message
          : this.translateService.instant('projects.updateError');
      this.toast.error(errorMessage);
    } finally {
      this.isSaving.set(false);
    }
  }

  handleReset(): void {
    const project = this.project();
    if (project) {
      this.name.set(project.name);
      this.description.set(project.description || '');
      this.originalName.set(project.name);
      this.originalDescription.set(project.description || '');
    }
  }

  handleDeleteProject(): void {
    const id = this.projectId();
    if (!id) {
      return;
    }

    this.modal.open(DeleteProjectModal, this.viewContainerRef, {
      size: 'md',
      data: { projectId: id, projectName: this.project()?.name || 'this project' },
    });
  }

  handleRetry(): void {
    const id = this.projectId();
    if (id) {
      this.projectService.fetchProject(id);
    }
  }

  handleSprintSelect(sprint: Sprint): void {
    // Set the selected sprint - issues will automatically reload because they depend on currentSprint
    this.sprintService.selectSprint(sprint);
  }

  handleCreateSprint(): void {
    this.modal.open(CreateSprintModal, this.viewContainerRef, {
      size: 'md',
      data: { projectId: this.projectId() },
    });
  }

  handleCompleteSprint(): void {
    // TODO: Open sprint completion modal
    console.log('Complete sprint');
  }

  handleIssueClick(issue: SprintIssue): void {
    const orgId = this.organizationId();
    const projectId = this.projectId();
    if (orgId && projectId) {
      this.navigationService.navigateToIssue(orgId, projectId, issue.id);
    }
  }

  handleSettingsClick(): void {
    const orgId = this.organizationId();
    const projectId = this.projectId();
    if (orgId && projectId) {
      this.router.navigate(['/app', 'organizations', orgId, 'projects', projectId, 'settings']);
    }
  }

  readonly settingsAction = computed<PageHeaderAction>(() => ({
    label: this.translateService.instant('projects.settings.title'),
    icon: 'settings',
    variant: 'ghost',
    size: 'sm',
    onClick: () => this.handleSettingsClick(),
  }));

  readonly sprintProgressPercent = computed(() => {
    const sprint = this.sprintService.currentSprint();
    if (!sprint || sprint.totalIssues === 0) return 0;
    return Math.round(((sprint.completedIssues || 0) / (sprint.totalIssues || 1)) * 100);
  });

  formatSprintDate(date: Date | string): string {
    const d = typeof date === 'string' ? new Date(date) : date;
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
    }).format(d);
  }

  async loadBacklogIssues(): Promise<void> {
    const projectId = this.projectId();
    if (!projectId) {
      return;
    }

    this.isLoadingBacklog.set(true);
    try {
      const search = this.backlogSearch().trim() || undefined;
      const page = this.backlogPage();
      const result = await this.issueService.getBacklogIssues(
        projectId,
        page,
        this.ITEMS_PER_PAGE,
        search,
      );
      this.backlogIssuesList.set(result.issues);
      this.backlogTotal.set(result.total);
      this.backlogTotalPages.set(result.pages);
    } catch (error) {
      console.error('Failed to load backlog issues:', error);
      this.backlogIssuesList.set([]);
      this.backlogTotal.set(0);
      this.backlogTotalPages.set(0);
    } finally {
      this.isLoadingBacklog.set(false);
    }
  }

  handleBacklogSearchChange(value: string): void {
    this.backlogSearchSubject.next(value);
  }

  handleBacklogPageChange(page: number): void {
    this.backlogPage.set(page);
    this.loadBacklogIssues();
  }

  private convertToSprintIssue(issue: IssueListItem): SprintIssue {
    // Map priority: 'critical' -> 'high', others stay the same
    const priority: 'low' | 'medium' | 'high' | undefined =
      issue.priority === 'critical' ? 'high' : issue.priority;

    // Map type: 'epic' -> 'story', others stay the same
    const type: 'task' | 'bug' | 'link' | 'story' | undefined =
      issue.type === 'epic' ? 'story' : issue.type;

    // Map status: 'cancelled' -> 'todo'
    const status: 'todo' | 'in_progress' | 'code_review' | 'done' =
      issue.status === 'cancelled' ? 'todo' : issue.status;

    return {
      id: issue.id,
      title: issue.title,
      projectId: issue.project_id,
      sprintId: undefined, // Backlog issues don't have a sprint
      priority,
      status,
      storyPoints: issue.story_points,
      type,
      // Note: assignee, labels, hasImage, imageUrl would need to be fetched separately
      // if needed for the backlog ribbon display
    };
  }
}
