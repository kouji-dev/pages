import { Component, ChangeDetectionStrategy } from '@angular/core';
import { Button, Icon, IconName } from 'shared-ui';

interface Feature {
  icon: IconName;
  title: string;
  description: string;
  details: string[];
}

interface FeatureCategory {
  title: string;
  description: string;
  features: Feature[];
}

@Component({
  selector: 'app-features-page',
  imports: [Button, Icon],
  template: `
    <div class="features-page">
      <!-- Header Section -->
      <section class="features-page_header">
        <div class="features-page_header-container">
          <h1 class="features-page_title">Everything You Need to Build Better Together</h1>
          <p class="features-page_subtitle">
            Pages combines powerful project management and documentation tools in one seamless
            platform.
          </p>
          <div class="features-page_header-actions">
            <lib-button variant="primary" size="lg" [link]="['/register']">Get Started</lib-button>
            <lib-button variant="secondary" size="lg" [link]="['/pricing']"
              >View Pricing</lib-button
            >
          </div>
        </div>
      </section>

      <!-- Feature Categories -->
      <section class="features-page_content">
        <div class="features-page_container">
          @for (category of featureCategories; track category.title) {
            <div class="features-page_category">
              <div class="features-page_category-header">
                <h2 class="features-page_category-title">{{ category.title }}</h2>
                <p class="features-page_category-description">{{ category.description }}</p>
              </div>
              <div class="features-page_category-grid">
                @for (feature of category.features; track feature.title) {
                  <div class="features-page_feature-card">
                    <div class="features-page_feature-icon">
                      <lib-icon
                        [name]="feature.icon"
                        size="xl"
                        [color]="'var(--color-primary-500)'"
                      />
                    </div>
                    <h3 class="features-page_feature-title">{{ feature.title }}</h3>
                    <p class="features-page_feature-description">{{ feature.description }}</p>
                    <ul class="features-page_feature-details">
                      @for (detail of feature.details; track detail) {
                        <li class="features-page_feature-detail">
                          <lib-icon name="check" size="sm" [color]="'var(--color-success)'" />
                          <span>{{ detail }}</span>
                        </li>
                      }
                    </ul>
                  </div>
                }
              </div>
            </div>
          }
        </div>
      </section>

      <!-- CTA Section -->
      <section class="features-page_cta">
        <div class="features-page_cta-container">
          <h2 class="features-page_cta-title">Ready to Get Started?</h2>
          <p class="features-page_cta-description">
            Join thousands of teams already using Pages to build better together.
          </p>
          <lib-button variant="primary" size="lg" [link]="['/register']"
            >Start Free Trial</lib-button
          >
        </div>
      </section>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .features-page {
        @apply min-h-screen;
        @apply flex flex-col;
        background: var(--color-bg-primary);
      }

      .features-page_header {
        @apply w-full;
        @apply py-16 md:py-24;
        @apply px-4 sm:px-6 lg:px-8;
        background: var(--color-bg-secondary);
        border-bottom: 1px solid var(--color-border-default);
      }

      .features-page_header-container {
        @apply max-w-4xl mx-auto;
        @apply flex flex-col items-center;
        @apply gap-6;
        @apply text-center;
      }

      .features-page_title {
        @apply text-4xl sm:text-5xl md:text-6xl;
        @apply font-bold;
        color: var(--color-text-primary);
        margin: 0;
      }

      .features-page_subtitle {
        @apply text-lg sm:text-xl md:text-2xl;
        color: var(--color-text-secondary);
        margin: 0;
        @apply max-w-2xl;
      }

      .features-page_header-actions {
        @apply flex flex-col sm:flex-row items-center justify-center;
        @apply gap-4;
        @apply mt-4;
      }

      .features-page_content {
        @apply flex-1;
        @apply w-full;
        @apply py-16 md:py-24;
        @apply px-4 sm:px-6 lg:px-8;
      }

      .features-page_container {
        @apply max-w-7xl mx-auto;
        @apply flex flex-col;
        @apply gap-16 md:gap-24;
      }

      .features-page_category {
        @apply flex flex-col;
        @apply gap-8 md:gap-12;
      }

      .features-page_category-header {
        @apply text-center;
        @apply max-w-3xl mx-auto;
      }

      .features-page_category-title {
        @apply text-3xl sm:text-4xl md:text-5xl;
        @apply font-bold;
        color: var(--color-text-primary);
        margin: 0 0 1rem 0;
      }

      .features-page_category-description {
        @apply text-lg sm:text-xl;
        color: var(--color-text-secondary);
        margin: 0;
      }

      .features-page_category-grid {
        @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3;
        @apply gap-6 md:gap-8;
        @apply mt-8;
      }

      .features-page_feature-card {
        @apply flex flex-col;
        @apply gap-4;
        @apply p-6;
        @apply rounded-lg;
        background: var(--color-bg-primary);
        border: 1px solid var(--color-border-default);
        @apply transition-shadow;
        @apply hover:shadow-lg;
      }

      .features-page_feature-icon {
        @apply flex items-center justify-center;
        @apply w-12 h-12;
        @apply rounded-lg;
        background: var(--color-bg-tertiary);
      }

      .features-page_feature-title {
        @apply text-xl font-semibold;
        color: var(--color-text-primary);
        margin: 0;
      }

      .features-page_feature-description {
        @apply text-base leading-relaxed;
        color: var(--color-text-secondary);
        margin: 0;
      }

      .features-page_feature-details {
        @apply flex flex-col;
        @apply gap-2;
        @apply mt-2;
        margin: 0;
        padding: 0;
        list-style: none;
      }

      .features-page_feature-detail {
        @apply flex items-start gap-2;
        @apply text-sm;
        color: var(--color-text-secondary);
      }

      .features-page_feature-detail lib-icon {
        @apply flex-shrink-0;
        @apply mt-0.5;
      }

      .features-page_feature-detail span {
        @apply flex-1;
      }

      .features-page_cta {
        @apply w-full;
        @apply py-16 md:py-24;
        @apply px-4 sm:px-6 lg:px-8;
        background: var(--color-bg-secondary);
        border-top: 1px solid var(--color-border-default);
      }

      .features-page_cta-container {
        @apply max-w-3xl mx-auto;
        @apply flex flex-col items-center;
        @apply gap-6;
        @apply text-center;
      }

      .features-page_cta-title {
        @apply text-3xl sm:text-4xl md:text-5xl;
        @apply font-bold;
        color: var(--color-text-primary);
        margin: 0;
      }

      .features-page_cta-description {
        @apply text-lg sm:text-xl;
        color: var(--color-text-secondary);
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FeaturesPage {
  readonly featureCategories: FeatureCategory[] = [
    {
      title: 'Project Management',
      description: 'Powerful tools to organize, track, and manage your projects.',
      features: [
        {
          icon: 'check-square',
          title: 'Issue Tracking',
          description: 'Create, assign, and track issues with custom workflows.',
          details: [
            'Custom issue types (Task, Bug, Story, Epic)',
            'Priority levels and due dates',
            'Issue linking and dependencies',
            'Subtasks and bulk operations',
          ],
        },
        {
          icon: 'layout',
          title: 'Agile Boards',
          description: 'Scrum and Kanban boards for flexible project management.',
          details: [
            'Drag-and-drop board views',
            'Sprint planning and tracking',
            'Backlog management',
            'Burndown charts and velocity reports',
          ],
        },
        {
          icon: 'git-branch',
          title: 'Workflows',
          description: "Customizable workflows to match your team's processes.",
          details: [
            'Custom workflow states',
            'Automated transitions',
            'Conditional logic',
            'Post-functions and validators',
          ],
        },
        {
          icon: 'bar-chart',
          title: 'Reporting & Analytics',
          description: "Real-time insights into your project's progress.",
          details: [
            'Custom dashboards',
            'Velocity and burndown reports',
            'Time tracking reports',
            'Export to PDF/CSV',
          ],
        },
      ],
    },
    {
      title: 'Documentation',
      description: 'Create, organize, and collaborate on documentation.',
      features: [
        {
          icon: 'file-text',
          title: 'Rich Text Editor',
          description: 'Powerful editor with formatting, media, and collaboration.',
          details: [
            'WYSIWYG editing',
            'Markdown support',
            'Media embeds',
            'Real-time collaboration',
          ],
        },
        {
          icon: 'folder-tree',
          title: 'Page Hierarchy',
          description: 'Organize pages in a flexible tree structure.',
          details: [
            'Nested page structure',
            'Drag-and-drop organization',
            'Page templates',
            'Quick navigation',
          ],
        },
        {
          icon: 'search',
          title: 'Advanced Search',
          description: 'Find anything instantly across your workspace.',
          details: [
            'Full-text search',
            'Filter by tags, author, date',
            'Saved searches',
            'Search in attachments',
          ],
        },
        {
          icon: 'users',
          title: 'Team Collaboration',
          description: 'Work together with comments, mentions, and notifications.',
          details: [
            'Comments and discussions',
            '@mentions and notifications',
            'Page watching',
            'Activity feed',
          ],
        },
      ],
    },
    {
      title: 'Platform Features',
      description: 'Everything you need to scale your team and organization.',
      features: [
        {
          icon: 'shield',
          title: 'Security & Permissions',
          description: 'Enterprise-grade security with fine-grained permissions.',
          details: [
            'Role-based access control',
            'SSO and SAML support',
            'Audit logs',
            'Two-factor authentication',
          ],
        },
        {
          icon: 'plug',
          title: 'Integrations',
          description: 'Connect with the tools your team already uses.',
          details: [
            'REST API and webhooks',
            'GitHub, GitLab, Slack',
            'Custom integrations',
            'Marketplace apps',
          ],
        },
        {
          icon: 'smartphone',
          title: 'Mobile Apps',
          description: 'Access your work on the go with native mobile apps.',
          details: [
            'iOS and Android apps',
            'Offline access',
            'Push notifications',
            'Mobile-optimized views',
          ],
        },
        {
          icon: 'zap',
          title: 'Performance',
          description: 'Lightning-fast performance, even with large workspaces.',
          details: [
            'Fast page loads',
            'Real-time updates',
            'Optimized for large teams',
            'Global CDN',
          ],
        },
      ],
    },
  ];
}
