import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  OnInit,
  signal,
  effect,
} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Button, Icon, LoadingState, ErrorState } from 'shared-ui';
import { ProjectService } from '../../application/services/project.service';
import { ProjectMemberList } from '../components/project-member-list';

type TabType = 'issues' | 'settings' | 'members';

@Component({
  selector: 'app-project-detail-page',
  imports: [Button, LoadingState, ErrorState, ProjectMemberList],
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
          <div class="project-detail-page_tabs">
            <lib-button
              variant="ghost"
              size="md"
              [class.project-detail-page_tab--active]="activeTab() === 'issues'"
              (clicked)="setActiveTab('issues')"
            >
              Issues
            </lib-button>
            <lib-button
              variant="ghost"
              size="md"
              [class.project-detail-page_tab--active]="activeTab() === 'members'"
              (clicked)="setActiveTab('members')"
            >
              Members
            </lib-button>
            <lib-button
              variant="ghost"
              size="md"
              [class.project-detail-page_tab--active]="activeTab() === 'settings'"
              (clicked)="setActiveTab('settings')"
            >
              Settings
            </lib-button>
          </div>

          <div class="project-detail-page_tab-content">
            @if (activeTab() === 'issues') {
              <div class="project-detail-page_issues">
                <p class="project-detail-page_placeholder">
                  Issues list will be implemented in task 1.3.6
                </p>
              </div>
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
        @apply max-w-7xl mx-auto;
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

      .project-detail-page_tabs {
        @apply max-w-7xl mx-auto;
        @apply flex items-center;
        @apply gap-2;
        @apply border-b;
        @apply border-border-default;
        @apply mb-6;
      }

      .project-detail-page_tab--active {
        @apply border-b-2;
        @apply border-primary-500;
      }

      .project-detail-page_tab-content {
        @apply max-w-7xl mx-auto;
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
export class ProjectDetailPage implements OnInit {
  readonly projectService = inject(ProjectService);
  readonly route = inject(ActivatedRoute);
  readonly router = inject(Router);

  readonly projectId = computed(() => this.route.snapshot.paramMap.get('id') || '');
  readonly project = computed(() => this.projectService.currentProject());
  readonly activeTab = signal<TabType>('issues');

  readonly errorMessage = computed(() => {
    const error = this.projectService.projectError();
    if (error) {
      return error instanceof Error
        ? error.message
        : 'An error occurred while loading the project.';
    }
    return 'An unknown error occurred.';
  });

  ngOnInit(): void {
    const id = this.projectId();
    if (id) {
      this.projectService.fetchProject(id);
    }
  }

  setActiveTab(tab: TabType): void {
    this.activeTab.set(tab);
  }

  handleNavigateToSettings(): void {
    const id = this.projectId();
    if (id) {
      this.router.navigate(['/app/projects', id, 'settings']);
    }
  }

  handleRetry(): void {
    const id = this.projectId();
    if (id) {
      this.projectService.fetchProject(id);
    }
  }
}
