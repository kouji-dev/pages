import { Component, ChangeDetectionStrategy, inject, computed } from '@angular/core';
import { Icon, IconName } from 'shared-ui';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';

interface Feature {
  icon: IconName;
  title: string;
  description: string;
}

@Component({
  selector: 'app-features-section',
  imports: [Icon, TranslatePipe],
  template: `
    <section class="features-section">
      <div class="features-section_container">
        <h2 class="features-section_heading">{{ 'public.whyChoose' | translate }}</h2>
        <p class="features-section_subheading">{{ 'public.everythingYouNeed' | translate }}</p>
        <div class="features-section_grid">
          @for (feature of features(); track feature.title) {
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
        @apply bg-muted;
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
        @apply text-foreground;
        margin: 0;
      }

      .features-section_subheading {
        @apply text-lg sm:text-xl md:text-2xl;
        @apply text-center;
        @apply text-muted-foreground;
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
        @apply bg-background;
        @apply border;
        @apply border-border;
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
        @apply bg-accent;
      }

      .features-section_card-title {
        @apply text-xl font-semibold;
        @apply text-foreground;
        margin: 0;
      }

      .features-section_card-description {
        @apply text-base leading-relaxed;
        @apply text-muted-foreground;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FeaturesSection {
  private readonly translateService = inject(TranslateService);

  readonly features = computed<Feature[]>(() => [
    {
      icon: 'zap',
      title: this.translateService.instant('public.lightningFast'),
      description: this.translateService.instant('public.lightningFastDescription'),
    },
    {
      icon: 'users',
      title: this.translateService.instant('public.teamCollaboration'),
      description: this.translateService.instant('public.teamCollaborationDescription'),
    },
    {
      icon: 'shield',
      title: this.translateService.instant('public.securePrivate'),
      description: this.translateService.instant('public.securePrivateDescription'),
    },
    {
      icon: 'folder',
      title: this.translateService.instant('public.flexibleWorkspace'),
      description: this.translateService.instant('public.flexibleWorkspaceDescription'),
    },
  ]);
}
