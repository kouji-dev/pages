import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  ViewContainerRef,
  signal,
  effect,
  OnInit,
  OnDestroy,
} from '@angular/core';
import {
  LoadingState,
  ErrorState,
  EmptyState,
  Modal,
  Input,
  Select,
  SelectOption,
  Pagination,
} from 'shared-ui';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { ProjectService, Project } from '../../../../application/services/project.service';
import { OrganizationService } from '../../../../application/services/organization.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import { ProjectCard } from '../../components/project-card/project-card';
import { CreateProjectModal } from '../../components/create-project-modal/create-project-modal';
import {
  PageHeader,
  PageHeaderAction,
  PageHeaderSearchInput,
  PageHeaderFilter,
} from '../../../../shared/layout/page-header/page-header';
import { PageBody } from '../../../../shared/layout/page-body/page-body';
import { PageContent } from '../../../../shared/layout/page-content/page-content';
import { PageFooter } from '../../../../shared/layout/page-footer/page-footer';

@Component({
  selector: 'app-projects-page',
  imports: [
    LoadingState,
    ErrorState,
    EmptyState,
    ProjectCard,
    Pagination,
    TranslatePipe,
    PageHeader,
    PageBody,
    PageContent,
    PageFooter,
  ],
  template: `
    <app-page-body>
      <app-page-header
        title="projects.title"
        subtitle="projects.subtitle"
        [searchInput]="searchInputConfig()"
        [filters]="filtersConfig()"
        [action]="createProjectAction()"
      />

      <app-page-content>
        @if (!organizationId()) {
          <lib-empty-state
            [title]="'projects.noOrganizationSelected' | translate"
            [message]="'projects.noOrganizationSelectedDescription' | translate"
            icon="building"
            [actionLabel]="'projects.goToOrganizations' | translate"
            actionIcon="arrow-right"
            (onAction)="handleGoToOrganizations()"
          />
        } @else if (projectService.isLoading()) {
          <lib-loading-state [message]="'projects.loadingProjects' | translate" />
        } @else if (projectService.hasError()) {
          <lib-error-state
            [title]="'projects.failedToLoad' | translate"
            [message]="errorMessage()"
            [retryLabel]="'common.retry' | translate"
            (onRetry)="handleRetry()"
          />
        } @else {
          <!-- Grid -->
          @if (projects().length === 0 && (searchQuery() || statusFilter() !== 'all')) {
            <lib-empty-state
              [title]="'projects.noProjectsFound' | translate"
              [message]="'projects.noProjectsFoundDescription' | translate"
              icon="search"
            />
          } @else if (projects().length === 0) {
            <lib-empty-state
              [title]="'projects.noProjects' | translate"
              [message]="'projects.noProjectsDescription' | translate"
              icon="folder"
              [actionLabel]="'projects.createProject' | translate"
              actionIcon="plus"
              (onAction)="handleCreateProject()"
            />
          } @else {
            <div class="projects-page_grid">
              @for (project of projects(); track project.id) {
                <app-project-card
                  [project]="project"
                  (onSettings)="handleProjectSettings($event)"
                />
              }
            </div>
          }
        }
      </app-page-content>

      @if (
        organizationId() &&
        !projectService.isLoading() &&
        !projectService.hasError() &&
        projects().length > 0
      ) {
        <app-page-footer>
          <lib-pagination
            [currentPage]="currentPage()"
            [totalItems]="totalItems()"
            [itemsPerPage]="ITEMS_PER_PAGE()"
            itemLabel="projects"
            (pageChange)="goToPage($event)"
          />
        </app-page-footer>
      }
    </app-page-body>
  `,
  styles: [
    `
      @reference "#mainstyles";

      :host {
        @apply flex flex-col flex-auto;
        @apply w-full;
        @apply min-h-0;
      }

      .projects-page_grid {
        @apply grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4;
        @apply flex-1;
        @apply content-start;
        @apply items-stretch;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProjectsPage implements OnInit, OnDestroy {
  readonly projectService = inject(ProjectService);
  readonly organizationService = inject(OrganizationService);
  readonly navigationService = inject(NavigationService);
  readonly modal = inject(Modal);
  readonly viewContainerRef = inject(ViewContainerRef);
  readonly translateService = inject(TranslateService);

  readonly searchQuery = signal('');
  readonly statusFilter = signal<string>('all');
  readonly currentPage = signal<number>(1);

  private readonly windowWidth = signal<number>(
    typeof window !== 'undefined' ? window.innerWidth : 1024,
  );

  // Responsive items per page based on screen size
  readonly ITEMS_PER_PAGE = computed(() => {
    const width = this.windowWidth();
    if (width >= 1536) return 24; // 2xl: 6 columns * 4 rows
    if (width >= 1280) return 20; // xl: 5 columns * 4 rows
    if (width >= 1024) return 16; // lg: 4 columns * 4 rows
    if (width >= 768) return 12; // md: 3 columns * 4 rows
    if (width >= 640) return 8; // sm: 2 columns * 4 rows
    return 6; // default: 1 column * 6 rows
  });

  private resizeListener?: () => void;

  readonly organizationId = computed(() => {
    // URL is the source of truth - organization service will sync automatically
    return this.navigationService.currentOrganizationId();
  });

  readonly statusFilterOptions = computed<SelectOption<string>[]>(() => [
    { value: 'all', label: 'All' },
    { value: 'active', label: 'Active' },
    { value: 'completed', label: 'Completed' },
    { value: 'on-hold', label: 'On Hold' },
  ]);

  // Backend-filtered and paginated projects
  readonly projectsResponse = computed(() => {
    return this.projectService.projects.value();
  });

  readonly projects = computed(() => {
    // Use projectsList which handles the mapping
    return this.projectService.projectsList();
  });

  readonly totalItems = computed(() => {
    const response = this.projectsResponse();
    return response?.total || 0;
  });

  readonly totalPages = computed(() => {
    const response = this.projectsResponse();
    return response?.pages || 0;
  });

  readonly errorMessage = computed(() => {
    const error = this.projectService.error();
    if (error) {
      return error instanceof Error ? error.message : 'An error occurred while loading projects.';
    }
    return 'An unknown error occurred.';
  });

  readonly createProjectAction = computed<PageHeaderAction>(() => ({
    label: this.translateService.instant('projects.createProject'),
    icon: 'plus',
    variant: 'primary',
    size: 'md',
    disabled: !this.organizationId(),
    onClick: () => this.handleCreateProject(),
  }));

  readonly searchInputConfig = computed<PageHeaderSearchInput | null>(() => {
    if (!this.organizationId()) {
      return null;
    }
    return {
      placeholder: this.translateService.instant('projects.searchPlaceholder'),
      model: this.searchQuery,
      leftIcon: 'search',
      class: 'page-header_search-input',
    };
  });

  readonly filtersConfig = computed<PageHeaderFilter[] | null>(() => {
    if (!this.organizationId()) {
      return null;
    }
    return [
      {
        type: 'select',
        options: this.statusFilterOptions(),
        model: this.statusFilter,
        class: 'page-header_filter',
      },
    ];
  });

  constructor() {
    // Update backend filters when search, status, page, or items per page changes
    effect(() => {
      const orgId = this.organizationId();
      if (!orgId) return;

      const search = this.searchQuery().trim() || undefined;
      const status = this.statusFilter() !== 'all' ? this.statusFilter() : undefined;
      const page = this.currentPage();
      const limit = this.ITEMS_PER_PAGE();

      this.projectService.updateProjectsFilters({
        search,
        status,
        page,
        limit,
      });
    });

    // Reset to page 1 when search or status changes
    effect(() => {
      this.searchQuery();
      this.statusFilter();
      // Reset page when filters change
      if (this.currentPage() !== 1) {
        this.currentPage.set(1);
      }
    });
  }

  ngOnInit(): void {
    // Listen to window resize to update items per page
    if (typeof window !== 'undefined') {
      this.resizeListener = () => {
        this.windowWidth.set(window.innerWidth);
      };
      window.addEventListener('resize', this.resizeListener);
      // Initialize width
      this.windowWidth.set(window.innerWidth);
    }
  }

  ngOnDestroy(): void {
    if (this.resizeListener && typeof window !== 'undefined') {
      window.removeEventListener('resize', this.resizeListener);
    }
  }

  handleCreateProject(): void {
    const orgId = this.organizationId();
    if (!orgId) {
      return;
    }
    this.modal.open(CreateProjectModal, this.viewContainerRef, {
      size: 'md',
      data: { organizationId: orgId },
    });
    // Note: CreateProjectModal already reloads projects after creation
  }

  handleProjectSettings(project: Project): void {
    const orgId = this.organizationId();
    if (!orgId) return;
    this.navigationService.navigateToProjectSettings(orgId, project.id);
  }

  handleRetry(): void {
    this.projectService.loadProjects();
  }

  handleGoToOrganizations(): void {
    this.navigationService.navigateToOrganizations();
  }

  goToPage(page: number): void {
    this.currentPage.set(page);
  }
}
