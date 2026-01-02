import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  ViewContainerRef,
  signal,
  effect,
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
          @if (filteredProjects().length === 0 && allProjects().length > 0) {
            <lib-empty-state
              [title]="'projects.noProjectsFound' | translate"
              [message]="'projects.noProjectsFoundDescription' | translate"
              icon="search"
            />
          } @else if (filteredProjects().length === 0) {
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
              @for (project of paginatedProjects(); track project.id) {
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
        filteredProjects().length > 0
      ) {
        <app-page-footer>
          <lib-pagination
            [currentPage]="currentPage()"
            [totalItems]="filteredProjects().length"
            [itemsPerPage]="ITEMS_PER_PAGE"
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
        @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6;
        @apply flex-1;
        @apply content-start;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProjectsPage {
  readonly projectService = inject(ProjectService);
  readonly organizationService = inject(OrganizationService);
  readonly navigationService = inject(NavigationService);
  readonly modal = inject(Modal);
  readonly viewContainerRef = inject(ViewContainerRef);
  readonly translateService = inject(TranslateService);

  readonly searchQuery = signal('');
  readonly statusFilter = signal<string>('all');
  readonly currentPage = signal<number>(1);
  readonly ITEMS_PER_PAGE = 6;

  readonly organizationId = computed(() => {
    // URL is the source of truth - organization service will sync automatically
    return this.navigationService.currentOrganizationId();
  });

  readonly allProjects = computed(() => {
    const orgId = this.organizationId();
    if (!orgId) return [];
    return this.projectService.getProjectsByOrganization(orgId);
  });

  readonly statusFilterOptions = computed<SelectOption<string>[]>(() => [
    { value: 'all', label: 'All' },
    { value: 'active', label: 'Active' },
    { value: 'completed', label: 'Completed' },
    { value: 'on-hold', label: 'On Hold' },
  ]);

  readonly filteredProjects = computed(() => {
    const projects = this.allProjects();
    const query = this.searchQuery().toLowerCase().trim();
    const status = this.statusFilter();

    let filtered = projects;

    // Filter by search query
    if (query) {
      filtered = filtered.filter((project) => {
        const nameMatch = project.name.toLowerCase().includes(query);
        const keyMatch = project.key.toLowerCase().includes(query);
        const descriptionMatch = project.description?.toLowerCase().includes(query) || false;
        return nameMatch || keyMatch || descriptionMatch;
      });
    }

    // Filter by status
    if (status !== 'all') {
      filtered = filtered.filter((project) => project.status === status);
    }

    return filtered;
  });

  readonly totalPages = computed(() => {
    return Math.ceil(this.filteredProjects().length / this.ITEMS_PER_PAGE);
  });

  readonly paginatedProjects = computed(() => {
    const projects = this.filteredProjects();
    const start = (this.currentPage() - 1) * this.ITEMS_PER_PAGE;
    const end = start + this.ITEMS_PER_PAGE;
    return projects.slice(start, end);
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
    if (!this.organizationId() || this.allProjects().length === 0) {
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
    if (!this.organizationId() || this.allProjects().length === 0) {
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

  // Projects are now automatically loaded when URL organizationId changes
  // No need for manual initialization effect

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
