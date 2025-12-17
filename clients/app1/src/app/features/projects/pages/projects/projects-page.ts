import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  ViewContainerRef,
  signal,
  effect,
} from '@angular/core';
import { Button, LoadingState, ErrorState, EmptyState, Modal, Input } from 'shared-ui';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { ProjectService, Project } from '../../../../application/services/project.service';
import { OrganizationService } from '../../../../application/services/organization.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import { ProjectCard } from '../../components/project-card/project-card';
import { CreateProjectModal } from '../../components/create-project-modal/create-project-modal';
import { PageHeader, PageHeaderAction } from '../../../../shared/layout/page-header/page-header';
import { PageBody } from '../../../../shared/layout/page-body/page-body';
import { PageContent } from '../../../../shared/layout/page-content/page-content';

@Component({
  selector: 'app-projects-page',
  imports: [
    Button,
    LoadingState,
    ErrorState,
    EmptyState,
    ProjectCard,
    Input,
    TranslatePipe,
    PageHeader,
    PageBody,
    PageContent,
  ],
  template: `
    <app-page-body>
      <app-page-header
        title="projects.title"
        subtitle="projects.subtitle"
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
          @if (allProjects().length > 0) {
            <div class="projects-page_search">
              <lib-input
                [placeholder]="'projects.searchPlaceholder' | translate"
                [(model)]="searchQuery"
                leftIcon="search"
                class="projects-page_search-input"
              />
            </div>
          }
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
              @for (project of filteredProjects(); track project.id) {
                <app-project-card
                  [project]="project"
                  (onSettings)="handleProjectSettings($event)"
                />
              }
            </div>
          }
        }
      </app-page-content>
    </app-page-body>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .projects-page_search {
        @apply max-w-7xl mx-auto;
        @apply mb-6;
      }

      .projects-page_search-input {
        @apply max-w-md;
      }

      .projects-page_grid {
        @apply max-w-7xl mx-auto;
        @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3;
        @apply gap-6;
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

  readonly organizationId = computed(() => {
    // URL is the source of truth - organization service will sync automatically
    return this.navigationService.currentOrganizationId();
  });

  readonly allProjects = computed(() => {
    const orgId = this.organizationId();
    if (!orgId) return [];
    return this.projectService.getProjectsByOrganization(orgId);
  });

  readonly filteredProjects = computed(() => {
    const projects = this.allProjects();
    const query = this.searchQuery().toLowerCase().trim();

    if (!query) {
      return projects;
    }

    return projects.filter((project) => {
      const nameMatch = project.name.toLowerCase().includes(query);
      const keyMatch = project.key.toLowerCase().includes(query);
      const descriptionMatch = project.description?.toLowerCase().includes(query) || false;
      return nameMatch || keyMatch || descriptionMatch;
    });
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
}
