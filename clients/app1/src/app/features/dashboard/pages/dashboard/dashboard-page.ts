import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Icon, IconName } from 'shared-ui';
import { PageHeader } from '../../../../shared/layout/page-header/page-header';
import { PageBody } from '../../../../shared/layout/page-body/page-body';
import { PageContent } from '../../../../shared/layout/page-content/page-content';
import { StatsCard } from '../../components/stats-card/stats-card';

interface Stat {
  title: string;
  value: string;
  icon: IconName;
  change: string;
}

const stats: Stat[] = [
  { title: 'Active Projects', value: '12', icon: 'kanban', change: '+2 this week' },
  { title: 'Documents', value: '48', icon: 'file-text', change: '+5 this week' },
  { title: 'Team Members', value: '8', icon: 'users', change: 'No change' },
  { title: 'Tasks Completed', value: '156', icon: 'activity', change: '+23 this week' },
];

const recentProjects = ['Website Redesign', 'Mobile App v2', 'API Integration'];
const recentDocuments = ['Product Requirements', 'Meeting Notes', 'Technical Spec'];

@Component({
  selector: 'app-dashboard-page',
  imports: [CommonModule, Icon, StatsCard, PageHeader, PageBody, PageContent],
  template: `
    <app-page-body>
      <app-page-header title="dashboard.title" subtitle="dashboard.subtitle" />

      <app-page-content>
        <!-- Stats Grid -->
        <div class="dashboard-page_stats">
          @for (stat of stats; track stat.title) {
            <app-stats-card
              [title]="stat.title"
              [value]="stat.value"
              [icon]="stat.icon"
              [change]="stat.change"
            />
          }
        </div>

        <!-- Recent Items Grid -->
        <div class="dashboard-page_recent">
          <!-- Recent Projects -->
          <div class="dashboard-page_recent-card">
            <div class="dashboard-page_recent-card-header">
              <h3 class="dashboard-page_recent-card-title">Recent Projects</h3>
              <p class="dashboard-page_recent-card-description">
                Your most recently updated projects
              </p>
            </div>
            <div class="dashboard-page_recent-card-content">
              @for (project of recentProjects; track project) {
                <div class="dashboard-page_item">
                  <div class="dashboard-page_item-content">
                    <lib-icon name="kanban" size="xs" class="dashboard-page_item-icon" />
                    <span class="dashboard-page_item-label">{{ project }}</span>
                  </div>
                  <span class="dashboard-page_item-meta">Updated today</span>
                </div>
              }
            </div>
          </div>

          <!-- Recent Documents -->
          <div class="dashboard-page_recent-card">
            <div class="dashboard-page_recent-card-header">
              <h3 class="dashboard-page_recent-card-title">Recent Documents</h3>
              <p class="dashboard-page_recent-card-description">
                Your most recently edited documents
              </p>
            </div>
            <div class="dashboard-page_recent-card-content">
              @for (doc of recentDocuments; track doc) {
                <div class="dashboard-page_item">
                  <div class="dashboard-page_item-content">
                    <lib-icon name="file-text" size="xs" class="dashboard-page_item-icon" />
                    <span class="dashboard-page_item-label">{{ doc }}</span>
                  </div>
                  <span class="dashboard-page_item-meta">Edited today</span>
                </div>
              }
            </div>
          </div>
        </div>
      </app-page-content>
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

      .dashboard-page_stats {
        @apply max-w-7xl mx-auto;
        @apply grid gap-4;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        @apply md:grid-cols-2 lg:grid-cols-4;
        @apply mb-8;
      }

      .dashboard-page_recent {
        @apply max-w-7xl mx-auto;
        @apply grid gap-4;
        @apply md:grid-cols-2;
      }

      .dashboard-page_recent-card {
        @apply rounded-lg shadow-sm bg-card text-card-foreground border border-border;
        @apply p-6;
      }

      .dashboard-page_recent-card-header {
        @apply mb-4;
      }

      .dashboard-page_recent-card-title {
        @apply text-lg font-semibold text-foreground mb-1;
      }

      .dashboard-page_recent-card-description {
        @apply text-sm text-muted-foreground;
      }

      .dashboard-page_recent-card-content {
        @apply space-y-3;
      }

      .dashboard-page_item {
        @apply flex items-center justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors cursor-pointer;
      }

      .dashboard-page_item-content {
        @apply flex items-center gap-3;
      }

      .dashboard-page_item-icon {
        @apply text-primary;
      }

      .dashboard-page_item-label {
        @apply font-medium text-foreground;
      }

      .dashboard-page_item-meta {
        @apply text-xs text-muted-foreground;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: true,
})
export class DashboardPage {
  readonly stats = stats;
  readonly recentProjects = recentProjects;
  readonly recentDocuments = recentDocuments;
}
