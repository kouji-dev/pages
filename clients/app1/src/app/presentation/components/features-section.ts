import { Component, ChangeDetectionStrategy } from '@angular/core';
import { Icon, IconName } from 'shared-ui';

interface Feature {
  icon: IconName;
  title: string;
  description: string;
}

@Component({
  selector: 'app-features-section',
  imports: [Icon],
  template: `
    <section class="features-section">
      <div class="features-section_container">
        <h2 class="features-section_heading">Why Choose Pages?</h2>
        <p class="features-section_subheading">Everything you need to collaborate and succeed</p>
        <div class="features-section_grid">
          @for (feature of features; track feature.title) {
            <div class="features-section_card">
              <div class="features-section_card-content">
                <div class="features-section_card-icon">
                  <lib-icon [name]="feature.icon" size="xl" color="primary-500" />
                </div>
                <h3 class="features-section_card-title">{{ feature.title }}</h3>
                <p class="features-section_card-description">{{ feature.description }}</p>
              </div>
            </div>
          }
        </div>
      </div>
    </section>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .features-section {
        @apply w-full;
        @apply py-16 md:py-24;
        @apply px-4 sm:px-6 lg:px-8;
        @apply bg-bg-secondary;
      }

      .features-section_container {
        @apply max-w-7xl mx-auto;
        @apply flex flex-col;
        @apply gap-8 md:gap-12;
      }

      .features-section_heading {
        @apply text-3xl sm:text-4xl md:text-5xl;
        @apply font-bold;
        @apply text-center;
        @apply text-text-primary;
        margin: 0;
      }

      .features-section_subheading {
        @apply text-lg sm:text-xl md:text-2xl;
        @apply text-center;
        @apply text-text-secondary;
        margin: 0;
      }

      .features-section_grid {
        @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8;
        @apply mt-8;
      }

      .features-section_card {
        @apply h-full;
        @apply rounded-lg;
        @apply p-6;
        @apply bg-bg-primary;
        @apply border;
        @apply border-border-default;
        @apply transition-shadow;
        @apply hover:shadow-lg;
      }

      .features-section_card-content {
        @apply flex flex-col;
        @apply gap-4;
        @apply h-full;
      }

      .features-section_card-icon {
        @apply flex items-center justify-center;
        @apply w-12 h-12;
        @apply rounded-lg;
        @apply bg-bg-tertiary;
      }

      .features-section_card-title {
        @apply text-xl font-semibold;
        @apply text-text-primary;
        margin: 0;
      }

      .features-section_card-description {
        @apply text-base leading-relaxed;
        @apply text-text-secondary;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FeaturesSection {
  readonly features: Feature[] = [
    {
      icon: 'zap',
      title: 'Lightning Fast',
      description:
        'Built for speed and performance. Experience seamless collaboration without any lag or delays.',
    },
    {
      icon: 'users',
      title: 'Team Collaboration',
      description:
        'Work together in real-time with your team. Share ideas, assign tasks, and stay in sync.',
    },
    {
      icon: 'shield',
      title: 'Secure & Private',
      description:
        'Your data is protected with enterprise-grade security. Privacy and safety are our top priorities.',
    },
    {
      icon: 'folder',
      title: 'Flexible Workspace',
      description:
        'Organize your work the way you want. Customize layouts, views, and workflows to fit your needs.',
    },
  ];
}
