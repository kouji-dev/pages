import { Component, ChangeDetectionStrategy } from '@angular/core';
import { Button, Icon } from 'shared-ui';

@Component({
  selector: 'app-hero-section',
  imports: [Button, Icon],
  template: `
    <section class="hero-section">
      <div class="hero-section_container">
        <div class="hero-section_content">
          <h1 class="hero-section_headline">{{ headline }}</h1>
          <p class="hero-section_subheading">{{ subheading }}</p>
          <p class="hero-section_description">{{ valueProposition }}</p>
          <div class="hero-section_actions">
            <lib-button variant="primary" size="lg" [link]="['/register']">
              {{ primaryCtaLabel }}
            </lib-button>
            <lib-button variant="secondary" size="lg" [link]="['/login']">
              {{ secondaryCtaLabel }}
            </lib-button>
          </div>
        </div>
        <div class="hero-section_image">
          <div class="hero-section_image-placeholder">
            <lib-icon name="image" size="2xl" color="var(--color-text-tertiary)" />
            <p class="hero-section_image-text">Hero Image</p>
          </div>
        </div>
      </div>
    </section>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .hero-section {
        @apply w-full;
        @apply py-16 md:py-24 lg:py-32;
        @apply px-4 sm:px-6 lg:px-8;
        @apply bg-bg-primary;
      }

      .hero-section_container {
        @apply max-w-7xl mx-auto;
        @apply grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12;
        @apply items-center;
      }

      .hero-section_content {
        @apply flex flex-col;
        @apply gap-6;
        @apply text-center lg:text-left;
      }

      .hero-section_headline {
        @apply text-4xl sm:text-5xl md:text-6xl lg:text-7xl;
        @apply font-bold leading-tight;
        @apply text-text-primary;
        margin: 0;
      }

      .hero-section_subheading {
        @apply text-xl sm:text-2xl md:text-3xl;
        @apply font-semibold;
        @apply text-text-secondary;
        margin: 0;
      }

      .hero-section_description {
        @apply text-base sm:text-lg md:text-xl;
        @apply leading-relaxed;
        @apply text-text-secondary;
        margin: 0;
        max-width: 600px;
        @apply mx-auto lg:mx-0;
      }

      .hero-section_actions {
        @apply flex flex-col sm:flex-row;
        @apply gap-4;
        @apply justify-center lg:justify-start;
        @apply mt-4;
      }

      .hero-section_image {
        @apply flex items-center justify-center;
        @apply w-full;
        @apply mt-8 lg:mt-0;
      }

      .hero-section_image-placeholder {
        @apply w-full max-w-lg;
        @apply aspect-square;
        @apply flex flex-col items-center justify-center;
        @apply border-2 border-dashed;
        @apply border-border-default;
        @apply rounded-lg;
        @apply bg-bg-secondary;
        @apply gap-4;
      }

      .hero-section_image-text {
        @apply text-sm font-medium;
        @apply text-text-tertiary;
        margin: 0;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HeroSection {
  readonly headline = 'Build Better Together';
  readonly subheading = 'Collaborate, Create, Succeed';
  readonly valueProposition =
    'Pages is your all-in-one workspace for teams. Organize projects, share ideas, and bring your vision to life with powerful collaboration tools.';
  readonly primaryCtaLabel = 'Get Started';
  readonly secondaryCtaLabel = 'Learn More';
}
