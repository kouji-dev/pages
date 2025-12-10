import { Component, ChangeDetectionStrategy, computed, inject } from '@angular/core';
import { Button, LoadingState, ErrorState } from 'shared-ui';
import { ProjectService } from '../../application/services/project.service';
import { OrganizationService } from '../../application/services/organization.service';
import { NavigationService } from '../../application/services/navigation.service';
import { ProjectMemberList } from '../components/project-member-list';
import { IssueList } from '../components/issue-list';
import { KanbanBoard } from '../components/kanban-board';
import { BackToPage } from '../components/back-to-page';

type TabType = 'issues' | 'board' | 'settings' | 'members';

@Component({
  selector: 'app-project-detail-page',
  imports: [
    Button,
    LoadingState,
    ErrorState,
    ProjectMemberList,
    IssueList,
    KanbanBoard,
    BackToPage,
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
            <div class="project-detail-page_header-main">
              <div class="project-detail-page_header-info">
                <app-back-to-page label="Back to Projects" (onClick)="handleBackToProjects()" />
                <div class="project-detail-page_key">{{ project()?.key }}</div>
                <h1 class="project-detail-page_title">{{ project()?.name }}</h1>
                @if (project()?.description) {
                  <p class="project-detail-page_description">{{ project()?.description }}</p>
                }
              </div>
            </div>
          </div>
        </div>

        <div class="project-detail-page_content">
          <div class="project-detail-page_container">
            <div class="project-detail-page_sidebar">
              <nav class="project-detail-page_nav">
                <lib-button
                  variant="ghost"
                  size="md"
                  [fullWidth]="true"
                  leftIcon="file-text"
                  [class.project-detail-page_nav-item--active]="activeTab() === 'issues'"
                  (clicked)="setActiveTab('issues')"
                  class="project-detail-page_nav-item"
                >
                  Issues
                </lib-button>
                <lib-button
                  variant="ghost"
                  size="md"
                  [fullWidth]="true"
                  leftIcon="columns2"
                  [class.project-detail-page_nav-item--active]="activeTab() === 'board'"
                  (clicked)="setActiveTab('board')"
                  class="project-detail-page_nav-item"
                >
                  Board
                </lib-button>
                <lib-button
                  variant="ghost"
                  size="md"
                  [fullWidth]="true"
                  leftIcon="users"
                  [class.project-detail-page_nav-item--active]="activeTab() === 'members'"
                  (clicked)="setActiveTab('members')"
                  class="project-detail-page_nav-item"
                >
                  Members
                </lib-button>
                <lib-button
                  variant="ghost"
                  size="md"
                  [fullWidth]="true"
                  leftIcon="settings"
                  [class.project-detail-page_nav-item--active]="activeTab() === 'settings'"
                  (clicked)="setActiveTab('settings')"
                  class="project-detail-page_nav-item"
                >
                  Settings
                </lib-button>
              </nav>
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
                  <lib-button variant="primary" size="md" (clicked)="handleNavigateToSettings()">
                    Go to Settings Page
                  </lib-button>
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
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
        @apply border-b;
        @apply border-border-default;
      }

      .project-detail-page_header-content {
        @apply w-full;
      }

      .project-detail-page_header-main {
        @apply flex items-start justify-between;
        @apply gap-4;
        @apply flex-wrap;
      }

      .project-detail-page_header-info {
        @apply flex flex-col;
        @apply gap-2;
      }

      .project-detail-page_key {
        @apply text-xs font-mono font-semibold;
        @apply px-2 py-1;
        @apply rounded;
        @apply bg-bg-secondary;
        @apply text-text-secondary;
        @apply inline-block;
        @apply w-fit;
      }

      .project-detail-page_title {
        @apply text-3xl font-bold;
        @apply text-text-primary;
        margin: 0;
      }

      .project-detail-page_description {
        @apply text-base;
        @apply text-text-secondary;
        margin: 0;
      }

      .project-detail-page_content {
        @apply flex-1;
        @apply w-full;
        @apply py-8;
        @apply px-4 sm:px-6 lg:px-8;
      }

      .project-detail-page_container {
        @apply w-full;
        @apply grid grid-cols-1 lg:grid-cols-12;
        @apply gap-8;
      }

      .project-detail-page_sidebar {
        @apply lg:col-span-2;
        @apply lg:order-first;
      }

      .project-detail-page_nav {
        @apply flex flex-col;
        @apply gap-2;
        @apply p-2;
        @apply rounded-lg;
        @apply border;
        @apply border-border-default;
        @apply bg-bg-secondary;
      }

      .project-detail-page_nav-item {
        @apply justify-start;
      }

      .project-detail-page_nav-item--active {
        @apply bg-bg-tertiary;
      }

      .project-detail-page_main {
        @apply lg:col-span-10;
        @apply lg:order-last;
        @apply min-w-0;
        @apply overflow-hidden;
      }

      .project-detail-page_placeholder {
        @apply text-base;
        @apply text-text-secondary;
        @apply text-center;
        @apply py-12;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProjectDetailPage {
  readonly projectService = inject(ProjectService);
  readonly organizationService = inject(OrganizationService);
  readonly navigationService = inject(NavigationService);

  readonly organizationId = computed(() => {
    return this.navigationService.currentOrganizationId() || '';
  });

  readonly projectId = computed(() => {
    return this.navigationService.currentProjectId() || '';
  });

  readonly project = computed(() => this.projectService.currentProject());

  // Get tab from URL query params, default to 'issues'
  readonly activeTab = computed<TabType>(() => {
    const tab = this.navigationService.currentTab();
    if (tab && ['issues', 'board', 'members', 'settings'].includes(tab)) {
      return tab as TabType;
    }
    return 'issues';
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

  // Project is now automatically loaded when URL projectId changes
  // No need for manual initialization effect

  setActiveTab(tab: TabType): void {
    // Update URL query params instead of local state
    this.navigationService.updateQueryParams({ tab });
  }

  handleNavigateToSettings(): void {
    const orgId = this.organizationId();
    const projectId = this.projectId();
    if (orgId && projectId) {
      this.navigationService.navigateToProjectSettings(orgId, projectId);
    }
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
