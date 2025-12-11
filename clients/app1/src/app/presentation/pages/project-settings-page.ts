import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  signal,
  ViewContainerRef,
  effect,
} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Button, Input, LoadingState, ErrorState, Modal, ToastService } from 'shared-ui';
import { ProjectService } from '../../application/services/project.service';
import { DeleteProjectModal } from '../components/delete-project-modal';

@Component({
  selector: 'app-project-settings-page',
  imports: [Button, Input, LoadingState, ErrorState],
  template: `
    <div class="project-settings-page">
      <div class="project-settings-page_header">
        <div class="project-settings-page_header-content">
          <div>
            <h1 class="project-settings-page_title">Project Settings</h1>
            <p class="project-settings-page_subtitle">
              Manage your project details and configuration.
            </p>
          </div>
        </div>
      </div>

      <div class="project-settings-page_content">
        @if (projectService.isFetchingProject()) {
          <lib-loading-state message="Loading project..." />
        } @else if (projectService.hasProjectError()) {
          <lib-error-state
            title="Failed to Load Project"
            [message]="errorMessage()"
            [retryLabel]="'Retry'"
            (onRetry)="handleRetry()"
          />
        } @else if (!project()) {
          <lib-error-state
            title="Project Not Found"
            message="The project you're looking for doesn't exist or you don't have access to it."
            [showRetry]="false"
          />
        } @else {
          <div class="project-settings-page_container">
            <!-- Project Details Section -->
            <div class="project-settings-page_section">
              <h2 class="project-settings-page_section-title">Project Details</h2>
              <form class="project-settings-page_form" (ngSubmit)="handleSaveProject()">
                <lib-input
                  label="Project Name"
                  placeholder="Enter project name"
                  [(model)]="name"
                  [required]="true"
                  [errorMessage]="nameError()"
                  helperText="The display name for your project"
                />
                <lib-input
                  label="Project Key"
                  placeholder="PROJ"
                  [(model)]="key"
                  [readonly]="true"
                  helperText="Project key cannot be changed after creation"
                />
                <lib-input
                  label="Description"
                  type="textarea"
                  placeholder="Describe your project (optional)"
                  [(model)]="description"
                  [rows]="4"
                  helperText="Optional description of your project"
                />
                <div class="project-settings-page_form-actions">
                  <lib-button
                    variant="primary"
                    type="submit"
                    [loading]="isSaving()"
                    [disabled]="!isFormValid() || !hasChanges()"
                  >
                    Save Changes
                  </lib-button>
                  <lib-button
                    variant="secondary"
                    (clicked)="handleReset()"
                    [disabled]="!hasChanges() || isSaving()"
                  >
                    Cancel
                  </lib-button>
                </div>
              </form>
            </div>

            <!-- Danger Zone Section -->
            <div class="project-settings-page_section project-settings-page_section--danger">
              <h2 class="project-settings-page_section-title">Danger Zone</h2>
              <div class="project-settings-page_danger-content">
                <div>
                  <h3 class="project-settings-page_danger-title">Delete Project</h3>
                  <p class="project-settings-page_danger-description">
                    Once you delete a project, there is no going back. Please be certain.
                  </p>
                </div>
                <lib-button
                  variant="danger"
                  size="md"
                  (clicked)="handleDeleteProject()"
                  [disabled]="isDeleting()"
                >
                  Delete Project
                </lib-button>
              </div>
            </div>
          </div>
        }
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .project-settings-page {
        @apply min-h-screen;
        @apply flex flex-col;
        @apply bg-bg-primary;
      }

      .project-settings-page_header {
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
        @apply border-b;
        @apply border-border-default;
      }

      .project-settings-page_header-content {
        @apply max-w-7xl mx-auto;
      }

      .project-settings-page_title {
        @apply text-3xl font-bold mb-2;
        @apply text-text-primary;
        margin: 0;
      }

      .project-settings-page_subtitle {
        @apply text-base;
        @apply text-text-secondary;
        margin: 0;
      }

      .project-settings-page_content {
        @apply flex-1;
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
      }

      .project-settings-page_container {
        @apply max-w-4xl mx-auto;
        @apply flex flex-col;
        @apply gap-8;
      }

      .project-settings-page_section {
        @apply flex flex-col;
        @apply gap-6;
        @apply p-6;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-primary;
      }

      .project-settings-page_section--danger {
        @apply border-error;
      }

      .project-settings-page_section-title {
        @apply text-xl font-semibold;
        @apply text-text-primary;
        margin: 0;
      }

      .project-settings-page_form {
        @apply flex flex-col;
        @apply gap-6;
      }

      .project-settings-page_form-actions {
        @apply flex items-center;
        @apply gap-3;
        @apply pt-4;
        @apply border-t;
        @apply border-border-default;
      }

      .project-settings-page_danger-content {
        @apply flex items-center justify-between;
        @apply gap-4;
        @apply flex-wrap;
      }

      .project-settings-page_danger-title {
        @apply text-lg font-semibold;
        @apply text-text-primary;
        margin: 0 0 0.5rem 0;
      }

      .project-settings-page_danger-description {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProjectSettingsPage {
  readonly projectService = inject(ProjectService);
  readonly route = inject(ActivatedRoute);
  readonly router = inject(Router);
  readonly modal = inject(Modal);
  readonly toast = inject(ToastService);
  readonly viewContainerRef = inject(ViewContainerRef);

  readonly projectId = computed(() => this.route.snapshot.paramMap.get('id') || '');
  readonly project = computed(() => this.projectService.currentProject());

  readonly name = signal('');
  readonly key = signal('');
  readonly description = signal('');
  readonly isSaving = signal(false);
  readonly isDeleting = signal(false);
  readonly originalName = signal('');
  readonly originalDescription = signal('');

  readonly nameError = computed(() => {
    const value = this.name();
    if (!value.trim()) {
      return 'Project name is required';
    }
    if (value.trim().length < 3) {
      return 'Project name must be at least 3 characters';
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

  readonly errorMessage = computed(() => {
    const error = this.projectService.projectError();
    if (error) {
      return error instanceof Error
        ? error.message
        : 'An error occurred while loading the project.';
    }
    return 'An unknown error occurred.';
  });

  private readonly initializeFormEffect = effect(
    () => {
      const project = this.project();
      if (project) {
        this.name.set(project.name);
        this.key.set(project.key);
        this.description.set(project.description || '');
        this.originalName.set(project.name);
        this.originalDescription.set(project.description || '');
      }
    },
    { allowSignalWrites: true },
  );

  private readonly initializeEffect = effect(
    () => {
      const id = this.projectId();
      if (id) {
        this.projectService.fetchProject(id);
      }
    },
    { allowSignalWrites: true },
  );

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
      this.toast.success('Project updated successfully!');
    } catch (error) {
      console.error('Failed to update project:', error);
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to update project. Please try again.';
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
}
