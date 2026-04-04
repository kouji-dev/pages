import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  signal,
  ViewContainerRef,
  effect,
  untracked,
} from '@angular/core';
import { Location } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { Button, Input, LoadingState, ErrorState, Modal, ToastService } from 'shared-ui';
import { ProjectService } from '../../../../application/services/project.service';
import { NavigationService } from '../../../../application/services/navigation.service';
import { LabelService, type Label } from '../../../../application/services/label.service';
import { DeleteProjectModal } from '../../components/delete-project-modal/delete-project-modal';
import {
  CreateLabelModal,
  type CreateLabelModalResult,
} from '../../components/create-label-modal/create-label-modal';
import { EditLabelModal } from '../../components/edit-label-modal/edit-label-modal';
import { DeleteLabelModal } from '../../components/delete-label-modal/delete-label-modal';
import { BackToPage } from '../../../../shared/components/back-to-page/back-to-page.component';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-project-settings-page',
  imports: [Button, Input, LoadingState, ErrorState, BackToPage, TranslatePipe],
  template: `
    <div class="project-settings-page">
      <div class="project-settings-page_header">
        <div class="project-settings-page_header-content">
          <div>
            <app-back-to-page
              [label]="'projects.backToProject' | translate"
              (onClick)="handleBackToProject()"
            />
            <h1 class="project-settings-page_title">{{ 'projects.settings.title' | translate }}</h1>
            <p class="project-settings-page_subtitle">
              {{ 'projects.settings.subtitle' | translate }}
            </p>
          </div>
        </div>
      </div>

      <div class="project-settings-page_content">
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
          <div class="project-settings-page_container">
            <!-- Project Details Section -->
            <div class="project-settings-page_section">
              <h2 class="project-settings-page_section-title">
                {{ 'projects.settings.details' | translate }}
              </h2>
              <form class="project-settings-page_form" (ngSubmit)="handleSaveProject()">
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
                <div class="project-settings-page_form-actions">
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

            <!-- Labels Section -->
            <div class="project-settings-page_section">
              <div class="project-settings-page_labels-header">
                <div>
                  <h2 class="project-settings-page_section-title">
                    {{ 'projects.settings.labels.title' | translate }}
                  </h2>
                  <p class="project-settings-page_labels-subtitle">
                    {{ 'projects.settings.labels.description' | translate }}
                  </p>
                </div>
                <lib-button variant="secondary" size="md" (clicked)="handleCreateLabel()">
                  {{ 'projects.settings.labels.create' | translate }}
                </lib-button>
              </div>

              @if (labelsLoading()) {
                <lib-loading-state [message]="'projects.settings.labels.loading' | translate" />
              } @else if (labelsError()) {
                <lib-error-state
                  [title]="'projects.settings.labels.loadErrorTitle' | translate"
                  [message]="labelsError()!"
                  [retryLabel]="'common.retry' | translate"
                  (onRetry)="fetchProjectLabels()"
                />
              } @else if (labels().length === 0) {
                <p class="project-settings-page_labels-empty">
                  {{ 'projects.settings.labels.empty' | translate }}
                </p>
              } @else {
                <ul class="project-settings-page_labels-list" role="list">
                  @for (label of labels(); track label.id) {
                    <li class="project-settings-page_labels-row">
                      <div class="project-settings-page_labels-main">
                        <span
                          class="project-settings-page_labels-swatch"
                          [style.background-color]="label.color"
                          [attr.aria-label]="'projects.settings.labels.colorSwatchAria' | translate"
                        ></span>
                        <span class="project-settings-page_labels-name">{{ label.name }}</span>
                        <span class="project-settings-page_labels-hex">{{ label.color }}</span>
                      </div>
                      <div class="project-settings-page_labels-actions">
                        <lib-button variant="ghost" size="sm" (clicked)="handleEditLabel(label)">
                          {{ 'projects.settings.labels.edit' | translate }}
                        </lib-button>
                        <lib-button variant="ghost" size="sm" (clicked)="handleDeleteLabel(label)">
                          {{ 'projects.settings.labels.delete' | translate }}
                        </lib-button>
                      </div>
                    </li>
                  }
                </ul>
                @if (labelsTotal() > labels().length) {
                  <p class="project-settings-page_labels-truncation">
                    {{
                      'projects.settings.labels.partialList'
                        | translate: { shown: labels().length, total: labelsTotal() }
                    }}
                  </p>
                }
              }
            </div>

            <!-- Danger Zone Section -->
            <div class="project-settings-page_section project-settings-page_section--danger">
              <h2 class="project-settings-page_section-title">
                {{ 'projects.settings.dangerZone' | translate }}
              </h2>
              <div class="project-settings-page_danger-content">
                <div>
                  <h3 class="project-settings-page_danger-title">
                    {{ 'projects.settings.deleteTitle' | translate }}
                  </h3>
                  <p class="project-settings-page_danger-description">
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
        @apply bg-background;
      }

      .project-settings-page_header {
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
        @apply border-b;
        @apply border-border;
      }

      .project-settings-page_header-content {
        @apply max-w-7xl mx-auto;
      }

      .project-settings-page_title {
        @apply text-3xl font-bold mb-2;
        @apply text-foreground;
        margin: 0;
      }

      .project-settings-page_subtitle {
        @apply text-base;
        @apply text-muted-foreground;
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
        @apply border-border;
        @apply bg-background;
      }

      .project-settings-page_section--danger {
        @apply border-destructive;
      }

      .project-settings-page_section-title {
        @apply text-xl font-semibold;
        @apply text-foreground;
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
        @apply border-border;
      }

      .project-settings-page_danger-content {
        @apply flex items-center justify-between;
        @apply gap-4;
        @apply flex-wrap;
      }

      .project-settings-page_danger-title {
        @apply text-lg font-semibold;
        @apply text-foreground;
        margin: 0 0 0.5rem 0;
      }

      .project-settings-page_danger-description {
        @apply text-sm;
        @apply text-muted-foreground;
        margin: 0;
      }

      .project-settings-page_labels-header {
        @apply flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4;
      }

      .project-settings-page_labels-subtitle {
        @apply text-sm text-muted-foreground mt-1;
        margin: 0;
      }

      .project-settings-page_labels-empty {
        @apply text-sm text-muted-foreground;
        margin: 0;
      }

      .project-settings-page_labels-list {
        @apply flex flex-col gap-2;
        list-style: none;
        margin: 0;
        padding: 0;
      }

      .project-settings-page_labels-row {
        @apply flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3;
        @apply py-3 px-3 rounded-md border border-border;
      }

      .project-settings-page_labels-main {
        @apply flex flex-wrap items-center gap-3 min-w-0;
      }

      .project-settings-page_labels-swatch {
        @apply inline-block h-4 w-4 rounded-sm shrink-0 border border-border;
      }

      .project-settings-page_labels-name {
        @apply font-medium text-foreground truncate;
      }

      .project-settings-page_labels-hex {
        @apply text-xs text-muted-foreground font-mono;
      }

      .project-settings-page_labels-actions {
        @apply flex flex-wrap items-center gap-1 shrink-0;
      }

      .project-settings-page_labels-truncation {
        @apply text-xs text-muted-foreground mt-2;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProjectSettingsPage {
  readonly projectService = inject(ProjectService);
  readonly labelService = inject(LabelService);
  readonly navigationService = inject(NavigationService);
  readonly route = inject(ActivatedRoute);
  readonly router = inject(Router);
  readonly location = inject(Location);
  readonly modal = inject(Modal);
  readonly toast = inject(ToastService);
  readonly viewContainerRef = inject(ViewContainerRef);
  private readonly translateService = inject(TranslateService);

  readonly projectId = computed(() => {
    return (
      this.navigationService.currentProjectId() || this.route.snapshot.paramMap.get('id') || ''
    );
  });
  readonly organizationId = computed(() => {
    return this.navigationService.currentOrganizationId() || '';
  });
  readonly project = computed(() => this.projectService.currentProject());

  readonly name = signal('');
  readonly key = signal('');
  readonly description = signal('');
  readonly isSaving = signal(false);
  readonly isDeleting = signal(false);
  readonly originalName = signal('');
  readonly originalDescription = signal('');

  readonly labels = signal<Label[]>([]);
  readonly labelsTotal = signal(0);
  readonly labelsLoading = signal(false);
  readonly labelsError = signal<string | null>(null);

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

  readonly errorMessage = computed(() => {
    const error = this.projectService.projectError();
    if (error) {
      return error instanceof Error
        ? error.message
        : this.translateService.instant('projects.loadError');
    }
    return this.translateService.instant('common.unknownError');
  });

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

  private readonly initializeEffect = effect(() => {
    const id = this.projectId();
    if (id) {
      this.projectService.fetchProject(id);
    }
  });

  private readonly loadLabelsWhenProjectReady = effect(() => {
    const id = this.projectId();
    const project = this.project();
    const hasErr = this.projectService.hasProjectError();
    if (!id || !project || hasErr) {
      return;
    }
    untracked(() => void this.fetchProjectLabels());
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

  async fetchProjectLabels(): Promise<void> {
    const id = this.projectId();
    if (!id) {
      return;
    }

    this.labelsLoading.set(true);
    this.labelsError.set(null);

    try {
      const response = await this.labelService.listProjectLabels(id, { page: 1, limit: 100 });
      if (this.projectId() !== id) {
        return;
      }
      this.labels.set(response.labels);
      this.labelsTotal.set(response.total);
    } catch (error) {
      console.error('Failed to load labels:', error);
      if (this.projectId() !== id) {
        return;
      }
      const message =
        error instanceof Error
          ? error.message
          : this.translateService.instant('projects.settings.labels.loadErrorMessage');
      this.labelsError.set(message);
    } finally {
      if (this.projectId() === id) {
        this.labelsLoading.set(false);
      }
    }
  }

  async handleCreateLabel(): Promise<void> {
    const projectId = this.projectId();
    if (!projectId) {
      return;
    }

    const result = await firstValueFrom(
      this.modal.open<CreateLabelModalResult | null>(CreateLabelModal, this.viewContainerRef, {
        size: 'sm',
        closable: true,
        data: {
          existingLabelNames: this.labels().map((l) => l.name),
        },
      }),
    );

    if (!result) {
      return;
    }

    try {
      await this.labelService.createLabel(projectId, result);
      this.toast.success(this.translateService.instant('projects.settings.labels.createSuccess'));
      await this.fetchProjectLabels();
    } catch (error) {
      console.error('Failed to create label:', error);
      const message =
        error instanceof Error
          ? error.message
          : this.translateService.instant('projects.settings.labels.createError');
      this.toast.error(message);
    }
  }

  async handleEditLabel(label: Label): Promise<void> {
    const otherNames = this.labels()
      .filter((l) => l.id !== label.id)
      .map((l) => l.name);

    const saved = await firstValueFrom(
      this.modal.open<boolean>(EditLabelModal, this.viewContainerRef, {
        size: 'sm',
        closable: true,
        data: {
          labelId: label.id,
          initialName: label.name,
          initialColor: label.color,
          existingLabelNames: otherNames,
        },
      }),
    );

    if (saved) {
      await this.fetchProjectLabels();
    }
  }

  async handleDeleteLabel(label: Label): Promise<void> {
    const confirmed = await firstValueFrom(
      this.modal.open<boolean>(DeleteLabelModal, this.viewContainerRef, {
        size: 'sm',
        closable: true,
        data: {
          labelId: label.id,
          labelName: label.name,
        },
      }),
    );

    if (confirmed) {
      await this.fetchProjectLabels();
    }
  }

  handleBackToProject(): void {
    if (window.history.length > 1) {
      this.location.back();
      return;
    }

    const orgId = this.organizationId();
    const projectId = this.projectId();
    if (orgId && projectId) {
      this.navigationService.navigateToProject(orgId, projectId);
      return;
    }
    if (orgId) {
      this.navigationService.navigateToOrganizationProjects(orgId);
    }
  }
}
