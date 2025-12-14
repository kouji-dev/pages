import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  signal,
  effect,
  ViewContainerRef,
} from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { filter, map } from 'rxjs';
import { Button, Input, LoadingState, ErrorState, Modal, ToastService } from 'shared-ui';
import { ProjectService } from '../../application/services/project.service';
import { OrganizationService } from '../../application/services/organization.service';
import { NavigationService } from '../../application/services/navigation.service';
import { ProjectMemberList } from '../components/project-member-list';
import { IssueList } from '../components/issue-list';
import { KanbanBoard } from '../components/kanban-board';
import { BackToPage } from '../components/back-to-page';
import { SidebarNav, SidebarNavItem } from '../components/sidebar-nav';
import { DeleteProjectModal } from '../components/delete-project-modal';

type TabType = 'issues' | 'board' | 'settings' | 'members';

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
    BackToPage,
    SidebarNav,
  ],
  template: `
    <div class="project-detail-page">
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
        <div class="project-detail-page_header">
          <div class="project-detail-page_header-content">
            <app-back-to-page label="Back to Projects" (onClick)="handleBackToProjects()" />
            <div class="project-detail-page_header-main">
              <div class="project-detail-page_key">{{ project()?.key }}</div>
              <h1 class="project-detail-page_title">{{ project()?.name }}</h1>
              @if (project()?.description) {
                <p class="project-detail-page_description">{{ project()?.description }}</p>
              }
            </div>
          </div>
        </div>

        <div class="project-detail-page_content">
          <div class="project-detail-page_container">
            <div class="project-detail-page_sidebar">
              <app-sidebar-nav [items]="navItems()" />
            </div>
            <div class="project-detail-page_main">
              @if (activeTab() === 'issues') {
                <app-issue-list [projectId]="projectId()" />
              } @else if (activeTab() === 'board') {
                <app-kanban-board [projectId]="projectId()" />
              } @else if (activeTab() === 'members') {
                <app-project-member-list [projectId]="projectId()" />
              } @else if (activeTab() === 'settings') {
                <div class="project-detail-page_settings">
                  <div class="project-detail-page_settings-container">
                    <!-- Project Details Section -->
                    <div class="project-detail-page_settings-section">
                      <h2 class="project-detail-page_settings-section-title">Project Details</h2>
                      <form
                        class="project-detail-page_settings-form"
                        (ngSubmit)="handleSaveProject()"
                      >
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
                        <div class="project-detail-page_settings-form-actions">
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
                    <div
                      class="project-detail-page_settings-section project-detail-page_settings-section--danger"
                    >
                      <h2 class="project-detail-page_settings-section-title">Danger Zone</h2>
                      <div class="project-detail-page_settings-danger-content">
                        <div>
                          <h3 class="project-detail-page_settings-danger-title">Delete Project</h3>
                          <p class="project-detail-page_settings-danger-description">
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
                </div>
              }
            </div>
          </div>
        </div>
      }
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .project-detail-page {
        @apply min-h-screen;
        @apply flex flex-col;
        @apply bg-bg-primary;
      }

      .project-detail-page_header {
        @apply w-full;
        @apply py-6;
        @apply px-4 sm:px-6 lg:px-8;
        @apply border-b;
        @apply border-border-default;
      }

      .project-detail-page_header-content {
        @apply w-full;
      }

      .project-detail-page_header-main {
        @apply flex items-center;
        @apply gap-4;
        @apply flex-wrap;
      }

      .project-detail-page_key {
        @apply text-xs font-mono font-semibold;
        @apply px-2 py-1;
        @apply rounded;
        @apply bg-bg-secondary;
        @apply text-text-secondary;
        @apply inline-block;
        @apply w-fit;
        @apply flex-shrink-0;
      }

      .project-detail-page_title {
        @apply text-2xl font-bold;
        @apply text-text-primary;
        margin: 0;
        @apply flex-shrink-0;
      }

      .project-detail-page_description {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
        @apply flex-shrink-0;
      }

      .project-detail-page_content {
        @apply flex-1;
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
        @apply min-h-0;
        @apply flex;
        @apply flex-col;
      }

      .project-detail-page_container {
        @apply w-full;
        @apply flex-1;
        @apply flex;
        @apply gap-8;
        @apply min-h-0;
        @apply h-full;
        @apply items-stretch;
      }

      .project-detail-page_sidebar {
        width: 256px !important; /* Fixed width: w-64 = 16rem = 256px */
        min-width: 256px;
        max-width: 256px;
        height: 100vh; /* Fixed height: full viewport height */
        @apply flex-shrink-0;
        @apply flex;
        @apply flex-col;
        @apply min-h-0;
      }

      .project-detail-page_main {
        @apply flex-1;
        @apply min-w-0;
        @apply overflow-hidden;
        @apply self-stretch;
      }

      .project-detail-page_placeholder {
        @apply text-base;
        @apply text-text-secondary;
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
        @apply border-border-default;
        @apply bg-bg-primary;
      }

      .project-detail-page_settings-section--danger {
        @apply border-error;
      }

      .project-detail-page_settings-section-title {
        @apply text-xl font-semibold;
        @apply text-text-primary;
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
        @apply border-border-default;
      }

      .project-detail-page_settings-danger-content {
        @apply flex items-center justify-between;
        @apply gap-4;
        @apply flex-wrap;
      }

      .project-detail-page_settings-danger-title {
        @apply text-lg font-semibold;
        @apply text-text-primary;
        margin: 0 0 0.5rem 0;
      }

      .project-detail-page_settings-danger-description {
        @apply text-sm;
        @apply text-text-secondary;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProjectDetailPage {
  private readonly router = inject(Router);
  readonly projectService = inject(ProjectService);
  readonly organizationService = inject(OrganizationService);
  readonly navigationService = inject(NavigationService);
  readonly modal = inject(Modal);
  readonly toast = inject(ToastService);
  readonly viewContainerRef = inject(ViewContainerRef);

  readonly organizationId = computed(() => {
    return this.navigationService.currentOrganizationId() || '';
  });

  readonly projectId = computed(() => {
    return this.navigationService.currentProjectId() || '';
  });

  readonly project = computed(() => this.projectService.currentProject());

  // Settings form state
  readonly name = signal('');
  readonly key = signal('');
  readonly description = signal('');
  readonly isSaving = signal(false);
  readonly isDeleting = signal(false);
  readonly originalName = signal('');
  readonly originalDescription = signal('');

  // Get tab from URL query params, default to 'issues'
  readonly activeTab = computed<TabType>(() => {
    const tab = this.navigationService.currentTab();
    if (tab && ['issues', 'board', 'members', 'settings'].includes(tab)) {
      return tab as TabType;
    }
    return 'issues';
  });

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

  // Initialize form when project changes
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

  readonly errorMessage = computed(() => {
    const error = this.projectService.projectError();
    if (error) {
      return error instanceof Error
        ? error.message
        : 'An error occurred while loading the project.';
    }
    return 'An unknown error occurred.';
  });

  readonly navItems = computed<SidebarNavItem[]>(() => {
    const currentTab = this.activeTab();
    return [
      {
        label: 'Issues',
        icon: 'file-text',
        active: currentTab === 'issues',
        onClick: () => this.setActiveTab('issues'),
      },
      {
        label: 'Board',
        icon: 'columns2',
        active: currentTab === 'board',
        onClick: () => this.setActiveTab('board'),
      },
      {
        label: 'Members',
        icon: 'users',
        active: currentTab === 'members',
        onClick: () => this.setActiveTab('members'),
      },
      {
        label: 'Settings',
        icon: 'settings',
        active: currentTab === 'settings',
        onClick: () => this.setActiveTab('settings'),
      },
    ];
  });

  // Project is now automatically loaded when URL projectId changes
  // No need for manual initialization effect

  setActiveTab(tab: TabType): void {
    // Update URL query params for all tabs including settings
    this.navigationService.updateQueryParams({ tab });
  }

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

  handleBackToProjects(): void {
    const orgId = this.organizationId();
    if (orgId) {
      this.navigationService.navigateToOrganizationProjects(orgId);
    }
  }
}
