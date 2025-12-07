import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  OnInit,
  ViewContainerRef,
  signal,
} from '@angular/core';
import { Router } from '@angular/router';
import { Button, LoadingState, ErrorState, EmptyState, Modal } from 'shared-ui';
import { ProjectService, Project } from '../../application/services/project.service';
import { OrganizationService } from '../../application/services/organization.service';
import { ProjectCard } from '../components/project-card';
import { CreateProjectModal } from '../components/create-project-modal';

@Component({
  selector: 'app-projects-page',
  imports: [Button, LoadingState, ErrorState, EmptyState, ProjectCard],
  template: `
    <div class="projects-page">
      <div class="projects-page_header">
        <div class="projects-page_header-content">
          <div>
            <h1 class="projects-page_title">Projects</h1>
            <p class="projects-page_subtitle">
              Manage your projects and track issues in one place.
            </p>
          </div>
          <lib-button
            variant="primary"
            size="md"
            leftIcon="plus"
            (clicked)="handleCreateProject()"
            [disabled]="!currentOrganizationId()"
          >
            Create Project
          </lib-button>
        </div>
      </div>

      <div class="projects-page_content">
        @if (projectService.isLoading()) {
          <lib-loading-state message="Loading projects..." />
        } @else if (projectService.hasError()) {
          <lib-error-state
            title="Failed to Load Projects"
            [message]="errorMessage()"
            [retryLabel]="'Retry'"
            (onRetry)="handleRetry()"
          />
        } @else if (projects().length === 0) {
          <lib-empty-state
            title="No projects yet"
            message="Get started by creating your first project to manage issues and tasks."
            icon="folder"
            actionLabel="Create Project"
            actionIcon="plus"
            (onAction)="handleCreateProject()"
          />
        } @else {
          <div class="projects-page_grid">
            @for (project of projects(); track project.id) {
              <app-project-card [project]="project" (onSettings)="handleProjectSettings($event)" />
            }
          </div>
        }
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .projects-page {
        @apply min-h-screen;
        @apply flex flex-col;
        @apply bg-bg-primary;
      }

      .projects-page_header {
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
        @apply border-b;
        @apply border-border-default;
      }

      .projects-page_header-content {
        @apply max-w-7xl mx-auto;
        @apply flex items-center justify-between;
        @apply gap-4;
        @apply flex-wrap;
      }

      .projects-page_title {
        @apply text-3xl font-bold;
        @apply text-text-primary;
        margin: 0 0 0.5rem 0;
      }

      .projects-page_subtitle {
        @apply text-base;
        @apply text-text-secondary;
        margin: 0;
      }

      .projects-page_content {
        @apply flex-1;
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
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
export class ProjectsPage implements OnInit {
  readonly projectService = inject(ProjectService);
  readonly organizationService = inject(OrganizationService);
  readonly router = inject(Router);
  readonly modal = inject(Modal);
  readonly viewContainerRef = inject(ViewContainerRef);

  readonly projects = computed(() => {
    const orgId = this.currentOrganizationId();
    if (!orgId) return [];
    return this.projectService.getProjectsByOrganization(orgId);
  });

  readonly currentOrganizationId = computed(() => {
    const org = this.organizationService.currentOrganization();
    return org?.id || null;
  });

  readonly errorMessage = computed(() => {
    const error = this.projectService.error();
    if (error) {
      return error instanceof Error ? error.message : 'An error occurred while loading projects.';
    }
    return 'An unknown error occurred.';
  });

  ngOnInit(): void {
    // Load projects when component initializes
    this.projectService.loadProjects();
  }

  handleCreateProject(): void {
    const orgId = this.currentOrganizationId();
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
    this.router.navigate(['/app/projects', project.id, 'settings']);
  }

  handleRetry(): void {
    this.projectService.loadProjects();
  }
}
