import { Component, ChangeDetectionStrategy, computed, inject } from '@angular/core';
import { Button, Icon, IconName } from 'shared-ui';
import { PublicNav } from '../components/public-nav';
import { Footer } from '../components/footer';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

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
  imports: [Button, Icon, PublicNav, Footer, TranslatePipe],
  template: `
    <div class="features-page">
      <app-public-nav />
      <!-- Header Section -->
      <section class="features-page_header">
        <div class="features-page_header-container">
          <h1 class="features-page_title">{{ 'public.featuresPage.header.title' | translate }}</h1>
          <p class="features-page_subtitle">
            {{ 'public.featuresPage.header.subtitle' | translate }}
          </p>
          <div class="features-page_header-actions">
            <lib-button variant="primary" size="lg" [link]="['/register']">{{
              'public.featuresPage.header.getStarted' | translate
            }}</lib-button>
            <lib-button variant="secondary" size="lg" [link]="['/pricing']">{{
              'public.featuresPage.header.viewPricing' | translate
            }}</lib-button>
          </div>
        </div>
      </section>

      <!-- Feature Categories -->
      <section class="features-page_content">
        <div class="features-page_container">
          @for (category of featureCategories(); track category.title) {
            <div class="features-page_category">
              <div class="features-page_category-header">
                <h2 class="features-page_category-title">{{ category.title }}</h2>
                <p class="features-page_category-description">{{ category.description }}</p>
              </div>
              <div class="features-page_category-grid">
                @for (feature of category.features; track feature.title) {
                  <div class="features-page_feature-card">
                    <div class="features-page_feature-icon">
                      <lib-icon [name]="feature.icon" size="xl" color="primary-500" />
                    </div>
                    <h3 class="features-page_feature-title">{{ feature.title }}</h3>
                    <p class="features-page_feature-description">{{ feature.description }}</p>
                    <ul class="features-page_feature-details">
                      @for (detail of feature.details; track detail) {
                        <li class="features-page_feature-detail">
                          <lib-icon name="check" size="sm" color="success" />
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
          <h2 class="features-page_cta-title">{{ 'public.featuresPage.cta.title' | translate }}</h2>
          <p class="features-page_cta-description">
            {{ 'public.featuresPage.cta.description' | translate }}
          </p>
          <lib-button variant="primary" size="lg" [link]="['/register']">{{
            'public.featuresPage.cta.startFreeTrial' | translate
          }}</lib-button>
        </div>
      </section>
      <app-footer />
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .features-page {
        @apply min-h-screen;
        @apply flex flex-col;
        @apply bg-bg-primary;
      }

      .features-page_header {
        @apply w-full;
        @apply py-16 md:py-24;
        @apply px-4 sm:px-6 lg:px-8;
        @apply bg-bg-secondary;
        @apply border-b;
        @apply border-border-default;
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
        @apply text-text-primary;
        margin: 0;
      }

      .features-page_subtitle {
        @apply text-lg sm:text-xl md:text-2xl;
        @apply text-text-secondary;
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
        @apply text-text-primary;
        margin: 0 0 1rem 0;
      }

      .features-page_category-description {
        @apply text-lg sm:text-xl;
        @apply text-text-secondary;
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
        @apply bg-bg-primary;
        @apply border;
        @apply border-border-default;
        @apply transition-shadow;
        @apply hover:shadow-lg;
      }

      .features-page_feature-icon {
        @apply flex items-center justify-center;
        @apply w-12 h-12;
        @apply rounded-lg;
        @apply bg-bg-tertiary;
      }

      .features-page_feature-title {
        @apply text-xl font-semibold;
        @apply text-text-primary;
        margin: 0;
      }

      .features-page_feature-description {
        @apply text-base leading-relaxed;
        @apply text-text-secondary;
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
        @apply text-text-secondary;
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
        @apply bg-bg-secondary;
        @apply border-t;
        @apply border-border-default;
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
        @apply text-text-primary;
        margin: 0;
      }

      .features-page_cta-description {
        @apply text-lg sm:text-xl;
        @apply text-text-secondary;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FeaturesPage {
  private readonly translateService = inject(TranslateService);

  readonly featureCategories = computed<FeatureCategory[]>(() => [
    {
      title: this.translateService.instant(
        'public.featuresPage.categories.projectManagement.title',
      ),
      description: this.translateService.instant(
        'public.featuresPage.categories.projectManagement.description',
      ),
      features: [
        {
          icon: 'square-check',
          title: this.translateService.instant(
            'public.featuresPage.categories.projectManagement.features.issueTracking.title',
          ),
          description: this.translateService.instant(
            'public.featuresPage.categories.projectManagement.features.issueTracking.description',
          ),
          details: [
            this.translateService.instant(
              'public.featuresPage.categories.projectManagement.features.issueTracking.details.customTypes',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.projectManagement.features.issueTracking.details.priorityDates',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.projectManagement.features.issueTracking.details.linking',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.projectManagement.features.issueTracking.details.subtasks',
            ),
          ],
        },
        {
          icon: 'layout-grid',
          title: this.translateService.instant(
            'public.featuresPage.categories.projectManagement.features.agileBoards.title',
          ),
          description: this.translateService.instant(
            'public.featuresPage.categories.projectManagement.features.agileBoards.description',
          ),
          details: [
            this.translateService.instant(
              'public.featuresPage.categories.projectManagement.features.agileBoards.details.dragDrop',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.projectManagement.features.agileBoards.details.sprintPlanning',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.projectManagement.features.agileBoards.details.backlog',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.projectManagement.features.agileBoards.details.charts',
            ),
          ],
        },
        {
          icon: 'git-branch',
          title: this.translateService.instant(
            'public.featuresPage.categories.projectManagement.features.workflows.title',
          ),
          description: this.translateService.instant(
            'public.featuresPage.categories.projectManagement.features.workflows.description',
          ),
          details: [
            this.translateService.instant(
              'public.featuresPage.categories.projectManagement.features.workflows.details.states',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.projectManagement.features.workflows.details.transitions',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.projectManagement.features.workflows.details.logic',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.projectManagement.features.workflows.details.functions',
            ),
          ],
        },
        {
          icon: 'trending-up',
          title: this.translateService.instant(
            'public.featuresPage.categories.projectManagement.features.reporting.title',
          ),
          description: this.translateService.instant(
            'public.featuresPage.categories.projectManagement.features.reporting.description',
          ),
          details: [
            this.translateService.instant(
              'public.featuresPage.categories.projectManagement.features.reporting.details.dashboards',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.projectManagement.features.reporting.details.velocity',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.projectManagement.features.reporting.details.timeTracking',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.projectManagement.features.reporting.details.export',
            ),
          ],
        },
      ],
    },
    {
      title: this.translateService.instant('public.featuresPage.categories.documentation.title'),
      description: this.translateService.instant(
        'public.featuresPage.categories.documentation.description',
      ),
      features: [
        {
          icon: 'file-text',
          title: this.translateService.instant(
            'public.featuresPage.categories.documentation.features.richTextEditor.title',
          ),
          description: this.translateService.instant(
            'public.featuresPage.categories.documentation.features.richTextEditor.description',
          ),
          details: [
            this.translateService.instant(
              'public.featuresPage.categories.documentation.features.richTextEditor.details.wysiwyg',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.documentation.features.richTextEditor.details.markdown',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.documentation.features.richTextEditor.details.media',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.documentation.features.richTextEditor.details.collaboration',
            ),
          ],
        },
        {
          icon: 'folder-tree',
          title: this.translateService.instant(
            'public.featuresPage.categories.documentation.features.pageHierarchy.title',
          ),
          description: this.translateService.instant(
            'public.featuresPage.categories.documentation.features.pageHierarchy.description',
          ),
          details: [
            this.translateService.instant(
              'public.featuresPage.categories.documentation.features.pageHierarchy.details.nested',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.documentation.features.pageHierarchy.details.dragDrop',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.documentation.features.pageHierarchy.details.templates',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.documentation.features.pageHierarchy.details.navigation',
            ),
          ],
        },
        {
          icon: 'search',
          title: this.translateService.instant(
            'public.featuresPage.categories.documentation.features.advancedSearch.title',
          ),
          description: this.translateService.instant(
            'public.featuresPage.categories.documentation.features.advancedSearch.description',
          ),
          details: [
            this.translateService.instant(
              'public.featuresPage.categories.documentation.features.advancedSearch.details.fullText',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.documentation.features.advancedSearch.details.filters',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.documentation.features.advancedSearch.details.saved',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.documentation.features.advancedSearch.details.attachments',
            ),
          ],
        },
        {
          icon: 'users',
          title: this.translateService.instant(
            'public.featuresPage.categories.documentation.features.teamCollaboration.title',
          ),
          description: this.translateService.instant(
            'public.featuresPage.categories.documentation.features.teamCollaboration.description',
          ),
          details: [
            this.translateService.instant(
              'public.featuresPage.categories.documentation.features.teamCollaboration.details.comments',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.documentation.features.teamCollaboration.details.mentions',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.documentation.features.teamCollaboration.details.watching',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.documentation.features.teamCollaboration.details.activity',
            ),
          ],
        },
      ],
    },
    {
      title: this.translateService.instant('public.featuresPage.categories.platformFeatures.title'),
      description: this.translateService.instant(
        'public.featuresPage.categories.platformFeatures.description',
      ),
      features: [
        {
          icon: 'shield',
          title: this.translateService.instant(
            'public.featuresPage.categories.platformFeatures.features.security.title',
          ),
          description: this.translateService.instant(
            'public.featuresPage.categories.platformFeatures.features.security.description',
          ),
          details: [
            this.translateService.instant(
              'public.featuresPage.categories.platformFeatures.features.security.details.rbac',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.platformFeatures.features.security.details.sso',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.platformFeatures.features.security.details.audit',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.platformFeatures.features.security.details.twoFactor',
            ),
          ],
        },
        {
          icon: 'plug',
          title: this.translateService.instant(
            'public.featuresPage.categories.platformFeatures.features.integrations.title',
          ),
          description: this.translateService.instant(
            'public.featuresPage.categories.platformFeatures.features.integrations.description',
          ),
          details: [
            this.translateService.instant(
              'public.featuresPage.categories.platformFeatures.features.integrations.details.api',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.platformFeatures.features.integrations.details.services',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.platformFeatures.features.integrations.details.custom',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.platformFeatures.features.integrations.details.marketplace',
            ),
          ],
        },
        {
          icon: 'smartphone',
          title: this.translateService.instant(
            'public.featuresPage.categories.platformFeatures.features.mobileApps.title',
          ),
          description: this.translateService.instant(
            'public.featuresPage.categories.platformFeatures.features.mobileApps.description',
          ),
          details: [
            this.translateService.instant(
              'public.featuresPage.categories.platformFeatures.features.mobileApps.details.platforms',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.platformFeatures.features.mobileApps.details.offline',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.platformFeatures.features.mobileApps.details.notifications',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.platformFeatures.features.mobileApps.details.optimized',
            ),
          ],
        },
        {
          icon: 'zap',
          title: this.translateService.instant(
            'public.featuresPage.categories.platformFeatures.features.performance.title',
          ),
          description: this.translateService.instant(
            'public.featuresPage.categories.platformFeatures.features.performance.description',
          ),
          details: [
            this.translateService.instant(
              'public.featuresPage.categories.platformFeatures.features.performance.details.fast',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.platformFeatures.features.performance.details.realtime',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.platformFeatures.features.performance.details.scale',
            ),
            this.translateService.instant(
              'public.featuresPage.categories.platformFeatures.features.performance.details.cdn',
            ),
          ],
        },
      ],
    },
  ]);
}
